import io
import os
import numpy as np
import imageio_ffmpeg
from pydub import AudioSegment

AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

VOSK_MODEL_PATH = "D:\\\\AImonims\\\\models\\\\vosk-model-small-cn-0.3"


def convert_audio_to_whisper_format(audio_bytes):
    """把任意浏览器录音格式转成 16k 单声道 numpy 数组"""
    audio_io = io.BytesIO(audio_bytes)
    audio_io.seek(0)

    try:
        audio = AudioSegment.from_file(audio_io, format="webm")
        audio = audio.set_frame_rate(16000).set_channels(1)

        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

        if audio.sample_width == 2:
            samples = samples / 32768.0
        elif audio.sample_width == 4:
            pass
        elif audio.sample_width == 1:
            samples = samples / 128.0

        if samples.max() > 1.0 or samples.min() < -1.0:
            max_val = max(abs(samples.max()), abs(samples.min()))
            if max_val > 0:
                samples = samples / max_val

        return samples, 16000
    except Exception as e:
        print(f"pydub转换失败: {e}")
        return None, 0


class VoskRecognizer:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.recognizer = None

    def load_model(self):
        if not self.model_loaded:
            print("加载 Vosk 中文模型...")
            try:
                from vosk import Model, KaldiRecognizer
                if not os.path.exists(VOSK_MODEL_PATH):
                    print(f"Vosk 模型未找到: {VOSK_MODEL_PATH}")
                    return False

                self.model = Model(VOSK_MODEL_PATH)
                self.recognizer = KaldiRecognizer(self.model, 16000)
                self.model_loaded = True
                print("Vosk 模型加载完成")
                return True
            except Exception as e:
                print(f"Vosk 模型加载失败: {e}")
                return False

    def recognize(self, audio_bytes):
        """识别语音并返回结果"""
        if not self.model_loaded:
            self.load_model()

        if not self.model_loaded:
            return {"text": "", "error": "Vosk 模型未加载"}

        try:
            audio_io = io.BytesIO(audio_bytes)
            audio = AudioSegment.from_file(audio_io, format="webm")
            audio = audio.set_frame_rate(16000).set_channels(1)

            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

            if audio.sample_width == 2:
                samples = samples / 32768.0
            elif audio.sample_width == 4:
                pass
            elif audio.sample_width == 1:
                samples = samples / 128.0

            if samples.max() > 1.0 or samples.min() < -1.0:
                max_val = max(abs(samples.max()), abs(samples.min()))
                if max_val > 0:
                    samples = samples / max_val

            samples_int16 = (samples * 32767).astype(np.int16).tobytes()

            self.recognizer.Reset()

            chunk_size = 4000
            for i in range(0, len(samples_int16), chunk_size):
                chunk = samples_int16[i:i + chunk_size]
                self.recognizer.AcceptWaveform(chunk)

            final_result = self.recognizer.FinalResult()
            import json
            result_dict = json.loads(final_result)
            text = result_dict.get("text", "").replace(" ", "")

            if text:
                return {
                    "text": text,
                    "success": True,
                    "language": "zh"
                }
            else:
                partial_result = self.recognizer.PartialResult()
                partial_dict = json.loads(partial_result)
                partial_text = partial_dict.get("partial", "").replace(" ", "")
                if partial_text:
                    return {
                        "text": partial_text,
                        "success": True,
                        "language": "zh"
                    }
                return {
                    "text": "",
                    "success": False,
                    "error": "未识别到语音"
                }

        except Exception as e:
            print(f"Vosk 识别失败: {e}")
            import traceback
            traceback.print_exc()
            return {"text": "", "error": str(e)}


class WhisperRecognizer:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.model_name = "base"

    def load_model(self):
        if not self.model_loaded:
            print("加载 Whisper 中文模型...")
            try:
                import whisper
                self.model = whisper.load_model(self.model_name, device='cpu')
                self.model_loaded = True
                print("Whisper 模型加载完成")
                return True
            except Exception as e:
                print(f"Whisper 模型加载失败: {e}")
                return False

    def recognize(self, audio_bytes):
        """使用 Whisper 识别语音"""
        if not self.model_loaded:
            self.load_model()

        if not self.model_loaded:
            return {"text": "", "error": "Whisper 模型未加载"}

        try:
            samples, sample_rate = convert_audio_to_whisper_format(audio_bytes)
            
            if samples is None:
                return {"text": "", "error": "音频转换失败"}

            print("开始 Whisper 识别...")
            
            # 添加 initial_prompt 提示面试场景，提高识别准确率
            result = self.model.transcribe(
                samples,
                language='zh',
                fp16=False,
                task="transcribe",
                initial_prompt="这是一个IT技术面试的录音，可能包含Java、Python、JavaScript、C++、算法、数据结构等技术词汇。",
                temperature=0.0,
                best_of=5,
                beam_size=5
            )
            
            text = result.get('text', '').strip()
            
            print(f"Whisper 识别结果: '{text}'")

            if text:
                return {
                    "text": text,
                    "success": True,
                    "language": "zh"
                }
            else:
                return {
                    "text": "",
                    "success": False,
                    "error": "未识别到语音"
                }

        except Exception as e:
            print(f"Whisper 识别失败: {e}")
            import traceback
            traceback.print_exc()
            return {"text": "", "error": str(e)}


# 优先使用 Whisper，如果失败再用 Vosk
try:
    whisper_recognizer = WhisperRecognizer()
    speech_recognizer = whisper_recognizer
    print("已选择 Whisper 作为语音识别引擎")
except Exception as e:
    print(f"Whisper 初始化失败，使用 Vosk: {e}")
    vosk_recognizer = VoskRecognizer()
    speech_recognizer = vosk_recognizer