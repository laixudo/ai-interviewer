import whisper
import numpy as np

print("加载Whisper模型...")
model = whisper.load_model('base', device='cpu')

print("\n测试 Whisper transcribe...")

# 测试 transcribe - 自动检测语言
audio = np.random.randn(16000 * 3).astype(np.float32) * 0.01  # 3秒随机噪声
result = model.transcribe(audio, fp16=False)
print(f"测试1 (无语言指定): '{result['text']}'")

# 测试指定语言
result2 = model.transcribe(audio, language='zh', fp16=False)
print(f"测试2 (指定中文): '{result2['text']}'")

# 测试 initial_prompt 参数
result3 = model.transcribe(audio, language='zh', fp16=False, initial_prompt="这是一个中文语音识别测试")
print(f"测试3 (带提示): '{result3['text']}'")

# 测试 task="translate"
result4 = model.transcribe(audio, language='zh', fp16=False, task="transcribe")
print(f"测试4 (transcribe任务): '{result4['text']}'")

# 测试 without_speech_threshold
result5 = model.transcribe(audio, language='zh', fp16=False, without_speech_threshold=0.5)
print(f"测试5 (无语音阈值): '{result5['text']}'")

# 打印完整的 result
print(f"\n完整结果: {result5}")

print("\n测试完成")
