# AI模拟面试与能力提升软件

基于豆包Doubao-Seed-2.0-pro大模型的AI模拟面试与能力提升平台。

## 功能特性

### 1. 岗位化题库与知识库构建
- 支持Java后端、Web前端、Python算法三种计算机专业岗位
- 包含技术知识、项目经历深挖、场景题、行为题等多种题型
- 建立了完善的岗位核心技术栈知识库
- 支持RAG（检索增强生成）

### 2. 多模态交互式模拟面试界面
- 支持语音和文字两种输入方式
- AI面试官具备多轮对话能力
- 智能追问，根据关键词深入挖掘
- 专业的面试节奏控制

### 3. 面试表现多维度分析模块
- **内容分析**：技术正确性、知识深度、逻辑严谨性、岗位匹配度
- **表达分析**：语速、清晰度、自信度评估
- **综合报告**：结构化评估报告，包含得分、亮点、不足和改进建议

### 4. 能力提升反馈
- 个性化提升建议和练习计划
- 面试历史记录
- 能力成长曲线可视化

## 技术栈

- **后端**：FastAPI + Python
- **前端**：Vue 3 + Element Plus + Vite
- **大模型**：豆包Doubao-Seed-2.0-pro
- **数据库**：SQLite
- **部署**：Docker + Docker Compose

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- Docker (可选，用于容器化部署)
- 豆包API_KEY

### 1. 配置环境

```bash
# 复制并编辑环境变量配置
cp .env.example .env
# 编辑 .env 文件，填入你的豆包API_KEY
```

.env文件内容：
```
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_MODEL=Doubao-Seed-2.0-pro
DOUBAO_API_BASE=https://ark.cn-beijing.volces.com/api/v3
```

### 2. 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端服务将在 http://localhost:8000 启动

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 4. Docker部署 (可选)

```bash
docker-compose up -d
```

## 项目结构

```
AImonims/
├── backend/              # 后端服务
│   ├── main.py          # 主入口文件
│   ├── requirements.txt # Python依赖
│   ├── ai/              # AI模块
│   ├── data/            # 数据模块
│   └── interview.db     # SQLite数据库
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── App.vue      # 主组件
│   │   └── main.js      # 入口文件
│   ├── package.json
│   └── vite.config.js
├── ai/                  # AI模块（共享）
│   ├── doubao_client.py # 豆包API客户端
│   ├── evaluator.py     # 评估模块
│   └── improver.py      # 提升建议模块
├── data/                # 数据模块（共享）
│   ├── database.py      # 数据库操作
│   └── job_knowledge_base.py # 岗位知识库
├── docker/              # Docker相关
├── docker-compose.yml   # Docker Compose配置
└── .env                 # 环境变量配置
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

## 使用说明

### 1. 用户注册/登录
- 访问首页，点击"我的"进行注册或登录

### 2. 开始面试
- 点击"模拟面试"
- 选择面试岗位（Java后端、Web前端、Python算法）
- 选择工作经验阶段
- 选择面试官角色
- 点击"开始面试"

### 3. 面试过程
- AI面试官会提问
- 通过文字或语音输入回答
- AI会根据回答进行追问
- 完成面试后查看评估报告

### 4. 查看报告
- 综合得分和等级
- 各维度详细评估
- 亮点分析
- 改进建议
- 能力提升计划

## 岗位类型

### 1. Java后端开发工程师
- 核心技术栈：Java SE、Spring Boot、Spring Cloud、MySQL、Redis、微服务架构
- 重点考察：多线程、JVM、Spring框架、数据库优化

### 2. Web前端开发工程师
- 核心技术栈：HTML5、CSS3、JavaScript、React/Vue、TypeScript、Webpack
- 重点考察：前端框架、性能优化、响应式设计、前端安全

### 3. Python算法工程师
- 核心技术栈：Python基础、NumPy/Pandas、Scikit-learn、TensorFlow/PyTorch
- 重点考察：算法设计、数据结构、机器学习、深度学习

## 开发说明

### 添加新岗位
1. 在 `data/job_knowledge_base.py` 中添加岗位定义
2. 添加该岗位的题库
3. 添加核心技术栈
4. 在前端添加岗位选项

### 自定义评估标准
1. 修改 `ai/evaluator.py` 中的评估逻辑
2. 或通过豆包API的提示词进行调整

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。
