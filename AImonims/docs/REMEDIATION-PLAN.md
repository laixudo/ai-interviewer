# AI 模拟面试平台 — 修复计划书

版本 v2（经 5 轮审计）· 2026-09-10 · 范围 P0（安全）+ P1（功能 Bug）· 39 项任务

## 0. 前置决策（已确认）

| 项 | 决定 |
|---|---|
| Git 安全网 | 先建 `.gitignore`，再做初始提交作为基线；**不 push 任何远端** |
| 管理后台 | 保留 `admin-frontend/` 独立应用；删除 `frontend/src/views/Admin*.vue` + `AdminPage.vue` |
| 改造范围 | P0 + P1。**不含** App.vue 拆分、不含 vue-router 改造 |
| 项目定位 | 课程/毕业设计，本地演示为主 → 鉴权用「HMAC 签名 token + PBKDF2 密码哈希」，**全部走 Python 标准库，不引入新依赖** |

## 1. 技术选型说明

鉴权不引入 `pyjwt` / `passlib` / `bcrypt`，原因：
- 项目定位本地演示，`requirements.txt` 本身已经严重失配（缺 11 个包），此时再加依赖会放大安装难度；
- `hashlib.pbkdf2_hmac`（PBKDF2-HMAC-SHA256，26 万次迭代）与 `hmac.compare_digest` 均为标准库，强度足够且无安装成本；
- token 用 `base64url(payload) + "." + HMAC-SHA256` 自签，含 `exp`，语义等价于精简版 JWT。

密钥 `APP_SECRET_KEY` 从环境变量读取，缺失时**启动即报错**（不允许静默使用默认值）。

---

## 2. 任务清单

### Wave 0 — 安全网（必须先做，后续所有删除依赖它）

| ID | 任务 | 位置 | 验证 |
|---|---|---|---|
| W0-1 | 创建 `.gitignore`：排除 `.env`、`*.db`、`venv/`、`node_modules/`、`dist/`、`__pycache__/`、`debug_audio/`、`_archive/` | 仓库根 `D:\AImonims` | `git status --porcelain` 不再列出密钥与数据库 |
| W0-2 | `git add -A` + 初始提交建立基线 | — | `git log --oneline` 有 1 条；`git status` clean |
| W0-3 | 备份在用库 `backend/interview.db`（6.2 MB / 9 用户 / 242 面试）到 `docs/backup/interview.db.bak` 并排除出 git | — | 文件存在且 `PRAGMA integrity_check` 通过 |

> W0-1 必须早于 W0-2，否则密钥进入 git 历史；W0-2 必须早于 Wave 3 的所有删除。

### Wave 1 — P0 安全

| ID | 问题 | 位置 | 修复方案 | 验证 |
|---|---|---|---|---|
| S1 | 密码明文存储 | `backend/data/database.py:242,251` | `users` 表加 `password_hash`、`password_salt`、`role` 列（保留旧 `password` 列以便回滚，值清空）；新增 `_hash_password/_verify_password`；`add_user` 写哈希；`login_user` 走 `compare_digest`；一次性迁移把现有 9 条明文转哈希后清空明文列 | 迁移后查库：`password` 全为空、`password_hash` 长度 64；用原密码登录成功 |
| S2 | 登录不发凭证、权限靠用户名字符串 | `backend/main.py:2799-2814` | 新建 `backend/auth.py`：`create_token/verify_token/get_current_user/require_admin`；`/api/auth/login` 返回 `token`；role 改为读 `users.role` 列而非 `ADMIN_USERS` 集合 | 注册名为 `admin` 的新账号，其 role 必须为 `user` |
| S3 | 16 个 `/api/admin/*` 零鉴权 | `backend/admin_api.py` 全部路由 | 15 个路由加 `_=Depends(require_admin)`；另将 3 个写共享数据的端点一并纳管：`POST /api/exam/questions`(main.py:1651)、`POST /api/selected-questions/generate`(main.py:1825)、`DELETE /api/selected-questions/{id}`(main.py:1893)。**第 16 个见 S10，不可直接加 require_admin** | 无 token 请求全部返回 401；普通用户 token 返回 403 |
| S10 | **审计发现的方案冲突**：`GET /api/admin/user/{user_id}/ability-profile`(admin_api.py:629) 被普通用户页面 `PersonalAbilityProfile.vue:457` 调用（「个人能力画像」）。直接套 `require_admin` 会让所有普通用户的该页面失效；而它当前无鉴权也构成 IDOR（改 id 即可读他人画像） | `backend/admin_api.py:629`、`frontend/src/components/PersonalAbilityProfile.vue` | 拆成两个端点：① `GET /api/user/ability-profile` 从 token 取自己的 id，登录即可用；② 原 admin 端点保留并加 `require_admin`。前端该页面改调 ① | 普通用户可看自己的画像；改他人 id 无法越权；管理端仍可查任意用户 |
| S4 | 越权访问（IDOR） | B 组 9 个面试端点、C 组 22 个 user_id 端点 | ① 新增 `assert_interview_owner(interview_id, user)` 用于 9 个面试端点；② **审计修正**：C 组的 `user_id` 参数**保留在签名/模型里以维持线缆兼容**，但其值一律不采信，身份改由 `Depends(get_current_user)` 覆盖。已核实前端 17 处调用中 10 处走 query、7 处走 JSON body，且无任何 Pydantic 模型设 `extra="forbid"`——若删参数，query 那批被忽略无碍，body 那批也不会 422，但保留参数可让前端 **17 处调用点零改动**，风险更低。`/api/auth/*` 除外 | 用户 A 的 token 读用户 B 的 `interview_id` 返回 403；伪造 `user_id=其他人` 无效，只返回自己的数据 |
| S5 | 前端无凭证传递 | `frontend/src/main.js`、`admin-frontend/src/main.js` | 装一个全局 `window.fetch` 包装：对同源 `/api/` 请求自动注入 `Authorization: Bearer`，401 时清 localStorage 并跳登录。**76 处 `fetch()` 调用点零改动** | `npm run build` 通过；构建产物含拦截器代码 |
| S6 | 71 处 `return {"error": str(e)}` 外泄内部信息 | 4 个后端文件 | 新建 `backend/errors.py`：统一异常处理器返回 `{"detail":"服务器内部错误","trace_id":...}`，真实堆栈进日志；逐处替换 `str(e)` | grep 复核：业务代码中返回体不再含 `str(e)` |
| S7 | 密钥落盘 + 两份 .env 分叉 | `.env`、`backend/.env` | 根 `.env` 是 `backend/.env` 的严格子集（DOUBAO 三项值相同），删除根 `.env`；新增 `.env.example`；`load_dotenv` 改为显式绝对路径，不再依赖 cwd；输出密钥轮换清单 | 只剩一份 `.env`；`.env.example` 无真实值 |
| S8 | `/api/user/info` 返回 password 字段 | `backend/data/database.py:266` | `get_user_by_id` 改为显式列清单，排除 `password*` | 接口响应无 password 字段 |
| S9 | CORS 白名单缺 admin-frontend（仅 3000-3003，管理后台在 8080）；开发期靠 vite 代理绕过，独立部署即失败 | `backend/main.py:274-279` | 来源改由 `CORS_ORIGINS` 环境变量配置，默认含 8080；`allow_headers` 从 `*` 收敛为显式含 `Authorization` | 8080 来源的预检请求通过 |

> **密钥轮换需你本人操作**：`DOUBAO_API_KEY`、`DASHSCOPE_API_KEY`、`ALIBABA_CLOUD_ACCESS_KEY_ID/SECRET` 已明文落盘一段时间，我无法代你到火山引擎/阿里云控制台重置。计划只负责让新密钥不再泄露。

### Wave 2 — P1 功能 Bug（全部已在分析阶段实测复现）

| ID | 问题 | 位置 | 修复方案 | 验证 |
|---|---|---|---|---|
| B1 | `docker-compose up` 必崩：卷挂载用 19 方法的旧 `data/` 覆盖 46 方法的正确实现，24 个方法丢失 | `docker-compose.yml:14-17` | 删除 `./ai:/app/ai`、`./data:/app/data` 两行；`Dockerfile` 不再 COPY 根 `ai/`、`data/` | 静态核对：镜像内 `data.database.Database` 方法数 = 46 |
| B2 | 管理端用户搜索必报 `ProgrammingError`：拼了 2 个占位符没传参 | `backend/admin_api.py:101` | 补齐参数元组 | 带 keyword 搜索返回 `success: true` |
| B3 | 评估报告只存进程内 dict，重启后端点永远返回 `generating` | `backend/main.py:553-585,1050` | **审计修正**：不能复用 `evaluation_reports` 表——该表 `overall_score`/`overall_level` 为 NOT NULL，而 `evaluate_interview_and_recommend` 产出的是 `{strengths, weaknesses, recommendations}`，两种报告形状不兼容。改为新建 `conversation_reports(interview_id UNIQUE, status, payload TEXT, error, created_at)` 存后者；端点先查库再查缓存；进程内缓存换 `OrderedDict` 加上限防泄漏 | 重启进程后仍能取到已完成报告；两种报告互不覆盖 |
| B4 | AI 失败时返回硬编码假评分（`overall_score: 85`、固定「推荐《Java核心技术》」），且不分岗位 | `backend/main.py:249,567`；`frontend/src/App.vue:830` | 后端失败返回 `status:"failed"` + 原因，不再编造内容；前端初始 state 的假数据清空，报告区按 `status` 分别渲染「生成中/失败/成功」 | grep 复核无兜底假报告；前端无硬编码 85 分 |
| B5 | `delete_interview` 无 return，接口返回 `null` | `backend/main.py:1271` | 补 return，消除未用变量 | 返回 `{"success": true}` |
| B6 | `job_type` 被静默丢弃 + 3 处写死 `"java_backend"` | `backend/main.py:48,59,580` | `evaluate_interview_and_recommend` 增加 `job_type` 形参并透传；两处写死改为参数 | 非 Java 岗位面试的评估提示词含正确岗位 |
| B7 | 前端 3 处资源泄漏 | `AIAvatar.vue:254`（interval 无句柄）、`Live2DAvatar.vue:42`（无卸载钩子）、`PersonalAbilityProfile.vue:709,835`（resize 监听不移除、3 init 仅 1 dispose） | 保存句柄并在 `unmounted/onUnmounted` 清理；resize 处理函数具名化后 `removeEventListener`；补齐 echarts `dispose()` | 静态核对 setInterval/clearInterval、addEventListener/removeEventListener、init/dispose 计数配平 |
| B8 | `requirements.txt` 缺 11 个实际导入包、多 6 个无人使用包、零版本锁定 | `backend/requirements.txt` | 按真实 import 图重建并锁版本；重依赖（torch/whisper/vosk/cv2/librosa）拆到 `requirements-speech.txt` 标为可选 | 脚本复核：所有第三方 import 均可在清单中找到 |
| B9 | `@element-plus/icons-vue` 未声明（靠传递依赖侥幸可用）；`axios` 声明了但 76 处全用原生 fetch | `frontend/package.json`、`admin-frontend/package.json` | 补声明 icons-vue；移除未使用的 axios | `npm run build` 通过 |
| B10 | PDF 上传无类型/大小校验，异常时临时文件泄漏 | `backend/main.py:2412-2441` | 校验扩展名与 magic number、限制 10 MB、`try/finally` 保证 unlink | 超限返回 400；异常路径无残留临时文件 |
| B11 | 语法错误 `unexpected indent` | `backend/add_face_methods.py:22` | 该文件属一次性迁移脚本，随 C2 移入 `_archive/` 并修正缩进 | AST 全量检查 0 错误 |
| B12 | 43 个 `async` 端点内同步阻塞事件循环（`requests.post` timeout=60、whisper 推理），全库 0 处 `run_in_executor` | `backend/ai/doubao_client.py:63`；`backend/main.py` 各端点 | 所有 LLM/ASR 调用改 `await asyncio.to_thread(...)` | 静态核对：`async def` 端点内不再直接调用阻塞函数 |
| B13 | `ThreadPoolExecutor(max_workers=6)` 建了从不用；改用裸 `threading.Thread` 无上限无 join | `backend/main.py:42,549,580` | 删除未用 executor 与 `TimeoutError` 导入；后台任务改 FastAPI `BackgroundTasks` | grep 复核无裸 `threading.Thread(...).start()` |
| B14 | DB 路径相对 cwd，已产生 4 个 db 文件（3 个空库） | `backend/data/database.py:6` | 默认路径改为基于 `__file__` 的绝对路径，可用 `INTERVIEW_DB_PATH` 覆盖 | 从任意 cwd 启动都指向同一个库 |
| B15 | VOSK 路径写死 `D:\\\\AImonims\\...`（多写一层转义），且模型在项目目录之外 | `backend/ai/speech_recognizer.py:9` | 改为读 `VOSK_MODEL_PATH` 环境变量，默认相对项目根 `models/`；缺失时优雅降级 | 静态核对无盘符字面量 |
| B16 | `speech_recognizer.load_model()` 在 import 期执行，缺依赖则整个服务起不来 | `backend/main.py:37` | 改为首次使用时惰性加载，缺依赖只关闭语音功能 | 最小 venv（无 torch/whisper/vosk）下 `import main` 成功 |
| B17 | 43 处 `sqlite3.connect` 全部未设 `timeout`，也未开 WAL；B12 改多线程后并发写会 `database is locked` | `backend/data/database.py` 全文件 | 统一走一个 `_connect()`：`timeout=10` + `PRAGMA journal_mode=WAL` + `PRAGMA foreign_keys=ON` | 脚本复核：无裸 `sqlite3.connect`；查库 `journal_mode` = wal |
| B18 | 7 处用贪婪正则 `\{[\s\S]*\}` 从 LLM 回复里抠 JSON，遇到含花括号的散文即解析错位 | `backend/main.py:238,398,1112,1759,2208,2265,2330` | 抽公共 `extract_json()`：先剥 ```json 围栏，再做括号配平扫描，失败返回 None 由调用方走失败分支 | 单测覆盖围栏/前后散文/嵌套/非法 4 种输入 |
| B19 | `DoubaoClient.cache` 是无锁 dict，且做了「先判断再删除」的读改写序列；B12 落地后会被多线程并发访问 | `backend/ai/doubao_client.py:15,26-45` | 加 `threading.Lock` 保护三处缓存操作 | 静态核对缓存读写均在锁内 |
| B20 | **审计新发现的 Bug**：`admin_api.py` 有 **16 处** `sqlite3.connect('interview.db')` 硬编码相对路径，完全绕过 `Database` 类。后果：① B14 的绝对路径修复对管理后台无效，换 cwd 启动即连到空库；② B17 的 WAL/timeout 对管理端全部失效 | `backend/admin_api.py:14,76,130,194,216,324,380,402,428,449,507,529,555,576,608,634` | 全部改走注入的 `get_connection`（`register_admin_routes` 已接收 `app`，改为同时接收 `db`，与 `prep_center_api`/`favorites_api` 的既有写法对齐） | 脚本复核 `admin_api.py` 内 0 处裸 `sqlite3.connect` |

### Wave 3 — 清理与文档

| ID | 任务 | 内容 | 验证 |
|---|---|---|---|
| C1 | 删除死代码 | ① 根 `ai/`、`data/`（约 2100 行，被 `backend/` 副本遮蔽）；② `frontend/src/views/Admin*.vue` + `AdminPage.vue`（约 2200 行，无人 import）；③ 孤立组件 `LoginView.vue`、`TestApp.vue`、`AIRecommend.vue`；④ `main.py` 内 6 个从未被调用的函数（约 174 行，含整个失效的 `lru_cache` 层） | 删除后 import 图无断链；前端 build 通过；后端 import 成功 |
| C2 | 移出一次性脚本 | `backend/` 下 59 个 `.py` 里**有 54 个**是一次性脚本（33 个 `test_*`、7 个 `check_*`、4 个 `debug_*`、7 个 `add_*`、`fix_main.py`、`simple_fix.py`、`main_clean.py`、`network_test.py`、`run_port_8001.py`）；`frontend/src/` 下 14 个 `fix_*.py`/`add_*.py`（硬编码 `d:/AImonims/...`，`simple_fix.py` 会把 `main.py` 截断）→ 全部移入 `_archive/oneoff-scripts/` | `frontend/src/` 无 `.py`；`backend/` 仅剩 5 个真实模块 |
| T1 | 补自动化测试 | 现有 33 个 `test_*.py` 全是无断言的手工调试脚本。把 V3 冒烟流程固化为 `backend/tests/test_auth_and_access.py`（pytest + TestClient），覆盖注册/登录/401/403/归属校验/密码迁移后可登录，外加 B18 的 `extract_json` 单测 | `pytest` 全绿，且是可重复运行的真实断言 |
| C3 | 清理工作区垃圾 | `backend/venv/`（14 MB 空壳仅装 pip）、`frontend/dist/`（7 MB 过期构建）、6 个 `__pycache__/`、`backend/debug_audio/`（真人录音）、3 个 0 字节空 db、根 `package.json` + 根 `node_modules`（45 MB，根目录无源码） | 工作区体积显著下降；`git status` clean |
| C4 | README 重写 | 现 README 未提及已实现的 8 个主要功能（管理后台/数字人 Live2D/面部分析/简历解析/社区/收藏/语音识别），却宣称未实现的 RAG（`data/knowledge_base.py` 从未被引用）。按实际功能与真实启动步骤重写，补 admin-frontend :8080 | 逐条核对功能与代码一致 |
| C5 | 结构化日志 | 后端 81 处 `print()` → `logging`，统一格式与级别 | grep 复核核心模块无裸 print |

---

## 3. 明确不在本次范围

| 项 | 原因 |
|---|---|
| App.vue 拆分（5875 行 / 3952 行未 scoped 全局 CSS） | 你已选择 P0+P1。另核查到有 5 个类（`.avatar`/`.main-content`/`.message-avatar`/`.multiple`/`.single`）被子组件依赖，直接加 `scoped` 会破样式；正确做法是抽成独立全局样式文件，留待下一轮 |
| vue-router 改造（14 个页面状态 / 53 处引用） | 会改变 URL 结构与用户可见行为，你已选择本轮不做 |
| `_aigcpanel/lib.cp310-win_amd64.pyd`（939 KB 第三方 Windows 二进制，无人引用）、`package/`（4 MB Live2D 素材副本） | 属第三方产物，删除与否需你判断版权/后续用途；本轮仅在 README 中标注来源与用途 |
| 密钥轮换 | 需你登录云控制台操作 |
| 面试业务逻辑正确性（追问轮次、阶段流转的产品语义） | 需要产品预期作为判据，非本轮技术修复目标 |

---

## 4. 验证策略

因为**当前环境没有任何 Python 依赖**（`backend/venv/` 只装了 pip，系统 Python 也没有 fastapi），必须先建立可验证环境，否则「修好了」无法证明。

| ID | 手段 | 覆盖 |
|---|---|---|
| V1 | AST 全量语法检查（94 个 .py） | 语法零错误 |
| V2 | 建最小 venv：`fastapi uvicorn pydantic python-dotenv httpx`（约 15 MB，不装 torch/whisper）。B16 惰性化后 `import main` 应成功 | 服务可启动 |
| V3 | `TestClient` 端到端冒烟：注册 → 登录取 token → 无 token 访问 `/api/admin/users` 应 401 → 普通用户 token 应 403 → 用户 A 读用户 B 的 interview 应 403 → 读自己的应 200 → 用原密码登录成功（验证 S1 迁移） | S1/S2/S3/S4 真实行为 |
| V4 | `npm run build`（frontend 与 admin-frontend，node_modules 已就位） | S5/B7/B9/C1 前端改动 |
| V5 | 脚本化复核：`str(e)` 外泄数、裸 `threading.Thread` 数、盘符字面量数、setInterval/clear 配平、init/dispose 配平、import 与 requirements 对齐 | B7/B8/B12/B13/B15/S6 |
| V6 | 删除后 import 图复检 | C1/C2/C3 无断链 |
| V7 | 数据库迁移前后对比：用户数 9、面试数 242、消息数 1156 不变 | S1 无数据丢失 |

## 5. 执行顺序与依赖

```
W0-1 → W0-2 → W0-3            （安全网，必须最先）
        ↓
S1 → S2 → S3 → S4 → S5        （S2 依赖 S1 的 role 列；S3/S4 依赖 S2 的依赖注入；S5 依赖 S2 的 token 契约）
S7 → S2                        （S2 需要 APP_SECRET_KEY 就位）
S6, S8                         （独立）
        ↓
B16 → V2                       （必须先惰性化，才能在最小 venv 里 import）
B14 → V3                       （TestClient 需要确定的 db 路径）
B1..B15                        （其余相互独立）
        ↓
C1 → V6                        （删除后复检）
C2, C3, C4, C5
        ↓
V1..V7 全量回归
```

## 6. 回滚方式

- 代码：`git checkout .` 或 `git reset --hard <基线 commit>`
- 数据库：`docs/backup/interview.db.bak` 覆盖回 `backend/interview.db`
- 删除物：Wave 3 的删除均在基线提交之后，可 `git checkout <基线> -- <路径>` 取回

---

## 7. 审计记录

计划书经 5 轮审计，共修正 **2 处方案缺陷**、新增 **8 项漏掉的任务**、发现 **2 个原分析未捕获的 Bug**。

| 轮次 | 审计内容 | 结论 |
|---|---|---|
| 第 1 轮 | 覆盖度追溯：分析阶段 37 项发现逐一映射到任务 | 初版覆盖 31/37。**6 项缺口**（全部经代码验证真实存在）补为 S9、B17、B18、B19、T1，并扩充 C2 |
| 第 2 轮 | 位置准确性：计划书引用的 32 处 `文件:行号` 回代码核对 | 30 处准确，**2 处偏差**已修正（`database.py:236→242`、`App.vue:824→830`） |
| 第 3 轮 | 技术可行性与任务冲突 | 抓出 **2 处方案缺陷 + 1 个新 Bug**，见下表 |
| 第 4 轮 | 剩余前置假设 | 5 项假设全部证实，并据此把 S4 改为更低风险的做法 |
| 第 5 轮 | 验证环境可行性 | 最小 venv 建成，8 项漏洞全部实测复现，验证策略成立 |

### 第 3 轮抓出的问题

| 类型 | 内容 | 处置 |
|---|---|---|
| 方案缺陷 | S3 原计划给全部 `/api/admin/*` 套 `require_admin`，但 `/api/admin/user/{id}/ability-profile` 被普通用户页面 `PersonalAbilityProfile.vue` 调用，会打断正常功能 | 拆为 S10：新增 `/api/user/ability-profile`（自己，取 token）+ 原端点保留并限管理员 |
| 方案缺陷 | B3 原计划复用 `evaluation_reports` 表，但该表 `overall_score`/`overall_level` 为 NOT NULL，而待存报告是 `{strengths, weaknesses, recommendations}`，形状不兼容 | 改为新建 `conversation_reports` 表 |
| **新 Bug** | `admin_api.py` 有 16 处 `sqlite3.connect('interview.db')` 硬编码相对路径，绕过 `Database` 类 → B14 的路径修复与 B17 的 WAL/timeout 对管理后台完全无效 | 新增 B20 |

### 第 5 轮：实测基线（未修复代码，`fastapi.TestClient` + 库副本）

| # | 用例 | 实测结果 | 对应任务 |
|---|---|---|---|
| 1 | 无凭证 `GET /api/admin/users` | **HTTP 200，返回真实用户列表** | S3 |
| 2 | `GET /api/admin/users?keyword=a` | HTTP 200 但 `success=false`，`Incorrect number of bindings supplied` | B2 |
| 3 | 无凭证 `GET /api/interview/detail?interview_id=1` | **HTTP 200，读到他人面试全文** | S4 |
| 4 | `POST /api/user/info?user_id=1` | **响应体含 `password` 字段** | S8 |
| 5 | 无凭证读他人能力画像 | **HTTP 200** | S10 |
| 6 | 已结束面试(id=244)的评估报告 | `status="generating"`，进程重启后永久卡死 | B3 |
| 7 | `DELETE /api/interview/delete` 成功分支 | 返回字面量 `null` | B5 |
| 8 | 用户 A 读 user_id=10 的面试 | **HTTP 200，拿到 16 条对话** | S4 |

> 另经实测确认：`sys.path` 顺序决定加载哪份 `ai/`、`data/`。按 `python main.py` 启动时 `backend/` 副本生效；但把项目根置前时会加载根目录旧副本（其 `ai/doubao_client.py` 依赖 `openai`，与 backend 版实现完全不同）。说明根目录副本不只是死重量，而是随 import 顺序变化的活地雷 —— C1 的删除优先级相应上调。

### 验证环境

`backend/.venv`（新建，替代只装了 pip 的 14 MB 空壳 `backend/venv/`）：fastapi 0.141.1、pydantic 2.13.5、pytest 9.1.1、httpx、python-dotenv、python-multipart、requests、numpy、librosa、imageio-ffmpeg、pydub。未装 torch/whisper/vosk/cv2/pdfplumber —— 这几个本来就是函数内惰性导入，不阻塞 `import main`。

## 8. 审计结论

计划书 v2 覆盖分析阶段全部 37 项发现：**33 项修复**（W0×3、S×10、B×20、C×5、T×1，含审计新增 9 项），**4 项明确排除**并说明原因（App.vue 拆分、vue-router、第三方素材去留、密钥轮换）。
每项均有可执行的验证判据，验证环境已建成并跑通基线。可以执行。
