import sqlite3

conn = sqlite3.connect('interview.db')
cursor = conn.cursor()

print("面试记录用户分布:")
cursor.execute('SELECT user_id, COUNT(*) as count FROM interviews GROUP BY user_id ORDER BY count DESC')
for row in cursor.fetchall():
    print(f"  user_id={row[0]}: {row[1]} 条记录")

print("\n最近10条面试记录:")
cursor.execute('SELECT id, user_id, position, status, created_at FROM interviews ORDER BY id DESC LIMIT 10')
for row in cursor.fetchall():
    print(f"  {row}")

print("\n管理员 API 返回的数据统计:")
cursor.execute('SELECT COUNT(*) FROM interviews')
print(f"  总记录数: {cursor.fetchone()[0]}")

conn.close()
