<template>
  <div class="ai-recommend">
    <div class="recommend-header">
      <h3>AI智能推荐</h3>
      <p class="tips">根据您的能力档案和面试记录，智能推荐学习内容</p>
    </div>

    <div v-loading="loading" class="recommend-content">
      <el-empty v-if="!loading && !hasData" description="暂无推荐数据">
        <el-button type="primary" @click="fetchRecommendations">刷新推荐</el-button>
      </el-empty>

      <div v-else class="recommend-sections">
        <el-card shadow="hover" class="recommend-section">
          <template #header>
            <div class="section-header">
              <span><i class="el-icon-document"></i> 推荐面试干货</span>
              <el-button link @click="$router.push('/prep-center?tab=tips')">查看更多</el-button>
            </div>
          </template>
          <div v-if="recommendations.tips?.length" class="recommend-list">
            <div v-for="tip in recommendations.tips" :key="tip.id" class="recommend-item" @click="handleViewTip(tip)">
              <div class="item-info">
                <el-tag size="small" :type="getDifficultyType(tip.difficulty)">{{ getDifficultyText(tip.difficulty) }}</el-tag>
                <h4>{{ tip.title }}</h4>
                <p>{{ tip.summary }}</p>
              </div>
            </div>
          </div>
          <div v-else class="empty-section">暂无推荐干货</div>
        </el-card>

        <el-card shadow="hover" class="recommend-section">
          <template #header>
            <div class="section-header">
              <span><i class="el-icon-question"></i> 推荐练习题目</span>
              <el-button link @click="$router.push('/question-bank')">查看更多</el-button>
            </div>
          </template>
          <div v-if="recommendations.questions?.length" class="recommend-list">
            <div v-for="q in recommendations.questions" :key="q.id" class="recommend-item">
              <div class="item-info">
                <el-tag size="small" type="info">{{ q.category }}</el-tag>
                <h4>{{ q.question }}</h4>
                <p>{{ q.analysis?.substring(0, 60) }}...</p>
              </div>
            </div>
          </div>
          <div v-else class="empty-section">暂无推荐题目</div>
        </el-card>

        <el-card shadow="hover" class="recommend-section">
          <template #header>
            <div class="section-header">
              <span><i class="el-icon-notebook-2"></i> 优秀简历参考</span>
              <el-button link @click="$router.push('/prep-center?tab=resume')">查看更多</el-button>
            </div>
          </template>
          <div v-if="recommendations.reference_resumes?.length" class="reference-list">
            <div v-for="resume in recommendations.reference_resumes" :key="resume.id" class="reference-item">
              <div class="reference-info">
                <h4>{{ resume.title }}</h4>
                <div class="reference-tags">
                  <el-tag size="small">{{ resume.industry }}</el-tag>
                  <el-tag size="small" type="info">{{ resume.position }}</el-tag>
                </div>
                <p v-if="resume.highlights" class="reference-highlights">{{ formatHighlights(resume.highlights) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="empty-section">暂无简历参考</div>
        </el-card>

        <div class="ability-summary" v-if="abilitySummary">
          <el-card shadow="hover">
            <template #header>
              <span><i class="el-icon-user"></i> 能力档案摘要</span>
            </template>
            <div class="ability-info">
              <div class="ability-item">
                <span class="ability-label">面试次数:</span>
                <span class="ability-value">{{ abilitySummary.interviewCount }} 次</span>
              </div>
              <div class="ability-item">
                <span class="ability-label">平均分数:</span>
                <span class="ability-value">{{ abilitySummary.avgScore }} 分</span>
              </div>
              <div class="ability-item">
                <span class="ability-label">能力等级:</span>
                <el-tag :type="getLevelType(abilitySummary.level)" size="small">{{ abilitySummary.level }}</el-tag>
              </div>
            </div>
            <div class="ability-tip">
              <i class="el-icon-info"></i>
              <span>基于您的能力档案，我们为您推荐了以上内容</span>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <el-dialog v-model="showTipDialog" :title="currentTip?.title" width="700px">
      <div v-if="currentTip" class="tip-detail">
        <div class="detail-meta">
          <el-tag size="small" :type="getDifficultyType(currentTip.difficulty)">{{ getDifficultyText(currentTip.difficulty) }}</el-tag>
          <el-tag size="small" type="info">{{ currentTip.category }}</el-tag>
          <span class="meta-text">阅读 {{ currentTip.view_count }} · 收藏 {{ currentTip.collect_count }}</span>
        </div>
        <div class="detail-content" v-html="formatContent(currentTip.content)"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AIRecommend',
  data() {
    return {
      recommendations: {},
      abilitySummary: null,
      loading: false,
      hasData: false,
      showTipDialog: false,
      currentTip: null
    }
  },
  mounted() {
    this.fetchRecommendations()
  },
  methods: {
    async fetchRecommendations() {
      const userId = this.getCurrentUserId()
      if (!userId) {
        this.$message.warning('请先登录')
        return
      }

      this.loading = true
      try {
        const [recResponse, abilityResponse] = await Promise.all([
          fetch(`/api/recommendations?user_id=${userId}&limit=5`),
          fetch(`/api/admin/user/${userId}/ability-profile`)
        ])

        const recData = await recResponse.json()
        if (recData.success) {
          this.recommendations = recData.data
          this.hasData = recData.data.tips?.length > 0 ||
                        recData.data.questions?.length > 0 ||
                        recData.data.reference_resumes?.length > 0
        }

        const abilityData = await abilityResponse.json()
        if (abilityData.success) {
          this.abilitySummary = {
            interviewCount: abilityData.interviewCount || 0,
            avgScore: abilityData.avgScore || 0,
            level: abilityData.level || '未知'
          }
        }
      } catch (error) {
        console.error('获取推荐失败:', error)
      } finally {
        this.loading = false
      }
    },
    async handleViewTip(tip) {
      try {
        const response = await fetch(`/api/tips/${tip.id}`)
        const data = await response.json()
        if (data.success) {
          this.currentTip = data.data
          this.showTipDialog = true
        }
      } catch (error) {
        console.error('获取干货详情失败:', error)
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
    getDifficultyType(difficulty) {
      const map = { beginner: 'success', intermediate: 'warning', advanced: 'danger' }
      return map[difficulty] || 'info'
    },
    getDifficultyText(difficulty) {
      const map = { beginner: '初级', intermediate: '中级', advanced: '高级' }
      return map[difficulty] || difficulty
    },
    getLevelType(level) {
      if (!level) return 'info'
      if (level.includes('高级') || level.includes('优秀')) return 'success'
      if (level.includes('中级')) return 'warning'
      return 'info'
    },
    formatHighlights(highlights) {
      if (!highlights) return ''
      if (typeof highlights === 'string') {
        try {
          highlights = JSON.parse(highlights)
        } catch (e) {
          return highlights
        }
      }
      if (Array.isArray(highlights)) {
        return highlights.join('、')
      }
      return String(highlights)
    },
    formatContent(content) {
      if (!content) return ''
      return content.replace(/\n/g, '<br>').replace(/#/g, '').replace(/\*\*/g, '<strong>')
    }
  }
}
</script>

<style scoped>
.ai-recommend {
  padding: 0;
}

.recommend-header {
  margin-bottom: 20px;
}

.recommend-header h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 4px;
}

.tips {
  font-size: 13px;
  color: #909399;
}

.recommend-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommend-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.recommend-item:hover {
  background: #ecf5ff;
}

.item-info h4 {
  margin: 8px 0 4px 0;
  font-size: 14px;
  color: #303133;
}

.item-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.reference-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reference-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.reference-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.reference-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.reference-highlights {
  margin: 0;
  font-size: 12px;
  color: #606266;
}

.empty-section {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.ability-summary {
  margin-top: 20px;
}

.ability-info {
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
}

.ability-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ability-label {
  font-size: 14px;
  color: #606266;
}

.ability-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.ability-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f0f9eb;
  border-radius: 8px;
  font-size: 13px;
  color: #67c23a;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.meta-text {
  font-size: 13px;
  color: #909399;
  margin-left: 8px;
}

.detail-content {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
</style>
