<template>
  <div class="main-content">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    <div class="particles-container">
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
    </div>
    
    <!-- 核心功能导航区 -->
    <div class="function-section">
      <div class="function-grid">
        <div class="function-item" @click="handleFunctionClick('面试干货')">
          <div class="function-icon-wrapper">
            <div class="function-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="16" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
            </div>
          </div>
          <div class="function-name">面试干货</div>
        </div>
        <div class="function-item" @click="handleFunctionClick('精选题库')">
          <div class="function-icon-wrapper">
            <div class="function-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </div>
          </div>
          <div class="function-name">精选题库</div>
        </div>
      </div>
    </div>
    
    <!-- 专项提升区 -->
    <div class="special-section">
      <div class="special-header">
        <div class="special-title-wrapper">
          <div class="special-frog">
            <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20character&image_size=square" alt="青蛙图标" class="frog-small-img">
          </div>
          <h3 class="special-title">专项提升</h3>
        </div>
        <div class="special-action">
          <button class="random-btn" @click="handleRandomQuestion">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"/>
              <polyline points="1 20 1 14 7 14"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            随机练一题
          </button>
        </div>
      </div>
      
      <div class="exam-questions-section">
        <div class="exam-questions-header">
          <h3 class="exam-questions-title">事业单位历年真题</h3>
        </div>
        
        <div class="exam-questions-list" v-if="examQuestions.length > 0">
          <div 
            v-for="question in examQuestions" 
            :key="question.id"
            class="exam-question-item"
            @click="viewExamQuestionDetail(question)"
          >
            <div class="exam-question-content">
              <h4 class="exam-question-title">{{ question.question }}</h4>
              <div class="exam-question-meta">
                <span class="exam-question-category">{{ question.category }}</span>
                <span class="exam-question-time">{{ question.created_at }}</span>
              </div>
            </div>
            <div class="exam-question-action">
              <span class="exam-question-more">查看详情</span>
              <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
        </div>
        <div v-else class="empty-exam-questions">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <p class="empty-text">暂无真题</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  props: {
    examQuestions: {
      type: Array,
      default: () => []
    },
    searchQuery: {
      type: String,
      default: ''
    },
    examSearchKeyword: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      localSearchQuery: this.searchQuery,
      localExamSearchKeyword: this.examSearchKeyword
    }
  },
  watch: {
    searchQuery(newVal) {
      this.localSearchQuery = newVal
    },
    examSearchKeyword(newVal) {
      this.localExamSearchKeyword = newVal
    }
  },
  methods: {
    handleFunctionClick(functionName) {
      this.$emit('function-click', functionName)
    },
    handleRandomQuestion() {
      this.$emit('random-question')
    },
    handleSearch() {
      this.$emit('search', this.localSearchQuery)
    },
    searchExamQuestions() {
      this.$emit('search-exam', this.localExamSearchKeyword)
    },
    viewExamQuestionDetail(question) {
      this.$emit('view-exam-question', question)
    }
  }
}
</script>

<style scoped>
.main-content {
  position: relative;
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  overflow: hidden;
}

.page-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  z-index: 0;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.scan-line {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(to bottom, 
    transparent 0%, 
    rgba(102, 126, 234, 0.3) 50%, 
    transparent 100%);
  pointer-events: none;
  z-index: 1;
  animation: scan 8s linear infinite;
}

@keyframes scan {
  0% {
    transform: translateY(-100%);
  }
  100% {
    transform: translateY(100vh);
  }
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
  width: 4px;
  height: 4px;
  background: #667eea;
  border-radius: 50%;
  box-shadow: 0 0 10px #667eea, 0 0 20px #667eea;
  animation: float 15s infinite;
  opacity: 0.6;
}

.particle:nth-child(2) {
  animation-delay: -3s;
  background: #764ba2;
  box-shadow: 0 0 10px #764ba2, 0 0 20px #764ba2;
}

.particle:nth-child(3) {
  animation-delay: -6s;
  background: #a855f7;
  box-shadow: 0 0 10px #a855f7, 0 0 20px #a855f7;
}

.particle:nth-child(4) {
  animation-delay: -9s;
  background: #6366f1;
  box-shadow: 0 0 10px #6366f1, 0 0 20px #6366f1;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 0.6;
  }
  90% {
    opacity: 0.6;
  }
  50% {
    transform: translateY(-100vh) translateX(100px);
  }
}

/* 核心功能导航区 */
.function-section {
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.function-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  padding: 28px 16px;
  border-radius: 20px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.function-item::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #667eea, #764ba2, #a855f7, #6366f1);
  border-radius: 22px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.function-item:hover::before {
  opacity: 1;
  animation: borderGlow 3s linear infinite;
}

@keyframes borderGlow {
  0%, 100% {
    filter: hue-rotate(0deg);
  }
  50% {
    filter: hue-rotate(90deg);
  }
}

.function-item:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 20px 40px rgba(102, 126, 234, 0.4),
    0 0 30px rgba(102, 126, 234, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border-color: rgba(102, 126, 234, 0.6);
}

.function-icon-wrapper {
  margin-bottom: 12px;
  position: relative;
}

.function-icon {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.4),
    0 0 20px rgba(102, 126, 234, 0.2);
  color: white;
  position: relative;
  overflow: hidden;
}

.function-icon::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  animation: shine 3s infinite;
}

@keyframes shine {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  100% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
}

.function-icon svg {
  width: 36px;
  height: 36px;
  stroke-width: 2;
  filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.5));
}

.function-name {
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

/* 专项提升区 */
.special-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.special-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.special-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.special-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.special-frog {
  display: flex;
  align-items: center;
}

.frog-small-img {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 3px solid #667eea;
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.5);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 15px rgba(102, 126, 234, 0.5);
  }
  50% {
    box-shadow: 0 0 25px rgba(102, 126, 234, 0.8);
  }
}

.special-title {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.special-action {
  display: flex;
  align-items: center;
}

.random-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.4),
    0 0 20px rgba(102, 126, 234, 0.2);
  position: relative;
  overflow: hidden;
}

.random-btn::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  animation: shine 3s infinite;
}

.random-btn:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 8px 24px rgba(102, 126, 234, 0.5),
    0 0 30px rgba(102, 126, 234, 0.3);
}

.btn-icon {
  width: 18px;
  height: 18px;
  filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.5));
}

/* 搜索框 */
.search-box {
  margin-bottom: 24px;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 16px;
  padding: 4px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
}

.search-input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 
    0 0 0 3px rgba(102, 126, 234, 0.2),
    0 0 20px rgba(102, 126, 234, 0.3);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: #a0a0c0;
  margin-left: 12px;
  flex-shrink: 0;
  filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.3));
}

.search-icon-small {
  width: 18px;
  height: 18px;
  color: #a0a0c0;
  margin-left: 8px;
  flex-shrink: 0;
  filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.3));
}

.search-input {
  flex: 1;
  border: none;
  padding: 12px 12px;
  font-size: 15px;
  outline: none;
  background: transparent;
  color: #ffffff;
}

.search-input::placeholder {
  color: #a0a0c0;
}

.exam-search-input {
  flex: 1;
  border: none;
  padding: 8px 8px;
  font-size: 14px;
  outline: none;
  background: transparent;
  color: #ffffff;
}

.exam-search-input::placeholder {
  color: #a0a0c0;
}

.search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4), 0 0 25px rgba(102, 126, 234, 0.3);
}

.exam-search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.exam-search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4), 0 0 20px rgba(102, 126, 234, 0.3);
}

/* 事业单位历年真题 */
.exam-questions-section {
  margin-top: 24px;
}

.exam-questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.exam-questions-title {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.exam-questions-search-wrapper {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 12px;
  padding: 4px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  width: 320px;
}

.exam-questions-search-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2), 0 0 15px rgba(102, 126, 234, 0.3);
}

.exam-questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.exam-question-item {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.exam-question-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.05), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.exam-question-item:hover::before {
  opacity: 1;
}

.exam-question-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2), 0 0 30px rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.5);
}

.exam-question-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.exam-question-title {
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 10px 0;
  line-height: 1.5;
}

.exam-question-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #a0a0c0;
}

.exam-question-category {
  background: rgba(102, 126, 234, 0.2);
  color: #a5b4fc;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 500;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.exam-question-action {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #a5b4fc;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.exam-question-more {
  font-weight: 500;
}

.arrow-icon {
  width: 16px;
  height: 16px;
  filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5));
}

.empty-exam-questions {
  padding: 48px 0;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
}

.empty-icon svg {
  width: 36px;
  height: 36px;
  color: #a5b4fc;
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
}

.empty-text {
  font-size: 15px;
  color: #a0a0c0;
  margin: 0;
}
</style>