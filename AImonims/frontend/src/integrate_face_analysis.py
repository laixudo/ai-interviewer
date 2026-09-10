#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改import语句，添加FaceAnalysis
old_import = "import AIAvatar from './AIAvatar.vue'"
new_import = """import AIAvatar from './AIAvatar.vue'
import FaceAnalysis from './FaceAnalysis.vue'"""

content = content.replace(old_import, new_import)

# 2. 修改数字人模式部分，使用FaceAnalysis替换AIAvatar
old_avatar_section = '''      <!-- 数字人模式 -->
      <div v-else>
        <AIAvatar />
      </div>'''

new_avatar_section = '''      <!-- 数字人+面部分析模式 -->
      <div v-else class="avatar-camera-mode">
        <div class="camera-wrapper">
          <FaceAnalysis
            ref="faceAnalysisRef"
            :interviewId="props.currentInterviewId"
            :analysisEnabled="true"
            @interviewStart="handleFaceAnalysisStart"
            @interviewEnd="handleFaceAnalysisEnd"
            @analysisResult="handleFaceAnalysisResult"
          />
        </div>
        <AIAvatar />
      </div>'''

content = content.replace(old_avatar_section, new_avatar_section)

# 3. 修改interviewMode ref的注释
old_mode_ref = "const interviewMode = ref('text') // text, voice, avatar"
new_mode_ref = "const interviewMode = ref('text') // text, voice, avatar, camera"

content = content.replace(old_mode_ref, new_mode_ref)

# 4. 添加faceAnalysisRef
old_ref_section = "const chatMessagesRef = ref(null)"
new_ref_section = """const chatMessagesRef = ref(null)
const faceAnalysisRef = ref(null)"""

content = content.replace(old_ref_section, new_ref_section)

# 5. 添加FaceAnalysis的事件处理方法
old_handleBack = '''const handleBack = () => {
  if (isRecording.value) {
    stopVoiceInput()
  }
  emit('back')
}'''

new_handleBack = '''const handleBack = () => {
  if (isRecording.value) {
    stopVoiceInput()
  }
  emit('back')
}

const handleFaceAnalysisStart = (interviewId) => {
  console.log('面部分析开始:', interviewId)
}

const handleFaceAnalysisEnd = (interviewId) => {
  console.log('面部分析结束:', interviewId)
}

const handleFaceAnalysisResult = (result) => {
  console.log('面部分析结果:', result)
}'''

content = content.replace(old_handleBack, new_handleBack)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("AIInterviewChat.vue修改成功！")
