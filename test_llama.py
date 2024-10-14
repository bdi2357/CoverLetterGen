import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file where you store your Llama API key
load_dotenv('.env', override=True)
llama_api_key = os.getenv('LLAMA_API_KEY')

def llama_chat_request(message):
    url = "https://api.llama.ai/v1/chat"  # Replace this with Meta's Llama API endpoint
    headers = {
        "Authorization": f"Bearer {llama_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3.2-3b",
        "messages": [{"role": "user", "content": message}]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    response = llama_chat_request("Hello, how are you today?")
    if response:
        print(response)
