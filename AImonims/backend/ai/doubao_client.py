import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


class DoubaoClient:
    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY")
        self.model = os.getenv("DOUBAO_MODEL", "doubao-seed-2-0-pro-260215")
        self.base_url = os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")

        self.cache = {}
        self.cache_max_size = 100
        self.cache_timeout = 3600

    def _get_cache_key(self, system_prompt, user_prompt, temperature, max_tokens):
        import hashlib
        key = f"{system_prompt}|{user_prompt}|{temperature}|{max_tokens}"
        return hashlib.md5(key.encode()).hexdigest()

    def _check_cache(self, key):
        import time
        if key in self.cache:
            cached_data = self.cache[key]
            if time.time() - cached_data['timestamp'] < self.cache_timeout:
                return cached_data['content']
            else:
                del self.cache[key]
        return None

    def _update_cache(self, key, content):
        import time
        current_time = time.time()
        expired_keys = [k for k, v in self.cache.items() if current_time - v['timestamp'] >= self.cache_timeout]
        for k in expired_keys:
            del self.cache[k]

        if len(self.cache) >= self.cache_max_size:
            oldest_key = min(self.cache, key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

        self.cache[key] = {
            'content': content,
            'timestamp': time.time()
        }

    def _make_request(self, messages, temperature=0.7, max_tokens=2000, timeout=60):
        url = f"{self.base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']

    def generate_response(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        cache_key = self._get_cache_key(system_prompt, user_prompt, temperature, max_tokens)

        cached_content = self._check_cache(cache_key)
        if cached_content:
            print("✅ 使用缓存结果")
            return cached_content

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            content = self._make_request(messages, temperature, max_tokens)
            self._update_cache(cache_key, content)
            return content
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return None

    def generate_followup_question_with_context(self, system_prompt, conversation_history):
        history_messages = []
        history_messages.append({"role": "system", "content": system_prompt})

        for msg in conversation_history:
            role = "assistant" if msg.get('role') == 'ai' else "user"
            history_messages.append({"role": role, "content": msg.get('content', '')})

        history_messages.append({"role": "user", "content": "请根据对话历史，生成下一个递进的面试问题。要求：每次只输出一个问题，不要额外解释，不要重复已问过的问题。"})

        try:
            return self._make_request(history_messages, temperature=0.7, max_tokens=500, timeout=60)
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return None

    def analyze_answer_quality(self, job_type, question, answer):
        system_prompt = """你是一位专业的面试评估专家，需要快速分析候选人回答的质量。
        请从以下维度评估：
        - 技术正确性：回答是否正确
        - 完整性：回答是否全面
        - 深度：回答是否有深度
        - 逻辑性：回答是否逻辑清晰

        请返回JSON格式，包含：
        {
            "quality": "excellent|good|average|poor",
            "confidence": 0-1,
            "reason": "简短原因"
        }"""

        user_prompt = f"""岗位类型：{job_type}
        面试问题：{question}
        候选人回答：{answer}

        请评估回答质量。"""

        response = self.generate_response(system_prompt, user_prompt, temperature=0.3, max_tokens=500)
        if response:
            try:
                return json.loads(response)
            except:
                return {"quality": "average", "confidence": 0.5, "reason": "无法评估"}
        return {"quality": "average", "confidence": 0.5, "reason": "无法评估"}

    def generate_answer_comment(self, job_type, question, answer, quality):
        system_prompt = """你是一位专业的面试官，需要对候选人的回答进行专业、具体、有针对性的点评。"""

        user_prompt = f"""岗位类型：{job_type}
        面试问题：{question}
        候选人回答：{answer}
        回答质量：{quality}

        请生成一段专业、具体、有针对性的面试官点评。"""

        return self.generate_response(system_prompt, user_prompt, temperature=0.6, max_tokens=300)

    def generate_followup_question_with_comment(self, system_prompt, conversation_history, comment):
        history_messages = []
        history_messages.append({"role": "system", "content": system_prompt})

        for msg in conversation_history:
            role = "assistant" if msg.get('role') == 'ai' else "user"
            history_messages.append({"role": role, "content": msg.get('content', '')})

        if comment:
            history_messages.append({"role": "assistant", "content": comment})

        history_messages.append({"role": "user", "content": "请根据对话历史，生成一个针对性的、深度的后续问题。"})

        try:
            return self._make_request(history_messages, temperature=0.7, max_tokens=500, timeout=60)
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return None

    def generate_response_simple(self, prompt, max_tokens=200):
        messages = [{"role": "user", "content": prompt}]
        try:
            return self._make_request(messages, temperature=0.7, max_tokens=max_tokens, timeout=60)
        except Exception as e:
            print(f"API调用失败: {e}")
            return None

    def analyze_speech(self, text):
        """分析语音的语速、语气、自信度"""
        system_prompt = """你是一位专业的语音分析专家。请分析用户语音转文字后的表达特征。

请从以下维度分析：
1. 语速（speech_rate）：评估说话速度是否适中、流畅
2. 语气（tone）：评估语气特点（如：紧张、自信、沉稳、焦虑、平和等）
3. 自信度（confidence）：评估表达的自信息（如：高、中、低）

请返回JSON格式：
{
    "speech_rate": "适中|偏快|偏慢|很慢|很快",
    "speech_rate_score": 0-100,
    "tone": "描述语气特点",
    "tone_type": "confident|calm|nervous|anxious|excited|neutral",
    "confidence": "高|中|低",
    "confidence_score": 0-100,
    "overall_analysis": "简短的整体分析"
}"""

        user_prompt = f"用户语音内容：{text}\n\n请分析这段话的表达特征。"

        response = self.generate_response(system_prompt, user_prompt, temperature=0.3, max_tokens=500)
        if response:
            try:
                import json as json_lib
                result = json_lib.loads(response)
                return result
            except:
                return {
                    "speech_rate": "适中",
                    "speech_rate_score": 70,
                    "tone": "平和",
                    "tone_type": "neutral",
                    "confidence": "中",
                    "confidence_score": 60,
                    "overall_analysis": "表达较为平稳"
                }
        return None

    def generate_digital_human_response(self, user_text, interview_context=None):
        """生成数字人面试官的拟人化回答"""
        context_prompt = ""
        if interview_context:
            context_prompt = f"""
面试背景：
- 岗位：{interview_context.get('position', '未知')}
- 面试时长：{interview_context.get('duration', '未知')}
- 当前阶段：{interview_context.get('phase', '自我介绍')}

对话历史：
{interview_context.get('conversation_history', '')}
"""

        system_prompt = f"""你是一位专业、温和、真实的AI面试官。

要求：
1. 回答要像真人面试官一样自然，不要太长
2. 每次只问一个问题或做一个点评
3. 可以适当追问深入
4. 语气要专业但不失亲和力
5. 根据面试阶段调整提问方式

回答格式：
- 如果是提问：直接输出问题
- 如果是点评：1-2句话简短点评 + 追问或过渡{context_prompt}"""

        user_prompt = f"候选人回答/说：{user_text}\n\n请以面试官的身份回应。"

        return self.generate_response(system_prompt, user_prompt, temperature=0.7, max_tokens=300)

    def analyze_face_expression(self, image_path):
        """分析面部表情（OpenCV 简单规则版 - 无需下载模型）"""
        try:
            import cv2
            import numpy as np
            import os

            if not os.path.exists(image_path):
                return None

            img = cv2.imread(image_path)
            if img is None:
                return None

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(faces) == 0:
                return None

            face_x, face_y, face_w, face_h = faces[0]
            face_roi = gray[face_y:face_y + face_h, face_x:face_x + face_w]

            mean_brightness = np.mean(face_roi)
            std_brightness = np.std(face_roi)
            max_brightness = np.max(face_roi)
            min_brightness = np.min(face_roi)
            brightness_range = max_brightness - min_brightness

            if mean_brightness > 130 and brightness_range > 60:
                emotion = "开心"
                confidence = 75
                focus = "专注"
                suggestion = "表情生动自然，继续保持良好状态"
            elif mean_brightness > 120 and std_brightness > 40:
                emotion = "平静"
                confidence = 80
                focus = "专注"
                suggestion = "表情自然，继续保持"
            elif mean_brightness > 100:
                emotion = "平静"
                confidence = 70
                focus = "专注"
                suggestion = "表情自然，继续保持当前状态"
            elif std_brightness > 45 and brightness_range > 40:
                emotion = "紧张"
                confidence = 60
                focus = "紧张"
                suggestion = "表情略显紧绷，请放松心情"
            elif brightness_range < 30:
                emotion = "平静"
                confidence = 65
                focus = "专注"
                suggestion = "表情较为单一，尝试更丰富一些"
            else:
                emotion = "平静"
                confidence = 70
                focus = "专注"
                suggestion = "保持当前状态，自然表达"

            return {
                "emotion": emotion,
                "confidence": confidence,
                "focus": focus,
                "suggestion": suggestion
            }
        except Exception as e:
            print(f"面部分析失败: {e}")
            import traceback
            traceback.print_exc()
            return None
