import sqlite3

conn = sqlite3.connect('interview.db')
cursor = conn.cursor()

cursor.execute('SELECT id, username FROM users WHERE username = ?', ('lxd',))
user = cursor.fetchone()
print('User:', user)

if user:
    user_id = user[0]
    cursor.execute('SELECT id, user_id, position, status, created_at FROM interviews WHERE user_id = ?', (user_id,))
    interviews = cursor.fetchall()
    print('Interviews count:', len(interviews))
    print('Interviews:', interviews[:5] if len(interviews) > 5 else interviews)

    cursor.execute('SELECT er.interview_id, er.overall_score, er.overall_level FROM evaluation_reports er WHERE er.interview_id IN (SELECT id FROM interviews WHERE user_id = ?)', (user_id,))
    reports = cursor.fetchall()
    print('Reports count:', len(reports))
    print('Reports:', reports)

conn.close()
