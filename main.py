import os
from flask import Flask, request, Response
from openai import OpenAI

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    user_msg = request.form.get('Body', '').strip().lower()
    print("Incoming message:", user_msg)

    # Always start with welcome message
    if user_msg in ['restart', 'reiniciar', 'oi', 'olá', 'hello', 'hi']:
        reply = """
        <Response>
          <Message>
            Obrigado por entrar em contato com o Bot de Aprendizado de Inglês da COP30. 🇧🇷🇺🇸

            Você está pronto para começar?  
            *Responda com "Sim" para continuar.*
          </Message>
        </Response>
        """

    elif user_msg in ['sim', 'yes', 'claro']:
        reply = """
        <Response>
          <Message>
            Escolha uma opção para começar:
            1️⃣ Frases úteis  
            2️⃣ Vocabulário  
            3️⃣ Falar com o Instrutor de IA 🤖
          </Message>
        </Response>
        """

    elif user_msg == '1':
        reply = """
        <Response>
          <Message>
            Frase útil:  
            🇺🇸 “Where is the hotel?”  
            🇧🇷 “Onde fica o hotel?”
          </Message>
        </Response>
        """

    elif user_msg == '2':
        reply = """
        <Response>
          <Message>
            Vocabulário do dia:  
            🇺🇸 Airport = Aeroporto  
            🇺🇸 Passport = Passaporte
          </Message>
        </Response>
        """

    elif user_msg == '3':
        reply = """
        <Response>
          <Message>
            Conectando com o Instrutor de IA...  
            Envie sua dúvida em inglês ou português 👇
          </Message>
        </Response>
        """

    elif user_msg:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            chat_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um instrutor de inglês para brasileiros que estão se preparando para a COP30."},
                    {"role": "user", "content": user_msg}
                ]
            )
            ai_reply = chat_response.choices[0].message.content.strip()

            reply = f"""
            <Response>
              <Message>{ai_reply}</Message>
            </Response>
            """
        except Exception as e:
            reply = f"""
            <Response>
              <Message>Ocorreu um erro ao falar com o Instrutor de IA: {str(e)}</Message>
            </Response>
            """

    else:
        reply = """
        <Response>
          <Message>
            Desculpe, não entendi. Responda com o número da opção desejada (1, 2 ou 3).
          </Message>
        </Response>
        """

    return Response(reply.strip(), mimetype='text/xml')
