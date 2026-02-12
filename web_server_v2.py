#!/usr/bin/env python3
"""
Simple web server for Mordomo 3.0 MAS
Serves static files and proxies to MAS Gateway
"""

import http.server
import socketserver
import json
import urllib.request
import os
from pathlib import Path

PORT = 8080
GATEWAY_URL = "http://localhost:8765"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / "web_interface"), **kwargs)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            if self.path == '/chat':
                # Proxy to MAS Gateway
                req = urllib.request.Request(
                    f"{GATEWAY_URL}/chat",
                    data=post_data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    response_data = response.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_data)
                
            elif self.path == '/mcp':
                # Proxy to MCP endpoint
                req = urllib.request.Request(
                    f"{GATEWAY_URL}/mcp",
                    data=post_data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    response_data = response.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_data)
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = json.dumps({"error": str(e), "response": None}).encode()
            self.wfile.write(error_msg)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Web server running at http://localhost:{PORT}")
        print(f"🔗 Connected to MAS Gateway at {GATEWAY_URL}")
        print("\n👉 Open http://localhost:8080 in your browser")
        print("👉 Or expose with: cloudflared tunnel --url http://localhost:8080")
        print("\nPress Ctrl+C to stop")
        httpd.serve_forever()
