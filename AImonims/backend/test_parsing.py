import sys
sys.path.insert(0, '.')

from main import generate_answer_comment_and_followup
import time

print('=== 测试 AI 返回解析 ===')

test_cases = [
    ("我是一名Java后端开发者，熟练掌握Spring Boot、MySQL。", [
        {"role": "assistant", "content": "你好！我是AI面试官。"}
    ]),
    ("我在项目中使用过Redis缓存。", [
        {"role": "assistant", "content": "你提到熟悉Spring Boot，能说说遇到过哪些问题吗？"}
    ]),
]

for user_answer, history in test_cases:
    print(f'\n用户回答: {user_answer}')
    result = generate_answer_comment_and_followup("自我介绍", user_answer, history)
    print(f'  comment: {result.get("comment")}')
    print(f'  followup: {result.get("followup")}')
    time.sleep(1)
