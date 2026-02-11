#!/usr/bin/env python3
"""
LLM Bridge for Utility Assistant
Enhances gateway responses with natural language using LLM
"""

import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

GATEWAY_URL = "http://localhost:8765/mcp"

import urllib.request
import urllib.error
import os

def call_llm(prompt):
    """Call Synthetic API for natural language generation"""
    print(f"DEBUG: call_llm called with prompt length {len(prompt)}")
    try:
        # Synthetic API key
        api_key = "syn_3005bb47081b13be8f207a31c56029fa"
        
        if not api_key:
            print("No API key found for Synthetic")
            return None
        
        print(f"Using API key: {api_key[:10]}...")
        
        # Call Synthetic API (Anthropic format)
        data = json.dumps({
            "model": "hf:deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 200
        }).encode()
        
        req = urllib.request.Request(
            "https://api.synthetic.new/anthropic/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_body = response.read()
            print(f"API Response: {response_body[:200]}...")
            result = json.loads(response_body)
            
            # Try Synthetic API format
            if 'content' in result:
                content = result['content'][0]
                if 'thinking' in content:
                    return content['thinking'].strip()
                elif 'text' in content:
                    return content['text'].strip()
            
            # Try OpenAI format
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            
            print(f"Unknown response format: {list(result.keys())}")
            return None
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP Error {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"LLM Error: {type(e).__name__}: {e}")
        return None

def enhance_response(user_query, tool_result, tool_name, context=""):
    """Use LLM to create natural language response from tool data"""
    
    # Adicionar contexto do histórico se existir
    context_section = f"\n\nHISTÓRICO DA CONVERSA:\n{context}" if context else ""
    
    if tool_name == "get_invoice" and "invoice" in tool_result:
        inv = tool_result["invoice"]
        prompt = f"""Responde como assistente de atendimento de uma empresa de energia em Portugal.{context_section}

PERGUNTA ATUAL DO CLIENTE: "{user_query}"

DADOS DA FATURA:
- Número: {inv['number']}
- Valor: €{inv['amount']}
- Data: {inv['date']}
- Consumo: {inv['consumption_kwh']} kWh
- Estado: {'paga' if inv['status'] == 'paid' else 'pendente'}

INSTRUÇÕES:
- Responde APENAS com a mensagem ao cliente (usa o contexto anterior se relevante)
- Em português de Portugal
- Máximo 2-3 frases
- Tom amigável e profissional
- Resposta direta e natural"""
        
        # LLM ativado com Claude Opus
        llm_response = call_llm(prompt)
        if llm_response:
            return llm_response
        
        # Fallback em português
        status_pt = "paga" if inv['status'] == 'paid' else "pendente"
        return f"A sua fatura {inv['number']} no valor de €{inv['amount']} foi emitida em {inv['date']}. O consumo foi de {inv['consumption_kwh']} kWh e o estado é {status_pt}."
    
    elif tool_name == "get_consumption":
        prompt = f"""Responde como assistente de atendimento de uma empresa de energia em Portugal.{context_section}

PERGUNTA ATUAL DO CLIENTE: "{user_query}"

DADOS DE CONSUMO: {json.dumps(tool_result, ensure_ascii=False)}

INSTRUÇÕES:
- Responde APENAS com a mensagem ao cliente (usa o contexto anterior se relevante)
- Em português de Portugal
- Máximo 2-3 frases
- Tom amigável e profissional
- Resposta direta sobre o consumo de energia"""
        
        # LLM ativado com Claude Opus
        llm_response = call_llm(prompt)
        if llm_response:
            return llm_response
        
        return "Já obtive os dados do seu consumo. Pode consultar os detalhes acima."
    
    # Caso 'general' - conversa sem dados específicos, apenas contexto
    elif tool_name == 'general':
        prompt = f"""Responde como assistente de atendimento de uma empresa de energia em Portugal.{context_section}

PERGUNTA ATUAL DO CLIENTE: "{user_query}"

INSTRUÇÕES:
- Responde de forma natural e contextual (usa o histórico anterior)
- Em português de Portugal
- Máximo 2-3 frases
- Tom amigável e profissional
- Continua a conversa de forma coerente com o contexto anterior"""
        
        llm_response = call_llm(prompt)
        if llm_response:
            return llm_response
        
        return "Entendido. Posso ajudar com mais alguma questão?"

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
                context = data.get('context', '')  # Histórico da conversa
                
                # Enhance with LLM (com contexto)
                enhanced = enhance_response(user_message, tool_result, tool_name, context)
                
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
    print("🧠 LLM Bridge running on http://localhost:8081")
    print("Enhancing responses with natural language generation...")
    server.serve_forever()
