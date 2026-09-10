import sys
sys.path.insert(0, '.')

from main import generate_answer_comment_and_followup
import time

print('=== 测试 generate_answer_comment_and_followup ===')

question = "请做自我介绍"
user_answer = "我是一名Java后端开发者，熟练掌握Spring Boot、MySQL、多线程编程。"

history = [
    {"role": "assistant", "content": "你好！我是AI面试官，今天将对你进行Java工程师岗位的面试。"},
    {"role": "user", "content": "面试官您好！我准备开始了。"}
]

print('调用 AI...')
start = time.time()
result = generate_answer_comment_and_followup(question, user_answer, history)
print(f'耗时: {time.time() - start:.2f}秒')

print(f'\n结果:')
print(f'  comment: {result.get("comment")}')
print(f'  followup: {result.get("followup")}')
