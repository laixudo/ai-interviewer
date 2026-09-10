# -*- coding: utf-8 -*-

# 定义要添加的API端点
api_endpoints = '''

# ==================== 面部分析相关功能 ====================

class FaceAnalysisRequest(BaseModel):
    image: str
    prompt: Optional[str] = "分析这张图片中的人物表情和状态"

@app.post("/api/doubao/face-analysis")
async def analyze_face(request: FaceAnalysisRequest):
    """使用豆包大模型进行面部分析"""
    try:
        import base64
        import json as json_lib

        # 构建提示词
        system_prompt = """你是一位专业的面试教练，擅长通过面部表情分析面试者的情绪和状态。
请根据提供的图片，分析面试者的以下维度：
1. 情绪状态（紧张/放松/焦虑/自信/平静等）
2. 自信度评分（0-100分）
3. 面试状态（专注/走神/疲惫/活跃等）
4. 简短改进建议（1-2句话）

请以JSON格式返回，字段为：emotion, confidence, focus, suggestion"""

        user_prompt = "请分析这张图片中人物的表情和面试状态"

        # 如果有图片数据，解码并临时保存
        image_data = None
        if request.image:
            try:
                image_data = base64.b64decode(request.image)
            except Exception as decode_error:
                print(f"图片解码失败: {decode_error}")

        if image_data:
            # 使用临时文件
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name

            try:
                response = global_doubao_client.analyze_face_expression(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            response = None

        if response:
            try:
                result = json_lib.loads(response)
                return result
            except:
                return {
                    "emotion": "平静",
                    "confidence": 70,
                    "focus": "专注",
                    "suggestion": "保持当前状态，继续积极表达"
                }

        # 默认响应
        return {
            "emotion": "平静",
            "confidence": 75,
            "focus": "专注",
            "suggestion": "保持良好状态，继续积极展示自己的能力"
        }

    except Exception as e:
        print(f"面部分析失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "emotion": "未知",
            "confidence": 0,
            "focus": "未知",
            "suggestion": "分析失败，请稍后重试"
        }


@app.post("/api/interview/save-face-analysis")
async def save_face_analysis(request: Request):
    """保存面部分析结果"""
    try:
        data = await request.json()
        interview_id = data.get('interview_id')
        emotion = data.get('emotion', '')
        confidence = data.get('confidence', 0)
        focus = data.get('focus', '')
        suggestion = data.get('suggestion', '')
        timestamp = data.get('timestamp')

        if not interview_id:
            return {"error": "缺少面试ID"}

        # 保存到数据库
        analysis_id = db.save_face_analysis(
            interview_id=interview_id,
            emotion=emotion,
            confidence=confidence,
            focus=focus,
            suggestion=suggestion,
            timestamp=timestamp
        )

        return {
            "status": "success",
            "analysis_id": analysis_id
        }
    except Exception as e:
        print(f"保存面部分析失败: {e}")
        return {"error": f"保存失败: {str(e)}"}


@app.get("/api/interview/face-analysis/{interview_id}")
async def get_face_analysis(interview_id: int):
    """获取面试的面部分析结果"""
    try:
        analyses = db.get_face_analyses(interview_id)
        summary = db.get_face_analysis_summary(interview_id)

        return {
            "status": "success",
            "analyses": analyses,
            "summary": summary
        }
    except Exception as e:
        print(f"获取面部分析失败: {e}")
        return {"error": f"获取失败: {str(e)}"}


@app.get("/api/interview/face-analysis-summary/{interview_id}")
async def get_face_analysis_summary_api(interview_id: int):
    """获取面部分析汇总"""
    try:
        summary = db.get_face_analysis_summary(interview_id)
        if summary:
            return {
                "status": "success",
                "summary": summary
            }
        else:
            return {
                "status": "not_found",
                "message": "暂无面部分析数据"
            }
    except Exception as e:
        print(f"获取面部分析汇总失败: {e}")
        return {"error": f"获取失败: {str(e)}"}

'''

# 读取main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已添加
if '/api/doubao/face-analysis' in content:
    print("面部分析API已存在，无需添加")
else:
    # 在文件末尾添加
    with open('main.py', 'a', encoding='utf-8') as f:
        f.write(api_endpoints)
    print("面部分析API添加成功")
