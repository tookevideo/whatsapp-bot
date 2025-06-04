from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    user_msg = request.form.get('Body', '').strip().lower()
    print("Incoming message:", user_msg)

    # Start every reply with this greeting
    reply = """
<Response>
  <Message>
    Obrigado por entrar em contato com o Bot de Aprendizado de Inglês da COP30. 🇧🇷🇺🇸
    
    Você está pronto para começar?  
    *Responda com "Sim" para continuar.*
  </Message>
"""

    # Add specific responses depending on the user message
    if user_msg in ['sim', 'yes', 'claro']:
        reply += """
  <Message>
    Escolha uma opção para começar:
    1️⃣ Frases úteis
    2️⃣ Vocabulário
    3️⃣ Falar com o Instrutor de IA 🤖
  </Message>
"""
    elif user_msg == '1':
        reply += """
  <Message>
    Frase útil:  
    🇺🇸 “Where is the hotel?”  
    🇧🇷 “Onde fica o hotel?”
  </Message>
"""
    elif user_msg == '2':
        reply += """
  <Message>
    Vocabulário do dia:  
    🇺🇸 Airport = Aeroporto  
    🇺🇸 Passport = Passaporte
  </Message>
"""
    elif user_msg == '3':
        reply += """
  <Message>
    Conectando com o Instrutor de IA...  
    Envie sua dúvida em inglês ou português 👇
  </Message>
"""
    elif user_msg in ['restart', 'reiniciar']:
        # Already included in the default message above, so no additional message needed
        pass
    else:
        reply += """
  <Message>
    Desculpe, não entendi. Responda com o número da opção desejada (1, 2 ou 3).
  </Message>
"""

    reply += "</Response>"
    return Response(reply.strip(), mimetype='text/xml')
