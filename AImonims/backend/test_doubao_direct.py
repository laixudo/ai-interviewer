import os
os.environ['NO_CACHE'] = '1'

import sys
sys.path.insert(0, '.')
from ai.doubao_client import DoubaoClient
import time

client = DoubaoClient()

system_prompt = "你是一位专业的面试官，正在进行Java工程师岗位的面试。根据候选人的回答，生成一个针对性的、深度的后续问题。"

conversation_history = [
    {"role": "assistant", "content": "你好！我是AI面试官，今天将对你进行Java工程师岗位的面试。请先做一个简单的自我介绍。"},
    {"role": "user", "content": "面试官您好！我是一名专注于Java 后端开发的求职者，熟练掌握 Java 核心语法、Spring Boot快速开发后端接口、多线程与并发编程。"}
]

print("Testing generate_response (simpler test)...")
start = time.time()
result2 = client.generate_response(
    system_prompt,
    "面试问题：自我介绍\n候选人回答：我熟练使用Spring Boot开发后端接口\n请生成下一个递进的面试问题。",
    temperature=0.7,
    max_tokens=500
)
print(f"Result2: {repr(result2)}")
print(f"Time: {time.time() - start:.2f}s")
