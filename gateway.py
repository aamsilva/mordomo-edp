#!/usr/bin/env python3
"""
Mordomo 3.0 MCP Gateway for EDP
Real-time MCP Gateway with WebSocket streaming support
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-gateway")

# ============== MCP Protocol Models ==============

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class MCPTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class MCPAgentInfo(BaseModel):
    id: str
    name: str
    description: str
    tools: List[MCPTool]
    status: str = "online"

# ============== Agent Registry ==============

class AgentRegistry:
    """Registry for MCP agents"""
    
    def __init__(self):
        self.agents: Dict[str, MCPAgentInfo] = {}
        self.handlers: Dict[str, Callable] = {}
        self.connections: Dict[str, WebSocket] = {}
    
    def register_agent(self, agent_info: MCPAgentInfo, handler: Callable):
        self.agents[agent_info.id] = agent_info
        self.handlers[agent_info.id] = handler
        logger.info(f"Agent registered: {agent_info.id} ({agent_info.name})")
    
    def get_agent(self, agent_id: str) -> Optional[MCPAgentInfo]:
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[MCPAgentInfo]:
        return list(self.agents.values())
    
    def get_handler(self, agent_id: str) -> Optional[Callable]:
        return self.handlers.get(agent_id)

# Global registry
registry = AgentRegistry()

# ============== Billing Agent Implementation ==============

class BillingAgent:
    """EDP Billing Agent - Handles billing-related queries"""
    
    def __init__(self):
        self.info = MCPAgentInfo(
            id="edp-billing-agent",
            name="EDP Billing Agent",
            description="Agent for handling EDP billing queries, invoices, payments, and consumption data",
            tools=[
                MCPTool(
                    name="get_invoice",
                    description="Retrieve invoice details by invoice number or date",
                    parameters={
                        "type": "object",
                        "properties": {
                            "invoice_number": {"type": "string", "description": "Invoice number"},
                            "date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)"}
                        }
                    }
                ),
                MCPTool(
                    name="get_consumption",
                    description="Get electricity/gas consumption data",
                    parameters={
                        "type": "object",
                        "properties": {
                            "period": {"type": "string", "enum": ["month", "year"], "description": "Time period"},
                            "meter_id": {"type": "string", "description": "Meter identifier"}
                        },
                        "required": ["period"]
                    }
                ),
                MCPTool(
                    name="list_payments",
                    description="List payment history",
                    parameters={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "default": 10, "description": "Number of payments to return"}
                        }
                    }
                ),
                MCPTool(
                    name="get_contract_info",
                    description="Get contract details",
                    parameters={
                        "type": "object",
                        "properties": {
                            "contract_id": {"type": "string", "description": "Contract identifier"}
                        }
                    }
                )
            ]
        )
        # Mock data for demo
        self.mock_invoices = {
            "INV-2026-001": {
                "number": "INV-2026-001",
                "date": "2026-01-15",
                "amount": 87.50,
                "status": "paid",
                "due_date": "2026-02-05",
                "consumption_kwh": 245
            },
            "INV-2025-012": {
                "number": "INV-2025-012",
                "date": "2025-12-15",
                "amount": 92.30,
                "status": "paid",
                "due_date": "2026-01-05",
                "consumption_kwh": 268
            }
        }
        self.mock_consumption = {
            "2026-01": {"kwh": 245, "cost": 87.50},
            "2025-12": {"kwh": 268, "cost": 92.30},
            "2025-11": {"kwh": 210, "cost": 72.15}
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP requests"""
        start_time = time.time()
        method = request.method
        params = request.params or {}
        
        logger.info(f"BillingAgent handling: {method} (id={request.id})")
        
        try:
            if method == "tools/list":
                result = {"tools": [tool.dict() for tool in self.info.tools]}
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})
                result = await self.execute_tool(tool_name, tool_params)
            
            elif method == "agent/info":
                result = self.info.dict()
            
            else:
                return MCPResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {method}"}
                )
            
            elapsed = time.time() - start_time
            logger.info(f"Request processed in {elapsed:.3f}s")
            
            return MCPResponse(id=request.id, result=result)
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": str(e)}
            )
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        
        if tool_name == "get_invoice":
            invoice_num = params.get("invoice_number")
            if invoice_num and invoice_num in self.mock_invoices:
                return {"invoice": self.mock_invoices[invoice_num]}
            return {"invoice": None, "message": "Invoice not found"}
        
        elif tool_name == "get_consumption":
            period = params.get("period", "month")
            return {
                "period": period,
                "data": self.mock_consumption,
                "average_daily": 8.2
            }
        
        elif tool_name == "list_payments":
            limit = params.get("limit", 10)
            payments = [
                {"date": "2026-01-20", "amount": 87.50, "method": "Direct Debit", "status": "completed"},
                {"date": "2025-12-20", "amount": 92.30, "method": "Direct Debit", "status": "completed"},
                {"date": "2025-11-18", "amount": 72.15, "method": "Credit Card", "status": "completed"}
            ]
            return {"payments": payments[:limit]}
        
        elif tool_name == "get_contract_info":
            return {
                "contract": {
                    "id": "CNT-EDP-12345",
                    "type": "Residential Electricity",
                    "tariff": "Bi-horária",
                    "power": "6.9 kVA",
                    "start_date": "2020-03-15",
                    "status": "active"
                }
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

# Initialize billing agent
billing_agent = BillingAgent()
registry.register_agent(billing_agent.info, billing_agent.handle_request)

# ============== FastAPI Application ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("=" * 60)
    logger.info("Mordomo 3.0 MCP Gateway for EDP")
    logger.info("Real-time MCP Gateway starting...")
    logger.info("=" * 60)
    yield
    logger.info("Gateway shutting down...")

app = FastAPI(
    title="Mordomo 3.0 MCP Gateway",
    description="Real-time MCP Gateway for EDP with WebSocket streaming",
    version="3.0.0",
    lifespan=lifespan
)

# ============== HTTP Endpoints ==============

@app.get("/")
async def root():
    """Gateway status endpoint"""
    return {
        "name": "Mordomo 3.0 MCP Gateway",
        "version": "3.0.0",
        "status": "online",
        "agents": [agent.id for agent in registry.get_all_agents()],
        "endpoints": {
            "mcp_http": "/mcp",
            "mcp_ws": "/mcp/ws",
            "agents": "/agents",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_online": len(registry.get_all_agents())
    }

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "agents": [agent.dict() for agent in registry.get_all_agents()]
    }

@app.post("/mcp")
async def mcp_http(request: MCPRequest):
    """HTTP endpoint for MCP requests"""
    agent_id = request.params.get("agent_id") if request.params else None
    
    if not agent_id:
        # Default to billing agent
        agent_id = "edp-billing-agent"
    
    handler = registry.get_handler(agent_id)
    if not handler:
        return MCPResponse(
            id=request.id,
            error={"code": -32602, "message": f"Agent not found: {agent_id}"}
        )
    
    response = await handler(request)
    return response

# ============== WebSocket Endpoint ==============

@app.websocket("/mcp/ws")
async def mcp_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP streaming"""
    await websocket.accept()
    client_id = f"ws_{id(websocket)}"
    registry.connections[client_id] = websocket
    
    logger.info(f"WebSocket client connected: {client_id}")
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            start_time = time.time()
            
            try:
                # Parse request
                data = json.loads(message)
                request = MCPRequest(**data)
                
                logger.info(f"WS Request: {request.method} (id={request.id})")
                
                # Get agent handler
                agent_id = request.params.get("agent_id") if request.params else "edp-billing-agent"
                handler = registry.get_handler(agent_id)
                
                if not handler:
                    response = MCPResponse(
                        id=request.id,
                        error={"code": -32602, "message": f"Agent not found: {agent_id}"}
                    )
                else:
                    # Process request
                    response = await handler(request)
                
                # Send response
                elapsed = time.time() - start_time
                response_dict = response.dict()
                response_dict["_meta"] = {"processing_time_ms": round(elapsed * 1000, 2)}
                
                await websocket.send_json(response_dict)
                
                logger.info(f"WS Response sent in {elapsed:.3f}s")
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error: Invalid JSON"}
                })
            except Exception as e:
                logger.error(f"Error processing WS message: {e}")
                await websocket.send_json({
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_id}")
    finally:
        if client_id in registry.connections:
            del registry.connections[client_id]

# ============== Main Entry Point ==============

if __name__ == "__main__":
    uvicorn.run(
        "gateway:app",
        host="0.0.0.0",
        port=8765,
        log_level="info",
        reload=False
    )