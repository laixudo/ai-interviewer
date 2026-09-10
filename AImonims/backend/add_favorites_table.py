import sqlite3
import json
import os

def add_favorites_table():
    db_path = os.path.join(os.path.dirname(__file__), 'interview.db')

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("开始创建收藏相关表...")

    # 用户收藏表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        favorite_type TEXT NOT NULL,
        item_id INTEGER NOT NULL,
        title TEXT,
        content TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, favorite_type, item_id)
    )
    ''')
    print("✓ user_favorites 表创建成功")

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_favorites_user ON user_favorites (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_favorites_type ON user_favorites (favorite_type)')
    print("✓ 索引创建成功")

    conn.commit()
    conn.close()

    print("\n收藏表创建完成！")

if __name__ == '__main__':
    add_favorites_table()