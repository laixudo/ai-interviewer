<template>
  <div class="main-content">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    
    <div class="record-header">
      <div class="back-btn" @click="$emit('back')">
        <i class="el-icon-arrow-left"></i>
      </div>
      <h2 class="record-title">个人能力档案</h2>
      <div class="empty"></div>
    </div>

    <div class="profile-content">
      <!-- 综合评分卡片 -->
      <div class="overall-card" :class="{ 'animate-in': mounted }">
        <div class="card-bg-pattern"></div>
        <div class="card-corner-decoration top-left"></div>
        <div class="card-corner-decoration top-right"></div>
        <div class="card-corner-decoration bottom-left"></div>
        <div class="card-corner-decoration bottom-right"></div>
        
        <div class="overall-left">
          <div class="overall-score-ring">
            <svg class="score-svg" viewBox="0 0 100 100">
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#f6d365"/>
                  <stop offset="100%" stop-color="#fda085"/>
                </linearGradient>
              </defs>
              <circle class="score-bg" cx="50" cy="50" r="45" />
              <circle
                class="score-progress"
                cx="50" cy="50" r="45"
                :stroke-dasharray="283 * overallScore / 100 + ' 283'"
              />
            </svg>
            <div class="score-center">
              <span class="score-number">{{ displayScore }}</span>
              <span class="score-label">综合评分</span>
            </div>
            <div class="score-glow"></div>
          </div>
        </div>
        <div class="overall-right">
          <div class="level-badge" :class="levelClass">
            <span class="badge-icon">
              <i :class="levelIcon"></i>
            </span>
            {{ levelText }}
          </div>
          <p class="level-desc">{{ levelDesc }}</p>
          <div class="history-stats">
            <div class="stat-item" v-for="(stat, index) in statsData" :key="index" :style="{ animationDelay: (index * 0.1) + 's' }">
              <span class="stat-value">
                <span v-if="stat.suffix" class="stat-prefix">{{ stat.prefix }}</span>
                <span v-count-up="stat.value">0</span>
                <span v-if="stat.suffix" class="stat-suffix">{{ stat.suffix }}</span>
              </span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
        <div class="card-decoration">
          <div class="deco-circle deco-1"></div>
          <div class="deco-circle deco-2"></div>
          <div class="deco-circle deco-3"></div>
          <div class="deco-line"></div>
        </div>
      </div>

      <!-- 能力画像 -->
      <div class="profile-section ability-section" :class="{ 'animate-in': mounted }">
        <div class="card-bg-pattern"></div>
        <div class="section-header">
          <h3 class="section-title">
            <i class="el-icon-odometer"></i>
            能力画像
          </h3>
          <div class="header-actions">
            <span class="update-time">
              <i class="el-icon-time"></i>
              {{ updateTime }}
            </span>
            <button class="refresh-btn" @click="refreshData">
              <i class="el-icon-refresh" :class="{ 'is-rotating': isRefreshing }"></i>
            </button>
          </div>
        </div>
        <div class="ability-content">
          <div class="radar-chart" id="radarChart"></div>
          <div class="ability-highlights">
            <div 
              class="highlight-item" 
              v-for="(item, index) in topAbilities" 
              :key="index"
              :style="{ animationDelay: (index * 0.15) + 's' }"
              @mouseenter="highlightDimension(index)"
              @mouseleave="unhighlightDimension"
            >
              <div class="highlight-icon" :style="{ background: `linear-gradient(135deg, ${item.color}, ${item.color}99)` }">
                <i :class="item.icon"></i>
              </div>
              <div class="highlight-info">
                <span class="highlight-name">{{ item.name }}</span>
                <div class="highlight-score-wrapper">
                  <span class="highlight-score" v-count-up="item.score">0</span>
                  <span class="highlight-unit">分</span>
                </div>
              </div>
              <div class="highlight-rank">TOP {{ item.rank }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 各维度详情 -->
      <div class="profile-section" :class="{ 'animate-in': mounted }">
        <div class="card-bg-pattern"></div>
        <h3 class="section-title">
          <i class="el-icon-data-line"></i>
          各维度能力分析
        </h3>
        <div class="dimension-grid">
          <div
            v-for="(dimension, index) in abilityDimensions"
            :key="index"
            class="dimension-card"
            :style="{ '--accent-color': dimension.color, animationDelay: (index * 0.08) + 's' }"
            @click="expandDimension(dimension)"
            :class="{ expanded: expandedDimension === dimension.name }"
          >
            <div class="card-shine"></div>
            <div class="dimension-top">
              <div class="dimension-icon" :style="{ background: `linear-gradient(135deg, ${dimension.color}, ${dimension.color}aa)` }">
                <i :class="dimension.icon"></i>
              </div>
              <div class="dimension-info">
                <span class="dimension-name">{{ dimension.name }}</span>
                <div class="dimension-trend" :class="dimension.trend > 0 ? 'up' : 'down'">
                  <i :class="dimension.trend > 0 ? 'el-icon-top' : 'el-icon-bottom'"></i>
                  {{ Math.abs(dimension.trend) }}%
                </div>
              </div>
              <div class="expand-icon">
                <i class="el-icon-arrow-right"></i>
              </div>
            </div>
            <div class="dimension-ring">
              <svg viewBox="0 0 100 100">
                <circle class="ring-bg" cx="50" cy="50" r="40" />
                <circle
                  class="ring-progress"
                  cx="50" cy="50" r="40"
                  :stroke-dasharray="251 * dimension.avgScore / 100 + ' 251'"
                />
              </svg>
              <div class="ring-center">
                <span class="ring-score" v-count-up="dimension.avgScore">0</span>
                <span class="ring-label">分</span>
              </div>
            </div>
            <div class="dimension-chart" v-if="expandedDimension === dimension.name">
              <div class="mini-chart" :id="'miniChart' + index"></div>
            </div>
            <div class="dimension-stats">
              <div class="stat">
                <span class="stat-label">最高</span>
                <span class="stat-value">{{ dimension.maxScore }}</span>
                <div class="stat-bar">
                  <div class="stat-bar-fill" :style="{ width: dimension.maxScore + '%', background: dimension.color }"></div>
                </div>
              </div>
              <div class="stat">
                <span class="stat-label">最低</span>
                <span class="stat-value">{{ dimension.minScore }}</span>
                <div class="stat-bar">
                  <div class="stat-bar-fill" :style="{ width: dimension.minScore + '%', background: dimension.color }"></div>
                </div>
              </div>
              <div class="stat">
                <span class="stat-label">次数</span>
                <span class="stat-value">{{ dimension.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 综合评分趋势 -->
      <div class="profile-section trend-section" :class="{ 'animate-in': mounted }">
        <div class="card-bg-pattern"></div>
        <div class="section-header">
          <h3 class="section-title">
            <i class="el-icon-data-analysis"></i>
            成长轨迹
          </h3>
          <div class="trend-period">
            <button 
              v-for="period in periods" 
              :key="period.value"
              class="period-btn"
              :class="{ active: selectedPeriod === period.value }"
              @click="changePeriod(period.value)"
            >
              {{ period.label }}
            </button>
          </div>
        </div>
        <div class="trend-chart" id="trendChart"></div>
        <div class="trend-summary">
          <div class="summary-item">
            <div class="summary-icon up">
              <i class="el-icon-top"></i>
            </div>
            <div class="summary-info">
              <span class="summary-value">+{{ trendData.improvement }}分</span>
              <span class="summary-label">较上周期提升</span>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-icon stable">
              <i class="el-icon-minus"></i>
            </div>
            <div class="summary-info">
              <span class="summary-value">{{ trendData.avgScore }}分</span>
              <span class="summary-label">平均得分</span>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-icon star">
              <i class="el-icon-star-on"></i>
            </div>
            <div class="summary-info">
              <span class="summary-value">{{ trendData.bestScore }}分</span>
              <span class="summary-label">历史最高</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 能力提升 -->
      <div class="profile-section improvement-section" :class="{ 'animate-in': mounted }">
        <div class="card-bg-pattern"></div>
        <h3 class="section-title">
          <i class="el-icon-guide"></i>
          专属提升方案
        </h3>
        <div class="improvement-cards">
          <div
            v-for="(path, index) in improvementPaths"
            :key="index"
            class="improvement-card"
            :style="{ '--card-color': path.color, animationDelay: (index * 0.12) + 's' }"
            @mouseenter="hoverCard(path)"
            @mouseleave="leaveCard"
          >
            <div class="card-glow" :style="{ background: `radial-gradient(circle at 20% 50%, ${path.color}33, transparent 60%)` }"></div>
            <div class="card-header">
              <div class="card-icon" :style="{ background: `linear-gradient(135deg, ${path.color}, ${path.color}aa)` }">
                <i :class="path.icon"></i>
              </div>
              <div class="card-title">
                <h4>{{ path.title }}</h4>
                <span class="card-subtitle">{{ path.subtitle }}</span>
              </div>
              <div class="priority-indicator">
                <div class="priority-bar" :class="path.priority" :style="{ width: (path.priority === 'high' ? '100%' : path.priority === 'medium' ? '66%' : '33%') }"></div>
              </div>
              <div class="priority-tag" :class="path.priority">{{ path.priorityText }}</div>
            </div>
            <p class="card-desc">{{ path.description }}</p>
            <div class="card-tasks">
              <div class="task-header">
                <i class="el-icon-check"></i>
                <span>推荐任务</span>
                <span class="task-count">{{ path.tasks.length }}项</span>
              </div>
              <div class="task-list">
                <span 
                  v-for="(task, tIndex) in path.tasks" 
                  :key="tIndex" 
                  class="task-item"
                  :style="{ animationDelay: (tIndex * 0.05) + 's' }"
                >
                  <span class="task-number">{{ tIndex + 1 }}</span>
                  {{ task }}
                </span>
              </div>
            </div>
            <div class="card-footer">
              <div class="duration">
                <i class="el-icon-time"></i>
                <span>{{ path.duration }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'PersonalAbilityProfile',
  props: {
    interviewHistory: {
      type: Array,
      default: () => []
    }
  },
  directives: {
    countUp: {
      mounted(el, binding) {
        const target = binding.value
        const duration = 1500
        const start = 0
        const startTime = performance.now()
        
        const animate = (currentTime) => {
          const elapsed = currentTime - startTime
          const progress = Math.min(elapsed / duration, 1)
          const easeOut = 1 - Math.pow(1 - progress, 3)
          const current = Math.floor(start + (target - start) * easeOut)
          el.textContent = current
          
          if (progress < 1) {
            requestAnimationFrame(animate)
          } else {
            el.textContent = target
          }
        }
        
        requestAnimationFrame(animate)
      }
    }
  },
  data() {
    return {
      mounted: false,
      displayScore: 0,
      isRefreshing: false,
      expandedDimension: null,
      selectedPeriod: 'month',
      periods: [
        { label: '周', value: 'week' },
        { label: '月', value: 'month' },
        { label: '季', value: 'quarter' }
      ],
      overallScore: 83,
      totalInterviews: 12,
      improvementRate: 15,
      rankPercent: 23,
      updateTime: new Date().toLocaleDateString(),
      statsData: [
        { label: '提升幅度', value: 15, prefix: '', suffix: '%' },
        { label: '排名', value: 23, prefix: 'TOP ', suffix: '%' }
      ],
      topAbilities: [
        { name: '言语表达', score: 92, icon: 'el-icon-microphone', color: '#409EFF', rank: 1 },
        { name: '项目经验', score: 90, icon: 'el-icon-folder', color: '#67C23A', rank: 2 },
        { name: '应急应变', score: 88, icon: 'el-icon-warning', color: '#E6A23C', rank: 3 }
      ],
      abilityDimensions: [
        { name: '综合分析', avgScore: 82, maxScore: 90, minScore: 75, count: 8, trend: 12, icon: 'el-icon-connection', color: '#409EFF' },
        { name: '组织协调', avgScore: 78, maxScore: 85, minScore: 70, count: 8, trend: 8, icon: 'el-icon-menu', color: '#67C23A' },
        { name: '应急应变', avgScore: 85, maxScore: 92, minScore: 78, count: 8, trend: 15, icon: 'el-icon-lightning', color: '#E6A23C' },
        { name: '技术能力', avgScore: 80, maxScore: 88, minScore: 72, count: 8, trend: 10, icon: 'el-icon-cpu', color: '#F56C6C' },
        { name: '言语表达', avgScore: 92, maxScore: 95, minScore: 85, count: 8, trend: 18, icon: 'el-icon-microphone', color: '#909399' },
        { name: '项目经验', avgScore: 90, maxScore: 95, minScore: 82, count: 8, trend: 5, icon: 'el-icon-folder', color: '#7C3AED' }
      ],
      trendData: {
        improvement: 15,
        avgScore: 78,
        bestScore: 92
      },
      improvementPaths: [
        {
          title: '综合分析能力提升',
          subtitle: '强化问题拆解能力',
          description: '通过系统学习与专项训练，提升对复杂问题的分析深度和广度，培养结构化思维能力',
          icon: 'el-icon-data-analysis',
          color: '#409EFF',
          priority: 'high',
          priorityText: '高优先级',
          tasks: ['每日新闻深度分析', 'MECE原则学习', '逻辑树练习', '案例拆解训练'],
          duration: '4周'
        },
        {
          title: '组织协调能力强化',
          subtitle: '提升团队管理技巧',
          description: '学习大型活动策划与资源调配技巧，提升跨部门沟通与团队协调能力',
          icon: 'el-icon-s-management',
          color: '#67C23A',
          priority: 'medium',
          priorityText: '中优先级',
          tasks: ['活动策划案练习', '资源调配模拟', '沟通技巧学习', '冲突管理训练'],
          duration: '3周'
        },
        {
          title: '应急应变能力突破',
          subtitle: '快速反应与决策',
          description: '通过高压场景模拟训练，提高快速反应能力和问题解决效率',
          icon: 'el-icon-lightning',
          color: '#E6A23C',
          priority: 'medium',
          priorityText: '中优先级',
          tasks: ['压力面试模拟', '快速决策练习', '应急场景演练', '时间管理训练'],
          duration: '3周'
        }
      ]
    }
  },
  computed: {
    levelClass() {
      if (this.overallScore >= 90) return 'excellent'
      if (this.overallScore >= 80) return 'good'
      if (this.overallScore >= 70) return 'average'
      return 'poor'
    },
    levelText() {
      if (this.overallScore >= 90) return '优秀'
      if (this.overallScore >= 80) return '良好'
      if (this.overallScore >= 70) return '中等'
      return '待提升'
    },
    levelIcon() {
      if (this.overallScore >= 90) return 'el-icon-crown'
      if (this.overallScore >= 80) return 'el-icon-star-on'
      if (this.overallScore >= 70) return 'el-icon-circle-check'
      return 'el-icon-warning'
    },
    levelDesc() {
      if (this.overallScore >= 90) return '恭喜！您的综合能力已达到优秀水平，继续保持！'
      if (this.overallScore >= 80) return '表现良好，还有提升空间，继续加油！'
      if (this.overallScore >= 70) return '处于中等水平，建议针对短板进行专项提升'
      return '需要加强基础能力，建议从提升计划开始'
    }
  },
  mounted() {
    setTimeout(() => {
      this.mounted = true
    }, 100)
    this.loadAbilityProfile()
    this.$nextTick(() => {
      this.initRadarChart()
      this.initTrendChart()
      this.animateScore()
    })
  },
  methods: {
    async loadAbilityProfile() {
      const userData = localStorage.getItem('userData')
      if (!userData) return

      const user = JSON.parse(userData)
      if (!user.id) return

      try {
        const response = await fetch(`/api/admin/user/${user.id}/ability-profile`)
        const data = await response.json()

        if (data.success) {
          this.totalInterviews = data.interviewCount || 0
          this.overallScore = data.avgScore || 0
          this.updateTime = new Date().toLocaleDateString()

          const improvementRate = this.totalInterviews > 0 ? Math.min(Math.round((this.overallScore / 100) * 20), 100) : 0
          const rankPercent = this.totalInterviews > 0 ? Math.max(100 - this.totalInterviews * 5, 1) : 99

          this.statsData = [
            { label: '提升幅度', value: improvementRate, prefix: '', suffix: '%' },
            { label: '排名', value: rankPercent, prefix: 'TOP ', suffix: '%' }
          ]

          this.$nextTick(() => {
            this.animateScore()
          })
        }
      } catch (error) {
        console.error('加载能力档案失败:', error)
      }
    },
    animateScore() {
      const target = this.overallScore
      const duration = 1500
      const startTime = performance.now()
      
      const animate = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / duration, 1)
        const easeOut = 1 - Math.pow(1 - progress, 3)
        this.displayScore = Math.floor(target * easeOut)
        
        if (progress < 1) {
          requestAnimationFrame(animate)
        } else {
          this.displayScore = target
        }
      }
      
      requestAnimationFrame(animate)
    },
    refreshData() {
      this.isRefreshing = true
      setTimeout(() => {
        this.isRefreshing = false
        this.$message.success('数据已刷新')
      }, 1000)
    },
    expandDimension(dimension) {
      if (this.expandedDimension === dimension.name) {
        this.expandedDimension = null
      } else {
        this.expandedDimension = dimension.name
        this.$nextTick(() => {
          const index = this.abilityDimensions.indexOf(dimension)
          this.initMiniChart(index, dimension)
        })
      }
    },
    highlightDimension(index) {
      const chart = echarts.getInstanceByDom(document.getElementById('radarChart'))
      if (chart) {
        chart.dispatchAction({
          type: 'highlight',
          seriesIndex: 0,
          dataIndex: index
        })
      }
    },
    unhighlightDimension() {
      const chart = echarts.getInstanceByDom(document.getElementById('radarChart'))
      if (chart) {
        chart.dispatchAction({
          type: 'downplay',
          seriesIndex: 0
        })
      }
    },
    hoverCard(path) {
      path.isHovered = true
    },
    leaveCard(path) {
      path.isHovered = false
    },
    changePeriod(period) {
      this.selectedPeriod = period
      this.initTrendChart()
    },
    initMiniChart(index, dimension) {
      const chartDom = document.getElementById('miniChart' + index)
      if (!chartDom) return

      const chart = echarts.init(chartDom)
      const option = {
        grid: {
          left: '10%',
          right: '10%',
          top: '10%',
          bottom: '10%'
        },
        xAxis: {
          type: 'category',
          data: ['第1次', '第2次', '第3次', '第4次'],
          show: false
        },
        yAxis: {
          type: 'value',
          show: false,
          min: 60
        },
        series: [{
          type: 'line',
          smooth: true,
          data: [dimension.minScore, dimension.minScore + 5, dimension.minScore + 8, dimension.avgScore],
          lineStyle: {
            color: dimension.color,
            width: 2
          },
          itemStyle: {
            color: dimension.color
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: dimension.color + '66' },
              { offset: 1, color: dimension.color + '11' }
            ])
          }
        }]
      }
      chart.setOption(option)
    },
    initRadarChart() {
      const chartDom = document.getElementById('radarChart')
      if (!chartDom) {
        console.error('radarChart DOM元素未找到')
        return
      }

      if (chartDom.clientWidth === 0 || chartDom.clientHeight === 0) {
        chartDom.style.width = '100%'
        chartDom.style.height = '320px'
        setTimeout(() => {
          this.initRadarChart()
        }, 100)
        return
      }

      const existingChart = echarts.getInstanceByDom(chartDom)
      if (existingChart) {
        existingChart.dispose()
      }

      const myChart = echarts.init(chartDom)
      
      const containerWidth = chartDom.clientWidth || 300
      const containerHeight = chartDom.clientHeight || 320
      
      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(15, 12, 41, 0.95)',
          borderColor: '#667eea',
          borderWidth: 1,
          textStyle: {
            color: '#e0e2ea',
            fontSize: 12
          },
          padding: [10, 14]
        },
        legend: {
          show: false
        },
        radar: {
          indicator: [
            { name: '综合分析', max: 100 },
            { name: '组织协调', max: 100 },
            { name: '应急应变', max: 100 },
            { name: '技术能力', max: 100 },
            { name: '言语表达', max: 100 },
            { name: '项目经验', max: 100 }
          ],
          shape: 'polygon',
          splitNumber: 5,
          center: ['50%', '50%'],
          radius: '65%',
          axisName: {
            color: '#a0a3b1',
            fontSize: 12,
            fontWeight: 600,
            padding: [5, 10]
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: 'rgba(102, 126, 234, 0.2)',
              width: 1,
              type: 'dashed'
            }
          },
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(15, 12, 41, 0.5)', 'rgba(48, 43, 99, 0.4)', 'rgba(36, 36, 62, 0.3)', 'rgba(48, 43, 99, 0.2)', 'rgba(15, 12, 41, 0.1)']
            }
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: 'rgba(102, 126, 234, 0.3)',
              width: 1
            }
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [82, 78, 85, 80, 92, 90],
            name: '能力评估',
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              color: '#667eea',
              width: 2
            },
            areaStyle: {
              color: 'rgba(102, 126, 234, 0.3)'
            },
            itemStyle: {
              color: '#667eea',
              borderColor: '#fff',
              borderWidth: 2
            }
          }]
        }],
        animation: true,
        animationDuration: 1500,
        animationEasing: 'cubicOut'
      }

      myChart.setOption(option)
      
      window.addEventListener('resize', () => {
        myChart.resize()
      })
    },
    initTrendChart() {
      const chartDom = document.getElementById('trendChart')
      if (!chartDom) return

      if (chartDom.clientWidth === 0 || chartDom.clientHeight === 0) {
        chartDom.style.width = '100%'
        chartDom.style.height = '280px'
        setTimeout(() => {
          this.initTrendChart()
        }, 100)
        return
      }

      const myChart = echarts.init(chartDom)
      
      let dates, scores
      if (this.selectedPeriod === 'week') {
        dates = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        scores = [75, 78, 76, 82, 85, 83, 88]
      } else if (this.selectedPeriod === 'month') {
        dates = ['第1周', '第2周', '第3周', '第4周', '第5周', '第6周']
        scores = [68, 72, 75, 78, 80, 83]
      } else {
        dates = ['Q1', 'Q2', 'Q3', 'Q4']
        scores = [70, 75, 80, 85]
      }

      const option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(15, 12, 41, 0.98)',
          borderColor: '#667eea',
          borderWidth: 1,
          textStyle: {
            color: '#e0e2ea'
          },
          extraCssText: 'box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3); border-radius: 12px; padding: 12px 16px;',
          formatter: function(params) {
            const item = params[0]
            return `<div style="padding: 4px 8px;">
              <div style="font-weight: 600; margin-bottom: 4px; color: #a0a3b1;">${item.axisValue}</div>
              <div style="color: #67C23A; font-size: 20px; font-weight: bold;">${item.value}分</div>
            </div>`
          }
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
          boundaryGap: false,
          data: dates,
          axisLine: {
            lineStyle: {
              color: 'rgba(102, 126, 234, 0.3)'
            }
          },
          axisLabel: {
            color: '#a0a3b1',
            fontWeight: 500
          }
        },
        yAxis: {
          type: 'value',
          min: 60,
          max: 100,
          axisLine: {
            show: false
          },
          axisLabel: {
            color: '#909399'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(102, 126, 234, 0.1)',
              type: 'dashed'
            }
          }
        },
        series: [{
          name: '综合评分',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 10,
          data: scores,
          lineStyle: {
            color: '#667eea',
            width: 3,
            shadowColor: 'rgba(102, 126, 234, 0.4)',
            shadowBlur: 12
          },
          itemStyle: {
            color: '#667eea',
            borderColor: '#fff',
            borderWidth: 3,
            shadowColor: 'rgba(102, 126, 234, 0.4)',
            shadowBlur: 10
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(102, 126, 234, 0.4)' },
              { offset: 0.5, color: 'rgba(102, 126, 234, 0.15)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.02)' }
            ])
          },
          markPoint: {
            symbol: 'pin',
            symbolSize: 60,
            data: [
              { type: 'max', name: '最高分', itemStyle: { color: '#667eea' }, label: { color: '#fff', fontWeight: 'bold', fontSize: 12 } }
            ]
          }
        }]
      }

      myChart.setOption(option)

      window.addEventListener('resize', () => {
        myChart.resize()
      })
    }
  }
}
</script>

<style scoped>
.main-content {
  position: relative;
  padding: 20px;
  padding-bottom: 30px;
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

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  position: relative;
  z-index: 2;
}

.back-btn {
  cursor: pointer;
  font-size: 20px;
  color: #a0a3b1;
  width: 60px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  color: #667eea;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.record-title {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
  text-align: center;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.empty {
  width: 60px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 16px;
  position: relative;
  z-index: 2;
}

.animate-in {
  animation: slideUp 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.overall-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 28px;
  display: flex;
  gap: 28px;
  color: white;
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
}

.card-bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.25) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.2) 0%, transparent 40%),
    linear-gradient(45deg, transparent 48%, rgba(255, 255, 255, 0.15) 49%, rgba(255, 255, 255, 0.15) 51%, transparent 52%),
    radial-gradient(circle at 50% 50%, transparent 0%, rgba(102, 126, 234, 0.1) 100%),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 50px,
      rgba(102, 126, 234, 0.08) 50px,
      rgba(102, 126, 234, 0.08) 51px
    );
  background-size: 100% 100%, 100% 100%, 25px 25px, 100% 100%, 100% 100%;
  pointer-events: none;
  z-index: 0;
}

.overall-left,
.overall-right,
.section-header,
.ability-content,
.dimension-grid,
.trend-chart,
.trend-summary,
.improvement-cards {
  position: relative;
  z-index: 1;
}

.card-corner-decoration {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  pointer-events: none;
  z-index: 0;
}

.card-corner-decoration.top-left {
  top: 10px;
  left: 10px;
  border-right: none;
  border-bottom: none;
}

.card-corner-decoration.top-right {
  top: 10px;
  right: 10px;
  border-left: none;
  border-bottom: none;
}

.card-corner-decoration.bottom-left {
  bottom: 10px;
  left: 10px;
  border-right: none;
  border-top: none;
}

.card-corner-decoration.bottom-right {
  bottom: 10px;
  right: 10px;
  border-left: none;
  border-top: none;
}

.deco-line {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
  animation: lineGlow 3s ease-in-out infinite;
}

@keyframes lineGlow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; }
}

.overall-left {
  flex-shrink: 0;
}

.overall-score-ring {
  position: relative;
  width: 130px;
  height: 130px;
}

.score-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
}

.score-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.2);
  stroke-width: 12;
}

.score-progress {
  fill: none;
  stroke: url(#scoreGradient);
  stroke-width: 12;
  stroke-linecap: round;
  stroke-dasharray: 0 283;
  transition: stroke-dasharray 1.5s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 2px 6px rgba(246, 211, 101, 0.4));
}

.score-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-number {
  display: block;
  font-size: 42px;
  font-weight: bold;
  line-height: 1;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.score-label {
  font-size: 13px;
  opacity: 0.9;
}

.score-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; }
}

.overall-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  z-index: 1;
}

.level-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 18px;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  margin-bottom: 10px;
  width: fit-content;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.level-badge::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.4) 0%, transparent 40%),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 8px,
      rgba(255, 255, 255, 0.15) 8px,
      rgba(255, 255, 255, 0.15) 9px
    );
  background-size: 100% 100%, 25px 25px;
  pointer-events: none;
}

.level-badge.excellent { background: linear-gradient(135deg, #f6d365, #fda085); }
.level-badge.good { background: rgba(255, 255, 255, 0.3); }
.level-badge.average { background: rgba(255, 255, 255, 0.2); }
.level-badge.poor { background: rgba(255, 255, 255, 0.15); }

.badge-icon {
  display: flex;
  align-items: center;
}

.level-desc {
  font-size: 14px;
  opacity: 0.95;
  margin: 0 0 18px 0;
  line-height: 1.6;
}

.history-stats {
  display: flex;
  gap: 28px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  animation: fadeIn 0.5s ease-out forwards;
  opacity: 0;
}

.stat-value {
  font-size: 22px;
  font-weight: bold;
  display: flex;
  align-items: baseline;
}

.stat-prefix {
  font-size: 14px;
  margin-right: 2px;
}

.stat-suffix {
  font-size: 14px;
  margin-left: 2px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

.card-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.deco-1 {
  width: 120px;
  height: 120px;
  top: -40px;
  right: -20px;
  animation: float 6s ease-in-out infinite;
}

.deco-2 {
  width: 80px;
  height: 80px;
  top: 20px;
  right: 60px;
  animation: float 5s ease-in-out infinite 1s;
}

.deco-3 {
  width: 50px;
  height: 50px;
  bottom: 20px;
  right: 40px;
  animation: float 4s ease-in-out infinite 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.ability-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  color: #e0e2ea;
  margin: 0;
}

.section-title i {
  color: #667eea;
  font-size: 20px;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.update-time {
  font-size: 13px;
  color: #a0a3b1;
  display: flex;
  align-items: center;
  gap: 4px;
}

.refresh-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.refresh-btn:hover {
  background: rgba(102, 126, 234, 0.2);
}

.refresh-btn i {
  font-size: 16px;
  color: #a0a3b1;
}

.refresh-btn i.is-rotating {
  animation: rotate 1s linear infinite;
  color: #667eea;
}

.ability-content {
  display: flex;
  gap: 28px;
  align-items: stretch;
}

.radar-chart {
  flex: 1;
  height: 320px;
  min-height: 320px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 16px;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.radar-chart > div {
  width: 100% !important;
  height: 100% !important;
}

.ability-highlights {
  width: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
}

.highlight-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 14px;
  border-left: 4px solid;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease-out forwards;
  opacity: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.highlight-item:hover {
  transform: translateX(6px) scale(1.02);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
}

.highlight-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.highlight-icon i {
  font-size: 20px;
  color: white;
}

.highlight-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.highlight-name {
  font-size: 13px;
  color: #a0a3b1;
}

.highlight-score-wrapper {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.highlight-score {
  font-size: 22px;
  font-weight: bold;
  color: #e0e2ea;
}

.highlight-unit {
  font-size: 12px;
  color: #909399;
}

.highlight-rank {
  font-size: 11px;
  color: #c0c4cc;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}

.profile-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.dimension-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  animation: scaleIn 0.5s ease-out forwards;
  opacity: 0;
  backdrop-filter: blur(10px);
}

.dimension-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 15% 20%, var(--accent-color, #667eea) 0%, transparent 25%),
    linear-gradient(135deg, transparent 48%, var(--accent-color, #667eea) 49%, var(--accent-color, #667eea) 51%, transparent 52%),
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 20px,
      rgba(255, 255, 255, 0.05) 20px,
      rgba(255, 255, 255, 0.05) 21px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 25px,
      var(--accent-color, #667eea) 25px,
      var(--accent-color, #667eea) 26px
    );
  background-size: 100% 100%, 25px 25px, 100% 100%, 50px 50px;
  opacity: 0.2;
  pointer-events: none;
  z-index: 0;
}

.dimension-top,
.dimension-ring,
.dimension-chart,
.dimension-stats {
  position: relative;
  z-index: 1;
}

.dimension-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--accent-color);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.dimension-card:hover::before,
.dimension-card.expanded::before {
  transform: scaleX(1);
}

.dimension-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.2);
  border-color: var(--accent-color);
}

.dimension-card.expanded {
  grid-column: span 1;
}

.card-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 40%,
    rgba(255, 255, 255, 0.1) 50%,
    transparent 60%
  );
  transform: translateX(-100%);
  transition: transform 0.6s ease;
  pointer-events: none;
}

.dimension-card:hover .card-shine {
  transform: translateX(100%);
}

.dimension-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.dimension-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.dimension-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3) 0%, transparent 50%),
    linear-gradient(45deg, transparent 48%, rgba(255, 255, 255, 0.15) 49%, rgba(255, 255, 255, 0.15) 51%, transparent 52%);
  background-size: 100% 100%, 20px 20px;
  pointer-events: none;
}

.dimension-icon::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 40%,
    rgba(255, 255, 255, 0.25) 50%,
    transparent 60%
  );
  transform: translateX(-100%);
  transition: transform 0.5s ease;
  pointer-events: none;
}

.dimension-card:hover .dimension-icon::after {
  transform: translateX(100%);
}

.dimension-icon i {
  font-size: 20px;
  color: white;
}

.dimension-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dimension-name {
  font-size: 15px;
  font-weight: 600;
  color: #e0e2ea;
}

.dimension-trend {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 6px;
  width: fit-content;
}

.dimension-trend.up {
  color: #67C23A;
  background: rgba(103, 194, 58, 0.2);
}

.dimension-trend.down {
  color: #F56C6C;
  background: rgba(245, 108, 108, 0.2);
}

.expand-icon {
  color: #c0c4cc;
  transition: all 0.3s ease;
}

.dimension-card:hover .expand-icon,
.dimension-card.expanded .expand-icon {
  color: var(--accent-color);
  transform: rotate(90deg);
}

.dimension-ring {
  position: relative;
  width: 90px;
  height: 90px;
  margin: 0 auto 16px;
}

.dimension-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 10;
}

.ring-progress {
  fill: none;
  stroke: var(--accent-color);
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dasharray 1.5s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 2px 6px currentColor);
}

.ring-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.ring-score {
  font-size: 24px;
  font-weight: bold;
  color: var(--accent-color);
}

.ring-label {
  font-size: 12px;
  color: #909399;
}

.dimension-chart {
  height: 80px;
  margin-bottom: 12px;
}

.mini-chart {
  width: 100%;
  height: 100%;
}

.dimension-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.dimension-stats .stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.dimension-stats .stat-label {
  font-size: 11px;
  color: #909399;
}

.dimension-stats .stat-value {
  font-size: 15px;
  font-weight: 600;
  color: #e0e2ea;
}

.stat-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}

.stat-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease;
}

.trend-section {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.trend-period {
  display: flex;
  gap: 6px;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.period-btn {
  padding: 6px 14px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #a0a3b1;
  transition: all 0.3s ease;
}

.period-btn:hover {
  color: #667eea;
}

.period-btn.active {
  background: rgba(102, 126, 234, 0.3);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  font-weight: 500;
}

.trend-chart {
  width: 100%;
  height: 280px;
}

.trend-summary {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-icon.up {
  background: rgba(103, 194, 58, 0.2);
  color: #67C23A;
}

.summary-icon.stable {
  background: rgba(144, 147, 153, 0.2);
  color: #909399;
}

.summary-icon.star {
  background: linear-gradient(135deg, #f6d365, #fda085);
  color: white;
}

.summary-icon i {
  font-size: 18px;
}

.summary-info {
  display: flex;
  flex-direction: column;
}

.summary-value {
  font-size: 18px;
  font-weight: bold;
  color: #e0e2ea;
}

.summary-label {
  font-size: 12px;
  color: #909399;
}

.improvement-section {
  padding: 24px;
}

.improvement-cards {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.improvement-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 18px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
  animation: fadeIn 0.5s ease-out forwards;
  opacity: 0;
  backdrop-filter: blur(10px);
}

.improvement-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 25% 75%, var(--card-color, #667eea) 0%, transparent 30%),
    radial-gradient(circle at 75% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 30%),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 8px,
      var(--card-color, #667eea) 8px,
      var(--card-color, #667eea) 9px
    ),
    repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 8px,
      rgba(255, 255, 255, 0.08) 8px,
      rgba(255, 255, 255, 0.08) 9px
    );
  background-size: 100% 100%, 100% 100%, 20px 20px, 20px 20px;
  opacity: 0.18;
  pointer-events: none;
  z-index: 0;
}

.card-header,
.card-desc,
.card-tasks,
.card-footer {
  position: relative;
  z-index: 1;
}

.improvement-card:hover {
  transform: translateX(8px);
  box-shadow: 0 12px 36px rgba(102, 126, 234, 0.2);
  border-color: var(--card-color);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.improvement-card:hover .card-glow {
  opacity: 1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
  position: relative;
  z-index: 1;
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.card-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.35) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.2) 0%, transparent 45%),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(255, 255, 255, 0.12) 10px,
      rgba(255, 255, 255, 0.12) 11px
    );
  background-size: 100% 100%, 100% 100%, 30px 30px;
  pointer-events: none;
}

.card-icon::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 40%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 60%
  );
  transform: translateX(-100%);
  transition: transform 0.5s ease;
  pointer-events: none;
}

.improvement-card:hover .card-icon::after {
  transform: translateX(100%);
}

.card-icon i {
  font-size: 26px;
  color: white;
}

.card-title {
  flex: 1;
}

.card-title h4 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #e0e2ea;
}

.card-subtitle {
  font-size: 13px;
  color: #909399;
}

.priority-indicator {
  width: 60px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.priority-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.priority-bar.high { background: #F56C6C; }
.priority-bar.medium { background: #E6A23C; }
.priority-bar.low { background: #909399; }

.priority-tag {
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.priority-tag.high {
  background: rgba(245, 108, 108, 0.2);
  color: #F56C6C;
}

.priority-tag.medium {
  background: rgba(230, 162, 60, 0.2);
  color: #E6A23C;
}

.priority-tag.low {
  background: rgba(144, 147, 153, 0.2);
  color: #909399;
}

.card-desc {
  font-size: 14px;
  color: #a0a3b1;
  line-height: 1.7;
  margin: 0 0 18px 0;
  position: relative;
  z-index: 1;
}

.card-tasks {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 18px;
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.task-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #e0e2ea;
  margin-bottom: 12px;
}

.task-header i {
  color: #67C23A;
}

.task-count {
  margin-left: auto;
  font-size: 12px;
  font-weight: normal;
  color: #909399;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}

.task-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #a0a3b1;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 8px;
  animation: fadeIn 0.3s ease-out forwards;
  opacity: 0;
}

.task-item:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.task-number {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--card-color, #409EFF);
  color: white;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 1;
  padding-top: 8px;
}

.duration {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #a0a3b1;
  padding: 10px 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.duration i {
  color: #667eea;
  font-size: 18px;
}

.card-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 30% 50%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
    linear-gradient(45deg, transparent 48%, rgba(255, 255, 255, 0.1) 49%, rgba(255, 255, 255, 0.1) 51%, transparent 52%);
  background-size: 100% 100%, 15px 15px;
  pointer-events: none;
}

.action-btn::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 40%,
    rgba(255, 255, 255, 0.2) 50%,
    transparent 60%
  );
  transform: translateX(-100%);
  transition: transform 0.4s ease;
  pointer-events: none;
}

.action-btn:hover::after {
  transform: translateX(100%);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #a0a3b1;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #e0e2ea;
}

.action-btn.primary {
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.action-btn i {
  font-size: 14px;
}

@media (max-width: 768px) {
  .overall-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 24px;
  }

  .history-stats {
    justify-content: center;
  }

  .ability-content {
    flex-direction: column;
  }

  .ability-highlights {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .dimension-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .trend-summary {
    flex-wrap: wrap;
    gap: 20px;
  }
}
</style>
