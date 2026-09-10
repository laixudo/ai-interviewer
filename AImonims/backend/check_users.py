import sqlite3

conn = sqlite3.connect('interview.db')
cursor = conn.cursor()

cursor.execute('SELECT id, username, email, created_at FROM users LIMIT 10')
users = cursor.fetchall()
print("用户列表:")
for u in users:
    print(f"  ID: {u[0]}, Username: {u[1]}, Email: {u[2]}")

conn.close()
