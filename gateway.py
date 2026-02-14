"""
MCP Gateway - Multi-Agent System Version
Replaces the simple gateway.py with full MAS orchestration
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import json
import os
from pathlib import Path

# Import the Multi-Agent System
from agents import Orchestrator, BillingAgent, EVAgent, SolarAgent
from llm_bridge import llm_bridge

# Import logging and error handling
from utils.logging_config import configure_logging, get_contextual_logger, generate_request_id
from utils.exceptions import AgentNotFoundError, LLMError, ValidationError, AgentProcessingError
from utils.error_handlers import register_exception_handlers

# Configure logging at startup
configure_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_to_file=True,
    log_to_console=True
)

# Get gateway logger
logger = get_contextual_logger("gateway")

app = FastAPI(title="Mordomo MAS Gateway", version="3.0")

# Register exception handlers
register_exception_handlers(app)

# Serve static files (web interface)
web_interface_path = Path(__file__).parent / "web_interface"
if web_interface_path.exists():
    # Serve web_interface files at /ui path (not root, to avoid conflicts with API routes)
    app.mount("/ui", StaticFiles(directory=str(web_interface_path), html=True), name="web_interface")

# CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Multi-Agent System
orchestrator = Orchestrator()

# Register all agents
orchestrator.register_agent(BillingAgent())
orchestrator.register_agent(EVAgent())
orchestrator.register_agent(SolarAgent())

logger.info("Multi-Agent System initialized", agent_count=len(orchestrator.agents), agents=list(orchestrator.agents.keys()))
print("🚀 Multi-Agent System initialized!")
print(f"📊 Registered agents: {list(orchestrator.agents.keys())}")

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    agent: str
    data: Dict[str, Any]
    follow_up: list

@app.get("/")
def root():
    # Serve index.html if it exists, otherwise return API info
    index_path = Path(__file__).parent / "web_interface" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    logger.info("Root endpoint accessed")
    return {
        "service": "Mordomo MAS Gateway",
        "version": "3.0",
        "agents": orchestrator.get_all_agents(),
        "status": "running"
    }

@app.get("/health")
def health():
    request_logger = get_contextual_logger("gateway")
    request_logger.info("Health check requested")
    return {"status": "healthy", "agents": len(orchestrator.agents)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - uses Multi-Agent System with LLM enhancement
    """
    # Create contextual logger with request ID
    request_logger = get_contextual_logger("gateway")
    request_id = request_logger.get_request_id()
    
    request_logger.info(
        "Chat request received",
        session_id=request.session_id,
        message_length=len(request.message)
    )
    
    # Validate request
    if not request.message or not request.message.strip():
        request_logger.warning("Empty message received", session_id=request.session_id)
        raise ValidationError(
            message="Message cannot be empty",
            error_id=request_id,
            field_errors={"message": "Message is required and cannot be empty"}
        )
    
    try:
        # Route query through orchestrator
        request_logger.info("Routing query to orchestrator", session_id=request.session_id)
        result = orchestrator.route_query(
            query=request.message,
            user_context=request.context or {}
        )
        
        response_data = result["response"]
        agent_name = result["primary_agent"]
        
        request_logger.info(
            "Query routed successfully",
            agent=agent_name,
            session_id=request.session_id,
            has_collaboration=len(result.get("collaborating_agents", [])) > 0
        )
        
        # 🧠 ENHANCE: Pass through LLM for natural language
        try:
            enhanced_message = llm_bridge.enhance_response(
                user_query=request.message,
                agent_response=response_data,
                agent_name=agent_name
            )
            request_logger.debug("Response enhanced by LLM", agent=agent_name)
        except Exception as llm_exc:
            request_logger.warning(
                "LLM enhancement failed, using raw response",
                error=str(llm_exc),
                agent=agent_name
            )
            # Don't fail the request if LLM enhancement fails
            enhanced_message = response_data.get("message", "Desculpe, ocorreu um erro ao processar a resposta.")
        
        request_logger.info(
            "Chat response prepared",
            agent=agent_name,
            session_id=request.session_id,
            response_length=len(enhanced_message)
        )
        
        return ChatResponse(
            response=enhanced_message,
            agent=agent_name,
            data=response_data.get("data", {}),
            follow_up=response_data.get("follow_up", [])
        )
        
    except ValidationError:
        raise
    except Exception as e:
        request_logger.error(
            "Error processing chat request",
            error=str(e),
            error_type=type(e).__name__,
            session_id=request.session_id
        )
        raise AgentProcessingError(
            agent_name="orchestrator",
            message=f"Failed to process chat request: {str(e)}",
            error_id=request_id
        )

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP-compatible endpoint for tool calls
    Maintains backward compatibility with MCP protocol
    """
    request_logger = get_contextual_logger("gateway")
    request_id = request_logger.get_request_id()
    
    request_logger.info("MCP endpoint called")
    
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        
        request_logger.debug("MCP request parsed", method=method)
        
        if method == "tools/list":
            # Return available agents as tools
            tools = []
            for agent in orchestrator.agents.values():
                tools.append({
                    "name": agent.name,
                    "description": agent.description,
                    "parameters": {
                        "query": {"type": "string"},
                        "context": {"type": "object"}
                    }
                })
            request_logger.info("MCP tools listed", tool_count=len(tools))
            return {"tools": tools}
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            request_logger.info("MCP tool called", tool=tool_name)
            
            # Route to appropriate agent via orchestrator
            result = orchestrator.route_query(
                query=arguments.get("query", ""),
                user_context=arguments
            )
            
            request_logger.info("MCP tool execution completed", tool=tool_name)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result["response"], ensure_ascii=False)
                    }
                ]
            }
        
        else:
            request_logger.warning("Unknown MCP method", method=method)
            return {"error": "Unknown method"}
            
    except json.JSONDecodeError as e:
        request_logger.error("Invalid JSON in MCP request", error=str(e))
        raise ValidationError(
            message="Invalid JSON in request body",
            error_id=request_id,
            field_errors={"body": "Invalid JSON format"}
        )
    except Exception as e:
        request_logger.error("MCP endpoint error", error=str(e), error_type=type(e).__name__)
        raise AgentProcessingError(
            agent_name="mcp_handler",
            message=f"MCP processing failed: {str(e)}",
            error_id=request_id
        )

@app.get("/agents")
def list_agents():
    """List all registered agents and their capabilities"""
    request_logger = get_contextual_logger("gateway")
    request_logger.info("Agents list requested")
    
    return {
        "agents": orchestrator.get_all_agents(),
        "total": len(orchestrator.agents)
    }

@app.post("/agents/{agent_name}/query")
def query_specific_agent(agent_name: str, request: ChatRequest):
    """Query a specific agent directly (for testing/debugging)"""
    request_logger = get_contextual_logger("gateway")
    request_id = request_logger.get_request_id()
    
    request_logger.info(
        "Direct agent query",
        agent=agent_name,
        session_id=request.session_id
    )
    
    if agent_name not in orchestrator.agents:
        request_logger.warning("Agent not found", agent=agent_name)
        raise AgentNotFoundError(agent_name=agent_name, error_id=request_id)
    
    try:
        agent = orchestrator.agents[agent_name]
        result = agent.process(request.message, request.context or {})
        
        request_logger.info(
            "Direct agent query completed",
            agent=agent_name,
            success=result.get("success", False)
        )
        
        return {
            "agent": agent_name,
            "response": result
        }
    except Exception as e:
        request_logger.error(
            "Agent processing error",
            agent=agent_name,
            error=str(e),
            error_type=type(e).__name__
        )
        raise AgentProcessingError(
            agent_name=agent_name,
            message=f"Agent failed to process request: {str(e)}",
            error_id=request_id
        )

@app.post("/context/clear")
def clear_context():
    """Clear conversation context (new session)"""
    request_logger = get_contextual_logger("gateway")
    request_logger.info("Context cleared")
    
    orchestrator.clear_context()
    return {"status": "context cleared"}

@app.get("/context")
def get_context():
    """Get current shared context"""
    request_logger = get_contextual_logger("gateway")
    request_logger.debug("Context requested")
    
    return orchestrator.shared_context

if __name__ == "__main__":
    port = int(os.getenv("GATEWAY_PORT", 8765))
    logger.info("Starting Mordomo Gateway", port=port, host="0.0.0.0")
    uvicorn.run(app, host="0.0.0.0", port=port)