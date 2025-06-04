from flask import Flask, request, Response
import openai
import os
import requests
from datetime import datetime
import uuid
import json

# ElevenLabs + Supabase credentials
SUPABASE_URL = "https://kaphgvwfgycfgpxponmw.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    user_msg = request.form.get('Body', '').strip().lower()
    print("Incoming message:", user_msg)

    if user_msg in ['restart', 'reiniciar', 'oi', 'olá', 'hello', 'hi']:
        reply = """
        <Response>
          <Message>
            Obrigado por entrar em contato com o Bot de Aprendizado de Inglês da COP30. 🌟

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
        phrase = "Where is the hotel?"
        translated = "Onde fica o hotel?"
        create_and_store_audio("last", phrase)
        reply = f"""
        <Response>
          <Message>
            Frase útil:  
            🇺🇸 “{phrase}”  
            🇧🇷 “{translated}”
            
            Se quiser ouvir a pronúncia, digite *falar*.
          </Message>
        </Response>
        """

    elif user_msg == '2':
        phrase = "Airport. Passport."
        vocab = "Airport = Aeroporto\nPassport = Passaporte"
        create_and_store_audio("last", phrase)
        reply = f"""
        <Response>
          <Message>
            Vocabulário do dia:  
            🇺🇸 {vocab}
            
            Se quiser ouvir a pronúncia, digite *falar*.
          </Message>
        </Response>
        """

    elif user_msg == '3':
        reply = """
        <Response>
          <Message>
            Conectando com o Instrutor de IA...
            Envie sua dúvida em inglês ou português 👇
            *Se quiser ouvir a pronúncia de algo, digite "falar" depois.*
          </Message>
        </Response>
        """

    elif user_msg == 'falar':
        audio_url = retrieve_audio_url()
        if audio_url:
            reply = f"""
            <Response>
              <Message>
                Aqui está a pronúncia: {audio_url}
              </Message>
            </Response>
            """
        else:
            reply = """
            <Response>
              <Message>
                Desculpe, não encontrei uma pronúncia recente. Tente novamente após escolher uma frase ou palavra.
              </Message>
            </Response>
            """

    else:
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um instrutor de inglês para brasileiros que estão se preparando para a COP30. Sempre responda em português com frases curtas e simples em inglês, e foque em saudações, turismo, cultura local e interações reais. Reconheça o nível de inglês e adapte seu ensino."},
                    {"role": "user", "content": user_msg}
                ]
            )
            bot_reply = response.choices[0].message.content.strip()

            # Extract English portion for pronunciation
            english_line = next((line for line in bot_reply.split('\n') if line.strip().startswith('"') or line.strip().startswith("“")), bot_reply)
            clean_english = english_line.strip('"“”') if english_line else bot_reply
            create_and_store_audio("last", clean_english)

            reply = f"""
            <Response>
              <Message>
                {bot_reply}
                *Digite \"falar\" se quiser ouvir a pronúncia.*
              </Message>
            </Response>
            """
        except Exception as e:
            print("Erro GPT:", e)
            reply = f"""
            <Response>
              <Message>
                Ocorreu um erro ao falar com o Instrutor de IA: {str(e)}
              </Message>
            </Response>
            """

    return Response(reply.strip(), mimetype='text/xml')

def create_and_store_audio(tag, text):
    audio_response = requests.post(
        "https://api.elevenlabs.io/v1/text-to-speech/Rachel",
        headers={
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
    )

    audio_filename = f"audio_{uuid.uuid4()}.mp3"
    with open(audio_filename, "wb") as f:
        f.write(audio_response.content)

    with open(audio_filename, "rb") as f:
        file_data = f.read()
        upload_url = f"{SUPABASE_URL}/storage/v1/object/audio/{audio_filename}"
        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/octet-stream"
        }
        requests.put(upload_url, headers=headers, data=file_data)

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/audio/{audio_filename}"

    metadata = {
        "user_message": tag,
        "audio_url": public_url,
        "created_at": datetime.utcnow().isoformat()
    }
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    requests.post(f"{SUPABASE_URL}/rest/v1/audio_responses", headers=headers, data=json.dumps(metadata))

def retrieve_audio_url():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    response = requests.get(f"{SUPABASE_URL}/rest/v1/audio_responses?select=audio_url&user_message=eq.last&order=created_at.desc&limit=1", headers=headers)
    if response.ok and response.json():
        return response.json()[0]['audio_url']
    return None
