from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    user_msg = request.form.get('Body', 'No message received.')
    print("Incoming message:", user_msg)

    reply = """
    <Response>
      <Message>
        Obrigado por entrar em contato com o Bot de Aprendizado de Inglês da COP30. 🇧🇷

        Você está pronto para começar a aprender?
      </Message>
    </Response>
    """
    return Response(reply.strip(), mimetype='text/xml')
