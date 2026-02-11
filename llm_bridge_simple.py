#!/usr/bin/env python3
"""
LLM Bridge - Simple version with direct prompts
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

API_KEY = "syn_3005bb47081b13be8f207a31c56029fa"

def call_llm(prompt):
    """Call Synthetic API"""
    try:
        data = json.dumps({
            "model": "hf:moonshotai/Kimi-K2.5",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 150
        }).encode()
        
        req = urllib.request.Request(
            "https://api.synthetic.new/anthropic/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            
            if 'content' in result and len(result['content']) > 0:
                content = result['content'][0]
                if 'text' in content:
                    return content['text'].strip()
                elif 'thinking' in content:
                    # Extract just the answer part from thinking
                    thinking = content['thinking'].strip()
                    # Try to find a response that looks like customer service
                    lines = thinking.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('-') and not line.startswith('*') and not line[0].isdigit():
                            if len(line) > 20 and len(line) < 200:
                                return line
                    return thinking[:200] + "..."
            
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def enhance_response(user_query, tool_result, tool_name):
    """Create natural language response"""
    
    if tool_name == "get_invoice" and "invoice" in tool_result:
        inv = tool_result["invoice"]
        # Ultra simple prompt
        prompt = f"Responde ao cliente em português (máx 2 frases): Fatura {inv['number']}, €{inv['amount']}, {inv['date']}, {inv['consumption_kwh']} kWh, {'paga' if inv['status'] == 'paid' else 'pendente'}."
        
        llm_response = call_llm(prompt)
        if llm_response:
            return llm_response
        
        status_pt = "paga" if inv['status'] == 'paid' else "pendente"
        return f"A sua fatura {inv['number']} é de €{inv['amount']} (emitida em {inv['date']}). Consumo: {inv['consumption_kwh']} kWh - {status_pt}."
    
    elif tool_name == "get_consumption":
        prompt = f"Responde sobre consumo de energia em português (máx 2 frases). Dados: {json.dumps(tool_result, ensure_ascii=False)[:200]}"
        
        llm_response = call_llm(prompt)
        if llm_response:
            return llm_response
        
        return "Aqui estão os dados do seu consumo de energia."
    
    return "Processado com sucesso."

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers.get('Content-Length', '0'))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                user_message = data.get('message', '')
                tool_result = data.get('result', {})
                tool_name = data.get('tool', '')
                
                enhanced = enhance_response(user_message, tool_result, tool_name)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"response": enhanced}).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8081), Handler)
    print("🧠 LLM Bridge (Simple) on http://localhost:8081")
    server.serve_forever()
