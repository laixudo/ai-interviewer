#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义新的CSS样式
new_css = '''

/* 一体化布局样式 */
.unified-interview-layout {
  display: grid;
  grid-template-columns: 300px 1fr 400px;
  gap: 20px;
  height: calc(100vh - 200px);
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.camera-panel {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.camera-panel :deep(.camera-section) {
  height: 100%;
  padding: 16px;
}

.camera-panel :deep(.camera-container) {
  width: 100%;
  height: 280px;
  margin-bottom: 16px;
}

.camera-panel :deep(.analysis-panel) {
  width: 100%;
  padding: 12px;
}

.avatar-panel {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.avatar-panel :deep(.ai-avatar-container) {
  height: 100%;
}

.avatar-panel :deep(.avatar-main) {
  height: calc(100% - 80px);
}

.chat-panel {
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
}

/* 响应式布局 */
@media (max-width: 1400px) {
  .unified-interview-layout {
    grid-template-columns: 280px 1fr 350px;
  }
}

@media (max-width: 1200px) {
  .unified-interview-layout {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
  }

  .camera-panel {
    grid-column: 1;
    grid-row: 1;
  }

  .avatar-panel {
    grid-column: 2;
    grid-row: 1;
  }

  .chat-panel {
    grid-column: 1 / -1;
    grid-row: 2;
    max-height: 400px;
  }
}
'''

# 查找</style>标签并在其前插入CSS
style_end = '</style>'
content = content.replace(style_end, new_css + '\n' + style_end)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("CSS样式添加成功！")
