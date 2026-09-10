import os
os.environ['NO_CACHE'] = '1'

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import time

client = OpenAI(
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url=os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")
)

print("Testing direct API call...")
start = time.time()

try:
    response = client.chat.completions.create(
        model=os.getenv("DOUBAO_MODEL", "doubao-seed-2-0-pro-260215"),
        messages=[
            {"role": "system", "content": "你是一位友好的AI助手"},
            {"role": "user", "content": "你好，请回复'测试成功'"}
        ],
        temperature=0.7,
        max_tokens=100,
        timeout=5
    )
    print(f"Success! Response: {response.choices[0].message.content}")
    print(f"Time: {time.time() - start:.2f}s")
except Exception as e:
    print(f"Error: {e}")
    print(f"Time: {time.time() - start:.2f}s")
