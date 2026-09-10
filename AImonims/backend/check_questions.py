import sqlite3
import json

conn = sqlite3.connect('interview.db')
cursor = conn.cursor()

cursor.execute('SELECT id, question_type, correct_answer FROM selected_questions WHERE question_type=?', ('multiple',))
rows = cursor.fetchall()

print(f"Found {len(rows)} multiple choice questions")
for r in rows[:3]:
    print(f"ID: {r[0]}, Type: {r[1]}, Answer: {r[2]}")

cursor.execute('SELECT id, question_type, correct_answer FROM selected_questions WHERE question_type=?', ('single',))
rows = cursor.fetchall()
print(f"\nFound {len(rows)} single choice questions")
for r in rows[:3]:
    print(f"ID: {r[0]}, Type: {r[1]}, Answer: {r[2]}")

conn.close()