<template>
  <div class="exam-questions-management">
    <div class="management-header">
      <h2 class="section-title">
        <i class="el-icon-document"></i>
        真题管理
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
        <el-button type="primary" class="add-btn" @click="showAddDialog">
          <i class="el-icon-plus"></i>
          新增真题
        </el-button>
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
        <el-table-column prop="question" label="题目" min-width="300" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag type="primary" size="small" effect="dark">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="answer" label="答案" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="viewQuestion(row)">
              <i class="el-icon-view"></i>
            </el-button>
            <el-button size="small" type="warning" text @click="editQuestion(row)">
              <i class="el-icon-edit"></i>
            </el-button>
            <el-button size="small" type="danger" text @click="deleteQuestion(row)">
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
      v-model="showDialog"
      :title="dialogTitle"
      width="700px"
      class="custom-dialog"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="题目">
          <el-input
            v-model="form.question"
            type="textarea"
            :rows="3"
            placeholder="请输入题目内容"
          />
        </el-form-item>
        <el-form-item label="答案">
          <el-input
            v-model="form.answer"
            type="textarea"
            :rows="4"
            placeholder="请输入参考答案"
          />
        </el-form-item>
        <el-form-item label="解析">
          <el-input
            v-model="form.analysis"
            type="textarea"
            :rows="3"
            placeholder="请输入题目解析"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="请选择分类" class="full-width">
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" class="submit-btn" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showViewDialog"
      title="真题详情"
      width="700px"
      class="custom-dialog"
    >
      <div v-if="selectedQuestion" class="question-detail">
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-question"></i> 题目</div>
          <div class="section-content question-text">{{ selectedQuestion.question }}</div>
        </div>
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-collection-tag"></i> 分类</div>
          <el-tag type="primary" size="small" effect="dark">{{ selectedQuestion.category }}</el-tag>
        </div>
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-check"></i> 答案</div>
          <div class="section-content answer-content">{{ selectedQuestion.answer }}</div>
        </div>
        <div class="detail-section" v-if="selectedQuestion.analysis">
          <div class="section-label"><i class="el-icon-info"></i> 解析</div>
          <div class="section-content analysis-content">{{ selectedQuestion.analysis }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AdminExamQuestions',
  data() {
    return {
      questions: [],
      categories: ['社会现象', '组织管理', '应急应变', '人际关系', '态度观点', '综合分析'],
      loading: false,
      currentPage: 1,
      pageSize: 20,
      total: 0,
      filterCategory: '',
      showDialog: false,
      showViewDialog: false,
      dialogTitle: '新增真题',
      isEdit: false,
      selectedQuestion: null,
      form: {
        id: null,
        question: '',
        answer: '',
        analysis: '',
        category: ''
      }
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
        let url = `http://localhost:8000/api/admin/exam-questions?page=${this.currentPage}&page_size=${this.pageSize}`
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
        console.error('加载真题失败:', error)
        this.$message.error('加载真题失败')
      } finally {
        this.loading = false
      }
    },
    async loadCategories() {
      try {
        const response = await fetch('http://localhost:8000/api/admin/categories')
        const data = await response.json()
        if (data.success && data.exam_categories) {
          this.categories = [...new Set([...this.categories, ...data.exam_categories])]
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
    formatDate(dateStr) {
      if (!dateStr) return '暂无'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    },
    showAddDialog() {
      this.dialogTitle = '新增真题'
      this.isEdit = false
      this.form = {
        id: null,
        question: '',
        answer: '',
        analysis: '',
        category: ''
      }
      this.showDialog = true
    },
    viewQuestion(question) {
      this.selectedQuestion = question
      this.showViewDialog = true
    },
    editQuestion(question) {
      this.dialogTitle = '编辑真题'
      this.isEdit = true
      this.form = {
        id: question.id,
        question: question.question,
        answer: question.answer,
        analysis: question.analysis,
        category: question.category
      }
      this.showDialog = true
    },
    async submitForm() {
      if (!this.form.question || !this.form.answer || !this.form.category) {
        this.$message.warning('请填写完整信息')
        return
      }

      try {
        let url = 'http://localhost:8000/api/admin/exam-questions'
        let method = 'POST'

        if (this.isEdit) {
          url += `/${this.form.id}`
          method = 'PUT'
        }

        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        })

        const data = await response.json()
        if (data.success) {
          this.$message.success(this.isEdit ? '更新成功' : '创建成功')
          this.showDialog = false
          this.loadQuestions()
        } else {
          this.$message.error(data.error || '操作失败')
        }
      } catch (error) {
        console.error('提交失败:', error)
        this.$message.error('操作失败')
      }
    },
    async deleteQuestion(question) {
      try {
        await this.$confirm('确定要删除这道真题吗？此操作不可恢复。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await fetch(`http://localhost:8000/api/admin/exam-questions/${question.id}`, {
          method: 'DELETE'
        })
        const data = await response.json()

        if (data.success) {
          this.$message.success('删除成功')
          this.loadQuestions()
        } else {
          this.$message.error(data.error || '删除失败')
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
.exam-questions-management {
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

.add-btn {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  border: none !important;
  color: white !important;
}

.add-btn:hover {
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

.full-width {
  width: 100%;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  border: none !important;
  color: white !important;
}

.question-detail {
  padding: 10px 0;
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

.answer-content {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.08) 0%, rgba(133, 206, 97, 0.08) 100%);
}

.analysis-content {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.08) 0%, rgba(251, 165, 108, 0.08) 100%);
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
