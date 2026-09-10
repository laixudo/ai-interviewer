<template>
  <div class="login-container">
    <div class="left-panel">
      <div class="logo-section">
        <div class="logo-icon">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="4" width="56" height="56" rx="12" fill="url(#gradient1)"/>
            <path d="M32 16L32 48" stroke="white" stroke-width="4" stroke-linecap="round"/>
            <path d="M20 24L32 16L44 24" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="32" cy="40" r="6" fill="white"/>
            <defs>
              <linearGradient id="gradient1" x1="4" y1="4" x2="60" y2="60" gradientUnits="userSpaceOnUse">
                <stop stop-color="#667eea"/>
                <stop offset="1" stop-color="#764ba2"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span class="logo-text">Offer制造机</span>
      </div>

      <div class="center-content">
        <div class="characters-container">
          <div class="character-wrapper character-purple-wrapper">
            <div 
              class="character character-purple" 
              :style="purpleStyle"
              :class="{ 'peeking': isPurplePeeking }"
            >
              <div class="character-body"></div>
              <div class="character-eyes">
                <div class="eye" :class="{ 'blinking': purpleBlinking }">
                  <div class="pupil" :style="getPupilStyle('purple', 0)"></div>
                </div>
                <div class="eye" :class="{ 'blinking': purpleBlinking }">
                  <div class="pupil" :style="getPupilStyle('purple', 1)"></div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="character character-orange" :style="orangeStyle">
            <div class="character-body"></div>
            <div class="character-eyes">
              <div class="eye"><div class="pupil" :style="getPupilStyle('orange', 0)"></div></div>
              <div class="eye"><div class="pupil" :style="getPupilStyle('orange', 1)"></div></div>
            </div>
          </div>
          
          <div class="character character-black" :style="blackStyle">
            <div class="character-body"></div>
            <div class="character-eyes">
              <div class="eye" :class="{ 'blinking': blackBlinking }">
                <div class="pupil" :style="getPupilStyle('black', 0)"></div>
              </div>
              <div class="eye" :class="{ 'blinking': blackBlinking }">
                <div class="pupil" :style="getPupilStyle('black', 1)"></div>
              </div>
            </div>
          </div>
          
          <div class="character character-yellow" :style="yellowStyle">
            <div class="character-body"></div>
            <div class="character-eyes">
              <div class="eye"><div class="pupil" :style="getPupilStyle('yellow', 0)"></div></div>
              <div class="eye"><div class="pupil" :style="getPupilStyle('yellow', 1)"></div></div>
            </div>
            <div class="character-mouth"></div>
          </div>
        </div>
      </div>

      <div class="bottom-links">
        <a href="#">隐私政策</a>
        <a href="#">服务条款</a>
      </div>
    </div>

    <div class="right-panel">
      <div class="login-form">
        <h1 class="title">欢迎回来！</h1>
        <p class="subtitle">请输入您的账号信息</p>

        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label>用户名</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              @focus="onInputFocus"
              @blur="onInputBlur"
              required
            />
          </div>

          <div class="form-group">
            <label>密码</label>
            <div class="password-wrapper">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                @focus="onInputFocus"
                @blur="onInputBlur"
                required
              />
              <button
                type="button"
                class="toggle-btn"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
          </div>

          <div class="options-row">
            <label class="remember">
              <input type="checkbox" v-model="rememberMe" />
              <span>记住我 30 天</span>
            </label>
            <a href="#" class="forgot">忘记密码？</a>
          </div>

          <div v-if="error" class="error">{{ error }}</div>

          <button type="submit" class="login-btn" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <p class="signup">
          还没有账号？
          <a href="#" class="signup-link" @click.prevent="handleGoRegister">立即注册</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  emits: ['login-success', 'go-register'],
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      rememberMe: false,
      loading: false,
      isTyping: false,
      error: '',
      mouseX: 0,
      mouseY: 0,
      isPurplePeeking: false,
      purpleBlinking: false,
      blackBlinking: false,
      isLookingAtEachOther: false,
      peekTimer: null,
      blinkTimer: null,
      lookAtEachOtherTimer: null
    }
  },
  computed: {
    isHidingPassword() {
      return this.password.length > 0 && !this.showPassword
    },
    isShowingPassword() {
      return this.password.length > 0 && this.showPassword
    },
    purpleStyle() {
      return this.getCharacterStyle('purple')
    },
    orangeStyle() {
      return this.getCharacterStyle('orange')
    },
    blackStyle() {
      return this.getCharacterStyle('black')
    },
    yellowStyle() {
      return this.getCharacterStyle('yellow')
    }
  },
  watch: {
    password(newVal) {
      if (newVal.length > 0 && this.showPassword) {
        this.startPeeking()
      } else {
        this.stopPeeking()
      }
    },
    showPassword(newVal) {
      if (newVal && this.password.length > 0) {
        this.startPeeking()
      } else {
        this.stopPeeking()
      }
    }
  },
  mounted() {
    window.addEventListener('mousemove', this.handleMouseMove)
    this.startBlinking()
  },
  beforeUnmount() {
    window.removeEventListener('mousemove', this.handleMouseMove)
    this.stopPeeking()
    this.stopBlinking()
    this.stopLookingAtEachOther()
  },
  methods: {
    onInputFocus() {
      this.isTyping = true
      this.startLookingAtEachOther()
    },
    onInputBlur() {
      this.isTyping = false
      this.stopLookingAtEachOther()
    },
    startLookingAtEachOther() {
      this.stopLookingAtEachOther()
      this.isLookingAtEachOther = true
      this.lookAtEachOtherTimer = setTimeout(() => {
        this.isLookingAtEachOther = false
      }, 800)
    },
    stopLookingAtEachOther() {
      if (this.lookAtEachOtherTimer) {
        clearTimeout(this.lookAtEachOtherTimer)
        this.lookAtEachOtherTimer = null
      }
      this.isLookingAtEachOther = false
    },
    handleMouseMove(e) {
      this.mouseX = e.clientX
      this.mouseY = e.clientY
    },
    getCharacterStyle(type) {
      const centerX = window.innerWidth / 4
      const centerY = window.innerHeight / 2
      
      const deltaX = this.mouseX - centerX
      const bodySkew = Math.max(-6, Math.min(6, -deltaX / 120))
      
      let transform = ''
      let height = ''
      
      if (type === 'purple') {
        let skewX = bodySkew
        let translateX = 0
        
        if (this.isShowingPassword) {
          if (this.isPurplePeeking) {
            skewX = 0
            translateX = 40
          } else {
            skewX = 0
            translateX = 40
          }
        } else if (this.isTyping || this.isHidingPassword) {
          skewX = bodySkew - 12
          translateX = 40
        }
        
        transform = `skewX(${skewX}deg) translateX(${translateX}px)`
        height = (this.isTyping || this.isHidingPassword || this.isShowingPassword) ? '490px' : '450px'
        
        return {
          transform,
          height,
          transition: 'transform 0.7s ease-in-out, height 0.7s ease-in-out'
        }
      } else if (type === 'black') {
        let skewX = bodySkew
        let translateX = 0
        
        if (this.isLookingAtEachOther) {
          skewX = bodySkew * 1.5 + 10
          translateX = 20
        }
        
        return {
          transform: `skewX(${skewX}deg) translateX(${translateX}px)`,
          transition: 'transform 0.7s ease-in-out'
        }
      } else {
        return {
          transform: `skewX(${bodySkew}deg)`,
          transition: 'transform 0.7s ease-in-out'
        }
      }
    },
    getPupilStyle(type, eyeIndex) {
      let x = 0
      let y = 0
      
      if (this.isShowingPassword && !this.isPurplePeeking) {
        x = -4
        y = -4
      } else if (this.isPurplePeeking && type === 'purple') {
        x = 4
        y = 5
      } else if (this.isLookingAtEachOther) {
        if (type === 'purple') {
          x = 3
          y = 4
        } else if (type === 'black') {
          x = 0
          y = -4
        }
      } else {
        const centerX = window.innerWidth / 4
        const centerY = window.innerHeight / 2
        
        const deltaX = this.mouseX - centerX
        const deltaY = this.mouseY - centerY
        
        x = Math.max(-4, Math.min(4, deltaX / 100))
        y = Math.max(-4, Math.min(4, deltaY / 100))
      }
      
      return {
        transform: `translate(${x}px, ${y}px)`,
        transition: 'transform 0.1s ease-out'
      }
    },
    startPeeking() {
      this.stopPeeking()
      const schedulePeek = () => {
        this.peekTimer = setTimeout(() => {
          this.isPurplePeeking = true
          setTimeout(() => {
            this.isPurplePeeking = false
            schedulePeek()
          }, 800)
        }, Math.random() * 3000 + 2000)
      }
      schedulePeek()
    },
    stopPeeking() {
      if (this.peekTimer) {
        clearTimeout(this.peekTimer)
        this.peekTimer = null
      }
      this.isPurplePeeking = false
    },
    startBlinking() {
      const blink = () => {
        const randomDelay = Math.random() * 4000 + 3000
        this.blinkTimer = setTimeout(() => {
          this.purpleBlinking = true
          setTimeout(() => { this.purpleBlinking = false }, 150)
          
          setTimeout(() => {
            this.blackBlinking = true
            setTimeout(() => { this.blackBlinking = false }, 150)
          }, Math.random() * 500)
          
          blink()
        }, randomDelay)
      }
      blink()
    },
    stopBlinking() {
      if (this.blinkTimer) {
        clearTimeout(this.blinkTimer)
        this.blinkTimer = null
      }
    },
    async handleLogin() {
      if (!this.username || !this.password) {
        this.error = '请输入用户名和密码'
        return
      }

      this.loading = true
      this.error = ''

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.username, password: this.password })
        })

        const data = await response.json()

        if (data.success) {
          const userInfo = { id: data.user_id, username: data.username, role: data.role }
          localStorage.setItem('userData', JSON.stringify(userInfo))
          if (data.token) localStorage.setItem('authToken', data.token)

          this.$message.success('登录成功！')
          this.$emit('login-success', userInfo)
        } else {
          this.error = data.message || '用户名或密码错误'
        }
      } catch (e) {
        this.error = '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    handleGoRegister() {
      console.log('立即注册按钮被点击了！')
      this.$emit('go-register')
    }
  }
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.login-container {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.left-panel {
  background: linear-gradient(145deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
  position: relative;
  overflow: hidden;
}

.left-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(102, 126, 234, 0.25) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.left-panel::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(139, 92, 246, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 50px 50px; }
}

.logo-section { 
  display: flex; 
  align-items: center; 
  gap: 16px; 
  position: relative;
  z-index: 1;
}
.logo-icon {
  width: 64px; 
  height: 64px; 
  border-radius: 16px;
  display: flex; 
  align-items: center; 
  justify-content: center;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}
.logo-icon svg {
  width: 100%;
  height: 100%;
}
.logo-text { 
  font-size: 28px; 
  font-weight: 800; 
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.6);
}

.center-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  position: relative;
  z-index: 1;
}

.characters-container {
  position: relative;
  width: 100%;
  height: 600px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.character-wrapper {
  position: absolute;
}

.character-purple-wrapper {
  left: 50%;
  transform: translateX(-50%);
  bottom: 0;
  z-index: 1;
}

.character {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform-origin: bottom center;
}

.character-purple {
  z-index: 1;
}

.character-purple .character-body {
  width: 180px;
  height: 450px;
  background: linear-gradient(135deg, #6c3ff5 0%, #4f2bc7 100%);
  border-radius: 10px 10px 0 0;
  transition: height 0.7s ease-in-out;
  box-shadow: 
    0 0 15px rgba(108, 63, 245, 0.25),
    0 0 30px rgba(108, 63, 245, 0.15),
    inset 0 0 10px rgba(255, 255, 255, 0.05);
  position: relative;
}

.character-purple .character-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 20%, rgba(255, 255, 255, 0.15) 0%, transparent 40%);
  border-radius: 10px 10px 0 0;
  animation: purpleGlow 4s ease-in-out infinite;
}

@keyframes purpleGlow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.character-orange {
  position: absolute;
  left: 12%;
  bottom: 0;
  z-index: 4;
}

.character-orange .character-body {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #ff9b6b 0%, #ff6b3d 100%);
  border-radius: 100px 100px 20px 20px;
  box-shadow: 
    0 0 15px rgba(255, 107, 61, 0.3),
    0 0 30px rgba(255, 107, 61, 0.18),
    inset 0 0 10px rgba(255, 255, 255, 0.08);
  position: relative;
}

.character-orange .character-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 30%, rgba(255, 255, 255, 0.18) 0%, transparent 45%);
  border-radius: 100px 100px 20px 20px;
  animation: orangeGlow 3.5s ease-in-out infinite;
}

@keyframes orangeGlow {
  0%, 100% { opacity: 0.25; }
  50% { opacity: 0.5; }
}

.character-black {
  position: absolute;
  right: 22%;
  bottom: 0;
  z-index: 2;
}

.character-black .character-body {
  width: 150px;
  height: 310px;
  background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
  border-radius: 15px;
  box-shadow: 
    0 0 12px rgba(80, 80, 80, 0.25),
    0 0 25px rgba(50, 50, 50, 0.15),
    inset 0 0 8px rgba(255, 255, 255, 0.03);
  position: relative;
}

.character-black .character-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 25%, rgba(100, 100, 100, 0.1) 0%, transparent 40%);
  border-radius: 15px;
  animation: blackGlow 4.5s ease-in-out infinite;
}

@keyframes blackGlow {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.4; }
}

.character-yellow {
  position: absolute;
  right: 8%;
  bottom: 0;
  z-index: 3;
}

.character-yellow .character-body {
  width: 140px;
  height: 230px;
  background: linear-gradient(135deg, #e8d754 0%, #d4c02a 100%);
  border-radius: 70px 70px 15px 15px;
  position: relative;
  box-shadow: 
    0 0 18px rgba(232, 215, 84, 0.35),
    0 0 35px rgba(232, 215, 84, 0.2),
    inset 0 0 10px rgba(255, 255, 255, 0.1);
}

.character-yellow .character-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 25%, rgba(255, 255, 255, 0.2) 0%, transparent 45%);
  border-radius: 70px 70px 15px 15px;
  animation: yellowGlow 3.8s ease-in-out infinite;
}

@keyframes yellowGlow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.55; }
}

.character-yellow .character-mouth {
  position: absolute;
  bottom: 80px;
  width: 60px;
  height: 4px;
  background: #2d2d2d;
  border-radius: 2px;
}

.character-eyes {
  position: absolute;
  top: 60px;
  display: flex;
  gap: 30px;
  z-index: 10;
}

.eye {
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 0 8px rgba(255, 255, 255, 0.5),
    0 0 15px rgba(255, 255, 255, 0.3);
  animation: eyePulse 3s ease-in-out infinite;
}

@keyframes eyePulse {
  0%, 100% { box-shadow: 0 0 8px rgba(255, 255, 255, 0.5), 0 0 15px rgba(255, 255, 255, 0.3); }
  50% { box-shadow: 0 0 12px rgba(255, 255, 255, 0.65), 0 0 22px rgba(255, 255, 255, 0.35); }
}

.eye.blinking {
  animation: blink 0.15s ease-in-out;
}

.pupil {
  width: 10px;
  height: 10px;
  background: #2d2d2d;
  border-radius: 50%;
  position: absolute;
  top: 7px;
  left: 7px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}

@keyframes blink {
  0%, 100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(0.1);
  }
}

.bottom-links { 
  display: flex; 
  gap: 24px; 
  font-size: 14px; 
  position: relative;
  z-index: 1;
}
.bottom-links a { 
  color: rgba(255,255,255,0.8); 
  text-decoration: none; 
  transition: all 0.3s ease;
}
.bottom-links a:hover { 
  color: white; 
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.8);
}

.right-panel {
  display: flex; 
  align-items: center; 
  justify-content: center;
  background: linear-gradient(135deg, #1a1628 0%, #0f0c29 50%, #1a1628 100%);
  padding: 48px;
  position: relative;
  overflow: hidden;
}

.right-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 80% 20%, rgba(102, 126, 234, 0.15) 0%, transparent 45%),
    radial-gradient(circle at 20% 80%, rgba(118, 75, 162, 0.15) 0%, transparent 45%);
  pointer-events: none;
}

.login-form { 
  width: 100%; 
  max-width: 480px; 
  position: relative;
  z-index: 1;
  background: linear-gradient(145deg, rgba(15, 12, 41, 0.85) 0%, rgba(30, 25, 65, 0.85) 100%);
  backdrop-filter: blur(20px);
  padding: 48px;
  border-radius: 24px;
  border: 1px solid rgba(139, 92, 246, 0.25);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 60px rgba(102, 126, 234, 0.1);
}

.title { 
  font-size: 36px; 
  font-weight: 800; 
  color: #ffffff; 
  margin-bottom: 8px; 
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.6);
}
.subtitle { 
  color: rgba(255, 255, 255, 0.6); 
  margin-bottom: 36px; 
}

.form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { 
  font-size: 14px; 
  font-weight: 600; 
  color: rgba(255, 255, 255, 0.8); 
}
.form-group input {
  height: 56px; 
  padding: 0 20px; 
  border: 1px solid rgba(139, 92, 246, 0.3);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 14px; 
  font-size: 15px; 
  transition: all 0.3s ease;
  color: #ffffff;
  backdrop-filter: blur(4px);
}
.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}
.form-group input:focus { 
  outline: none; 
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.password-wrapper { position: relative; }
.password-wrapper input { width: 100%; padding-right: 50px; }
.toggle-btn {
  position: absolute; 
  right: 14px; 
  top: 50%; 
  transform: translateY(-50%);
  background: none; 
  border: none; 
  cursor: pointer; 
  font-size: 18px;
  transition: all 0.3s ease;
}
.toggle-btn:hover {
  transform: translateY(-50%) scale(1.1);
}

.options-row { display: flex; justify-content: space-between; align-items: center; }
.remember { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  font-size: 14px; 
  color: rgba(255, 255, 255, 0.7); 
  cursor: pointer; 
}
.remember input { 
  width: 18px; 
  height: 18px; 
  cursor: pointer; 
  accent-color: #667eea;
}
.forgot { 
  font-size: 14px; 
  color: #a78bfa; 
  text-decoration: none; 
  transition: all 0.3s ease;
}
.forgot:hover { 
  text-decoration: underline; 
  color: #c4b5fd;
  text-shadow: 0 0 10px rgba(167, 139, 250, 0.5);
}

.error { 
  color: #f87171; 
  font-size: 14px; 
  margin-top: -8px; 
  text-shadow: 0 0 10px rgba(248, 113, 113, 0.4);
}

.login-btn {
  width: 100%;
  height: 56px; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; 
  border: none; 
  border-radius: 14px;
  font-size: 18px; 
  font-weight: 600; 
  cursor: pointer; 
  transition: all 0.3s ease; 
  margin-top: 8px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.login-btn:hover:not(:disabled) { 
  transform: translateY(-2px); 
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
}
.login-btn:disabled { 
  opacity: 0.6; 
  cursor: not-allowed; 
}

.divider { 
  display: flex; 
  align-items: center; 
  margin: 24px 0; 
  color: rgba(255, 255, 255, 0.5); 
  font-size: 14px; 
}
.divider::before, .divider::after { 
  content: ''; 
  flex: 1; 
  height: 1px; 
  background: rgba(139, 92, 246, 0.3); 
}
.divider span { padding: 0 16px; }

.google-btn {
  width: 100%; 
  height: 52px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  gap: 12px;
  background: rgba(255, 255, 255, 0.05); 
  border: 1px solid rgba(139, 92, 246, 0.3); 
  border-radius: 14px;
  font-size: 15px; 
  color: rgba(255, 255, 255, 0.8); 
  cursor: pointer; 
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
}
.google-btn:hover:not(:disabled) { 
  background: rgba(255, 255, 255, 0.1); 
  border-color: rgba(102, 126, 234, 0.6);
}
.google-icon { width: 20px; height: 20px; }

.signup { 
  margin-top: 24px; 
  text-align: center; 
  font-size: 14px; 
  color: rgba(255, 255, 255, 0.6); 
}
.signup a { 
  color: #a78bfa; 
  text-decoration: none; 
  font-weight: 600; 
  transition: all 0.3s ease;
}
.signup a:hover { 
  text-decoration: underline; 
  color: #c4b5fd;
  text-shadow: 0 0 10px rgba(167, 139, 250, 0.5);
}

@media (max-width: 768px) {
  .login-container { grid-template-columns: 1fr; }
  .left-panel { display: none; }
  .right-panel { min-height: 100vh; }
}
</style>
