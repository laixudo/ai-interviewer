<template>
  <div class="ai-interview-wrapper">
    <!-- 统一AI面试页面 -->
    <div class="main-content unified-chat-page" :class="{ 'animate-in': mounted }">
      <!-- 头部 -->
      <div class="chat-header">
        <div class="header-left">
          <div class="back-btn" @click="handleBack">
            <i class="el-icon-arrow-left"></i>
            <span class="back-text">返回</span>
          </div>
          <div class="header-info">
            <h2 class="chat-title">{{ props.job }}</h2>
            <div class="chat-subtitle">
              <span class="subtitle-badge">
                <i class="el-icon-user"></i>
                AI面试官
              </span>
              <span class="subtitle-divider">|</span>
              <span class="subtitle-text">模拟面试中</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <!-- 声音选择按钮 -->
          <div class="voice-selector" @click="toggleVoiceSelector">
            <div class="voice-popover-content" v-if="showVoicePopover">
              <h4>选择面试官声音</h4>
              <div v-if="!availableVoices || Object.keys(availableVoices).length === 0" class="loading-voices">
                <i class="el-icon-loading"></i> 加载中...
              </div>
              <div v-else class="voice-list">
                <div
                  v-for="(voiceInfo, voiceKey) in availableVoices"
                  :key="voiceKey"
                  class="voice-item"
                  :class="{ active: selectedVoice === voiceKey }"
                  @click.stop="selectVoice(voiceKey)"
                >
                  <div class="voice-name">{{ voiceInfo.name }}</div>
                  <div class="voice-desc">{{ voiceInfo.description }}</div>
                </div>
              </div>
            </div>
            <button class="voice-btn-native">
              <i class="el-icon-setting"></i>
              <span>声音切换</span>
            </button>
          </div>
          
          <button class="end-interview-btn" @click="showEndInterviewConfirm">
            <i class="el-icon-close"></i>
            终止面试
          </button>
          <div class="mode-switch">
            <button
              class="mode-btn"
              :class="{ active: interviewMode === 'text' }"
              @click="setInterviewMode('text')"
            >
              <i class="el-icon-edit"></i>
              文字
            </button>
            <button
              class="mode-btn"
              :class="{ active: interviewMode === 'voice' }"
              @click="setInterviewMode('voice')"
            >
              <i class="el-icon-microphone"></i>
              语音
            </button>
            <button
              class="mode-btn"
              :class="{ active: interviewMode === 'avatar' }"
              @click="setInterviewMode('avatar')"
            >
              <i class="el-icon-video-camera"></i>
              数字人
            </button>
          </div>
          <div class="progress-ring-wrapper">
            <div class="progress-ring">
              <svg viewBox="0 0 100 100">
                <circle class="ring-bg" cx="50" cy="50" r="45" />
                <circle 
                  class="ring-progress" 
                  cx="50" cy="50" r="45"
                  :stroke-dasharray="283 * (props.currentQuestionIndex + 1) / props.totalQuestions + ' 283'"
                />
              </svg>
              <div class="progress-center">
                <span class="progress-current">{{ props.currentQuestionIndex + 1 }}</span>
                <span class="progress-separator">/</span>
                <span class="progress-total">{{ props.totalQuestions }}</span>
              </div>
            </div>
            <div class="progress-label">答题进度</div>
          </div>
        </div>
      </div>

      <!-- 状态栏 -->
      <div class="status-bar">
        <div class="status-item">
          <div class="status-dot" :class="{ recording: isLoading }"></div>
          <span>{{ isLoading ? 'AI思考中...' : '等待回答' }}</span>
        </div>
        <div class="status-item" v-if="isRecording">
          <div class="status-dot recording"></div>
          <span>正在录音</span>
        </div>
        <div class="status-item mode-indicator">
          <i :class="inputMode === 'voice' ? 'el-icon-microphone' : 'el-icon-edit'"></i>
          <span>{{ inputMode === 'voice' ? '语音输入模式' : '文字输入模式' }}</span>
        </div>
      </div>
      
      <!-- 对话区域 -->
      <div v-if="interviewMode !== 'avatar'" class="chat-container">
        <div class="chat-messages" ref="chatMessagesRef">
          <transition-group name="message-slide" tag="div" class="messages-wrapper">
            <div 
              v-for="(message, index) in props.chatMessages" 
              :key="index" 
              :class="['message-item', message.type, { 'animate-in': true }]"
              :style="{ animationDelay: (index * 0.05) + 's' }"
            >
              <div v-if="message.type !== 'system'" class="message-avatar">
                <div class="avatar-wrapper">
                  <img 
                    v-if="message.type === 'ai'" 
                    src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20wearing%20glasses%20and%20suits&image_size=square" 
                    alt="AI面试官" 
                    class="avatar-img"
                  >
                  <img 
                    v-else 
                    src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20avatar&image_size=square" 
                    alt="用户" 
                    class="avatar-img"
                  >
                  <div class="avatar-badge" v-if="message.type === 'ai'">
                    <i class="el-icon-connection"></i>
                  </div>
                </div>
              </div>
              
              <div class="message-bubble">
                    <div v-if="message.type === 'system'" class="system-message">
                      <el-button 
                        v-if="message.content === 'evaluate'" 
                        type="success" 
                        @click="evaluateInterview" 
                        class="evaluate-btn"
                      >
                        <i class="el-icon-document"></i>
                        查看评估报告
                      </el-button>
                    </div>
                    
                    <div v-else class="message-content">
                      <div v-if="message.audioUrl" class="audio-player">
                        <audio :src="message.audioUrl" controls class="audio-element"></audio>
                      </div>
                      <div class="message-text" :class="{ 'ai-message': message.type === 'ai', 'user-message': message.type === 'user' }">
                        <template v-if="message.type === 'ai' && speakingIndex === index">
                          <span class="typing-indicator">
                            <span></span><span></span><span></span>
                          </span>
                        </template>
                        <template v-else>
                          {{ message.content }}
                        </template>
                      </div>
                      
                      <div v-if="message.speechAnalysis && message.type === 'user'" class="speech-analysis">
                        <div class="analysis-header">
                          <i class="el-icon-data-line"></i>
                          <span>语音分析</span>
                        </div>
                        <div class="analysis-items">
                          <div class="analysis-item">
                            <span class="analysis-label">语速</span>
                            <div class="analysis-value">
                              <el-progress 
                                :percentage="message.speechAnalysis.speech_rate_score" 
                                :color="getProgressColor(message.speechAnalysis.speech_rate_score)"
                                :stroke-width="8"
                              ></el-progress>
                              <span class="analysis-text">{{ message.speechAnalysis.speech_rate }}</span>
                            </div>
                          </div>
                          <div class="analysis-item">
                            <span class="analysis-label">自信度</span>
                            <div class="analysis-value">
                              <el-progress 
                                :percentage="message.speechAnalysis.confidence_score" 
                                :color="getProgressColor(message.speechAnalysis.confidence_score)"
                                :stroke-width="8"
                              ></el-progress>
                              <span class="analysis-text">{{ message.speechAnalysis.confidence }}</span>
                            </div>
                          </div>
                          <div v-if="message.speechAnalysis.tone" class="analysis-item">
                            <span class="analysis-label">语气</span>
                            <span class="analysis-tag">{{ getToneLabel(message.speechAnalysis.tone_type) }}</span>
                          </div>
                        </div>
                        <div v-if="message.speechAnalysis.overall_analysis" class="analysis-overall">
                          <i class="el-icon-info"></i>
                          {{ message.speechAnalysis.overall_analysis }}
                        </div>
                      </div>
                      
                      <div class="message-footer">
                        <span class="message-time">{{ message.time }}</span>
                        <div class="footer-right">
                          <el-button 
                            v-if="message.type === 'ai'" 
                            @click="speakText(message.content)" 
                            class="play-voice-btn"
                            :class="{ playing: speakingIndex === index }"
                          >
                            <i :class="speakingIndex === index ? 'el-icon-video-pause' : 'el-icon-video-play'"></i>
                            {{ speakingIndex === index ? '暂停' : '播放' }}
                          </el-button>
                          <span class="message-status" v-if="message.type === 'user'">
                            <i class="el-icon-check"></i>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </transition-group>
          
          <!-- 加载指示器 -->
          <div v-if="isLoading" class="loading-indicator">
            <div class="loading-dots">
              <span></span><span></span><span></span>
            </div>
            <span class="loading-text">AI面试官正在思考...</span>
          </div>
        </div>
        
        <!-- 统一输入区域 -->
        <div class="unified-input-area">
          <!-- 语音波形可视化 -->
          <div class="voice-visual" v-if="isRecording && inputMode === 'voice'">
            <div class="sound-wave">
              <span v-for="i in 12" :key="i" :style="{ animationDelay: (i * 0.1) + 's' }"></span>
            </div>
          </div>

          <!-- 文字输入模式 -->
          <div v-if="inputMode === 'text'" class="text-input-mode">
            <div class="input-wrapper">
              <el-input
                v-model="userInput"
                placeholder="输入您的回答，按Enter发送..."
                @keyup.enter="sendMessage"
                type="textarea"
                :rows="3"
                :disabled="isLoading"
                class="chat-input"
              ></el-input>
            </div>
            <div class="input-actions">
              <span class="input-hint">
                <i class="el-icon-info"></i>
                按Enter发送，Shift+Enter换行
              </span>
              <el-button 
                type="primary" 
                @click="sendMessage" 
                :disabled="!userInput.trim() || isLoading"
                class="send-btn"
              >
                <i v-if="isLoading" class="el-icon-loading"></i>
                <i v-else class="el-icon-s-promotion"></i>
                {{ isLoading ? '发送中...' : '发送' }}
              </el-button>
            </div>
          </div>

          <!-- 语音输入模式 -->
          <div v-if="inputMode === 'voice'" class="voice-input-mode">
            <div class="voice-input-card" :class="{ recording: isRecording }">
              <div v-if="!isRecording" class="voice-record-hint">
                <i class="el-icon-microphone"></i>
                <span>点击开始录音</span>
              </div>
              <div v-else class="voice-recording-indicator">
                <div class="sound-wave">
                  <span v-for="i in 8" :key="i" :style="{ animationDelay: (i * 0.1) + 's' }"></span>
                </div>
                <span>正在录音...</span>
              </div>
              
              <!-- 实时语音识别文字显示 -->
              <div v-if="isRecording || voiceTranscript" class="voice-transcript">
                <div class="transcript-label">
                  <i class="el-icon-edit-outline"></i>
                  <span>语音识别中...</span>
                </div>
                <div class="transcript-text">
                  {{ voiceTranscript || '正在识别您的语音...' }}
                </div>
              </div>
              
              <el-button
                :type="isRecording ? 'danger' : 'primary'"
                @click="toggleVoiceRecording"
                size="large"
                :disabled="isLoading"
                class="voice-record-btn"
              >
                <i :class="isRecording ? 'el-icon-video-pause' : 'el-icon-microphone'"></i>
                {{ isRecording ? '停止录音' : '开始录音' }}
              </el-button>
              
              <!-- 使用识别的文字 -->
              <div v-if="voiceTranscript && !isRecording" class="voice-actions">
                <el-button size="small" @click="useVoiceTranscript">
                  <i class="el-icon-check"></i>
                  使用此文字
                </el-button>
                <el-button size="small" @click="clearVoiceTranscript">
                  <i class="el-icon-close"></i>
                  清除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 数字人+摄像头+对话一体化模式 -->
      <div v-else class="avatar-camera-mode">
        <!-- 顶部：摄像头和数字人并排 -->
        <div class="top-panels">
          <div class="camera-panel">
            <FaceAnalysis
              ref="faceAnalysisRef"
              :interviewId="props.currentInterviewId"
              :analysisEnabled="true"
              @interviewStart="handleFaceAnalysisStart"
              @interviewEnd="handleFaceAnalysisEnd"
              @analysisResult="handleFaceAnalysisResult"
            />
          </div>
          <div class="avatar-panel">
            <AIAvatar
              :isAiResponding="isAiResponding"
              :aiSpeakingText="currentAiText"
              :selectedVoice="selectedVoice"
              @voice-change="handleVoiceChange"
            />
          </div>
        </div>
        <!-- 底部：对话区 -->
        <div class="bottom-chat-panel">
          <div class="chat-messages" ref="chatMessagesRef">
            <transition-group name="message-slide" tag="div" class="messages-wrapper">
              <div
                v-for="(message, index) in props.chatMessages"
                :key="index"
                :class="['message-item', message.type, { 'animate-in': true }]"
                :style="{ animationDelay: (index * 0.05) + 's' }"
              >
                <div v-if="message.type !== 'system'" class="message-avatar">
                  <div class="avatar-wrapper">
                    <img
                      v-if="message.type === 'ai'"
                      src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20wearing%20glasses%20and%20suits&image_size=square"
                      alt="AI面试官"
                      class="avatar-img"
                    >
                    <img
                      v-else
                      src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20avatar&image_size=square"
                      alt="用户"
                      class="avatar-img"
                    >
                  </div>
                </div>
                <div class="message-bubble">
                  <div class="message-text" :class="{ 'ai-message': message.type === 'ai', 'user-message': message.type === 'user' }">
                    {{ message.content }}
                  </div>
                  <div class="message-footer">
                    <span class="message-time">{{ message.time }}</span>
                  </div>
                </div>
              </div>
            </transition-group>
          </div>
          <div class="input-area">
            <div class="input-mode-switch">
              <button
                class="mode-btn"
                :class="{ active: inputMode === 'text' }"
                @click="setInputMode('text')"
              >
                <i class="el-icon-edit"></i>
                文字
              </button>
              <button
                class="mode-btn"
                :class="{ active: inputMode === 'voice' }"
                @click="setInputMode('voice')"
              >
                <i class="el-icon-microphone"></i>
                语音
              </button>
            </div>

            <div v-if="inputMode === 'text'" class="text-input-wrapper">
              <el-input
                v-model="userInput"
                placeholder="输入您的回答..."
                @keyup.enter="sendMessage"
                type="textarea"
                :rows="2"
                :disabled="isLoading"
                class="chat-input"
              ></el-input>
              <el-button
                type="primary"
                @click="sendMessage"
                :disabled="!userInput.trim() || isLoading"
                class="send-btn"
              >
                <i v-if="isLoading" class="el-icon-loading"></i>
                <i v-else class="el-icon-s-promotion"></i>
                发送
              </el-button>
            </div>

            <div v-else class="voice-input-wrapper">
              <div v-if="!isRecording" class="voice-record-hint">
                <i class="el-icon-microphone"></i>
                <span>点击开始录音</span>
              </div>
              <div v-else class="voice-recording-indicator">
                <div class="sound-wave">
                  <span v-for="i in 8" :key="i" :style="{ animationDelay: (i * 0.1) + 's' }"></span>
                </div>
                <span>正在录音...</span>
              </div>
              <el-button
                :type="isRecording ? 'danger' : 'primary'"
                @click="toggleVoiceRecording"
                size="large"
                :disabled="isLoading"
                class="voice-record-btn"
              >
                <i :class="isRecording ? 'el-icon-video-pause' : 'el-icon-microphone'"></i>
                {{ isRecording ? '停止录音' : '开始录音' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import AIAvatar from './AIAvatar.vue'
import FaceAnalysis from './FaceAnalysis.vue'

const emit = defineEmits(['back', 'addMessage', 'evaluationComplete', 'end'])

const props = defineProps({
  interviewType: String,
  job: String,
  chatMessages: Array,
  currentQuestionIndex: Number,
  totalQuestions: Number,
  currentInterviewId: Number,
  aiInterviewForm: Object
})

const mounted = ref(false)
const userInput = ref('')
const isRecording = ref(false)
const recognition = ref(null)
const voiceTranscript = ref('')
const interviewQuestions = ref([])
const isLoading = ref(false)
const speakingIndex = ref(null)
const chatMessagesRef = ref(null)
const faceAnalysisRef = ref(null)
const inputMode = ref('text')
const interviewMode = ref(props.interviewType === 'avatar' || props.interviewType === 'ai' ? 'avatar' : 'text')
const isAiResponding = ref(false)
const currentAiText = ref('')
const mediaRecorder = ref(null)
const audioChunks = ref([])
const audioStream = ref(null)
const recordingStartTime = ref(0)
const currentSpeechRecord = ref(null)

// 声音选择功能
const availableVoices = ref([])
const selectedVoice = ref('')
const showVoicePopover = ref(false)

// 切换声音选择弹窗
const toggleVoiceSelector = () => {
  showVoicePopover.value = !showVoicePopover.value
  if (showVoicePopover.value) {
    loadAvailableVoices()
  }
}

// 加载可用声音
const loadAvailableVoices = async () => {
  try {
    const response = await fetch('/api/avatar/voices')
    const data = await response.json()
    availableVoices.value = data.voices
    // 默认选择第一个声音
    if (availableVoices.value && !selectedVoice.value) {
      const voiceKeys = Object.keys(availableVoices.value)
      if (voiceKeys.length > 0) {
        selectedVoice.value = voiceKeys[0]
      }
    }
  } catch (error) {
    console.error('加载声音失败:', error)
  }
}

// 选择声音
const selectVoice = (voiceKey) => {
  selectedVoice.value = voiceKey
  ElMessage.success(`已选择: ${availableVoices.value[voiceKey].name}`)
}

// 处理来自AIAvatar的声音变化
const handleVoiceChange = (voiceName) => {
  selectedVoice.value = voiceName
}

// 设置输入模式
const setInputMode = (mode) => {
  inputMode.value = mode
}

// 设置面试模式
const setInterviewMode = (mode) => {
  interviewMode.value = mode
  
  // 根据面试模式自动设置输入模式
  if (mode === 'voice') {
    // 语音面试模式 → 自动使用语音输入
    inputMode.value = 'voice'
  } else {
    // 文字或数字人模式 → 自动使用文字输入
    inputMode.value = 'text'
  }
  
  // 如果正在录音，停止
  if (isRecording.value) {
    stopVoiceRecording()
  }
}

watch(inputMode, (newMode) => {
  if (newMode === 'voice') {
    currentSpeechRecord.value = null
    userInput.value = ''
  } else if (newMode === 'text' && isRecording.value) {
    stopVoiceRecording()
  }
})

watch(() => props.interviewType, (newType) => {
  if (newType === 'avatar' || newType === 'ai') {
    interviewMode.value = 'avatar'
  } else {
    interviewMode.value = 'text'
  }
  // 保障：每次切换面试类型时，确保使用文字输入模式
  inputMode.value = 'text'
})

const handleBack = () => {
  if (isRecording.value) {
    stopVoiceRecording()
  }
  emit('back')
}

const showEndInterviewConfirm = () => {
  if (confirm('确定要终止面试吗？终止后将无法继续当前面试。')) {
    endInterview()
  }
}

const endInterview = () => {
  if (isRecording.value) {
    stopVoiceRecording()
  }
  emit('end')
}

const handleFaceAnalysisStart = (interviewId) => {
  console.log('面部分析开始:', interviewId)
}

const handleFaceAnalysisEnd = (interviewId) => {
  console.log('面部分析结束:', interviewId)
}

const handleFaceAnalysisResult = (result) => {
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
  triggerAiSpeak
})

const speakText = (() => {
  let isSpeaking = false;
  let currentAudio = null;
  let currentText = '';
  let currentIndex = null;

  return async (text, index) => {
    if (isSpeaking && currentIndex === index) {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
      isSpeaking = false;
      currentText = '';
      currentIndex = null;
      speakingIndex.value = null;
      return;
    }

    if (isSpeaking) {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
      isSpeaking = false;
    }

    isSpeaking = true;
    currentText = text;
    currentIndex = index;
    speakingIndex.value = index;

    try {
      const response = await fetch('/api/avatar/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          voice_type: selectedVoice.value || 'Cherry'
        })
      });

      if (!response.ok) {
        throw new Error('TTS请求失败');
      }

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      currentAudio = new Audio(audioUrl);
      currentAudio.play();

      currentAudio.onended = () => {
        isSpeaking = false;
        currentAudio = null;
        currentText = '';
        currentIndex = null;
        speakingIndex.value = null;
        URL.revokeObjectURL(audioUrl);
      };

      currentAudio.onerror = () => {
        isSpeaking = false;
        currentAudio = null;
        currentText = '';
        currentIndex = null;
        speakingIndex.value = null;
        URL.revokeObjectURL(audioUrl);
      };
    } catch (error) {
      console.error('TTS播放失败:', error);
      isSpeaking = false;
      currentAudio = null;
      currentText = '';
      currentIndex = null;
      speakingIndex.value = null;
    }
  };
})();

const sendMessage = async () => {
  if (!userInput.value.trim()) return
  if (!props.currentInterviewId) {
    ElMessage.error('面试信息丢失，请重新开始面试')
    return
  }

  window.speechSynthesis.cancel()

  const userMessage = userInput.value
  
  emit('addMessage', {
    type: 'user',
    content: userMessage,
    time: new Date().toLocaleTimeString()
  })
  
  userInput.value = ''
  
  if (userMessage.includes('结束面试')) {
    evaluateInterview()
    return
  }
  
  isLoading.value = true
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

    // 如果有点评，先显示点评
    if (data.comment && data.comment.trim()) {
      emit('addMessage', {
        type: 'ai',
        content: data.comment,
        time: new Date().toLocaleTimeString(),
        isComment: true
      })
      
      // 如果有下一题，添加到问题列表
      if (data.followup && data.followup.trim()) {
        interviewQuestions.value.push(data.followup)
      }
    }
    
    // 显示下一题
    emit('addMessage', {
      type: 'ai',
      content: data.response,
      time: new Date().toLocaleTimeString()
    })
    
    if (!data.comment || !data.comment.trim()) {
      // 如果没有点评，才把下一题加入问题列表
      interviewQuestions.value.push(data.response)
    }
    
    nextTick(() => {
      scrollToBottom()
    })

    if (interviewMode.value !== 'avatar') {
      nextTick(() => {
        speakText(data.response, aiMessageIndex)
      })
    }
    
    if (data.answer_quality) {
      console.log('回答质量:', data.answer_quality)
    }
    
    // 如果面试结束，自动生成评估报告
    if (data.is_interview_over) {
      setTimeout(() => {
        evaluateInterview()
      }, 2000)
    } else if (data.response.includes('面试到此结束') || data.response.includes('面试结束')) {
      setTimeout(() => {
        evaluateInterview()
      }, 2000)
    }
    
    isLoading.value = false
    
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('获取AI回复失败，请稍后重试')
    
    emit('addMessage', {
      type: 'ai',
      content: '感谢你的回答。让我们继续下一个话题。',
      time: new Date().toLocaleTimeString()
    })
    
    isLoading.value = false
  }
}

const scrollToBottom = () => {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

const clearVoiceInput = () => {
  userInput.value = ''
  currentSpeechRecord.value = null
}

const evaluateInterview = async () => {
  if (!props.currentInterviewId) {
    ElMessage.error('面试信息丢失，请重新开始面试')
    return
  }
  
  const questions = interviewQuestions.value
  const answers = props.chatMessages.filter(msg => msg.type === 'user').map(msg => msg.content)
  
  if (answers.length === 0) {
    ElMessage.error('请先完成面试回答')
    return
  }
  
  try {
    const response = await fetch('/api/interview/evaluate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        interview_id: props.currentInterviewId,
        job_type: props.aiInterviewForm.jobType,
        questions: questions,
        answers: answers
      })
    })
    
    if (!response.ok) {
      throw new Error(`API调用失败: ${response.status}`)
    }
    
    const report = await response.json()
    emit('evaluationComplete', report)
  } catch (error) {
    console.error('评估失败:', error)
    ElMessage.error('评估失败，请稍后重试')
  }
}

const getProgressColor = (score) => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

const getToneLabel = (toneType) => {
  const toneLabels = {
    'confident': '自信',
    'calm': '沉稳',
    'nervous': '紧张',
    'anxious': '焦虑',
    'excited': '兴奋',
    'neutral': '平和'
  }
  return toneLabels[toneType] || toneType
}

const toggleVoiceRecording = async () => {
  if (isRecording.value) {
    await stopVoiceRecording()
  } else {
    await startVoiceRecording()
  }
}

const startVoiceRecording = async () => {
  try {
    // 初始化语音识别
    initSpeechRecognition()
    
    audioStream.value = await navigator.mediaDevices.getUserMedia({ audio: { sampleRate: 16000, channelCount: 1 } })
    const options = MediaRecorder.isTypeSupported('audio/wav') ? 'audio/wav' : 'audio/webm'
    mediaRecorder.value = new MediaRecorder(audioStream.value, { mimeType: options })
    audioChunks.value = []
    voiceTranscript.value = ''
    recordingStartTime.value = Date.now()

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }

    mediaRecorder.value.onstop = async () => {
      await handleRecordingComplete()
    }

    mediaRecorder.value.start()
    isRecording.value = true
    
    // 启动语音识别
    if (recognition.value) {
      recognition.value.start()
    }
  } catch (error) {
    console.error('开始录音失败:', error)
    ElMessage.error('无法访问麦克风，请检查权限设置')
  }
}

// 初始化语音识别
const initSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.warn('浏览器不支持语音识别')
    return
  }

  recognition.value = new SpeechRecognition()
  recognition.value.continuous = true
  recognition.value.interimResults = true
  recognition.value.lang = 'zh-CN'

  recognition.value.onresult = (event) => {
    let transcript = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript
    }
    voiceTranscript.value = transcript
  }

  recognition.value.onerror = (event) => {
    console.error('语音识别错误:', event.error)
    
    // 网络错误时给出友好提示，但不中断录音
    if (event.error === 'network') {
      ElMessage.info('本地Vosk模型将进行离线识别')
      voiceTranscript.value = ''
    }
  }

  recognition.value.onend = () => {
    if (isRecording.value && recognition.value) {
      // 如果还在录音，重新启动识别
      try {
        recognition.value.start()
      } catch (e) {
        console.error('重启语音识别失败:', e)
      }
    }
  }
}

// 使用语音识别的文字
const useVoiceTranscript = () => {
  if (voiceTranscript.value) {
    userInput.value = voiceTranscript.value
    inputMode.value = 'text'
    ElMessage.success('已使用语音识别文字，可直接发送或继续编辑')
  }
}

// 清除语音识别的文字
const clearVoiceTranscript = () => {
  voiceTranscript.value = ''
}

const stopVoiceRecording = async () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
  }
  if (recognition.value) {
    try {
      recognition.value.stop()
    } catch (e) {
      console.error('停止语音识别失败:', e)
    }
  }
  if (audioStream.value) {
    audioStream.value.getTracks().forEach(track => track.stop())
  }
  isRecording.value = false
}

const handleRecordingComplete = async () => {
  const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
  const duration = (Date.now() - recordingStartTime.value) / 1000

  const audioUrl = URL.createObjectURL(audioBlob)
  const audio = new Audio(audioUrl)
  audio.play()

  currentSpeechRecord.value = {
    audioBlob,
    duration,
    text: ''
  }

  userInput.value = ''

  await sendVoiceMessage()
}

const sendVoiceMessage = async () => {
  if (!currentSpeechRecord.value) return
  if (!props.currentInterviewId) {
    ElMessage.error('面试信息丢失，请重新开始面试')
    return
  }

  window.speechSynthesis.cancel()

  isLoading.value = true

  try {
    const formData = new FormData()
    formData.append('interview_id', props.currentInterviewId)
    formData.append('text', '')
    formData.append('duration', currentSpeechRecord.value.duration)
    formData.append('audio', currentSpeechRecord.value.audioBlob, 'recording.webm')

    const uploadResponse = await fetch('/api/speech/upload', {
      method: 'POST',
      body: formData
    })

    const uploadResult = await uploadResponse.json()

    if (!uploadResult.success) {
      throw new Error(uploadResult.error || '语音上传失败')
    }

    const audioUrl = `/api/speech/record/${uploadResult.speech_record_id}`
    const recognizedText = uploadResult.text

    const userMessage = {
      type: 'user',
      content: recognizedText,
      time: new Date().toLocaleTimeString(),
      audioUrl: audioUrl,
      speechAnalysis: {
        ...uploadResult.speech_analysis,
        speech_rate_score: uploadResult.metrics.speech_rate_score,
        confidence_score: uploadResult.metrics.confidence_score
      }
    }

    emit('addMessage', userMessage)

    const messageText = recognizedText
    currentSpeechRecord.value = null

    if (messageText.includes('结束面试')) {
      evaluateInterview()
      return
    }

    isAiResponding.value = true

    const response = await fetch('/api/interview/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: messageText,
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
    })

    interviewQuestions.value.push(data.response)

    nextTick(() => {
      scrollToBottom()
    })

    if (interviewMode.value !== 'avatar') {
      nextTick(() => {
        speakText(data.response, aiMessageIndex)
      })
    }

    if (data.response.includes('面试到此结束') || data.response.includes('面试结束')) {
      setTimeout(() => {
        evaluateInterview()
      }, 1000)
    }

    isLoading.value = false

  } catch (error) {
    console.error('发送语音消息失败:', error)
    ElMessage.error('发送失败，请稍后重试')
    isLoading.value = false
  }
}

setTimeout(() => {
  mounted.value = true
  loadAvailableVoices()
  
  // 点击外部关闭声音选择弹窗
  document.addEventListener('click', handleClickOutside)
}, 100)

const handleClickOutside = (event) => {
  if (showVoicePopover.value) {
    const voiceSelector = document.querySelector('.voice-selector')
    if (voiceSelector && !voiceSelector.contains(event.target)) {
      showVoicePopover.value = false
    }
  }
}

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.ai-interview-wrapper {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 99999;
}

.ai-interview-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  z-index: 0;
}

.main-content {
  width: 100%;
  height: auto;
  min-height: calc(100vh - 60px);
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 8px;
  box-sizing: border-box;
}

.animate-in {
  animation: slideUp 0.5s ease-out forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 8px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.back-btn {
  width: auto;
  height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-3px);
}

.back-text {
  font-size: 14px;
  font-weight: 500;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.chat-title {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.chat-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 4px;
}

.subtitle-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.subtitle-divider {
  margin: 0 8px;
  color: rgba(255, 255, 255, 0.5);
}

.subtitle-text {
  color: rgba(255, 255, 255, 0.8);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 终止面试按钮 */
.end-interview-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
}

.end-interview-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(245, 87, 108, 0.5);
}

.end-interview-btn:active {
  transform: translateY(0);
}

/* 模式切换按钮 */
.mode-switch {
  display: flex;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 4px;
  gap: 4px;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.mode-btn.active {
  background: white;
  color: #667eea;
  font-weight: 500;
}

.mode-btn i {
  font-size: 14px;
}

/* 进度环 */
.progress-ring-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.progress-ring {
  position: relative;
  width: 60px;
  height: 60px;
}

.progress-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-ring .ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.2);
  stroke-width: 6;
}

.progress-ring .ring-progress {
  fill: none;
  stroke: white;
  stroke-width: 6;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.progress-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.progress-current {
  font-size: 18px;
  font-weight: bold;
  color: white;
}

.progress-separator {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.progress-total {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.progress-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

/* 状态栏 */
.status-bar {
  display: flex;
  gap: 20px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  margin-bottom: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #a0a0c0;
  font-weight: 500;
}

.status-item.mode-indicator {
  margin-left: auto;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: white;
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.status-item.mode-indicator i {
  font-size: 14px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
}

.status-dot.recording {
  background: #67C23A;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 聊天容器 */
.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  gap: 16px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  min-height: 0;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 消息动画 */
.message-slide-enter-active {
  animation: messageIn 0.4s ease-out;
}

@keyframes messageIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 14px;
  animation: fadeIn 0.3s ease-out forwards;
  opacity: 0;
}

@keyframes fadeIn {
  to { opacity: 1; }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-item.user .message-bubble {
  margin-left: 0;
  margin-right: 24px;
}

.message-item.ai {
  flex-direction: row;
}

.avatar-wrapper {
  position: relative;
}

.avatar-img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.avatar-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409EFF, #66B1FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
}

/* 消息气泡 */
.message-bubble {
  max-width: 75%;
}

.message-item.user .message-bubble {
  margin-left: auto;
}

.message-content {
  width: 100%;
  min-width: 0;
}

.message-text {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
  width: 100%;
  display: block;
}

.ai-message {
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-top-left-radius: 4px;
  color: #ffffff;
}

.user-message {
  background: rgba(64, 158, 255, 0.25);
  border: 1px solid rgba(64, 158, 255, 0.5);
  color: white;
  border-top-right-radius: 4px;
  text-align: right;
}

.msg.user {
  text-align: right !important;
  align-self: flex-end !important;
  margin-left: auto !important;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  padding: 0 4px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: auto;
  position: relative;
  z-index: 50;
}

.message-time {
  font-size: 11px;
  color: #a0a0c0;
}

.message-status {
  color: #67C23A;
  font-size: 12px;
}

/* 播放按钮 */
.play-voice-btn {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  background: rgba(64, 158, 255, 0.1);
  border: none;
  color: #409EFF;
  transition: all 0.3s ease;
  pointer-events: auto !important;
  position: relative;
  z-index: 100;
  cursor: pointer;
}

.play-voice-btn:hover {
  background: rgba(64, 158, 255, 0.2);
  transform: scale(1.05);
}

.play-voice-btn.playing {
  background: #409EFF;
  color: white;
}

/* 加载指示器 */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
}

.loading-dots {
  display: flex;
  gap: 6px;
}

.loading-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #409EFF;
  animation: bounce 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(1) { animation-delay: 0s; }
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.loading-text {
  font-size: 13px;
  color: #a0a0c0;
}

/* 统一输入区域 */
.unified-input-area {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

/* 语音波形 */
.voice-visual {
  display: flex;
  justify-content: center;
  padding: 16px 0;
  margin-bottom: 16px;
}

.sound-wave {
  display: flex;
  gap: 4px;
  align-items: center;
}

.sound-wave span {
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #F56C6C, #409EFF);
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { height: 20px; }
  50% { height: 50px; }
}

/* 文字输入模式 */
.text-input-mode .input-wrapper {
  margin-bottom: 12px;
}

.text-input-mode .input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-hint {
  font-size: 12px;
  color: #a0a0c0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.chat-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 14px;
  line-height: 1.6;
  border: 2px solid rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  transition: all 0.3s ease;
}

.chat-input :deep(.el-textarea__inner:focus) {
  border-color: #409EFF;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.chat-input :deep(.el-textarea__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.send-btn {
  padding: 10px 24px;
  border-radius: 20px;
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* 语音输入模式 */
.voice-input-mode {
  display: flex;
  justify-content: center;
}

.voice-input-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  width: 100%;
  max-width: 500px;
}

.voice-input-card.recording {
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 0 rgba(245, 108, 108, 0); }
  50% { box-shadow: 0 0 30px rgba(245, 108, 108, 0.3); }
}

.voice-input-hint {
  font-size: 14px;
  color: #a0a0c0;
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.recording-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #F56C6C;
  animation: pulse 1s ease-in-out infinite;
}

.voice-input-btn {
  width: 200px;
  height: 56px;
  font-size: 16px;
  border-radius: 28px;
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  border: none;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.voice-input-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.5);
}

/* 语音识别文字显示 */
.voice-transcript {
  width: 100%;
  margin: 16px 0;
  padding: 16px;
  background: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.transcript-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #409EFF;
  margin-bottom: 8px;
  font-weight: 500;
}

.transcript-label i {
  animation: pulse 1s ease-in-out infinite;
}

.transcript-text {
  font-size: 14px;
  color: #ffffff;
  line-height: 1.6;
  min-height: 40px;
  word-break: break-word;
}

/* 语音识别操作按钮 */
.voice-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 8px;
}

.voice-actions .el-button {
  border-radius: 20px;
  font-weight: 500;
}

.voice-input-preview {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 16px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 10px;
}

.preview-content {
  font-size: 14px;
  color: #a0a0c0;
  line-height: 1.6;
  margin-bottom: 12px;
  max-height: 100px;
  overflow-y: auto;
}

.preview-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.preview-send-btn {
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  border: none;
}

/* 系统消息 */
.system-message {
  text-align: center;
  padding: 20px;
}

.evaluate-btn {
  padding: 12px 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
  font-weight: 500;
}

.evaluate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(103, 194, 58, 0.4);
}

/* 打字指示器 */
.typing-indicator {
  display: inline-flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  animation: typingBounce 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
    border-radius: 12px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .chat-title {
    font-size: 16px;
  }

  .chat-messages {
    padding: 14px;
    border-radius: 12px;
  }

  .message-item {
    gap: 10px;
  }

  .avatar-img {
    width: 40px;
    height: 40px;
  }

  .message-text {
    padding: 12px 14px;
    font-size: 13px;
  }

  .message-bubble {
    max-width: 80%;
  }

  .mode-switch {
    order: -1;
  }

  .mode-btn {
    padding: 6px 12px;
    font-size: 12px;
  }

  .status-bar {
    flex-wrap: wrap;
    gap: 10px;
  }

  .status-item.mode-indicator {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }
}


/* 数字人模式布局 - 顶部固定，聊天区滚动 */
.avatar-camera-mode {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: calc(100vh - 130px);
  gap: 8px;
}

/* 顶部面板容器 - 摄像头和数字人并排 */
.top-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
  height: 280px;
  flex-shrink: 0;
  background: transparent;
}

/* 底部对话区 - 自适应填满剩余空间 */
.bottom-chat-panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 300px;
  width: 100%;
  max-width: none;
}

.bottom-chat-panel .chat-messages {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  background: transparent;
}

.bottom-chat-panel .chat-messages .messages-wrapper {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.bottom-chat-panel .input-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.03);
  flex-shrink: 0;
  height: 140px;
  z-index: 99999;
}

.bottom-chat-panel .chat-input {
  flex: 1;
  min-width: 0;
}

.bottom-chat-panel .send-btn {
  flex-shrink: 0;
  align-self: flex-end;
  padding: 10px 24px;
}

/* 一体化布局样式 - 核心：对话区占绝对核心位置 */
.unified-interview-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  width: 100%;
  height: 100%;
  padding: 16px;
  background: transparent;
  border-radius: 16px;
  overflow: hidden;
  max-width: none;
  box-sizing: border-box;
  align-items: stretch;
}

/* 左侧悬浮区域 - 摄像头和AI形象 */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

/* 摄像头小窗 - 紧凑悬浮设计 */
.camera-panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  display: flex;
  flex-direction: column;
  min-width: 0;
  height: 100%;
}

.camera-panel :deep(.camera-section) {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 12px;
  gap: 10px;
}

.camera-panel :deep(.camera-container) {
  width: 100%;
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(102, 126, 234, 0.3);
  min-height: 0;
}

.camera-panel :deep(.analysis-panel) {
  display: none;
}

.camera-panel :deep(.camera-controls) {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
}

/* AI形象小窗 - 紧凑悬浮设计 */
.avatar-panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  overflow: visible;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
  min-height: 0;
}

.avatar-panel :deep(.ai-avatar-container) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.avatar-panel :deep(.avatar-header) {
  flex-shrink: 0;
}

.avatar-panel :deep(.avatar-main) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* 右侧对话区 - 核心区域，占据70%以上空间，铺满全部可用宽度 */
.chat-panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  overflow: visible;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  min-height: 0;
  width: 100%;
  max-width: none;
  height: 100%;
}

.chat-panel .chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  min-height: 0;
  background: transparent;
}

.chat-panel .chat-messages .messages-wrapper {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.chat-panel .input-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.03);
  flex-shrink: 0;
  height: auto;
  min-height: 160px;
}

.input-area .input-mode-switch {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.input-area .input-mode-switch .mode-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  font-size: 12px;
  color: #a0a0c0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.input-area .input-mode-switch .mode-btn:hover {
  border-color: #409EFF;
  color: #409EFF;
  background: rgba(64, 158, 255, 0.1);
}

.input-area .input-mode-switch .mode-btn.active {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.text-input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-panel .chat-input {
  flex: 1;
  min-width: 0;
}

.chat-panel .send-btn {
  flex-shrink: 0;
  align-self: flex-end;
  padding: 10px 24px;
}

.voice-input-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.voice-record-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #909399;
}

.voice-record-hint i {
  font-size: 24px;
  color: #409EFF;
}

.voice-recording-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.voice-recording-indicator .sound-wave {
  display: flex;
  gap: 4px;
  align-items: center;
}

.voice-recording-indicator .sound-wave span {
  width: 6px;
  height: 24px;
  background: linear-gradient(180deg, #F56C6C, #409EFF);
  border-radius: 3px;
  animation: wave 0.8s ease-in-out infinite;
}

.voice-recording-indicator .sound-wave span:nth-child(1) { animation-delay: 0s; }
.voice-recording-indicator .sound-wave span:nth-child(2) { animation-delay: 0.1s; }
.voice-recording-indicator .sound-wave span:nth-child(3) { animation-delay: 0.2s; }
.voice-recording-indicator .sound-wave span:nth-child(4) { animation-delay: 0.3s; }
.voice-recording-indicator .sound-wave span:nth-child(5) { animation-delay: 0.4s; }
.voice-recording-indicator .sound-wave span:nth-child(6) { animation-delay: 0.5s; }
.voice-recording-indicator .sound-wave span:nth-child(7) { animation-delay: 0.6s; }
.voice-recording-indicator .sound-wave span:nth-child(8) { animation-delay: 0.7s; }

.voice-recording-indicator span {
  font-size: 14px;
  color: #F56C6C;
}

.voice-record-btn {
  width: 180px;
  height: 52px;
  font-size: 15px;
  border-radius: 26px;
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
}

.voice-preview {
  width: 100%;
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
}

.voice-preview .preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 10px;
}

.voice-preview .preview-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
  max-height: 80px;
  overflow-y: auto;
}

.voice-preview .preview-textarea {
  margin-bottom: 12px;
}

.voice-preview .preview-textarea :deep(.el-textarea__inner) {
  border-radius: 8px;
  font-size: 14px;
}

.voice-preview .preview-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.audio-player {
  margin-bottom: 12px;
}

.audio-element {
  width: 100%;
  max-width: 300px;
}

.speech-analysis {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.speech-analysis .analysis-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.speech-analysis .analysis-header i {
  color: #409EFF;
}

.speech-analysis .analysis-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.speech-analysis .analysis-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.speech-analysis .analysis-item .analysis-label {
  font-size: 12px;
  color: #909399;
  min-width: 50px;
}

.speech-analysis .analysis-item .analysis-value {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.speech-analysis .analysis-item .analysis-value .analysis-text {
  font-size: 12px;
  color: #606266;
  min-width: 60px;
}

.speech-analysis .analysis-item .analysis-tag {
  padding: 4px 12px;
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  color: white;
  border-radius: 12px;
  font-size: 12px;
}

.speech-analysis .analysis-overall {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

.speech-analysis .analysis-overall i {
  color: #E6A23C;
  margin-top: 2px;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .unified-interview-layout {
    grid-template-columns: 240px 1fr;
    gap: 16px;
    padding: 16px;
  }
}

@media (max-width: 900px) {
  .unified-interview-layout {
    grid-template-columns: 200px 1fr;
    gap: 12px;
    padding: 12px;
  }

  .left-panel {
    gap: 12px;
  }

  .camera-panel {
    height: 180px;
  }
}

@media (max-width: 768px) {
  .unified-interview-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    height: auto;
    min-height: calc(100vh - 180px);
  }

  .left-panel {
    flex-direction: row;
    height: 200px;
  }

  .camera-panel,
  .avatar-panel {
    flex: 1;
    height: auto;
  }

  .chat-panel {
    min-height: 400px;
  }
}

/* 声音选择按钮 - 使用更高权重选择器 */
.header-right .voice-selector {
  position: relative;
  display: flex !important;
  align-items: center !important;
  z-index: 9999 !important;
  flex-shrink: 0 !important;
}

.voice-btn-native {
  width: auto;
  height: 36px;
  padding: 0 16px !important;
  background: rgba(255, 255, 255, 0.95) !important;
  border: 2px solid rgba(102, 126, 234, 0.8) !important;
  transition: all 0.3s ease;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px;
  border-radius: 18px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
  cursor: pointer;
}

.voice-btn-native:hover {
  background: rgba(255, 255, 255, 1) !important;
  border-color: rgba(102, 126, 234, 1) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

.voice-btn-native i {
  font-size: 16px;
  color: rgba(102, 126, 234, 0.9) !important;
}

.voice-btn-native span {
  font-size: 13px;
  font-weight: 600;
  color: rgba(102, 126, 234, 0.9) !important;
  white-space: nowrap;
}

/* 声音选择弹窗 */
.voice-popover-content {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  padding: 16px;
  min-width: 280px;
  max-width: 320px;
  z-index: 10000;
}

.voice-popover-content h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.loading-voices {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
  padding: 8px 0;
}

.voice-list {
  max-height: 300px;
  overflow-y: auto;
}

.voice-item {
  padding: 10px 14px;
  margin-bottom: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  background: #f5f7fa;
  border: 1px solid transparent;
}

.voice-item:hover {
  background: #ecf5ff;
  border-color: rgba(102, 126, 234, 0.3);
}

.voice-item.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-color: rgba(102, 126, 234, 0.5);
}

.voice-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.voice-desc {
  font-size: 12px;
  color: #909399;
}
</style>
