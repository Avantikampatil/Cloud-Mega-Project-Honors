from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
translator = Translator()


@app.route('/opeaicall', methods=['POST'])
def openai_call():
    import os
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    user_message = request.json['user_message']

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_message
            },
        ],
        model="gpt-3.5-turbo"
    )
    return jsonify({'bot_response': chat_completion.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True)