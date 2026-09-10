<template>
  <div class="main-content">
    <div class="page-background"></div>
    <div class="scan-line"></div>
    
    <div class="ai-interview-header">
      <div class="back-btn" @click="handleBack">
        <i class="el-icon-arrow-left"></i>
      </div>
      <h2 class="ai-interview-title">{{ interviewType === 'voice' ? '语音面试' : interviewType === 'avatar' ? '数字人面试' : 'AI交流对话面试' }}</h2>
      <div class="history-link" @click="handleHistoryClick">历史记录</div>
    </div>
    
    <div class="ai-interview-form">
      <div class="form-section">
        <h3 class="section-title">面试岗位</h3>
        <div class="job-select">
          <el-input v-model="formData.job" placeholder="请输入面试岗位"></el-input>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">岗位类型</h3>
        <div class="job-type-options">
          <el-radio-group v-model="formData.jobType" class="radio-group">
            <el-radio value="java_backend">Java后端开发</el-radio>
            <el-radio value="web_frontend">Web前端开发</el-radio>
            <el-radio value="python_algorithm">Python算法工程师</el-radio>
            <el-radio value="test_engineer">测试工程师</el-radio>
            <el-radio value="public_sector">事业单位</el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">工作经验阶段</h3>
        <div class="experience-options">
          <el-radio-group v-model="formData.experience" class="radio-group">
            <el-radio value="实习">实习</el-radio>
            <el-radio value="应届">应届</el-radio>
            <el-radio value="1-3年工作经验">1-3年工作经验</el-radio>
            <el-radio value="3年以上工作经验">3年以上工作经验</el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">面试官角色</h3>
        <div class="interviewer-options">
          <el-radio-group v-model="formData.interviewerRole" class="radio-group">
            <el-radio value="HR面试官">HR面试官</el-radio>
            <el-radio value="业务面试官">业务面试官</el-radio>
            <el-radio value="技术面试官">技术面试官</el-radio>
            <el-radio value="CEO/总经理">CEO/总经理</el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">个人简历</h3>
        <div class="resume-upload">
          <el-upload
            class="resume-uploader"
            action="#"
            :auto-upload="false"
            :on-change="handleResumeUpload"
            :limit="1"
            accept=".pdf,.doc,.docx,.txt"
          >
            <el-button size="large" type="primary" class="resume-btn">导入简历</el-button>
            <template #tip>
              <div class="upload-tip">
                支持PDF（不支持扫描件）、Doc、Docx、txt格式文档，建议上传5000字以内的纯文档，文档大小不超5M
              </div>
            </template>
          </el-upload>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">面试压力等级</h3>
        <div class="pressure-level-options">
          <el-radio-group v-model="formData.pressureLevel" class="radio-group">
            <el-radio :value="1">
              <div class="pressure-option">
                <span class="pressure-level">等级1</span>
                <span class="pressure-desc">温和友好 - 适合初次练习</span>
              </div>
            </el-radio>
            <el-radio :value="2">
              <div class="pressure-option">
                <span class="pressure-level">等级2</span>
                <span class="pressure-desc">专业严谨 - 模拟常规面试</span>
              </div>
            </el-radio>
            <el-radio :value="3">
              <div class="pressure-option">
                <span class="pressure-level">等级3</span>
                <span class="pressure-desc">高压挑战 - 模拟真实压力面试</span>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">面试时长</h3>
        <div class="interview-duration-options">
          <el-radio-group v-model="formData.duration" class="radio-group">
            <el-radio :value="5">
              <div class="duration-option">
                <span class="duration-time">5分钟</span>
                <span class="duration-desc">快速初筛</span>
              </div>
            </el-radio>
            <el-radio :value="10">
              <div class="duration-option">
                <span class="duration-time">10分钟</span>
                <span class="duration-desc">基础考察</span>
              </div>
            </el-radio>
            <el-radio :value="20">
              <div class="duration-option">
                <span class="duration-time">20分钟</span>
                <span class="duration-desc">核心考察</span>
              </div>
            </el-radio>
            <el-radio :value="30">
              <div class="duration-option">
                <span class="duration-time">30分钟</span>
                <span class="duration-desc">全面考察</span>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">目标公司信息（非必填）</h3>
        <div class="company-info">
          <el-input v-model="formData.company" placeholder="请输入目标公司名称"></el-input>
        </div>
      </div>
      
      <div class="start-ai-interview">
        <el-button 
          type="primary" 
          class="start-btn" 
          @click="handleStartInterview"
          :loading="isLoading"
          :disabled="isLoading"
        >
          {{ isLoading ? '生成问题中...' : '开始面试' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AIInterviewConfig',
  props: {
    interviewType: {
      type: String,
      default: 'ai'
    },
    initialFormData: {
      type: Object,
      default: () => ({
        job: 'Java工程师',
        jobType: 'java_backend',
        experience: '实习',
        interviewerRole: 'HR面试官',
        company: '',
        pressureLevel: 1,
        duration: 10,
        resumeText: ''
      })
    }
  },
  data() {
    return {
      formData: {
        job: 'Java工程师',
        jobType: 'java_backend',
        experience: '实习',
        interviewerRole: 'HR面试官',
        company: '',
        pressureLevel: 1,
        duration: 10,
        resumeText: ''
      },
      isLoading: false
    }
  },
  mounted() {
    this.formData = { ...this.initialFormData }
  },
  methods: {
    handleBack() {
      this.$emit('back')
    },
    handleHistoryClick() {
      this.$emit('history-click')
    },
    handleResumeUpload(file) {
      const rawFile = file.raw
      if (!rawFile) return
      
      try {
        if (rawFile.type === 'text/plain' || rawFile.name.endsWith('.txt')) {
          this.readFileAsText(rawFile).then(text => {
            this.formData.resumeText = text
            this.$message.success('简历解析成功')
          })
        } else if (rawFile.name.endsWith('.pdf')) {
          this.parsePdfResume(rawFile)
        } else if (rawFile.name.endsWith('.doc') || rawFile.name.endsWith('.docx')) {
          this.$message.warning('Word文档解析功能暂未完全实现，请使用TXT格式或手动粘贴简历内容')
        }
      } catch (error) {
        console.error('简历解析失败:', error)
        this.$message.error('简历解析失败，请重试或手动粘贴简历内容')
      }
    },
    async parsePdfResume(file) {
      this.$message.info('正在解析 PDF 简历...')
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
        const response = await fetch(API_BASE + '/api/resume/parse-pdf', {
          method: 'POST',
          body: formData
        })
        
        if (!response.ok) {
          throw new Error('解析失败')
        }
        
        const result = await response.json()
        
        if (result.status === 'success' && result.text) {
          this.formData.resumeText = result.text
          this.$message.success('PDF简历解析成功')
        } else if (result.message) {
          this.$message.warning(result.message + '，请手动粘贴简历内容')
        } else {
          this.$message.warning('PDF中未提取到文本，请手动粘贴简历内容')
        }
      } catch (error) {
        console.error('PDF解析失败:', error)
        this.$message.error('PDF解析失败，请手动粘贴简历内容')
      }
    },
    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = (e) => reject(e)
        reader.readAsText(file)
      })
    },
    handleStartInterview() {
      if (!this.formData.job) {
        this.$message.error('请输入面试岗位')
        return
      }
      
      this.$emit('start-interview', this.formData)
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

.ai-interview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  position: relative;
  z-index: 2;
}

.back-btn {
  cursor: pointer;
  font-size: 20px;
  color: #a0a3b1;
  transition: all 0.3s ease;
}

.back-btn:hover {
  color: #667eea;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.ai-interview-title {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.history-link {
  color: #667eea;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.history-link:hover {
  color: #764ba2;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.ai-interview-form {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 2;
}

.form-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #e0e2ea;
  margin: 0 0 12px 0;
}

.job-select,
.company-info {
  width: 100%;
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.pressure-option,
.duration-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pressure-level,
.duration-time {
  font-weight: 500;
  color: #e0e2ea;
}

.pressure-desc,
.duration-desc {
  font-size: 12px;
  color: #909399;
}

.resume-upload {
  margin-top: 8px;
}

.resume-btn {
  min-width: 150px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.start-ai-interview {
  margin-top: 30px;
  text-align: center;
}

.start-btn {
  min-width: 200px;
  font-size: 16px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}
</style>
