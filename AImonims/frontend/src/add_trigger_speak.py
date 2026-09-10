#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在handleFaceAnalysisResult方法后添加triggerAiSpeak方法
old_handler = '''const handleFaceAnalysisResult = (result) => {
  console.log('面部分析结果:', result)
}'''

new_handler = '''const handleFaceAnalysisResult = (result) => {
  console.log('面部分析结果:', result)
}

// 暴露给父组件的方法，用于触发数字人朗读
const triggerAiSpeak = (text) => {
  if (text && text.trim()) {
    isAiResponding.value = true
    currentAiText.value = text
    // 延迟重置状态，让数字人有时间开始朗读
    setTimeout(() => {
      isAiResponding.value = false
    }, 100)
  }
}

defineExpose({
  startInterview,
  stopInterview,
  isInterviewing,
  triggerAiSpeak
})'''

content = content.replace(old_handler, new_handler)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('AIInterviewChat triggerAiSpeak method added!')
