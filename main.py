from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    user_msg = data.get('Body', 'No message received.')
    print("Incoming message:", user_msg)
    return jsonify({"reply": f"You said: {user_msg}"})

if __name__ == '__main__':
    app.run()
