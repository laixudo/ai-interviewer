import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DOUBAO_API_KEY")
MODEL = os.getenv("DOUBAO_MODEL", "doubao-seed-2-0-pro-260215")
BASE_URL = os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")

def generate_response_simple(prompt, max_tokens=100):
    url = f"{BASE_URL}/chat/completions"

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }

    cmd = [
        'curl', '-s', '-X', 'POST', url,
        '-H', f'Authorization: Bearer {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(data)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    response = json.loads(result.stdout)
    return response['choices'][0]['message']['content']

if __name__ == "__main__":
    print("Testing with curl...")
    result = generate_response_simple("Say hello in 3 words", max_tokens=50)
    print(f"Result: {result}")
