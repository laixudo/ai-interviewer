import requests
import json

print('=== 测试新面试流程 ===')

# Step 1: 开始5分钟面试（应该只有2个问题）
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
print(f'Status: {resp.status_code}')
result = resp.json()
interview_id = result.get('interview_id')
print(f'面试ID: {interview_id}')
print(f'开场白: {result.get("initial_question", "")[:100]}...')

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
print(f'AI 点评: {result.get("comment", "")}')
print(f'AI 追问: {result.get("followup", "")[:100]}...' if result.get("followup") else "无")
print(f'问题计数: {result.get("question_count")}/{result.get("question_limit")}')
print(f'面试结束: {result.get("is_interview_over")}')

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
print(f'AI 点评: {result.get("comment", "")}')
print(f'AI 追问: {result.get("followup", "")[:100] if result.get("followup") else "无"}...')
print(f'问题计数: {result.get("question_count")}/{result.get("question_limit")}')
print(f'面试结束: {result.get("is_interview_over")}')
print(f'评估报告: {"有" if result.get("evaluation_report") else "无"}')
if result.get("evaluation_report"):
    print(f'评估报告内容: {json.dumps(result.get("evaluation_report"), ensure_ascii=False, indent=2)[:500]}...')
