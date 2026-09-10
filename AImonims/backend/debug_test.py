import sqlite3
from data.database import Database

db = Database()
messages = db.get_messages(18)

print('=== 从db.get_messages获取的消息 ===')
for i, msg in enumerate(messages):
    content_preview = msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content']
    print(f'{i}: sender={msg["sender"]}, content_len={len(msg["content"])}, content={content_preview}')

print('\n=== 模拟遍历逻辑 ===')
conversation_history = []
last_question = ""
ai_questions_count = 0
user_answers_count = 0

for idx, msg in enumerate(messages):
    role = msg['sender']
    content = msg['content']
    print(f'\n处理消息 {idx}: role={role}, content_len={len(content)}')

    conversation_history.append({
        'role': role,
        'content': content
    })

    if role == 'ai':
        ai_questions_count += 1
        if len(conversation_history) >= 2:
            print(f'  -> 更新 last_question (当前: len={len(last_question)})')
            last_question = content
            print(f'  -> last_question 变成: {repr(content[:30])}... (len={len(content)})')
    elif role == 'user':
        user_answers_count += 1
        print(f'  -> 用户回答，记录完毕')

print(f'\n=== 最终结果 ===')
print(f'ai_questions_count: {ai_questions_count}')
print(f'user_answers_count: {user_answers_count}')
print(f'last_question: {repr(last_question)}')
print(f'last_question is empty: {not last_question}')
