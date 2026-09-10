<template>
  <div class="interview-management">
    <div class="management-header">
      <h2 class="section-title">
        <i class="el-icon-chat-dot-round"></i>
        面试记录管理
      </h2>
      <div class="header-actions">
        <el-select
          v-model="filterUserId"
          placeholder="筛选用户"
          clearable
          class="filter-select"
          @change="handleFilterChange"
        >
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.username"
            :value="user.id"
          />
        </el-select>
        <el-button type="primary" class="refresh-btn" @click="loadInterviews">
          <i class="el-icon-refresh"></i>
          刷新
        </el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table
        :data="interviews"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="position" label="岗位" min-width="150" />
        <el-table-column prop="round_info" label="面试轮次" width="100" />
        <el-table-column prop="duration" label="时长" width="100">
          <template #default="{ row }">
            {{ row.duration ? `${row.duration}分钟` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="viewInterviewDetail(row)">
              <i class="el-icon-view"></i>
              查看
            </el-button>
            <el-button size="small" type="danger" text @click="deleteInterview(row)">
              <i class="el-icon-delete"></i>
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
      title="面试详情"
      width="700px"
      class="custom-dialog"
    >
      <div v-if="selectedInterview" class="interview-detail">
        <div class="detail-header">
          <div class="detail-icon">
            <i class="el-icon-chat-dot-round"></i>
          </div>
          <div class="detail-title">
            <h3>{{ selectedInterview.position || '面试记录' }}</h3>
            <el-tag :type="getStatusType(selectedInterview.status)" size="small" effect="dark">
              {{ getStatusText(selectedInterview.status) }}
            </el-tag>
          </div>
        </div>
        <el-divider />
        <div class="detail-grid">
          <div class="detail-item">
            <span class="item-label"><i class="el-icon-user"></i> 用户名</span>
            <span class="item-value">{{ selectedInterview.username }}</span>
          </div>
          <div class="detail-item">
            <span class="item-label"><i class="el-icon-time"></i> 时长</span>
            <span class="item-value">{{ selectedInterview.duration ? `${selectedInterview.duration}分钟` : '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="item-label"><i class="el-icon-date"></i> 面试轮次</span>
            <span class="item-value">{{ selectedInterview.round_info || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="item-label"><i class="el-icon-clock"></i> 创建时间</span>
            <span class="item-value">{{ formatDate(selectedInterview.created_at) }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AdminInterviewManagement',
  data() {
    return {
      interviews: [],
      users: [],
      loading: false,
      currentPage: 1,
      pageSize: 20,
      total: 0,
      filterUserId: null,
      showDetailDialog: false,
      selectedInterview: null
    }
  },
  mounted() {
    this.loadInterviews()
    this.loadUsers()
  },
  methods: {
    async loadInterviews() {
      this.loading = true
      try {
        let url = `http://localhost:8000/api/admin/interviews?page=${this.currentPage}&page_size=${this.pageSize}`
        if (this.filterUserId) {
          url += `&user_id=${this.filterUserId}`
        }
        const response = await fetch(url)
        const data = await response.json()
        if (data.success) {
          this.interviews = data.interviews
          this.total = data.total
        }
      } catch (error) {
        console.error('加载面试记录失败:', error)
        this.$message.error('加载面试记录失败')
      } finally {
        this.loading = false
      }
    },
    async loadUsers() {
      try {
        const response = await fetch('http://localhost:8000/api/admin/users?page=1&page_size=1000')
        const data = await response.json()
        if (data.success) {
          this.users = data.users
        }
      } catch (error) {
        console.error('加载用户列表失败:', error)
      }
    },
    handleFilterChange() {
      this.currentPage = 1
      this.loadInterviews()
    },
    handlePageChange() {
      this.loadInterviews()
    },
    getStatusType(status) {
      const map = {
        'pending': 'warning',
        'in_progress': 'primary',
        'completed': 'success',
        'cancelled': 'info'
      }
      return map[status] || 'info'
    },
    getStatusText(status) {
      const map = {
        'pending': '待开始',
        'in_progress': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return map[status] || status
    },
    formatDate(dateStr) {
      if (!dateStr) return '暂无'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    },
    viewInterviewDetail(interview) {
      this.selectedInterview = interview
      this.showDetailDialog = true
    },
    async deleteInterview(interview) {
      try {
        await this.$confirm('确定要删除这条面试记录吗？此操作不可恢复。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await fetch(`http://localhost:8000/api/admin/interviews/${interview.id}`, {
          method: 'DELETE'
        })
        const data = await response.json()

        if (data.success) {
          this.$message.success('删除成功')
          this.loadInterviews()
        } else {
          this.$message.error(data.error || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除面试记录失败:', error)
          this.$message.error('删除失败')
        }
      }
    }
  }
}
</script>

<style scoped>
.interview-management {
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

.filter-select {
  width: 180px;
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

.interview-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.detail-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.detail-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.item-label i {
  color: #667eea;
}

.item-value {
  font-size: 15px;
  color: #303133;
  font-weight: 500;
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
