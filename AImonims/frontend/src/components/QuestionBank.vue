<template>
  <div class="question-bank-container">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    <div class="particles-container">
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
    </div>
    
    <div class="page-header">
      <div class="header-decoration">
        <div class="deco-circle dc1"></div>
        <div class="deco-circle dc2"></div>
        <div class="deco-dots">
          <span class="deco-dot"></span>
          <span class="deco-dot"></span>
          <span class="deco-dot"></span>
        </div>
      </div>
      <div class="header-content">
        <div class="header-left">
          <div class="header-badge">
            <i class="el-icon-collection"></i>
            精选题库
          </div>
          <h2>事业单位面试精选题库</h2>
          <p class="header-desc">AI智能生成，高质量面试题目练习</p>
        </div>
        <div class="header-stats" v-if="stats">
          <div class="stat-item">
            <span class="stat-num">{{ stats.total }}</span>
            <span class="stat-label">总题数</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-num">{{ Object.keys(stats.stats || {}).length }}</span>
            <span class="stat-label">分类数</span>
          </div>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="filter-tabs">
        <button
          class="filter-tab"
          :class="{ active: activeTab === 'all' }"
          @click="handleTabChange('all')"
        >
          全部
        </button>
        <button
          v-for="cat in categories"
          :key="cat"
          class="filter-tab"
          :class="{ active: activeTab === cat }"
          @click="handleTabChange(cat)"
        >
          {{ cat }}
        </button>
      </div>

      <div class="filter-actions">
        <div class="type-filter">
          <el-radio-group v-model="questionType" size="small" @change="handleTypeChange">
            <el-radio-button value="all">全部题型</el-radio-button>
            <el-radio-button value="single">单选题</el-radio-button>
            <el-radio-button value="multiple">多选题</el-radio-button>
          </el-radio-group>
        </div>
        <div class="generate-buttons">
          <button class="generate-btn random" @click="handleRandomPractice" :disabled="isGenerating || filteredQuestions.length === 0">
            <i class="el-icon-question"></i>
            随机练一题
          </button>
          <button class="generate-btn single" @click="handleGenerate('single')" :disabled="isGenerating">
            <i class="el-icon-refresh" :class="{ spinning: isGeneratingSingle }"></i>
            {{ isGeneratingSingle ? '生成中...' : '生成单选' }}
          </button>
          <button class="generate-btn multiple" @click="handleGenerate('multiple')" :disabled="isGenerating">
            <i class="el-icon-refresh" :class="{ spinning: isGeneratingMultiple }"></i>
            {{ isGeneratingMultiple ? '生成中...' : '生成多选' }}
          </button>
        </div>
      </div>
    </div>

    <div class="questions-content">
      <div class="questions-list" v-if="filteredQuestions.length > 0">
        <div
          v-for="(question, index) in filteredQuestions"
          :key="question.id"
          class="question-card"
          :class="{ expanded: expandedId === question.id }"
          @click="handleQuestionClick(question)"
        >
          <div class="question-header">
            <div class="question-meta">
              <span class="question-index">{{ index + 1 }}</span>
              <span class="question-type" :class="question.question_type">
                {{ question.question_type === 'single' ? '单选' : '多选' }}
              </span>
              <span class="question-category">{{ question.category }}</span>
              <span class="question-difficulty" :class="question.difficulty">
                {{ difficultyText[question.difficulty] || '中等' }}
              </span>
            </div>
            <div class="question-actions">
              <svg
                class="favorite-icon"
                :class="{ favorited: isQuestionFavorited(question.id) }"
                @click.stop="handleToggleFavorite(question)"
                :title="isQuestionFavorited(question.id) ? '取消收藏' : '收藏'"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              <i class="el-icon-arrow-down expand-icon" :class="{ rotated: expandedId === question.id }"></i>
            </div>
          </div>

          <div class="question-body">
            <p class="question-text">{{ question.question }}</p>

            <div class="options-list" v-if="expandedId === question.id">
              <div
                v-for="(option, optIndex) in question.options"
                :key="optIndex"
                class="option-item"
                :class="{
                  selected: selectedAnswers[question.id] === option.charAt(0),
                  correct: showAnswer && isCorrectAnswer(question, option),
                  incorrect: showAnswer && selectedAnswers[question.id] === option.charAt(0) && !isCorrectAnswer(question, option)
                }"
                @click.stop="handleOptionSelect(question, option)"
              >
                <span class="option-letter">{{ option.charAt(0) }}</span>
                <span class="option-text">{{ option.substring(3) }}</span>
                <i v-if="showAnswer && isCorrectAnswer(question, option)" class="el-icon-check correct-icon"></i>
                <i v-if="showAnswer && selectedAnswers[question.id] === option && !isCorrectAnswer(question, option)" class="el-icon-close incorrect-icon"></i>
              </div>
            </div>

            <div class="answer-section" v-if="expandedId === question.id && showAnswer">
              <div class="correct-answer">
                <span class="answer-label">正确答案：</span>
                <span class="answer-value">{{ formatAnswer(question) }}</span>
              </div>
              <div class="analysis-section">
                <div class="analysis-label">
                  <i class="el-icon-document"></i>
                  题目解析
                </div>
                <p class="analysis-text">{{ question.analysis }}</p>
              </div>
            </div>

            <div class="action-bar" v-if="expandedId === question.id">
              <button class="action-btn submit-btn" v-if="!showAnswer" @click.stop="handleSubmit(question)">
                提交答案
              </button>
              <button class="action-btn next-btn" v-else @click.stop="handleNext">
                下一题
                <i class="el-icon-arrow-right"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else>
        <div class="empty-icon">
          <i class="el-icon-document"></i>
        </div>
        <h3>暂无题目</h3>
        <p>点击"AI生成题目"按钮开始生成精选题库</p>
        <button class="generate-btn-large" @click="handleGenerate" :disabled="isGenerating">
          <i class="el-icon-refresh" :class="{ spinning: isGenerating }"></i>
          {{ isGenerating ? '生成中...' : '立即生成' }}
        </button>
      </div>
    </div>

    <div class="bottom-spacer"></div>

    <el-dialog
      v-model="randomPracticeDialogVisible"
      :title="randomPracticeTitle"
      width="600px"
      :close-on-click-modal="false"
      class="random-practice-dialog"
    >
      <div class="random-practice-content" v-if="currentRandomQuestion">
        <div class="random-question-meta">
          <span class="question-type" :class="currentRandomQuestion.question_type">
            {{ currentRandomQuestion.question_type === 'single' ? '单选题' : '多选题' }}
          </span>
          <span class="question-category">{{ currentRandomQuestion.category }}</span>
          <span class="question-difficulty" :class="currentRandomQuestion.difficulty">
            {{ difficultyText[currentRandomQuestion.difficulty] || '中等' }}
          </span>
        </div>

        <p class="random-question-text">{{ currentRandomQuestion.question }}</p>

        <div class="random-options-list">
          <div
            v-for="(option, optIndex) in currentRandomQuestion.options"
            :key="optIndex"
            class="option-item"
            :class="{
              selected: randomPracticeSelectedAnswer === option.charAt(0),
              correct: randomPracticeShowAnswer && isCorrectAnswer(currentRandomQuestion, option),
              incorrect: randomPracticeShowAnswer && randomPracticeSelectedAnswer === option.charAt(0) && !isCorrectAnswer(currentRandomQuestion, option)
            }"
            @click="handleRandomOptionSelect(option)"
          >
            <span class="option-letter">{{ option.charAt(0) }}</span>
            <span class="option-text">{{ option.substring(3) }}</span>
            <i v-if="randomPracticeShowAnswer && isCorrectAnswer(currentRandomQuestion, option)" class="el-icon-check correct-icon"></i>
            <i v-if="randomPracticeShowAnswer && randomPracticeSelectedAnswer === option && !isCorrectAnswer(currentRandomQuestion, option)" class="el-icon-close incorrect-icon"></i>
          </div>
        </div>

        <div class="answer-section" v-if="randomPracticeShowAnswer">
          <div class="correct-answer">
            <span class="answer-label">正确答案：</span>
            <span class="answer-value">{{ formatAnswer(currentRandomQuestion) }}</span>
          </div>
          <div class="analysis-section">
            <div class="analysis-label">
              <i class="el-icon-document"></i>
              题目解析
            </div>
            <p class="analysis-text">{{ currentRandomQuestion.analysis }}</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <button class="action-btn submit-btn" v-if="!randomPracticeShowAnswer" @click="handleRandomSubmit">
            提交答案
          </button>
          <button class="action-btn next-btn" v-else @click="handleRandomNext">
            再练一题
            <i class="el-icon-refresh"></i>
          </button>
          <button class="action-btn close-btn" @click="randomPracticeDialogVisible = false">
            关闭
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'QuestionBank',
  emits: ['back'],
  data() {
    return {
      questions: [],
      categories: ['组织协调', '应急应变', '技术能力', '言语表达', '项目经验'],
      difficultyText: {
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
      },
      activeTab: 'all',
      questionType: 'all',
      expandedId: null,
      selectedAnswers: {},
      showAnswer: false,
      isGenerating: false,
      isGeneratingSingle: false,
      isGeneratingMultiple: false,
      stats: null,
      randomPracticeDialogVisible: false,
      randomPracticeTitle: '随机练一题',
      currentRandomQuestion: null,
      randomPracticeSelectedAnswer: null,
      randomPracticeShowAnswer: false,
      favoritedQuestions: new Set()
    }
  },
  computed: {
    filteredQuestions() {
      let filtered = this.questions;

      if (this.activeTab !== 'all') {
        filtered = filtered.filter(q => q.category === this.activeTab);
      }

      if (this.questionType !== 'all') {
        filtered = filtered.filter(q => q.question_type === this.questionType);
      }

      return filtered;
    }
  },
  mounted() {
    this.loadQuestions();
    this.loadStats();
    this.loadFavoritedQuestions();
  },
  methods: {
    async loadQuestions() {
      try {
        const response = await fetch('/api/selected-questions');
        if (response.ok) {
          const data = await response.json();
          this.questions = data.questions || [];
        }
      } catch (error) {
        console.error('加载题目失败:', error);
        this.$message.error('加载题目失败');
      }
    },

    async loadStats() {
      try {
        const response = await fetch('/api/selected-questions/stats');
        if (response.ok) {
          const data = await response.json();
          this.stats = data;
        }
      } catch (error) {
        console.error('加载统计失败:', error);
      }
    },

    async loadFavoritedQuestions() {
      const userData = localStorage.getItem('userData');
      if (!userData) return;

      try {
        const user = JSON.parse(userData);
        const response = await fetch(`/api/favorites?user_id=${user.id}&favorite_type=question`);
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data) {
            this.favoritedQuestions = new Set(data.data.map(f => f.item_id));
          }
        }
      } catch (error) {
        console.error('加载收藏状态失败:', error);
      }
    },

    isQuestionFavorited(questionId) {
      return this.favoritedQuestions.has(questionId);
    },

    async handleToggleFavorite(question) {
      const userData = localStorage.getItem('userData');
      if (!userData) {
        this.$message.warning('请先登录');
        return;
      }

      const user = JSON.parse(userData);

      try {
        const response = await fetch('/api/favorites/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: user.id,
            favorite_type: 'question',
            item_id: question.id,
            title: question.question,
            content: question.analysis
          })
        });

        const data = await response.json();
        if (data.success) {
          if (data.is_favorited) {
            this.favoritedQuestions.add(question.id);
            this.$message.success('收藏成功');
          } else {
            this.favoritedQuestions.delete(question.id);
            this.$message.success('已取消收藏');
          }
        }
      } catch (error) {
        console.error('收藏操作失败:', error);
        this.$message.error('操作失败');
      }
    },

    handleTabChange(tab) {
      this.activeTab = tab;
      this.expandedId = null;
      this.showAnswer = false;
      this.selectedAnswers = {};
    },

    handleTypeChange(type) {
      this.questionType = type;
      this.expandedId = null;
      this.showAnswer = false;
      this.selectedAnswers = {};
    },

    handleQuestionClick(question) {
      if (this.expandedId === question.id) {
        return;
      }
      this.expandedId = question.id;
      this.showAnswer = false;
      this.selectedAnswers[question.id] = null;
    },

    handleOptionSelect(question, option) {
      if (this.showAnswer) return;

      const optionLetter = option.charAt(0);

      if (question.question_type === 'single') {
        this.selectedAnswers[question.id] = optionLetter;
      } else {
        const current = this.selectedAnswers[question.id] || [];
        const exists = current.includes(optionLetter);

        if (exists) {
          this.selectedAnswers[question.id] = current.filter(o => o !== optionLetter);
        } else {
          this.selectedAnswers[question.id] = [...current, optionLetter];
        }
      }
    },

    isCorrectAnswer(question, option) {
      const correct = question.correct_answer;
      const optionLetter = option.charAt(0);

      let correctAnswers = [];
      if (typeof correct === 'string') {
        if (correct.includes(',')) {
          correctAnswers = correct.split(',');
        } else {
          correctAnswers = [correct];
        }
      } else if (Array.isArray(correct)) {
        correctAnswers = correct;
      }

      return correctAnswers.includes(optionLetter);
    },

    formatAnswer(question) {
      const correct = question.correct_answer;
      if (typeof correct === 'string' && correct.includes(',')) {
        return correct.split(',').join('、');
      }
      return correct;
    },

    handleSubmit(question) {
      if (!this.selectedAnswers[question.id]) {
        this.$message.warning('请选择答案');
        return;
      }
      this.showAnswer = true;
    },

    handleNext() {
      const currentIndex = this.filteredQuestions.findIndex(q => q.id === this.expandedId);
      if (currentIndex < this.filteredQuestions.length - 1) {
        this.expandedId = this.filteredQuestions[currentIndex + 1].id;
        this.showAnswer = false;
        this.selectedAnswers[this.expandedId] = null;
      } else {
        this.$message.success('已做完所有题目');
        this.expandedId = null;
        this.showAnswer = false;
      }
    },

    handleRandomPractice() {
      if (this.filteredQuestions.length === 0) {
        this.$message.warning('暂无题目可练习');
        return;
      }
      const randomIndex = Math.floor(Math.random() * this.filteredQuestions.length);
      this.currentRandomQuestion = this.filteredQuestions[randomIndex];
      this.randomPracticeSelectedAnswer = null;
      this.randomPracticeShowAnswer = false;
      this.randomPracticeDialogVisible = true;
    },

    handleRandomOptionSelect(option) {
      if (this.randomPracticeShowAnswer) return;
      this.randomPracticeSelectedAnswer = option.charAt(0);
    },

    handleRandomSubmit() {
      if (!this.randomPracticeSelectedAnswer) {
        this.$message.warning('请选择答案');
        return;
      }
      this.randomPracticeShowAnswer = true;
    },

    handleRandomNext() {
      const randomIndex = Math.floor(Math.random() * this.filteredQuestions.length);
      this.currentRandomQuestion = this.filteredQuestions[randomIndex];
      this.randomPracticeSelectedAnswer = null;
      this.randomPracticeShowAnswer = false;
    },

    async handleGenerate(questionType) {
      if (questionType === 'single') {
        this.isGeneratingSingle = true;
      } else {
        this.isGeneratingMultiple = true;
      }
      this.isGenerating = true;

      try {
        const response = await fetch(`/api/selected-questions/generate?count_per_category=2&question_type=${questionType}`, {
          method: 'POST'
        });

        if (response.ok) {
          const data = await response.json();
          this.$message.success(data.message || '生成成功');
          await this.loadQuestions();
          await this.loadStats();
        } else {
          this.$message.error('生成失败');
        }
      } catch (error) {
        console.error('生成题目失败:', error);
        this.$message.error('生成题目失败');
      } finally {
        this.isGenerating = false;
        this.isGeneratingSingle = false;
        this.isGeneratingMultiple = false;
      }
    }
  }
}
</script>

<style scoped>
.question-bank-container {
  padding: 16px;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  position: relative;
  overflow: hidden;
}

.page-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.08) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: 0;
  animation: gridMove 25s linear infinite;
  pointer-events: none;
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(40px, 40px); }
}

.scan-line {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to bottom, 
    transparent 0%, 
    rgba(102, 126, 234, 0.4) 50%, 
    transparent 100%);
  pointer-events: none;
  z-index: 1;
  animation: scan 7s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}

.particles-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #667eea;
  border-radius: 50%;
  box-shadow: 0 0 8px #667eea, 0 0 16px #667eea;
  animation: float 12s infinite;
  opacity: 0.5;
}

.particle:nth-child(2) {
  animation-delay: -2s;
  background: #764ba2;
  box-shadow: 0 0 8px #764ba2, 0 0 16px #764ba2;
}

.particle:nth-child(3) {
  animation-delay: -5s;
  background: #a855f7;
  box-shadow: 0 0 8px #a855f7, 0 0 16px #a855f7;
}

.particle:nth-child(4) {
  animation-delay: -8s;
  background: #6366f1;
  box-shadow: 0 0 8px #6366f1, 0 0 16px #6366f1;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% { opacity: 0.5; }
  90% { opacity: 0.5; }
  50% { transform: translateY(-100vh) translateX(80px); }
}

.page-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px;
  padding: 32px 28px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 
    0 12px 48px rgba(102, 126, 234, 0.4),
    0 0 30px rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  z-index: 1;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #fff, transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.dc1 {
  width: 200px;
  height: 200px;
  top: -80px;
  right: -50px;
}

.dc2 {
  width: 120px;
  height: 120px;
  bottom: -50px;
  left: 60px;
}

.deco-dots {
  position: absolute;
  top: 20%;
  right: 20%;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.deco-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  position: relative;
  z-index: 1;
}

.header-left {
  flex: 1;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.18);
  border-radius: 20px;
  font-size: 13px;
  color: white;
  font-weight: 500;
  margin-bottom: 14px;
  backdrop-filter: blur(8px);
}

.page-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: white;
  margin: 0 0 10px 0;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  letter-spacing: 0.5px;
}

.header-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 20px;
  background: rgba(255, 255, 255, 0.15);
  padding: 16px 24px;
  border-radius: 16px;
  backdrop-filter: blur(8px);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
}

.filter-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 8px 16px;
  border: none;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab:hover {
  background: #ecf5ff;
  color: #409EFF;
}

.filter-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.type-filter {
  display: flex;
  gap: 12px;
}

.generate-buttons {
  display: flex;
  gap: 10px;
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-btn.single {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.generate-btn.multiple {
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.generate-btn.random {
  background: linear-gradient(135deg, #E6A23C 0%, #F56C6C 100%);
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.3);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.generate-btn.single:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.generate-btn.multiple:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.4);
}

.generate-btn.random:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(230, 162, 60, 0.4);
}

.generate-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.questions-content {
  min-height: 400px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.question-card.expanded {
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.question-index {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.question-type {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.question-type.single {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.question-type.multiple {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.question-category {
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 12px;
  font-size: 12px;
  color: #606266;
}

.question-difficulty {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.question-difficulty.easy {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.question-difficulty.medium {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.question-difficulty.hard {
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
}

.expand-icon {
  font-size: 18px;
  color: #909399;
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.question-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.favorite-icon {
  width: 24px;
  height: 24px;
  color: #909399;
  cursor: pointer;
  transition: all 0.3s ease;
}

.favorite-icon:hover {
  color: #E6A23C;
  transform: scale(1.1);
}

.favorite-icon.favorited {
  color: #E6A23C;
  fill: #E6A23C;
}

.question-body {
  margin-top: 16px;
}

.question-text {
  font-size: 16px;
  color: #303133;
  line-height: 1.7;
  margin: 0;
}

.options-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #f8f9ff;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
}

.option-item:hover {
  background: #f0f4ff;
  border-color: #d9ecff;
}

.option-item.selected {
  background: rgba(64, 158, 255, 0.08);
  border-color: #409EFF;
}

.option-item.correct {
  background: rgba(103, 194, 58, 0.08);
  border-color: #67C23A;
}

.option-item.incorrect {
  background: rgba(245, 108, 108, 0.08);
  border-color: #F56C6C;
}

.option-letter {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: white;
  border: 2px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.option-item.selected .option-letter {
  background: #409EFF;
  border-color: #409EFF;
  color: white;
}

.option-item.correct .option-letter {
  background: #67C23A;
  border-color: #67C23A;
  color: white;
}

.option-item.incorrect .option-letter {
  background: #F56C6C;
  border-color: #F56C6C;
  color: white;
}

.option-text {
  flex: 1;
  font-size: 15px;
  color: #303133;
  line-height: 1.5;
}

.correct-icon {
  font-size: 18px;
  color: #67C23A;
  font-weight: bold;
}

.incorrect-icon {
  font-size: 18px;
  color: #F56C6C;
  font-weight: bold;
}

.answer-section {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9ff;
  border-radius: 12px;
}

.correct-answer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.answer-label {
  font-size: 14px;
  color: #606266;
}

.answer-value {
  font-size: 16px;
  font-weight: 600;
  color: #67C23A;
}

.analysis-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 12px;
}

.analysis-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.analysis-label i {
  color: #667eea;
}

.analysis-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
  margin: 0;
}

.action-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.next-btn {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.next-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon i {
  font-size: 36px;
  color: #909399;
}

.empty-state h3 {
  font-size: 20px;
  color: #303133;
  margin: 0 0 10px 0;
}

.empty-state p {
  font-size: 14px;
  color: #909399;
  margin: 0 0 24px 0;
}

.generate-btn-large {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.generate-btn-large:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
}

.generate-btn-large:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.bottom-spacer {
  height: 20px;
}

.random-practice-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
}

.random-practice-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #E6A23C 0%, #F56C6C 100%);
  padding: 20px;
  margin: 0;
}

.random-practice-dialog :deep(.el-dialog__title) {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.random-practice-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.random-practice-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.random-practice-content {
  max-height: 60vh;
  overflow-y: auto;
}

.random-question-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.random-question-text {
  font-size: 16px;
  color: #303133;
  line-height: 1.7;
  margin: 0 0 20px 0;
}

.random-options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.close-btn {
  background: #909399;
  color: white;
  box-shadow: 0 4px 12px rgba(144, 147, 153, 0.3);
}

.close-btn:hover {
  background: #787878;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(144, 147, 153, 0.4);
}
</style>
