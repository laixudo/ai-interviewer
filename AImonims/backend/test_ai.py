import requests
import json

payload = {
    'content': '面试官您好！我是一名专注于Java 后端开发的求职者，熟练掌握 Java 核心语法、Spring Boot快速开发后端接口、多线程与并发编程，熟悉 MySQL 数据库设计。在实践方面，我独立参与了AI 模拟面试系统的完整开发。',
    'interview_id': 18
}

print('发送请求测试 AI 追问...')
resp = requests.post('http://localhost:8000/api/interview/message', json=payload, timeout=30)
result = resp.json()

print(f'状态码: {resp.status_code}')
print(f'AI 追问: {result.get("response")}')
