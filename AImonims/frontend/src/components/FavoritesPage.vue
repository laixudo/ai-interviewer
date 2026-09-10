<template>
  <div class="favorites-container">
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
      </div>
      <div class="header-content">
        <div class="header-left">
          <div class="header-badge">
            <i class="el-icon-star-on"></i>
            我的收藏
          </div>
          <h2>我的收藏夹</h2>
          <p class="header-desc">收藏喜欢的题目和面试记录</p>
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
          class="filter-tab"
          :class="{ active: activeTab === 'question' }"
          @click="handleTabChange('question')"
        >
          收藏题目
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeTab === 'interview' }"
          @click="handleTabChange('interview')"
        >
          收藏面试
        </button>
      </div>
    </div>

    <div class="favorites-content">
      <div class="favorites-list" v-if="filteredFavorites.length > 0">
        <div
          v-for="item in filteredFavorites"
          :key="item.id"
          class="favorite-card"
          :class="{ expanded: expandedId === item.id }"
          @click="handleItemClick(item)"
        >
          <div class="favorite-header">
            <div class="favorite-meta">
              <span class="favorite-type" :class="item.favorite_type">
                {{ getTypeName(item.favorite_type) }}
              </span>
              <span class="favorite-time">{{ formatTime(item.created_at) }}</span>
            </div>
            <div class="favorite-actions">
              <svg
                class="favorited-icon"
                @click.stop="handleRemoveFavorite(item)"
                title="取消收藏"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
          </div>

          <div class="favorite-content">
            <h3 class="favorite-title">{{ item.title || '无标题' }}</h3>
            <p class="favorite-preview" v-if="item.content">{{ truncateContent(item.content) }}</p>
          </div>

          <div class="answer-section" v-if="expandedId === item.id && item.favorite_type === 'question'">
            <div class="analysis-section">
              <div class="analysis-label">
                <i class="el-icon-document"></i>
                题目解析
              </div>
              <p class="analysis-text">{{ item.content || '暂无解析' }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else>
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        </div>
        <h3>暂无收藏</h3>
        <p>快去收藏喜欢的题目和面试记录吧</p>
      </div>
    </div>

    <div class="bottom-spacer"></div>
  </div>
</template>

<script>
export default {
  name: 'FavoritesPage',
  emits: ['back'],
  data() {
    return {
      favorites: [],
      activeTab: 'all',
      expandedId: null
    }
  },
  computed: {
    filteredFavorites() {
      if (this.activeTab === 'all') {
        return this.favorites;
      }
      return this.favorites.filter(f => f.favorite_type === this.activeTab);
    }
  },
  mounted() {
    this.loadFavorites();
  },
  methods: {
    async loadFavorites() {
      const userData = localStorage.getItem('userData');
      if (!userData) {
        this.$message.warning('请先登录');
        return;
      }

      try {
        const user = JSON.parse(userData);
        const response = await fetch(`/api/favorites?user_id=${user.id}`);
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            this.favorites = data.data || [];
          }
        }
      } catch (error) {
        console.error('加载收藏失败:', error);
        this.$message.error('加载收藏失败');
      }
    },

    handleTabChange(tab) {
      this.activeTab = tab;
      this.expandedId = null;
    },

    handleItemClick(item) {
      if (item.favorite_type === 'question') {
        this.expandedId = this.expandedId === item.id ? null : item.id;
      }
    },

    getTypeName(type) {
      const typeMap = {
        'question': '题目',
        'interview': '面试'
      };
      return typeMap[type] || type;
    },

    formatTime(timeStr) {
      if (!timeStr) return '';
      const date = new Date(timeStr);
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    },

    truncateContent(content, maxLength = 50) {
      if (!content) return '';
      if (content.length <= maxLength) return content;
      return content.substring(0, maxLength) + '...';
    },

    async handleRemoveFavorite(item) {
      const userData = localStorage.getItem('userData');
      if (!userData) {
        this.$message.warning('请先登录');
        return;
      }

      try {
        const user = JSON.parse(userData);
        const response = await fetch('/api/favorites/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: user.id,
            favorite_type: item.favorite_type,
            item_id: item.item_id
          })
        });

        const data = await response.json();
        if (data.success) {
          this.favorites = this.favorites.filter(f => f.id !== item.id);
          this.$message.success('已取消收藏');
        }
      } catch (error) {
        console.error('取消收藏失败:', error);
        this.$message.error('操作失败');
      }
    }
  }
}
</script>

<style scoped>
.favorites-container {
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
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
  border-radius: 24px;
  padding: 32px 28px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(102, 126, 234, 0.2);
  border: 2px solid rgba(102, 126, 234, 0.4);
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

.filter-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.filter-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.filter-tab {
  padding: 8px 16px;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  font-size: 14px;
  color: #c0c4cc;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(102, 126, 234, 0.2);
  backdrop-filter: blur(10px);
}

.filter-tab:hover {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.filter-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5), 0 0 30px rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.8);
}

.favorites-content {
  min-height: 400px;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.favorite-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(102, 126, 234, 0.3);
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  position: relative !important;
  z-index: 1 !important;
  overflow: hidden;
}

.favorite-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(45deg, rgba(102, 126, 234, 0.03) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(102, 126, 234, 0.03) 25%, transparent 25%);
  background-size: 20px 20px;
  pointer-events: none;
}

.favorite-card:hover {
  transform: translateY(-4px) translateX(2px);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3), 0 0 40px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.6);
}

.favorite-card.expanded {
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4), 0 0 50px rgba(102, 126, 234, 0.25);
}

.favorite-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.favorite-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.favorite-type {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.favorite-type.question {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.favorite-type.interview {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.favorite-time {
  font-size: 12px;
  color: #c0c4cc;
  font-weight: 500;
}

.favorite-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.favorited-icon {
  width: 24px;
  height: 24px;
  color: #f093fb;
  fill: #f093fb;
  cursor: pointer;
  transition: all 0.3s ease;
  filter: drop-shadow(0 0 8px rgba(240, 147, 251, 0.5));
}

.favorited-icon:hover {
  transform: scale(1.15);
  filter: drop-shadow(0 0 16px rgba(240, 147, 251, 0.8));
}

.favorite-content {
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.favorite-title {
  font-size: 16px;
  font-weight: 600;
  color: #e0e2ea;
  margin: 0 0 8px 0;
  line-height: 1.5;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.favorite-preview {
  font-size: 14px;
  color: #c0c4cc;
  margin: 0;
  line-height: 1.5;
  font-weight: 500;
}

.answer-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(102, 126, 234, 0.3);
  position: relative;
  z-index: 1;
}

.analysis-section {
  background: rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.analysis-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #e0e2ea;
  margin-bottom: 8px;
}

.analysis-label i {
  color: #667eea;
}

.analysis-text {
  font-size: 14px;
  color: #c0c4cc;
  line-height: 1.7;
  margin: 0;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.empty-state::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(102, 126, 234, 0.4);
  position: relative;
  z-index: 1;
}

.empty-icon svg {
  width: 36px;
  height: 36px;
  color: white;
  fill: white;
}

.empty-state h3 {
  font-size: 20px;
  color: #e0e2ea;
  margin: 0 0 10px 0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
  position: relative;
  z-index: 1;
}

.empty-state p {
  font-size: 14px;
  color: #c0c4cc;
  margin: 0;
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.bottom-spacer {
  height: 20px;
}
</style>