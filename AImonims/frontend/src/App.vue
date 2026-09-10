<template>
  <div class="app-container">
    <!-- 登录页面 -->
    <LoginPage
      v-if="!isLoggedIn"
      @login-success="handleLoginSuccess"
      @go-register="handleGoRegister"
    />

    <!-- 注册对话框 -->
    <el-dialog
      v-model="showRegisterDialog"
      title="注册"
      width="420px"
      center
      class="register-dialog"
    >
      <div class="register-form">
        <el-form :model="registerForm">
          <el-form-item label="用户名">
            <el-input v-model="registerForm.username" placeholder="请输入用户名" class="black-text-input"></el-input>
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" class="black-text-input"></el-input>
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" class="black-text-input"></el-input>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="register">注册</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 已登录用户显示主界面 -->
    <template v-if="isLoggedIn">
    <!-- 欢迎区域 -->
    <div v-show="currentPage === 'home'" class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-greeting">
          <span class="greeting-text">欢迎回来，</span>
          <span class="username">{{ userInfo.username }}</span>
        </div>
        <div class="typewriter-container">
          <span class="typewriter-text">{{ typewriterText }}</span>
          <span class="cursor">|</span>
        </div>
        <div class="welcome-stats">
          <div class="stat-item">
            <span class="stat-number">{{ interviewHistory.length }}</span>
            <span class="stat-label">面试次数</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">0</span>
            <span class="stat-label">收藏内容</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">∞</span>
            <span class="stat-label">无限可能</span>
          </div>
        </div>
      </div>
      <div class="welcome-decoration">
        <div class="deco-ring ring-1"></div>
        <div class="deco-ring ring-2"></div>
        <div class="deco-ring ring-3"></div>
      </div>
    </div>
    
    <!-- 首页 -->
    <HomePage
      v-show="currentPage === 'home'"
      :examQuestions="examQuestions"
      :searchQuery="searchQuery"
      :examSearchKeyword="examSearchKeyword"
      @function-click="handleFunctionClick"
      @random-question="handleRandomQuestion"
      @search="handleSearch"
      @search-exam="searchExamQuestions"
      @view-exam-question="viewExamQuestionDetail"
    />
    
    <!-- 模拟面试页面 -->
    <InterviewPage 
      v-show="currentPage === 'interview'"
      @voice-interview="handleVoiceInterview"
      @ai-interview="handleAIInterview"
      @avatar-interview="handleAvatarInterview"
      @history-click="handleHistoryClick"
    />
    
    <!-- AI面试配置页面 -->
    <AIInterviewConfig 
      v-show="currentPage === 'aiInterview'"
      :interviewType="interviewType"
      :initialFormData="aiInterviewForm"
      @back="currentPage = 'interview'"
      @history-click="handleHistoryClick"
      @start-interview="startAIInterview"
    />
    
    <!-- AI面试对话页面 -->
    <AIInterviewChat 
      ref="aiInterviewChatRef"
      v-show="currentPage === 'aiInterviewChat'"
      :interviewType="interviewType"
      :job="aiInterviewForm.job"
      :chatMessages="chatMessages"
      :currentQuestionIndex="currentQuestionIndex"
      :totalQuestions="totalQuestions"
      :currentInterviewId="currentInterviewId"
      :aiInterviewForm="aiInterviewForm"
      @back="currentPage = 'aiInterview'"
      @add-message="addMessage"
      @evaluation-complete="handleEvaluationComplete"
      @end="handleEndInterview"
    />
    
    <!-- 面试评估报告页面 -->
    <InterviewReport 
      v-show="currentPage === 'interviewReport'"
      :report="interviewReport"
      @back="currentPage = 'aiInterviewChat'"
      @restart="currentPage = 'aiInterview'"
      @view-plan="viewImprovementPlan"
      @back-home="currentPage = 'home'"
    />
    
    <!-- 能力提升计划页面 -->
    <ImprovementPlan 
      v-show="currentPage === 'improvementPlan'"
      :plan="improvementPlan"
      @back="currentPage = 'interviewReport'"
      @back-home="currentPage = 'home'"
    />
    
    <!-- 个人能力档案页面 -->
    <PersonalAbilityProfile
      v-show="currentPage === 'personalProfile'"
      :interview-history="interviewHistory"
      @back="currentPage = 'mine'"
    />

    <!-- 精选题库页面 -->
    <QuestionBank
      v-show="currentPage === 'questionBank'"
      @back="currentPage = 'home'"
    />

    <!-- 我的收藏页面 -->
    <FavoritesPage
      v-show="currentPage === 'favorites'"
      @back="currentPage = 'mine'"
    />

    <!-- 面试准备中心页面 -->
    <PrepCenter
      v-show="currentPage === 'prepCenter'"
      @back="currentPage = 'home'"
    />

    <!-- 面试记录页面 -->
    <div class="main-content" v-show="currentPage === 'interviewRecord'">
      <div class="record-header">
        <div class="back-btn" @click="currentPage = 'mine'">
          <i class="el-icon-arrow-left"></i>
        </div>
        <h2 class="record-title">面试记录</h2>
        <div class="empty"></div>
      </div>
      
      <div class="record-content">
        <div v-if="interviewHistory.length === 0" class="empty-record">
          <el-empty description="暂无面试记录"></el-empty>
        </div>
        <div v-else class="record-list">
          <div 
            v-for="(interview, index) in interviewHistory" 
            :key="interview.id"
            class="record-item"
          >
            <div class="record-info" @click="viewInterviewDetail(interview.id)">
              <h3 class="record-position">{{ interview.position }}</h3>
              <div class="record-meta">
                <span class="record-time">{{ interview.created_at }}</span>
                <span class="record-status" :class="interview.status">{{ interview.status === 'completed' ? '已完成' : '进行中' }}</span>
              </div>
              <div class="record-details">
                <span class="record-detail-item">
                  <i class="el-icon-suitcase"></i>
                  {{ interview.job_type || '未设置' }}
                </span>
                <span class="record-detail-item">
                  <i class="el-icon-time"></i>
                  {{ interview.experience || '未设置' }}
                </span>
                <span class="record-detail-item">
                  <i class="el-icon-user"></i>
                  {{ interview.interviewer_role || '未设置' }}
                </span>
              </div>
            </div>
            <div class="record-actions">
              <svg
                class="favorite-icon"
                :class="{ favorited: isInterviewFavorited(interview.id) }"
                @click.stop="handleToggleInterviewFavorite(interview)"
                :title="isInterviewFavorited(interview.id) ? '取消收藏' : '收藏'"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              <el-button
                type="danger"
                size="small"
                icon="el-icon-delete"
                @click.stop="deleteInterview(interview.id)"
              >删除</el-button>
              <div class="record-arrow">
                <i class="el-icon-arrow-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 面试详情页面 -->
    <div class="main-content" v-show="currentPage === 'interviewDetail'">
      <div class="record-header">
        <div class="back-btn" @click="currentPage = 'interviewRecord'">
          <i class="el-icon-arrow-left"></i>
        </div>
        <h2 class="record-title">面试详情</h2>
        <div class="empty"></div>
      </div>
      
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-content">
          <div class="loading-spinner">加载中...</div>
        </div>
      </div>
      
      <div v-else class="interview-detail-content">
        <!-- 面试基本信息 -->
        <div class="detail-section">
          <h3 class="section-title">基本信息</h3>
          <div class="detail-info">
            <div class="info-item">
              <span class="info-label">面试岗位：</span>
              <span class="info-value">{{ currentInterviewDetail?.position || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">面试时间：</span>
              <span class="info-value">{{ currentInterviewDetail?.created_at || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">面试状态：</span>
              <span class="info-value status-badge" :class="currentInterviewDetail?.status">{{ currentInterviewDetail?.status === 'completed' ? '已完成' : '进行中' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">岗位类型：</span>
              <span class="info-value">{{ currentInterviewDetail?.job_type || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">工作经验：</span>
              <span class="info-value">{{ currentInterviewDetail?.experience || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">面试官角色：</span>
              <span class="info-value">{{ currentInterviewDetail?.interviewer_role || '未设置' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 面试对话记录 -->
        <div class="detail-section">
          <h3 class="section-title">对话记录</h3>
          <div v-if="currentInterviewDetail?.messages?.length === 0" class="empty-messages">
            <el-empty description="暂无对话记录"></el-empty>
          </div>
          <div v-else class="messages-list">
            <div 
              v-for="(message, index) in currentInterviewDetail?.messages" 
              :key="index"
              :class="['message-item', message.sender]"
            >
              <div class="message-avatar">
                <img v-if="message.sender === 'ai'" src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20wearing%20glasses%20and%20suits&image_size=square" alt="AI面试官" class="avatar-img">
                <img v-else src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20avatar&image_size=square" alt="用户" class="avatar-img">
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ message.created_at }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 面试评估报告 -->
        <div v-if="currentInterviewDetail?.report" class="detail-section">
          <h3 class="section-title">评估报告</h3>
          <div class="report-summary">
            <div class="overall-score">
              <div class="score-circle">
                <span class="score-value">{{ currentInterviewDetail.report.overall_score }}</span>
                <span class="score-unit">分</span>
              </div>
              <div class="score-info">
                <div class="score-level">{{ currentInterviewDetail.report.overall_level }}</div>
                <div class="score-date">{{ currentInterviewDetail.report.timestamp }}</div>
              </div>
            </div>
            
            <div class="evaluation-grid">
              <div v-for="(result, criterion) in currentInterviewDetail.report.content_evaluation" :key="criterion" class="evaluation-item">
                <div class="evaluation-label">{{ result.comment }}</div>
                <div class="evaluation-score">{{ result.score }}分</div>
              </div>
              <div v-for="(result, item) in currentInterviewDetail.report.expression_evaluation" :key="item" class="evaluation-item">
                <div class="evaluation-label">{{ result.comment }}</div>
                <div class="evaluation-score">{{ result.score }}分</div>
              </div>
            </div>
            
            <div class="highlights-suggestions">
              <div class="highlights-list">
                <h4 class="list-title">亮点分析</h4>
                <div v-for="(highlight, index) in currentInterviewDetail.report.highlights" :key="index" class="highlight-item">
                  <i class="el-icon-check-circle"></i>
                  <span>{{ highlight }}</span>
                </div>
              </div>
              <div class="suggestions-list">
                <h4 class="list-title">改进建议</h4>
                <div v-for="(suggestion, index) in currentInterviewDetail.report.suggestions" :key="index" class="suggestion-item">
                  <i class="el-icon-warning-outline"></i>
                  <span>{{ suggestion }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 能力提升计划 -->
        <div v-if="currentInterviewDetail?.plan" class="detail-section">
          <h3 class="section-title">能力提升计划</h3>
          <div class="improvement-plan">
            <div class="weaknesses-list">
              <h4 class="list-title">能力短板</h4>
              <div v-for="(weakness, index) in currentInterviewDetail.plan.weaknesses" :key="index" class="weakness-item">
                <i class="el-icon-warning-outline"></i>
                <span>{{ weakness }}</span>
              </div>
            </div>
            
            <div class="suggestions-list">
              <h4 class="list-title">提升建议</h4>
              <div v-for="(suggestion, index) in currentInterviewDetail.plan.suggestions" :key="index" class="suggestion-item">
                <i class="el-icon-check-circle"></i>
                <span>{{ suggestion }}</span>
              </div>
            </div>
            
            <div class="resources-list">
              <h4 class="list-title">推荐学习资源</h4>
              <div v-for="(resource, index) in currentInterviewDetail.plan.resources" :key="index" class="resource-item">
                <i class="el-icon-document"></i>
                <span>{{ resource }}</span>
              </div>
            </div>
            
            <div class="learning-plan">
              <h4 class="list-title">30天学习计划</h4>
              <div v-for="(weekPlan, index) in currentInterviewDetail.plan.learning_plan" :key="index" class="week-plan">
                <div class="week-header">
                  <span class="week-number">第{{ weekPlan.week }}周</span>
                  <span class="week-title">{{ weekPlan.title }}</span>
                </div>
                <div class="week-tasks">
                  <div v-for="(task, taskIndex) in weekPlan.tasks" :key="taskIndex" class="task-item">
                    <i class="el-icon-right"></i>
                    <span>{{ task }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 简历评价 -->
        <div v-if="currentInterviewDetail?.resume_evaluation" class="detail-section">
          <h3 class="section-title">简历评价</h3>
          <div class="resume-evaluation">
            <div class="overall-score">
              <div class="score-circle resume-score">
                <span class="score-value">{{ currentInterviewDetail.resume_evaluation.overall_score }}</span>
                <span class="score-unit">分</span>
              </div>
              <div class="score-info">
                <div class="score-level">简历制作质量</div>
                <div class="score-date">{{ currentInterviewDetail.resume_evaluation.created_at || '刚刚完成评价' }}</div>
              </div>
            </div>
            
            <div class="dimensions-grid">
              <div v-for="(scoreData, dimensionKey) in currentInterviewDetail.resume_evaluation.dimensions" :key="dimensionKey" class="dimension-item">
                <div class="dimension-label">{{ getDimensionName(dimensionKey) }}</div>
                <div class="dimension-score-bar">
                  <div class="score-fill" :style="{ width: (scoreData.score * 10) + '%' }"></div>
                  <span class="score-text">{{ scoreData.score }}分</span>
                </div>
                <div class="dimension-comment">{{ scoreData.comment }}</div>
              </div>
            </div>
            
            <div class="strengths-improvements">
              <div class="strengths-section">
                <h4 class="list-title"><i class="el-icon-thumb"></i>简历亮点</h4>
                <div v-for="(strength, index) in currentInterviewDetail.resume_evaluation.strengths" :key="index" class="strength-item">
                  <i class="el-icon-check-circle"></i>
                  <span>{{ strength }}</span>
                </div>
              </div>
              <div class="improvements-section">
                <h4 class="list-title"><i class="el-icon-edit-outline"></i>改进建议</h4>
                <div v-for="(improvement, index) in currentInterviewDetail.resume_evaluation.improvements" :key="index" class="improvement-item">
                  <i class="el-icon-warning-outline"></i>
                  <span>{{ improvement }}</span>
                </div>
              </div>
            </div>
            
            <div class="template-suggestion">
              <h4 class="list-title"><i class="el-icon-document"></i>模板建议</h4>
              <div class="suggestion-content">{{ currentInterviewDetail.resume_evaluation.template_suggestion }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 个人中心页面 -->
    <div class="main-content mine-page" v-show="currentPage === 'mine'">
      <!-- 用户信息卡片 -->
      <div class="user-info-card" :class="{ 'animate-in': pageMounted }">
        <div class="card-decoration">
          <div class="deco-circle deco-1"></div>
          <div class="deco-circle deco-2"></div>
          <div class="deco-circle deco-3"></div>
        </div>
        <div class="user-info-content">
          <div class="avatar-wrapper">
            <div class="avatar-container">
              <img :src="userInfo.avatar" alt="用户头像" class="avatar-img">
              <div class="avatar-ring"></div>
            </div>
            <div class="level-badge">
              <span>Lv.{{ userLevel }}</span>
            </div>
          </div>
          <div class="user-details">
            <h3 class="username">{{ userInfo.username }}</h3>
            <div class="user-bio">
              <span class="bio-tag" v-if="isLoggedIn">
                <i class="el-icon-check"></i>
                已认证
              </span>
              <span class="bio-tag">
                <i class="el-icon-sunny"></i>
                积极成长中
              </span>
            </div>
            <div class="user-points">
              <div class="points-item">
                <span class="points-value">{{ userInfo.points }}</span>
                <span class="points-label">积分</span>
              </div>
              <div class="points-divider"></div>
              <div class="points-item">
                <span class="points-value">{{ interviewHistory.length }}</span>
                <span class="points-label">面试</span>
              </div>
              <div class="points-divider"></div>
              <div class="points-item">
                <span class="points-value">12</span>
                <span class="points-label">徽章</span>
              </div>
            </div>
          </div>
          <div class="user-actions">
            <button class="action-btn edit-btn" @click="currentPage = 'settings'">
              <i class="el-icon-edit"></i>
              <span>设置</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 数据统计卡片 -->
      <div class="stats-cards" :class="{ 'animate-in': pageMounted }">
        <div class="stat-card stat-1">
          <div class="stat-icon">
            <i class="el-icon-video-camera"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ animatedStats.interviewCount }}</span>
            <span class="stat-label">面试次数</span>
          </div>
          <div class="stat-trend up">
            <i class="el-icon-top"></i>
            <span>+2</span>
          </div>
        </div>
        <div class="stat-card stat-2">
          <div class="stat-icon">
            <i class="el-icon-s-data"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ animatedStats.avgScore }}</span>
            <span class="stat-label">平均分数</span>
          </div>
          <div class="stat-trend up">
            <i class="el-icon-top"></i>
            <span>+5</span>
          </div>
        </div>
        <div class="stat-card stat-3">
          <div class="stat-icon">
            <i class="el-icon-trophy"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ animatedStats.badgeCount }}</span>
            <span class="stat-label">获得徽章</span>
          </div>
          <div class="stat-trend up">
            <i class="el-icon-top"></i>
            <span>+1</span>
          </div>
        </div>
      </div>
      
      <!-- 能力成长曲线 -->
      <div class="growth-section" :class="{ 'animate-in': pageMounted }">
        <div class="section-header">
          <h3 class="section-title">
            <i class="el-icon-data-line"></i>
            能力成长曲线
          </h3>
          <span class="update-time">最近30天</span>
        </div>
        <div class="growth-chart" id="growthChart"></div>
      </div>

      <!-- 最近活动 -->
      <div class="activity-section" :class="{ 'animate-in': pageMounted }">
        <div class="section-header">
          <h3 class="section-title">
            <i class="el-icon-time"></i>
            最近活动
          </h3>
          <span class="more-link">查看全部</span>
        </div>
        <div class="activity-list">
          <div class="activity-item" v-if="interviewHistory.length > 0" v-for="(item, index) in interviewHistory.slice(0, 3)" :key="index">
            <div class="activity-content">
              <span class="activity-title">完成{{ item.position || '面试' }}</span>
              <span class="activity-time">{{ item.created_at || '刚刚' }}</span>
            </div>
            <div class="activity-score">
              <span class="score-num">85</span>
              <span class="score-label">分</span>
            </div>
          </div>
          <div class="activity-item" v-else>
            <div class="activity-content">
              <span class="activity-title">开始你的第一次面试</span>
              <span class="activity-time">还没有面试记录</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 功能列表 -->
      <div class="function-list" :class="{ 'animate-in': pageMounted }">
        <div class="list-header">
          <h3 class="list-title">常用功能</h3>
        </div>
        <div 
          v-for="(item, index) in functionItems" 
          :key="index"
          class="list-item" 
          @click="handleListItemClick(item.key)"
          :style="{ animationDelay: (index * 0.08 + 0.2) + 's' }"
        >
          <div class="item-icon" :style="{ background: item.color }">
            <i :class="item.icon"></i>
          </div>
          <div class="item-content">
            <span class="item-title">{{ item.title }}</span>
            <span class="item-desc" v-if="item.badge">{{ item.badge }}</span>
          </div>
          <i class="el-icon-arrow-right item-arrow"></i>
        </div>
      </div>

      <!-- 底部留白 -->
      <div class="bottom-spacer"></div>
    </div>
    
    <!-- 设置页面 -->
    <div class="main-content" v-show="currentPage === 'settings'">
      <div class="settings-header">
        <div class="back-btn" @click="currentPage = 'mine'">
          <i class="el-icon-arrow-left"></i>
        </div>
        <h2 class="settings-title">设置</h2>
        <div class="empty"></div>
      </div>
      
      <!-- 登录注册 -->
      <div class="settings-section">
        <h3 class="section-title">账号管理</h3>
        <div class="settings-card">
          <div v-if="!isLoggedIn" class="auth-section">
            <el-button class="register-btn" @click="showRegisterDialog = true">注册</el-button>
          </div>
          <div v-else class="user-info-section">
            <div class="avatar-section">
              <div class="avatar-upload">
                <img :src="userInfo.avatar" alt="用户头像" class="upload-avatar">
                <input type="file" class="avatar-input" accept="image/*" @change="handleAvatarUpload">
                <div class="avatar-overlay">
                  <i class="el-icon-camera"></i>
                  <span>更换头像</span>
                </div>
              </div>
            </div>
            <div class="account-info">
              <div class="info-item">
                <span class="info-label">用户名</span>
                <el-input v-model="userInfo.username" placeholder="请输入用户名"></el-input>
              </div>
              <div class="info-item">
                <span class="info-label">手机号</span>
                <el-input v-model="userInfo.phone" placeholder="请输入手机号"></el-input>
              </div>
              <div class="info-item">
                <span class="info-label">邮箱</span>
                <el-input v-model="userInfo.email" placeholder="请输入邮箱"></el-input>
              </div>
              <el-button type="primary" class="save-btn" @click="saveUserInfo">保存信息</el-button>
              <el-button class="logout-btn" @click="logout">退出登录</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部导航栏 - 面试页面时隐藏 -->
    <div class="bottom-nav" v-show="currentPage !== 'aiInterviewChat' && currentPage !== 'interviewReport' && currentPage !== 'improvementPlan'">
      <div class="nav-item" :class="{ active: currentPage === 'home' }" @click="currentPage = 'home'">
        <i class="el-icon-house"></i>
        <span>首页</span>
      </div>
      <div class="nav-item" :class="{ active: currentPage === 'interview' }" @click="currentPage = 'interview'">
        <i class="el-icon-video-camera"></i>
        <span>模拟面试</span>
      </div>
      <div class="nav-item" :class="{ active: currentPage === 'mine' }" @click="currentPage = 'mine'">
        <i class="el-icon-user"></i>
        <span>我的</span>
      </div>
    </div>
    
    <!-- 真题详情对话框 -->
    <el-dialog
      v-model="showExamQuestionDialog"
      :title="currentExamQuestion?.question || '真题详情'"
      width="800px"
      class="exam-question-dialog"
    >
      <div class="exam-question-detail" v-if="currentExamQuestion">
        <div class="exam-question-section">
          <h4 class="section-title">题目</h4>
          <p class="question-content">{{ currentExamQuestion.question }}</p>
          <div class="question-meta">
            <span class="category-tag">{{ currentExamQuestion.category }}</span>
            <span class="question-time">{{ currentExamQuestion.created_at }}</span>
          </div>
        </div>

        <div class="exam-answer-section">
          <h4 class="section-title">答案</h4>
          <p class="answer-content">{{ currentExamQuestion.answer }}</p>
        </div>

        <div class="exam-analysis-section">
          <h4 class="section-title">解析</h4>
          <p class="analysis-content">{{ currentExamQuestion.analysis }}</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showExamQuestionDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 随机练一题对话框 -->
    <el-dialog
      v-model="showRandomPracticeDialog"
      title="随机练一题"
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
            {{ getDifficultyText(currentRandomQuestion.difficulty) }}
          </span>
        </div>

        <p class="random-question-text">{{ currentRandomQuestion.question }}</p>

        <div class="random-options-list">
          <div
            v-for="(option, optIndex) in currentRandomQuestion.options"
            :key="optIndex"
            class="option-item"
            :class="{
              selected: randomPracticeSelectedAnswer.includes(option.charAt(0)),
              correct: randomPracticeShowAnswer && isCorrectAnswer(option),
              incorrect: randomPracticeShowAnswer && randomPracticeSelectedAnswer.includes(option.charAt(0)) && !isCorrectAnswer(option)
            }"
            @click="handleRandomOptionSelect(option)"
          >
            <span class="option-letter">{{ option.charAt(0) }}</span>
            <span class="option-text">{{ option.substring(3) }}</span>
            <i v-if="randomPracticeShowAnswer && isCorrectAnswer(option)" class="el-icon-check correct-icon"></i>
            <i v-if="randomPracticeShowAnswer && randomPracticeSelectedAnswer.includes(option.charAt(0)) && !isCorrectAnswer(option)" class="el-icon-close incorrect-icon"></i>
          </div>
        </div>

        <div class="answer-section" v-if="randomPracticeShowAnswer">
          <div class="correct-answer">
            <span class="answer-label">正确答案：</span>
            <span class="answer-value">{{ formatRandomAnswer() }}</span>
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
          <button class="action-btn close-btn" @click="showRandomPracticeDialog = false">
            关闭
          </button>
        </div>
      </template>
    </el-dialog>
    </template>
  </div>
</template>

<script>
import HomePage from './components/HomePage.vue'
import InterviewPage from './components/InterviewPage.vue'
import AIInterviewConfig from './components/AIInterviewConfig.vue'
import AIInterviewChat from './components/AIInterviewChat.vue'
import InterviewReport from './components/InterviewReport.vue'
import ImprovementPlan from './components/ImprovementPlan.vue'
import PersonalAbilityProfile from './components/PersonalAbilityProfile.vue'
import QuestionBank from './components/QuestionBank.vue'
import PrepCenter from './components/PrepCenter.vue'
import FavoritesPage from './components/FavoritesPage.vue'
import LoginPage from './views/LoginPage.vue'
import * as echarts from 'echarts'

export default {
  name: 'App',
  components: {
    HomePage,
    InterviewPage,
    AIInterviewConfig,
    AIInterviewChat,
    InterviewReport,
    ImprovementPlan,
    PersonalAbilityProfile,
    QuestionBank,
    PrepCenter,
    FavoritesPage,
    LoginPage
  },
  data() {
    return {
      currentPage: 'home',
      messages: [],
      inputMessage: '',
      isRecording: false,
      interviewInfo: {
        position: '事业单位',
        round: '结构化面试'
      },
      showReport: false,
      interviewReport: {
        overall_score: 85,
        overall_level: '优秀',
        timestamp: new Date().toLocaleString(),
        content_evaluation: {
          technical: { comment: '技术知识掌握扎实', score: 90 },
          logic: { comment: '逻辑思维清晰', score: 85 },
          communication: { comment: '沟通表达流畅', score: 80 }
        },
        expression_evaluation: {
          clarity: { comment: '表达清晰', score: 85 },
          confidence: { comment: '自信度良好', score: 80 },
          speed: { comment: '语速适中', score: 90 }
        },
        highlights: ['技术知识掌握扎实', '逻辑思维清晰', '沟通表达流畅'],
        suggestions: ['加强项目经验的描述', '提高问题分析能力', '增强技术深度']
      },
      improvementPlan: {
        weakness_analysis: [
          { weakness: '技术深度不足', severity: '中' },
          { weakness: '项目经验不够丰富', severity: '中' },
          { weakness: '沟通表达需要加强', severity: '中' }
        ],
        improvement_suggestions: [
          { suggestion: '系统学习核心技术栈', category: '技术提升', priority: '高' },
          { suggestion: '参与更多实际项目', category: '项目经验', priority: '高' },
          { suggestion: '练习演讲和表达', category: '沟通提升', priority: '中' }
        ],
        learning_resources: [
          { title: '技术文档', type: '在线课程', url: '' },
          { title: '在线课程', type: '视频', url: '' },
          { title: '实战项目', type: '项目', url: '' }
        ],
        thirty_day_plan: [
          { week: 1, focus: '技术基础强化', daily_tasks: ['学习核心技术概念', '完成基础练习题', '阅读技术文档'], expected_outcome: '掌握核心基础' },
          { week: 2, focus: '项目经验积累', daily_tasks: ['参与实际项目', '分析项目案例', '总结项目经验'], expected_outcome: '积累项目经验' },
          { week: 3, focus: '沟通表达提升', daily_tasks: ['练习演讲', '模拟面试', '学习沟通技巧'], expected_outcome: '提升表达能力' },
          { week: 4, focus: '综合能力提升', daily_tasks: ['系统复习', '模拟面试', '总结提升'], expected_outcome: '全面提升' }
        ]
      },
      recognition: null,
      searchQuery: '',
      isLoggedIn: false,
      userInfo: {
        id: null,
        username: '未登录',
        avatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20avatar&image_size=square',
        points: 0,
        phone: '',
        email: ''
      },
      showRegisterDialog: false,
      registerForm: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      aiInterviewForm: {
        job: 'Java工程师',
        jobType: 'java_backend',
        experience: '实习',
        interviewerRole: 'HR面试官',
        company: '',
        pressureLevel: 1,
        duration: 10,
        resumeText: ''
      },
      chatMessages: [],
      userInput: '',
      currentQuestionIndex: 0,
      totalQuestions: 3,
      interviewQuestions: [],
      isLoading: false,
      currentInterviewId: null,
      interviewHistory: [],
      currentInterviewDetail: null,
      examQuestions: [],
      examSearchKeyword: '',
      showExamQuestionDialog: false,
      currentExamQuestion: null,
      interviewType: 'ai',
      pageMounted: false,
      statsAnimated: false,
      userLevel: 5,
      animatedStats: {
        interviewCount: 0,
        avgScore: 0,
        badgeCount: 0
      },
      showRandomPracticeDialog: false,
      currentRandomQuestion: null,
      randomPracticeSelectedAnswer: [],
      randomPracticeShowAnswer: false,
      questions: [],
      favoritedInterviews: new Set(),
      functionItems: [
        { key: 'abilityProfile', title: '个人能力档案', icon: 'el-icon-data-analysis', color: 'linear-gradient(135deg, #7C3AED, #A78BFA)', badge: '查看详情' },
        { key: 'interviewRecord', title: '面试记录', icon: 'el-icon-document', color: 'linear-gradient(135deg, #409EFF, #66B1FF)', badge: '查看详情' },
        { key: 'favorites', title: '我的收藏', icon: 'el-icon-star-off', color: 'linear-gradient(135deg, #F7BA1E, #F7BA1E)', badge: '查看详情' },
        { key: 'notifications', title: '消息通知', icon: 'el-icon-bell', color: 'linear-gradient(135deg, #F56C6C, #F56C6C)', badge: '查看详情' },
        { key: 'feedback', title: '联系与反馈', icon: 'el-icon-chat-line-round', color: 'linear-gradient(135deg, #67C23A, #85CE61)', badge: '' },
        { key: 'settings', title: '设置', icon: 'el-icon-setting', color: 'linear-gradient(135deg, #909399, #C0C4CC)', badge: '' }
      ],
      // 打字机效果
      typewriterTexts: [
        '今天也要加油哦！💪',
        '面试准备好了吗？',
        '让我们一起进步吧！',
        '成功就在眼前！',
        '相信你自己！✨'
      ],
      typewriterText: '',
      typewriterIndex: 0,
      charIndex: 0,
      isDeleting: false,
      typewriterTimer: null,
      _growthChart: null,
      _growthChartResizeHandler: null
    }
  },
  mounted() {
    // 检查本地存储中的登录状态
    const userData = localStorage.getItem('userData');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        this.userInfo = user;
        this.isLoggedIn = true;
        this.loadInterviewHistory();
      } catch (error) {
        console.error('解析用户数据失败:', error);
        localStorage.removeItem('userData');
      }
    }
    
    // 加载事业单位真题
    this.loadExamQuestions();
    
    // 启动打字机效果
    this.startTypewriter();
  },
  beforeUnmount() {
    // 清理图表实例和事件监听器
    if (this._growthChart) {
      this._growthChart.dispose();
    }
    if (this._growthChartResizeHandler) {
      window.removeEventListener('resize', this._growthChartResizeHandler);
    }
    // 清理打字机定时器
    if (this.typewriterTimer) {
      clearTimeout(this.typewriterTimer);
    }
  },
  watch: {
    currentPage(newPage) {
      if (newPage === 'mine') {
        this.pageMounted = false;
        this.statsAnimated = false;
        setTimeout(() => {
          this.pageMounted = true;
          this.animateStats();
        }, 50);
      }
      if (newPage === 'mine' && this.isLoggedIn) {
        this.$nextTick(() => {
          this.initGrowthChart();
        });
      }
    },
    interviewHistory(newHistory) {
      if (this.currentPage === 'mine' && this.isLoggedIn) {
        this.$nextTick(() => {
          this.initGrowthChart();
          this.animateStats();
        });
      }
    }
  },
  methods: {
    // 打字机效果
    startTypewriter() {
      const type = () => {
        const fullText = this.typewriterTexts[this.typewriterIndex];
        
        if (this.isDeleting) {
          this.typewriterText = fullText.substring(0, this.charIndex - 1);
          this.charIndex--;
        } else {
          this.typewriterText = fullText.substring(0, this.charIndex + 1);
          this.charIndex++;
        }

        let typeSpeed = this.isDeleting ? 50 : 100;

        if (!this.isDeleting && this.charIndex === fullText.length) {
          typeSpeed = 2000;
          this.isDeleting = true;
        } else if (this.isDeleting && this.charIndex === 0) {
          this.isDeleting = false;
          this.typewriterIndex = (this.typewriterIndex + 1) % this.typewriterTexts.length;
          typeSpeed = 500;
        }

        this.typewriterTimer = setTimeout(type, typeSpeed);
      };
      
      type();
    },
    
    // 计算平均分
    calculateAverageScore() {
      if (!this.interviewHistory || this.interviewHistory.length === 0) {
        return 0
      }
      let totalScore = 0
      let count = 0
      this.interviewHistory.forEach(interview => {
        if (interview.overall_score) {
          totalScore += interview.overall_score
          count++
        }
      })
      return count > 0 ? Math.round(totalScore / count) : 0
    },
    
    // 数字递增动画
    animateStats() {
      if (this.statsAnimated) return;
      this.statsAnimated = true;
      
      const targetValues = {
        interviewCount: this.interviewHistory.length || 0,
        avgScore: this.calculateAverageScore(),
        badgeCount: 3
      };
      
      const duration = 1500;
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        
        this.animatedStats.interviewCount = Math.floor(targetValues.interviewCount * easeProgress);
        this.animatedStats.avgScore = Math.floor(targetValues.avgScore * easeProgress);
        this.animatedStats.badgeCount = Math.floor(targetValues.badgeCount * easeProgress);
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      
      requestAnimationFrame(animate);
    },
    // 初始化能力成长曲线图表
    initGrowthChart() {
      const chartDom = document.getElementById('growthChart');
      if (!chartDom) return;
      
      // 检查是否已经初始化过，如果已初始化则先销毁
      if (this._growthChart) {
        try {
          if (!this._growthChart.isDisposed()) {
            this._growthChart.dispose();
          }
        } catch (e) {
          console.warn('图表销毁失败:', e);
        }
        this._growthChart = null;
      }
      
      const myChart = echarts.init(chartDom);
      
      // 准备数据 - 如果没有真实数据，使用示例数据
      let dates = [];
      let scores = [];
      
      if (this.isLoggedIn && this.interviewHistory.length > 0) {
        const completedInterviews = this.interviewHistory.filter(interview => interview.status === 'completed');
        if (completedInterviews.length > 0) {
          dates = completedInterviews.map(interview => {
            const date = new Date(interview.created_at);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          });
          
          scores = completedInterviews.map(interview => {
            return Math.floor(Math.random() * 20) + 70;
          });
        }
      }
      
      // 如果没有真实数据，使用示例数据
      if (dates.length === 0) {
        dates = ['1/5', '1/10', '1/15', '1/20', '1/25', '1/30', '2/4'];
        scores = [72, 75, 78, 76, 80, 82, 85];
      }
      
      const option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          borderColor: '#e4e7ed',
          borderWidth: 1,
          textStyle: {
            color: '#303133',
            fontSize: 13
          },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#409EFF'
            }
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '8%',
          top: '12%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLine: {
            lineStyle: {
              color: '#dcdfe6'
            }
          },
          axisLabel: {
            color: '#606266',
            fontSize: 12
          },
          axisTick: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          min: 60,
          max: 100,
          interval: 10,
          splitLine: {
            lineStyle: {
              color: '#f0f2f5',
              type: 'dashed'
            }
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            color: '#909399',
            fontSize: 12
          }
        },
        series: [
          {
            name: '综合评分',
            type: 'line',
            smooth: 0.6,
            symbol: 'circle',
            symbolSize: 10,
            data: scores,
            lineStyle: {
              color: '#409EFF',
              width: 3,
              shadowBlur: 8,
              shadowColor: 'rgba(64, 158, 255, 0.3)'
            },
            itemStyle: {
              color: '#409EFF',
              borderColor: '#fff',
              borderWidth: 2,
              shadowBlur: 6,
              shadowColor: 'rgba(64, 158, 255, 0.3)'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgba(64, 158, 255, 0.25)'
                },
                {
                  offset: 0.5,
                  color: 'rgba(64, 158, 255, 0.12)'
                },
                {
                  offset: 1,
                  color: 'rgba(64, 158, 255, 0.02)'
                }
              ])
            },
            emphasis: {
              focus: 'series',
              itemStyle: {
                color: '#66b1ff',
                borderColor: '#fff',
                borderWidth: 3,
                shadowBlur: 12,
                shadowColor: 'rgba(64, 158, 255, 0.6)'
              },
              lineStyle: {
                width: 4
              }
            }
          }
        ]
      };
      
      myChart.setOption(option);
      
      // 清理旧的事件监听器
      if (this._growthChartResizeHandler) {
        window.removeEventListener('resize', this._growthChartResizeHandler);
      }
      
      // 响应式调整
      const resizeHandler = () => {
        if (myChart && !myChart.isDisposed()) {
          myChart.resize();
        }
      };
      window.addEventListener('resize', resizeHandler);
      
      // 保存实例引用以便销毁
      this._growthChart = myChart;
      this._growthChartResizeHandler = resizeHandler;
    },
    // 处理功能入口点击
    handleFunctionClick(functionName) {
      if (functionName === '精选题库') {
        this.currentPage = 'questionBank'
      } else if (functionName === '面试干货') {
        this.currentPage = 'prepCenter'
      } else {
        this.$message.info(`点击了：${functionName}`)
      }
    },
    
    // 处理随机练一题按钮点击
    handleRandomQuestion() {
      // 如果对话框已经打开且已有题目，直接随机选一道新题
      if (this.showRandomPracticeDialog && this.questions.length > 0) {
        const randomIndex = Math.floor(Math.random() * this.questions.length);
        this.currentRandomQuestion = this.questions[randomIndex];
        this.randomPracticeSelectedAnswer = [];
        this.randomPracticeShowAnswer = false;
      } else {
        // 否则加载题目
        this.loadQuestionsForPractice();
      }
    },

    async loadQuestionsForPractice() {
      try {
        const response = await fetch('/api/selected-questions');
        if (response.ok) {
          const data = await response.json();
          this.questions = data.questions || [];
          if (this.questions.length > 0) {
            const randomIndex = Math.floor(Math.random() * this.questions.length);
            this.currentRandomQuestion = this.questions[randomIndex];
            this.randomPracticeSelectedAnswer = [];
            this.randomPracticeShowAnswer = false;
            this.showRandomPracticeDialog = true;
          } else {
            this.$message.warning('题库中暂无题目，请先生成题目');
          }
        }
      } catch (error) {
        console.error('加载题目失败:', error);
        this.$message.error('加载题目失败');
      }
    },

    getDifficultyText(difficulty) {
      const difficultyText = {
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
      };
      return difficultyText[difficulty] || '中等';
    },

    handleRandomOptionSelect(option) {
      if (this.randomPracticeShowAnswer) return;
      const optionLetter = option.charAt(0);
      
      // 判断是否是多选题
      const isMultiple = this.currentRandomQuestion?.type === 'multiple' || 
                         (this.currentRandomQuestion?.correct_answer && 
                          typeof this.currentRandomQuestion.correct_answer === 'string' && 
                          this.currentRandomQuestion.correct_answer.includes(','));
      
      if (isMultiple) {
        // 多选题：切换选择
        const index = this.randomPracticeSelectedAnswer.indexOf(optionLetter);
        if (index > -1) {
          this.randomPracticeSelectedAnswer.splice(index, 1);
        } else {
          this.randomPracticeSelectedAnswer.push(optionLetter);
        }
      } else {
        // 单选题：单选
        this.randomPracticeSelectedAnswer = [optionLetter];
      }
    },

    isCorrectAnswer(option) {
      if (!this.currentRandomQuestion) return false;
      const correct = this.currentRandomQuestion.correct_answer;
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

    handleRandomSubmit() {
      if (this.randomPracticeSelectedAnswer.length === 0) {
        this.$message.warning('请选择答案');
        return;
      }
      this.randomPracticeShowAnswer = true;
    },

    handleRandomNext() {
      if (this.questions.length > 0) {
        const randomIndex = Math.floor(Math.random() * this.questions.length);
        this.currentRandomQuestion = this.questions[randomIndex];
        this.randomPracticeSelectedAnswer = [];
        this.randomPracticeShowAnswer = false;
      } else {
        this.$message.warning('题库中暂无题目');
      }
    },

    formatRandomAnswer() {
      if (!this.currentRandomQuestion) return '';
      const correct = this.currentRandomQuestion.correct_answer;
      if (typeof correct === 'string' && correct.includes(',')) {
        return correct.split(',').join('、');
      }
      return correct;
    },
    
    // 处理搜索按钮点击
    handleSearch() {
      this.$message.info('搜索功能')
    },

    // 处理语音面试按钮点击
    handleVoiceInterview() {
      // 设置为语音面试模式
      this.interviewType = 'voice'
      // 跳转到配置页面
      this.currentPage = 'aiInterview'
    },

    // 处理AI交流对话面试按钮点击
    handleAIInterview() {
      // 设置为AI交流对话面试模式
      this.interviewType = 'ai'
      // 跳转到配置页面
      this.currentPage = 'aiInterview'
    },
    
    // 处理数字人面试按钮点击
    handleAvatarInterview() {
      // 设置为数字人面试模式
      this.interviewType = 'avatar'
      // 跳转到配置页面
      this.currentPage = 'aiInterview'
    },
    
    // 处理历史记录点击
    handleHistoryClick() {
      this.loadInterviewHistory()
      this.loadFavoritedInterviews()
      this.currentPage = 'interviewRecord'
    },
    
    // 开始AI面试
    async startAIInterview(formData) {
      if (!this.isLoggedIn) {
        this.$message.error('请先登录')
        return
      }
      
      if (!this.userInfo.id) {
        this.$message.error('用户信息不完整，请重新登录')
        return
      }
      
      this.isLoading = true
      
      try {
        // 开始面试，保存到数据库
        const startResponse = await fetch(`/api/interview/start?user_id=${this.userInfo.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            position: formData.job,
            round: this.interviewType === 'voice' ? '语音面试' : 'AI交流对话面试',
            job_type: formData.jobType,
            experience: formData.experience,
            interviewer_role: formData.interviewerRole,
            pressure_level: formData.pressureLevel,
            duration: formData.duration,
            resume_text: formData.resumeText,
            target_company: formData.company
          })
        })
        
        if (!startResponse.ok) {
          throw new Error('开始面试失败')
        }
        
        const startData = await startResponse.json()
        this.currentInterviewId = startData.interview_id
        
        // 清空消息和问题列表
        this.chatMessages = []
        this.userInput = ''
        this.interviewQuestions = []
        this.currentQuestionIndex = 0
        
        // 根据面试时长生成不同的开场白
        const duration = formData.duration
        let openingText = ''
        
        if (duration === 5) {
          // 5分钟面试：精简版
          openingText = `你好！我是AI面试官，今天将对你进行${formData.job}岗位的面试，时长5分钟。本次面试主要考察你的基本适配度。请先做一个自我介绍（1.5分钟以内），包括个人基本信息、核心技能、求职意向。然后我会问你1-2个核心问题。最后你可以提问1个最关心的问题。准备好了吗？我们开始吧！`
        } else if (duration === 10) {
          // 10分钟面试：常规版
          openingText = `你好！我是AI面试官，今天将对你进行${formData.job}岗位的AI交流对话面试，时长10分钟。本次面试主要考察你的技能匹配度和表达能力。请先做一个详细的自我介绍（2分钟以内），包括个人基本信息、技能掌握情况和相关学习/项目经历（重点提炼1个核心亮点）。然后我会问你3-4个针对性问题。最后你可以提问1-2个问题。准备好了吗？我们开始吧！`
        } else if (duration === 20) {
          // 20分钟面试：深度版
          openingText = `你好！我是AI面试官，今天将对你进行${formData.job}岗位的面试，时长20分钟。本次面试将从技能掌握、项目经验、问题处理、职业素养等方面进行全面考察。请先做一个完整的自我介绍（3分钟以内），包括个人信息、技能体系、学习/项目经历（简要展开1个相关案例，说明自身职责与成果）、职业规划。然后我会问你5-6个深入的问题，针对重点内容可能会追问。最后你可以提问2-3个问题。准备好了吗？我们开始吧！`
        } else if (duration === 30) {
          // 30分钟面试：完整版
          openingText = `你好！我是AI面试官，今天将对你进行${formData.job}岗位的全面面试，时长30分钟。本次面试将全方位考察你的能力、态度与潜力。请先做一个详细的自我介绍（4分钟以内），包括个人基本信息、技能掌握情况（可补充技能熟练度）、学习/项目经历（展开1-2个核心案例，说明背景、自身职责、遇到的问题及解决成果）、职业规划。然后我会问你7-8个综合问题，针对关键内容会深入追问。最后你可以提问3-4个问题，我会详细解答。准备好了吗？我们开始吧！`
        } else {
          // 默认10分钟
          openingText = `你好！我是AI面试官，今天将对你进行${formData.job}岗位的AI交流对话面试，时长10分钟。本次面试主要考察你的技能匹配度和表达能力。请先做一个详细的自我介绍，包括个人基本信息、技能掌握情况和相关学习/项目经历（重点提炼1个核心亮点）。`
        }
        
        // 添加AI面试官的开场白
        this.chatMessages.push({
          type: 'ai',
          content: openingText,
          time: new Date().toLocaleTimeString()
        })
        
        // 将开场白添加到问题列表
        this.interviewQuestions.push(openingText)
        
        // 跳转到面试对话页面
        this.currentPage = 'aiInterviewChat'
        
        // 语音面试模式或数字人模式下，自动播放AI面试官的问题
        this.$nextTick(() => {
          if (this.interviewType === 'voice') {
            this.speakText(openingText)
          } else if (this.interviewType === 'avatar' && this.$refs.aiInterviewChatRef) {
            // 数字人模式下，触发数字人朗读
            this.$refs.aiInterviewChatRef.triggerAiSpeak(openingText)
          } else if (this.interviewType === 'ai' && this.$refs.aiInterviewChatRef) {
            // AI交流对话面试模式下，也触发数字人朗读（如果存在）
            this.$refs.aiInterviewChatRef.triggerAiSpeak(openingText)
          }
        })
      } catch (error) {
        console.error('开始面试失败:', error)
        this.$message.error('生成面试问题失败，请稍后重试')
      } finally {
        this.isLoading = false
      }
    },
    
    // 添加消息
    addMessage(message) {
      this.chatMessages.push(message)
    },
    
    // 处理评估完成
    handleEvaluationComplete(report) {
      this.interviewReport = report
      this.currentPage = 'interviewReport'
    },

    // 处理终止面试
    handleEndInterview() {
      // 重置面试状态
      this.chatMessages = []
      this.currentQuestionIndex = 0
      this.currentInterviewId = null
      // 回到面试选择页面
      this.currentPage = 'aiInterview'
    },
    
    // 查看提升计划
    async viewImprovementPlan() {
      if (!this.isLoggedIn) {
        this.$message.error('请先登录')
        return
      }
      
      if (!this.currentInterviewId) {
        this.$message.error('面试信息丢失，请重新开始面试')
        return
      }
      
      this.isLoading = true
      
      try {
        // 调用后端提升计划API
        const response = await fetch('/api/interview/improvement-plan', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            interview_id: this.currentInterviewId,
            job_type: this.aiInterviewForm.jobType,
            evaluation_report: this.interviewReport
          })
        })
        
        if (!response.ok) {
          throw new Error(`API调用失败: ${response.status}`)
        }

        const improvementPlan = await response.json()
        this.improvementPlan = improvementPlan
        
        // 调用学习资源推荐API
        const resourcesResponse = await fetch('/api/learning/recommend-resources', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            job_type: this.aiInterviewForm.jobType,
            weak_areas: improvementPlan.weakness_analysis?.map(item => item.weakness) || [],
            user_id: this.userInfo.id
          })
        })
        
        if (resourcesResponse.ok) {
          const resourcesData = await resourcesResponse.json()
          if (resourcesData.resources && resourcesData.resources.length > 0) {
            // 如果学习资源是字符串格式，则转换为对象格式
            const formattedResources = resourcesData.resources.map(resource => {
              if (typeof resource === 'string') {
                return { title: resource, type: '在线课程', url: '' }
              }
              return resource
            })
            // 只在资源为空或数量不足时才更新
            if (!this.improvementPlan.learning_resources || this.improvementPlan.learning_resources.length === 0) {
              this.improvementPlan.learning_resources = formattedResources
            }
            this.improvementPlan.study_advice = resourcesData.study_advice
          }
        }
        
        // 跳转到提升计划页面
        this.currentPage = 'improvementPlan'
      } catch (error) {
        console.error('生成提升计划失败:', error)
        this.$message.error('生成提升计划失败，请稍后重试')
      } finally {
        this.isLoading = false
      }
    },
    
    // 注册
    async register() {
      if (!this.registerForm.username || !this.registerForm.password) {
        this.$message.error('请输入用户名和密码')
        return
      }
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.$message.error('两次密码输入不一致')
        return
      }
      
      this.isLoading = true
      try {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.registerForm.username,
            password: this.registerForm.password,
            email: `${this.registerForm.username}@example.com` // 模拟邮箱
          })
        })
        
        if (!response.ok) {
          throw new Error('注册失败')
        }
        
        const data = await response.json()
        this.$message.success('注册成功，请登录')
        this.showRegisterDialog = false
      } catch (error) {
        console.error('注册失败:', error)
        this.$message.error('用户名或邮箱已存在')
      } finally {
        this.isLoading = false
      }
    },

    // 登录成功处理
    handleLoginSuccess(userInfo) {
      this.userInfo = userInfo
      this.isLoggedIn = true
      this.loadInterviewHistory()
    },

    // 跳转到注册
    handleGoRegister() {
      console.log('App.vue: handleGoRegister 被调用')
      console.log('showRegisterDialog 当前值:', this.showRegisterDialog)
      this.showRegisterDialog = true
      console.log('showRegisterDialog 设置后:', this.showRegisterDialog)
    },

    // 退出登录
    logout() {
      this.isLoggedIn = false
      this.userInfo = {
        id: null,
        username: '未登录',
        avatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20avatar&image_size=square',
        points: 0,
        phone: '',
        email: ''
      }
      localStorage.removeItem('userData')
      this.$message.success('退出登录成功')
      this.currentPage = 'home'
    },

    // 加载面试历史
    async loadInterviewHistory() {
      if (!this.isLoggedIn || !this.userInfo.id) return

      try {
        const response = await fetch(`/api/interview/history?user_id=${this.userInfo.id}`)
        if (response.ok) {
          const data = await response.json()
          this.interviewHistory = data.interviews
        }
      } catch (error) {
        console.error('加载面试历史失败:', error)
      }
    },

    async loadFavoritedInterviews() {
      if (!this.isLoggedIn || !this.userInfo.id) return

      try {
        const response = await fetch(`/api/favorites?user_id=${this.userInfo.id}&favorite_type=interview`)
        if (response.ok) {
          const data = await response.json()
          if (data.success && data.data) {
            this.favoritedInterviews = new Set(data.data.map(f => f.item_id))
          }
        }
      } catch (error) {
        console.error('加载面试收藏状态失败:', error)
      }
    },

    isInterviewFavorited(interviewId) {
      return this.favoritedInterviews.has(interviewId)
    },

    async handleToggleInterviewFavorite(interview) {
      if (!this.isLoggedIn) {
        this.$message.warning('请先登录')
        return
      }

      try {
        const response = await fetch('/api/favorites/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: this.userInfo.id,
            favorite_type: 'interview',
            item_id: interview.id,
            title: interview.position || '面试',
            content: `面试时间：${interview.created_at}`
          })
        })

        const data = await response.json()
        if (data.success) {
          if (data.is_favorited) {
            this.favoritedInterviews.add(interview.id)
            this.$message.success('收藏成功')
          } else {
            this.favoritedInterviews.delete(interview.id)
            this.$message.success('已取消收藏')
          }
        }
      } catch (error) {
        console.error('收藏操作失败:', error)
        this.$message.error('操作失败')
      }
    },

    // 更换头像
    handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (file) {
        // 模拟上传
        const reader = new FileReader()
        reader.onload = (e) => {
          this.userInfo.avatar = e.target.result
          this.$message.success('头像更新成功')
        }
        reader.readAsDataURL(file)
      }
    },

    // 保存用户信息
    saveUserInfo() {
      this.$message.success('用户信息保存成功')
    },
    
    // 处理个人能力档案点击
    handleProfileClick() {
      if (!this.isLoggedIn) {
        this.$message.error('请先登录')
        return
      }
      this.currentPage = 'personalProfile'
    },
    
    // 处理功能列表点击
    handleListItemClick(itemKey) {
      if (!this.isLoggedIn) {
        this.$message.error('请先登录')
        return
      }

      if (itemKey === 'interviewRecord') {
        this.loadInterviewHistory()
        this.currentPage = 'interviewRecord'
      } else if (itemKey === 'abilityProfile') {
        this.currentPage = 'personalProfile'
      } else if (itemKey === 'favorites') {
        this.currentPage = 'favorites'
      } else {
        this.$message.info(`点击了：${itemKey}`)
      }
    },
    
    // 获取简历评价维度的中文名称
    getDimensionName(dimensionKey) {
      const dimensionNames = {
        'completeness': '完整性',
        'professionalism': '专业性',
        'logic': '逻辑性',
        'highlights': '亮点突出',
        'details': '细节处理'
      }
      return dimensionNames[dimensionKey] || dimensionKey
    },

    // 查看面试详情
    async viewInterviewDetail(interviewId) {
      this.isLoading = true
      try {
        const response = await fetch(`/api/interview/detail?interview_id=${interviewId}`)
        if (response.ok) {
          const data = await response.json()
          // 处理后端返回的数据结构
          this.currentInterviewDetail = {
            ...data.interview,
            messages: data.messages,
            report: data.report,
            plan: data.plan,
            resume_evaluation: data.resume_evaluation
          }
          this.currentPage = 'interviewDetail'
        } else {
          this.$message.error('加载面试详情失败')
        }
      } catch (error) {
        console.error('加载面试详情失败:', error)
        this.$message.error('加载面试详情失败')
      } finally {
        this.isLoading = false
      }
    },

    // 删除面试记录
    async deleteInterview(interviewId) {
      this.$confirm('确定要删除这条面试记录吗？删除后将无法恢复。', '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          // 调用后端API删除面试记录
          const response = await fetch(`/api/interview/delete?interview_id=${interviewId}&user_id=${this.userInfo.id}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json'
            }
          })
          
          if (!response.ok) {
            throw new Error('删除失败')
          }
          
          // 从前端列表中移除
          this.interviewHistory = this.interviewHistory.filter(item => item.id !== interviewId)
          this.$message.success('删除成功')
        } catch (error) {
          console.error('删除面试记录失败:', error)
          this.$message.error('删除失败')
        }
      }).catch(() => {
        // 取消删除
      })
    },
    
    // 加载事业单位真题
    async loadExamQuestions() {
      try {
        const response = await fetch('/api/exam/questions')
        if (response.ok) {
          const data = await response.json()
          this.examQuestions = data.questions
        }
      } catch (error) {
        console.error('加载真题失败:', error)
      }
    },
    
    // 搜索事业单位真题
    async searchExamQuestions() {
      if (!this.examSearchKeyword.trim()) {
        this.loadExamQuestions()
        return
      }
      
      try {
        const response = await fetch(`/api/exam/search?keyword=${encodeURIComponent(this.examSearchKeyword)}`)
        if (response.ok) {
          const data = await response.json()
          this.examQuestions = data.questions
        }
      } catch (error) {
        console.error('搜索真题失败:', error)
      }
    },
    
    // 查看真题详情
    viewExamQuestionDetail(question) {
      this.currentExamQuestion = question
      this.showExamQuestionDialog = true
    }
  }
}
</script>

<style>
/* 全局样式 */
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* 欢迎区域样式 */
.welcome-section {
  position: relative;
  padding: 24px 20px 20px;
  z-index: 2;
}

.welcome-content {
  position: relative;
  z-index: 2;
}

.welcome-greeting {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
  animation: slideInDown 0.6s ease-out;
}

.greeting-text {
  font-size: 24px;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.username {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(102, 126, 234, 0.6);
  animation: pulse 2s ease-in-out infinite;
}

.typewriter-container {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  height: 28px;
  animation: slideInUp 0.6s ease-out 0.2s both;
}

.typewriter-text {
  font-size: 18px;
  font-weight: 500;
  color: #a0a0c0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.cursor {
  display: inline-block;
  width: 3px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-left: 4px;
  animation: blink 1s step-end infinite;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.8);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.welcome-stats {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px 16px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideInUp 0.6s ease-out 0.4s both;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  cursor: default;
}

.stat-item:hover {
  transform: translateY(-4px) scale(1.05);
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.stat-label {
  font-size: 13px;
  color: #a0a0c0;
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: linear-gradient(180deg, transparent, rgba(102, 126, 234, 0.4), transparent);
}

.welcome-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  pointer-events: none;
  z-index: 1;
}

.deco-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(102, 126, 234, 0.2);
  animation: ringPulse 3s ease-in-out infinite;
}

.ring-1 {
  width: 120px;
  height: 120px;
  top: 20px;
  right: 20px;
  animation-delay: 0s;
}

.ring-2 {
  width: 160px;
  height: 160px;
  top: 0;
  right: 0;
  animation-delay: 0.5s;
}

.ring-3 {
  width: 200px;
  height: 200px;
  top: -20px;
  right: -20px;
  animation-delay: 1s;
}

@keyframes ringPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.6;
  }
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.5));
  }
  50% {
    filter: drop-shadow(0 0 40px rgba(102, 126, 234, 0.8));
  }
}

/* 页面过渡动画 */
.main-content {
  transition: all 0.3s ease-in-out;
  position: relative;
  z-index: 1;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 12, 41, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: all 0.3s ease-in-out;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  font-size: 32px;
  color: #667eea;
  animation: spin 1s linear infinite;
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.8));
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 16px;
  font-size: 16px;
  color: #a0a0c0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  padding-bottom: 80px;
}

/* 底部导航栏 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: rgba(15, 12, 41, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.4), 0 0 30px rgba(102, 126, 234, 0.1);
  padding: 10px 0;
  z-index: 100;
  border-top: 1px solid rgba(102, 126, 234, 0.3);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  cursor: pointer;
  color: #a0a0c0;
  transition: all 0.3s ease;
  position: relative;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 0 0 3px 3px;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.6);
}

.nav-item.active::before {
  width: 40px;
}

.nav-item.active {
  color: #667eea;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.8);
}

.nav-item i {
  font-size: 20px;
  filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.3));
  transition: filter 0.3s ease;
}

.nav-item.active i {
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.8));
}

.nav-item span {
  font-size: 12px;
}

/* 通用组件样式 */
.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #ffffff;
  margin: 0 0 20px 0;
}

/* 报告页面样式 */
.record-header,
.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.back-btn {
  cursor: pointer;
  font-size: 20px;
  color: #a0a0c0;
}

.record-title,
.settings-title {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
}

.empty {
  width: 60px;
}

.record-content,
.settings-content {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.detail-section,
.settings-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 16px 0;
  text-shadow: 0 0 8px rgba(102, 126, 234, 0.3);
}

/* 个人中心样式 */
.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  margin-bottom: 20px;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.avatar {
  position: relative;
}

.avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.pass-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.8);
}

.user-details {
  flex: 1;
}

.username {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  margin: 0 0 8px 0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.user-points {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a0a0c0;
}

.points-icon {
  font-size: 16px;
  filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5));
}



/* 能力成长曲线 */
.growth-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  margin-bottom: 20px;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.growth-chart {
  width: 100%;
  height: 300px;
}

.profile-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  margin-top: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.profile-entry:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5), 0 0 30px rgba(102, 126, 234, 0.2);
}

.profile-entry i:first-child {
  font-size: 20px;
  color: white;
}

.profile-entry span {
  font-size: 16px;
  font-weight: 500;
  color: white;
}

.profile-entry i:last-child {
  font-size: 16px;
  color: white;
}

/* 功能列表 */
.function-list {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.list-item:last-child {
  border-bottom: none;
}

.list-item:hover {
  background-color: #f5f7fa;
}

.list-item span {
  font-size: 14px;
  color: #ffffff;
}

.list-item i {
  font-size: 16px;
  color: #a0a0c0;
}

/* 面试记录页面样式 */
.record-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.record-item {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.record-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(118, 75, 162, 0.12) 0%, transparent 50%),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 15px,
      rgba(255, 255, 255, 0.03) 15px,
      rgba(255, 255, 255, 0.03) 16px
    );
  pointer-events: none;
  z-index: 0;
}

.record-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.6);
}

.record-item:hover::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shine 2s infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes shine {
  0% { left: -100%; }
  100% { left: 100%; }
}

.record-info {
  flex: 1;
  cursor: pointer;
  position: relative;
  z-index: 1;
}

.record-position {
  font-size: 18px;
  font-weight: 700;
  color: #e0e2ea;
  margin: 0 0 12px 0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.record-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #c0c4cc;
  font-weight: 500;
}

.record-status {
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.record-status.completed {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2) 0%, rgba(103, 194, 58, 0.1) 100%);
  color: #85ce61;
  border: 1px solid rgba(103, 194, 58, 0.3);
  box-shadow: 0 0 10px rgba(103, 194, 58, 0.2);
}

.record-status.in_progress {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(64, 158, 255, 0.1) 100%);
  color: #66b1ff;
  border: 1px solid rgba(64, 158, 255, 0.3);
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.2);
}

.record-details {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #c0c4cc;
  font-weight: 500;
}

.record-detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.record-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.favorite-icon {
  width: 28px;
  height: 28px;
  color: #c0c4cc;
  cursor: pointer;
  transition: all 0.3s ease;
  filter: drop-shadow(0 0 6px rgba(102, 126, 234, 0.2));
}

.favorite-icon:hover {
  color: #f093fb;
  transform: scale(1.2);
  filter: drop-shadow(0 0 12px rgba(240, 147, 251, 0.5));
}

.favorite-icon.favorited {
  color: #f093fb;
  fill: #f093fb;
  filter: drop-shadow(0 0 16px rgba(240, 147, 251, 0.6));
}

.record-arrow {
  font-size: 18px;
  color: #c0c4cc;
  filter: drop-shadow(0 0 6px rgba(102, 126, 234, 0.3));
  transition: all 0.3s ease;
}

.record-arrow:hover {
  color: #667eea;
  transform: translateX(4px);
  filter: drop-shadow(0 0 12px rgba(102, 126, 234, 0.6));
}

/* 面试详情页面样式 */
.interview-detail-content {
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

.detail-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 20px 0;
  text-shadow: 0 0 16px rgba(167, 139, 250, 0.5);
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
  padding: 24px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 14px;
  color: #a5b4fc;
  font-weight: 500;
}

.info-value {
  font-size: 15px;
  color: #ffffff;
  font-weight: 600;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.status-badge {
  padding: 6px 14px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 700;
  width: fit-content;
  letter-spacing: 0.5px;
}

.status-badge.completed {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.25) 0%, rgba(74, 222, 128, 0.25) 100%);
  color: #86efac;
  border: 1px solid rgba(34, 197, 94, 0.4);
  box-shadow: 0 0 16px rgba(34, 197, 94, 0.2);
}

.status-badge.in_progress {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(96, 165, 250, 0.25) 100%);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.4);
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.2);
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
  padding: 24px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.message-item {
  display: flex;
  gap: 12px;
}

.message-item.ai {
  flex-direction: flex-start;
}

.message-item.user {
  flex-direction: flex-end;
  justify-content: flex-end;
}

.message-avatar {
  flex-shrink: 0;
}

.message-avatar img {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(167, 139, 250, 0.4);
  box-shadow: 0 0 12px rgba(167, 139, 250, 0.3);
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  backdrop-filter: blur(10px);
}

.message-item.ai .message-text {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(167, 139, 250, 0.15) 100%);
  border: 1px solid rgba(167, 139, 250, 0.4);
  color: #ffffff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), 0 0 20px rgba(167, 139, 250, 0.15);
}

.message-item.user .message-text {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(96, 165, 250, 0.2) 100%);
  border: 1px solid rgba(96, 165, 250, 0.5);
  color: #ffffff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), 0 0 20px rgba(59, 130, 246, 0.15);
}

.message-time {
  font-size: 12px;
  color: #a5b4fc;
  margin-top: 6px;
  text-align: right;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.report-summary {
  padding: 24px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.2);
  margin-bottom: 20px;
}

.overall-score {
  display: flex;
  align-items: center;
  gap: 28px;
  margin-bottom: 24px;
}

.score-circle {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-circle.resume-score {
  width: 100px;
  height: 100px;
}

.score-circle .score-value {
  font-size: 36px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
  z-index: 1;
  text-shadow: 0 0 20px rgba(167, 139, 250, 0.6);
}

.score-circle .score-unit {
  font-size: 14px;
  color: #c4b5fd;
  margin-top: 4px;
  z-index: 1;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.score-circle::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%);
  box-shadow: 
    0 0 24px rgba(167, 139, 250, 0.4),
    0 0 48px rgba(167, 139, 250, 0.2),
    inset 0 0 16px rgba(255, 255, 255, 0.12);
  z-index: 0;
}

.score-circle::after {
  content: '';
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(167, 139, 250, 0.3) 0%, transparent 70%);
  animation: scoreGlow 3s ease-in-out infinite;
  z-index: -1;
}

@keyframes scoreGlow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
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
  text-shadow: 0 0 16px rgba(167, 139, 250, 0.5);
}

.score-date {
  font-size: 14px;
  color: #a5b4fc;
}

.evaluation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.evaluation-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.2);
  padding: 16px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.evaluation-item:hover {
  transform: translateY(-2px);
  border-color: rgba(167, 139, 250, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.evaluation-label {
  flex: 1;
  font-size: 14px;
  color: #e0e7ff;
  line-height: 1.5;
}

.evaluation-score {
  font-size: 18px;
  font-weight: 700;
  color: #c4b5fd;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.6);
  min-width: 60px;
  text-align: right;
}

.highlights-suggestions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 24px;
}

.list-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 16px 0;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.5);
}

.highlights-list,
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.highlight-item,
.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.15);
  transition: all 0.3s ease;
  color: #ffffff;
  font-weight: 500;
}

.highlight-item span,
.suggestion-item span {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.highlight-item:hover,
.suggestion-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(167, 139, 250, 0.35);
}

.highlight-item i {
  color: #4ade80;
  margin-top: 2px;
  flex-shrink: 0;
  font-size: 18px;
  text-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.suggestion-item i {
  color: #fbbf24;
  margin-top: 2px;
  flex-shrink: 0;
  font-size: 18px;
  text-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
}

.improvement-plan {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.weaknesses-list,
.resources-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weakness-item,
.resource-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.15);
  transition: all 0.3s ease;
  color: #ffffff;
  font-weight: 500;
}

.weakness-item span,
.resource-item span {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.weakness-item:hover,
.resource-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(167, 139, 250, 0.35);
}

.weakness-item i {
  color: #f87171;
  margin-top: 2px;
  flex-shrink: 0;
  font-size: 18px;
  text-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.resource-item i {
  color: #60a5fa;
  margin-top: 2px;
  flex-shrink: 0;
  font-size: 18px;
  text-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
}

.learning-plan {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.week-plan {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  padding: 18px;
  border: 1px solid rgba(167, 139, 250, 0.2);
  transition: all 0.3s ease;
}

.week-plan:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(167, 139, 250, 0.4);
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
}

.task-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #ffffff;
  font-weight: 500;
}

.task-item span {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.task-item i {
  color: #c4b5fd;
  margin-top: 2px;
  flex-shrink: 0;
  font-size: 16px;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

/* 简历评价样式 */
.resume-evaluation {
  padding: 24px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.dimensions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.dimension-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.2);
  padding: 18px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.dimension-item:hover {
  transform: translateY(-2px);
  border-color: rgba(167, 139, 250, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.dimension-label {
  font-size: 14px;
  font-weight: 600;
  color: #e0e7ff;
  margin-bottom: 10px;
}

.dimension-score-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
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
  box-shadow: 0 0 12px rgba(167, 139, 250, 0.6);
}

.score-text {
  font-size: 16px;
  font-weight: 700;
  color: #c4b5fd;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.6);
  min-width: 45px;
  text-align: right;
}

.dimension-comment {
  font-size: 13px;
  color: #a5b4fc;
  line-height: 1.5;
}

.strengths-improvements {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 24px;
}

.strengths-section,
.improvements-section {
  display: flex;
  flex-direction: column;
}

.strength-item,
.improvement-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.15);
  transition: all 0.3s ease;
  margin-bottom: 10px;
  color: #ffffff;
  font-weight: 500;
}

.strength-item span,
.improvement-item span {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

.strength-item:hover,
.improvement-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(167, 139, 250, 0.35);
}

.strength-item i {
  color: #4ade80;
  margin-top: 2px;
  flex-shrink: 0;
  font-size: 18px;
  text-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.improvement-item i {
  color: #fbbf24;
  margin-top: 2px;
  flex-shrink: 0;
  font-size: 18px;
  text-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
}

.template-suggestion {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(167, 139, 250, 0.2);
}

.suggestion-content {
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 16px;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(167, 139, 250, 0.4);
}

/* 设置页面样式 */
.settings-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.auth-section {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 40px 0;
}

.login-btn,
.register-btn {
  min-width: 120px;
}

.user-info-section {
  display: flex;
  gap: 40px;
}

.avatar-section {
  flex-shrink: 0;
  text-align: center;
}

.avatar-upload {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
  cursor: pointer;
}

.upload-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(102, 126, 234, 0.5);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.avatar-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 5;
}

.avatar-upload:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay i {
  font-size: 28px;
  margin-bottom: 6px;
}

.avatar-overlay span {
  font-size: 12px;
  font-weight: 500;
}

/* 个人中心优化样式 */
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

/* 用户信息卡片 */
.user-info-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
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
  background: rgba(255, 255, 255, 0.02);
}

.deco-1 {
  width: 100px;
  height: 100px;
  top: -30px;
  right: -20px;
  animation: float 6s ease-in-out infinite;
}

.deco-2 {
  width: 60px;
  height: 60px;
  top: 40px;
  right: 40px;
  animation: float 5s ease-in-out infinite 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.user-info-content {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.avatar-wrapper {
  position: relative;
}

.avatar-container {
  position: relative;
}

.avatar-container .avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.avatar-ring {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  animation: ringPulse 2s ease-in-out infinite;
}

@keyframes ringPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.5; }
}

.level-badge {
  position: absolute;
  bottom: 0;
  right: -5px;
  background: linear-gradient(135deg, #f6d365, #fda085);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(246, 211, 101, 0.4);
}

.user-details {
  flex: 1;
}

.user-info-card .username {
  font-size: 20px;
  font-weight: bold;
  color: white;
  margin: 0 0 12px 0;
}

.user-info-card .user-points {
  display: flex;
  gap: 20px;
}

.points-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.points-item i {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
}

.points-value {
  font-size: 18px;
  font-weight: bold;
  color: white;
}

.points-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.user-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  width: auto;
  height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: white;
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.action-btn i {
  font-size: 18px;
}

/* 能力成长曲线优化 */
.growth-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header .section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.section-header .section-title i {
  color: #409EFF;
  font-size: 19px;
}

.update-time {
  font-size: 13px;
  color: #a0a0c0;
}

.profile-entry {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  margin-top: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.profile-entry:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.entry-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.entry-icon i {
  font-size: 22px;
  color: white;
}

.entry-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.entry-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.entry-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4px;
}

.entry-arrow {
  font-size: 18px;
  color: white;
  transition: transform 0.3s ease;
}

.profile-entry:hover .entry-arrow {
  transform: translateX(5px);
}

/* 功能列表优化 */
.function-list {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.function-list .list-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border-bottom: 1px solid #f5f7fa;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out forwards;
  opacity: 0;
}

.function-list .list-item:last-child {
  border-bottom: none;
}

.function-list .list-item:hover {
  background: linear-gradient(90deg, #f8f9ff 0%, rgba(64, 158, 255, 0.05) 100%);
  transform: translateX(4px);
}

.function-list .list-item:active {
  transform: translateX(2px);
}

.item-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.function-list .list-item:hover .item-icon {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.item-icon i {
  font-size: 20px;
  color: white;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-title {
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
  transition: color 0.3s ease;
}

.function-list .list-item:hover .item-title {
  color: #409EFF;
}

.item-desc {
  font-size: 12px;
  color: #F56C6C;
  margin-top: 4px;
  font-weight: 500;
}

.item-arrow {
  font-size: 16px;
  color: #c0c4cc;
  transition: all 0.3s ease;
}

.function-list .list-item:hover .item-arrow {
  color: #409EFF;
  transform: translateX(5px);
}

/* 页面整体优化 */
.mine-page {
  padding: 16px;
  padding-bottom: 90px;
}

.bottom-spacer {
  height: 20px;
}

/* 用户信息卡片优化 */
.user-info-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
  border-radius: 24px;
  padding: 28px;
  margin-bottom: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
  border: 2px solid rgba(102, 126, 234, 0.3);
}

.card-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 250px;
  height: 250px;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.02);
}

.deco-1 {
  width: 120px;
  height: 120px;
  top: -30px;
  right: -20px;
  animation: float 6s ease-in-out infinite;
}

.deco-2 {
  width: 70px;
  height: 70px;
  top: 50px;
  right: 50px;
  animation: float 5s ease-in-out infinite 1s;
}

.deco-3 {
  width: 40px;
  height: 40px;
  bottom: -10px;
  right: 120px;
  animation: float 4s ease-in-out infinite 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.user-info-content {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar-container {
  position: relative;
}

.avatar-container .avatar-img {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.avatar-ring {
  position: absolute;
  top: -6px;
  left: -6px;
  right: -6px;
  bottom: -6px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.5);
  animation: ringPulse 2.5s ease-in-out infinite;
}

@keyframes ringPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.08); opacity: 0.6; }
}

.level-badge {
  position: absolute;
  bottom: -5px;
  right: -8px;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 14px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(246, 211, 101, 0.5);
  border: 2px solid white;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-info-card .username {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 10px 0;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.8), 0 0 30px rgba(255, 255, 255, 0.5), 0 0 50px rgba(102, 126, 234, 0.6);
  letter-spacing: 1px;
}

.user-bio {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.bio-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 12px;
  color: white;
  backdrop-filter: blur(4px);
}

.bio-tag i {
  font-size: 10px;
}

.user-info-card .user-points {
  display: flex;
  align-items: center;
  gap: 16px;
}

.points-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.points-value {
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4), 0 0 12px rgba(102, 126, 234, 0.3);
}

.points-label {
  font-size: 12px;
  color: #e0e2ea;
  font-weight: 500;
}

.points-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 4px;
}

.user-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-shrink: 0;
}

.action-btn {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.08);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.action-btn i {
  font-size: 20px;
}

/* 数据统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 18px 14px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideUp 0.6s ease-out forwards;
  opacity: 0;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2), 0 0 30px rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.6);
}

.stat-1 {
  animation-delay: 0.1s;
  border-left: 4px solid #409EFF;
}

.stat-2 {
  animation-delay: 0.2s;
  border-left: 4px solid #67C23A;
}

.stat-3 {
  animation-delay: 0.3s;
  border-left: 4px solid #E6A23C;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  position: relative;
  transition: all 0.3s ease;
}

.stat-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: inherit;
  filter: blur(10px);
  opacity: 0.4;
  z-index: -1;
}

.stat-1 .stat-icon {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
}

.stat-2 .stat-icon {
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
}

.stat-3 .stat-icon {
  background: linear-gradient(135deg, #E6A23C 0%, #FBA56C 100%);
}

.stat-icon i {
  font-size: 22px;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stat-card:hover .stat-icon {
  transform: scale(1.1);
}

.stat-card:hover .stat-icon::before {
  filter: blur(14px);
  opacity: 0.6;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 26px;
  font-weight: bold;
  color: #ffffff;
  line-height: 1;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.stat-label {
  font-size: 12px;
  color: #c0c4cc;
  font-weight: 500;
}

.stat-trend {
  position: absolute;
  top: 14px;
  right: 14px;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.up {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-trend i {
  font-size: 10px;
}

/* 能力成长曲线优化 */
.growth-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header .section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.section-header .section-title i {
  color: #409EFF;
  font-size: 19px;
}

.update-time {
  font-size: 13px;
  color: #a0a0c0;
}

.profile-entry {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
  margin-top: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.profile-entry::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.profile-entry:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
}

.profile-entry:hover::before {
  opacity: 1;
}

.entry-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
}

.profile-entry:hover .entry-icon {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.3);
}

.entry-icon i {
  font-size: 24px;
  color: white;
}

.entry-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.entry-title {
  font-size: 17px;
  font-weight: 600;
  color: white;
}

.entry-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 5px;
}

.entry-action {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: white;
  font-size: 13px;
  font-weight: 500;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
}

.profile-entry:hover .entry-action {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(4px);
}

.entry-arrow {
  font-size: 16px;
  color: white;
  transition: transform 0.3s ease;
}

.profile-entry:hover .entry-arrow {
  transform: translateX(5px);
}

/* 最近活动区域 */
.activity-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}

.more-link {
  font-size: 13px;
  color: #409EFF;
  cursor: pointer;
  transition: color 0.3s ease;
}

.more-link:hover {
  color: #66B1FF;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 14px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.activity-item:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
  transform: translateX(6px);
}

.activity-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.activity-title {
  font-size: 15px;
  font-weight: 600;
  color: #e0e2ea;
  transition: all 0.3s ease;
  text-shadow: 0 0 8px rgba(102, 126, 234, 0.2);
}

.activity-item:hover .activity-title {
  color: #409EFF;
  font-weight: 700;
}

.activity-time {
  font-size: 13px;
  color: #c0c4cc;
  font-weight: 500;
}

.activity-score {
  display: flex;
  align-items: baseline;
  gap: 4px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #67C23A, #85CE61);
  border-radius: 20px;
  box-shadow: 0 3px 10px rgba(103, 194, 58, 0.3);
}

.score-num {
  font-size: 18px;
  font-weight: bold;
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.score-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
}

/* 功能列表优化 */
.function-list {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}

.list-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
}

.list-title {
  font-size: 17px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.function-list .list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out forwards;
  opacity: 0;
}

.function-list .list-item:last-child {
  border-bottom: none;
}

.function-list .list-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateX(6px);
}

.function-list .list-item:active {
  transform: translateX(3px);
}

.item-icon {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  transition: all 0.3s ease;
}

.item-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: inherit;
  filter: blur(8px);
  opacity: 0.5;
  z-index: -1;
  transition: all 0.3s ease;
}

.function-list .list-item:hover .item-icon {
  transform: scale(1.15);
}

.function-list .list-item:hover .item-icon::before {
  filter: blur(12px);
  opacity: 0.7;
}

.item-icon i {
  font-size: 21px;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.item-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #e0e2ea;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
  text-shadow: 0 0 8px rgba(102, 126, 234, 0.2);
}

.function-list .list-item:hover .item-title {
  color: #409EFF;
  font-weight: 700;
}

.item-desc {
  font-size: 13px;
  color: #c0c4cc;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  font-weight: 500;
}

.item-arrow {
  font-size: 16px;
  color: #c0c4cc;
  transition: all 0.3s ease;
}

.function-list .list-item:hover .item-arrow {
  color: #409EFF;
  transform: translateX(4px);
}

/* 动画优化 */
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

/* 简历评价样式 */
.resume-evaluation {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.resume-evaluation .overall-score {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  border: 1px solid #bae6fd;
}

.resume-score {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
}

.dimensions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.dimension-item {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dimension-label {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
}

.dimension-score-bar {
  position: relative;
  height: 8px;
  background-color: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
  border-radius: 4px;
  transition: width 0.8s ease-out;
}

.score-text {
  position: absolute;
  right: 0;
  top: -24px;
  font-size: 14px;
  font-weight: 600;
  color: #10b981;
}

.dimension-comment {
  font-size: 13px;
  color: #a0a0c0;
  line-height: 1.5;
}

.strengths-improvements {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.strengths-section,
.improvements-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strengths-section .list-title,
.improvements-section .list-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.strength-item,
.improvement-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  line-height: 1.5;
  padding: 12px;
  border-radius: 8px;
}

.strength-item {
  background-color: #f0f9eb;
  border: 1px solid #e1f5e8;
}

.improvement-item {
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
}

.strength-item i {
  color: #67c23a;
  margin-top: 2px;
  flex-shrink: 0;
}

.improvement-item i {
  color: #f56c6c;
  margin-top: 2px;
  flex-shrink: 0;
}

.template-suggestion {
  background-color: #fff7e6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  padding: 16px;
}

.template-suggestion .list-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.suggestion-content {
  font-size: 14px;
  color: #a0a0c0;
  line-height: 1.6;
}

/* 随机练一题对话框样式 - 终极优化版 */
.random-practice-dialog {
  --el-dialog-bg-color: transparent !important;
  --el-dialog-header-bg: transparent !important;
}

.random-practice-dialog :deep(.el-overlay) {
  background: rgba(0, 0, 0, 0.85) !important;
  backdrop-filter: blur(12px);
}

.random-practice-dialog :deep(.el-dialog) {
  border-radius: 24px !important;
  overflow: hidden !important;
  background: transparent !important;
  position: relative;
}

.random-practice-dialog :deep(.el-dialog)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(145deg, rgba(15, 12, 41, 0.96) 0%, rgba(30, 25, 65, 0.96) 50%, rgba(15, 12, 41, 0.96) 100%),
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
}

.random-practice-dialog :deep(.el-dialog)::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 15% 10%, rgba(139, 92, 246, 0.2) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(99, 102, 241, 0.15) 0%, transparent 45%);
  z-index: 1;
  pointer-events: none;
}

.random-practice-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.95) 0%, rgba(139, 92, 246, 0.95) 50%, rgba(168, 85, 247, 0.95) 100%) !important;
  padding: 20px 28px !important;
  margin: 0 !important;
  position: relative !important;
  overflow: hidden !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
  z-index: 10;
}

.random-practice-dialog :deep(.el-dialog__header)::before {
  content: '';
  position: absolute;
  top: -60%;
  right: -20%;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 55%);
  animation: headerGlow 4.5s ease-in-out infinite;
}

@keyframes headerGlow {
  0%, 100% { opacity: 0.4; transform: scale(0.9); }
  50% { opacity: 0.8; transform: scale(1.15); }
}

.random-practice-dialog :deep(.el-dialog__title) {
  color: #ffffff !important;
  font-size: 38px !important;
  font-weight: 900 !important;
  position: relative !important;
  z-index: 10 !important;
  letter-spacing: 5px;
  text-shadow: 
    0 0 12px rgba(255, 255, 255, 1),
    0 0 24px rgba(255, 255, 255, 0.9),
    0 0 36px rgba(255, 255, 255, 0.7),
    0 0 48px rgba(139, 92, 246, 0.8),
    0 0 60px rgba(99, 102, 241, 0.6),
    0 2px 6px rgba(0, 0, 0, 0.6) !important;
  animation: titleShake 0.5s ease-in-out infinite alternate, titleGlow 1s ease-in-out infinite alternate;
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.random-practice-dialog :deep(.el-dialog__title)::before {
  content: '⚡';
  font-size: 32px;
  animation: iconBounce 0.6s ease-in-out infinite;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.8));
}

.random-practice-dialog :deep(.el-dialog__title)::after {
  content: '⚡';
  font-size: 32px;
  animation: iconBounce 0.6s ease-in-out infinite 0.3s;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.8));
}

@keyframes iconBounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-6px) scale(1.1); }
}

@keyframes titleShake {
  0% { transform: translateX(0); }
  100% { transform: translateX(2px); }
}

@keyframes titleGlow {
  0% {
    text-shadow: 
      0 0 12px rgba(255, 255, 255, 1),
      0 0 24px rgba(255, 255, 255, 0.9),
      0 0 36px rgba(255, 255, 255, 0.7),
      0 0 48px rgba(139, 92, 246, 0.8),
      0 0 60px rgba(99, 102, 241, 0.6),
      0 2px 6px rgba(0, 0, 0, 0.6);
  }
  100% {
    text-shadow: 
      0 0 18px rgba(255, 255, 255, 1),
      0 0 36px rgba(255, 255, 255, 1),
      0 0 54px rgba(255, 255, 255, 0.9),
      0 0 72px rgba(139, 92, 246, 1),
      0 0 90px rgba(99, 102, 241, 0.8),
      0 2px 6px rgba(0, 0, 0, 0.6);
  }
}

.random-practice-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white !important;
  font-size: 22px !important;
  transition: all 0.3s ease !important;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  z-index: 10;
}

.random-practice-dialog :deep(.el-dialog__headerbtn .el-dialog__close:hover) {
  transform: rotate(90deg) !important;
  color: white !important;
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 16px rgba(255, 255, 255, 0.25);
}

.random-practice-dialog :deep(.el-dialog__body) {
  padding: 28px !important;
  background: transparent !important;
  position: relative !important;
  z-index: 5 !important;
}

.random-practice-content {
  max-height: 62vh;
  overflow-y: auto;
  padding-right: 16px;
  position: relative;
}

.random-practice-content::-webkit-scrollbar {
  width: 10px;
}

.random-practice-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 5px;
  border: 1px solid rgba(139, 92, 246, 0.15);
  margin: 4px 0;
}

.random-practice-content::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 5px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
}

.random-practice-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #818cf8 0%, #a78bfa 100%);
}

.random-question-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.random-question-meta .question-type,
.random-question-meta .question-category,
.random-question-meta .question-difficulty {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(12px);
  border: 1px solid;
  transition: all 0.25s ease;
  position: relative;
}

.random-question-meta .question-type.single {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(59, 130, 246, 0.08) 100%);
  border-color: rgba(96, 165, 250, 0.45);
  color: #93c5fd;
}

.random-question-meta .question-type.multiple {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.18) 0%, rgba(249, 115, 22, 0.08) 100%);
  border-color: rgba(251, 146, 60, 0.45);
  color: #fdba74;
}

.random-question-meta .question-category {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.18) 0%, rgba(34, 197, 94, 0.08) 100%);
  border-color: rgba(74, 222, 128, 0.45);
  color: #86efac;
}

.random-question-meta .question-difficulty.easy {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.18) 0%, rgba(34, 197, 94, 0.08) 100%);
  border-color: rgba(74, 222, 128, 0.45);
  color: #86efac;
}

.random-question-meta .question-difficulty.medium {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.18) 0%, rgba(234, 179, 8, 0.08) 100%);
  border-color: rgba(250, 204, 21, 0.45);
  color: #fde047;
}

.random-question-meta .question-difficulty.hard {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.18) 0%, rgba(239, 68, 68, 0.08) 100%);
  border-color: rgba(248, 113, 113, 0.45);
  color: #fca5a5;
}

.random-question-text {
  font-size: 18px;
  color: #f9fafb;
  line-height: 1.7;
  margin: 0 0 24px 0;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  position: relative;
  padding: 18px 22px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.14) 0%, rgba(99, 102, 241, 0.07) 100%);
  border-radius: 16px;
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-left: 3px solid #8b5cf6;
  backdrop-filter: blur(16px);
}

.random-question-text::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 20px,
      rgba(255, 255, 255, 0.02) 20px,
      rgba(255, 255, 255, 0.02) 21px
    );
  border-radius: 16px;
  pointer-events: none;
}

.random-options-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.random-practice-dialog .option-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
  border-radius: 16px;
  border: 2px solid rgba(139, 92, 246, 0.18);
  transition: all 0.25s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(16px);
}

.random-practice-dialog .option-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 16px,
      rgba(139, 92, 246, 0.03) 16px,
      rgba(139, 92, 246, 0.03) 17px
    );
  border-radius: 16px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.random-practice-dialog .option-item:hover::before {
  opacity: 1;
}

.random-practice-dialog .option-item:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.16) 0%, rgba(99, 102, 241, 0.08) 100%);
  border-color: rgba(139, 92, 246, 0.5);
  transform: translateX(4px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.2);
}

.random-practice-dialog .option-item.selected {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.22) 0%, rgba(59, 130, 246, 0.12) 100%);
  border-color: #3b82f6;
  box-shadow: 0 8px 28px rgba(59, 130, 246, 0.3), inset 0 0 20px rgba(59, 130, 246, 0.12);
  transform: translateX(4px);
}

.random-practice-dialog .option-item.correct {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.22) 0%, rgba(34, 197, 94, 0.12) 100%);
  border-color: #22c55e;
  box-shadow: 0 8px 28px rgba(34, 197, 94, 0.3), inset 0 0 20px rgba(34, 197, 94, 0.12);
}

.random-practice-dialog .option-item.incorrect {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.22) 0%, rgba(239, 68, 68, 0.12) 100%);
  border-color: #ef4444;
  box-shadow: 0 8px 28px rgba(239, 68, 68, 0.3), inset 0 0 20px rgba(239, 68, 68, 0.12);
}

.random-practice-dialog .option-letter {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(16px);
  border: 2px solid rgba(139, 92, 246, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #d1d5db;
  flex-shrink: 0;
  transition: all 0.25s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.random-practice-dialog .option-item.selected .option-letter {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  border-color: #3b82f6;
  color: white;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
  transform: scale(1.1);
}

.random-practice-dialog .option-item.correct .option-letter {
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
  border-color: #22c55e;
  color: white;
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.45);
  transform: scale(1.1);
}

.random-practice-dialog .option-item.incorrect .option-letter {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  border-color: #ef4444;
  color: white;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.45);
  transform: scale(1.1);
}

.random-practice-dialog .option-text {
  flex: 1;
  font-size: 16px;
  color: #e5e7eb;
  line-height: 1.6;
  font-weight: 500;
  transition: all 0.25s ease;
}

.random-practice-dialog .option-item:hover .option-text {
  color: #ffffff;
}

.random-practice-dialog .correct-icon {
  font-size: 26px;
  color: #22c55e;
  font-weight: bold;
  animation: correctPulse 0.5s ease-out;
  filter: drop-shadow(0 0 12px rgba(34, 197, 94, 0.5));
}

@keyframes correctPulse {
  0% { transform: scale(0.4); opacity: 0; }
  70% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

.random-practice-dialog .incorrect-icon {
  font-size: 26px;
  color: #ef4444;
  font-weight: bold;
  animation: incorrectShake 0.45s ease-out;
  filter: drop-shadow(0 0 12px rgba(239, 68, 68, 0.5));
}

@keyframes incorrectShake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}

.random-practice-dialog .answer-section {
  margin-top: 24px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.035) 100%);
  border-radius: 16px;
  border: 1px solid rgba(139, 92, 246, 0.25);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(16px);
}

.random-practice-dialog .answer-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7, #6366f1);
  background-size: 200% 100%;
  animation: answerBorder 3s linear infinite;
}

@keyframes answerBorder {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

.random-practice-dialog .correct-answer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.random-practice-dialog .answer-label {
  font-size: 15px;
  color: #9ca3af;
  font-weight: 600;
}

.random-practice-dialog .answer-value {
  font-size: 18px;
  font-weight: 700;
  color: #22c55e;
  text-shadow: 0 0 14px rgba(34, 197, 94, 0.4);
}

.random-practice-dialog .answer-value::before {
  content: '✓ ';
  font-weight: bold;
}

.random-practice-dialog .analysis-section {
  border-top: 1px solid rgba(139, 92, 246, 0.2);
  padding-top: 16px;
  margin-top: 16px;
  position: relative;
  z-index: 1;
}

.random-practice-dialog .analysis-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 12px;
}

.random-practice-dialog .analysis-label i {
  color: #f59e0b;
  font-size: 18px;
}

.random-practice-dialog .analysis-text {
  font-size: 15px;
  color: #d1d5db;
  line-height: 1.7;
  margin: 0;
  padding: 14px 18px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
  border-radius: 12px;
  border-left: 2px solid #f59e0b;
}

.random-practice-dialog :deep(.el-dialog__footer) {
  padding: 20px 28px !important;
  border-top: 1px solid rgba(139, 92, 246, 0.18) !important;
  background: linear-gradient(180deg, transparent 0%, rgba(15, 12, 41, 0.45) 100%) !important;
  position: relative;
  z-index: 5;
}

.random-practice-dialog .dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.random-practice-dialog .action-btn {
  padding: 12px 28px;
  border: none;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.3px;
  position: relative;
  overflow: hidden;
}

.random-practice-dialog .submit-btn {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
  order: 3;
}

.random-practice-dialog .submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.45);
}

.random-practice-dialog .next-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.35);
  order: 2;
}

.random-practice-dialog .next-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.45);
}

.random-practice-dialog .close-btn {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.06) 100%);
  color: #9ca3af;
  border: 2px solid rgba(139, 92, 246, 0.25);
  backdrop-filter: blur(16px);
  order: 1;
}

.random-practice-dialog .close-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0.09) 100%);
  color: #ffffff;
  border-color: rgba(139, 92, 246, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.2);
}

/* 真题详情对话框样式 */
.exam-question-dialog {
  --el-dialog-bg-color: transparent !important;
  --el-dialog-header-bg: transparent !important;
}

.exam-question-dialog :deep(.el-overlay) {
  background: rgba(0, 0, 0, 0.85) !important;
  backdrop-filter: blur(12px);
}

.exam-question-dialog :deep(.el-dialog) {
  border-radius: 24px !important;
  overflow: hidden !important;
  background: transparent !important;
  position: relative;
}

.exam-question-dialog :deep(.el-dialog)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(145deg, rgba(15, 12, 41, 0.96) 0%, rgba(30, 25, 65, 0.96) 50%, rgba(15, 12, 41, 0.96) 100%),
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
}

.exam-question-dialog :deep(.el-dialog)::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 15% 10%, rgba(139, 92, 246, 0.2) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(99, 102, 241, 0.15) 0%, transparent 45%);
  z-index: 1;
  pointer-events: none;
}

.exam-question-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.95) 0%, rgba(139, 92, 246, 0.95) 50%, rgba(168, 85, 247, 0.95) 100%) !important;
  padding: 20px 28px !important;
  margin: 0 !important;
  position: relative !important;
  overflow: hidden !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
  z-index: 10;
}

.exam-question-dialog :deep(.el-dialog__header)::before {
  content: '';
  position: absolute;
  top: -60%;
  right: -20%;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 55%);
  animation: headerGlow 4.5s ease-in-out infinite;
}

.exam-question-dialog :deep(.el-dialog__title) {
  color: #ffffff !important;
  font-size: 20px !important;
  font-weight: 700 !important;
  position: relative !important;
  z-index: 10 !important;
  text-shadow: 0 0 12px rgba(255, 255, 255, 0.5), 0 0 24px rgba(139, 92, 246, 0.5) !important;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.exam-question-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white !important;
  font-size: 22px !important;
  transition: all 0.3s ease !important;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  z-index: 10;
}

.exam-question-dialog :deep(.el-dialog__headerbtn .el-dialog__close:hover) {
  transform: rotate(90deg) !important;
  color: white !important;
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 16px rgba(255, 255, 255, 0.25);
}

.exam-question-dialog :deep(.el-dialog__body) {
  padding: 28px !important;
  background: transparent !important;
  position: relative !important;
  z-index: 5 !important;
}

.exam-question-detail {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 8px;
  position: relative;
}

.exam-question-detail::-webkit-scrollbar {
  width: 10px;
}

.exam-question-detail::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 5px;
  border: 1px solid rgba(139, 92, 246, 0.15);
  margin: 4px 0;
}

.exam-question-detail::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 5px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
}

.exam-question-detail::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #818cf8 0%, #a78bfa 100%);
}

.exam-question-section,
.exam-answer-section,
.exam-analysis-section {
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(99, 102, 241, 0.06) 100%);
  border-radius: 16px;
  border: 1px solid rgba(139, 92, 246, 0.25);
  backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
}

.exam-question-section::before,
.exam-answer-section::before,
.exam-analysis-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 20px,
    rgba(255, 255, 255, 0.02) 20px,
    rgba(255, 255, 255, 0.02) 21px
  );
  border-radius: 16px;
  pointer-events: none;
}

.exam-question-dialog .section-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 12px 0;
  text-shadow: 0 0 8px rgba(102, 126, 234, 0.5);
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.exam-question-dialog .section-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.6);
}

.exam-question-dialog .question-content,
.exam-question-dialog .answer-content,
.exam-question-dialog .analysis-content {
  font-size: 15px;
  color: #f9fafb;
  line-height: 1.8;
  margin: 0;
  position: relative;
  z-index: 1;
}

.question-meta {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
}

.category-tag {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.18) 0%, rgba(34, 197, 94, 0.08) 100%);
  border: 1px solid rgba(74, 222, 128, 0.45);
  color: #86efac;
}

.question-time {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(59, 130, 246, 0.08) 100%);
  border: 1px solid rgba(96, 165, 250, 0.45);
  color: #93c5fd;
}

.exam-question-dialog :deep(.el-dialog__footer) {
  background: transparent !important;
  padding: 16px 28px 24px !important;
  position: relative !important;
  z-index: 5 !important;
  border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.exam-question-dialog .dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.exam-question-dialog :deep(.el-button) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  padding: 10px 28px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
  transition: all 0.3s ease;
}

.exam-question-dialog :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

/* 注册对话框样式 */
.register-dialog {
  --el-dialog-bg-color: #120826 !important;
  --el-dialog-header-bg: transparent !important;
  --el-text-color-primary: #ffffff !important;
  --el-text-color-regular: #ffffff !important;
  --el-form-label-color: #ffffff !important;
}

.register-dialog :deep(.el-input) {
  --el-text-color-primary: #000000 !important;
  --el-text-color-regular: #000000 !important;
}

.register-dialog :deep(.el-overlay) {
  background: rgba(0, 0, 0, 0.9) !important;
  backdrop-filter: blur(12px);
  pointer-events: none;
}

.register-dialog :deep(.el-dialog) {
  pointer-events: auto !important;
}

.register-dialog :deep(.el-dialog) {
  border-radius: 24px !important;
  overflow: hidden !important;
  background: linear-gradient(145deg, #120826 0%, #1f1540 50%, #120826 100%) !important;
  position: relative;
  box-shadow: 
    0 0 40px rgba(0, 0, 0, 0.8), 
    0 0 80px rgba(167, 139, 250, 0.4),
    inset 0 0 2px rgba(196, 181, 253, 0.6),
    inset 0 0 10px rgba(0, 0, 0, 0.5) !important;
}

.register-dialog :deep(.el-dialog)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px solid transparent;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.9), rgba(196, 181, 253, 0.4), rgba(167, 139, 250, 0.9)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  z-index: 2;
  pointer-events: none;
  animation: borderGlow 3s ease-in-out infinite;
}

@keyframes borderGlow {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.register-dialog :deep(.el-dialog)::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 24px,
      rgba(167, 139, 250, 0.08) 24px,
      rgba(167, 139, 250, 0.08) 25px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 24px,
      rgba(167, 139, 250, 0.08) 24px,
      rgba(167, 139, 250, 0.08) 25px
    );
  z-index: 0;
  pointer-events: none;
}

.register-dialog .register-form::before {
  content: '';
  position: absolute;
  top: -28px;
  left: -28px;
  right: -28px;
  bottom: -28px;
  background: linear-gradient(
    180deg,
    rgba(167, 139, 250, 0) 0%,
    rgba(167, 139, 250, 0.1) 48%,
    rgba(167, 139, 250, 0.1) 52%,
    rgba(167, 139, 250, 0) 100%
  );
  animation: scanLine 3s linear infinite;
  z-index: 0;
  pointer-events: none;
}

@keyframes scanLine {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

.register-dialog .glow-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 15% 10%, rgba(167, 139, 250, 0.3) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(124, 58, 237, 0.25) 0%, transparent 45%);
  z-index: 1;
  pointer-events: none;
}

.register-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.98) 0%, rgba(167, 139, 250, 0.98) 50%, rgba(196, 181, 253, 0.98) 100%) !important;
  padding: 20px 28px !important;
  margin: 0 !important;
  position: relative !important;
  overflow: hidden !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
  z-index: 10;
}

.register-dialog :deep(.el-dialog__header)::before {
  content: '';
  position: absolute;
  top: -60%;
  right: -20%;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 55%);
  animation: headerGlow 4.5s ease-in-out infinite;
}

.register-dialog :deep(.el-dialog__title) {
  color: #ffffff !important;
  font-size: 36px !important;
  font-weight: 800 !important;
  position: relative !important;
  z-index: 10 !important;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.6) !important;
  letter-spacing: 0px;
}

.register-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white !important;
  font-size: 22px !important;
  transition: all 0.3s ease !important;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  z-index: 10;
}

.register-dialog :deep(.el-dialog__headerbtn .el-dialog__close:hover) {
  transform: rotate(90deg) !important;
  color: white !important;
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 16px rgba(255, 255, 255, 0.25);
}

.register-dialog :deep(.el-dialog__body) {
  padding: 32px !important;
  background: transparent !important;
  position: relative !important;
  z-index: 5 !important;
  pointer-events: auto !important;
}

.register-dialog .register-form {
  position: relative;
  z-index: 1;
  pointer-events: auto;
}

.register-dialog :deep(.el-form-item__content) {
  pointer-events: auto;
}

.register-dialog :deep(.el-form-item__label) {
  color: #ffffff !important;
  font-weight: 800 !important;
  font-size: 14px !important;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.6) !important;
  letter-spacing: 0px;
}

.register-dialog :deep(.el-input__wrapper) {
  background: #ffffff !important;
  border: 1px solid #dcdfe6 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  transition: all 0.3s ease !important;
  position: relative;
  overflow: visible;
}

.register-dialog :deep(.el-input__wrapper)::before {
  display: none;
}

.register-dialog :deep(.el-input__wrapper:hover) {
  border-color: #409eff !important;
  background: #ffffff !important;
  box-shadow: none !important;
}

.register-dialog :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff !important;
  background: #ffffff !important;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
}

@keyframes inputPulse {
  0%, 100% {
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
  }
  50% {
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) !important;
  }
}

.register-dialog :deep(.el-input__wrapper) .el-input__inner {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
  font-size: 15px;
  font-weight: normal;
}

.register-dialog :deep(.el-input__wrapper) input::placeholder {
  color: #999999 !important;
  -webkit-text-fill-color: #999999 !important;
}

.register-dialog :deep(.el-input__wrapper) input {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
}

.register-dialog :deep(.el-dialog__footer) {
  background: transparent !important;
  padding: 20px 28px 28px !important;
  position: relative !important;
  z-index: 5 !important;
  border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
}

.register-dialog .dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.register-dialog :deep(.el-button) {
  border-radius: 14px !important;
  padding: 12px 28px !important;
  font-weight: 700 !important;
  font-size: 16px !important;
  transition: all 0.3s ease !important;
}

.register-dialog :deep(.el-button:not(.el-button--primary)) {
  background: rgba(255, 255, 255, 0.18) !important;
  color: rgba(255, 255, 255, 1) !important;
  border: 2px solid rgba(196, 181, 253, 0.6) !important;
  backdrop-filter: blur(4px);
}

.register-dialog :deep(.el-button:not(.el-button--primary):hover) {
  background: rgba(255, 255, 255, 0.28) !important;
  border-color: rgba(230, 219, 255, 0.9) !important;
  color: #ffffff !important;
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(196, 181, 253, 0.4) !important;
}

.register-dialog :deep(.el-button--primary) {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 50%, #ddd6fe 100%) !important;
  color: white !important;
  border: none !important;
  box-shadow: 
    0 6px 20px rgba(167, 139, 250, 0.7),
    0 0 30px rgba(167, 139, 250, 0.45) inset !important;
  position: relative;
  overflow: hidden;
  letter-spacing: 0.5px;
}

.register-dialog :deep(.el-button--primary)::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: buttonShine 1.5s infinite;
}

@keyframes buttonShine {
  0% { left: -100%; }
  100% { left: 100%; }
}

.register-dialog :deep(.el-button--primary:hover) {
  transform: translateY(-3px);
  box-shadow: 
    0 10px 35px rgba(167, 139, 250, 0.9),
    0 0 40px rgba(167, 139, 250, 0.6) inset !important;
}

.register-dialog .black-text-input input {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
}

.register-dialog .black-text-input .el-input__wrapper {
  background-color: #ffffff !important;
}
</style>