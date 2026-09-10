import requests
import json

print('=== Step 1: 开始新面试 ===')
# user_id 是 query 参数，round 在 body 中
resp = requests.post(
    'http://localhost:8000/api/interview/start?user_id=1',
    json={
        "position": "Java工程师",
        "job_type": "java_backend",
        "round": "第一轮",
        "interviewer_role": "技术面试官",
        "pressure_level": 1,
        "duration": 5,
        "experience": "1-3年",
        "resume_text": "熟悉Java Spring Boot",
        "target_company": ""
    },
    timeout=30
)
print(f'Status: {resp.status_code}')
result = resp.json()
print(f'Response: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}')

interview_id = result.get('interview_id')
if not interview_id:
    print('Failed to create interview')
    exit(1)

print(f'\n=== Step 2: 发送用户回答 ===')
message_payload = {
    'content': '面试官您好！我是一名专注于Java后端开发的求职者，熟练掌握Spring Boot、MySQL、多线程并发编程。',
    'interview_id': interview_id
}

resp = requests.post('http://localhost:8000/api/interview/message', json=message_payload, timeout=60)
print(f'Status: {resp.status_code}')
result = resp.json()
print(f'AI 追问: {result.get("response")}')
print(f'answer_quality: {result.get("answer_quality")}')
