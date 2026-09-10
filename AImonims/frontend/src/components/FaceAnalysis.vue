<template>
  <div class="camera-section">
    <div class="camera-container">
      <video
        ref="videoRef"
        autoplay
        playsinline
        muted
        class="camera-video"
        :class="{ 'recording': isInterviewing }"
      ></video>
      <canvas ref="canvasRef" class="face-canvas"></canvas>
      <div class="analysis-status" v-if="isInterviewing && analysisEnabled">
        <span class="status-dot"></span>
        <span>正在进行面部分析...</span>
      </div>
      <div class="camera-controls">
        <el-button
          v-if="!isInterviewing"
          type="primary"
          size="large"
          @click="startInterview"
          class="camera-btn"
        >
          <i class="el-icon-video-camera"></i>
          开启摄像头
        </el-button>
        <el-button
          v-else
          type="danger"
          size="large"
          @click="stopInterview"
          class="camera-btn"
        >
          <i class="el-icon-close"></i>
          关闭摄像头
        </el-button>
      </div>
    </div>

    <div class="analysis-panel" v-if="lastAnalysis">
      <h4 class="panel-title">实时面部分析</h4>
      <div class="analysis-grid">
        <div class="analysis-item">
          <span class="analysis-label">情绪状态</span>
          <span class="analysis-value emotion">{{ lastAnalysis.emotion || '分析中' }}</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">自信度</span>
          <span class="analysis-value confidence">{{ lastAnalysis.confidence || 0 }}分</span>
        </div>
        <div class="analysis-item">
          <span class="analysis-label">专注状态</span>
          <span class="analysis-value focus">{{ lastAnalysis.focus || '分析中' }}</span>
        </div>
      </div>
      <div class="analysis-suggestion" v-if="lastAnalysis.suggestion">
        <i class="el-icon-warning"></i>
        <span>{{ lastAnalysis.suggestion }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineExpose } from 'vue'

const emit = defineEmits(['analysisResult', 'interviewStart', 'interviewEnd'])

const props = defineProps({
  interviewId: {
    type: Number,
    default: null
  },
  analysisEnabled: {
    type: Boolean,
    default: true
  }
})

const videoRef = ref(null)
const canvasRef = ref(null)
const isInterviewing = ref(false)
const lastAnalysis = ref(null)
const cameraError = ref(null)

let cameraStream = null
let analysisTimer = null
let interviewSessionId = null

const initCamera = async () => {
  try {
    // 先停止任何现有的摄像头流
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop())
      cameraStream = null
    }
    
    const constraints = {
      video: {
        width: { ideal: 1280, max: 1920 },
        height: { ideal: 720, max: 1080 },
        facingMode: 'user'
      },
      audio: false
    }
    
    cameraStream = await navigator.mediaDevices.getUserMedia(constraints)

    if (videoRef.value) {
      videoRef.value.srcObject = cameraStream
      await videoRef.value.play()
    }
  } catch (err) {
    console.error('摄像头初始化失败:', err)
    cameraError.value = err.message
    
    if (err.name === 'NotAllowedError') {
      alert('请允许访问摄像头权限')
    } else if (err.name === 'NotFoundError') {
      alert('未找到摄像头设备，请检查摄像头连接')
    } else if (err.name === 'NotReadableError') {
      alert('摄像头被其他程序占用，请关闭其他使用摄像头的应用（如微信、钉钉、QQ等）后刷新页面重试')
    } else {
      alert(`摄像头初始化失败: ${err.message}`)
    }
  }
}

const startInterview = () => {
  if (!props.interviewId) {
    console.warn('没有面试ID，无法启动面部分析')
    return
  }
  
  isInterviewing.value = true
  interviewSessionId = props.interviewId
  
  if (props.analysisEnabled) {
    startAnalysisLoop()
  }
  
  emit('interviewStart', interviewSessionId)
}

const stopInterview = () => {
  isInterviewing.value = false
  clearInterval(analysisTimer)
  lastAnalysis.value = null
  
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop())
    cameraStream = null
  }
  
  emit('interviewEnd', interviewSessionId)
}

const startAnalysisLoop = () => {
  analysisTimer = setInterval(async () => {
    if (!isInterviewing.value) return
    
    const frame = captureFrame()
    if (!frame) return
    
    const result = await analyzeFaceWithDoubao(frame)
    if (result) {
      lastAnalysis.value = result
      await saveAnalysisResult(interviewSessionId, result)
      emit('analysisResult', result)
    }
  }, 3000)
}

const captureFrame = () => {
  const video = videoRef.value
  if (!video || video.videoWidth === 0 || video.videoHeight === 0) {
    return null
  }
  
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
  
  return canvas.toDataURL('image/jpeg', 0.8).split(',')[1]
}

const analyzeFaceWithDoubao = async (base64Image) => {
  try {
    const response = await fetch('/api/doubao/face-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image: base64Image,
        prompt: `你是专业的面试教练，根据这张求职者的实时面部画面，分析以下维度：
        1. 情绪状态（紧张/放松/焦虑/自信/平静等）
        2. 自信度评分（0-100分）
        3. 面试状态（专注/走神/疲惫/活跃等）
        4. 简短改进建议（1-2句话）

        请以JSON格式返回，字段为：emotion, confidence, focus, suggestion`
      })
    })
    
    if (!response.ok) {
      throw new Error('面部分析API调用失败')
    }
    
    return await response.json()
  } catch (err) {
    console.error('面部分析失败:', err)
    return null
  }
}

const saveAnalysisResult = async (sessionId, result) => {
  if (!result || !sessionId) return
  
  try {
    await fetch('/api/interview/save-face-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        interview_id: sessionId,
        ...result,
        timestamp: new Date().toISOString()
      })
    })
  } catch (err) {
    console.error('保存分析结果失败:', err)
  }
}

onMounted(() => {
  initCamera()
})

onUnmounted(() => {
  stopInterview()
})

defineExpose({
  startInterview,
  stopInterview,
  isInterviewing
})
</script>

<style scoped>
.camera-section {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.camera-container {
  position: relative;
  width: 100%;
  height: 280px;
  border-radius: 12px;
  overflow: hidden;
  background: #1a1a1a;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.camera-video.recording {
  border: 3px solid #409eff;
  box-shadow: 0 0 20px rgba(64, 158, 255, 0.5);
}

.face-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.analysis-status {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 20px;
  color: white;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #67C23A;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.camera-controls {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
}

.camera-btn {
  padding: 12px 28px;
  border-radius: 24px;
  font-size: 15px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.interviewer-info {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.interviewer-info .avatar {
  margin-bottom: 12px;
}

.interviewer-info .avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.interviewer-info h3 {
  margin: 0 0 6px 0;
  font-size: 18px;
  color: #303133;
}

.interviewer-info p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.analysis-panel {
  width: 100%;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.panel-title {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.analysis-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.analysis-label {
  font-size: 12px;
  color: #a0a0c0;
}

.analysis-value {
  font-size: 14px;
  font-weight: 600;
}

.analysis-value.emotion {
  color: #E6A23C;
}

.analysis-value.confidence {
  color: #409EFF;
}

.analysis-value.focus {
  color: #67C23A;
}

.analysis-suggestion {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: rgba(230, 162, 60, 0.1);
  border: 1px solid rgba(230, 162, 60, 0.3);
  border-radius: 8px;
  font-size: 13px;
  color: #E6A23C;
  line-height: 1.5;
}

.analysis-suggestion i {
  flex-shrink: 0;
  margin-top: 2px;
}
</style>
