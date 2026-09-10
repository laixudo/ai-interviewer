import sqlite3

conn = sqlite3.connect('interview.db')
cursor = conn.cursor()

page_size = 20
offset = 0

cursor.execute("""
    SELECT id, question, answer, analysis, category, created_at
    FROM exam_questions
    ORDER BY created_at DESC
    LIMIT ? OFFSET ?
""", (page_size, offset))

questions = cursor.fetchall()
print(f"Fetched {len(questions)} questions")
for q in questions[:2]:
    print(f"  ID: {q[0]}, Q: {q[1][:30]}...")

cursor.execute("SELECT COUNT(*) FROM exam_questions")
total = cursor.fetchone()[0]
print(f"Total count: {total}")

conn.close()
