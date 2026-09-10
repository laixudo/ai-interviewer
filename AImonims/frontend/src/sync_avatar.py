#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIAvatar.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改props定义，添加aiResponding属性
old_props = '''  props: {
    interviewId: {
      type: [Number, String],
      default: null
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

content = content.replace(old_props, new_props)

# 2. 添加watch来监听AI响应状态
old_watch_start = '''  watch: {
    asrResult: {
      handler(newVal) {
        if (newVal) {
          this.inputMessage = newVal
        }
      }
    }
  },'''

new_watch_start = '''  watch: {
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

content = content.replace(old_watch_start, new_watch_start)

# 3. 添加处理AI发言的方法
old_methods_start = '''    handleLive2DError(error) {
      console.error('Live2D加载失败:', error)
      this.$message.error('数字人加载失败，请刷新页面重试')
    },'''

new_methods_start = '''    handleLive2DError(error) {
      console.error('Live2D加载失败:', error)
      this.$message.error('数字人加载失败，请刷新页面重试')
    },

    handleAiStartSpeaking() {
      this.currentMood = 'speaking'
      this.isAISpeaking = true

      if (this.avatarMode === 'svg' && this.avatarSvgRef) {
        this.avatarSvgRef.classList.add('speaking')
      }
    },

    handleAiEndSpeaking() {
      this.currentMood = 'listening'
      this.isAISpeaking = false

      if (this.avatarSvgRef) {
        this.avatarSvgRef.classList.remove('speaking')
      }
    },'''

content = content.replace(old_methods_start, new_methods_start)

# 4. 修改模板，在AI回复时触发发言动画
old_message_item = '''              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ message.time }}</div>
                <div v-if="message.type === 'ai'" class="message-actions">
                  <el-button link size="small" @click="playMessage(message)">
                    <i class="el-icon-video-camera"></i> 播放
                  </el-button>
                </div>
              </div>'''

new_message_item = '''              <div class="message-content" :class="{ 'ai-speaking': message.type === 'ai' && isAiResponding && index === messages.length - 1 }">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ message.time }}</div>
                <div v-if="message.type === 'ai'" class="message-actions">
                  <el-button link size="small" @click="playMessage(message)">
                    <i class="el-icon-video-camera"></i> 播放
                  </el-button>
                </div>
              </div>'''

content = content.replace(old_message_item, new_message_item)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('AIAvatar synchronization updated!')
