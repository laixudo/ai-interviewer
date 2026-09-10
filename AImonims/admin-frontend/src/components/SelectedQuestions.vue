<template>
  <div class="selected-questions">
    <div class="page-header">
      <h2 class="page-title">精选题库</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加题目
      </el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filterCategory" placeholder="筛选分类" clearable style="width: 150px">
        <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
      </el-select>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索题目..."
        prefix-icon="Search"
        clearable
        style="width: 250px; margin-left: 12px"
      />
    </div>

    <div class="questions-table">
      <el-table :data="filteredQuestions" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="question" label="题目" show-overflow-tooltip />
        <el-table-column prop="type" label="题型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="100">
          <template #default="{ row }">
            <el-tag :type="getDifficultyTag(row.difficulty)">{{ row.difficulty }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑题目' : '添加题目'" width="700px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="题目">
          <el-input v-model="form.question" type="textarea" rows="3" placeholder="请输入题目内容" />
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="form.type" placeholder="请选择题型" style="width: 100%">
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="简答题" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item label="选项" v-if="form.type !== 'short'">
          <el-input v-model="form.options" type="textarea" rows="3" placeholder="请输入选项，用换行分隔" />
        </el-form-item>
        <el-form-item label="正确答案">
          <el-input v-model="form.correct_answer" placeholder="请输入正确答案" />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="form.analysis" type="textarea" rows="3" placeholder="请输入题目解析" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="form.difficulty" placeholder="请选择难度" style="width: 100%">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="题目详情" width="600px">
      <div v-if="currentQuestion" class="question-detail">
        <div class="detail-item">
          <label>题目:</label>
          <p>{{ currentQuestion.question }}</p>
        </div>
        <div class="detail-item">
          <label>题型:</label>
          <span>{{ currentQuestion.type }}</span>
        </div>
        <div class="detail-item">
          <label>分类:</label>
          <el-tag type="info">{{ currentQuestion.category }}</el-tag>
        </div>
        <div class="detail-item">
          <label>难度:</label>
          <el-tag :type="getDifficultyTag(currentQuestion.difficulty)">{{ currentQuestion.difficulty }}</el-tag>
        </div>
        <div v-if="currentQuestion.options" class="detail-item">
          <label>选项:</label>
          <div class="options-content">
            <div v-for="(opt, idx) in parseOptions(currentQuestion.options)" :key="idx" class="option-item">
              {{ getOptionLabel(idx) }}. {{ opt }}
            </div>
          </div>
        </div>
        <div class="detail-item">
          <label>正确答案:</label>
          <span class="correct-answer">{{ getOptionLabel(getAnswerIndex(currentQuestion.correct_answer)) }} - {{ getAnswerText(currentQuestion.options, currentQuestion.correct_answer) }}</span>
        </div>
        <div class="detail-item">
          <label>解析:</label>
          <p>{{ currentQuestion.analysis }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { Plus, Search } from '@element-plus/icons-vue'

export default {
  name: 'SelectedQuestions',
  components: { Plus, Search },
  data() {
    return {
      questions: [],
      categories: [],
      filterCategory: '',
      searchKeyword: '',
      loading: false,
      dialogVisible: false,
      detailDialogVisible: false,
      isEdit: false,
      currentId: null,
      currentQuestion: null,
      form: {
        type: 'single',
        question: '',
        options: '',
        correct_answer: '',
        analysis: '',
        category: '',
        difficulty: 'medium'
      }
    }
  },
  computed: {
    filteredQuestions() {
      let result = this.questions
      if (this.filterCategory) {
        result = result.filter(q => q.category === this.filterCategory)
      }
      if (this.searchKeyword) {
        const keyword = this.searchKeyword.toLowerCase()
        result = result.filter(q =>
          q.question?.toLowerCase().includes(keyword) ||
          q.category?.toLowerCase().includes(keyword)
        )
      }
      return result
    }
  },
  mounted() {
    this.fetchQuestions()
    this.fetchCategories()
  },
  methods: {
    async fetchQuestions() {
      this.loading = true
      try {
        const response = await fetch('/api/admin/selected-questions?page=1&page_size=100')
        const data = await response.json()
        if (data.success) {
          this.questions = data.questions || []
        }
      } catch (error) {
        console.error('获取精选题库失败:', error)
      } finally {
        this.loading = false
      }
    },
    async fetchCategories() {
      try {
        const response = await fetch('/api/admin/categories')
        const data = await response.json()
        if (data.success) {
          this.categories = data.selected_categories || []
        }
      } catch (error) {
        console.error('获取分类失败:', error)
      }
    },
    showAddDialog() {
      this.isEdit = false
      this.currentId = null
      this.form = {
        type: 'single',
        question: '',
        options: '',
        correct_answer: '',
        analysis: '',
        category: '',
        difficulty: 'medium'
      }
      this.dialogVisible = true
    },
    handleView(row) {
      this.currentQuestion = row
      this.detailDialogVisible = true
    },
    handleEdit(row) {
      this.isEdit = true
      this.currentId = row.id
      this.form = {
        type: row.type || 'single',
        question: row.question || '',
        options: row.options || '',
        correct_answer: row.correct_answer || '',
        analysis: row.analysis || '',
        category: row.category || '',
        difficulty: row.difficulty || 'medium'
      }
      this.dialogVisible = true
    },
    async handleSave() {
      if (!this.form.question || !this.form.category) {
        this.$message.warning('请填写题目和分类')
        return
      }

      try {
        let url, method
        if (this.isEdit) {
          url = `/api/admin/selected-questions/${this.currentId}?type=${encodeURIComponent(this.form.type)}&question=${encodeURIComponent(this.form.question)}&options=${encodeURIComponent(this.form.options)}&correct_answer=${encodeURIComponent(this.form.correct_answer)}&analysis=${encodeURIComponent(this.form.analysis)}&category=${encodeURIComponent(this.form.category)}&difficulty=${encodeURIComponent(this.form.difficulty)}`
          method = 'PUT'
        } else {
          url = `/api/admin/selected-questions?type=${encodeURIComponent(this.form.type)}&question=${encodeURIComponent(this.form.question)}&options=${encodeURIComponent(this.form.options)}&correct_answer=${encodeURIComponent(this.form.correct_answer)}&analysis=${encodeURIComponent(this.form.analysis)}&category=${encodeURIComponent(this.form.category)}&difficulty=${encodeURIComponent(this.form.difficulty)}`
          method = 'POST'
        }

        const response = await fetch(url, { method })

        if (response.ok) {
          this.$message.success(this.isEdit ? '更新成功' : '添加成功')
          this.dialogVisible = false
          this.fetchQuestions()
          this.fetchCategories()
        } else {
          const data = await response.json()
          throw new Error(data.error || '保存失败')
        }
      } catch (error) {
        this.$message.error(error.message || '保存失败')
      }
    },
    async handleDelete(row) {
      try {
        await this.$confirm('确定要删除这道精选题目吗？', '删除确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await fetch(`/api/admin/selected-questions/${row.id}`, {
          method: 'DELETE'
        })

        if (response.ok) {
          this.$message.success('删除成功')
          this.fetchQuestions()
        } else {
          const data = await response.json()
          throw new Error(data.error || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error(error.message || '删除失败')
        }
      }
    },
    getTypeTag(type) {
      const types = {
        'single': '',
        'multiple': 'warning',
        'short': 'info'
      }
      return types[type] || ''
    },
    getDifficultyTag(difficulty) {
      const difficulties = {
        'easy': 'success',
        'medium': 'warning',
        'hard': 'danger'
      }
      return difficulties[difficulty] || ''
    },
    parseOptions(optionsStr) {
      if (!optionsStr) return []
      try {
        const parsed = JSON.parse(optionsStr)
        if (Array.isArray(parsed)) {
          return parsed.map(opt => {
            if (typeof opt === 'string') {
              return opt.replace(/^[A-D]\.\s*/, '')
            }
            return opt
          })
        }
        return optionsStr.split('\n').filter(opt => opt.trim())
      } catch {
        return optionsStr.split('\n').filter(opt => opt.trim())
      }
    },
    getOptionLabel(idx) {
      return String.fromCharCode(65 + idx)
    },
    getAnswerIndex(correctAnswer) {
      if (!correctAnswer) return -1
      const answer = correctAnswer.toUpperCase().trim()
      if (answer.length === 1 && answer >= 'A' && answer <= 'Z') {
        return answer.charCodeAt(0) - 65
      }
      return parseInt(answer) - 1
    },
    getAnswerText(optionsStr, correctAnswer) {
      const options = this.parseOptions(optionsStr)
      const answerIdx = this.getAnswerIndex(correctAnswer)
      if (answerIdx >= 0 && answerIdx < options.length) {
        return options[answerIdx]
      }
      return correctAnswer
    }
  }
}
</script>

<style scoped>
.selected-questions {
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
  display: flex;
  margin-bottom: 20px;
}

.questions-table {
  margin-top: 16px;
}

.question-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
}

.detail-item p {
  font-size: 14px;
  color: #303133;
  margin: 0;
  line-height: 1.6;
}

.detail-item span {
  font-size: 14px;
  color: #303133;
}

.options-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
}

.option-item {
  font-size: 14px;
  color: #303133;
}

.correct-answer {
  color: #67c23a !important;
  font-weight: 600;
}
</style>