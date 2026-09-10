<template>
  <div class="selected-questions-management">
    <div class="management-header">
      <h2 class="section-title">
        <i class="el-icon-check-circle"></i>
        精选题库
      </h2>
      <div class="header-actions">
        <el-select
          v-model="filterCategory"
          placeholder="筛选分类"
          clearable
          class="filter-select"
          @change="handleFilterChange"
        >
          <el-option
            v-for="cat in categories"
            :key="cat"
            :label="cat"
            :value="cat"
          />
        </el-select>
      </div>
    </div>

    <div class="table-container">
      <el-table
        :data="questions"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '单选' ? 'primary' : 'success'" size="small" effect="dark">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question" label="题目" min-width="300" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag type="warning" size="small" effect="dark">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="correct_answer" label="正确答案" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="danger" effect="plain" size="large">{{ row.correct_answer }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="viewQuestion(row)">
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
      v-model="showViewDialog"
      title="题目详情"
      width="700px"
      class="custom-dialog"
    >
      <div v-if="selectedQuestion" class="question-detail">
        <div class="detail-header">
          <div class="detail-icon">
            <i class="el-icon-question-fill"></i>
          </div>
          <div class="detail-title">
            <h3>{{ selectedQuestion.category }}</h3>
            <el-tag :type="selectedQuestion.type === '单选' ? 'primary' : 'success'" size="small" effect="dark">
              {{ selectedQuestion.type }}
            </el-tag>
          </div>
        </div>
        <el-divider />
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-question"></i> 题目</div>
          <div class="section-content question-text">{{ selectedQuestion.question }}</div>
        </div>
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-tickets"></i> 选项</div>
          <div class="options-list">
            <div
              v-for="(opt, index) in parseOptions(selectedQuestion.options)"
              :key="index"
              class="option-item"
              :class="{ correct: opt.charAt(0) === selectedQuestion.correct_answer }"
            >
              <span class="option-marker">{{ opt.charAt(0) }}</span>
              <span class="option-text">{{ opt.substring(2) }}</span>
              <i v-if="opt.charAt(0) === selectedQuestion.correct_answer" class="el-icon-check correct-icon"></i>
            </div>
          </div>
        </div>
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-info"></i> 解析</div>
          <div class="section-content explanation-content">{{ selectedQuestion.explanation || '暂无解析' }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AdminSelectedQuestions',
  data() {
    return {
      questions: [],
      categories: ['综合分析', '组织协调', '应急应变', '言语表达', '项目经验', '技术能力'],
      loading: false,
      currentPage: 1,
      pageSize: 20,
      total: 0,
      filterCategory: '',
      showViewDialog: false,
      selectedQuestion: null
    }
  },
  mounted() {
    this.loadQuestions()
    this.loadCategories()
  },
  methods: {
    async loadQuestions() {
      this.loading = true
      try {
        let url = `http://localhost:8000/api/admin/selected-questions?page=${this.currentPage}&page_size=${this.pageSize}`
        if (this.filterCategory) {
          url += `&category=${encodeURIComponent(this.filterCategory)}`
        }
        const response = await fetch(url)
        const data = await response.json()
        if (data.success) {
          this.questions = data.questions
          this.total = data.total
        }
      } catch (error) {
        console.error('加载精选题库失败:', error)
        this.$message.error('加载精选题库失败')
      } finally {
        this.loading = false
      }
    },
    async loadCategories() {
      try {
        const response = await fetch('http://localhost:8000/api/admin/categories')
        const data = await response.json()
        if (data.success && data.selected_categories) {
          this.categories = [...new Set([...this.categories, ...data.selected_categories])]
        }
      } catch (error) {
        console.error('加载分类失败:', error)
      }
    },
    handleFilterChange() {
      this.currentPage = 1
      this.loadQuestions()
    },
    handlePageChange() {
      this.loadQuestions()
    },
    parseOptions(optionsStr) {
      try {
        if (typeof optionsStr === 'string') {
          return JSON.parse(optionsStr)
        }
        return optionsStr || []
      } catch {
        return []
      }
    },
    viewQuestion(question) {
      this.selectedQuestion = question
      this.showViewDialog = true
    }
  }
}
</script>

<style scoped>
.selected-questions-management {
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

.question-detail {
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
  background: linear-gradient(135deg, #f6d365, #fda085);
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

.detail-section {
  margin-bottom: 20px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.section-label i {
  color: #667eea;
}

.section-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  padding: 12px;
  border-radius: 10px;
  background: #f8f9ff;
}

.question-text {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 10px;
  border: 2px solid #f0f0f0;
  transition: all 0.3s ease;
}

.option-item:hover {
  border-color: #e4e7ed;
}

.option-item.correct {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(133, 206, 97, 0.1) 100%);
  border-color: #67C23A;
}

.option-marker {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.option-item.correct .option-marker {
  background: linear-gradient(135deg, #67C23A, #85CE61);
}

.option-text {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.correct-icon {
  color: #67C23A;
  font-size: 20px;
  font-weight: bold;
}

.explanation-content {
  background: linear-gradient(135deg, rgba(246, 211, 101, 0.15) 0%, rgba(253, 160, 133, 0.15) 100%);
  border-left: 4px solid #f6d365;
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
