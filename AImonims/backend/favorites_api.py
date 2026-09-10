import json
from datetime import datetime

def register_favorites_routes(app, get_db):
    """注册收藏相关路由"""

    @app.post("/api/favorites")
    async def add_favorite(request: dict):
        """添加收藏"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            favorite_type = request.get('favorite_type')
            item_id = request.get('item_id')
            title = request.get('title', '')
            content = request.get('content', '')
            metadata = request.get('metadata', {})

            cursor.execute(
                "SELECT * FROM user_favorites WHERE user_id = ? AND favorite_type = ? AND item_id = ?",
                (user_id, favorite_type, item_id)
            )
            existing = cursor.fetchone()

            if existing:
                return {"success": True, "message": "已收藏", "is_favorited": True}

            cursor.execute('''
                INSERT INTO user_favorites (user_id, favorite_type, item_id, title, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, favorite_type, item_id, title, content, json.dumps(metadata)))

            conn.commit()
            return {"success": True, "message": "收藏成功", "is_favorited": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.delete("/api/favorites")
    async def remove_favorite(request: dict):
        """移除收藏"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            favorite_type = request.get('favorite_type')
            item_id = request.get('item_id')

            cursor.execute(
                "DELETE FROM user_favorites WHERE user_id = ? AND favorite_type = ? AND item_id = ?",
                (user_id, favorite_type, item_id)
            )

            conn.commit()
            return {"success": True, "message": "已取消收藏", "is_favorited": False}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/favorites")
    async def get_favorites(user_id: int, favorite_type: str = ""):
        """获取收藏列表"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            if favorite_type:
                cursor.execute(
                    "SELECT * FROM user_favorites WHERE user_id = ? AND favorite_type = ? ORDER BY created_at DESC",
                    (user_id, favorite_type)
                )
            else:
                cursor.execute(
                    "SELECT * FROM user_favorites WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,)
                )

            favorites = []
            for row in cursor.fetchall():
                fav = dict(row)
                fav['id'] = fav.get('item_id')
                if fav.get('metadata'):
                    try:
                        fav['metadata'] = json.loads(fav['metadata'])
                    except:
                        pass
                favorites.append(fav)

            return {"success": True, "data": favorites}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.get("/api/favorites/check")
    async def check_favorite(user_id: int, favorite_type: str, item_id: int):
        """检查是否已收藏"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM user_favorites WHERE user_id = ? AND favorite_type = ? AND item_id = ?",
                (user_id, favorite_type, item_id)
            )
            existing = cursor.fetchone()

            return {"success": True, "is_favorited": existing is not None}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @app.post("/api/favorites/toggle")
    async def toggle_favorite(request: dict):
        """切换收藏状态"""
        conn = get_db()
        cursor = conn.cursor()

        try:
            user_id = request.get('user_id')
            favorite_type = request.get('favorite_type')
            item_id = request.get('item_id')
            title = request.get('title', '')
            content = request.get('content', '')
            metadata = request.get('metadata', {})

            cursor.execute(
                "SELECT * FROM user_favorites WHERE user_id = ? AND favorite_type = ? AND item_id = ?",
                (user_id, favorite_type, item_id)
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "DELETE FROM user_favorites WHERE user_id = ? AND favorite_type = ? AND item_id = ?",
                    (user_id, favorite_type, item_id)
                )
                conn.commit()
                return {"success": True, "is_favorited": False, "message": "已取消收藏"}
            else:
                cursor.execute('''
                    INSERT INTO user_favorites (user_id, favorite_type, item_id, title, content, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, favorite_type, item_id, title, content, json.dumps(metadata)))
                conn.commit()
                return {"success": True, "is_favorited": True, "message": "收藏成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    print("收藏路由注册完成！")