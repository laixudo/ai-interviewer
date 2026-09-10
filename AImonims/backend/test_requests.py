import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DOUBAO_API_KEY")
MODEL = os.getenv("DOUBAO_MODEL", "doubao-seed-2-0-pro-260215")
BASE_URL = os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")

def generate_response_simple(prompt, max_tokens=50):
    url = f"{BASE_URL}/chat/completions"

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }

    print(f"Sending request to {url}...")
    response = requests.post(url, headers=headers, json=data, timeout=60)
    print(f"Status: {response.status_code}")

    result = response.json()
    return result['choices'][0]['message']['content']

if __name__ == "__main__":
    print("Testing with requests library...")
    result = generate_response_simple("Say hello in 3 words", max_tokens=20)
    print(f"Result: {result}")
