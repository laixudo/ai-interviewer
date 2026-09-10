#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/App.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 固定的面试开场白
opening_speech = "你好！我是AI面试官，今天将对你进行Java工程师岗位的AI交流对话面试，时长为10分钟。本次面试主要考察你的技能匹配度和表达能力。请先做一个详细的自我介绍，包括个人基本信息、技能掌握情况和相关学习/项目经历（重点提炼1个核心亮点）。"

# 替换为固定开场白
old_opening = '''        // 添加面试开场白到对话
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

new_opening = f'''        // 添加固定的面试开场白到对话
        this.chatMessages.push({{
          type: 'ai',
          content: '{opening_speech}',
          time: new Date().toLocaleTimeString()
        }})
        // 触发数字人朗读开场白
        this.$nextTick(() => {{
          if (this.$refs.aiInterviewChat) {{
            this.$refs.aiInterviewChat.triggerAiSpeak('{opening_speech}')
          }}
        }})'''

content = content.replace(old_opening, new_opening)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed opening speech!')
