from flask import Flask, request, Response
import os
import openai

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

# Track user session (simple memory)
user_state = {}

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    user_msg = request.form.get('Body', '').strip().lower()
    from_number = request.form.get('From', '')
    print("Incoming message:", user_msg)

    global user_state
    state = user_state.get(from_number, "initial")

    # Restart conversation
    if user_msg in ['restart', 'reiniciar']:
        user_state[from_number] = "initial"
        reply = """<Response><Message>Obrigado por entrar em contato com o Bot de Aprendizado de Inglês da COP30. 🇧🇷🇺🇸\n\nVocê está pronto para começar?\n*Responda com "Sim" para continuar.*</Message></Response>"""
    
    elif state == "initial":
        user_state[from_number] = "menu"
        reply = """<Response><Message>Escolha uma opção para começar:\n1️⃣ Frases úteis\n2️⃣ Vocabulário\n3️⃣ Falar com o Instrutor de IA 🤖</Message></Response>"""
    
    elif user_msg in ['sim', 'yes', 'claro']:
        user_state[from_number] = "menu"
        reply = """<Response><Message>Escolha uma opção para começar:\n1️⃣ Frases úteis\n2️⃣ Vocabulário\n3️⃣ Falar com o Instrutor de IA 🤖</Message></Response>"""

    elif state == "menu":
        if user_msg == '1':
            reply = """<Response><Message>Frase útil:\n🇺🇸 “Where is the hotel?”\n🇧🇷 “Onde fica o hotel?”</Message></Response>"""
        elif user_msg == '2':
            reply = """<Response><Message>Vocabulário do dia:\n🇺🇸 Airport = Aeroporto\n🇺🇸 Passport = Passaporte</Message></Response>"""
        elif user_msg == '3':
            user_state[from_number] = "chatgpt"
            reply = """<Response><Message>Conectando com o Instrutor de IA...\nEnvie sua dúvida em inglês ou português 👇</Message></Response>"""
        else:
            reply = """<Response><Message>Desculpe, não entendi. Responda com 1, 2 ou 3.</Message></Response>"""
    
    elif state == "chatgpt":
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um instrutor de inglês para brasileiros que estão se preparando para a COP30."},
                    {"role": "user", "content": user_msg}
                ]
            )
            answer = completion['choices'][0]['message']['content'].strip()
        except Exception as e:
            answer = f"Ocorreu um erro ao falar com o Instrutor de IA: {e}"

        reply = f"""<Response><Message>{answer}</Message></Response>"""

    else:
        # fallback to intro if unknown state
        user_state[from_number] = "initial"
        reply = """<Response><Message>Obrigado por entrar em contato com o Bot de Aprendizado de Inglês da COP30. 🇧🇷🇺🇸\n\nVocê está pronto para começar?\n*Responda com "Sim" para continuar.*</Message></Response>"""

    return Response(reply.strip(), mimetype='text/xml')
