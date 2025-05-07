from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()



import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


prompt = "10 car names"

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt
        },
    ],
    model="gpt-3.5-turbo"
)

print(chat_completion.choices[0].message.content)
