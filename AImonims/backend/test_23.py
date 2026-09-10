import requests
import json

print('=== 直接测试 interview 23 ===')
message_payload = {
    'content': '我是一名Java后端开发者，熟练掌握Spring Boot、MySQL、多线程编程。',
    'interview_id': 23
}

resp = requests.post('http://localhost:8000/api/interview/message', json=message_payload, timeout=60)
print(f'Status: {resp.status_code}')
result = resp.json()
print(f'Full Response: {json.dumps(result, ensure_ascii=False, indent=2)}')
