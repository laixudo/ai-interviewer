<template>
  <div class="main-content">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    <div class="glow-effect"></div>
    
    <div class="plan-header">
      <div class="back-btn" @click="$emit('back')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </div>
      <h2 class="plan-title">能力提升计划</h2>
      <div class="empty"></div>
    </div>

    <div class="plan-content">
      <!-- 能力短板 -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-icon">⚠️</div>
          <h3 class="section-title">能力短板</h3>
        </div>
        <div class="weaknesses-list">
          <div v-for="(item, index) in plan.weakness_analysis" :key="index" class="weakness-item">
            <div class="card-glow"></div>
            <div class="item-icon">!</div>
            <span>{{ item.weakness }}</span>
            <span class="severity-badge" :class="item.severity">{{ item.severity }}</span>
          </div>
        </div>
      </div>
      
      <!-- 提升建议 -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-icon">💡</div>
          <h3 class="section-title">提升建议</h3>
        </div>
        <div class="suggestions-list">
          <div v-for="(item, index) in plan.improvement_suggestions" :key="index" class="suggestion-item">
            <div class="card-glow"></div>
            <div class="item-icon">✓</div>
            <div class="suggestion-content">
              <div class="suggestion-category">{{ item.category }}</div>
              <div class="suggestion-text">{{ item.suggestion }}</div>
              <div class="priority-badge" :class="`priority-${item.priority}`">优先级: {{ item.priority }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 推荐学习资源 -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-icon">📚</div>
          <h3 class="section-title">推荐学习资源</h3>
        </div>
        <div class="resources-list">
          <div v-for="(resource, index) in plan.learning_resources" :key="index" class="resource-item">
            <div class="card-glow"></div>
            <div class="item-icon">📖</div>
            <div class="resource-content">
              <div class="resource-title">{{ resource.title }}</div>
              <div class="resource-description">{{ resource.description }}</div>
              <div v-if="resource.url" class="resource-url">
                <a :href="resource.url" target="_blank">{{ resource.url }}</a>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 学习计划 -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-icon">📅</div>
          <h3 class="section-title">30天学习计划</h3>
        </div>
        <div class="learning-plan">
          <div v-for="(weekPlan, index) in plan.thirty_day_plan" :key="index" class="week-plan">
            <div class="week-header">
              <span class="week-number">第{{ weekPlan.week }}周</span>
              <span class="week-title">{{ weekPlan.focus }}</span>
            </div>
            <div class="week-tasks">
              <div v-for="(task, taskIndex) in weekPlan.daily_tasks" :key="taskIndex" class="task-item">
                <div class="task-icon">→</div>
                <span>{{ task }}</span>
              </div>
            </div>
            <div v-if="weekPlan.expected_outcome" class="week-outcome">
              <span class="outcome-label">预期成果：</span>
              <span class="outcome-text">{{ weekPlan.expected_outcome }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="plan-actions">
        <div class="action-btn secondary" @click="$emit('back')">
          <div class="btn-glow"></div>
          <span>返回评估报告</span>
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
  name: 'ImprovementPlan',
  props: {
    plan: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['back', 'back-home']
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
  0% { transform: translate(0, 0); }
  100% { transform: translate(48px, 48px); }
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
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
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

.plan-header {
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
  border: 1px solid rgba(167, 139, 250, 0.4);
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

.plan-title {
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

.plan-content {
  background: linear-gradient(145deg, rgba(15, 12, 41, 0.9) 0%, rgba(30, 25, 65, 0.9) 100%);
  backdrop-filter: blur(24px);
  border-radius: 24px;
  padding: 28px;
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.5),
    0 0 80px rgba(139, 92, 246, 0.12),
    inset 0 0 2px rgba(167, 139, 250, 0.3);
  border: 1px solid rgba(167, 139, 250, 0.25);
  position: relative;
  z-index: 2;
}

.plan-section {
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

.weaknesses-list,
.suggestions-list,
.resources-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.weakness-item,
.suggestion-item,
.resource-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.weakness-item:hover,
.suggestion-item:hover,
.resource-item:hover {
  transform: translateY(-3px);
  border-color: rgba(167, 139, 250, 0.45);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35), 0 0 24px rgba(167, 139, 250, 0.2);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.weakness-item .card-glow {
  background: radial-gradient(circle at 20% 20%, rgba(239, 68, 68, 0.2) 0%, transparent 55%);
}

.suggestion-item .card-glow {
  background: radial-gradient(circle at 20% 20%, rgba(34, 197, 94, 0.2) 0%, transparent 55%);
}

.resource-item .card-glow {
  background: radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.2) 0%, transparent 55%);
}

.weakness-item:hover .card-glow,
.suggestion-item:hover .card-glow,
.resource-item:hover .card-glow {
  opacity: 1;
}

.item-icon {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  flex-shrink: 0;
}

.weakness-item .item-icon {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.35) 0%, rgba(248, 113, 113, 0.35) 100%);
  color: #fca5a5;
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.3);
}

.suggestion-item .item-icon {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.35) 0%, rgba(74, 222, 128, 0.35) 100%);
  color: #86efac;
  box-shadow: 0 0 16px rgba(34, 197, 94, 0.3);
}

.resource-item .item-icon {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.35) 0%, rgba(96, 165, 250, 0.35) 100%);
  color: #93c5fd;
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.3);
}

.weakness-item span,
.task-item span {
  flex: 1;
  font-size: 15px;
  line-height: 1.6;
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.severity-badge {
  padding: 6px 14px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.severity-badge.高 {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(248, 113, 113, 0.25) 100%);
  color: #fca5a5;
  border: 1px solid rgba(248, 113, 113, 0.4);
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.2);
}

.severity-badge.中 {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.25) 0%, rgba(250, 204, 21, 0.25) 100%);
  color: #fde047;
  border: 1px solid rgba(250, 204, 21, 0.4);
  box-shadow: 0 0 16px rgba(234, 179, 8, 0.2);
}

.severity-badge.低 {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(96, 165, 250, 0.25) 100%);
  color: #93c5fd;
  border: 1px solid rgba(96, 165, 250, 0.4);
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.2);
}

.suggestion-content {
  flex: 1;
}

.suggestion-category {
  font-size: 14px;
  font-weight: 700;
  color: #86efac;
  margin-bottom: 6px;
  text-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
}

.suggestion-text {
  font-size: 15px;
  line-height: 1.6;
  color: #ffffff;
  font-weight: 500;
  margin-bottom: 10px;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.priority-badge {
  display: inline-block;
  padding: 5px 14px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.priority-1 {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(248, 113, 113, 0.25) 100%);
  color: #fca5a5;
  border: 1px solid rgba(248, 113, 113, 0.4);
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.2);
}

.priority-2 {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.25) 0%, rgba(250, 204, 21, 0.25) 100%);
  color: #fde047;
  border: 1px solid rgba(250, 204, 21, 0.4);
  box-shadow: 0 0 16px rgba(234, 179, 8, 0.2);
}

.priority-3 {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(96, 165, 250, 0.25) 100%);
  color: #93c5fd;
  border: 1px solid rgba(96, 165, 250, 0.4);
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.2);
}

.resource-content {
  flex: 1;
}

.resource-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 10px;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.5);
}

.resource-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.resource-type,
.resource-difficulty,
.resource-time {
  font-size: 13px;
  padding: 5px 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2) 0%, rgba(196, 181, 253, 0.2) 100%);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.35);
  font-weight: 600;
}

.resource-description {
  font-size: 14px;
  line-height: 1.6;
  color: #e0e7ff;
  margin-bottom: 10px;
  font-weight: 500;
}

.resource-url a {
  font-size: 13px;
  color: #93c5fd;
  text-decoration: none;
  word-break: break-all;
  font-weight: 500;
  text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

.resource-url a:hover {
  text-decoration: underline;
  color: #bfdbfe;
}

.learning-plan {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.week-plan {
  position: relative;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 18px;
  padding: 18px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.week-plan:hover {
  transform: translateY(-3px);
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(167, 139, 250, 0.45);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35), 0 0 24px rgba(167, 139, 250, 0.2);
}

.week-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(167, 139, 250, 0.3);
}

.week-number {
  font-size: 15px;
  font-weight: 700;
  color: #a78bfa;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.5);
}

.week-title {
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 0 10px rgba(167, 139, 250, 0.4);
}

.week-tasks {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.task-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 15px;
  line-height: 1.6;
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.task-icon {
  width: 24px;
  height: 24px;
  min-width: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3) 0%, rgba(196, 181, 253, 0.3) 100%);
  color: #c4b5fd;
  box-shadow: 0 0 10px rgba(167, 139, 250, 0.2);
  flex-shrink: 0;
}

.week-outcome {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid rgba(167, 139, 250, 0.25);
  font-size: 14px;
}

.outcome-label {
  font-weight: 700;
  color: #c4b5fd;
  text-shadow: 0 0 10px rgba(167, 139, 250, 0.4);
}

.outcome-text {
  color: #e0e7ff;
  line-height: 1.6;
  font-weight: 500;
}

.plan-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid rgba(167, 139, 250, 0.2);
}

.action-btn {
  min-width: 150px;
  padding: 14px 32px;
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
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.4);
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
  background: rgba(167, 139, 250, 0.18);
  border-color: rgba(196, 181, 253, 0.7);
  color: #ffffff;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 24px rgba(167, 139, 250, 0.25);
}

.action-btn.secondary:hover .btn-glow {
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
