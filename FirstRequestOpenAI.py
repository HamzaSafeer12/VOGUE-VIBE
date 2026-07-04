from dotenv import load_dotenv
import os
from openai import OpenAI, OpenAIError

# .env file load
# load_dotenv()

# # API key read
# api_key = os.getenv("OPENAI_API_KEY")

# # OpenAI client
# client = OpenAI(api_key=api_key)

# try:
#     user_input = input("AI se kya poochna hai? : ")

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": user_input}]
#     )

#     print("\nAI ka jawab:\n")
#     print(response.choices[0].message.content)

# except OpenAIError as e:
#     print("OpenAI error:", e)
# except Exception as e:
#     print("General error:", e)
#    ************************************************************************************** 


# OLLAMA KA USE KIYA HM NY API K THROUGH
import requests
import json

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "tinyllama",
        "prompt": "Python kya hai?"
    },
    stream=True  # stream mode important hai
)

full_text = ""

for line in response.iter_lines():
    if line:
        data = json.loads(line)  # ek line ko parse karo
        full_text += data.get("response", "")

print(full_text)


