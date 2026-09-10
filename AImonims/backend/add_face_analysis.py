# -*- coding: utf-8 -*-
import sqlite3
import json

def add_face_analysis_table():
    db_path = 'data/interview.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建面部分析表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        emotion TEXT DEFAULT NULL,
        confidence INTEGER DEFAULT 0,
        focus TEXT DEFAULT NULL,
        suggestion TEXT DEFAULT NULL,
        raw_response TEXT DEFAULT NULL,
        timestamp TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (interview_id) REFERENCES interviews (id)
    )
    ''')

    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_face_analyses_interview_id ON face_analyses (interview_id)')

    conn.commit()
    conn.close()
    print("面部分析表创建成功！")

if __name__ == '__main__':
    add_face_analysis_table()
