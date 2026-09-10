#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加isAiResponding ref
old_ref = '''const faceAnalysisRef = ref(null)
const inputMode = ref('text')
const interviewMode = ref('text') // text, voice, avatar, camera'''

new_ref = '''const faceAnalysisRef = ref(null)
const inputMode = ref('text')
const interviewMode = ref('text') // text, voice, avatar, camera
const isAiResponding = ref(false)
const currentAiText = ref('')'''

content = content.replace(old_ref, new_ref)

# 2. 修改sendMessage函数，在发送后设置AI响应状态
old_send_start = '''  isLoading.value = true
  
  try {
    const response = await fetch('/api/interview/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: userMessage,
        interview_id: props.currentInterviewId
      })
    })
    
    if (!response.ok) {
      throw new Error('获取AI回复失败')
    }
    
    const data = await response.json()
    
    const aiMessageIndex = props.chatMessages.length
    emit('addMessage', {
      type: 'ai',
      content: data.response,
      time: new Date().toLocaleTimeString()
    })'''

new_send_start = '''  isLoading.value = true
  isAiResponding.value = true

  try {
    const response = await fetch('/api/interview/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: userMessage,
        interview_id: props.currentInterviewId
      })
    })

    if (!response.ok) {
      throw new Error('获取AI回复失败')
    }

    const data = await response.json()

    isAiResponding.value = false
    currentAiText.value = data.response

    const aiMessageIndex = props.chatMessages.length
    emit('addMessage', {
      type: 'ai',
      content: data.response,
      time: new Date().toLocaleTimeString()
    })'''

content = content.replace(old_send_start, new_send_start)

# 3. 修改AIAvatar组件，添加isAiResponding和aiSpeakingText属性
old_avatar = '''          <!-- 中间：数字人 -->
          <div class="avatar-panel">
            <AIAvatar />
          </div>'''

new_avatar = '''          <!-- 中间：数字人 -->
          <div class="avatar-panel">
            <AIAvatar
              :isAiResponding="isAiResponding"
              :aiSpeakingText="currentAiText"
            />
          </div>'''

content = content.replace(old_avatar, new_avatar)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('AIInterviewChat synchronization updated!')
