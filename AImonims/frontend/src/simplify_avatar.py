#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIAvatar.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 隐藏AIAvatar自己的头部控制
old_header = '''    <div class="avatar-header">
      <h3>AI模拟面试</h3>
      <div class="avatar-controls">
        <el-select v-model="selectedLive2DModel" placeholder="选择面试官" size="small" @change="handleLive2DModelChange">
          <el-option label="女面试官" value="female"></el-option>
          <el-option label="男面试官" value="male"></el-option>
        </el-select>
        <el-select v-model="selectedVoice" placeholder="选择声音" size="small" @change="handleVoiceChange">
          <el-option label="艾夏(芊悦)" value="Cherry"></el-option>
          <el-option label="苏瑶" value="Serena"></el-option>
          <el-option label="晨煦(男声)" value="Ethan"></el-option>
          <el-option label="千雪(二次元)" value="Chelsie"></el-option>
          <el-option label="茉兔" value="Momo"></el-option>
          <el-option label="月白(帅气)" value="Moon"></el-option>
          <el-option label="四月(知性)" value="Maia"></el-option>
          <el-option label="凯(耳朵SPA)" value="Kai"></el-option>
          <el-option label="萌宝(萝莉)" value="Bella"></el-option>
          <el-option label="甜茶" value="Ryan"></el-option>
          <el-option label="沧明子(老者)" value="Eldric_Sage"></el-option>
          <el-option label="邻家妹妹" value="Nini"></el-option>
        </el-select>
        <el-button type="primary" size="small" @click="startAvatar">开始面试</el-button>
      </div>
    </div>'''

new_header = '''    <div class="avatar-header" style="display: none;">
      <h3>AI模拟面试</h3>
    </div>'''

content = content.replace(old_header, new_header)

# 2. 隐藏AIAvatar自己的聊天区域
old_chat_area = '''      <div class="avatar-interaction">
        <div class="interaction-header">
          <h4>面试对话</h4>
          <div class="input-mode-toggle">
            <el-radio-group v-model="inputMode" size="small">
              <el-radio-button value="voice">语音回答</el-radio-button>
              <el-radio-button value="text">文字输入</el-radio-button>
            </el-radio-group>
          </div>
        </div>

        <div class="interaction-content">
          <div class="message-list" ref="messageList">
            <div v-for="(message, index) in messages" :key="index"
                 :class="['message-item', message.type]"
                 :data-type="message.type">
              <div class="message-avatar">
                <svg v-if="message.type === 'ai'" viewBox="0 0 32 32" class="avatar-svg">
                  <circle cx="16" cy="12" r="6" fill="#409EFF"/>
                  <path d="M8 20 L24 20 L24 28 C24 30 20 32 16 32 C12 32 8 30 8 28 Z" fill="#409EFF"/>
                </svg>
                <svg v-else viewBox="0 0 32 32" class="avatar-svg">
                  <circle cx="16" cy="12" r="6" fill="#67C23A"/>
                  <path d="M8 20 L24 20 L24 28 C24 30 20 32 16 32 C12 32 8 30 8 28 Z" fill="#67C23A"/>
                </svg>
              </div>
              <div class="message-content" :class="{ 'ai-speaking': message.type === 'ai' && isAiResponding && index === messages.length - 1 }">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ message.time }}</div>
                <div v-if="message.type === 'ai'" class="message-actions">
                  <el-button link size="small" @click="playMessage(message)">
                    <i class="el-icon-video-camera"></i> 播放
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <div class="input-area">
            <div v-if="inputMode === 'voice'" class="voice-input">
              <div class="voice-wave" :class="{ active: isRecording }">
                <div v-for="i in 5" :key="i" class="wave-bar" :style="{ animationDelay: i * 0.1 + 's' }"></div>
              </div>
              <el-button
                :type="isRecording ? 'danger' : 'primary'"
                @click="toggleVoiceRecording"
                :icon="isRecording ? 'el-icon-close' : 'el-icon-microphone'"
                circle
                size="large"
              ></el-button>
              <div class="voice-status">{{ voiceStatus }}</div>
            </div>
            <div v-else class="text-input">
              <el-input
                v-model="inputMessage"
                type="textarea"
                placeholder="请输入您的回答..."
                :rows="3"
              ></el-input>
              <el-button type="primary" @click="sendTextMessage">提交回答</el-button>
            </div>
            <div v-if="asrMetrics" class="asr-metrics">
              <div class="metric-item">
                <span class="metric-label">语速</span>
                <el-progress :percentage="Math.round(asrMetrics.speech_rate * 10)" :stroke-width="6" :show-text="true"></el-progress>
                <span class="metric-value">{{ asrMetrics.speech_rate }} 字/秒</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">清晰度</span>
                <el-progress :percentage="Math.round(asrMetrics.clarity * 100)" :stroke-width="6" :show-text="true"></el-progress>
                <span class="metric-value">{{ (asrMetrics.clarity * 100).toFixed(0) }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">自信度</span>
                <el-progress :percentage="Math.round(asrMetrics.confidence * 100)" :stroke-width="6" :show-text="true"></el-progress>
                <span class="metric-value">{{ (asrMetrics.confidence * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>'''

new_chat_area = ''''''

content = content.replace(old_chat_area, new_chat_area)

# 3. 自动激活数字人，隐藏覆盖层
old_scene_overlay = '''            <div class="scene-overlay" v-if="!isAvatarActive">
              <div class="overlay-content">
                <div class="interviewer-badge">
                  <svg viewBox="0 0 24 24" width="18" height="18">
                    <circle cx="12" cy="8" r="4" fill="#409EFF"/>
                    <path d="M12 14 L12 20 M8 16 L16 16 M8 20 L16 20" stroke="#409EFF" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  <span>AI模拟面试官</span>
                </div>
                <p class="interviewer-info">
                  <template v-if="selectedLive2DModel === 'male'">
                    男面试官 · 职场精英 · 沉稳专业
                  </template>
                  <template v-else>
                    女面试官 · 职场精英 · 知性优雅
                  </template>
                </p>
                <p class="interviewer-hint">点击「开始面试」与面试官对话</p>
              </div>
            </div>'''

new_scene_overlay = ''''''

content = content.replace(old_scene_overlay, new_scene_overlay)

# 4. 设置isAvatarActive默认为true，并自动设置currentMood
old_data = '''      isAvatarActive: false,
      isAISpeaking: false,
      currentMood: 'neutral','''

new_data = '''      isAvatarActive: true,
      isAISpeaking: false,
      currentMood: 'listening','''

content = content.replace(old_data, new_data)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('AIAvatar simplified!')
