import io
import os
import numpy as np
import librosa
import imageio_ffmpeg
from pydub import AudioSegment

AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()


class LightSpeechAnalyzer:
    def __init__(self):
        pass

    def get_volume(self, audio: np.ndarray) -> tuple:
        """计算音量大小（分贝）"""
        try:
            audio = audio.flatten()
            rms = np.sqrt(np.mean(audio**2) + 1e-10)
            db = 20 * np.log10(rms)

            if np.isnan(db) or np.isinf(db):
                return -50.0, "正常"

            if db > -20:
                level = "大声"
            elif db < -40:
                level = "小声"
            else:
                level = "正常"

            return round(float(db), 2), level
        except:
            return -50.0, "正常"

    def get_speed(self, duration: float, estimated_words: int = None) -> tuple:
        """计算语速（字/分钟）"""
        if duration <= 0:
            duration = 1

        if estimated_words is not None:
            count = estimated_words
        else:
            count = int(duration * 3)

        wpm = int(count / duration * 60)

        if wpm > 180:
            level = "偏快"
        elif wpm < 100:
            level = "偏慢"
        else:
            level = "正常"

        return wpm, level, count

    def get_confidence(self, db: float, wpm: int) -> int:
        """计算自信度评分（0-100）"""
        try:
            if np.isnan(db) or np.isinf(db):
                db = -50.0
            if np.isnan(wpm) or np.isinf(wpm):
                wpm = 150

            score = 0

            if -35 < db < -20:
                score += 40
            elif db > -20:
                score += 30
            elif db < -40:
                score += 15
            else:
                score += 25

            if 120 < wpm < 180:
                score += 40
            elif 100 < wpm < 200:
                score += 25
            elif wpm >= 200:
                score += 10
            elif wpm < 100:
                score += 15
            else:
                score += 20

            score += 20

            return max(0, min(int(score), 100))
        except:
            return 60

    def analyze_audio(self, audio_bytes: bytes, duration: float = None) -> dict:
        """分析音频特征（无需 AI 模型）

        Args:
            audio_bytes: WebM 音频数据
            duration: 录音时长（秒）

        Returns:
            dict: 包含 volume_db, volume, speed_wpm, speed, confidence, duration
        """
        try:
            audio_io = io.BytesIO(audio_bytes)
            audio = AudioSegment.from_file(audio_io, format="webm")

            if duration is None:
                duration = audio.duration_seconds

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

            volume_db, volume_level = self.get_volume(samples)

            speech_segments = self._detect_speech_segments(samples)
            estimated_words = self._estimate_words(speech_segments, duration)

            wpm, speed_level, word_count = self.get_speed(duration, estimated_words)

            confidence = self.get_confidence(volume_db, wpm)

            return {
                "volume_db": volume_db,
                "volume": volume_level,
                "speed_wpm": wpm,
                "speed": speed_level,
                "confidence": confidence,
                "word_count": word_count,
                "duration": round(duration, 2),
                "speech_ratio": round(len(speech_segments) / duration if duration > 0 else 0, 2),
                "text": "",
                "message": "语音分析完成（无识别）"
            }
        except Exception as e:
            print(f"音频分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "volume_db": -50.0,
                "volume": "正常",
                "speed_wpm": 0,
                "speed": "正常",
                "confidence": 50,
                "word_count": 0,
                "duration": duration or 0,
                "text": "",
                "message": f"分析失败: {str(e)}"
            }

    def _detect_speech_segments(self, samples: np.ndarray, threshold: float = 0.02) -> list:
        """检测语音段落（基于能量）"""
        try:
            frame_length = 1600
            hop_length = 800

            energy = []
            for i in range(0, len(samples) - frame_length, hop_length):
                frame = samples[i:i + frame_length]
                frame_energy = np.sqrt(np.mean(frame**2))
                energy.append(frame_energy)

            energy = np.array(energy)

            speech_mask = energy > threshold

            speech_frames = []
            in_speech = False
            start_frame = 0

            for i, is_speech in enumerate(speech_mask):
                if is_speech and not in_speech:
                    start_frame = i
                    in_speech = True
                elif not is_speech and in_speech:
                    speech_frames.append((start_frame, i))
                    in_speech = False

            if in_speech:
                speech_frames.append((start_frame, len(energy)))

            return speech_frames
        except:
            return []

    def _estimate_words(self, speech_segments: list, duration: float) -> int:
        """基于语音段落估算字数"""
        if not speech_segments:
            return 0

        total_speech_frames = sum(end - start for start, end in speech_segments)
        hop_length = 800

        speech_duration = (total_speech_frames * hop_length) / 16000

        avg_speech_rate = 150
        estimated_words = int(speech_duration * avg_speech_rate / 60)

        return estimated_words

    def analyze_with_text(self, audio_bytes: bytes, recognized_text: str = "", duration: float = None) -> dict:
        """结合识别结果的音频分析"""
        result = self.analyze_audio(audio_bytes, duration)

        if recognized_text:
            char_count = len([c for c in recognized_text if c.strip()])
            result["word_count"] = char_count

            if duration and duration > 0:
                wpm, speed_level, _ = self.get_speed(duration, char_count)
                result["speed_wpm"] = wpm
                result["speed"] = speed_level

                confidence = self.get_confidence(result["volume_db"], wpm)
                result["confidence"] = confidence

        return result


light_speech_analyzer = LightSpeechAnalyzer()