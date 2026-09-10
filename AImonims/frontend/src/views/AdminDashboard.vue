<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2 class="section-title">
        <i class="el-icon-data-line"></i>
        数据概览
      </h2>
    </div>

    <div class="stats-cards">
      <div class="stat-card stat-users">
        <div class="stat-decoration"></div>
        <div class="stat-icon">
          <i class="el-icon-user"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_users || 0 }}</div>
          <div class="stat-label">用户总数</div>
          <div class="stat-badge badge-new">+{{ stats.new_users_7d || 0 }} 本周新增</div>
        </div>
      </div>

      <div class="stat-card stat-interviews">
        <div class="stat-decoration"></div>
        <div class="stat-icon">
          <i class="el-icon-chat-dot-round"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_interviews || 0 }}</div>
          <div class="stat-label">面试记录</div>
          <div class="stat-badge badge-new">+{{ stats.new_interviews_7d || 0 }} 本周新增</div>
        </div>
      </div>

      <div class="stat-card stat-exam">
        <div class="stat-decoration"></div>
        <div class="stat-icon">
          <i class="el-icon-document"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_exam_questions || 0 }}</div>
          <div class="stat-label">真题数量</div>
        </div>
      </div>

      <div class="stat-card stat-selected">
        <div class="stat-decoration"></div>
        <div class="stat-icon">
          <i class="el-icon-check-circle"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_selected_questions || 0 }}</div>
          <div class="stat-label">精选题库</div>
        </div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <i class="el-icon-data-analysis"></i>
            面试趋势（近30天）
          </h3>
        </div>
        <div class="chart-body">
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <i class="el-icon-pie-chart"></i>
            精选题库分布
          </h3>
        </div>
        <div class="chart-body">
          <div ref="categoryChartRef" class="chart-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {},
      trendChart: null,
      categoryChart: null
    }
  },
  mounted() {
    this.loadStats()
  },
  beforeUnmount() {
    if (this.trendChart) {
      this.trendChart.dispose()
    }
    if (this.categoryChart) {
      this.categoryChart.dispose()
    }
  },
  methods: {
    async loadStats() {
      try {
        const response = await fetch('http://localhost:8000/api/admin/stats')
        const data = await response.json()
        if (data.success) {
          this.stats = data.stats
          this.$nextTick(() => {
            this.initTrendChart()
            this.initCategoryChart()
          })
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    initTrendChart() {
      if (!this.$refs.trendChartRef) return

      this.trendChart = echarts.init(this.$refs.trendChartRef)

      const trendData = this.stats.interviews_trend || []
      const dates = trendData.map(item => item[0])
      const counts = trendData.map(item => item[1])

      const option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e4e7ed',
          textStyle: { color: '#303133' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '8%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLine: { lineStyle: { color: '#DCDFE6' } },
          axisLabel: { color: '#606266', rotate: 45 }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisLabel: { color: '#909399' },
          splitLine: { lineStyle: { color: '#F2F6FC', type: 'dashed' } }
        },
        series: [{
          name: '面试次数',
          type: 'line',
          smooth: true,
          data: counts,
          lineStyle: { color: '#667eea', width: 3 },
          itemStyle: { color: '#667eea' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
            ])
          }
        }]
      }

      this.trendChart.setOption(option)
      window.addEventListener('resize', () => this.trendChart.resize())
    },
    initCategoryChart() {
      if (!this.$refs.categoryChartRef) return

      this.categoryChart = echarts.init(this.$refs.categoryChartRef)

      const categoryData = this.stats.questions_by_category || []
      const data = categoryData.map(item => ({ name: item[0], value: item[1] }))

      const option = {
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e4e7ed',
          textStyle: { color: '#303133' }
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center'
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 18,
              fontWeight: 'bold'
            }
          },
          labelLine: { show: false },
          data: data,
          color: ['#667eea', '#764ba2', '#f6d365', '#fda085', '#67C23A', '#409EFF']
        }]
      }

      this.categoryChart.setOption(option)
      window.addEventListener('resize', () => this.categoryChart.resize())
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.dashboard-header {
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  gap: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
  border-radius: 0 0 0 100px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-users .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-interviews .stat-icon { background: linear-gradient(135deg, #409EFF, #67C23A); }
.stat-exam .stat-icon { background: linear-gradient(135deg, #E6A23C, #F56C6C); }
.stat-selected .stat-icon { background: linear-gradient(135deg, #67C23A, #909399); }

.stat-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  width: fit-content;
}

.badge-new {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.chart-title i {
  color: #667eea;
}

.chart-body {
  position: relative;
}

.chart-container {
  width: 100%;
  height: 300px;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-section {
    grid-template-columns: 1fr;
  }
}
</style>
