#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIAvatar.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修改watch部分，添加aiSpeakingText的监听
old_watch = '''  watch: {
    asrResult: {
      handler(newVal) {
        if (newVal) {
          this.inputMessage = newVal
        }
      }
    },
    isAiResponding: {
      handler(newVal) {
        if (newVal) {
          this.handleAiStartSpeaking()
        } else {
          this.handleAiEndSpeaking()
        }
      }
    }
  },'''

new_watch = '''  watch: {
    asrResult: {
      handler(newVal) {
        if (newVal) {
          this.inputMessage = newVal
        }
      }
    },
    isAiResponding: {
      handler(newVal) {
        if (newVal) {
          this.handleAiStartSpeaking()
        } else {
          this.handleAiEndSpeaking()
        }
      }
    },
    aiSpeakingText: {
      handler(newVal) {
        if (newVal && newVal.trim()) {
          this.speakAiResponse(newVal)
        }
      }
    }
  },'''

content = content.replace(old_watch, new_watch)

# 添加speakAiResponse方法
old_method = '''    handleAiEndSpeaking() {
      this.currentMood = 'listening'
      this.isAISpeaking = false

      if (this.avatarSvgRef) {
        this.avatarSvgRef.classList.remove('speaking')
      }
    },'''

new_method = '''    handleAiEndSpeaking() {
      this.currentMood = 'listening'
      this.isAISpeaking = false

      if (this.avatarSvgRef) {
        this.avatarSvgRef.classList.remove('speaking')
      }

      // 停止语音
      if (this.speechUtterance) {
        window.speechSynthesis.cancel()
        this.speechUtterance = null
      }
    },

    speakAiResponse(text) {
      // 使用语音合成朗读AI回复
      if ('speechSynthesis' in window) {
        // 先停止之前的朗读
        window.speechSynthesis.cancel()

        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'zh-CN'
        utterance.rate = 1.0
        utterance.pitch = 1.0
        utterance.volume = 1.0

        utterance.onstart = () => {
          this.isAISpeaking = true
          this.currentMood = 'speaking'
        }

        utterance.onend = () => {
          this.isAISpeaking = false
          this.currentMood = 'listening'
          this.speechUtterance = null
        }

        utterance.onerror = () => {
          this.isAISpeaking = false
          this.currentMood = 'listening'
          this.speechUtterance = null
        }

        this.speechUtterance = utterance
        window.speechSynthesis.speak(utterance)
      }
    },'''

content = content.replace(old_method, new_method)

# 添加speechUtterance到data
old_data = '''      isAISpeaking: false,
      currentMood: 'neutral','''

new_data = '''      isAISpeaking: false,
      currentMood: 'neutral',
      speechUtterance: null,'''

content = content.replace(old_data, new_data)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('AI speech synthesis added!')
