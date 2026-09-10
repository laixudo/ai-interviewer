import sqlite3

db_path = r"D:\AImonims\AImonims\backend\interview.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表:")
for t in tables:
    print(f"  {t[0]}")

# 查看所有用户
cursor.execute("SELECT id, username FROM users")
users = cursor.fetchall()
print(f"\n所有用户 ({len(users)} 条):")
for u in users:
    print(f"  ID: {u[0]}, Username: {u[1]}")

# 查看每个用户的面试记录数
print("\n每个用户的面试记录数:")
cursor.execute("""
    SELECT u.username, COUNT(i.id) as interview_count
    FROM users u
    LEFT JOIN interviews i ON u.id = i.user_id
    GROUP BY u.id
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} 条")

conn.close()
