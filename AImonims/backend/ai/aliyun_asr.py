import os
import base64
import time
import requests
import json
from typing import Optional

class AliyunASR:
    def __init__(self):
        self.access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        self.app_key = os.getenv("ALIYUN_ASR_APP_KEY")
        self.region_id = os.getenv("ALIYUN_REGION_ID", "cn-shanghai")

    def _generate_token(self) -> Optional[str]:
        """生成阿里云API Token"""
        try:
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.request import CommonRequest

            client = AcsClient(self.access_key_id, self.access_key_secret, self.region_id)

            request = CommonRequest()
            request.set_method('POST')
            request.set_domain('nls-gateway.cn-shanghai.aliyuncs.com')
            request.set_uri_pattern('/oauth/token')
            request.add_query_param('grant_type', 'client_credentials')
            request.add_query_param('client_id', self.access_key_id)
            request.add_query_param('client_secret', self.access_key_secret)

            response = client.do_action(request)
            result = json.loads(response.decode('utf-8'))

            if result.get('Token'):
                return result['Token']['Id']
        except Exception as e:
            print(f"获取Token失败: {e}")
        return None

    def recognize_speech(self, audio_data: bytes, duration: float = 0) -> Optional[dict]:
        """识别语音并返回文本和分析结果

        Returns:
            dict: {"text": "识别文本", "confidence": 0.8, ...}
        """
        if not self.access_key_id or not self.access_key_secret or not self.app_key:
            print("阿里云ASR配置不完整")
            return self._fallback_recognition(audio_data, duration)

        try:
            token = self._generate_token()
            if not token:
                return self._fallback_recognition(audio_data, duration)

            url = f"https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr"

            headers = {
                "Content-Type": "audio/pcm",
                "X-NLS-Token": token,
            }

            params = {
                "appkey": self.app_key,
                "format": "pcm",
                "sample_rate": 16000,
            }

            response = requests.post(
                url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    text = result.get("result", {}).get("text", "")
                    return {
                        "text": text,
                        "confidence": 0.85 if text else 0,
                        "duration": duration,
                    }
                else:
                    print(f"ASR识别失败: {result}")
            else:
                print(f"ASR请求失败: {response.status_code}")

        except Exception as e:
            print(f"ASR识别异常: {e}")

        return self._fallback_recognition(audio_data, duration)

    def _fallback_recognition(self, audio_data: bytes, duration: float) -> dict:
        """备用识别方案 - 基于音频特性分析"""
        audio_size = len(audio_data)
        estimated_text = f"语音回答（长度:{duration:.1f}秒, 大小:{audio_size}字节）"

        return {
            "text": estimated_text,
            "confidence": 0.5,
            "duration": duration,
            "note": "ASR服务不可用，使用默认识别"
        }

    def recognize_audio_base64(self, audio_base64: str, audio_format: str = "wav") -> Optional[dict]:
        """识别Base64编码的音频数据"""
        try:
            audio_data = base64.b64decode(audio_base64)
            return self.recognize_speech(audio_data)
        except Exception as e:
            print(f"Base64音频解码失败: {e}")
            return None

aliyun_asr = AliyunASR()
