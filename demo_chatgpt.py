#!/usr/bin/env python3
"""
Mordomo 3.0 - ChatGPT MCP Demo Script
Demonstrates how to connect ChatGPT to the MCP Gateway
"""

import asyncio
import json
import sys
from typing import Optional

try:
    import websockets
    import httpx
except ImportError:
    print("❌ Missing dependencies. Install with: pip install websockets httpx")
    sys.exit(1)

# Gateway URL
GATEWAY_HTTP = "http://localhost:8765"
GATEWAY_WS = "ws://localhost:8765/mcp/ws"


class MCPClient:
    """Simple MCP client for demonstration"""
    
    def __init__(self, use_websocket: bool = True):
        self.use_websocket = use_websocket
        self.websocket = None
        self.request_id = 0
    
    def _next_id(self) -> str:
        self.request_id += 1
        return f"req-{self.request_id}"
    
    async def connect(self):
        """Connect to MCP Gateway"""
        if self.use_websocket:
            print(f"🔌 Connecting to WebSocket: {GATEWAY_WS}")
            self.websocket = await websockets.connect(GATEWAY_WS)
            print("✅ Connected to WebSocket")
        else:
            print(f"📡 Using HTTP endpoint: {GATEWAY_HTTP}")
    
    async def call(self, method: str, params: Optional[dict] = None) -> dict:
        """Make an MCP call"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {}
        }
        
        if self.use_websocket and self.websocket:
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            return json.loads(response)
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{GATEWAY_HTTP}/mcp",
                    json=request,
                    timeout=10.0
                )
                return response.json()
    
    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()


async def demo_http():
    """Demo using HTTP endpoint"""
    print("\n" + "="*60)
    print("🧪 DEMO 1: HTTP Endpoint")
    print("="*60)
    
    client = MCPClient(use_websocket=False)
    await client.connect()
    
    # Test 1: Get agent info
    print("\n📋 Test 1: Get Agent Info")
    print("-" * 40)
    response = await client.call("agent/info")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 2: List tools
    print("\n🔧 Test 2: List Available Tools")
    print("-" * 40)
    response = await client.call("tools/list")
    tools = response.get("result", {}).get("tools", [])
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    
    # Test 3: Call get_invoice tool
    print("\n📄 Test 3: Get Invoice (INV-2026-001)")
    print("-" * 40)
    response = await client.call("tools/call", {
        "name": "get_invoice",
        "arguments": {"invoice_number": "INV-2026-001"}
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 4: Call get_consumption tool
    print("\n⚡ Test 4: Get Consumption Data")
    print("-" * 40)
    response = await client.call("tools/call", {
        "name": "get_consumption",
        "arguments": {"period": "month"}
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    await client.close()


async def demo_websocket():
    """Demo using WebSocket endpoint"""
    print("\n" + "="*60)
    print("🧪 DEMO 2: WebSocket Streaming")
    print("="*60)
    
    client = MCPClient(use_websocket=True)
    await client.connect()
    
    # Test 1: List payments
    print("\n💳 Test 1: List Payments")
    print("-" * 40)
    response = await client.call("tools/call", {
        "name": "list_payments",
        "arguments": {"limit": 3}
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 2: Get contract info
    print("\n📄 Test 2: Get Contract Info")
    print("-" * 40)
    response = await client.call("tools/call", {
        "name": "get_contract_info",
        "arguments": {}
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 3: Get non-existent invoice
    print("\n❌ Test 3: Get Non-existent Invoice")
    print("-" * 40)
    response = await client.call("tools/call", {
        "name": "get_invoice",
        "arguments": {"invoice_number": "INVALID"}
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    await client.close()


async def demo_performance():
    """Demo performance - multiple rapid requests"""
    print("\n" + "="*60)
    print("🧪 DEMO 3: Performance Test (10 rapid requests)")
    print("="*60)
    
    client = MCPClient(use_websocket=True)
    await client.connect()
    
    import time
    start = time.time()
    
    for i in range(10):
        response = await client.call("tools/call", {
            "name": "get_invoice",
            "arguments": {"invoice_number": "INV-2026-001"}
        })
        meta = response.get("_meta", {})
        proc_time = meta.get("processing_time_ms", "N/A")
        print(f"  Request {i+1}: {proc_time}ms")
    
    elapsed = (time.time() - start) * 1000
    print(f"\n✅ Total time for 10 requests: {elapsed:.2f}ms")
    print(f"✅ Average: {elapsed/10:.2f}ms per request")
    
    await client.close()


async def main():
    """Run all demos"""
    print("\n" + "🤖"*30)
    print("  Mordomo 3.0 MCP Gateway - ChatGPT Integration Demo")
    print("  " + "🤖"*30)
    print("\n  This demo shows how ChatGPT can interact with the")
    print("  EDP Billing Agent through the MCP Gateway.")
    print("\n  Make sure the gateway is running: ./start.sh")
    
    try:
        await demo_http()
        await demo_websocket()
        await demo_performance()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the gateway is running:")
        print("  ./start.sh")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())