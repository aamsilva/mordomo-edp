#!/usr/bin/env python3
"""
Simple web server for Mordomo 3.0 Demo
Serves static files and proxies API requests to gateway
"""

import http.server
import socketserver
import json
import urllib.request
import os
from pathlib import Path

PORT = 8080
GATEWAY_URL = "http://localhost:8765/mcp"
LLM_BRIDGE_URL = "http://localhost:8081/chat"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / "web_interface"), **kwargs)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            if self.path == '/mcp':
                # Proxy to gateway
                req = urllib.request.Request(
                    GATEWAY_URL,
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
                
            elif self.path == '/chat':
                # Proxy to LLM bridge
                req = urllib.request.Request(
                    LLM_BRIDGE_URL,
                    data=post_data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=60) as response:
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
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Web server running at http://localhost:{PORT}")
        print(f"🔗 Connected to gateway at {GATEWAY_URL}")
        print(f"📁 Serving files from: {Path(__file__).parent / 'web_interface'}")
        print("\n👉 Open http://localhost:8080 in your browser")
        print("👉 Or expose with: cloudflared tunnel --url http://localhost:8080")
        print("\nPress Ctrl+C to stop")
        httpd.serve_forever()
