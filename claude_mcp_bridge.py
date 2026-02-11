#!/usr/bin/env python3
"""
MCP Bridge for Claude Desktop
Connects Claude (stdio) to Mordomo HTTP Gateway
"""

import sys
import json
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/tmp/mcp_bridge.log'
)
logger = logging.getLogger('mcp-bridge')

GATEWAY_URL = "http://localhost:8765/mcp"

def send_response(id_, result=None, error=None):
    """Send JSON-RPC response to Claude"""
    # Only send response if there's an id (it's a request, not a notification)
    if id_ is None:
        return
    
    response = {
        "jsonrpc": "2.0",
        "id": id_
    }
    if error:
        response["error"] = error
    else:
        response["result"] = result or {}
    
    print(json.dumps(response), flush=True)
    logger.info(f"Sent response: {response}")

def handle_initialize(id_):
    """Handle initialize method"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "mordomo-edp-gateway",
            "version": "3.0.0"
        }
    }

def handle_tools_list(id_):
    """Handle tools/list method"""
    return {
        "tools": [
            {
                "name": "get_invoice",
                "description": "Get invoice details by number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "invoice_number": {"type": "string"}
                    }
                }
            },
            {
                "name": "get_consumption",
                "description": "Get energy consumption data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "period": {"type": "string"}
                    }
                }
            }
        ]
    }

def handle_tools_call(id_, params):
    """Handle tools/call method - forward to HTTP gateway"""
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Handle special case "latest" for invoice
        if tool_name == "get_invoice" and arguments.get("invoice_number") == "latest":
            arguments["invoice_number"] = "INV-2026-001"  # Most recent mock invoice
        
        response = requests.post(
            GATEWAY_URL,
            json={
                "jsonrpc": "2.0",
                "id": str(id_),  # Converter para string!
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("result", {})
            
            # Format for Claude Desktop compatibility
            if "invoice" in data:
                inv = data["invoice"]
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Fatura {inv['number']}: €{inv['amount']}\nData: {inv['date']}\nConsumo: {inv['consumption_kwh']} kWh\nEstado: {inv['status']}"
                        }
                    ]
                }
            elif "data" in data:
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Consumo registrado. Período: {data.get('period', 'N/A')}"
                        }
                    ]
                }
            return data
        else:
            logger.error(f"Gateway error: {response.status_code}")
            return {"error": "Gateway error"}
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}

def main():
    logger.info("MCP Bridge started")
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            request = json.loads(line)
            logger.info(f"Received: {request}")
            
            method = request.get("method")
            id_ = request.get("id")  # Can be None for notifications
            params = request.get("params", {})
            
            # Handle notifications (no id) - just log, don't respond
            if id_ is None:
                logger.info(f"Notification received: {method}")
                # For notifications/initialized, just acknowledge internally
                continue
            
            # Handle requests (with id) - must respond
            if method == "initialize":
                result = handle_initialize(id_)
                send_response(id_, result=result)
                
            elif method == "tools/list":
                result = handle_tools_list(id_)
                send_response(id_, result=result)
                
            elif method == "tools/call":
                result = handle_tools_call(id_, params)
                if result is not None:
                    send_response(id_, result=result)
                else:
                    send_response(id_, error={"code": -32603, "message": "Gateway error"})
                    
            else:
                send_response(id_, error={"code": -32601, "message": f"Method not found: {method}"})
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            # Can't respond if we can't parse the id
            
        except Exception as e:
            logger.error(f"Error: {e}")
            # Try to respond if we have an id
            try:
                if 'id_' in locals() and id_ is not None:
                    send_response(id_, error={"code": -32603, "message": str(e)})
            except:
                pass

if __name__ == "__main__":
    main()
