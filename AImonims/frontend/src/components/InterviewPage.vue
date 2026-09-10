<template>
  <div class="main-content interview-page-container">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    <div class="particles-container">
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
    </div>
    
    <div class="interview-header">
      <div class="header-decoration">
        <div class="deco-circle dc1"></div>
        <div class="deco-circle dc2"></div>
        <div class="deco-dots">
          <span class="deco-dot"></span>
          <span class="deco-dot"></span>
          <span class="deco-dot"></span>
          <span class="deco-dot"></span>
        </div>
      </div>
      <div class="header-content">
        <div class="header-left">
          <div class="header-badge">
            <i class="el-icon-medal"></i>
            面试训练
          </div>
          <h2>事业单位面试</h2>
          <p class="header-desc">模拟真实面试场景，提升应试能力</p>
        </div>
        <span class="record-link" @click="handleHistoryClick">
          <i class="el-icon-document"></i>
          面试记录
        </span>
      </div>
    </div>
    
    <div class="interview-section">
      <div class="section-header">
        <div class="section-line"></div>
        <h3 class="section-title">
          <i class="el-icon-tickets"></i>
          面试流程说明
        </h3>
        <div class="section-line"></div>
      </div>
      
      <div class="process-content">
        <div class="process-flow">
          <div class="flow-line"></div>
          <div class="process-step" @mouseenter="activeStep = 1" @mouseleave="activeStep = 0">
            <div class="step-indicator">
              <div class="step-dot" :class="{ active: activeStep === 1 }">
                <span class="step-num">01</span>
              </div>
            </div>
            <div class="process-item">
              <div class="process-icon" :class="{ 'is-active': activeStep === 1 }">
                <svg viewBox="0 0 40 40" class="process-svg">
                  <rect x="8" y="6" width="24" height="30" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>
                  <line x1="13" y1="13" x2="27" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <line x1="13" y1="19" x2="27" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <line x1="13" y1="25" x2="22" y2="25" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="process-text">
                <h4>三个结构化面试题</h4>
                <p>本面试通过三个结构化面试题，考察考生的综合分析、组织协调、应急应变等能力。</p>
              </div>
            </div>
          </div>
          
          <div class="process-step" @mouseenter="activeStep = 2" @mouseleave="activeStep = 0">
            <div class="step-indicator">
              <div class="step-dot" :class="{ active: activeStep === 2 }">
                <span class="step-num">02</span>
              </div>
            </div>
            <div class="process-item">
              <div class="process-icon" :class="{ 'is-active': activeStep === 2 }">
                <svg viewBox="0 0 40 40" class="process-svg">
                  <rect x="6" y="8" width="28" height="26" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>
                  <line x1="11" y1="14" x2="29" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <line x1="11" y1="20" x2="25" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <line x1="11" y1="26" x2="29" y2="26" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <circle cx="28" cy="26" r="6" fill="none" stroke="currentColor" stroke-width="2"/>
                  <line x1="32" y1="30" x2="36" y2="34" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="process-text">
                <h4>多种题型随机组合</h4>
                <p>社会现象、态度观点、组织管理、应急应变、人际关系、情景模拟、串词、演讲、漫画、自我认知、复合题。</p>
              </div>
            </div>
          </div>
          
          <div class="process-step" @mouseenter="activeStep = 3" @mouseleave="activeStep = 0">
            <div class="step-indicator">
              <div class="step-dot" :class="{ active: activeStep === 3 }">
                <span class="step-num">03</span>
              </div>
            </div>
            <div class="process-item">
              <div class="process-icon highlight-icon" :class="{ 'is-active': activeStep === 3 }">
                <svg viewBox="0 0 40 40" class="process-svg highlight-svg">
                  <rect x="5" y="5" width="30" height="30" rx="4" fill="none" stroke="currentColor" stroke-width="2"/>
                  <line x1="12" y1="20" x2="28" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M15 12 L25 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M15 28 L22 28" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <circle cx="26" cy="26" r="8" fill="none" stroke="currentColor" stroke-width="2"/>
                  <path d="M30 30 L35 35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="process-text">
                <h4>自动生成面试反馈</h4>
                <p>完成三个问题的作答后，将自动为您生成详细的<span class="highlight">面试反馈</span>，帮助您了解自身表现。</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="interview-section">
      <div class="section-header">
        <div class="section-line"></div>
        <h3 class="section-title">
          <i class="el-icon-menu"></i>
          选择面试模式
        </h3>
        <div class="section-line"></div>
      </div>
      
      <div class="mode-cards">
        <div class="mode-card voice" @click="handleVoiceInterview" @mouseenter="voiceHover = true" @mouseleave="voiceHover = false">
          <div class="card-bg-effect"></div>
          <div class="mode-icon" :class="{ 'is-hover': voiceHover }">
            <svg viewBox="0 0 48 48" class="mode-svg">
              <circle cx="24" cy="14" r="8" fill="currentColor" opacity="0.9"/>
              <path d="M14 20 C14 20 10 36 24 36 C38 36 34 20 34 20" fill="currentColor" opacity="0.85"/>
              <rect x="21" y="34" width="6" height="4" rx="2" fill="currentColor" opacity="0.7"/>
              <rect x="17" y="36" width="14" height="3" rx="1.5" fill="currentColor" opacity="0.5"/>
              <path d="M36 22 L42 19 L42 25 L36 22" fill="currentColor" opacity="0.6"/>
            </svg>
          </div>
          <div class="mode-info">
            <h4>语音面试</h4>
            <p>通过语音与AI进行实时对话</p>
          </div>
          <div class="mode-tags">
            <span class="tag" :class="{ 'is-active': voiceHover }">语音识别</span>
            <span class="tag" :class="{ 'is-active': voiceHover }">实时对话</span>
          </div>
          <div class="mode-arrow" :class="{ 'is-hover': voiceHover }">
            <i class="el-icon-arrow-right"></i>
          </div>
        </div>
        
        <div class="mode-card ai" @click="handleAIInterview" @mouseenter="aiHover = true" @mouseleave="aiHover = false">
          <div class="card-bg-effect"></div>
          <div class="mode-icon" :class="{ 'is-hover': aiHover }">
            <svg viewBox="0 0 48 48" class="mode-svg">
              <circle cx="20" cy="14" r="6" fill="currentColor" opacity="0.9"/>
              <path d="M10 22 C10 22 8 34 20 34 C32 34 30 22 30 22" fill="currentColor" opacity="0.85"/>
              <rect x="28" y="26" width="14" height="4" rx="2" fill="currentColor" opacity="0.7" transform="rotate(-25 28 26)"/>
              <rect x="36" y="21" width="6" height="3" rx="1" fill="currentColor" opacity="0.5" transform="rotate(-25 36 21)"/>
              <circle cx="40" cy="17" r="2" fill="currentColor" opacity="0.4"/>
            </svg>
          </div>
          <div class="mode-info">
            <h4>AI交流对话</h4>
            <p>通过文字与AI进行对话交流</p>
          </div>
          <div class="mode-tags">
            <span class="tag" :class="{ 'is-active': aiHover }">文字输入</span>
            <span class="tag" :class="{ 'is-active': aiHover }">深度交流</span>
          </div>
          <div class="mode-arrow" :class="{ 'is-hover': aiHover }">
            <i class="el-icon-arrow-right"></i>
          </div>
        </div>
        
        <div class="mode-card avatar" @click="handleAvatarInterview" @mouseenter="avatarHover = true" @mouseleave="avatarHover = false">
          <div class="card-bg-effect"></div>
          <div class="mode-icon" :class="{ 'is-hover': avatarHover }">
            <svg viewBox="0 0 48 48" class="mode-svg">
              <circle cx="24" cy="16" r="8" fill="currentColor" opacity="0.9"/>
              <path d="M16 24 L32 24 L32 40 C32 42.2 30.2 44 28 44 H20 C17.8 44 16 42.2 16 40 Z" fill="currentColor" opacity="0.85"/>
              <circle cx="20" cy="14" r="2" fill="currentColor" opacity="0.7"/>
              <circle cx="28" cy="14" r="2" fill="currentColor" opacity="0.7"/>
              <path d="M20 20 Q24 22 28 20" fill="none" stroke="currentColor" stroke-width="2" opacity="0.6"/>
            </svg>
          </div>
          <div class="mode-info">
            <h4>数字人面试</h4>
            <p>与虚拟数字人进行面对面面试</p>
          </div>
          <div class="mode-tags">
            <span class="tag" :class="{ 'is-active': avatarHover }">实时形象</span>
            <span class="tag" :class="{ 'is-active': avatarHover }">语音交互</span>
          </div>
          <div class="mode-arrow" :class="{ 'is-hover': avatarHover }">
            <i class="el-icon-arrow-right"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InterviewPage',
  data() {
    return {
      activeStep: 0,
      voiceHover: false,
      aiHover: false,
      avatarHover: false
    }
  },
  methods: {
    handleVoiceInterview() {
      this.$emit('voice-interview')
    },
    handleAIInterview() {
      this.$emit('ai-interview')
    },
    handleAvatarInterview() {
      this.$emit('avatar-interview')
    },
    handleHistoryClick() {
      this.$emit('history-click')
    }
  }
}
</script>

<style scoped>
.interview-page-container {
  padding: 20px 16px;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  position: relative;
  overflow: hidden;
}

.interview-header {
  position: relative;
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  border-radius: 24px;
  padding: 32px 28px;
  margin-bottom: 28px;
  overflow: hidden;
  box-shadow: 0 12px 48px rgba(64, 158, 255, 0.32);
  z-index: 2;
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
  background: rgba(255, 255, 255, 0.08);
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

.interview-header h2 {
  font-size: 28px;
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

.record-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 22px;
  transition: all 0.3s;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.record-link:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.interview-section {
  margin-bottom: 32px;
  position: relative;
  z-index: 2;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 22px;
}

.section-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #dcdfe6 50%, transparent 100%);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  white-space: nowrap;
  text-shadow: 0 0 8px rgba(102, 126, 234, 0.3);
}

.section-title i {
  font-size: 17px;
  color: #409EFF;
}

.process-content {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 22px;
  padding: 32px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 6px 32px rgba(0, 0, 0, 0.3);
}

.process-flow {
  position: relative;
}

.flow-line {
  position: absolute;
  left: 23px;
  top: 40px;
  bottom: 40px;
  width: 2px;
  background: linear-gradient(180deg, #409EFF 0%, #66B1FF 50%, #e4e7ed 100%);
  border-radius: 2px;
}

.process-step {
  display: flex;
  gap: 24px;
  padding: 20px 0;
  position: relative;
  transition: all 0.3s;
}

.process-step:first-child {
  padding-top: 0;
}

.process-step:last-child {
  padding-bottom: 0;
}

.step-indicator {
  position: relative;
  z-index: 2;
}

.step-dot {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(102, 126, 234, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.step-dot.active {
  border-color: #409EFF;
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.3);
}

.step-num {
  font-size: 13px;
  font-weight: 700;
  color: #409EFF;
  font-family: 'DIN Alternate', -apple-system, sans-serif;
  transition: color 0.3s;
}

.step-dot.active .step-num {
  color: white;
}

.process-item {
  display: flex;
  gap: 18px;
  flex: 1;
  align-items: flex-start;
}

.process-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(102, 126, 234, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.process-icon.is-active {
  transform: scale(1.12) rotate(4deg);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.25);
}

.process-svg {
  width: 28px;
  height: 28px;
  color: #409EFF;
  transition: color 0.3s;
}

.highlight-icon {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.3);
}

.highlight-svg {
  color: white;
}

.process-text {
  flex: 1;
  padding-top: 4px;
}

.process-text h4 {
  font-size: 17px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 8px 0;
}

.process-text p {
  font-size: 14px;
  color: #a0a0c0;
  margin: 0;
  line-height: 1.8;
}

.highlight {
  color: #409EFF;
  font-weight: 500;
}

.mode-cards {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.mode-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 26px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.card-bg-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.4s;
}

.mode-card.voice .card-bg-effect {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.03) 0%, rgba(149, 212, 117, 0.03) 100%);
}

.mode-card.ai .card-bg-effect {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.03) 0%, rgba(102, 177, 255, 0.03) 100%);
}

.mode-card.avatar .card-bg-effect {
  background: linear-gradient(135deg, rgba(160, 82, 45, 0.03) 0%, rgba(210, 180, 140, 0.03) 100%);
}

.mode-card:hover .card-bg-effect {
  opacity: 1;
}

.mode-card.voice:hover {
  border-color: #67C23A;
  box-shadow: 0 14px 48px rgba(103, 194, 58, 0.18);
  transform: translateY(-5px);
}

.mode-card.ai:hover {
  border-color: #409EFF;
  box-shadow: 0 14px 48px rgba(64, 158, 255, 0.18);
  transform: translateY(-5px);
}

.mode-card.avatar:hover {
  border-color: #D2691E;
  box-shadow: 0 14px 48px rgba(210, 105, 30, 0.18);
  transform: translateY(-5px);
}

.mode-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-icon.is-hover {
  transform: rotate(6deg) scale(1.1);
}

.mode-icon.voice {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
  box-shadow: 0 6px 24px rgba(103, 194, 58, 0.35);
}

.mode-card.voice:hover .mode-icon.voice {
  box-shadow: 0 10px 32px rgba(103, 194, 58, 0.45);
}

.mode-icon.ai {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  box-shadow: 0 6px 24px rgba(64, 158, 255, 0.35);
}

.mode-card.ai:hover .mode-icon.ai {
  box-shadow: 0 10px 32px rgba(64, 158, 255, 0.45);
}

.mode-icon.avatar {
  background: linear-gradient(135deg, #D2691E 0%, #F4A460 100%);
  box-shadow: 0 6px 24px rgba(210, 105, 30, 0.35);
}

.mode-card.avatar:hover .mode-icon.avatar {
  box-shadow: 0 10px 32px rgba(210, 105, 30, 0.45);
}

.mode-svg {
  width: 34px;
  height: 34px;
  color: white;
}

.mode-info {
  flex: 1;
}

.mode-info h4 {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 6px 0;
}

.mode-info p {
  font-size: 14px;
  color: #a0a0c0;
  margin: 0;
}

.mode-tags {
  display: flex;
  gap: 10px;
}

.tag {
  padding: 5px 14px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  font-size: 12px;
  color: #a0a0c0;
  transition: all 0.3s;
}

.tag.is-active {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.mode-card.voice .tag.is-active {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.mode-card.avatar .tag.is-active {
  background: rgba(210, 105, 30, 0.1);
  color: #D2691E;
}

.mode-arrow {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-arrow.is-hover {
  transform: translateX(6px);
}

.mode-card.voice:hover .mode-arrow {
  background: #67C23A;
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.35);
}

.mode-card.ai:hover .mode-arrow {
  background: #409EFF;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.35);
}

.mode-card.avatar:hover .mode-arrow {
  background: #D2691E;
  box-shadow: 0 6px 20px rgba(210, 105, 30, 0.35);
}

.mode-arrow i {
  font-size: 18px;
  color: #909399;
  transition: color 0.3s;
}

.mode-arrow.is-hover i {
  color: white;
}

/* 科技感背景效果 */
.page-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  z-index: 0;
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(102, 126, 234, 0.6),
    transparent
  );
  animation: scan 3s linear infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes scan {
  0% { top: -3px; }
  100% { top: 100%; }
}

.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(102, 126, 234, 0.8);
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.8);
  animation: particleFloating 8s infinite ease-in-out;
}

.particle:nth-child(1) {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.particle:nth-child(2) {
  top: 60%;
  left: 85%;
  animation-delay: 2s;
}

.particle:nth-child(3) {
  top: 80%;
  left: 30%;
  animation-delay: 4s;
}

.particle:nth-child(4) {
  top: 30%;
  left: 70%;
  animation-delay: 6s;
}

@keyframes particleFloating {
  0%, 100% {
    transform: translateY(0px) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  50% {
    transform: translateY(-30px) scale(1.2);
    opacity: 0.8;
  }
  90% {
    opacity: 1;
  }
}
</style>