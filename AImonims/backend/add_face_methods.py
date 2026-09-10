# -*- coding: utf-8 -*-

# 读取database.py文件
with open('data/database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 检查是否已经添加过face_analysis相关方法
content = ''.join(lines)
if 'save_face_analysis' in content:
    print("面部分析方法已存在，无需添加")
else:
    # 找到update_resume_based_questions方法后的位置
    insert_after = "def update_resume_based_questions"
    new_methods = '''

    def save_face_analysis(self, interview_id, emotion, confidence, focus, suggestion, raw_response=None, timestamp=None):
        """保存面部分析结果"""
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
        """获取面试的所有面部分析结果"""
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
        """获取面部分析汇总"""
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

'''

    # 找到插入位置
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if insert_after in line:
            # 在这个方法后添加新方法
            new_lines.append(new_methods)

    # 写回文件
    with open('data/database.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("面部分析方法添加成功！")
