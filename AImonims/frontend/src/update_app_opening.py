#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/App.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改startAIInterview函数，添加开场白到对话
old_start = '''        const startData = await startResponse.json()
        this.currentInterviewId = startData.interview_id

        // 清空消息和问题列表
        this.chatMessages = []
        this.userInput = ''
        this.interviewQuestions = []
        this.currentQuestionIndex = 0'''

new_start = '''        const startData = await startResponse.json()
        this.currentInterviewId = startData.interview_id

        // 清空消息和问题列表
        this.chatMessages = []
        this.userInput = ''
        this.interviewQuestions = []
        this.currentQuestionIndex = 0

        // 添加面试开场白到对话
        if (startData.initial_question) {
          this.chatMessages.push({
            type: 'ai',
            content: startData.initial_question,
            time: new Date().toLocaleTimeString()
          })
          // 触发数字人朗读开场白
          this.$nextTick(() => {
            if (this.$refs.aiInterviewChat) {
              this.$refs.aiInterviewChat.triggerAiSpeak(startData.initial_question)
            }
          })
        }'''

content = content.replace(old_start, new_start)

# 2. 修改AIInterviewChat组件，添加triggerAiSpeak方法
old_chat_component = '''    <AIInterviewChat
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
    />'''

new_chat_component = '''    <AIInterviewChat
      ref="aiInterviewChat"
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
    />'''

content = content.replace(old_chat_component, new_chat_component)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('App.vue updated with opening speech!')
