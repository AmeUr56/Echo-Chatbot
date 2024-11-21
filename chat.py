from huggingface_hub import InferenceClient              
import requests
import os
from dotenv import load_dotenv

try:
    client = InferenceClient(api_key=os.getenv('HUGGINGFACE_API_KEY1'))
except:
    client = InferenceClient(api_key=os.getenv('HUGGINGFACE_API_KEY2'))
    
'''
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-base"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read() 

    response = requests.post(API_URL, headers=headers, data=data) 
    return response.json()
'''

prompt = [
        {
        "role": "system",
        "content": "."
        }
    ]

def activate_echo():
    client.chat.completions.create(
        model="Qwen/Qwen2.5-1.5B-Instruct",
        messages=prompt
    )

def echo_response(conversation_history,user_input):
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-1.5B-Instruct",
        messages=conversation_history,
        max_tokens=500,
        stream=True
    )
    assistant_reply = []
    for chunk in response:
        word = chunk.choices[0].delta.content
        assistant_reply += [word]

        yield word

    assistant_reply = "".join(assistant_reply)

    conversation_history.append({
        "role": "assistant",
        "content": assistant_reply
    })