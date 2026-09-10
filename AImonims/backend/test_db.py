import sqlite3

# 测试数据库连接
conn = sqlite3.connect('interview.db')
cursor = conn.cursor()

# 测试创建表
cursor.execute('''
CREATE TABLE IF NOT EXISTS test_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
''')

# 测试插入数据
cursor.execute('INSERT INTO test_table (name) VALUES (?)', ('test',))
conn.commit()

# 测试查询数据
cursor.execute('SELECT * FROM test_table')
result = cursor.fetchall()
print('查询结果:', result)

# 测试用户表
cursor.execute('SELECT * FROM users LIMIT 1')
users = cursor.fetchall()
print('用户表数据:', users)

conn.close()
print('数据库测试成功！')