#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIAvatar.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改props定义
old_props = '''  props: {
    interviewId: {
      type: [Number, String],
      default: null
    },
    isAiResponding: {
      type: Boolean,
      default: false
    },
    aiSpeakingText: {
      type: String,
      default: ''
    }
  },'''

new_props = '''  props: {
    interviewId: {
      type: [Number, String],
      default: null
    },
    isAiResponding: {
      type: Boolean,
      default: false
    },
    aiSpeakingText: {
      type: String,
      default: ''
    }
  },'''

# 保持props不变，但修改watch部分
content = content.replace(old_props, old_props)

# 2. 修改watch部分，使用Options API语法
old_watch = '''  watch: {
    currentMood(newMood) {
      this.updateMouthColor()
    }
  },'''

new_watch = '''  watch: {
    currentMood(newMood) {
      this.updateMouthColor()
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

# 3. 添加speechUtterance到data
old_data = '''      isAISpeaking: false,
      currentMood: 'neutral','''

new_data = '''      isAISpeaking: false,
      currentMood: 'neutral',
      speechUtterance: null,'''

content = content.replace(old_data, new_data)

# 4. 添加handleAiStartSpeaking和handleAiEndSpeaking方法
old_methods = '''    handleLive2DError(error) {
      console.error('Live2D加载失败:', error)
      this.$message.error('数字人加载失败，请刷新页面重试')
    },'''

new_methods = '''    handleLive2DError(error) {
      console.error('Live2D加载失败:', error)
      this.$message.error('数字人加载失败，请刷新页面重试')
    },

    handleAiStartSpeaking() {
      this.currentMood = 'speaking'
      this.isAISpeaking = true

      if (this.avatarSvgRef) {
        this.avatarSvgRef.classList.add('speaking')
      }
    },

    handleAiEndSpeaking() {
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

content = content.replace(old_methods, new_methods)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('AIAvatar Options API version updated!')
