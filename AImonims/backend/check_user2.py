import sqlite3
import json

conn = sqlite3.connect('interview.db')
cursor = conn.cursor()

user_id = 1

cursor.execute("""
    SELECT ir.id, ir.position, ir.round, ir.created_at,
           er.overall_score, er.overall_level
    FROM interviews ir
    LEFT JOIN evaluation_reports er ON ir.id = er.interview_id
    WHERE ir.user_id = ?
    ORDER BY ir.created_at DESC
""", (user_id,))

records = cursor.fetchall()

total_scores = []
level_counts = {'初级': 0, '中级': 0, '高级': 0}
positions = {}

for record in records:
    interview_id = record[0]
    position = record[1]
    created_at = record[3]
    overall_score = record[4]
    overall_level = record[5]

    if position not in positions:
        positions[position] = 0
    positions[position] += 1

    if overall_score:
        total_scores.append(overall_score)
        if overall_level:
            if '初级' in overall_level:
                level_counts['初级'] += 1
            elif '中级' in overall_level:
                level_counts['中级'] += 1
            elif '高级' in overall_level or '优秀' in overall_level:
                level_counts['高级'] += 1

print(f"Total interviews: {len(records)}")
print(f"Interviews with scores: {len(total_scores)}")
print(f"Total scores: {total_scores}")
print(f"Average score: {sum(total_scores) / len(total_scores) if total_scores else 0}")
print(f"Level counts: {level_counts}")
print(f"Positions: {positions}")

conn.close()
