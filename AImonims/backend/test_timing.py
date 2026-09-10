import requests
import time

# 创建一个新面试
print('=== 创建面试 ===')
resp = requests.post(
    'http://localhost:8001/api/interview/start?user_id=1',
    json={
        "position": "Java工程师",
        "job_type": "java_backend",
        "round": "第一轮",
        "interviewer_role": "技术面试官",
        "pressure_level": 1,
        "duration": 5,
        "experience": "1-3年",
        "resume_text": "",
        "target_company": ""
    },
    timeout=30
)
result = resp.json()
interview_id = result.get('interview_id')
print(f'面试ID: {interview_id}')

# 发送消息并立即检查
print('\n=== 发送第1条消息 ===')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '测试消息1',
        'interview_id': interview_id
    },
    timeout=60
)
result = resp.json()
print(f'question_count: {result.get("question_count")}')
print(f'is_interview_over: {result.get("is_interview_over")}')

time.sleep(1)  # 等待

# 发送第2条消息
print('\n=== 发送第2条消息 ===')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '测试消息2',
        'interview_id': interview_id
    },
    timeout=60
)
result = resp.json()
print(f'question_count: {result.get("question_count")}')
print(f'is_interview_over: {result.get("is_interview_over")}')
