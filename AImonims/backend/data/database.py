import sqlite3
import os
import json

class Database:
    def __init__(self, db_path="interview.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

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
            duration INTEGER DEFAULT 10,
            resume_text TEXT DEFAULT NULL,
            target_company TEXT DEFAULT NULL,
            status TEXT DEFAULT 'in_progress',
            phase TEXT DEFAULT 'introduction',
            candidate_question_count INTEGER DEFAULT 0,
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
            metadata TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews (id)
        )
        ''')

        try:
            cursor.execute('ALTER TABLE messages ADD COLUMN metadata TEXT DEFAULT NULL')
        except:
            pass

        try:
            cursor.execute("ALTER TABLE interviews ADD COLUMN phase TEXT DEFAULT 'introduction'")
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN candidate_question_count INTEGER DEFAULT 0')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN self_intro_question_count INTEGER DEFAULT 0')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN tech_question_count INTEGER DEFAULT 0')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN interview_config TEXT DEFAULT NULL')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN current_question_index INTEGER DEFAULT 0')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN current_followup_count INTEGER DEFAULT 0')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN max_followups_per_question INTEGER DEFAULT 2')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN resume_info TEXT DEFAULT NULL')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN resume_based_questions TEXT DEFAULT NULL')
        except:
            pass

        try:
            cursor.execute('ALTER TABLE interviews ADD COLUMN max_followups_per_question INTEGER DEFAULT 1')
        except:
            pass
        
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
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS selected_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_type TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            analysis TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            overall_score INTEGER DEFAULT 0,
            dimensions TEXT DEFAULT NULL,
            strengths TEXT DEFAULT NULL,
            improvements TEXT DEFAULT NULL,
            template_suggestion TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews (id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            emotion TEXT DEFAULT NULL,
            confidence REAL DEFAULT 0,
            focus TEXT DEFAULT NULL,
            suggestion TEXT DEFAULT NULL,
            raw_response TEXT DEFAULT NULL,
            timestamp DATETIME DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews (id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS speech_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            message_id INTEGER DEFAULT NULL,
            audio_data BLOB DEFAULT NULL,
            audio_format TEXT DEFAULT 'webm',
            duration REAL DEFAULT 0,
            speech_rate REAL DEFAULT 0,
            confidence_score REAL DEFAULT 0,
            tone_type TEXT DEFAULT NULL,
            overall_analysis TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews (id),
            FOREIGN KEY (message_id) REFERENCES messages (id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_interview_id ON messages (interview_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evaluation_reports_interview_id ON evaluation_reports (interview_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_improvement_plans_interview_id ON improvement_plans (interview_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_exam_questions_category ON exam_questions (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_selected_questions_category ON selected_questions (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_selected_questions_type ON selected_questions (question_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resume_evaluations_interview_id ON resume_evaluations (interview_id)')

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
    
    def start_interview(self, user_id, position, round_info, job_type=None, experience=None, interviewer_role=None, pressure_level=1, duration=10, resume_text=None, target_company=None):
        """开始面试"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO interviews (user_id, position, round, job_type, experience, interviewer_role, pressure_level, duration, resume_text, target_company, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_progress')
            ''', (user_id, position, round_info, job_type, experience, interviewer_role, pressure_level, duration, resume_text, target_company))
            
            interview_id = cursor.lastrowid
            conn.commit()
            return interview_id
        finally:
            conn.close()
    
    def add_message(self, interview_id, sender, content):
        """添加消息"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO messages (interview_id, sender, content) VALUES (?, ?, ?)', (interview_id, sender, content))
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
    
    def update_interview_phase(self, interview_id, phase):
        """更新面试阶段"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET phase = ? WHERE id = ?', (phase, interview_id))
        finally:
            conn.close()
    
    def update_candidate_question_count(self, interview_id, count):
        """更新候选人提问计数"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET candidate_question_count = ? WHERE id = ?', (count, interview_id))
        finally:
            conn.close()
    
    def update_interview_config(self, interview_id, config):
        """更新面试配置"""
        import json
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET interview_config = ? WHERE id = ?', (json.dumps(config), interview_id))
        finally:
            conn.close()
    
    def update_self_intro_question_count(self, interview_id, count):
        """更新自我介绍问题计数"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET self_intro_question_count = ? WHERE id = ?', (count, interview_id))
        finally:
            conn.close()
    
    def update_tech_question_count(self, interview_id, count):
        """更新技术问题计数"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET tech_question_count = ? WHERE id = ?', (count, interview_id))
        finally:
            conn.close()
    
    def update_current_question_index(self, interview_id, index):
        """更新当前问题索引"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET current_question_index = ? WHERE id = ?', (index, interview_id))
        finally:
            conn.close()
    
    def update_current_followup_count(self, interview_id, count):
        """更新当前追问计数"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET current_followup_count = ? WHERE id = ?', (count, interview_id))
        finally:
            conn.close()
    
    def update_max_followups_per_question(self, interview_id, max_count):
        """更新每个问题的最大追问次数"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE interviews SET max_followups_per_question = ? WHERE id = ?', (max_count, interview_id))
        finally:
            conn.close()
    
    def add_message_metadata(self, interview_id, metadata_key, metadata_value):
        """添加消息元数据"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO messages (interview_id, sender, content, metadata) VALUES (?, ?, ?, ?)',
                         (interview_id, 'system', f'{metadata_key}:{metadata_value}', f'{metadata_key}:{metadata_value}'))
        finally:
            conn.close()
    
    def get_user_interviews(self, user_id):
        """获取用户的所有面试记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT ir.*, er.overall_score, er.overall_level
            FROM interviews ir
            LEFT JOIN evaluation_reports er ON ir.id = er.interview_id
            WHERE ir.user_id = ?
            ORDER BY ir.created_at DESC
            ''', (user_id,))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def get_messages(self, interview_id):
        """获取面试消息"""
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT sender, content, created_at FROM messages WHERE interview_id = ? ORDER BY created_at', (interview_id,))
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
    
    def update_resume_info(self, interview_id, resume_info):
        """更新简历信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            UPDATE interviews SET resume_info = ? WHERE id = ?
            ''', (resume_info, interview_id))
            conn.commit()
        finally:
            conn.close()
    
    def update_resume_based_questions(self, interview_id, questions):
        """更新基于简历的问题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            UPDATE interviews SET resume_based_questions = ? WHERE id = ?
            ''', (questions, interview_id))
            conn.commit()
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

    def add_selected_question(self, question_type, question, options, correct_answer, analysis, category, difficulty='medium'):
        """添加精选题库题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO selected_questions (question_type, question, options, correct_answer, analysis, category, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (question_type, question, json.dumps(options), json.dumps(correct_answer) if isinstance(correct_answer, list) else correct_answer, analysis, category, difficulty))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_selected_questions(self, category=None, question_type=None, difficulty=None, limit=None):
        """获取精选题库列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            query = 'SELECT * FROM selected_questions WHERE 1=1'
            params = []

            if category:
                query += ' AND category = ?'
                params.append(category)

            if question_type:
                query += ' AND question_type = ?'
                params.append(question_type)

            if difficulty:
                query += ' AND difficulty = ?'
                params.append(difficulty)

            query += ' ORDER BY created_at DESC'

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()

    def get_selected_question_by_id(self, question_id):
        """根据ID获取精选题目"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM selected_questions WHERE id = ?', (question_id,))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
        finally:
            conn.close()

    def delete_selected_question(self, question_id):
        """删除精选题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM selected_questions WHERE id = ?', (question_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"删除精选题目失败: {e}")
            return False
        finally:
            conn.close()

    def get_selected_questions_count(self, category=None, question_type=None):
        """获取精选题目数量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            query = 'SELECT COUNT(*) FROM selected_questions WHERE 1=1'
            params = []

            if category:
                query += ' AND category = ?'
                params.append(category)

            if question_type:
                query += ' AND question_type = ?'
                params.append(question_type)

            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count
        finally:
            conn.close()

    def search_selected_questions(self, keyword, category=None, question_type=None):
        """搜索精选题目"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            query = 'SELECT * FROM selected_questions WHERE question LIKE ?'
            params = [f'%{keyword}%']

            if category:
                query += ' AND category = ?'
                params.append(category)

            if question_type:
                query += ' AND question_type = ?'
                params.append(question_type)

            query += ' ORDER BY created_at DESC'

            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()

    def save_resume_evaluation(self, interview_id, overall_score, dimensions, strengths, improvements, template_suggestion):
        """保存简历评价"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO resume_evaluations (interview_id, overall_score, dimensions, strengths, improvements, template_suggestion)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (interview_id, overall_score,
                  dimensions if isinstance(dimensions, str) else json.dumps(dimensions),
                  strengths if isinstance(strengths, str) else json.dumps(strengths),
                  improvements if isinstance(improvements, str) else json.dumps(improvements),
                  template_suggestion))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_resume_evaluation(self, interview_id):
        """获取简历评价"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT * FROM resume_evaluations WHERE interview_id = ?
            ''', (interview_id,))
            evaluation = cursor.fetchone()
            if evaluation:
                eval_dict = dict(evaluation)
                if eval_dict.get('dimensions'):
                    eval_dict['dimensions'] = json.loads(eval_dict['dimensions'])
                if eval_dict.get('strengths'):
                    eval_dict['strengths'] = json.loads(eval_dict['strengths'])
                if eval_dict.get('improvements'):
                    eval_dict['improvements'] = json.loads(eval_dict['improvements'])
                return eval_dict
            return None
        finally:
            conn.close()


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
    
    def save_speech_record(self, interview_id, message_id=None, audio_data=None, audio_format='webm', duration=0, 
                            speech_rate=0, confidence_score=0, tone_type=None, overall_analysis=None):
        """保存语音记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO speech_records (interview_id, message_id, audio_data, audio_format, duration, 
                                        speech_rate, confidence_score, tone_type, overall_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (interview_id, message_id, audio_data, audio_format, duration, 
                  speech_rate, confidence_score, tone_type, overall_analysis))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_speech_records(self, interview_id):
        """获取面试的语音记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM speech_records WHERE interview_id = ? ORDER BY created_at', (interview_id,))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def get_speech_record_by_id(self, record_id):
        """根据ID获取语音记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM speech_records WHERE id = ?', (record_id,))
            record = cursor.fetchone()
            if record:
                return dict(record)
            return None
        finally:
            conn.close()
    
    def get_speech_analysis_summary(self, interview_id):
        """获取语音分析汇总"""
        records = self.get_speech_records(interview_id)
        if not records:
            return None
        
        total = len(records)
        avg_speech_rate = sum(r.get('speech_rate', 0) for r in records) / total if total > 0 else 0
        avg_confidence = sum(r.get('confidence_score', 0) for r in records) / total if total > 0 else 0
        
        tone_types = [r.get('tone_type') for r in records if r.get('tone_type')]
        tone_count = {}
        for t in tone_types:
            tone_count[t] = tone_count.get(t, 0) + 1
        dominant_tone = max(tone_count, key=tone_count.get) if tone_count else None
        
        return {
            'total_records': total,
            'avg_speech_rate': round(avg_speech_rate, 1),
            'avg_confidence': round(avg_confidence, 1),
            'dominant_tone': dominant_tone,
            'tone_distribution': tone_count
        }
