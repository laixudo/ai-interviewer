<template>
  <div class="interview-tips">
    <div class="tips-header">
      <div class="filter-bar">
        <el-select v-model="selectedCategory" placeholder="全部分类" clearable style="width: 150px" @change="handleFilter">
          <el-option v-for="cat in categories" :key="cat.name" :label="cat.name" :value="cat.name" />
        </el-select>
        <el-select v-model="selectedDifficulty" placeholder="难度筛选" clearable style="width: 120px" @change="handleFilter">
          <el-option label="初级" value="beginner" />
          <el-option label="中级" value="intermediate" />
          <el-option label="高级" value="advanced" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索干货..." style="width: 200px" clearable @input="handleSearch">
          <template #prefix>
            <i class="el-icon-search"></i>
          </template>
        </el-input>
      </div>
    </div>

    <div v-loading="loading" class="tips-content">
      <div v-if="tips.length === 0 && !loading" class="empty-state">
        <i class="el-icon-document"></i>
        <p>暂无面试干货</p>
      </div>

      <div v-else class="tips-grid">
        <div v-for="tip in tips" :key="tip.id" class="tip-card" @click="handleViewTip(tip)">
          <div class="tip-header">
            <el-tag size="small" :type="getDifficultyType(tip.difficulty)">
              {{ getDifficultyText(tip.difficulty) }}
            </el-tag>
            <el-tag size="small" type="info">{{ tip.category }}</el-tag>
          </div>
          <h3 class="tip-title">{{ tip.title }}</h3>
          <p class="tip-summary">{{ tip.summary }}</p>
          <div class="tip-footer">
            <span class="tip-author">
              <i class="el-icon-user"></i> {{ tip.author_name }}
            </span>
            <span class="tip-stats">
              <i class="el-icon-view"></i> {{ tip.view_count }}
              <i class="el-icon-star-off" :class="{ 'is-collected': tip.is_collected }"></i> {{ tip.collect_count }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="total > pageSize" class="pagination">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" :title="currentTip?.title" width="800px" class="tip-dialog">
      <div v-if="currentTip" class="tip-detail">
        <div class="detail-meta">
          <el-tag size="small" :type="getDifficultyType(currentTip.difficulty)">
            {{ getDifficultyText(currentTip.difficulty) }}
          </el-tag>
          <el-tag size="small" type="info">{{ currentTip.category }}</el-tag>
          <span class="meta-text">阅读 {{ currentTip.view_count }} · 收藏 {{ currentTip.collect_count }}</span>
        </div>
        <div class="detail-tags" v-if="currentTip.tags?.length">
          <el-tag v-for="tag in currentTip.tags" :key="tag" size="small" type="warning" class="tag-item">
            {{ tag }}
          </el-tag>
        </div>
        <div class="detail-content" v-html="formatContent(currentTip.content)"></div>
        <div class="detail-actions">
          <el-button type="primary" :icon="currentTip.is_collected ? 'el-icon-star-on' : 'el-icon-star-off'" @click="handleCollect(currentTip)">
            {{ currentTip.is_collected ? '已收藏' : '收藏' }}
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'InterviewTips',
  data() {
    return {
      tips: [],
      categories: [],
      selectedCategory: '',
      selectedDifficulty: '',
      keyword: '',
      loading: false,
      currentPage: 1,
      pageSize: 12,
      total: 0,
      detailVisible: false,
      currentTip: null
    }
  },
  mounted() {
    this.fetchCategories()
    this.fetchTips()
  },
  methods: {
    async fetchCategories() {
      try {
        const response = await fetch('/api/tips/categories')
        const data = await response.json()
        if (data.success) {
          this.categories = data.data
        }
      } catch (error) {
        console.error('获取分类失败:', error)
      }
    },
    async fetchTips() {
      this.loading = true
      try {
        const params = new URLSearchParams({
          page: this.currentPage,
          page_size: this.pageSize
        })
        if (this.selectedCategory) params.append('category', this.selectedCategory)
        if (this.selectedDifficulty) params.append('difficulty', this.selectedDifficulty)
        if (this.keyword) params.append('keyword', this.keyword)

        const response = await fetch(`/api/tips?${params}`)
        const data = await response.json()
        if (data.success) {
          this.tips = data.data
          this.total = data.total
        }
      } catch (error) {
        console.error('获取干货失败:', error)
      } finally {
        this.loading = false
      }
    },
    handleFilter() {
      this.currentPage = 1
      this.fetchTips()
    },
    handleSearch() {
      this.currentPage = 1
      this.fetchTips()
    },
    handlePageChange(page) {
      this.currentPage = page
      this.fetchTips()
    },
    async handleViewTip(tip) {
      try {
        const response = await fetch(`/api/tips/${tip.id}`)
        const data = await response.json()
        if (data.success) {
          this.currentTip = data.data
          this.detailVisible = true
        }
      } catch (error) {
        console.error('获取干货详情失败:', error)
      }
    },
    async handleCollect(tip) {
      const userId = this.getCurrentUserId()
      if (!userId) {
        this.$message.warning('请先登录')
        return
      }
      try {
        const response = await fetch(`/api/tips/${tip.id}/collect?user_id=${userId}`, { method: 'POST' })
        const data = await response.json()
        if (data.success) {
          tip.is_collected = data.is_collected
          tip.collect_count += data.is_collected ? 1 : -1
          this.$message.success(data.is_collected ? '收藏成功' : '取消收藏')
        }
      } catch (error) {
        console.error('收藏失败:', error)
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
    formatContent(content) {
      if (!content) return ''
      return content.replace(/\n/g, '<br>').replace(/#/g, '').replace(/\*\*/g, '<strong>')
    }
  }
}
</script>

<style scoped>
.interview-tips {
  padding: 0;
}

.tips-header {
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.tip-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.tip-card:hover {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.6);
}

.tip-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tip-title {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tip-summary {
  font-size: 13px;
  color: #a0a0c0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12px;
}

.tip-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.tip-stats {
  display: flex;
  gap: 12px;
}

.tip-stats i {
  margin-right: 4px;
}

.is-collected {
  color: #f56c6c;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.tip-dialog :deep(.el-dialog__body) {
  padding: 20px;
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

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag-item {
  margin-right: 0;
}

.detail-content {
  font-size: 14px;
  line-height: 1.8;
  color: #000000;
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.detail-actions {
  display: flex;
  justify-content: center;
}
</style>
