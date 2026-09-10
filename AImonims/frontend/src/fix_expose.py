#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复defineExpose，移除不存在的startInterview
old_expose = '''defineExpose({
  startInterview,
  stopInterview,
  isInterviewing,
  triggerAiSpeak
})'''

new_expose = '''defineExpose({
  stopInterview,
  isInterviewing,
  triggerAiSpeak
})'''

content = content.replace(old_expose, new_expose)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('defineExpose fixed!')
