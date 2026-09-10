import whisper
import numpy as np
import torch

print("检查 CUDA...")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

print("\n加载 Whisper medium 模型...")
model = whisper.load_model("medium", device="cuda")

print("\n测试识别...")
# 创建3秒测试音频
audio = np.random.randn(16000 * 3).astype(np.float32) * 0.01

print(f"音频 shape: {audio.shape}, dtype: {audio.dtype}")
result = model.transcribe(audio, language="zh", fp16=False)
print(f"识别结果: '{result['text']}'")

print("\n完成！")
