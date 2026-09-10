<template>
  <div class="interview-management">
    <div class="page-header">
      <h2 class="page-title">面试记录</h2>
      <el-button type="primary" @click="$emit('refresh')">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filterUserId" placeholder="筛选用户" clearable style="width: 200px">
        <el-option v-for="user in users" :key="user.id" :label="user.username" :value="user.id" />
      </el-select>
    </div>

    <div class="interview-table">
      <el-table :data="filteredInterviews" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="username" label="用户名" width="100" />
        <el-table-column prop="position" label="面试岗位" min-width="180" show-overflow-tooltip />
        <el-table-column prop="job_type" label="岗位类型" width="120" />
        <el-table-column prop="experience" label="经验要求" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="面试记录详情" width="800px" class="interview-dialog">
      <div v-if="currentInterview" class="interview-detail">
        <div class="detail-header">
          <h3>{{ currentInterview.position }}</h3>
          <el-tag :type="currentInterview.status === 'completed' ? 'success' : 'warning'">
            {{ currentInterview.status === 'completed' ? '已完成' : '进行中' }}
          </el-tag>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <label>用户</label>
            <span>{{ currentInterview.username }}</span>
          </div>
          <div class="detail-item">
            <label>面试官角色</label>
            <span>{{ currentInterview.interviewer_role || '面试官' }}</span>
          </div>
          <div class="detail-item">
            <label>岗位类型</label>
            <span>{{ currentInterview.job_type || '未设置' }}</span>
          </div>
          <div class="detail-item">
            <label>经验要求</label>
            <span>{{ currentInterview.experience || '未设置' }}</span>
          </div>
          <div class="detail-item">
            <label>面试环节</label>
            <span>{{ currentInterview.round || '未设置' }}</span>
          </div>
          <div class="detail-item">
            <label>时长</label>
            <span>{{ currentInterview.duration }} 分钟</span>
          </div>
          <div class="detail-item">
            <label>目标公司</label>
            <span>{{ currentInterview.target_company || '未设置' }}</span>
          </div>
          <div class="detail-item full-width">
            <label>创建时间</label>
            <span>{{ currentInterview.created_at }}</span>
          </div>
        </div>

        <div v-if="currentInterview.resume_text" class="detail-section">
          <h4>简历信息</h4>
          <p class="resume-content">{{ currentInterview.resume_text }}</p>
        </div>

        <div v-if="chatMessages.length > 0" class="detail-section">
          <h4>面试对话 ({{ chatMessages.length }}条)</h4>
          <div class="messages-list">
            <div v-for="(msg, index) in chatMessages" :key="index"
                 :class="['message-item', msg.sender === 'ai' ? 'message-ai' : 'message-user']">
              <div class="message-header">
                <span class="message-sender">{{ msg.sender === 'ai' ? '面试官' : '候选人' }}</span>
                <span class="message-time">{{ formatTime(msg.created_at) }}</span>
              </div>
              <div class="message-content">{{ msg.content }}</div>
            </div>
          </div>
        </div>

        <div v-if="evaluationReport" class="detail-section">
          <h4>评估报告</h4>
          <div class="report-content">
            <div class="report-score">
              <span class="score-label">综合评分:</span>
              <span class="score-value">{{ evaluationReport.overall_score }}分</span>
              <el-tag :type="getScoreTagType(evaluationReport.overall_score)" size="small">
                {{ evaluationReport.overall_level }}
              </el-tag>
            </div>
            <div v-if="evaluationReport.content_evaluation" class="report-item">
              <label>内容评价:</label>
              <div v-if="isJsonString(evaluationReport.content_evaluation)" class="evaluation-details">
                <div v-for="(item, key) in parseJson(evaluationReport.content_evaluation)" :key="key" class="eval-sub-item">
                  <span class="eval-label">{{ getEvalLabel(key) }}:</span>
                  <span>{{ item.comment || item }}</span>
                  <span v-if="item.score" class="eval-score"> ({{ item.score }}分)</span>
                </div>
              </div>
              <p v-else>{{ evaluationReport.content_evaluation }}</p>
            </div>
            <div v-if="evaluationReport.expression_evaluation" class="report-item">
              <label>表达评价:</label>
              <div v-if="isJsonString(evaluationReport.expression_evaluation)" class="evaluation-details">
                <div v-for="(item, key) in parseJson(evaluationReport.expression_evaluation)" :key="key" class="eval-sub-item">
                  <span class="eval-label">{{ getEvalLabel(key) }}:</span>
                  <span>{{ item.comment || item }}</span>
                  <span v-if="item.score" class="eval-score"> ({{ item.score }}分)</span>
                </div>
              </div>
              <p v-else>{{ evaluationReport.expression_evaluation }}</p>
            </div>
            <div v-if="evaluationReport.highlights" class="report-item">
              <label>亮点:</label>
              <div v-if="isJsonString(evaluationReport.highlights)" class="highlights-list">
                <el-tag v-for="(highlight, idx) in parseJson(evaluationReport.highlights)" :key="idx" type="success" size="small" class="highlight-tag">
                  {{ highlight }}
                </el-tag>
              </div>
              <p v-else>{{ evaluationReport.highlights }}</p>
            </div>
            <div v-if="evaluationReport.suggestions" class="report-item">
              <label>建议:</label>
              <div v-if="isJsonString(evaluationReport.suggestions)" class="suggestions-list">
                <div v-for="(suggestion, idx) in parseJson(evaluationReport.suggestions)" :key="idx" class="suggestion-item">
                  {{ idx + 1 }}. {{ suggestion }}
                </div>
              </div>
              <p v-else>{{ evaluationReport.suggestions }}</p>
            </div>
          </div>
        </div>

        <div v-if="improvementPlan" class="detail-section">
          <h4>改进计划</h4>
          <div class="plan-content">
            <div v-if="improvementPlan.weaknesses" class="plan-item">
              <label>需要改进的地方:</label>
              <div v-if="isJsonString(improvementPlan.weaknesses)" class="suggestions-list">
                <div v-for="(item, idx) in parseJson(improvementPlan.weaknesses)" :key="idx" class="suggestion-item">
                  {{ idx + 1 }}. {{ item }}
                </div>
              </div>
              <p v-else>{{ improvementPlan.weaknesses }}</p>
            </div>
            <div v-if="improvementPlan.suggestions" class="plan-item">
              <label>建议:</label>
              <div v-if="isJsonString(improvementPlan.suggestions)" class="suggestions-list">
                <div v-for="(item, idx) in parseJson(improvementPlan.suggestions)" :key="idx" class="suggestion-item">
                  {{ idx + 1 }}. {{ item }}
                </div>
              </div>
              <p v-else>{{ improvementPlan.suggestions }}</p>
            </div>
            <div v-if="improvementPlan.resources" class="plan-item">
              <label>学习资源:</label>
              <div v-if="isJsonString(improvementPlan.resources)" class="suggestions-list">
                <div v-for="(item, idx) in parseJson(improvementPlan.resources)" :key="idx" class="suggestion-item">
                  {{ idx + 1 }}. {{ item }}
                </div>
              </div>
              <p v-else>{{ improvementPlan.resources }}</p>
            </div>
            <div v-if="improvementPlan.learning_plan" class="plan-item">
              <label>学习计划:</label>
              <div v-if="isJsonString(improvementPlan.learning_plan)" class="learning-plan-list">
                <div v-for="(week, idx) in parseJson(improvementPlan.learning_plan)" :key="idx" class="week-plan">
                  <div class="week-title">{{ week.title }} (第{{ week.week }}周)</div>
                  <ul class="week-tasks">
                    <li v-for="(task, taskIdx) in week.tasks" :key="taskIdx">{{ task }}</li>
                  </ul>
                </div>
              </div>
              <p v-else>{{ improvementPlan.learning_plan }}</p>
            </div>
          </div>
        </div>

        <div v-if="!chatMessages.length && !evaluationReport && !improvementPlan" class="no-data">
          <p>暂无面试详情数据</p>
        </div>
      </div>
      <div v-else-if="detailLoading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { Refresh, Loading } from '@element-plus/icons-vue'

export default {
  name: 'InterviewManagement',
  components: { Refresh, Loading },
  props: {
    interviews: {
      type: Array,
      default: () => []
    },
    users: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  data() {
    return {
      filterUserId: null,
      dialogVisible: false,
      currentInterview: null,
      detailLoading: false,
      chatMessages: [],
      evaluationReport: null,
      improvementPlan: null
    }
  },
  computed: {
    filteredInterviews() {
      if (!this.filterUserId) return this.interviews
      return this.interviews.filter(interview => interview.user_id === this.filterUserId)
    },
    users() {
      return [...new Map(this.interviews.map(i => [i.user_id, { id: i.user_id, username: i.username || `用户${i.user_id}` }])).values()]
    }
  },
  methods: {
    async handleView(row) {
      this.currentInterview = null
      this.chatMessages = []
      this.evaluationReport = null
      this.improvementPlan = null
      this.detailLoading = true
      this.dialogVisible = true

      try {
        const response = await fetch(`/api/admin/interview-detail?interview_id=${row.id}`)
        const data = await response.json()

        if (data.success) {
          this.currentInterview = data.interview
          this.chatMessages = data.messages || []
          this.evaluationReport = data.report
          this.improvementPlan = data.plan
        } else {
          this.$message.error(data.error || '获取详情失败')
          this.dialogVisible = false
        }
      } catch (error) {
        this.$message.error('获取详情失败')
        this.dialogVisible = false
      } finally {
        this.detailLoading = false
      }
    },
    formatTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getScoreTagType(score) {
      if (score >= 80) return 'success'
      if (score >= 60) return 'warning'
      return 'danger'
    },
    onTopScroll(e) {
      const tableBody = this.tableWrapper?.querySelector('.el-table__body-wrapper')
      if (tableBody) {
        tableBody.scrollLeft = e.target.scrollLeft
      }
    },
    onTableScroll(e) {
      if (this.topScrollbar) {
        this.topScrollbar.scrollLeft = e.target.scrollLeft
      }
    },
    isJsonString(str) {
      if (!str) return false
      if (typeof str !== 'string') return false
      try {
        const parsed = JSON.parse(str)
        return typeof parsed === 'object' && parsed !== null
      } catch {
        return false
      }
    },
    parseJson(str) {
      if (!str) return []
      if (typeof str === 'object') return str
      try {
        return JSON.parse(str)
      } catch {
        return []
      }
    },
    getEvalLabel(key) {
      const labels = {
        technical: '技术知识',
        logic: '逻辑思维',
        communication: '沟通能力',
        clarity: '表达清晰度',
        confidence: '自信度',
        speed: '语速'
      }
      return labels[key] || key
    },
    async handleDelete(row) {
      try {
        await this.$confirm('确定要删除这条面试记录吗？', '删除确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await fetch(`/api/admin/interviews/${row.id}`, {
          method: 'DELETE'
        })

        if (response.ok) {
          this.$message.success('删除成功')
          this.$emit('refresh')
        } else {
          const data = await response.json()
          throw new Error(data.error || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error(error.message || '删除失败')
        }
      }
    }
  }
}
</script>

<style scoped>
.interview-management {
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

.filter-bar {
  margin-bottom: 20px;
}

.interview-table {
  margin-top: 16px;
}

.interview-detail {
  padding: 10px 0;
  max-height: 70vh;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 13px;
  color: #909399;
}

.detail-item span {
  font-size: 15px;
  color: #303133;
}

.detail-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.detail-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.resume-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  margin: 0;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 8px;
}

.message-item {
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 85%;
}

.message-ai {
  background: #f0f9eb;
  align-self: flex-start;
}

.message-user {
  background: #ecf5ff;
  align-self: flex-end;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.message-sender {
  font-weight: 600;
  color: #606266;
}

.message-time {
  color: #909399;
}

.message-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-score {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.score-label {
  font-size: 14px;
}

.score-value {
  font-size: 24px;
  font-weight: bold;
}

.report-item {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
}

.report-item label {
  font-size: 13px;
  color: #909399;
  display: block;
  margin-bottom: 8px;
}

.report-item p {
  font-size: 14px;
  color: #303133;
  margin: 0;
  line-height: 1.6;
}

.evaluation-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.eval-sub-item {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.eval-label {
  font-weight: 600;
  color: #409eff;
  margin-right: 8px;
}

.eval-score {
  color: #67c23a;
  font-weight: 500;
}

.highlights-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.highlight-tag {
  margin: 0;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.suggestion-item {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.learning-plan-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.week-plan {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
}

.week-title {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.week-tasks {
  margin: 0;
  padding-left: 20px;
}

.week-tasks li {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.plan-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-item {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
}

.plan-item label {
  font-size: 13px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.plan-item p {
  font-size: 14px;
  color: #303133;
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.no-data p {
  margin: 0;
  font-size: 14px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
  gap: 12px;
}

.loading-container .el-icon {
  font-size: 32px;
}
</style>
