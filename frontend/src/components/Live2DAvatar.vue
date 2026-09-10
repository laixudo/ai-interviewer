<template>
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
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  gender: {
    type: String,
    default: 'female'
  }
})

const isTalking = ref(false)
const isBlinking = ref(false)
const isNodding = ref(false)

let blinkInterval = null
let nodInterval = null

onMounted(() => {
  startBlinkAnimation()
})

function startBlinkAnimation() {
  blinkInterval = setInterval(() => {
    isBlinking.value = true
    setTimeout(() => {
      isBlinking.value = false
    }, 150)
  }, 3000)
}

const speak = (audioUrl) => {
  isTalking.value = true

  if (audioUrl) {
    const audio = new Audio(audioUrl)
    audio.play().catch(() => {})
    audio.onended = () => {
      isTalking.value = false
    }
  }

  nodInterval = setInterval(() => {
    isNodding.value = true
    setTimeout(() => {
      isNodding.value = false
    }, 120)
  }, 300)
}

const stopSpeaking = () => {
  isTalking.value = false
  if (nodInterval) {
    clearInterval(nodInterval)
    nodInterval = null
  }
}

const changeModel = (g) => {
  console.log('切换面试官:', g)
}

defineExpose({
  speak,
  stopSpeaking,
  changeModel
})

// 原先两个 setInterval 都没有卸载清理，onUnmounted 钩子也不存在
onUnmounted(() => {
  if (blinkInterval) { clearInterval(blinkInterval); blinkInterval = null }
  if (nodInterval) { clearInterval(nodInterval); nodInterval = null }
})

</script>

<style scoped>
.interviewer {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
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
</style>
