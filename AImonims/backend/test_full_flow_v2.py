import requests
import json

print('=== 测试新面试流程（含候选人提问环节）===')

# 10分钟面试（3个问题 + 2个候选人提问）
print('\n--- Step 1: 开始10分钟面试 ---')
resp = requests.post(
    'http://localhost:8001/api/interview/start?user_id=1',
    json={
        "position": "Java工程师",
        "job_type": "java_backend",
        "round": "第一轮",
        "interviewer_role": "技术面试官",
        "pressure_level": 1,
        "duration": 10,
        "experience": "1-3年",
        "resume_text": "",
        "target_company": ""
    },
    timeout=30
)
result = resp.json()
interview_id = result.get('interview_id')
print(f'面试ID: {interview_id}')
print(f'开场白: {result.get("initial_question", "")[:80]}...')

# Step 2: 用户回答第1次
print('\n--- Step 2: 用户回答第1次 ---')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '我是一名Java后端开发者，熟练掌握Spring Boot、MySQL。',
        'interview_id': interview_id
    },
    timeout=60
)
result = resp.json()
print(f'AI点评: {result.get("comment", "")[:60]}...')
print(f'AI追问: {result.get("followup", "")[:60]}...')
print(f'问题计数: {result.get("question_count")}/{result.get("question_limit")}')

# Step 3: 用户回答第2次
print('\n--- Step 3: 用户回答第2次 ---')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '我在项目中使用过Redis做缓存，MySQL做存储。',
        'interview_id': interview_id
    },
    timeout=60
)
result = resp.json()
print(f'AI点评: {result.get("comment", "")[:60]}...')
print(f'AI追问: {result.get("followup", "")[:60]}...')
print(f'问题计数: {result.get("question_count")}/{result.get("question_limit")}')

# Step 4: 用户回答第3次（应该进入候选人提问环节）
print('\n--- Step 4: 用户回答第3次（进入候选人提问环节）---')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '我熟悉多线程编程，在项目中用过线程池。',
        'interview_id': interview_id
    },
    timeout=60
)
result = resp.json()
print(f'AI回应: {result.get("response", "")[:100]}...')
print(f'候选人提问环节: {result.get("is_candidate_question_phase")}')
print(f'面试结束: {result.get("is_interview_over")}')

# Step 5: 候选人提问第1次
print('\n--- Step 5: 候选人提问第1次 ---')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '请问这个岗位的培养机制是怎样的？',
        'interview_id': interview_id
    },
    timeout=60
)
result = resp.json()
print(f'AI回答: {result.get("response", "")[:100]}...')
print(f'面试结束: {result.get("is_interview_over")}')

# Step 6: 候选人提问第2次（应该结束面试）
print('\n--- Step 6: 候选人提问第2次（面试结束）---')
resp = requests.post(
    'http://localhost:8001/api/interview/message',
    json={
        'content': '请问团队的技术栈是什么？',
        'interview_id': interview_id
    },
    timeout=90
)
result = resp.json()
print(f'AI回答: {result.get("response", "")[:100]}...')
print(f'面试结束: {result.get("is_interview_over")}')
print(f'评估报告: {"有" if result.get("evaluation_report") else "无"}')
