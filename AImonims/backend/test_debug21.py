import sys
sys.path.insert(0, '.')

from data.database import Database
from main import process_interview

db = Database()
interview_id = 21  # Latest interview

messages = db.get_messages(interview_id)
print(f'=== Messages for interview {interview_id} ===')
for i, msg in enumerate(messages):
    print(f'{i}: sender={msg["sender"]}, content={msg["content"][:50]}...')

print('\n=== Building conversation_history and last_question ===')
conversation_history = []
last_question = ""

for msg in messages:
    role = msg['sender']
    content = msg['content']
    if role == 'ai':
        role = 'assistant'
    conversation_history.append({
        "role": role,
        "content": content
    })
    if msg['sender'] == 'ai' and content.strip():
        print(f'Setting last_question to: {content[:50]}...')
        last_question = content

print(f'\nlast_question: {last_question[:50]}...' if len(last_question) > 50 else f'last_question: {last_question}')
print(f'conversation_history length: {len(conversation_history)}')

if last_question:
    print('\n=== Calling process_interview ===')
    user_answer = '我是一名Java后端开发者，熟练使用Spring Boot。'
    result = process_interview(last_question, user_answer, conversation_history)
    print(f'followup: {result.get("followup")}')
else:
    print('\nlast_question is empty!')
