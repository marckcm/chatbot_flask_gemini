#!/usr/bin/env python3
"""
Script para testar a conexão com a API do Gemini
"""

import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_gemini_connection():
    """Testa a conexão com a API do Gemini"""
    
    # Verificar se a chave API existe
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERRO: Chave API do Gemini não encontrada!")
        print("📝 Crie um arquivo .env na raiz do projeto com:")
        print("   GEMINI_API_KEY=sua_chave_api_aqui")
        print("🔗 Obtenha sua chave em: https://makersuite.google.com/app/apikey")
        return False
    
    if api_key == "sua_chave_api_aqui":
        print("❌ ERRO: Você precisa substituir 'sua_chave_api_aqui' pela sua chave real!")
        return False
    
    print(f"✅ Chave API encontrada: {api_key[:10]}...")
    
    # URL da API
    api_url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-2.0-flash:generateContent?key={api_key}")
    
    # Dados de teste
    test_data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": "Olá! Você está funcionando?"}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 100,
            "topK": 40,
            "topP": 0.95
        }
    }
    
    print("🔄 Testando conexão com a API do Gemini...")
    
    try:
        response = requests.post(
            api_url,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if (data.get('candidates') and 
                len(data['candidates']) > 0 and
                data['candidates'][0].get('content') and
                data['candidates'][0]['content'].get('parts')):
                
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                print("✅ Conexão com Gemini bem-sucedida!")
                print(f"🤖 Resposta da IA: {ai_response}")
                return True
            else:
                print("❌ Resposta da API em formato inesperado")
                print(f"📄 Resposta completa: {data}")
                return False
                
        elif response.status_code == 400:
            print("❌ ERRO 400: Requisição inválida")
            print("🔍 Verifique se a chave API está correta")
            print(f"📄 Resposta: {response.text}")
            return False
            
        elif response.status_code == 403:
            print("❌ ERRO 403: Acesso negado")
            print("🔍 Verifique se a chave API está válida e ativa")
            print(f"📄 Resposta: {response.text}")
            return False
            
        elif response.status_code == 429:
            print("❌ ERRO 429: Limite de requisições excedido")
            print("⏰ Aguarde alguns minutos e tente novamente")
            return False
            
        else:
            print(f"❌ ERRO {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout na conexão")
        print("🌐 Verifique sua conexão com a internet")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Falha na conexão")
        print("🌐 Verifique sua conexão com a internet")
        return False
        
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Conexão com Gemini API")
    print("=" * 40)
    
    success = test_gemini_connection()
    
    print("=" * 40)
    if success:
        print("🎉 Teste concluído com sucesso!")
        print("💡 O chat deve funcionar normalmente agora")
    else:
        print("💥 Teste falhou!")
        print("🔧 Corrija os problemas acima e tente novamente")

