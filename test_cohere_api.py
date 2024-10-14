import cohere
from dotenv import load_dotenv
import os

load_dotenv('.env', override=True)
cohere_api_key = os.getenv('COHERE_API_KEY')
co = cohere.ClientV2(cohere_api_key)
if __name__ == "__main__":
    response = co.chat(
        model="command-r-plus",
        messages=[
            {
                "role": "user",
                "content": "hello world!"
            }
        ]
    )

    #print(response)
    text_response = response.message.content[0].text
    print(text_response)
