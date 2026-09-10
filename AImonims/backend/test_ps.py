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

    ps_script = f'''
    $headers = @{{"Authorization"="Bearer {API_KEY}";"Content-Type"="application/json"}}
    $body = '{json.dumps(data, ensure_ascii=False)}'
    $response = Invoke-WebRequest -Uri "{url}" -Method Post -Headers $headers -Body $body -TimeoutSec 30
    $response.Content
    '''

    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    try:
        response = json.loads(result.stdout.strip())
        return response['choices'][0]['message']['content']
    except:
        print(f"Failed to parse response: {result.stdout[:200]}")
        return None

if __name__ == "__main__":
    print("Testing with PowerShell...")
    result = generate_response_simple("Say hello in 3 words", max_tokens=50)
    print(f"Result: {result}")
