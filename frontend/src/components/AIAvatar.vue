<template>
  <div class="ai-avatar-simple">
    <!-- 弱化的标题栏 -->
    <div class="avatar-header">
      <h3>AI面试官</h3>
    </div>

    <!-- 虚拟人展示区 - 核心主体 -->
    <div class="avatar-display">
      <div class="avatar-scene active">
        <!-- 装饰背景 -->
        <div class="scene-background">
          <div class="bg-gradient"></div>
          <div class="bg-grid"></div>
          <div class="bg-decor-circles"></div>
        </div>

        <!-- 虚拟人主体 -->
        <div class="live2d-wrapper">
          <Live2DAvatar
            ref="live2dAvatarRef"
            :modelUrl="selectedLive2DModel"
            :scale="0.45"
            @loaded="handleLive2DLoaded"
            @error="handleLive2DError"
            @speakStart="handleLive2DSpeakStart"
            @speakEnd="handleLive2DSpeakEnd"
          />
        </div>

        <!-- 状态气泡 - 移到虚拟人下巴下方，与主体关联 -->
        <div class="mood-indicator" v-if="currentMood === 'listening' || currentMood === 'speaking'">
          <div class="mood-badge" :class="currentMood">
            <span v-if="currentMood === 'listening'">正在倾听...</span>
            <span v-else-if="currentMood === 'speaking'">回答中...</span>
          </div>
          <div class="voice-waves" v-if="currentMood === 'listening'">
            <span class="wave"></span>
            <span class="wave"></span>
            <span class="wave"></span>
          </div>
        </div>

        <!-- 声音选择小按钮 - 右上角 -->
        <div class="voice-selector">
          <el-popover
            placement="bottom-end"
            width="280"
            trigger="click"
          >
            <div class="voice-popover">
              <h4>选择面试官声音</h4>
              <div v-if="availableVoices.length === 0" class="loading-voices">
                <i class="el-icon-loading"></i> 加载中...
              </div>
              <div v-else class="voice-list">
                <div
                  v-for="(voiceInfo, voiceKey) in availableVoices"
                  :key="voiceKey"
                  class="voice-item"
                  :class="{ active: localSelectedVoice === voiceKey }"
                  @click="selectVoice(voiceKey)"
                >
                  <div class="voice-name">{{ voiceInfo.name }}</div>
                  <div class="voice-desc">{{ voiceInfo.description }}</div>
                </div>
              </div>
            </div>
            <el-button slot="reference" class="voice-btn" type="primary" plain circle>
              <i class="el-icon-setting"></i>
            </el-button>
          </el-popover>
        </div>
      </div>
    </div>

    <!-- 显眼的状态栏 -->
    <div class="avatar-status">
      <div class="status-indicator" :class="{ active: true, speaking: isAISpeaking }"></div>
      <span class="status-text">{{ isAISpeaking ? '面试官回答中' : '面试进行中' }}</span>
    </div>
  </div>
</template>

<script>
import Live2DAvatar from './Live2DAvatar.vue'

export default {
  name: 'AIAvatar',
  components: {
    Live2DAvatar
  },
  props: {
    isAiResponding: {
      type: Boolean,
      default: false
    },
    aiSpeakingText: {
      type: String,
      default: ''
    },
    selectedVoice: {
      type: String,
      default: 'Cherry'
    }
  },
  data() {
    return {
      selectedLive2DModel: 'hiyori',
      live2dAvatarRef: null,
      isAISpeaking: false,
      currentMood: 'listening',
      audioElement: null,
      localSelectedVoice: 'Cherry',
      availableVoices: {}
    }
  },
  watch: {
    aiSpeakingText: {
      handler(newVal) {
        if (newVal && newVal.trim()) {
          this.speakAiResponse(newVal)
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
    selectedVoice: {
      handler(newVal) {
        if (newVal) {
          this.localSelectedVoice = newVal
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.startBlinkAnimation()
    this.loadVoices()
  },
  beforeUnmount() {
    if (this.audioElement) {
      this.audioElement.pause()
      this.audioElement = null
    }
    // 眨眼定时器原先没有句柄也从不清理，组件卸载后仍在轮询 DOM
    if (this.blinkTimer) {
      clearInterval(this.blinkTimer)
      this.blinkTimer = null
    }
  },
  methods: {
    async loadVoices() {
      try {
        const response = await fetch('/api/avatar/voices')
        const data = await response.json()
        this.availableVoices = data.voices
        console.log('阿里云TTS声音:', this.availableVoices)
      } catch (error) {
        console.error('加载声音列表失败:', error)
      }
    },
    selectVoice(voiceName) {
      this.localSelectedVoice = voiceName
      console.log('声音已切换:', voiceName)
      this.$message.success('声音已切换')
      this.$emit('voice-change', voiceName)
    },
    handleLive2DLoaded() {
      console.log('Live2D 模型加载完成')
    },
    handleLive2DError(error) {
      console.error('Live2D 错误:', error)
    },
    handleLive2DSpeakStart() {
      this.isAISpeaking = true
    },
    handleLive2DSpeakEnd() {
      this.isAISpeaking = false
    },
    handleAiStartSpeaking() {
      this.currentMood = 'speaking'
    },
    handleAiEndSpeaking() {
      this.currentMood = 'listening'
    },
    async speakAiResponse(text) {
      if (!text || !text.trim()) {
        return
      }

      this.currentMood = 'speaking'
      this.isAISpeaking = true

      if (this.audioElement) {
        this.audioElement.pause()
      }

      try {
        const response = await fetch('/api/avatar/tts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: text,
            voice_type: this.localSelectedVoice
          })
        })

        if (!response.ok) {
          throw new Error('TTS请求失败')
        }

        const audioBlob = await response.blob()
        const audioUrl = URL.createObjectURL(audioBlob)

        this.audioElement = new Audio(audioUrl)
        this.audioElement.onended = () => {
          this.isAISpeaking = false
          this.currentMood = 'listening'
          URL.revokeObjectURL(audioUrl)
        }
        this.audioElement.onerror = () => {
          this.isAISpeaking = false
          this.currentMood = 'listening'
          this.$message.error('音频播放失败')
        }
        if (this.audioElement.src && this.audioElement.readyState >= 2) {
          this.audioElement.play().catch(err => {
            console.error('音频播放失败:', err)
            this.isAISpeaking = false
            this.currentMood = 'listening'
          })
        } else {
          this.audioElement.oncanplay = () => {
            this.audioElement.play().catch(err => {
              console.error('音频播放失败:', err)
              this.isAISpeaking = false
              this.currentMood = 'listening'
            })
          }
        }
      } catch (error) {
        console.error('阿里云TTS播放失败:', error)
        this.isAISpeaking = false
        this.currentMood = 'listening'
        this.$message.error('语音播放失败，请稍后重试')
      }
    },
    startBlinkAnimation() {
      if (this.blinkTimer) clearInterval(this.blinkTimer)
      this.blinkTimer = setInterval(() => {
        if (this.isAISpeaking || this.currentMood === 'speaking') return
        const blinkLids = document.querySelectorAll('.blink-lid-left, .blink-lid-right')
        blinkLids.forEach(lid => {
          lid.style.opacity = '1'
          setTimeout(() => {
            lid.style.opacity = '0'
          }, 100)
        })
      }, 3000 + Math.random() * 2000)
    }
  }
}
</script>

<style scoped>
.ai-avatar-simple {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
}

/* 弱化的标题栏 */
.avatar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(8px);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.avatar-header h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
}

/* 虚拟人展示区 - 核心主体，占据更多空间 */
.avatar-display {
  flex: 1;
  min-height: 0;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(25px);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 8px 40px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.avatar-scene {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 装饰背景 */
.scene-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, 
    rgba(26, 26, 46, 0.95) 0%, 
    rgba(22, 33, 62, 0.98) 40%, 
    rgba(15, 52, 96, 0.95) 100%);
}

/* 网格装饰 */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.06) 1px, transparent 1px);
  background-size: 40px 40px;
  background-position: center;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 40px 40px; }
}

/* 装饰圆 */
.bg-decor-circles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-decor-circles::before {
  content: '';
  position: absolute;
  top: 10%;
  right: 10%;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
  animation: floatCircle 8s ease-in-out infinite;
}

.bg-decor-circles::after {
  content: '';
  position: absolute;
  bottom: 15%;
  left: 8%;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.12) 0%, transparent 70%);
  animation: floatCircle 6s ease-in-out infinite reverse;
}

@keyframes floatCircle {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.8; }
  50% { transform: translateY(-15px) scale(1.1); opacity: 1; }
}

/* 虚拟人包装器 - 更大的展示空间，确保在最上层 */
.live2d-wrapper {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
}

/* 状态气泡 - 移到虚拟人下巴下方，与主体关联 */
.mood-indicator {
  position: absolute;
  bottom: 15%;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  z-index: 5;
}

/* 弱化气泡样式，不抢焦点 */
.mood-badge {
  padding: 6px 16px;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.mood-badge.speaking {
  background: rgba(64, 158, 255, 0.5);
  color: white;
  border: 1px solid rgba(64, 158, 255, 0.4);
}

.mood-badge.listening {
  background: rgba(103, 194, 58, 0.4);
  color: white;
  border: 1px solid rgba(103, 194, 58, 0.3);
}

/* 语音波纹动画 */
.voice-waves {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 4px;
  height: 20px;
}

.voice-waves .wave {
  width: 3px;
  background: linear-gradient(to top, rgba(103, 194, 58, 0.8), rgba(103, 194, 58, 0.3));
  border-radius: 2px;
  animation: voiceWave 0.8s ease-in-out infinite;
}

.voice-waves .wave:nth-child(1) {
  height: 8px;
  animation-delay: 0s;
}

.voice-waves .wave:nth-child(2) {
  height: 16px;
  animation-delay: 0.15s;
}

.voice-waves .wave:nth-child(3) {
  height: 12px;
  animation-delay: 0.3s;
}

@keyframes voiceWave {
  0%, 100% {
    transform: scaleY(0.5);
    opacity: 0.5;
  }
  50% {
    transform: scaleY(1);
    opacity: 1;
  }
}

/* 声音选择小按钮 - 右上角 */
/* 声音选择小按钮 - 左上角 */
.voice-selector {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 20;
}

.voice-btn {
  width: 36px;
  height: 36px;
  background: rgba(102, 126, 234, 0.3) !important;
  backdrop-filter: blur(16px);
  border: 1px solid rgba(102, 126, 234, 0.5) !important;
  transition: all 0.3s ease;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-btn:hover {
  background: rgba(102, 126, 234, 0.5) !important;
  border-color: rgba(102, 126, 234, 0.8) !important;
  transform: scale(1.1);
}

.voice-btn i {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.95);
}

/* 声音选择弹窗 */
.voice-popover {
  padding: 8px;
}

.voice-popover h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #ffffff;
  font-weight: 600;
}

.loading-voices {
  padding: 20px;
  text-align: center;
  color: #a0a0c0;
  font-size: 13px;
}

.voice-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 250px;
  overflow-y: auto;
}

.voice-item {
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.voice-item:hover {
  background: rgba(102, 126, 234, 0.1);
}

.voice-item.active {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
}

.voice-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 2px;
}

.voice-desc {
  font-size: 12px;
  color: #a0a0c0;
}

/* 显眼的状态栏 */
.avatar-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: rgba(102, 126, 234, 0.08);
  backdrop-filter: blur(16px);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #67C23A;
  transition: all 0.3s;
  flex-shrink: 0;
  animation: statusGlow 2s ease-in-out infinite;
}

@keyframes statusGlow {
  0%, 100% { 
    box-shadow: 0 0 8px rgba(103, 194, 58, 0.5);
  }
  50% { 
    box-shadow: 0 0 14px rgba(103, 194, 58, 0.8);
  }
}

.status-indicator.speaking {
  background: #409EFF;
  animation: speakingGlow 0.8s ease-in-out infinite;
}

@keyframes speakingGlow {
  0%, 100% { 
    box-shadow: 0 0 10px rgba(64, 158, 255, 0.6);
  }
  50% { 
    box-shadow: 0 0 18px rgba(64, 158, 255, 0.9);
  }
}

.status-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  letter-spacing: 0.3px;
}
</style>
