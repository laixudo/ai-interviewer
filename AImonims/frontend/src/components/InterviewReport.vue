<template>
  <div class="main-content">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    <div class="glow-effect"></div>
    
    <div class="report-header">
      <div class="back-btn" @click="$emit('back')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </div>
      <h2 class="report-title">面试评估报告</h2>
      <div class="empty"></div>
    </div>
    
    <div class="report-content">
      <div class="report-section">
        <div class="section-header">
          <div class="section-icon">📊</div>
          <h3 class="section-title">综合评估</h3>
        </div>
        <div class="overall-score">
          <div class="score-circle">
            <div class="score-circle-inner">
              <span class="score-value">{{ report.overall_score }}</span>
              <span class="score-unit">分</span>
            </div>
            <div class="score-glow"></div>
          </div>
          <div class="score-info">
            <div class="score-level">{{ report.overall_level }}</div>
            <div class="score-date">{{ report.timestamp }}</div>
          </div>
        </div>
      </div>
      
      <div class="report-section">
        <div class="section-header">
          <div class="section-icon">📝</div>
          <h3 class="section-title">内容评估</h3>
        </div>
        <div class="evaluation-grid">
          <div v-for="(result, criterion) in report.content_evaluation" :key="criterion" class="evaluation-card">
            <div class="evaluation-content">
              <div class="evaluation-label">{{ result.comment }}</div>
              <div class="score-display">
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: Math.min((result.score / 30) * 100, 100) + '%' }"></div>
                </div>
                <div class="evaluation-score">{{ result.score }}分</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="report-section">
        <div class="section-header">
          <div class="section-icon">💬</div>
          <h3 class="section-title">表达评估</h3>
        </div>
        <div class="evaluation-grid">
          <div v-for="(result, item) in report.expression_evaluation" :key="item" class="evaluation-card">
            <div class="evaluation-content">
              <div class="evaluation-label">{{ result.comment }}</div>
              <div class="score-display">
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: Math.min((result.score / 30) * 100, 100) + '%' }"></div>
                </div>
                <div class="evaluation-score">{{ result.score }}分</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="report-section">
        <div class="section-header">
          <div class="section-icon">🎙️</div>
          <h3 class="section-title">语音评估</h3>
        </div>
        <div class="evaluation-grid">
          <div v-if="report.expression_evaluation.voice_tone" class="evaluation-card">
            <div class="evaluation-content">
              <div class="evaluation-label">{{ report.expression_evaluation.voice_tone.comment }}</div>
              <div class="score-display">
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: Math.min((report.expression_evaluation.voice_tone.score / 30) * 100, 100) + '%' }"></div>
                </div>
                <div class="evaluation-score">{{ report.expression_evaluation.voice_tone.score }}分</div>
              </div>
            </div>
          </div>
          <div v-if="report.expression_evaluation.speech_rate" class="evaluation-card">
            <div class="evaluation-content">
              <div class="evaluation-label">{{ report.expression_evaluation.speech_rate.comment }}</div>
              <div class="score-display">
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: Math.min((report.expression_evaluation.speech_rate.score / 30) * 100, 100) + '%' }"></div>
                </div>
                <div class="evaluation-score">{{ report.expression_evaluation.speech_rate.score }}分</div>
              </div>
            </div>
          </div>
          <div v-if="report.expression_evaluation.voice_volume" class="evaluation-card">
            <div class="evaluation-content">
              <div class="evaluation-label">{{ report.expression_evaluation.voice_volume.comment }}</div>
              <div class="score-display">
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: Math.min((report.expression_evaluation.voice_volume.score / 30) * 100, 100) + '%' }"></div>
                </div>
                <div class="evaluation-score">{{ report.expression_evaluation.voice_volume.score }}分</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="report-section">
        <div class="section-header">
          <div class="section-icon">✨</div>
          <h3 class="section-title">亮点分析</h3>
        </div>
        <div class="highlights-list">
          <div v-for="(highlight, index) in report.highlights" :key="index" class="highlight-card">
            <div class="card-glow"></div>
            <div class="card-icon">✓</div>
            <div class="card-content">
              <span>{{ highlight }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="report-section">
        <div class="section-header">
          <div class="section-icon">📈</div>
          <h3 class="section-title">改进建议</h3>
        </div>
        <div class="suggestions-list">
          <div v-for="(suggestion, index) in report.improvement_suggestions" :key="index" class="suggestion-card">
            <div class="card-glow"></div>
            <div class="card-icon">⚡</div>
            <div class="card-content">
              <span>{{ suggestion.suggestion }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="report-actions">
        <div class="action-btn secondary" @click="$emit('restart')">
          <div class="btn-glow"></div>
          <span>重新面试</span>
        </div>
        <div class="action-btn accent" @click="$emit('view-plan')">
          <div class="btn-glow"></div>
          <span>查看提升计划</span>
        </div>
        <div class="action-btn primary" @click="$emit('back-home')">
          <div class="btn-glow"></div>
          <span>返回首页</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InterviewReport',
  props: {
    report: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['back', 'restart', 'view-plan', 'back-home']
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.main-content {
  position: relative;
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(145deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  overflow: hidden;
}

.page-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 24px,
      rgba(139, 92, 246, 0.06) 24px,
      rgba(139, 92, 246, 0.06) 25px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 24px,
      rgba(139, 92, 246, 0.06) 24px,
      rgba(139, 92, 246, 0.06) 25px
    );
  z-index: 0;
  pointer-events: none;
  animation: gridMove 25s linear infinite;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(48px, 48px);
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
    rgba(167, 139, 250, 0.5) 50%, 
    transparent 100%);
  pointer-events: none;
  z-index: 1;
  animation: scan 6s linear infinite;
}

@keyframes scan {
  0% {
    transform: translateY(-100%);
  }
  100% {
    transform: translateY(100vh);
  }
}

.glow-effect {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 15% 10%, rgba(167, 139, 250, 0.18) 0%, transparent 45%),
    radial-gradient(circle at 85% 90%, rgba(124, 58, 237, 0.15) 0%, transparent 45%);
  pointer-events: none;
  z-index: 1;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(167, 139, 250, 0.3);
  position: relative;
  z-index: 2;
}

.back-btn {
  cursor: pointer;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: #c4b5fd;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(167, 139, 250, 0.15);
  border-color: rgba(196, 181, 253, 0.6);
  color: #ffffff;
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.3);
  transform: translateY(-2px);
}

.back-btn svg {
  width: 22px;
  height: 22px;
}

.report-title {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 0 20px rgba(167, 139, 250, 0.6), 0 0 40px rgba(167, 139, 250, 0.3);
  letter-spacing: 0.5px;
}

.empty {
  width: 60px;
}

.report-content {
  background: linear-gradient(145deg, rgba(15, 12, 41, 0.88) 0%, rgba(30, 25, 65, 0.88) 100%);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(167, 139, 250, 0.25);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.5),
    0 0 80px rgba(139, 92, 246, 0.12),
    inset 0 0 2px rgba(167, 139, 250, 0.3);
  position: relative;
  z-index: 2;
}

.report-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.section-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(167, 139, 250, 0.3) 100%);
  border-radius: 12px;
  font-size: 20px;
  box-shadow: 0 0 16px rgba(167, 139, 250, 0.2);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 0 16px rgba(167, 139, 250, 0.5);
}

.overall-score {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 24px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-circle-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 
    0 0 30px rgba(167, 139, 250, 0.5),
    0 0 60px rgba(167, 139, 250, 0.3),
    inset 0 0 20px rgba(255, 255, 255, 0.15);
  z-index: 1;
}

.score-glow {
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(167, 139, 250, 0.4) 0%, transparent 70%);
  animation: scoreGlow 3s ease-in-out infinite;
}

@keyframes scoreGlow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.08); }
}

.score-value {
  font-size: 38px;
  font-weight: 800;
  line-height: 1;
}

.score-unit {
  font-size: 16px;
  margin-top: 6px;
  opacity: 0.95;
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-level {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.5);
}

.score-date {
  font-size: 15px;
  color: #a5b4fc;
}

.evaluation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 18px;
}

.evaluation-card {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(167, 139, 250, 0.2);
  padding: 20px;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(12px);
}

.evaluation-card:hover {
  transform: translateY(-4px);
  border-color: rgba(196, 181, 253, 0.5);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), 0 0 30px rgba(167, 139, 250, 0.2);
}

.evaluation-content {
  position: relative;
  z-index: 1;
}

.evaluation-label {
  font-size: 15px;
  color: #e0e7ff;
  line-height: 1.6;
  margin-bottom: 14px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-bar {
  flex: 1;
  height: 10px;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 5px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%);
  border-radius: 5px;
  transition: width 1s ease;
  box-shadow: 0 0 12px rgba(167, 139, 250, 0.6);
}

.evaluation-score {
  font-size: 20px;
  font-weight: 700;
  color: #c4b5fd;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.6);
  min-width: 60px;
  text-align: right;
}

.highlights-list,
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.highlight-card,
.suggestion-card {
  padding: 18px 20px;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  backdrop-filter: blur(12px);
  transition: all 0.3s ease;
}

.highlight-card {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.highlight-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 24px rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.5);
}

.suggestion-card {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.suggestion-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 24px rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.highlight-card .card-glow {
  background: radial-gradient(circle at 20% 20%, rgba(34, 197, 94, 0.3) 0%, transparent 55%);
}

.suggestion-card .card-glow {
  background: radial-gradient(circle at 20% 20%, rgba(239, 68, 68, 0.3) 0%, transparent 55%);
}

.highlight-card:hover .card-glow,
.suggestion-card:hover .card-glow {
  opacity: 1;
}

.card-icon {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
}

.highlight-card .card-icon {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.35) 0%, rgba(74, 222, 128, 0.35) 100%);
  color: #4ade80;
  box-shadow: 0 0 16px rgba(34, 197, 94, 0.3);
}

.suggestion-card .card-icon {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.35) 0%, rgba(248, 113, 113, 0.35) 100%);
  color: #f87171;
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.3);
}

.card-content {
  flex: 1;
}

.card-content span {
  font-size: 15px;
  line-height: 1.6;
  color: #e0e7ff;
}

.report-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid rgba(167, 139, 250, 0.2);
}

.action-btn {
  min-width: 140px;
  padding: 14px 28px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn span {
  position: relative;
  z-index: 1;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: #e0e7ff;
}

.action-btn.secondary .btn-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 0%, rgba(167, 139, 250, 0.25) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-btn.secondary:hover {
  background: rgba(167, 139, 250, 0.15);
  border-color: rgba(196, 181, 253, 0.6);
  color: #ffffff;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 24px rgba(167, 139, 250, 0.25);
}

.action-btn.secondary:hover .btn-glow {
  opacity: 1;
}

.action-btn.accent {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.25) 0%, rgba(74, 222, 128, 0.25) 100%);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #86efac;
}

.action-btn.accent .btn-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 0%, rgba(34, 197, 94, 0.3) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-btn.accent:hover {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.35) 0%, rgba(74, 222, 128, 0.35) 100%);
  border-color: rgba(74, 222, 128, 0.7);
  color: #bbf7d0;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 24px rgba(34, 197, 94, 0.3);
}

.action-btn.accent:hover .btn-glow {
  opacity: 1;
}

.action-btn.primary {
  background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%);
  border: none;
  color: white;
  box-shadow: 
    0 6px 20px rgba(167, 139, 250, 0.45),
    0 0 30px rgba(167, 139, 250, 0.3) inset;
}

.action-btn.primary .btn-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: buttonShine 2s infinite;
}

@keyframes buttonShine {
  0% { left: -100%; }
  100% { left: 100%; }
}

.action-btn.primary:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 12px 36px rgba(167, 139, 250, 0.65),
    0 0 40px rgba(167, 139, 250, 0.4) inset;
}
</style>
