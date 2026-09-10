import sqlite3
conn = sqlite3.connect('interview.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(interviews)')
print('interviews 表结构:')
for row in cursor.fetchall():
    print(' ', row)

cursor.execute('SELECT * FROM interviews LIMIT 1')
print('\ninterviews 示例数据:')
for row in cursor.fetchall():
    print(' ', row)
conn.close()
