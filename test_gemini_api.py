import pathlib
import textwrap

import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv('.env', override=True)
google_api_key = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

if __name__ == "__main__":
    prompt = "pi 5 numbers after the decimal point"
    print(model.generate_content(prompt).text)
    prompt = "what architecture is better and why ChatGPT or BERT"
    print(model.generate_content(prompt).text)