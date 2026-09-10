import requests
import json

print('=== 测试新面试流程（完整输出） ===')

# Step 1: 开始5分钟面试
print('\n--- Step 1: 开始5分钟面试 ---')
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

# Step 2: 用户回答第1次
print('\n--- Step 2: 用户回答第1次 ---')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '我是一名Java后端开发者，熟练掌握Spring Boot、MySQL、多线程编程。',
        'interview_id': interview_id
    },
    timeout=60
)
result = resp.json()
print(f'完整返回: {json.dumps(result, ensure_ascii=False, indent=2)}')

# Step 3: 用户回答第2次（应该结束面试）
print('\n--- Step 3: 用户回答第2次（面试应该结束） ---')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '我在项目中用过Spring Boot开发REST接口，使用MySQL存储数据，多线程用于处理并发请求。',
        'interview_id': interview_id
    },
    timeout=90
)
result = resp.json()
print(f'完整返回: {json.dumps(result, ensure_ascii=False, indent=2)}')
