<template>
  <div class="resume-analysis">
    <div class="analysis-header">
      <h3>简历分析</h3>
      <p class="tips">上传简历，获取AI智能分析和优化建议</p>
    </div>

    <div class="analysis-content">
      <div class="upload-section">
        <el-card shadow="hover">
          <div class="upload-area" @click="triggerUpload" v-if="!currentResume">
            <i class="el-icon-upload"></i>
            <p>点击上传简历</p>
            <p class="upload-tip">支持 PDF、Word、图片格式</p>
          </div>
          <div v-else class="resume-info">
            <i class="el-icon-document"></i>
            <div class="resume-details">
              <p class="resume-name">{{ currentResume.file_name }}</p>
              <p class="resume-position">目标岗位: {{ currentResume.target_position || '未指定' }}</p>
            </div>
            <div class="resume-actions">
              <el-button link @click="triggerUpload">重新上传</el-button>
              <el-button type="primary" @click="handleAnalyze">开始分析</el-button>
            </div>
          </div>
          <input type="file" ref="fileInput" @change="handleFileChange" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" style="display: none" />
        </el-card>
      </div>

      <div v-if="analysisResult" class="analysis-result">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>分析报告</span>
              <el-tag :type="getScoreTagType(analysisResult.overall_score)">
                综合评分: {{ analysisResult.overall_score }}分
              </el-tag>
            </div>
          </template>

          <div class="score-grid">
            <div class="score-item">
              <el-progress type="circle" :percentage="analysisResult.completeness_score" :width="80" :stroke-width="8">
                <template #default>
                  <span class="score-value">{{ analysisResult.completeness_score }}</span>
                </template>
              </el-progress>
              <p class="score-label">完整性</p>
            </div>
            <div class="score-item">
              <el-progress type="circle" :percentage="analysisResult.match_score" :width="80" :stroke-width="8" :color="getMatchColor(analysisResult.match_score)">
                <template #default>
                  <span class="score-value">{{ analysisResult.match_score }}</span>
                </template>
              </el-progress>
              <p class="score-label">匹配度</p>
            </div>
            <div class="score-item">
              <el-progress type="circle" :percentage="analysisResult.keyword_score" :width="80" :stroke-width="8" :color="getKeywordColor(analysisResult.keyword_score)">
                <template #default>
                  <span class="score-value">{{ analysisResult.keyword_score }}</span>
                </template>
              </el-progress>
              <p class="score-label">关键词</p>
            </div>
            <div class="score-item">
              <el-progress type="circle" :percentage="analysisResult.quantification_score" :width="80" :stroke-width="8" :color="getQuantColor(analysisResult.quantification_score)">
                <template #default>
                  <span class="score-value">{{ analysisResult.quantification_score }}</span>
                </template>
              </el-progress>
              <p class="score-label">量化程度</p>
            </div>
          </div>

          <div class="summary-section">
            <h4>总体评价</h4>
            <p>{{ analysisResult.summary }}</p>
          </div>
        </el-card>

        <el-card shadow="hover" class="suggestions-card">
          <template #header>
            <span>优化建议</span>
          </template>
          <div v-if="suggestions.length === 0" class="empty-suggestions">
            <p>暂无优化建议</p>
          </div>
          <div v-else class="suggestions-list">
            <div v-for="(suggestion, index) in suggestions" :key="index" class="suggestion-item" :class="suggestion.priority">
              <div class="suggestion-header">
                <el-tag size="small" :type="getPriorityType(suggestion.priority)">
                  {{ getPriorityText(suggestion.priority) }}
                </el-tag>
                <span class="suggestion-dimension">{{ getDimensionText(suggestion.dimension) }}</span>
              </div>
              <p class="suggestion-issue">{{ suggestion.issue }}</p>
              <p class="suggestion-text">{{ suggestion.suggestion }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <div v-if="!currentResume && !analysisResult" class="history-section">
        <h4>历史简历</h4>
        <div v-if="resumeList.length === 0" class="empty-history">
          <p>暂无历史简历</p>
        </div>
        <div v-else class="resume-list">
          <div v-for="resume in resumeList" :key="resume.id" class="resume-item" @click="selectResume(resume)">
            <i class="el-icon-document"></i>
            <div class="resume-item-info">
              <p class="resume-item-name">{{ resume.file_name }}</p>
              <p class="resume-item-date">{{ formatDate(resume.created_at) }}</p>
            </div>
            <el-tag size="small" :type="getStatusType(resume.status)">
              {{ getStatusText(resume.status) }}
            </el-tag>
            <el-button type="danger" size="small" circle icon="el-icon-delete" @click.stop="handleDeleteResume(resume.id)" class="delete-btn"></el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResumeAnalysis',
  data() {
    return {
      currentResume: null,
      resumeList: [],
      analysisResult: null,
      suggestions: []
    }
  },
  mounted() {
    this.fetchResumes()
  },
  methods: {
    triggerUpload() {
      this.$refs.fileInput.click()
    },
    async handleFileChange(e) {
      const file = e.target.files[0]
      if (!file) return

      const userId = this.getCurrentUserId()
      if (!userId) {
        this.$message.warning('请先登录')
        return
      }

      try {
        const response = await fetch('/api/resumes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            file_name: file.name,
            target_position: ''
          })
        })
        const data = await response.json()
        if (data.success) {
          this.$message.success('上传成功')
          this.currentResume = {
            id: data.resume_id,
            file_name: file.name,
            target_position: ''
          }
          this.fetchResumes()
        }
      } catch (error) {
        console.error('上传失败:', error)
        this.$message.error('上传失败')
      }
    },
    async fetchResumes() {
      const userId = this.getCurrentUserId()
      if (!userId) return

      try {
        const response = await fetch(`/api/resumes?user_id=${userId}`)
        const data = await response.json()
        if (data.success) {
          this.resumeList = data.data
        }
      } catch (error) {
        console.error('获取简历列表失败:', error)
      }
    },
    async selectResume(resume) {
      try {
        const response = await fetch(`/api/resumes/${resume.id}`)
        const data = await response.json()
        if (data.success) {
          this.currentResume = data.data
          if (data.data.analysis_result) {
            this.analysisResult = data.data.analysis_result
            this.suggestions = data.data.suggestions || []
          }
        }
      } catch (error) {
        console.error('获取简历详情失败:', error)
      }
    },
    async handleAnalyze() {
      if (!this.currentResume?.id) return

      try {
        const response = await fetch(`/api/resumes/${this.currentResume.id}/analyze`, { method: 'POST' })
        const data = await response.json()
        if (data.success) {
          this.analysisResult = data.data
          this.$message.success('分析完成')
          this.fetchResumes()
          this.selectResume({ id: this.currentResume.id })
        }
      } catch (error) {
        console.error('分析失败:', error)
        this.$message.error('分析失败')
      }
    },
    getCurrentUserId() {
      const userData = localStorage.getItem('userData')
      if (userData) {
        const user = JSON.parse(userData)
        return user.id || 0
      }
      return 0
    },
    getScoreTagType(score) {
      if (score >= 80) return 'success'
      if (score >= 60) return 'warning'
      return 'danger'
    },
    getMatchColor(score) {
      if (score >= 80) return '#67c23a'
      if (score >= 60) return '#e6a23c'
      return '#f56c6c'
    },
    getKeywordColor(score) {
      if (score >= 80) return '#67c23a'
      if (score >= 60) return '#e6a23c'
      return '#f56c6c'
    },
    getQuantColor(score) {
      if (score >= 80) return '#67c23a'
      if (score >= 60) return '#e6a23c'
      return '#f56c6c'
    },
    getPriorityType(priority) {
      const map = { high: 'danger', medium: 'warning', low: 'info' }
      return map[priority] || 'info'
    },
    getPriorityText(priority) {
      const map = { high: '高优先级', medium: '中优先级', low: '低优先级' }
      return map[priority] || priority
    },
    getDimensionText(dimension) {
      const map = {
        completeness: '完整性',
        match: '匹配度',
        keyword: '关键词',
        quantification: '量化程度',
        expression: '表达质量'
      }
      return map[dimension] || dimension
    },
    getStatusType(status) {
      const map = { uploaded: 'info', analyzed: 'success', optimized: 'primary' }
      return map[status] || 'info'
    },
    getStatusText(status) {
      const map = { uploaded: '待分析', analyzed: '已分析', optimized: '已优化' }
      return map[status] || status
    },
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString('zh-CN')
    },
    async handleDeleteResume(resumeId) {
      try {
        const confirmed = await this.$confirm('确定要删除这份简历吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        if (confirmed) {
          const response = await fetch(`/api/resumes/${resumeId}`, { method: 'DELETE' })
          const data = await response.json()
          if (data.success) {
            this.$message.success('删除成功')
            this.fetchResumes()
            if (this.currentResume?.id === resumeId) {
              this.currentResume = null
              this.analysisResult = null
              this.suggestions = []
            }
          } else {
            this.$message.error('删除失败')
          }
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          this.$message.error('删除失败')
        }
      }
    }
  }
}
</script>

<style scoped>
.resume-analysis {
  padding: 0;
}

.analysis-header {
  margin-bottom: 20px;
}

.analysis-header h3 {
  font-size: 18px;
  color: #ffffff;
  margin-bottom: 4px;
}

.tips {
  font-size: 13px;
  color: #909399;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-area {
  text-align: center;
  padding: 40px 20px;
  cursor: pointer;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.upload-area i {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-area p {
  margin: 0;
  color: #606266;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.resume-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.resume-info i {
  font-size: 36px;
  color: #409eff;
}

.resume-details {
  flex: 1;
}

.resume-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.resume-position {
  font-size: 13px;
  color: #909399;
}

.resume-actions {
  display: flex;
  gap: 8px;
}

.analysis-result {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.score-item {
  text-align: center;
}

.score-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.score-label {
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
}

.summary-section {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-section h4 {
  margin-bottom: 8px;
  font-size: 14px;
  color: #303133;
}

.summary-section p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.suggestions-card {
  margin-top: 0;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.suggestion-item.high {
  border-left-color: #f56c6c;
}

.suggestion-item.medium {
  border-left-color: #e6a23c;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.suggestion-dimension {
  font-size: 13px;
  color: #909399;
}

.suggestion-issue {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.suggestion-text {
  font-size: 13px;
  color: #606266;
  margin: 0;
}

.history-section {
  margin-top: 24px;
}

.history-section h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 16px;
}

.empty-history,
.empty-suggestions {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.resume-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resume-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.resume-item:hover {
  background: #f5f7fa;
}

.resume-item i {
  font-size: 28px;
  color: #409eff;
}

.resume-item-info {
  flex: 1;
}

.resume-item-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.resume-item-date {
  font-size: 12px;
  color: #909399;
}

.delete-btn {
  margin-left: 8px;
}
</style>
