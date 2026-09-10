import sys
sys.path.insert(0, '.')

from main import process_interview
import time

print('Testing process_interview...')
start = time.time()

# 测试 with conversation history
history = [
    {"role": "assistant", "content": "你好！我是AI面试官，今天将对你进行Java工程师岗位的面试。"},
    {"role": "user", "content": "面试官您好！我是一名专注于Java后端开发的求职者，熟练掌握Spring Boot。"}
]

result = process_interview("请做自我介绍", "我擅长Java Spring Boot开发", history)

print(f'Time: {time.time() - start:.2f}s')
print('Result keys:', result.keys())
print('followup:', result.get('followup'))
