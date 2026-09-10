<template>
  <div class="avatar-wrapper">
    <div v-if="mode === 'css'" class="css-avatar">
      <div class="interviewer">
        <div class="character" :class="{ talking: isTalking }" :style="{ transform: isNodding ? 'translateY(-5px)' : 'translateY(0)' }">
          <div class="hair" :class="gender"></div>
          <div class="head">
            <div class="eye left" :class="{ blink: isBlinking }"></div>
            <div class="eye right" :class="{ blink: isBlinking }"></div>
            <div class="mouth" :style="{ height: isTalking ? '14px' : '2px' }"></div>
            <div class="blush left"></div>
            <div class="blush right"></div>
          </div>
          <div class="body">
            <div class="shirt"></div>
            <div class="suit"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="mode === 'live2d'" class="live2d-container">
      <iframe
        ref="live2dFrame"
        src="/live2d-page.html"
        class="live2d-iframe"
        frameborder="0"
        allow="autoplay"
      ></iframe>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>Live2D加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'live2d',
    validator: (v) => ['css', 'live2d'].includes(v)
  },
  gender: {
    type: String,
    default: 'female'
  },
  speaking: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['loaded', 'error'])

const isTalking = ref(false)
const isBlinking = ref(false)
const isNodding = ref(false)
const loading = ref(true)
const live2dFrame = ref(null)

onMounted(() => {
  window.addEventListener('message', handleMessage)
  if (props.mode === 'css') {
    startCSSBlink()
  }
})

onUnmounted(() => {
  window.removeEventListener('message', handleMessage)
})

function handleMessage(event) {
  const data = event.data
  if (!data || !data.type) return

  switch (data.type) {
    case 'loaded':
    case 'ready':
      loading.value = false
      emit('loaded')
      break
    case 'error':
      emit('error', data)
      loading.value = false
      break
  }
}

function startCSSBlink() {
  setInterval(() => {
    isBlinking.value = true
    setTimeout(() => isBlinking.value = false, 150)
  }, 3000)
}

watch(() => props.speaking, (newVal) => {
  if (props.mode === 'css') {
    isTalking.value = newVal
  } else {
    if (live2dFrame.value?.contentWindow) {
      live2dFrame.value.contentWindow.postMessage({
        type: newVal ? 'speak' : 'stopSpeak'
      }, '*')
    }
  }
})

const speak = (audioUrl) => {
  if (props.mode === 'css') {
    if (!audioUrl) return
    isTalking.value = true
    const audio = new Audio(audioUrl)
    audio.play().catch(() => isTalking.value = false)

    const nod = setInterval(() => {
      isNodding.value = true
      setTimeout(() => isNodding.value = false, 120)
    }, 300)

    audio.onended = () => {
      isTalking.value = false
      clearInterval(nod)
    }
  } else {
    if (live2dFrame.value?.contentWindow) {
      live2dFrame.value.contentWindow.postMessage({ type: 'speak' }, '*')
    }
    if (audioUrl) {
      const audio = new Audio(audioUrl)
      audio.play()
      audio.onended = () => {
        if (live2dFrame.value?.contentWindow) {
          live2dFrame.value.contentWindow.postMessage({ type: 'stopSpeak' }, '*')
        }
      }
    }
  }
}

const stopSpeaking = () => {
  if (props.mode === 'css') {
    isTalking.value = false
  } else {
    if (live2dFrame.value?.contentWindow) {
      live2dFrame.value.contentWindow.postMessage({ type: 'stopSpeak' }, '*')
    }
  }
}

const setExpression = (expression) => {
  if (live2dFrame.value?.contentWindow) {
    live2dFrame.value.contentWindow.postMessage({
      type: 'expression',
      expression: expression
    }, '*')
  }
}

const triggerMotion = (motion) => {
  if (live2dFrame.value?.contentWindow) {
    live2dFrame.value.contentWindow.postMessage({
      type: 'motion',
      motion: motion
    }, '*')
  }
}

defineExpose({
  speak,
  stopSpeaking,
  setExpression,
  triggerMotion
})
</script>

<style scoped>
.avatar-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.css-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.interviewer {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.character {
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.12s ease;
}

.hair {
  position: relative;
  margin-bottom: -10px;
  z-index: 1;
  border-radius: 70px 70px 0 0;
}
.hair.female {
  width: 140px;
  height: 70px;
  background: #2a2a2a;
}
.hair.male {
  width: 130px;
  height: 60px;
  background: #1a1a1a;
}

.head {
  width: 120px;
  height: 120px;
  background: #f6e0d1;
  border-radius: 50%;
  border: 3px solid #2c3e50;
  position: relative;
  z-index: 2;
}

.eye {
  position: absolute;
  top: 42px;
  width: 13px;
  height: 13px;
  background: #222;
  border-radius: 50%;
  transition: all 0.15s;
}
.eye.left { left: 32px; }
.eye.right { right: 32px; }
.eye.blink { height: 2px; }

.mouth {
  position: absolute;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  background: #b53a3a;
  border-radius: 0 0 20px 20px;
  transition: height 0.1s;
}

.blush {
  position: absolute;
  top: 62px;
  width: 18px;
  height: 8px;
  background: rgba(255, 173, 183, 0.3);
  border-radius: 50%;
}
.blush.left { left: 20px; }
.blush.right { right: 20px; }

.body {
  width: 105px;
  height: 165px;
  position: relative;
}
.suit {
  width: 105px;
  height: 165px;
  background: #2c3e50;
  border: 3px solid #1a2530;
  border-radius: 10px 10px 0 0;
}
.shirt {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 48px;
  height: 22px;
  background: white;
  border-bottom: 2px solid #222;
  border-radius: 0 0 6px 6px;
}

.live2d-container {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.live2d-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.95);
  z-index: 10;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  margin-top: 16px;
  color: white;
  font-size: 14px;
}
</style>
