<template>
  <div class="prep-center">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    <div class="particles-container">
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
      <div class="particle"></div>
    </div>
    
    <div class="prep-header">
      <div class="header-decoration">
        <div class="deco-circle dc1"></div>
        <div class="deco-circle dc2"></div>
      </div>
      <div class="header-content">
        <div class="header-badge">
          <svg class="badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          面试准备
        </div>
        <h2>面试准备中心</h2>
        <p class="subtitle">一站式面试准备平台，助您斩获offer</p>
      </div>
    </div>

    <div class="prep-tabs-wrapper">
      <div class="prep-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="prep-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path :d="tab.icon" />
          </svg>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="tab-content">
      <InterviewTips v-if="activeTab === 'tips'" />
      <ResumeAnalysis v-if="activeTab === 'resume'" />
      <CommunityHub v-if="activeTab === 'community'" />
    </div>
  </div>
</template>

<script>
import InterviewTips from './InterviewTips.vue'
import ResumeAnalysis from './ResumeAnalysis.vue'
import CommunityHub from './CommunityHub.vue'

export default {
  name: 'PrepCenter',
  components: {
    InterviewTips,
    ResumeAnalysis,
    CommunityHub
  },
  data() {
    return {
      activeTab: 'tips',
      tabs: [
        { key: 'tips', label: '面试干货', icon: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5' },
        { key: 'resume', label: '简历分析', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
        { key: 'community', label: '社区互动', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' }
      ]
    }
  }
}
</script>

<style scoped>
.prep-center {
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

.prep-header {
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
  width: 160px;
  height: 160px;
  top: -60px;
  right: -40px;
}

.dc2 {
  width: 100px;
  height: 100px;
  bottom: -40px;
  left: 50px;
}

.header-content {
  position: relative;
  z-index: 1;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.18);
  border-radius: 20px;
  font-size: 13px;
  color: white;
  font-weight: 500;
  margin-bottom: 14px;
  backdrop-filter: blur(8px);
}

.badge-icon {
  width: 18px;
  height: 18px;
}

.prep-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: white;
  margin: 0 0 10px 0;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  letter-spacing: 0.5px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  margin: 0;
}

.prep-tabs-wrapper {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 4px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.prep-tabs {
  display: flex;
  gap: 8px;
}

.prep-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 12px;
  background: transparent;
  border: none;
  border-radius: 16px;
  font-size: 14px;
  color: #a0a0c0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.prep-tab:hover {
  background: rgba(102, 126, 234, 0.1);
}

.prep-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.tab-icon {
  width: 24px;
  height: 24px;
}

.tab-content {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  min-height: 400px;
  border: 1px solid rgba(102, 126, 234, 0.3);
}
</style>