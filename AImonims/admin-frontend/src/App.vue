<template>
  <div class="admin-wrapper">
    <template v-if="!isLoggedIn">
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
            <h1 class="title">管理员登录</h1>
            <p class="subtitle">请输入您的账号信息</p>

            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label>用户名</label>
                <input
                  v-model="username"
                  type="text"
                  placeholder="请输入管理员账号"
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
                  <span>记住我</span>
                </label>
              </div>

              <div v-if="error" class="error">{{ error }}</div>

              <button type="submit" class="login-btn" :disabled="loading">
                {{ loading ? '登录中...' : '登录' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="admin-layout">
        <aside class="sidebar">
          <div class="sidebar-header">
            <h2 class="sidebar-title">管理中心</h2>
          </div>
          <nav class="sidebar-nav">
            <div 
              v-for="item in menuItems" 
              :key="item.key"
              class="nav-item"
              :class="{ active: activeMenu === item.key }"
              @click="activeMenu = item.key"
            >
              <span>{{ item.label }}</span>
            </div>
          </nav>
          <div class="sidebar-footer">
            <div class="user-info">
              <span class="username">{{ userInfo.username }}</span>
              <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
            </div>
          </div>
        </aside>

        <main class="main-content">
          <Dashboard v-if="activeMenu === 'dashboard'" :stats="stats" />
          <UserManagement v-if="activeMenu === 'users'" :users="users" @refresh="loadUsers" />
          <InterviewManagement v-if="activeMenu === 'interviews'" :interviews="interviews" @refresh="loadInterviews" />
          <ExamQuestions v-if="activeMenu === 'questions'" :questions="examQuestions" @refresh="loadQuestions" />
          <SelectedQuestions v-if="activeMenu === 'selected'" />
        </main>
      </div>
    </template>
  </div>
</template>

<script>
import Dashboard from './components/Dashboard.vue'
import UserManagement from './components/UserManagement.vue'
import InterviewManagement from './components/InterviewManagement.vue'
import ExamQuestions from './components/ExamQuestions.vue'
import SelectedQuestions from './components/SelectedQuestions.vue'

export default {
  name: 'AdminApp',
  components: {
    Dashboard, UserManagement, InterviewManagement, ExamQuestions, SelectedQuestions
  },
  data() {
    return {
      isLoggedIn: false,
      loading: false,
      username: '',
      password: '',
      showPassword: false,
      rememberMe: false,
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
      lookAtEachOtherTimer: null,
      userInfo: { username: '管理员' },
      activeMenu: 'dashboard',
      menuItems: [
        { key: 'dashboard', label: '数据概览' },
        { key: 'users', label: '用户管理' },
        { key: 'interviews', label: '面试记录' },
        { key: 'questions', label: '真题管理' },
        { key: 'selected', label: '精选题库' }
      ],
      stats: { totalUsers: 0, totalInterviews: 0, totalQuestions: 0, avgScore: 0 },
      users: [],
      interviews: [],
      examQuestions: []
    }
  },
  computed: {
    isHidingPassword() { return this.password.length > 0 && !this.showPassword },
    isShowingPassword() { return this.password.length > 0 && this.showPassword },
    purpleStyle() { return this.getCharacterStyle('purple') },
    orangeStyle() { return this.getCharacterStyle('orange') },
    blackStyle() { return this.getCharacterStyle('black') },
    yellowStyle() { return this.getCharacterStyle('yellow') }
  },
  watch: {
    password(newVal) {
      if (newVal.length > 0 && this.showPassword) { this.startPeeking() }
      else { this.stopPeeking() }
    },
    showPassword(newVal) {
      if (newVal && this.password.length > 0) { this.startPeeking() }
      else { this.stopPeeking() }
    }
  },
  mounted() {
    this.checkLoginStatus()
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
    checkLoginStatus() {
      // 已移除 ?admin=<base64> 的 URL 提权分支：原来只要构造
      // btoa('{"role":"admin"}') 放进地址栏就能进管理后台。
      // 管理员身份现在只能由后端签发的令牌证明。
      
      const adminData = localStorage.getItem('adminData')
      if (adminData) {
        try {
          const admin = JSON.parse(adminData)
          if (admin.role === 'admin') {
            this.userInfo = admin
            this.isLoggedIn = true
            this.loadAllData()
          }
        } catch (e) { localStorage.removeItem('adminData') }
      }
    },
    onInputFocus() { this.isTyping = true; this.startLookingAtEachOther() },
    onInputBlur() { this.isTyping = false; this.stopLookingAtEachOther() },
    startLookingAtEachOther() {
      this.stopLookingAtEachOther()
      this.isLookingAtEachOther = true
      this.lookAtEachOtherTimer = setTimeout(() => { this.isLookingAtEachOther = false }, 800)
    },
    stopLookingAtEachOther() {
      if (this.lookAtEachOtherTimer) { clearTimeout(this.lookAtEachOtherTimer); this.lookAtEachOtherTimer = null }
      this.isLookingAtEachOther = false
    },
    handleMouseMove(e) { this.mouseX = e.clientX; this.mouseY = e.clientY },
    getCharacterStyle(type) {
      const centerX = window.innerWidth / 4
      const centerY = window.innerHeight / 2
      const deltaX = this.mouseX - centerX
      const bodySkew = Math.max(-6, Math.min(6, -deltaX / 120))
      
      if (type === 'purple') {
        let skewX = bodySkew, translateX = 0
        if (this.isShowingPassword) { skewX = 0; translateX = 40 }
        else if (this.isTyping || this.isHidingPassword) { skewX = bodySkew - 12; translateX = 40 }
        return { transform: `skewX(${skewX}deg) translateX(${translateX}px)`, height: (this.isTyping || this.isHidingPassword || this.isShowingPassword) ? '490px' : '450px', transition: 'transform 0.7s ease-in-out, height 0.7s ease-in-out' }
      } else if (type === 'black') {
        let skewX = bodySkew, translateX = 0
        if (this.isLookingAtEachOther) { skewX = bodySkew * 1.5 + 10; translateX = 20 }
        return { transform: `skewX(${skewX}deg) translateX(${translateX}px)`, transition: 'transform 0.7s ease-in-out' }
      }
      return { transform: `skewX(${bodySkew}deg)`, transition: 'transform 0.7s ease-in-out' }
    },
    getPupilStyle(type, eyeIndex) {
      let x = 0, y = 0
      if (this.isShowingPassword && !this.isPurplePeeking) { x = -4; y = -4 }
      else if (this.isPurplePeeking && type === 'purple') { x = 4; y = 5 }
      else if (this.isLookingAtEachOther) { if (type === 'purple') { x = 3; y = 4 } else if (type === 'black') { x = 0; y = -4 } }
      else { const centerX = window.innerWidth / 4; const centerY = window.innerHeight / 2; const deltaX = this.mouseX - centerX; const deltaY = this.mouseY - centerY; x = Math.max(-4, Math.min(4, deltaX / 100)); y = Math.max(-4, Math.min(4, deltaY / 100)) }
      return { transform: `translate(${x}px, ${y}px)`, transition: 'transform 0.1s ease-out' }
    },
    startPeeking() {
      this.stopPeeking()
      const schedulePeek = () => {
        this.peekTimer = setTimeout(() => {
          this.isPurplePeeking = true
          setTimeout(() => { this.isPurplePeeking = false; schedulePeek() }, 800)
        }, Math.random() * 3000 + 2000)
      }
      schedulePeek()
    },
    stopPeeking() { if (this.peekTimer) { clearTimeout(this.peekTimer); this.peekTimer = null } this.isPurplePeeking = false },
    startBlinking() {
      const blink = () => {
        const randomDelay = Math.random() * 4000 + 3000
        this.blinkTimer = setTimeout(() => {
          this.purpleBlinking = true
          setTimeout(() => { this.purpleBlinking = false }, 150)
          setTimeout(() => { this.blackBlinking = true; setTimeout(() => { this.blackBlinking = false }, 150) }, Math.random() * 500)
          blink()
        }, randomDelay)
      }
      blink()
    },
    stopBlinking() { if (this.blinkTimer) { clearTimeout(this.blinkTimer); this.blinkTimer = null } },
    async handleLogin() {
      if (!this.username || !this.password) { this.error = '请输入用户名和密码'; return }
      this.loading = true; this.error = ''
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
          if (data.role === 'admin') {
            this.userInfo = userInfo
            this.isLoggedIn = true
            localStorage.setItem('adminData', JSON.stringify(this.userInfo))
            this.loadAllData()
          } else {
            this.error = '您不是管理员'
          }
        } else { this.error = data.message || '用户名或密码错误' }
      } catch (e) { this.error = '网络错误，请稍后重试' }
      finally { this.loading = false }
    },
    handleLogout() {
      this.isLoggedIn = false
      this.userInfo = { username: '管理员' }
      this.username = ''
      this.password = ''
      this.activeMenu = 'dashboard'
      localStorage.removeItem('adminData')
    },
    async loadAllData() {
      await Promise.all([this.loadStats(), this.loadUsers(), this.loadInterviews(), this.loadQuestions()])
    },
    async loadStats() {
      try {
        const response = await fetch('/api/admin/stats')
        if (response.ok) { const data = await response.json(); this.stats = data }
      } catch (error) { console.error('加载统计数据失败:', error) }
    },
    async loadUsers() {
      try {
        const response = await fetch('/api/admin/users')
        if (response.ok) { const data = await response.json(); this.users = data.users || [] }
      } catch (error) { console.error('加载用户列表失败:', error) }
    },
    async loadInterviews() {
      try {
        const response = await fetch('/api/admin/interviews')
        if (response.ok) { const data = await response.json(); this.interviews = data.interviews || [] }
      } catch (error) { console.error('加载面试记录失败:', error) }
    },
    async loadQuestions() {
      try {
        const response = await fetch('/api/admin/exam-questions')
        if (response.ok) { const data = await response.json(); this.examQuestions = data.questions || [] }
      } catch (error) { console.error('加载真题列表失败:', error) }
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
.admin-wrapper { min-height: 100vh; }
.login-container {
  min-height: 100vh; display: grid; grid-template-columns: 1fr 1fr;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.left-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 48px; display: flex; flex-direction: column; justify-content: space-between; color: white;
}
.logo-section { display: flex; align-items: center; gap: 16px; }
.logo-icon { width: 64px; height: 64px; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.logo-icon svg { width: 100%; height: 100%; }
.logo-text { font-size: 28px; font-weight: 800; }
.center-content { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; }
.characters-container { position: relative; width: 100%; height: 600px; display: flex; align-items: flex-end; justify-content: center; }
.character-wrapper { position: absolute; }
.character-purple-wrapper { left: 50%; transform: translateX(-50%); bottom: 0; z-index: 1; }
.character { position: relative; display: flex; flex-direction: column; align-items: center; transform-origin: bottom center; }
.character-purple { z-index: 1; }
.character-purple .character-body { width: 180px; height: 450px; background: #6c3ff5; border-radius: 10px 10px 0 0; transition: height 0.7s ease-in-out; }
.character-orange { position: absolute; left: 12%; bottom: 0; z-index: 4; }
.character-orange .character-body { width: 200px; height: 200px; background: #ff9b6b; border-radius: 100px 100px 20px 20px; }
.character-black { position: absolute; right: 22%; bottom: 0; z-index: 2; }
.character-black .character-body { width: 150px; height: 310px; background: #2d2d2d; border-radius: 15px; }
.character-yellow { position: absolute; right: 8%; bottom: 0; z-index: 3; }
.character-yellow .character-body { width: 140px; height: 230px; background: #e8d754; border-radius: 70px 70px 15px 15px; position: relative; }
.character-yellow .character-mouth { position: absolute; bottom: 80px; width: 60px; height: 4px; background: #2d2d2d; border-radius: 2px; }
.character-eyes { position: absolute; top: 60px; display: flex; gap: 30px; z-index: 10; }
.eye { width: 24px; height: 24px; background: white; border-radius: 50%; position: relative; overflow: hidden; }
.eye.blinking { animation: blink 0.15s ease-in-out; }
.pupil { width: 10px; height: 10px; background: #2d2d2d; border-radius: 50%; position: absolute; top: 7px; left: 7px; }
@keyframes blink { 0%, 100% { transform: scaleY(1); } 50% { transform: scaleY(0.1); } }
.bottom-links { display: flex; gap: 24px; font-size: 14px; }
.bottom-links a { color: rgba(255,255,255,0.8); text-decoration: none; }
.bottom-links a:hover { color: white; }
.right-panel { display: flex; align-items: center; justify-content: center; background: #f5f7fa; padding: 48px; }
.login-form { width: 100%; max-width: 480px; }
.title { font-size: 36px; font-weight: 800; color: #303133; margin-bottom: 8px; }
.subtitle { color: #909399; margin-bottom: 36px; }
.form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 14px; font-weight: 600; color: #303133; }
.form-group input { height: 56px; padding: 0 16px; border: 1px solid #e4e7ed; border-radius: 10px; font-size: 15px; transition: border-color 0.3s; }
.form-group input:focus { outline: none; border-color: #667eea; }
.password-wrapper { position: relative; }
.password-wrapper input { width: 100%; padding-right: 50px; }
.toggle-btn { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 18px; }
.options-row { display: flex; justify-content: space-between; align-items: center; }
.remember { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #606266; cursor: pointer; }
.remember input { width: 16px; height: 16px; cursor: pointer; }
.error { color: #f56c6c; font-size: 14px; margin-top: -8px; }
.login-btn { width: 100%; height: 56px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: 600; cursor: pointer; transition: all 0.3s; margin-top: 8px; }
.login-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102,126,234,0.4); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.admin-layout { display: flex; min-height: 100vh; }
.sidebar { width: 240px; background: white; display: flex; flex-direction: column; box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1); }
.sidebar-header { padding: 24px 20px; border-bottom: 1px solid #f0f0f0; }
.sidebar-title { font-size: 18px; font-weight: 600; color: #303133; }
.sidebar-nav { flex: 1; padding: 16px 12px; }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 14px 16px; margin-bottom: 8px; border-radius: 12px; cursor: pointer; color: #606266; transition: all 0.3s ease; }
.nav-item:hover { background: #f5f7fa; color: #667eea; }
.nav-item.active { background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); color: #667eea; font-weight: 500; }
.sidebar-footer { padding: 16px 20px; border-top: 1px solid #f0f0f0; }
.user-info { display: flex; align-items: center; justify-content: space-between; }
.user-info .username { font-size: 14px; color: #303133; }
.main-content { flex: 1; padding: 24px; overflow-y: auto; background: #f5f7fa; }
@media (max-width: 768px) { .login-container { grid-template-columns: 1fr; } .left-panel { display: none; } .right-panel { min-height: 100vh; } }
</style>
