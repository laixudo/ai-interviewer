# AI 模拟面试与能力提升平台

基于豆包 Doubao-Seed-2.0-pro 的 AI 模拟面试系统。用户端负责面试与复盘，管理端负责用户、面试记录与题库的运营。

- 后端：FastAPI + SQLite，89 个接口
- 用户端：Vue 3 + Element Plus + Vite，16 个页面组件（端口 3000）
- 管理端：独立 Vue 3 应用，5 个页面组件（端口 8080）

## 功能

### 面试主流程
- **面试配置**：岗位（Java 后端 / Web 前端 / Python 算法）、经验阶段、面试官角色、压力等级、时长（5/10/20/30 分钟）
- **分阶段面试**：自我介绍 → 技术提问 → 反问环节，各阶段题目数量按时长自动分配
- **智能追问**：根据回答内容决定是否追问，每题追问次数有上限
- **多模态输入**：文字输入，或语音作答（Whisper / Vosk 本地识别）
- **数字人面试官**：Live2D 形象 + 语音合成（阿里云百炼 CosyVoice）

### 复盘与提升
- **评估报告**：技术正确性、知识深度、逻辑严谨性、岗位匹配度
- **能力提升计划**：短板分析、改进建议、学习资源、30 天计划
- **个人能力画像**：雷达图 + 成长趋势曲线（ECharts）
- **简历分析**：PDF 解析、信息提取、质量评分，并据此生成针对性面试题
- **面部表情分析**：面试过程中的情绪、专注度、自信度评估

### 辅助模块
- **题库**：选择题与问答题，支持分类检索与收藏
- **备战中心**：面试技巧、简历管理、投递记录
- **社区**：经验帖、评论、点赞

### 管理端（:8080）
用户管理、面试记录管理、笔试题管理、精选题管理、数据看板。全部接口需要管理员令牌。

> 说明：仓库中的 `data/knowledge_base.py`（Chroma 向量库）曾用于 RAG 实验，但从未被后端引用，已在清理中移除。当前岗位知识库是 `AImonims/backend/data/job_knowledge_base.py` 里的静态字典，**不是 RAG**。

## 快速开始

### 前置要求
- Python 3.10+
- Node.js 16+
- 豆包 API Key（[火山方舟](https://www.volcengine.com/product/ark)）

### 1. 配置

```bash
cp AImonims/backend/.env.example AImonims/backend/.env
```

编辑 `AImonims/backend/.env`，至少填两项：

| 变量 | 说明 |
|---|---|
| `DOUBAO_API_KEY` | 豆包 API 密钥 |
| `APP_SECRET_KEY` | 会话令牌签名密钥，**必填**，缺失或短于 32 字符则服务启动即报错 |

生成签名密钥：

```bash
python -c "import secrets;print(secrets.token_hex(32))"
```

其余变量（阿里云语音、CORS 来源、数据库路径、Vosk 模型路径）见 `.env.example` 内注释。

### 2. 后端

```bash
cd AImonims/backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt && .venv/Scripts/python main.py
```

服务启动在 http://localhost:8000 ，接口文档 http://localhost:8000/docs 。

语音识别与面部分析属可选功能，需要额外安装（体积较大，含 torch）：

```bash
pip install -r requirements-speech.txt
```

不装也能正常启动，只是语音相关接口会返回明确的「组件未安装」提示。

### 3. 用户端

```bash
cd AImonims/frontend && npm install && npm run dev
```

http://localhost:3000

### 4. 管理端

```bash
cd AImonims/admin-frontend && npm install && npm run dev
```

http://localhost:8080 。需要用 `role = admin` 的账号登录；角色只能直接改数据库 `users.role` 字段授予，注册接口不接受角色参数。

### 5. Docker（可选）

```bash
docker compose up -d
```

`.env` 中的 `DOUBAO_API_KEY` 与 `APP_SECRET_KEY` 会透传进容器，数据库存在名为 `backend_data` 的具名卷里。

## 测试

```bash
cd AImonims/backend && .venv/Scripts/python -m pytest
```

34 条用例，覆盖密码哈希、令牌鉴权、管理端权限、越权访问、错误响应不外泄，以及模型回复的 JSON 解析。测试跑在临时库副本上，不会碰 `AImonims/backend/interview.db`。

## 项目结构

项目代码位于仓库的 `AImonims/` 子目录下（沿用了原始的本地目录布局），仓库根只有本文件与 `.gitignore`。

```
ai-interviewer/
├── README.md                        # 本文件
├── .gitignore
├── models/                          # Vosk 中文模型，需自行下载（不入库，约 49 MB）
└── AImonims/
    ├── backend/
    │   ├── main.py                  # 主入口，面试主流程与大部分接口
    │   ├── auth.py                  # 令牌签发/校验、权限依赖、归属校验
    │   ├── errors.py                # 统一异常处理（对外只给 trace_id）
    │   ├── llm_utils.py             # 模型回复的 JSON 解析
    │   ├── admin_api.py             # 管理端接口（全部要求管理员）
    │   ├── prep_center_api.py       # 备战中心、简历、社区
    │   ├── favorites_api.py         # 收藏
    │   ├── ai/                      # 豆包客户端、评估、语音识别、语速分析
    │   ├── data/                    # 数据库访问与岗位知识库
    │   ├── tests/                   # 34 条 pytest 用例
    │   ├── requirements.txt         # 核心依赖
    │   ├── requirements-speech.txt  # 可选的语音/视觉依赖
    │   └── .env.example             # 配置模板（.env 本身不入库）
    ├── frontend/                    # 用户端（:3000）
    │   ├── src/http.js              # fetch 拦截器，自动附带令牌
    │   ├── src/App.vue              # 主壳与页面切换
    │   └── src/components/          # 16 个页面组件
    ├── admin-frontend/              # 管理端（:8080）
    ├── docker/                      # 后端镜像
    ├── docker-compose.yml
    ├── docs/
    │   ├── REMEDIATION-PLAN.md      # 安全与 Bug 修复计划书（含 5 轮审计记录）
    │   └── backup/                  # 数据库备份（不入库）
    ├── package/                     # Live2D 模型素材
    └── _aigcpanel/                  # 第三方组件（当前未被引用）
```

## 安全说明

- 密码用 PBKDF2-HMAC-SHA256（26 万次迭代）加盐存储，不保留明文
- 登录下发 HMAC 签名令牌（含有效期），前端由 `http.js` 自动附加到 `/api/` 请求
- 管理端接口一律要求管理员令牌；面试类接口校验资源归属
- 异常只回传 `trace_id`，真实堆栈进日志
- `.env` 与 `*.db` 已在仓库根的 `.gitignore` 中排除

**若你从旧版本升级**：旧版 `.env` 中的密钥曾以明文长期存在于工作区，且数据库中存有明文密码。请到火山引擎/阿里云控制台轮换 `DOUBAO_API_KEY`、`DASHSCOPE_API_KEY`、`ALIBABA_CLOUD_ACCESS_KEY_ID/SECRET`。首次启动新版后端时，数据库里的明文密码会自动迁移为哈希，用户的原密码仍然可用。

## 已知限制

- `AImonims/frontend/src/App.vue` 仍是 5800 余行的单文件，其中约 3900 行是未加 `scoped` 的全局样式
- 页面切换用组件内 `currentPage` 字符串，没有引入 vue-router，因此不支持浏览器前进/后退、刷新保持与深链接
- 上述两项与面试业务逻辑本身的产品语义，均不在本轮修复范围内，见 [docs/REMEDIATION-PLAN.md](AImonims/docs/REMEDIATION-PLAN.md) 第 3 节

## 许可证

MIT License
