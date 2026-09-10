#!/usr/bin/env python3
# -*- coding: utf-8 -*-

file_path = 'd:/AImonims/AImonims/frontend/src/components/AIInterviewChat.vue'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 完全重写CSS样式
old_css_start = '''

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

new_css = '''

/* 一体化布局样式 */
.unified-interview-layout {
  display: grid;
  grid-template-columns: 320px 1fr 420px;
  gap: 24px;
  height: calc(100vh - 180px);
  min-height: 600px;
  padding: 20px;
  background: #f0f2f5;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.camera-panel {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.camera-panel :deep(.camera-section) {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  gap: 12px;
}

.camera-panel :deep(.camera-container) {
  width: 100%;
  flex: 0 0 auto;
  height: 260px;
  border-radius: 8px;
  overflow: hidden;
}

.camera-panel :deep(.analysis-panel) {
  width: 100%;
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.avatar-panel {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.avatar-panel :deep(.ai-avatar-container) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.avatar-panel :deep(.avatar-header) {
  flex-shrink: 0;
}

.avatar-panel :deep(.avatar-main) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.chat-panel {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-panel .chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 0;
}

.chat-panel .input-area {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e8e8e8;
  background: #fafafa;
  flex-shrink: 0;
}

.chat-panel .chat-input {
  flex: 1;
  min-width: 0;
}

.chat-panel .send-btn {
  flex-shrink: 0;
  align-self: flex-end;
  padding: 12px 28px;
}

/* 响应式布局 */
@media (max-width: 1600px) {
  .unified-interview-layout {
    grid-template-columns: 300px 1fr 380px;
    gap: 20px;
    padding: 16px;
  }
}

@media (max-width: 1400px) {
  .unified-interview-layout {
    grid-template-columns: 280px 1fr 350px;
  }
}

@media (max-width: 1200px) {
  .unified-interview-layout {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto 1fr;
    height: auto;
    min-height: calc(100vh - 180px);
  }

  .camera-panel {
    grid-column: 1;
    grid-row: 1;
    max-height: 500px;
  }

  .avatar-panel {
    grid-column: 2;
    grid-row: 1;
    max-height: 500px;
  }

  .chat-panel {
    grid-column: 1 / -1;
    grid-row: 2;
    max-height: 500px;
  }
}

@media (max-width: 900px) {
  .unified-interview-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
  }

  .camera-panel,
  .avatar-panel,
  .chat-panel {
    grid-column: 1;
  }

  .camera-panel {
    grid-row: 1;
    max-height: 450px;
  }

  .avatar-panel {
    grid-row: 2;
    max-height: 450px;
  }

  .chat-panel {
    grid-row: 3;
    max-height: 450px;
  }
}
'''

content = content.replace(old_css_start, new_css)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("布局优化完成！")
