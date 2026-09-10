<template>
  <div class="exam-questions">
    <div class="page-header">
      <h2 class="page-title">真题管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加真题
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
      <el-table :data="filteredQuestions" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="question" label="题目" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="添加时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑真题' : '添加真题'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="题目">
          <el-input v-model="form.question" type="textarea" rows="3" placeholder="请输入题目内容" />
        </el-form-item>
        <el-form-item label="答案">
          <el-input v-model="form.answer" type="textarea" rows="4" placeholder="请输入答案" />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="form.analysis" type="textarea" rows="3" placeholder="请输入题目解析" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { Plus, Search } from '@element-plus/icons-vue'

export default {
  name: 'ExamQuestions',
  components: { Plus, Search },
  props: {
    questions: {
      type: Array,
      default: () => []
    }
  },
  emits: ['refresh'],
  data() {
    return {
      filterCategory: '',
      searchKeyword: '',
      dialogVisible: false,
      isEdit: false,
      currentId: null,
      form: {
        question: '',
        answer: '',
        analysis: '',
        category: ''
      },
      categories: ['社会现象', '态度观点', '组织管理', '应急应变', '人际关系']
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
          q.answer?.toLowerCase().includes(keyword)
        )
      }
      return result
    }
  },
  methods: {
    showAddDialog() {
      this.isEdit = false
      this.currentId = null
      this.form = { question: '', answer: '', analysis: '', category: '' }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.isEdit = true
      this.currentId = row.id
      this.form = {
        question: row.question || '',
        answer: row.answer || '',
        analysis: row.analysis || '',
        category: row.category || ''
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
          url = `/api/admin/exam-questions/${this.currentId}?question=${encodeURIComponent(this.form.question)}&answer=${encodeURIComponent(this.form.answer)}&analysis=${encodeURIComponent(this.form.analysis)}&category=${encodeURIComponent(this.form.category)}`
          method = 'PUT'
        } else {
          url = `/api/admin/exam-questions?question=${encodeURIComponent(this.form.question)}&answer=${encodeURIComponent(this.form.answer)}&analysis=${encodeURIComponent(this.form.analysis)}&category=${encodeURIComponent(this.form.category)}`
          method = 'POST'
        }
        
        const response = await fetch(url, { method })

        if (response.ok) {
          this.$message.success(this.isEdit ? '更新成功' : '添加成功')
          this.dialogVisible = false
          this.$emit('refresh')
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
        await this.$confirm('确定要删除这道真题吗？', '删除确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await fetch(`/api/admin/exam-questions/${row.id}`, {
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
.exam-questions {
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
</style>
