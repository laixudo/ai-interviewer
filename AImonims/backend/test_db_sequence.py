import sys
sys.path.insert(0, '.')

from main import db

# 清空面试30的消息重新测试
import sqlite3
conn = sqlite3.connect('interview.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM messages WHERE interview_id = 30')
conn.commit()
conn.close()

print('Cleared messages for interview 30')

# 模拟 send_message 的逻辑
print('\n=== Simulating send_message ===')

# Step 1: Save user message
db.add_message(30, "user", "我是一名Java后端开发者")
print('Saved user message')

# Step 2: Read messages
messages = db.get_messages(30)
print(f'Read {len(messages)} messages')
for m in messages:
    print(f'  {m["sender"]}: {m["content"][:30]}...')

# Step 3: Count
user_answers_count = sum(1 for msg in messages if msg['sender'] == 'user')
print(f'user_answers_count: {user_answers_count}')

# Step 4: Save AI response
db.add_message(30, "ai", "这是一个AI回复")
print('Saved AI message')

# Step 5: Read again
messages = db.get_messages(30)
print(f'\nRead {len(messages)} messages after AI save')
user_answers_count = sum(1 for msg in messages if msg['sender'] == 'user')
print(f'user_answers_count: {user_answers_count}')
