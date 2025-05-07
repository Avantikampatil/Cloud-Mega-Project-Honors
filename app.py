from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_message():
    data = request.get_json()
    user_message = data.get('user_message', '')

    try:
        # Translate input to Marathi
        translated_response = translator.translate(user_message, dest='mr').text
        return jsonify({'bot_response': translated_response})
    except Exception as e:
        return jsonify({'bot_response': f'Error: {str(e)}'})

@app.route('/listen', methods=['POST'])
def listen_message():
    data = request.get_json()
    bot_response = data.get('bot_response', '')
    
    try:
        # Convert the response into speech (we will handle this in frontend)
        # For simplicity, we don't need to add anything extra on the backend for speech synthesis.
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
