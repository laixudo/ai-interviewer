<template>
  <div class="user-management">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <el-button type="primary" @click="$emit('refresh')">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索用户名..."
        prefix-icon="Search"
        clearable
        style="width: 300px"
      />
    </div>

    <div class="user-table">
      <el-table :data="filteredUsers" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="created_at" label="注册时间" />
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewProfile(row)">
              查看档案
            </el-button>
            <el-button 
              v-if="!isAdminUser(row)" 
              type="danger" 
              size="small" 
              @click="handleDeleteUser(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="profileDialogVisible" title="用户能力档案" width="600px">
      <div v-if="currentUser" class="profile-content">
        <div class="profile-header">
          <div class="avatar">
            <img :src="currentUser.avatar || defaultAvatar" alt="avatar" />
          </div>
          <div class="user-details">
            <h3>{{ currentUser.username }}</h3>
            <p>注册时间: {{ currentUser.created_at }}</p>
          </div>
        </div>
        <div class="profile-stats">
          <div class="stat-item">
            <span class="label">面试次数</span>
            <span class="value">{{ userAbilityProfile.interviewCount || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="label">平均分数</span>
            <span class="value">{{ userAbilityProfile.avgScore || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="label">能力等级</span>
            <span class="value level">{{ userAbilityProfile.level || '暂无数据' }}</span>
          </div>
        </div>
        <div v-if="userAbilityProfile.positions && userAbilityProfile.positions.length > 0" class="profile-abilities">
          <h4>面试岗位分布</h4>
          <div class="ability-list">
            <div v-for="(item, idx) in userAbilityProfile.positions" :key="idx" class="ability-item">
              <span class="ability-name">{{ item.name }}</span>
              <el-progress :percentage="Math.round((item.count / userAbilityProfile.interviewCount) * 100)" :color="getProgressColor(Math.round((item.count / userAbilityProfile.interviewCount) * 100))" />
              <span class="ability-count">{{ item.count }}次</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { Search, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'UserManagement',
  components: { Search, Refresh },
  props: {
    users: {
      type: Array,
      default: () => []
    }
  },
  emits: ['refresh'],
  data() {
    return {
      searchQuery: '',
      profileDialogVisible: false,
      currentUser: null,
      userAbilityProfile: {},
      defaultAvatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20avatar&image_size=square'
    }
  },
  computed: {
    filteredUsers() {
      if (!this.searchQuery) return this.users
      return this.users.filter(user => 
        user.username?.toLowerCase().includes(this.searchQuery.toLowerCase())
      )
    }
  },
  methods: {
    async viewProfile(user) {
      this.currentUser = user
      this.profileDialogVisible = true
      this.userAbilityProfile = {}
      try {
        const response = await fetch(`/api/admin/user/${user.id}/ability-profile`)
        if (response.ok) {
          const data = await response.json()
          console.log('用户档案API返回:', data)
          if (data.success) {
            this.userAbilityProfile = data
            console.log('设置后的userAbilityProfile:', this.userAbilityProfile)
          } else {
            this.$message.error(data.error || '获取用户档案失败')
          }
        }
      } catch (error) {
        console.error('加载用户档案失败:', error)
        this.$message.error('加载用户档案失败')
      }
    },
    getAbilityName(key) {
      const names = {
        technical: '技术能力',
        communication: '沟通表达',
        problemSolving: '问题解决',
        teamwork: '团队协作'
      }
      return names[key] || key
    },
    getProgressColor(value) {
      if (value >= 80) return '#67c23a'
      if (value >= 60) return '#409eff'
      if (value >= 40) return '#e6a23c'
      return '#f56c6c'
    },
    isAdminUser(user) {
      const adminUsernames = ['admin', 'administrator', '管理员']
      return adminUsernames.includes(user.username?.toLowerCase())
    },
    async handleDeleteUser(user) {
      try {
        const confirmed = await this.$confirm(
          `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
          '删除确认',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        if (confirmed) {
          const response = await fetch(`/api/admin/users/${user.id}`, {
            method: 'DELETE'
          })
          const result = await response.json()
          
          if (result.success) {
            this.$message.success('删除成功！')
            this.$emit('refresh')
          } else {
            this.$message.error(result.error || '删除失败')
          }
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除用户失败:', error)
          this.$message.error('删除失败')
        }
      }
    }
  }
}
</script>

<style scoped>
.user-management {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.search-bar {
  margin-bottom: 20px;
}

.user-table {
  margin-top: 16px;
}

.profile-content {
  padding: 10px 0;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.avatar img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.user-details h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.user-details p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.profile-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.stat-item {
  flex: 1;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
}

.stat-item .label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-item .value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-item .value.level {
  font-size: 16px;
  color: #667eea;
}

.profile-abilities h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.ability-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ability-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ability-name {
  width: 120px;
  font-size: 14px;
  color: #606266;
}

.ability-count {
  width: 50px;
  font-size: 13px;
  color: #909399;
  text-align: right;
}

.ability-item :deep(.el-progress) {
  flex: 1;
}
</style>
