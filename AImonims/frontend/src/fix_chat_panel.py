#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复CSS样式
old_css = '''.chat-panel {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.chat-panel .chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-panel .input-area {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

.chat-panel .chat-input {
  flex: 1;
}

.chat-panel .send-btn {
  align-self: flex-end;
}'''

new_css = '''.chat-panel {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  height: 100%;
  min-height: 500px;
}

.chat-panel .chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;
}

.chat-panel .input-area {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
  flex-shrink: 0;
}

.chat-panel .chat-input {
  flex: 1;
  min-width: 0;
}

.chat-panel .send-btn {
  flex-shrink: 0;
}'''

content = content.replace(old_css, new_css)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("CSS样式修复成功！")
