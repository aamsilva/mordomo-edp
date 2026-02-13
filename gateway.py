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

app = FastAPI(title="Mordomo MAS Gateway", version="3.0")

# Serve static files (web interface)
web_interface_path = Path(__file__).parent / "web_interface"
if web_interface_path.exists():
    # Serve web_interface files at root
    app.mount("/", StaticFiles(directory=str(web_interface_path), html=True), name="web_interface")

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
    return {
        "service": "Mordomo MAS Gateway",
        "version": "3.0",
        "agents": orchestrator.get_all_agents(),
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "agents": len(orchestrator.agents)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - uses Multi-Agent System with LLM enhancement
    """
    try:
        # Route query through orchestrator
        result = orchestrator.route_query(
            query=request.message,
            user_context=request.context or {}
        )
        
        response_data = result["response"]
        agent_name = result["primary_agent"]
        
        # 🧠 ENHANCE: Pass through LLM for natural language
        enhanced_message = llm_bridge.enhance_response(
            user_query=request.message,
            agent_response=response_data,
            agent_name=agent_name
        )
        
        return ChatResponse(
            response=enhanced_message,
            agent=agent_name,
            data=response_data.get("data", {}),
            follow_up=response_data.get("follow_up", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP-compatible endpoint for tool calls
    Maintains backward compatibility with MCP protocol
    """
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        
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
            return {"tools": tools}
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Route to appropriate agent via orchestrator
            result = orchestrator.route_query(
                query=arguments.get("query", ""),
                user_context=arguments
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result["response"], ensure_ascii=False)
                    }
                ]
            }
        
        else:
            return {"error": "Unknown method"}
            
    except Exception as e:
        return {"error": str(e)}

@app.get("/agents")
def list_agents():
    """List all registered agents and their capabilities"""
    return {
        "agents": orchestrator.get_all_agents(),
        "total": len(orchestrator.agents)
    }

@app.post("/agents/{agent_name}/query")
def query_specific_agent(agent_name: str, request: ChatRequest):
    """Query a specific agent directly (for testing/debugging)"""
    if agent_name not in orchestrator.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    agent = orchestrator.agents[agent_name]
    result = agent.process(request.message, request.context or {})
    
    return {
        "agent": agent_name,
        "response": result
    }

@app.post("/context/clear")
def clear_context():
    """Clear conversation context (new session)"""
    orchestrator.clear_context()
    return {"status": "context cleared"}

@app.get("/context")
def get_context():
    """Get current shared context"""
    return orchestrator.shared_context

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
