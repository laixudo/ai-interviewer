import sqlite3
import os
import json

class Database:
    def __init__(self, db_path="interview.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            avatar TEXT DEFAULT NULL,
            phone TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            position TEXT NOT NULL,
            round TEXT NOT NULL,
            job_type TEXT DEFAULT NULL,
            experience TEXT DEFAULT NULL,
            interviewer_role TEXT DEFAULT NULL,
            pressure_level INTEGER DEFAULT 1,
            resume_text TEXT DEFAULT NULL,
            target_company TEXT DEFAULT NULL,
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluation_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            overall_score INTEGER NOT NULL,
            overall_level TEXT NOT NULL,
            content_evaluation TEXT DEFAULT NULL,
            expression_evaluation TEXT DEFAULT NULL,
            highlights TEXT DEFAULT NULL,
            suggestions TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS improvement_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            weaknesses TEXT DEFAULT NULL,
            suggestions TEXT DEFAULT NULL,
            resources TEXT DEFAULT NULL,
            learning_plan TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            analysis TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, username, password, email, phone=None, avatar=None):
        """添加用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO users (username, password, email, phone, avatar) VALUES (?, ?, ?, ?, ?)
            ''', (username, password, email, phone, avatar))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def login_user(self, username, password):
        """用户登录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
            ''', (username, password))
            user = cursor.fetchone()
            if user:
                return dict(user)
            return None
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            if user:
                return dict(user)
            return None
        finally:
            conn.close()
    
    def update_user(self, user_id, username=None, email=None, phone=None, avatar=None):
        """更新用户信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            updates = []
            values = []
            
            if username:
                updates.append("username = ?")
                values.append(username)
            if email:
                updates.append("email = ?")
                values.append(email)
            if phone:
                updates.append("phone = ?")
                values.append(phone)
            if avatar:
                updates.append("avatar = ?")
                values.append(avatar)
            
            if updates:
                values.append(user_id)
                cursor.execute(f'''
                UPDATE users SET {', '.join(updates)} WHERE id = ?
                ''', values)
                conn.commit()
                return True
            return False
        finally:
            conn.close()
    
    def start_interview(self, user_id, position, round_info, job_type=None, experience=None, interviewer_role=None, pressure_level=1, resume_text=None, target_company=None):
        """开始面试"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO interviews (user_id, position, round, job_type, experience, interviewer_role, pressure_level, resume_text, target_company, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_progress')
            ''', (user_id, position, round_info, job_type, experience, interviewer_role, pressure_level, resume_text, target_company))
            
            interview_id = cursor.lastrowid
            conn.commit()
            return interview_id
        finally:
            conn.close()
    
    def add_message(self, interview_id, sender, content):
        """添加消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO messages (interview_id, sender, content) VALUES (?, ?, ?)
            ''', (interview_id, sender, content))
            conn.commit()
        finally:
            conn.close()
    
    def get_interview(self, interview_id):
        """获取面试信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM interviews WHERE id = ?
            ''', (interview_id,))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
        finally:
            conn.close()
    
    def get_user_interviews(self, user_id):
        """获取用户的所有面试记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM interviews WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def get_messages(self, interview_id):
        """获取面试消息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT sender, content, created_at FROM messages WHERE interview_id = ? ORDER BY created_at
            ''', (interview_id,))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def save_evaluation_report(self, interview_id, overall_score, overall_level, content_evaluation, expression_evaluation, highlights, suggestions):
        """保存评估报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO evaluation_reports (interview_id, overall_score, overall_level, content_evaluation, expression_evaluation, highlights, suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (interview_id, overall_score, overall_level, 
                  content_evaluation if isinstance(content_evaluation, str) else json.dumps(content_evaluation),
                  expression_evaluation if isinstance(expression_evaluation, str) else json.dumps(expression_evaluation),
                  highlights if isinstance(highlights, str) else json.dumps(highlights),
                  suggestions if isinstance(suggestions, str) else json.dumps(suggestions)))
            
            conn.commit()
            cursor.execute('''
            UPDATE interviews SET status = 'completed' WHERE id = ?
            ''', (interview_id,))
            conn.commit()
        finally:
            conn.close()
    
    def save_improvement_plan(self, interview_id, weaknesses, suggestions, resources, learning_plan):
        """保存提升计划"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO improvement_plans (interview_id, weaknesses, suggestions, resources, learning_plan)
            VALUES (?, ?, ?, ?, ?)
            ''', (interview_id, 
                  weaknesses if isinstance(weaknesses, str) else json.dumps(weaknesses),
                  suggestions if isinstance(suggestions, str) else json.dumps(suggestions),
                  resources if isinstance(resources, str) else json.dumps(resources),
                  learning_plan if isinstance(learning_plan, str) else json.dumps(learning_plan)))
            conn.commit()
        finally:
            conn.close()
    
    def get_evaluation_report(self, interview_id):
        """获取评估报告"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM evaluation_reports WHERE interview_id = ?
            ''', (interview_id,))
            report = cursor.fetchone()
            if report:
                report_dict = dict(report)
                if report_dict.get('content_evaluation'):
                    report_dict['content_evaluation'] = json.loads(report_dict['content_evaluation'])
                if report_dict.get('expression_evaluation'):
                    report_dict['expression_evaluation'] = json.loads(report_dict['expression_evaluation'])
                if report_dict.get('highlights'):
                    report_dict['highlights'] = json.loads(report_dict['highlights'])
                if report_dict.get('suggestions'):
                    report_dict['suggestions'] = json.loads(report_dict['suggestions'])
                return report_dict
            return None
        finally:
            conn.close()
    
    def get_improvement_plan(self, interview_id):
        """获取提升计划"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM improvement_plans WHERE interview_id = ?
            ''', (interview_id,))
            plan = cursor.fetchone()
            if plan:
                plan_dict = dict(plan)
                if plan_dict.get('weaknesses'):
                    plan_dict['weaknesses'] = json.loads(plan_dict['weaknesses'])
                if plan_dict.get('suggestions'):
                    plan_dict['suggestions'] = json.loads(plan_dict['suggestions'])
                if plan_dict.get('resources'):
                    plan_dict['resources'] = json.loads(plan_dict['resources'])
                if plan_dict.get('learning_plan'):
                    plan_dict['learning_plan'] = json.loads(plan_dict['learning_plan'])
                return plan_dict
            return None
        finally:
            conn.close()
    
    def delete_interview(self, interview_id):
        """删除面试记录及其相关数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM improvement_plans WHERE interview_id = ?', (interview_id,))
            cursor.execute('DELETE FROM evaluation_reports WHERE interview_id = ?', (interview_id,))
            cursor.execute('DELETE FROM messages WHERE interview_id = ?', (interview_id,))
            cursor.execute('DELETE FROM interviews WHERE id = ?', (interview_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"删除面试记录失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def add_exam_question(self, question, answer, analysis, category):
        """添加事业单位真题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO exam_questions (question, answer, analysis, category) VALUES (?, ?, ?, ?)
            ''', (question, answer, analysis, category))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_exam_questions(self, category=None, limit=None):
        """获取事业单位真题列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            query = 'SELECT * FROM exam_questions'
            params = []
            
            if category:
                query += ' WHERE category = ?'
                params.append(category)
            
            query += ' ORDER BY created_at DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def search_exam_questions(self, keyword, category=None):
        """搜索事业单位真题"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            query = 'SELECT * FROM exam_questions WHERE question LIKE ?'
            params = [f'%{keyword}%']
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
