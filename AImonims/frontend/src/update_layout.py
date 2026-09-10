#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义新的数字人+摄像头+对话布局
new_layout = '''      <!-- 数字人+摄像头+对话一体化模式 -->
      <div v-else class="avatar-camera-mode">
        <div class="unified-interview-layout">
          <!-- 左侧：摄像头 -->
          <div class="camera-panel">
            <FaceAnalysis
              ref="faceAnalysisRef"
              :interviewId="props.currentInterviewId"
              :analysisEnabled="true"
              @interviewStart="handleFaceAnalysisStart"
              @interviewEnd="handleFaceAnalysisEnd"
              @analysisResult="handleFaceAnalysisResult"
            />
          </div>

          <!-- 中间：数字人 -->
          <div class="avatar-panel">
            <AIAvatar />
          </div>

          <!-- 右侧：对话信息 -->
          <div class="chat-panel">
            <div class="chat-messages" ref="chatMessagesRef">
              <transition-group name="message-slide" tag="div" class="messages-wrapper">
                <div
                  v-for="(message, index) in props.chatMessages"
                  :key="index"
                  :class="['message-item', message.type, { 'animate-in': true }]"
                  :style="{ animationDelay: (index * 0.05) + 's' }"
                >
                  <div v-if="message.type !== 'system'" class="message-avatar">
                    <div class="avatar-wrapper">
                      <img
                        v-if="message.type === 'ai'"
                        src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20wearing%20glasses%20and%20suits&image_size=square"
                        alt="AI面试官"
                        class="avatar-img"
                      >
                      <img
                        v-else
                        src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20frog%20avatar&image_size=square"
                        alt="用户"
                        class="avatar-img"
                      >
                      <div class="avatar-badge" v-if="message.type === 'ai'">
                        <i class="el-icon-connection"></i>
                      </div>
                    </div>
                  </div>

                  <div class="message-bubble">
                    <div v-if="message.type === 'system'" class="system-message">
                      <el-button
                        v-if="message.content === 'evaluate'"
                        type="success"
                        @click="evaluateInterview"
                        class="evaluate-btn"
                      >
                        <i class="el-icon-document"></i>
                        查看评估报告
                      </el-button>
                    </div>

                    <div v-else class="message-content">
                      <div class="message-text" :class="{ 'ai-message': message.type === 'ai', 'user-message': message.type === 'user' }">
                        <template v-if="message.type === 'ai' && speakingIndex === index">
                          <span class="typing-indicator">
                            <span></span><span></span><span></span>
                          </span>
                        </template>
                        <template v-else>
                          {{ message.content }}
                        </template>
                      </div>

                      <div class="message-footer">
                        <span class="message-time">{{ message.time }}</span>
                        <div class="footer-right">
                          <el-button
                            v-if="message.type === 'ai'"
                            @click="speakText(message.content)"
                            class="play-voice-btn"
                            :class="{ playing: speakingIndex === index }"
                          >
                            <i :class="speakingIndex === index ? 'el-icon-video-pause' : 'el-icon-video-play'"></i>
                            {{ speakingIndex === index ? '暂停' : '播放' }}
                          </el-button>
                          <span class="message-status" v-if="message.type === 'user'">
                            <i class="el-icon-check"></i>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </transition-group>

              <div v-if="isLoading" class="loading-indicator">
                <div class="loading-dots">
                  <span></span><span></span><span></span>
                </div>
                <span class="loading-text">AI面试官正在思考...</span>
              </div>
            </div>

            <div class="input-area">
              <el-input
                v-model="userInput"
                placeholder="输入您的回答..."
                @keyup.enter="sendMessage"
                type="textarea"
                :rows="2"
                :disabled="isLoading"
                class="chat-input"
              ></el-input>
              <el-button
                type="primary"
                @click="sendMessage"
                :disabled="!userInput.trim() || isLoading"
                class="send-btn"
              >
                <i v-if="isLoading" class="el-icon-loading"></i>
                <i v-else class="el-icon-s-promotion"></i>
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>'''

# 查找并替换原来的avatar-camera-mode部分
old_pattern = "      <!-- 数字人+面部分析模式 -->\n      <div v-else class=\"avatar-camera-mode\">\n        <div class=\"camera-wrapper\">\n          <FaceAnalysis\n            ref=\"faceAnalysisRef\"\n            :interviewId=\"props.currentInterviewId\"\n            :analysisEnabled=\"true\"\n            @interviewStart=\"handleFaceAnalysisStart\"\n            @interviewEnd=\"handleFaceAnalysisEnd\"\n            @analysisResult=\"handleFaceAnalysisResult\"\n          />\n        </div>\n        <AIAvatar />\n      </div>"

content = content.replace(old_pattern, new_layout)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("布局优化成功！")
