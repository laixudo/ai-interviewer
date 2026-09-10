<template>
  <div class="user-management">
    <div class="management-header">
      <h2 class="section-title">
        <i class="el-icon-user"></i>
        用户管理
      </h2>
      <div class="header-actions">
        <el-input
          v-model="keyword"
          placeholder="搜索用户名或邮箱"
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <i class="el-icon-search"></i>
          </template>
        </el-input>
        <el-button type="primary" class="refresh-btn" @click="loadUsers">
          <i class="el-icon-refresh"></i>
          刷新
        </el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table
        :data="users"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'success'" size="small" effect="dark">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="interview_count" label="面试次数" width="100" align="center" />
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="viewUserDetail(row)">
              <i class="el-icon-view"></i>
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog
      v-model="showDetailDialog"
      title="用户详情"
      width="600px"
      class="custom-dialog"
    >
      <div v-if="selectedUser" class="user-detail">
        <div class="detail-header">
          <div class="user-avatar">
            <i class="el-icon-user-solid"></i>
          </div>
          <div class="user-basic">
            <h3>{{ selectedUser.username }}</h3>
            <el-tag :type="selectedUser.role === 'admin' ? 'danger' : 'success'" size="small" effect="dark">
              {{ selectedUser.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </div>
        </div>
        <el-divider />
        <div class="detail-info">
          <div class="info-item">
            <span class="info-label"><i class="el-icon-message"></i> 邮箱</span>
            <span class="info-value">{{ selectedUser.email || '暂无' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label"><i class="el-icon-chat-dot-round"></i> 面试次数</span>
            <span class="info-value highlight">{{ selectedUser.interview_count }} 次</span>
          </div>
          <div class="info-item">
            <span class="info-label"><i class="el-icon-time"></i> 注册时间</span>
            <span class="info-value">{{ formatDate(selectedUser.created_at) }}</span>
          </div>
        </div>
        <el-divider />
        <div class="ability-section">
          <h4><i class="el-icon-data-analysis"></i> 能力档案</h4>
          <div v-if="userAbilityProfile" class="ability-info">
            <div class="ability-score">
              <div class="score-circle">
                <svg viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" class="score-bg" />
                  <circle
                    cx="50" cy="50" r="45"
                    class="score-progress"
                    :stroke-dasharray="283 * (userAbilityProfile.overall_score / 100) + ' 283'"
                  />
                </svg>
                <div class="score-center">
                  <span class="score-value">{{ userAbilityProfile.overall_score || 0 }}</span>
                  <span class="score-label">分</span>
                </div>
              </div>
            </div>
            <div class="ability-stats">
              <div class="stat-item">
                <span class="stat-value">{{ userAbilityProfile.total_interviews || 0 }}</span>
                <span class="stat-label">面试次数</span>
              </div>
            </div>
          </div>
          <div v-else class="no-data">暂无能力档案数据</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AdminUserManagement',
  emits: ['switch-menu'],
  data() {
    return {
      users: [],
      loading: false,
      currentPage: 1,
      pageSize: 20,
      total: 0,
      keyword: '',
      showDetailDialog: false,
      selectedUser: null,
      userAbilityProfile: null
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        const params = new URLSearchParams({
          page: this.currentPage,
          page_size: this.pageSize,
          keyword: this.keyword
        })
        const response = await fetch(`http://localhost:8000/api/admin/users?${params}`)
        const data = await response.json()
        if (data.success) {
          this.users = data.users
          this.total = data.total
        }
      } catch (error) {
        console.error('加载用户失败:', error)
        this.$message.error('加载用户失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.currentPage = 1
      this.loadUsers()
    },
    handlePageChange() {
      this.loadUsers()
    },
    formatDate(dateStr) {
      if (!dateStr) return '暂无'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    },
    async viewUserDetail(user) {
      this.selectedUser = user
      this.showDetailDialog = true
      this.userAbilityProfile = null

      try {
        const response = await fetch(`http://localhost:8000/api/admin/user/${user.id}/ability-profile`)
        const data = await response.json()
        if (data.success) {
          this.userAbilityProfile = data
        }
      } catch (error) {
        console.error('加载能力档案失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.user-management {
  padding: 0;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.section-title i {
  color: #667eea;
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 280px;
}

.refresh-btn {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  border: none !important;
  color: white !important;
}

.refresh-btn:hover {
  background: linear-gradient(135deg, #5a6fd6, #6a4190) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.user-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: white;
}

.user-basic h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #909399;
  min-width: 100px;
}

.info-label i {
  color: #667eea;
}

.info-value {
  font-size: 14px;
  color: #303133;
}

.info-value.highlight {
  font-size: 20px;
  font-weight: bold;
  color: #667eea;
}

.ability-section {
  margin-top: 20px;
}

.ability-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.ability-section h4 i {
  color: #667eea;
}

.ability-info {
  display: flex;
  align-items: center;
  gap: 24px;
}

.ability-score {
  flex-shrink: 0;
}

.score-circle {
  position: relative;
  width: 120px;
  height: 120px;
}

.score-circle svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.score-bg {
  fill: none;
  stroke: #f0f0f0;
  stroke-width: 10;
}

.score-progress {
  fill: none;
  stroke: #667eea;
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dasharray 1s ease;
}

.score-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-value {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #667eea;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.ability-stats {
  flex: 1;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.no-data {
  color: #909399;
  font-size: 14px;
  text-align: center;
  padding: 20px;
}

:deep(.custom-dialog .el-dialog) {
  border-radius: 20px;
}

:deep(.custom-dialog .el-dialog__header) {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 16px;
}

:deep(.el-tag--dark) {
  border: none;
}
</style>
