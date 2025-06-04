from flask import Flask, request, Response
import openai
import os
import requests
from supabase import create_client, Client

# --- Configuration ---
openai.api_key = os.getenv("OPENAI_API_KEY")  # Set your API Key in Render Environment Variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
SUPABASE_URL = "https://kaphgvwfgycfgpxponmw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Truncated for clarity
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- App Setup ---
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    user_msg = request.form.get('Body', '').strip().lower()
    print("Incoming message:", user_msg)

    # Default greeting
    if user_msg in ['restart', 'reiniciar', 'oi', 'olá', 'hello', 'hi'] or user_msg == "":
        reply = """
        <Response>
          <Message>
            Obrigado por entrar em contato com o Bot de Aprendizado de Inglês da COP30. 🇧🇷🇺🇸

            Você está pronto para começar?  
            *Responda com "Sim" para continuar.*
          </Message>
        </Response>
        """
        return Response(reply.strip(), mimetype='text/xml')

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
        return Response(reply.strip(), mimetype='text/xml')

    elif user_msg == '1':
        phrase = "Where is the hotel?"
        audio_url = generate_audio(phrase)
        reply = f"""
        <Response>
          <Message>
            Frase útil:  
            🇺🇸 {phrase}  
            🇧🇷 “Onde fica o hotel?”
            {audio_url}
          </Message>
        </Response>
        """
        return Response(reply.strip(), mimetype='text/xml')

    elif user_msg == '2':
        vocab = "Airport = Aeroporto\nPassport = Passaporte"
        audio_url = generate_audio("Airport, Passport")
        reply = f"""
        <Response>
          <Message>
            Vocabulário do dia:  
            🇺🇸 {vocab}
            {audio_url}
          </Message>
        </Response>
        """
        return Response(reply.strip(), mimetype='text/xml')

    elif user_msg == '3':
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """Você é um instrutor de inglês para brasileiros que estão se preparando para a COP30. Sempre use o português para explicações e comunicações. Fale em inglês de forma simples, evite frases longas e complicadas. Ensine cumprimentos, como receber visitantes, como fazer pequenas conversas, perguntar se estão gostando da cidade, e aspectos de cultura e turismo de Belém, Pará. Tente perceber o nível de inglês da pessoa e responda de forma apropriada. Nunca envie mensagens longas — sempre mantenha respostas curtas e práticas."""},
                    {"role": "user", "content": "Olá, quero aprender inglês."}
                ]
            )
            bot_response = response.choices[0].message.content.strip()
        except Exception as e:
            bot_response = f"Ocorreu um erro ao falar com o Instrutor de IA: {e}"

        reply = f"""
        <Response>
          <Message>{bot_response}</Message>
        </Response>
        """
        return Response(reply.strip(), mimetype='text/xml')

    else:
        reply = """
        <Response>
          <Message>
            Desculpe, não entendi.  
            Responda com "1", "2" ou "3" para continuar, ou "Reiniciar" para começar do início.
          </Message>
        </Response>
        """
        return Response(reply.strip(), mimetype='text/xml')


def generate_audio(text):
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    voice_id = "EXAVITQu4vr4xnSDxMaL"  # Default voice
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        audio_data = response.content
        filename = f"audio_{text[:10].replace(' ', '_')}.mp3"
        file_path = f"public/{filename}"

        # Upload to Supabase bucket
        supabase.storage.from_("audio").upload(file_path, audio_data, {"content-type": "audio/mpeg"})
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/audio/{filename}"
        return f"🔊 Ouça: {public_url}"
    else:
        return "(Erro ao gerar áudio.)"


if __name__ == '__main__':
    app.run(debug=True)
