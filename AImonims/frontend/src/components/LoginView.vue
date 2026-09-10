<template>
  <div class="login-page">
    <div class="login-card">
      <h1>🎯 Offer制造机</h1>
      <p>AI 智能面试系统</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <input
            v-model="username"
            type="text"
            placeholder="用户名"
            required
          />
        </div>
        <div class="form-group">
          <input
            v-model="password"
            type="password"
            placeholder="密码"
            required
          />
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="footer">
        <span>还没有账号？</span>
        <a href="#" @click.prevent="$emit('go-register')">立即注册</a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  emits: ['login-success', 'go-register'],
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''

      try {
        const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
        const response = await fetch(`${API_BASE}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        })

        const data = await response.json()

        if (data.success) {
          const userInfo = {
            id: data.user_id,
            username: data.username,
            role: data.role
          }
          localStorage.setItem('userData', JSON.stringify(userInfo))

          if (data.role === 'admin') {
            this.$message.success('管理员登录成功，即将跳转...')
            setTimeout(() => {
              window.location.href = `${API_BASE}/docs`
            }, 1500)
          } else {
            this.$message.success('登录成功！')
            this.$emit('login-success', userInfo)
          }
        } else {
          this.error = data.message || '用户名或密码错误'
        }
      } catch (e) {
        console.error('登录失败:', e)
        this.error = '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 48px 40px;
  border-radius: 20px;
  text-align: center;
  width: 400px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
}

.login-card h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.login-card > p {
  color: #909399;
  margin-bottom: 32px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group input {
  width: 100%;
  padding: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 15px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

button[type="submit"] {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
  transition: opacity 0.3s;
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button[type="submit"]:hover:not(:disabled) {
  opacity: 0.9;
}

.error {
  color: #f56c6c;
  margin-top: 16px;
  font-size: 14px;
}

.footer {
  margin-top: 24px;
  font-size: 14px;
  color: #909399;
}

.footer a {
  color: #667eea;
  text-decoration: none;
  margin-left: 4px;
}

.footer a:hover {
  text-decoration: underline;
}
</style>