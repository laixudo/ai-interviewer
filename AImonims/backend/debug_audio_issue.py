import os
import io
import numpy as np
import whisper
import soundfile as sf
import librosa
from pydub import AudioSegment
import imageio_ffmpeg

AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

print("=" * 50)
print("详细音频诊断")
print("=" * 50)

# 读取实际录音
import sqlite3
conn = sqlite3.connect('interview.db')
cur = conn.cursor()
cur.execute('SELECT audio_data, duration FROM speech_records ORDER BY id DESC LIMIT 1')
row = cur.fetchone()
conn.close()

if not row or not row[0]:
    print("没有找到录音数据")
    exit()

audio_bytes = row[0]
duration = row[1]
print(f"\n1. 原始数据信息:")
print(f"   音频数据大小: {len(audio_bytes)} bytes")
print(f"   录音时长: {duration}秒")

# 保存原始文件
os.makedirs("debug_audio", exist_ok=True)
with open("debug_audio/raw_recording.webm", "wb") as f:
    f.write(audio_bytes)
print(f"   已保存: debug_audio/raw_recording.webm")

# 检查文件头
print(f"\n2. 文件头分析:")
print(f"   前20字节 (hex): {audio_bytes[:20].hex()}")
if audio_bytes[:4] == b'RIFF':
    print(f"   格式: RIFF (可能是 WAV)")
elif audio_bytes[:4] == b'\x1aE\xdf\xa3':
    print(f"   格式: WebM/MKV")
elif audio_bytes[:8] == b'\x00\x00\x00\x1cftypmp4':
    print(f"   格式: MP4/M4A")
else:
    print(f"   格式: 未知")

# pydub 转换
print(f"\n3. pydub 转换:")
try:
    audio_io = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_io)
    print(f"   类型: {type(audio)}")
    print(f"   frame_rate: {audio.frame_rate}")
    print(f"   channels: {audio.channels}")
    print(f"   frame_count: {audio.frame_count()}")
    print(f"   duration_seconds: {audio.duration_seconds}")

    # 转换为 16kHz 单声道
    audio_16k = audio.set_frame_rate(16000).set_channels(1)
    samples = np.array(audio_16k.get_array_of_samples(), dtype=np.float32)

    # 检查是否是 16-bit 音频
    if audio_16k.sample_width == 2:
        samples = samples / 32768.0
    elif audio_16k.sample_width == 1:
        samples = samples / 128.0

    print(f"   转换后 frame_rate: {audio_16k.frame_rate}")
    print(f"   转换后 channels: {audio_16k.channels}")
    print(f"   转换后 sample_width: {audio_16k.sample_width}")
    print(f"   转换后长度: {len(samples)}")
    print(f"   转换后 dtype: {samples.dtype}")
    print(f"   转换后 min/max: {samples.min():.4f} / {samples.max():.4f}")
    rms = np.sqrt(np.mean(samples**2))
    print(f"   转换后 RMS: {rms:.6f}")
    print(f"   转换后 dB: {20 * np.log10(rms + 1e-10):.2f} dB")

    # 保存转换后的文件
    sf.write("debug_audio/converted_16k.wav", samples, 16000)
    print(f"   已保存: debug_audio/converted_16k.wav")

except Exception as e:
    print(f"   pydub 处理失败: {e}")
    import traceback
    traceback.print_exc()
    samples = None

# Whisper 识别测试
print(f"\n4. Whisper 识别测试:")
if samples is not None and len(samples) > 0:
    print(f"   加载模型 (medium, cuda)...")
    model = whisper.load_model("medium", device="cuda")

    for test_len in [2, 3, duration]:
        print(f"\n   测试 {test_len}秒音频:")

        if len(samples) >= test_len * 16000:
            test_audio = samples[:int(test_len * 16000)]
        else:
            test_audio = np.pad(samples, (0, int(test_len * 16000) - len(samples)))

        # 测试不同的语言
        for lang, lang_name in [("zh", "指定中文"), ("auto", "自动检测")]:
            try:
                if lang == "auto":
                    result = model.transcribe(test_audio.astype(np.float32), fp16=False)
                else:
                    result = model.transcribe(test_audio.astype(np.float32), language=lang, fp16=False)

                text = result.get("text", "").strip()
                lang_detected = result.get("language", "unknown")
                segments = result.get("segments", [])
                no_speech_prob = segments[0].get("no_speech_prob", 0) if segments else 0

                print(f"      {lang_name}: '{text}' (检测语言:{lang_detected}, 无语音概率:{no_speech_prob:.3f})")
            except Exception as e:
                print(f"      {lang_name}: 失败 - {e}")
else:
    print("   没有可用的音频数据")

print("\n诊断完成！")
