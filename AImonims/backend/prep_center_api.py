import json
from datetime import datetime

def register_prep_center_routes(app, get_db):
    """注册面试准备中心相关路由"""

    # ========== 面试干货 API ==========

    @app.get("/api/tips")
    async def get_tips(
        page: int = 1,
        page_size: int = 10,
        category: str = "",
        keyword: str = "",
        difficulty: str = ""
    ):
        """获取面试干货列表"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM interview_tips WHERE status = 'published'"
            params = []
            count_query = "SELECT COUNT(*) FROM interview_tips WHERE status = 'published'"

            if category:
                query += " AND category = ?"
                count_query += " AND category = ?"
                params.append(category)

            if keyword:
                query += " AND (title LIKE ? OR summary LIKE ?)"
                count_query += " AND (title LIKE ? OR summary LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])

            if difficulty:
                query += " AND difficulty = ?"
                count_query += " AND difficulty = ?"
                params.append(difficulty)

            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            tips = []
            for row in cursor.fetchall():
                tip = dict(row)
                if tip.get('tags'):
                    tip['tags'] = json.loads(tip['tags'])
                if tip.get('related_skills'):
                    tip['related_skills'] = json.loads(tip['related_skills'])
                tips.append(tip)

            return {
                "success": True,
                "data": tips,
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/tips/categories")
    async def get_tip_categories():
        """获取干货分类列表"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT category, COUNT(*) as count FROM interview_tips WHERE status = 'published' GROUP BY category"
            )
            categories = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
            return {"success": True, "data": categories}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/tips/{tip_id}")
    async def get_tip_detail(tip_id: int):
        """获取干货详情"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE interview_tips SET view_count = view_count + 1 WHERE id = ?",
                (tip_id,)
            )
            conn.commit()

            cursor.execute(
                "SELECT * FROM interview_tips WHERE id = ?",
                (tip_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "干货不存在"}

            tip = dict(row)
            if tip.get('tags'):
                tip['tags'] = json.loads(tip['tags'])
            if tip.get('related_skills'):
                tip['related_skills'] = json.loads(tip['related_skills'])

            return {"success": True, "data": tip}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.post("/api/tips/{tip_id}/collect")
    async def collect_tip(tip_id: int, request: dict):
        """收藏/取消收藏干货"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            
            cursor.execute(
                "SELECT * FROM user_tip_interactions WHERE user_id = ? AND tip_id = ?",
                (user_id, tip_id)
            )
            interaction = cursor.fetchone()

            if interaction:
                is_collected = 1 - interaction['is_collected']
                cursor.execute(
                    "UPDATE user_tip_interactions SET is_collected = ? WHERE user_id = ? AND tip_id = ?",
                    (is_collected, user_id, tip_id)
                )
            else:
                is_collected = 1
                cursor.execute(
                    "INSERT INTO user_tip_interactions (user_id, tip_id, is_collected) VALUES (?, ?, 1)",
                    (user_id, tip_id)
                )

            if is_collected:
                cursor.execute(
                    "UPDATE interview_tips SET collect_count = collect_count + 1 WHERE id = ?",
                    (tip_id,)
                )
            else:
                cursor.execute(
                    "UPDATE interview_tips SET collect_count = collect_count - 1 WHERE id = ?",
                    (tip_id,)
                )

            conn.commit()
            return {"success": True, "is_collected": bool(is_collected)}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # ========== 用户简历 API ==========

    @app.post("/api/resumes")
    async def upload_resume(request: dict):
        """上传简历"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            file_name = request.get('file_name', '')
            target_position = request.get('target_position', '')

            cursor.execute('''
                INSERT INTO user_resumes (user_id, file_name, target_position, status)
                VALUES (?, ?, ?, 'uploaded')
            ''', (user_id, file_name, target_position))

            resume_id = cursor.lastrowid
            conn.commit()

            return {"success": True, "resume_id": resume_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/resumes")
    async def get_resumes(user_id: int):
        """获取用户简历列表"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM user_resumes WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            resumes = [dict(row) for row in cursor.fetchall()]
            return {"success": True, "data": resumes}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/resumes/{resume_id}")
    async def get_resume_detail(resume_id: int):
        """获取简历详情"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM user_resumes WHERE id = ?",
                (resume_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "简历不存在"}

            resume = dict(row)
            if resume.get('parsed_data'):
                resume['parsed_data'] = json.loads(resume['parsed_data'])
            if resume.get('analysis_result'):
                resume['analysis_result'] = json.loads(resume['analysis_result'])

            cursor.execute(
                "SELECT * FROM resume_suggestions WHERE resume_id = ? ORDER BY priority DESC",
                (resume_id,)
            )
            resume['suggestions'] = [dict(row) for row in cursor.fetchall()]

            return {"success": True, "data": resume}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.post("/api/resumes/{resume_id}/analyze")
    async def analyze_resume(resume_id: int):
        """分析简历"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM user_resumes WHERE id = ?",
                (resume_id,)
            )
            resume = cursor.fetchone()
            if not resume:
                return {"success": False, "error": "简历不存在"}

            analysis_result = {
                "completeness_score": 75,
                "match_score": 60,
                "keyword_score": 55,
                "quantification_score": 50,
                "expression_score": 70,
                "overall_score": 62,
                "summary": "简历基本完整，但需要加强关键词和量化描述"
            }

            cursor.execute(
                "UPDATE user_resumes SET analysis_result = ?, status = 'analyzed' WHERE id = ?",
                (json.dumps(analysis_result), resume_id)
            )

            suggestions = [
                {
                    "resume_id": resume_id,
                    "dimension": "quantification",
                    "issue": "工作经历缺乏量化数据",
                    "suggestion": "建议为每项工作经历添加具体的数字成果",
                    "priority": "high"
                },
                {
                    "resume_id": resume_id,
                    "dimension": "keyword",
                    "issue": "缺少目标岗位关键词",
                    "suggestion": "根据目标岗位要求，添加相关技能关键词",
                    "priority": "medium"
                }
            ]

            for suggestion in suggestions:
                cursor.execute('''
                    INSERT INTO resume_suggestions (resume_id, dimension, issue, suggestion, priority)
                    VALUES (?, ?, ?, ?, ?)
                ''', (resume_id, suggestion['dimension'], suggestion['issue'],
                      suggestion['suggestion'], suggestion['priority']))

            conn.commit()

            return {"success": True, "data": analysis_result}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.delete("/api/resumes/{resume_id}")
    async def delete_resume(resume_id: int):
        """删除简历"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM resume_suggestions WHERE resume_id = ?", (resume_id,))
            cursor.execute("DELETE FROM user_resumes WHERE id = ?", (resume_id,))
            conn.commit()
            return {"success": True, "message": "删除成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # ========== 投递追踪 API ==========

    @app.post("/api/applications")
    async def create_application(request: dict):
        """创建投递记录"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            company = request.get('company')
            position = request.get('position')
            job_type = request.get('job_type', 'fulltime')
            salary_range = request.get('salary_range', '')
            source = request.get('source', '')

            cursor.execute('''
                INSERT INTO job_applications (user_id, company, position, job_type, salary_range, source, stage)
                VALUES (?, ?, ?, ?, ?, ?, 'applied')
            ''', (user_id, company, position, job_type, salary_range, source))

            application_id = cursor.lastrowid
            conn.commit()

            return {"success": True, "application_id": application_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/applications")
    async def get_applications(
        user_id: int,
        stage: str = "",
        page: int = 1,
        page_size: int = 20
    ):
        """获取投递记录列表"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM job_applications WHERE user_id = ?"
            count_query = "SELECT COUNT(*) FROM job_applications WHERE user_id = ?"
            params = [user_id]

            if stage:
                query += " AND stage = ?"
                count_query += " AND stage = ?"
                params.append(stage)

            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            applications = [dict(row) for row in cursor.fetchall()]

            return {
                "success": True,
                "data": applications,
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.put("/api/applications/{application_id}")
    async def update_application(
        application_id: int,
        stage: str = "",
        interview_date: str = "",
        notes: str = ""
    ):
        """更新投递记录"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            updates = []
            params = []

            if stage:
                updates.append("stage = ?")
                params.append(stage)
            if interview_date:
                updates.append("interview_date = ?")
                params.append(interview_date)
            if notes:
                updates.append("notes = ?")
                params.append(notes)

            updates.append("updated_at = ?")
            params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            params.append(application_id)
            cursor.execute(
                f"UPDATE job_applications SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()

            return {"success": True, "message": "更新成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.delete("/api/applications/{application_id}")
    async def delete_application(application_id: int):
        """删除投递记录"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM job_applications WHERE id = ?", (application_id,))
            conn.commit()
            return {"success": True, "message": "删除成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/applications/stats")
    async def get_application_stats(user_id: int):
        """获取投递统计"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT stage, COUNT(*) as count FROM job_applications WHERE user_id = ? GROUP BY stage",
                (user_id,)
            )
            stage_stats = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute(
                "SELECT COUNT(*) FROM job_applications WHERE user_id = ?",
                (user_id,)
            )
            total = cursor.fetchone()[0]

            return {
                "success": True,
                "data": {
                    "total": total,
                    "stages": stage_stats
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # ========== 社区帖子 API ==========

    @app.get("/api/posts")
    async def get_posts(
        page: int = 1,
        page_size: int = 10,
        type: str = "",
        category: str = "",
        keyword: str = ""
    ):
        """获取社区帖子列表"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM community_posts WHERE status = 'published'"
            count_query = "SELECT COUNT(*) FROM community_posts WHERE status = 'published'"
            params = []
            params_count = []

            if type:
                query += " AND type = ?"
                count_query += " AND type = ?"
                params.append(type)
                params_count.append(type)

            if category:
                query += " AND category = ?"
                count_query += " AND category = ?"
                params.append(category)
                params_count.append(category)

            if keyword:
                query += " AND (title LIKE ? OR content LIKE ?)"
                count_query += " AND (title LIKE ? OR content LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
                params_count.extend([f"%{keyword}%", f"%{keyword}%"])

            cursor.execute(count_query, params_count)
            total = cursor.fetchone()[0]

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            posts = []
            for row in cursor.fetchall():
                post = dict(row)
                if post.get('tags'):
                    post['tags'] = json.loads(post['tags'])
                posts.append(post)

            return {
                "success": True,
                "data": posts,
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/posts/{post_id}")
    async def get_post_detail(post_id: int):
        """获取帖子详情"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE community_posts SET view_count = view_count + 1 WHERE id = ?",
                (post_id,)
            )
            conn.commit()

            cursor.execute(
                "SELECT * FROM community_posts WHERE id = ?",
                (post_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "帖子不存在"}

            post = dict(row)
            if post.get('tags'):
                post['tags'] = json.loads(post['tags'])

            cursor.execute(
                "SELECT * FROM post_comments WHERE post_id = ? ORDER BY created_at ASC",
                (post_id,)
            )
            post['comments'] = [dict(row) for row in cursor.fetchall()]

            return {"success": True, "data": post}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.post("/api/posts")
    async def create_post(request: dict):
        """创建帖子"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            username = request.get('username')
            title = request.get('title')
            content = request.get('content')
            type = request.get('type', 'experience')
            category = request.get('category', '')
            tags = request.get('tags', '')

            cursor.execute('''
                INSERT INTO community_posts (user_id, username, title, content, type, category, tags, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'published')
            ''', (user_id, username, title, content, type, category, tags))

            post_id = cursor.lastrowid
            conn.commit()

            return {"success": True, "post_id": post_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.post("/api/posts/{post_id}/like")
    async def like_post(post_id: int):
        """点赞帖子"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE community_posts SET like_count = like_count + 1 WHERE id = ?",
                (post_id,)
            )
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.post("/api/posts/{post_id}/comments")
    async def create_comment(post_id: int, request: dict):
        """创建评论"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            username = request.get('username')
            content = request.get('content')
            parent_id = request.get('parent_id', 0)

            cursor.execute('''
                INSERT INTO post_comments (post_id, user_id, username, content, parent_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (post_id, user_id, username, content, parent_id))

            cursor.execute(
                "UPDATE community_posts SET comment_count = comment_count + 1 WHERE id = ?",
                (post_id,)
            )
            conn.commit()

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # ========== 优秀简历参考 API ==========

    @app.get("/api/reference-resumes")
    async def get_reference_resumes(
        industry: str = "",
        position: str = ""
    ):
        """获取优秀简历参考"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM reference_resumes WHERE 1=1"
            params = []

            if industry:
                query += " AND industry = ?"
                params.append(industry)

            if position:
                query += " AND position LIKE ?"
                params.append(f"%{position}%")

            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            resumes = []
            for row in cursor.fetchall():
                resume = dict(row)
                if resume.get('resume_data'):
                    resume['resume_data'] = json.loads(resume['resume_data'])
                if resume.get('highlights'):
                    resume['highlights'] = json.loads(resume['highlights'])
                resumes.append(resume)

            return {"success": True, "data": resumes}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # ========== AI智能推荐 API ==========

    @app.get("/api/recommendations")
    async def get_recommendations(
        user_id: int,
        limit: int = 5
    ):
        """获取个性化推荐"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM evaluation_reports er WHERE er.interview_id IN (SELECT id FROM interviews WHERE user_id = ?) ORDER BY er.created_at DESC LIMIT 1",
                (user_id,)
            )
            report = cursor.fetchone()

            recommendations = {
                "tips": [],
                "questions": [],
                "reference_resumes": []
            }

            if report:
                report_dict = dict(report)
                if report_dict.get('suggestions'):
                    suggestions = json.loads(report_dict['suggestions'])
                    for suggestion in suggestions[:3]:
                        cursor.execute(
                            "SELECT * FROM interview_tips WHERE status = 'published' AND (title LIKE ? OR tags LIKE ?) LIMIT 2",
                            (f"%{suggestion}%", f"%{suggestion}%")
                        )
                        tips = [dict(row) for row in cursor.fetchall()]
                        recommendations["tips"].extend(tips)
            else:
                cursor.execute(
                    "SELECT * FROM interview_tips WHERE status = 'published' ORDER BY view_count DESC LIMIT ?",
                    (limit,)
                )
                recommendations["tips"] = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                "SELECT * FROM selected_questions ORDER BY RANDOM() LIMIT ?",
                (limit,)
            )
            recommendations["questions"] = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                "SELECT * FROM reference_resumes ORDER BY RANDOM() LIMIT ?",
                (2,)
            )
            recommendations["reference_resumes"] = [dict(row) for row in cursor.fetchall()]

            return {"success": True, "data": recommendations}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    print("面试准备中心路由注册完成！")
