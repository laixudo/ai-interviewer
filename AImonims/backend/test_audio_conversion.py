import whisper
import numpy as np
import torch
import io
from pydub import AudioSegment
import imageio_ffmpeg

AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

print("加载 Whisper medium 模型...")
model = whisper.load_model("medium", device="cuda")

# 读取实际录音文件测试
import sqlite3
conn = sqlite3.connect('interview.db')
cur = conn.cursor()
cur.execute('SELECT audio_data FROM speech_records ORDER BY id DESC LIMIT 1')
row = cur.fetchone()
conn.close()

if row and row[0]:
    audio_bytes = row[0]
    print(f"音频数据大小: {len(audio_bytes)} bytes")

    # 转换为 Whisper 格式
    audio_io = io.BytesIO(audio_bytes)
    try:
        audio = AudioSegment.from_file(audio_io, format="webm")
        audio = audio.set_frame_rate(16000).set_channels(1)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
        print(f"转换后 samples 长度: {len(samples)}, dtype: {samples.dtype}")
        print(f"Samples min/max: {samples.min():.4f} / {samples.max():.4f}")
        print(f"Samples RMS: {np.sqrt(np.mean(samples**2)):.6f}")

        # 识别
        result = model.transcribe(samples, language="zh", fp16=False)
        print(f"识别结果: '{result['text']}'")
    except Exception as e:
        print(f"转换失败: {e}")
else:
    print("没有找到录音数据")
