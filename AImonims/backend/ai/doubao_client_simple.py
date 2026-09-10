import os
import httpx
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

    def _make_request(self, messages, temperature=0.7, max_tokens=2000, timeout=10):
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

        response = httpx.post(url, headers=headers, json=data, timeout=timeout)
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
            return self._make_request(history_messages, temperature=0.7, max_tokens=1000, timeout=15)
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
            return self._make_request(history_messages, temperature=0.7, max_tokens=1000, timeout=15)
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return None

    def generate_response_simple(self, prompt, max_tokens=200):
        messages = [{"role": "user", "content": prompt}]
        try:
            return self._make_request(messages, temperature=0.7, max_tokens=max_tokens, timeout=15)
        except Exception as e:
            print(f"API调用失败: {e}")
            return None
