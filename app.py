from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Para permitir requisições do frontend


# CONFIGURAÇÃO DE TREINAMENTO - PERSONALIZE AQUI
COMPANY_CONFIG = {
    'company_name': 'Tochique',
    # ecommerce, tech, finance, health, education, retail, services, restaurant
    'business_type': ('Cordões de altaqualidade banhados em ouro com '
                      'garantia de 30 dias'),
    'custom_instructions': '''
    - Sempre seja educado e prestativo
    - Mencione nossa garantia de 30 dias cobre os seguintes casos:
      descoloração, manchas, perda de banho, defeitos de fabricação
      caso seja relevante
    - Ofereça suporte técnico especializado
    - Se não souber algo, encaminhe para nossa equipe técnica
    - Use emojis moderadamente para deixar a conversa amigável
    - mensione o agendamento pessoal caso a pessoa solisite, envie como
      um link clicavel mais chamativo:
      <a href="https://calendar.app.google/qNYjwZzu5iewu6Cs6">
      -> clicar aqui <- </a> e nosso telefone (32) 98881-1234
    ''',
    'work_hours': 'Segunda a Sexta, 8h às 18h',
    'contact_phone': '(32) 98881-1234',
    'contact_email': 'acessoria@tochique.com.br',
    'website': 'www.tochique.com.br',
}

# Sua chave da API Gemini
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
                  f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}")

# Base de conhecimento por tipo de negócio
BUSINESS_KNOWLEDGE = {
    'ecommerce': {
        'specialty': 'vendas online, pedidos, entregas e produtos',
        'common_topics': ['pedido', 'entrega', 'produto', 'pagamento',
                          'devolução', 'troca', 'desconto', 'frete'],
        'greeting_style': ('Sou especializado em e-commerce e posso ajudar com '
                           'pedidos, produtos, entregas e muito mais! 🛒')
    },
    'tech': {
        'specialty': 'tecnologia, software, suporte técnico e implementações',
        'common_topics': ['instalação', 'licença', 'erro', 'suporte',
                          'atualização', 'configuração', 'bug', 'integração'],
        'greeting_style': ('Sou o suporte técnico especializado e estou aqui para '
                           'resolver problemas técnicos, licenças e instalações! 💻')
    },
    'finance': {
        'specialty': 'serviços financeiros, conta, investimentos e transações',
        'common_topics': ['conta', 'saldo', 'cartão', 'empréstimo',
                          'investimento', 'transferência', 'taxa', 'financiamento'],
        'greeting_style': ('Posso ajudar com sua conta, investimentos, cartões e '
                           'todos nossos serviços financeiros! 💰')
    },
    'health': {
        'specialty': 'saúde, consultas, exames e agendamentos médicos',
        'common_topics': ['consulta', 'exame', 'agendamento', 'médico',
                          'resultado', 'convênio', 'especialista', 'receita'],
        'greeting_style': ('Posso ajudar com agendamentos, consultas, exames e '
                           'informações sobre nossos serviços de saúde! 🏥')
    },
    'education': {
        'specialty': 'educação, cursos, matrículas e ensino',
        'common_topics': ['curso', 'matrícula', 'aula', 'certificado',
                          'professor', 'prova', 'diploma', 'mensalidade'],
        'greeting_style': ('Posso ajudar com cursos, matrículas, aulas e todas as '
                           'informações acadêmicas! 📚')
    },
    'retail': {
        'specialty': 'varejo, produtos, vendas e atendimento em loja',
        'common_topics': ['produto', 'preço', 'promoção', 'estoque',
                          'loja', 'horário', 'desconto', 'garantia'],
        'greeting_style': ('Posso ajudar com produtos, promoções, estoque e '
                           'atendimento da nossa loja! 🏪')
    },
    'services': {
        'specialty': 'prestação de serviços, agendamentos e orçamentos',
        'common_topics': ['serviço', 'agendamento', 'orçamento', 'técnico',
                          'visita', 'contrato', 'garantia', 'prazo'],
        'greeting_style': ('Posso ajudar com nossos serviços, agendamentos, '
                           'orçamentos e contratos! 🔧')
    },
    'restaurant': {
        'specialty': 'restaurante, alimentação, pedidos e reservas',
        'common_topics': ['cardápio', 'pedido', 'delivery', 'reserva',
                          'ingredientes', 'promoção', 'horário', 'mesa'],
        'greeting_style': 'Posso ajudar com cardápio, pedidos, reservas e delivery! 🍽️'
    }
}

def build_system_prompt(user_message=""):  # noqa: ARG001
    """Constrói o prompt personalizado baseado na configuração"""

    config = COMPANY_CONFIG
    business_info = BUSINESS_KNOWLEDGE.get(config['business_type'], {})

    system_prompt = f"""
Você é o assistente virtual da empresa "{config['company_name']}"
especializada em {business_info.get('specialty', config['business_type'])}.

INFORMAÇÕES DA EMPRESA:
- Nome: {config['company_name']}
- Especialidade: {business_info.get('specialty', 'atendimento geral')}
- Telefone: {config['contact_phone']}
- Email: {config.get('contact_email', 'N/A')}
- Site: {config.get('website', 'N/A')}
- Horário: {config['work_hours']}

INSTRUÇÕES ESPECÍFICAS:
{config['custom_instructions']}

TÓPICOS COMUNS QUE VOCÊ DOMINA:
{', '.join(business_info.get('common_topics', ['atendimento geral']))}

DIRETRIZES DE COMPORTAMENTO:
- Seja sempre educado, prestativo e profissional
- Responda em português brasileiro
- Use o nome da empresa quando apropriado
- Se não souber algo específico, seja honesto e ofereça alternativas
- Forneça informações de contato quando necessário
- Mantenha respostas concisas mas completas
- Use emojis moderadamente para deixar a conversa amigável
- Sempre tente resolver o problema do cliente da melhor forma

Se o cliente perguntar sobre algo que você não tem informação específica
da empresa, seja transparente e ofereça os canais de contato:
{config['contact_phone']} ou {config.get('contact_email', 'nosso email')}.
"""

    return system_prompt


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal do chat com treinamento personalizado integrado"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Construir prompt personalizado
        system_prompt = build_system_prompt(user_message)
        full_message = (system_prompt +
                        f"\n\nPergunta do cliente: {user_message}")
        
        # Chamar API Gemini
        response = requests.post(GEMINI_API_URL,
                                 headers={'Content-Type': 'application/json'},
                                 json={
                                     "contents": [{
                                         "role": "user",
                                         "parts": [{"text": full_message}]
                                     }],
                                     "generationConfig": {
                                         "temperature": 0.7,
                                         "maxOutputTokens": 1000,
                                         "topK": 40,
                                         "topP": 0.95
                                     }
                                 },
                                 timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API Gemini retornou status "
                           f"{response.status_code}")
        
        gemini_data = response.json()
        
        # Extrair resposta da IA
        if (gemini_data.get('candidates') and
            len(gemini_data['candidates']) > 0 and
            gemini_data['candidates'][0].get('content') and
            gemini_data['candidates'][0]['content'].get('parts') and
            len(gemini_data['candidates'][0]['content']['parts']) > 0):
            
            ai_response = (gemini_data['candidates'][0]['content']['parts'][0]
                           ['text'])
        else:
            # Fallback para erro da IA
            config = COMPANY_CONFIG
            ai_response = "Desculpe, não consegui processar sua solicitação no momento. "
            ai_response += (f"Para atendimento imediato, entre em contato pelo "
                            f"telefone {config['contact_phone']}")
            if config.get('contact_email'):
                ai_response += f" ou pelo email {config['contact_email']}"
            ai_response += (f". Nosso horário de atendimento é "
                           f"{config['work_hours']}.")
        
        # Log da conversa (opcional)
        print(f"[{datetime.now()}] User: {user_message}")
        print(f"[{datetime.now()}] Bot: {ai_response[:100]}...")
        
        return jsonify({'response': ai_response})

    except requests.exceptions.Timeout:
        return jsonify({'response': ('Desculpe, o tempo de resposta excedeu o '
                                    'limite. Tente novamente.')}), 500

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        config = COMPANY_CONFIG
        error_msg = "Estou com dificuldades técnicas no momento. "
        error_msg += (f"Por favor, entre em contato pelo telefone "
                      f"{config['contact_phone']} para atendimento imediato.")
        return jsonify({'response': error_msg}), 500

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({'response': ('Erro interno do servidor. Tente novamente '
                                    'mais tarde.')}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'ok',
        'company': COMPANY_CONFIG['company_name'],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Endpoint para obter configurações básicas (sem dados sensíveis)"""
    return jsonify({
        'company_name': COMPANY_CONFIG['company_name'],
        'business_type': COMPANY_CONFIG['business_type'],
        'work_hours': COMPANY_CONFIG['work_hours'],
        'contact_phone': COMPANY_CONFIG['contact_phone']
    })


if __name__ == '__main__':
    print(f"Iniciando chatbot para: {COMPANY_CONFIG['company_name']}")
    print(f"Tipo de negócio: {COMPANY_CONFIG['business_type']}")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 
