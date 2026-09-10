#!/usr/bin/env python3
# -*- coding: utf-8 -*-

db_path = 'data/interview.db'

new_methods = """

    def save_face_analysis(self, interview_id, emotion, confidence, focus, suggestion, raw_response=None, timestamp=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO face_analyses (interview_id, emotion, confidence, focus, suggestion, raw_response, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (interview_id, emotion, confidence, focus, suggestion, raw_response, timestamp))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_face_analyses(self, interview_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM face_analyses WHERE interview_id = ? ORDER BY created_at
            ''', (interview_id,))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()

    def get_face_analysis_summary(self, interview_id):
        analyses = self.get_face_analyses(interview_id)
        if not analyses:
            return None

        total = len(analyses)
        avg_confidence = sum(a.get('confidence', 0) for a in analyses) / total if total > 0 else 0

        emotions = [a.get('emotion') for a in analyses if a.get('emotion')]
        focuses = [a.get('focus') for a in analyses if a.get('focus')]

        emotion_count = {}
        for e in emotions:
            emotion_count[e] = emotion_count.get(e, 0) + 1
        dominant_emotion = max(emotion_count, key=emotion_count.get) if emotion_count else None

        focus_count = {}
        for f in focuses:
            focus_count[f] = focus_count.get(f, 0) + 1
        dominant_focus = max(focus_count, key=focus_count.get) if focus_count else None

        suggestions = [a.get('suggestion') for a in analyses if a.get('suggestion')]

        return {
            'total_analyses': total,
            'avg_confidence': round(avg_confidence, 1),
            'dominant_emotion': dominant_emotion,
            'dominant_focus': dominant_focus,
            'emotion_distribution': emotion_count,
            'focus_distribution': focus_count,
            'all_suggestions': suggestions
        }
"""

with open('data/database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

content = ''.join(lines)
if 'save_face_analysis' in content:
    print('方法已存在')
else:
    with open('data/database.py', 'a', encoding='utf-8') as f:
        f.write(new_methods)
    print('方法添加成功')
