"""
管理员端 API 扩展
这些 API 需要管理员权限才能访问
"""

def register_admin_routes(app):
    """注册管理员端 API 路由"""

    @app.get("/api/admin/stats")
    async def get_admin_stats():
        """获取管理后台统计数据"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            total_users = 0
            total_interviews = 0
            total_questions = 0

            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
            except:
                pass

            try:
                cursor.execute("SELECT COUNT(*) FROM interviews")
                total_interviews = cursor.fetchone()[0]
            except:
                pass

            try:
                cursor.execute("SELECT COUNT(*) FROM exam_questions")
                total_questions = cursor.fetchone()[0]
            except:
                pass

            try:
                cursor.execute("SELECT COUNT(*) FROM selected_questions")
                total_selected = cursor.fetchone()[0]
            except:
                total_selected = 0

            avg_score = 0
            try:
                cursor.execute("""
                    SELECT AVG(er.overall_score) FROM evaluation_reports er
                    WHERE er.overall_score IS NOT NULL
                """)
                result = cursor.fetchone()[0]
                if result:
                    avg_score = round(result, 1)
            except:
                pass

            conn.close()

            return {
                "success": True,
                "totalUsers": total_users,
                "totalInterviews": total_interviews,
                "totalQuestions": total_questions,
                "avgScore": avg_score,
                "totalSelected": total_selected
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.get("/api/admin/users")
    async def get_admin_users(page: int = 1, page_size: int = 20, keyword: str = ""):
        """获取用户列表（管理后台）"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            offset = (page - 1) * page_size

            if keyword:
                cursor.execute("""
                    SELECT id, username, email, created_at,
                           (SELECT COUNT(*) FROM interviews WHERE user_id = users.id) as interview_count
                    FROM users
                    WHERE username LIKE ? OR email LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (f"%{keyword}%", f"%{keyword}%", page_size, offset))
            else:
                cursor.execute("""
                    SELECT id, username, email, created_at,
                           (SELECT COUNT(*) FROM interviews WHERE user_id = users.id) as interview_count
                    FROM users
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (page_size, offset))

            users = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM users" + (" WHERE username LIKE ? OR email LIKE ?" if keyword else ""))
            total = cursor.fetchone()[0]

            conn.close()

            return {
                "success": True,
                "users": [
                    {
                        "id": u[0],
                        "username": u[1],
                        "email": u[2],
                        "created_at": u[3],
                        "interview_count": u[4]
                    } for u in users
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.get("/api/admin/interviews")
    async def get_admin_interviews(page: int = 1, page_size: int = 20, user_id: int = None):
        """获取面试记录列表（管理后台）"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            offset = (page - 1) * page_size

            if user_id:
                cursor.execute("""
                    SELECT ir.id, ir.user_id, u.username, ir.position, ir.round,
                           ir.job_type, ir.experience, ir.duration, ir.status, ir.created_at
                    FROM interviews ir
                    JOIN users u ON ir.user_id = u.id
                    WHERE ir.user_id = ?
                    ORDER BY ir.created_at DESC
                    LIMIT ? OFFSET ?
                """, (user_id, page_size, offset))
            else:
                cursor.execute("""
                    SELECT ir.id, ir.user_id, u.username, ir.position, ir.round,
                           ir.job_type, ir.experience, ir.duration, ir.status, ir.created_at
                    FROM interviews ir
                    JOIN users u ON ir.user_id = u.id
                    ORDER BY ir.created_at DESC
                    LIMIT ? OFFSET ?
                """, (page_size, offset))

            interviews = cursor.fetchall()

            if user_id:
                cursor.execute("SELECT COUNT(*) FROM interviews WHERE user_id = ?", (user_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM interviews")
            total = cursor.fetchone()[0]

            conn.close()

            return {
                "success": True,
                "interviews": [
                    {
                        "id": i[0],
                        "user_id": i[1],
                        "username": i[2],
                        "position": i[3],
                        "round": i[4],
                        "job_type": i[5],
                        "experience": i[6],
                        "duration": i[7],
                        "status": i[8],
                        "created_at": i[9]
                    } for i in interviews
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.delete("/api/admin/interviews/{interview_id}")
    async def delete_interview(interview_id: int):
        """删除面试记录"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("DELETE FROM interviews WHERE id = ?", (interview_id,))
            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                return {"success": True, "message": "删除成功"}
            else:
                return {"success": False, "error": "记录不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.get("/api/admin/interview-detail")
    async def get_admin_interview_detail(interview_id: int):
        """获取面试详情（管理后台）"""
        try:
            import sqlite3
            import json
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ir.id, ir.user_id, u.username, ir.position, ir.round,
                       ir.job_type, ir.experience, ir.duration, ir.status, ir.created_at,
                       ir.interviewer_role, ir.target_company, ir.resume_text
                FROM interviews ir
                JOIN users u ON ir.user_id = u.id
                WHERE ir.id = ?
            """, (interview_id,))

            interview_row = cursor.fetchone()

            if not interview_row:
                conn.close()
                return {"success": False, "error": "面试记录不存在"}

            cursor.execute("""
                SELECT sender, content, created_at FROM messages
                WHERE interview_id = ?
                ORDER BY created_at ASC
            """, (interview_id,))
            messages = cursor.fetchall()

            cursor.execute("""
                SELECT overall_score, overall_level, content_evaluation,
                       expression_evaluation, highlights, suggestions, created_at
                FROM evaluation_reports
                WHERE interview_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (interview_id,))
            report_row = cursor.fetchone()

            cursor.execute("""
                SELECT weaknesses, suggestions, resources, learning_plan, created_at
                FROM improvement_plans
                WHERE interview_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (interview_id,))
            plan_row = cursor.fetchone()

            conn.close()

            interview = {
                "id": interview_row[0],
                "user_id": interview_row[1],
                "username": interview_row[2],
                "position": interview_row[3],
                "round": interview_row[4],
                "job_type": interview_row[5] or "未设置",
                "experience": interview_row[6] or "未设置",
                "duration": interview_row[7],
                "status": interview_row[8],
                "created_at": interview_row[9],
                "interviewer_role": interview_row[10] or "面试官",
                "target_company": interview_row[11] or "",
                "resume_text": interview_row[12] or ""
            }

            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "sender": msg[0],
                    "content": msg[1],
                    "created_at": msg[2]
                })

            report = None
            if report_row:
                report = {
                    "overall_score": report_row[0],
                    "overall_level": report_row[1],
                    "content_evaluation": report_row[2] or "",
                    "expression_evaluation": report_row[3] or "",
                    "highlights": report_row[4] or "",
                    "suggestions": report_row[5] or "",
                    "created_at": report_row[6]
                }

            plan = None
            if plan_row:
                plan = {
                    "weaknesses": plan_row[0] or "",
                    "suggestions": plan_row[1] or "",
                    "resources": plan_row[2] or "",
                    "learning_plan": plan_row[3] or "",
                    "created_at": plan_row[4]
                }

            return {
                "success": True,
                "interview": interview,
                "messages": formatted_messages,
                "report": report,
                "plan": plan
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.get("/api/admin/exam-questions")
    async def get_admin_exam_questions(page: int = 1, page_size: int = 20, category: str = ""):
        """获取真题列表（管理后台）"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            offset = (page - 1) * page_size

            if category:
                cursor.execute("""
                    SELECT id, question, answer, analysis, category, created_at
                    FROM exam_questions
                    WHERE category = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (category, page_size, offset))
            else:
                cursor.execute("""
                    SELECT id, question, answer, analysis, category, created_at
                    FROM exam_questions
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (page_size, offset))

            questions = cursor.fetchall()

            if category:
                cursor.execute("SELECT COUNT(*) FROM exam_questions WHERE category = ?", (category,))
            else:
                cursor.execute("SELECT COUNT(*) FROM exam_questions")
            total = cursor.fetchone()[0]

            conn.close()

            return {
                "success": True,
                "questions": [
                    {
                        "id": q[0],
                        "question": q[1],
                        "answer": q[2],
                        "analysis": q[3],
                        "category": q[4],
                        "created_at": q[5]
                    } for q in questions
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.post("/api/admin/exam-questions")
    async def create_exam_question(question: str, answer: str, analysis: str, category: str):
        """创建真题"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO exam_questions (question, answer, analysis, category)
                VALUES (?, ?, ?, ?)
            """, (question, answer, analysis, category))

            conn.commit()
            question_id = cursor.lastrowid
            conn.close()

            return {"success": True, "question_id": question_id, "message": "创建成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.put("/api/admin/exam-questions/{question_id}")
    async def update_exam_question(question_id: int, question: str, answer: str, analysis: str, category: str):
        """更新真题"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE exam_questions
                SET question = ?, answer = ?, analysis = ?, category = ?
                WHERE id = ?
            """, (question, answer, analysis, category, question_id))

            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                return {"success": True, "message": "更新成功"}
            else:
                return {"success": False, "error": "记录不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.delete("/api/admin/exam-questions/{question_id}")
    async def delete_exam_question(question_id: int):
        """删除真题"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("DELETE FROM exam_questions WHERE id = ?", (question_id,))
            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                return {"success": True, "message": "删除成功"}
            else:
                return {"success": False, "error": "记录不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.get("/api/admin/selected-questions")
    async def get_admin_selected_questions(page: int = 1, page_size: int = 20, category: str = ""):
        """获取精选题库列表（管理后台）"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            offset = (page - 1) * page_size

            if category:
                cursor.execute("""
                    SELECT id, question_type, question, options, correct_answer, analysis, category, difficulty
                    FROM selected_questions
                    WHERE category = ?
                    ORDER BY id DESC
                    LIMIT ? OFFSET ?
                """, (category, page_size, offset))
            else:
                cursor.execute("""
                    SELECT id, question_type, question, options, correct_answer, analysis, category, difficulty
                    FROM selected_questions
                    ORDER BY id DESC
                    LIMIT ? OFFSET ?
                """, (page_size, offset))

            questions = cursor.fetchall()

            if category:
                cursor.execute("SELECT COUNT(*) FROM selected_questions WHERE category = ?", (category,))
            else:
                cursor.execute("SELECT COUNT(*) FROM selected_questions")
            total = cursor.fetchone()[0]

            conn.close()

            return {
                "success": True,
                "questions": [
                    {
                        "id": q[0],
                        "type": q[1],
                        "question": q[2],
                        "options": q[3],
                        "correct_answer": q[4],
                        "analysis": q[5],
                        "category": q[6],
                        "difficulty": q[7]
                    } for q in questions
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.post("/api/admin/selected-questions")
    async def create_selected_question(type: str, question: str, options: str, correct_answer: str, analysis: str, category: str, difficulty: str = "medium"):
        """创建精选题目"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO selected_questions (question_type, question, options, correct_answer, analysis, category, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (type, question, options, correct_answer, analysis, category, difficulty))

            conn.commit()
            question_id = cursor.lastrowid
            conn.close()

            return {"success": True, "question_id": question_id, "message": "创建成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.put("/api/admin/selected-questions/{question_id}")
    async def update_selected_question(question_id: int, type: str, question: str, options: str, correct_answer: str, analysis: str, category: str, difficulty: str = "medium"):
        """更新精选题目"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE selected_questions
                SET question_type = ?, question = ?, options = ?, correct_answer = ?, analysis = ?, category = ?, difficulty = ?
                WHERE id = ?
            """, (type, question, options, correct_answer, analysis, category, difficulty, question_id))

            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                return {"success": True, "message": "更新成功"}
            else:
                return {"success": False, "error": "记录不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.delete("/api/admin/selected-questions/{question_id}")
    async def delete_selected_question(question_id: int):
        """删除精选题目"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("DELETE FROM selected_questions WHERE id = ?", (question_id,))
            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                return {"success": True, "message": "删除成功"}
            else:
                return {"success": False, "error": "记录不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.delete("/api/admin/users/{user_id}")
    async def delete_user(user_id: int):
        """删除用户"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                conn.close()
                return {"success": False, "error": "用户不存在"}

            username = user[0]
            if username.lower() in {"admin", "administrator", "管理员"}:
                conn.close()
                return {"success": False, "error": "不能删除管理员账号"}

            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                return {"success": True, "message": "删除成功"}
            else:
                return {"success": False, "error": "用户不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.get("/api/admin/categories")
    async def get_admin_categories():
        """获取分类列表"""
        try:
            import sqlite3
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("SELECT DISTINCT category FROM exam_questions ORDER BY category")
            exam_categories = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT category FROM selected_questions ORDER BY category")
            selected_categories = [row[0] for row in cursor.fetchall()]

            conn.close()

            return {
                "success": True,
                "exam_categories": exam_categories,
                "selected_categories": selected_categories
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    @app.get("/api/admin/user/{user_id}/ability-profile")
    async def get_user_ability_profile(user_id: int):
        """获取用户能力档案"""
        try:
            import sqlite3
            import json
            conn = sqlite3.connect('interview.db')
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                conn.close()
                return {"success": False, "error": "用户不存在"}

            username = user_row[0]

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

            if not records:
                conn.close()
                return {
                    "success": True,
                    "username": username,
                    "has_data": False,
                    "interviewCount": 0,
                    "avgScore": 0,
                    "level": "暂无数据",
                    "positions": []
                }

            avg_score = sum(total_scores) / len(total_scores) if total_scores else 0

            max_level = '初级'
            if level_counts['中级'] > level_counts['初级']:
                max_level = '中级'
            if level_counts['高级'] > level_counts['中级']:
                max_level = '高级'

            avg_score_rounded = round(avg_score, 1) if avg_score else 0

            conn.close()

            return {
                "success": True,
                "username": username,
                "has_data": True,
                "interviewCount": len(records),
                "avgScore": avg_score_rounded,
                "level": max_level,
                "positions": [{"name": k, "count": v} for k, v in positions.items()],
                "recent_records": [
                    {
                        "id": r[0],
                        "position": r[1],
                        "overall_score": r[4],
                        "overall_level": r[5],
                        "created_at": r[3]
                    } for r in records[:10]
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
