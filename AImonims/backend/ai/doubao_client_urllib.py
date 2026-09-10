import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()


class DoubaoClient:
    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY")
        self.model = os.getenv("DOUBAO_MODEL", "doubao-seed-2-0-pro-260215")
        self.base_url = os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")

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

        req = urllib.request.Request(
            url,
            headers=headers,
            data=json.dumps(data).encode('utf-8'),
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"HTTP Error {e.code}: {error_body}")
            raise

    def generate_response(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            content = self._make_request(messages, temperature, max_tokens)
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

    def generate_response_simple(self, prompt, max_tokens=200):
        messages = [{"role": "user", "content": prompt}]
        try:
            return self._make_request(messages, temperature=0.7, max_tokens=max_tokens, timeout=15)
        except Exception as e:
            print(f"API调用失败: {e}")
            return None
