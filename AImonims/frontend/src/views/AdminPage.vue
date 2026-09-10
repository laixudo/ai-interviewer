<template>
  <div class="admin-container">
    <div class="admin-header">
      <div class="header-left">
        <h1 class="admin-title">
          <i class="el-icon-setting"></i>
          管理后台
        </h1>
      </div>
      <div class="header-right">
        <div class="admin-info">
          <span class="admin-badge">
            <i class="el-icon-user"></i>
            管理员
          </span>
          <span class="username">{{ username }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <i class="el-icon-switch-button"></i>
          退出
        </button>
      </div>
    </div>

    <div class="admin-content">
      <div class="admin-sidebar">
        <el-menu
          :default-active="activeMenu"
          class="admin-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="dashboard">
            <i class="el-icon-data-line"></i>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="users">
            <i class="el-icon-user"></i>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="interviews">
            <i class="el-icon-chat-dot-round"></i>
            <span>面试记录</span>
          </el-menu-item>
          <el-menu-item index="exam-questions">
            <i class="el-icon-document"></i>
            <span>真题管理</span>
          </el-menu-item>
          <el-menu-item index="selected-questions">
            <i class="el-icon-check-circle"></i>
            <span>精选题库</span>
          </el-menu-item>
        </el-menu>
      </div>

      <div class="admin-main">
        <component :is="currentComponent" @switch-menu="handleMenuSelect" />
      </div>
    </div>
  </div>
</template>

<script>
import AdminDashboard from './AdminDashboard.vue'
import AdminUserManagement from './AdminUserManagement.vue'
import AdminInterviewManagement from './AdminInterviewManagement.vue'
import AdminExamQuestions from './AdminExamQuestions.vue'
import AdminSelectedQuestions from './AdminSelectedQuestions.vue'

export default {
  name: 'AdminPage',
  components: {
    AdminDashboard,
    AdminUserManagement,
    AdminInterviewManagement,
    AdminExamQuestions,
    AdminSelectedQuestions
  },
  data() {
    return {
      activeMenu: 'dashboard',
      username: localStorage.getItem('username') || 'admin'
    }
  },
  computed: {
    currentComponent() {
      const components = {
        'dashboard': 'AdminDashboard',
        'users': 'AdminUserManagement',
        'interviews': 'AdminInterviewManagement',
        'exam-questions': 'AdminExamQuestions',
        'selected-questions': 'AdminSelectedQuestions'
      }
      return components[this.activeMenu] || 'AdminDashboard'
    }
  },
  methods: {
    handleMenuSelect(index) {
      this.activeMenu = index
    },
    handleLogout() {
      localStorage.clear()
      this.$emit('logout')
    }
  }
}
</script>

<style scoped>
.admin-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.admin-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-title i {
  font-size: 28px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
}

.username {
  font-size: 16px;
  font-weight: 500;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.admin-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.admin-sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.admin-menu {
  border: none;
}

.admin-menu i {
  font-size: 18px;
}

.admin-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
