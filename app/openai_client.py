import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(user_input):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content.strip()
