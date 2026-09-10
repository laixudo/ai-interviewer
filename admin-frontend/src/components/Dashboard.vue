<template>
  <div class="dashboard">
    <h2 class="page-title">数据概览</h2>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon users">
          <el-icon :size="32"><UserFilled /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalUsers || 0 }}</span>
          <span class="stat-label">注册用户</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon interviews">
          <el-icon :size="32"><VideoCamera /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalInterviews || 0 }}</span>
          <span class="stat-label">面试记录</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon questions">
          <el-icon :size="32"><QuestionFilled /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalQuestions || 0 }}</span>
          <span class="stat-label">真题数量</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon score">
          <el-icon :size="32"><Star /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.avgScore || 0 }}</span>
          <span class="stat-label">平均分数</span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <h3 class="chart-title">面试趋势</h3>
        <div class="chart-container" ref="trendChartRef"></div>
      </div>
      
      <div class="chart-card">
        <h3 class="chart-title">题库分布</h3>
        <div class="chart-container" ref="pieChartRef"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { UserFilled, VideoCamera, QuestionFilled, Star } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  components: { UserFilled, VideoCamera, QuestionFilled, Star },
  props: {
    stats: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      trendChart: null,
      pieChart: null
    }
  },
  mounted() {
    this.initCharts()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    if (this.trendChart) this.trendChart.dispose()
    if (this.pieChart) this.pieChart.dispose()
  },
  methods: {
    initCharts() {
      this.initTrendChart()
      this.initPieChart()
    },
    initTrendChart() {
      if (!this.$refs.trendChartRef) return
      this.trendChart = echarts.init(this.$refs.trendChartRef)
      const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
          axisLine: { lineStyle: { color: '#e4e7ed' } },
          axisLabel: { color: '#606266' }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f0f2f5' } },
          axisLabel: { color: '#606266' }
        },
        series: [{
          name: '面试次数',
          type: 'line',
          smooth: true,
          data: [12, 15, 10, 18, 22, 19, 25],
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
    },
    initPieChart() {
      if (!this.$refs.pieChartRef) return
      this.pieChart = echarts.init(this.$refs.pieChartRef)
      const option = {
        tooltip: { trigger: 'item' },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          textStyle: { color: '#606266' }
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['35%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: 14, fontWeight: 'bold' }
          },
          data: [
            { value: 35, name: '社会现象', itemStyle: { color: '#667eea' } },
            { value: 25, name: '态度观点', itemStyle: { color: '#764ba2' } },
            { value: 20, name: '组织管理', itemStyle: { color: '#f093fb' } },
            { value: 12, name: '应急应变', itemStyle: { color: '#4facfe' } },
            { value: 8, name: '人际关系', itemStyle: { color: '#43e97b' } }
          ]
        }]
      }
      this.pieChart.setOption(option)
    },
    handleResize() {
      if (this.trendChart) this.trendChart.resize()
      if (this.pieChart) this.pieChart.resize()
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.users { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.interviews { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-icon.questions { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.score { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
