# EduMind 项目问题审计与待办清单

## 1. 审计结论摘要

- 当前项目已经具备 Web 学生端、教师端、管理员端、小程序学生端和 FastAPI 后端的基础目录与页面雏形，但本轮静态审计发现后端入口存在 P0 级合并问题：`backend/app/main.py` 使用多个 router 名称却没有导入对应模块，按当前代码形态存在后端启动失败风险。
- 基础三端路由和菜单基本完整，新增页面 `/student/knowledge-graph`、`/student/smart-quiz`、`/teacher/ai-workbench`、`/admin/content-review`、`/admin/platform-quality` 已有路由和页面，但多个页面仍依赖集中 mock 或本地 fallback 数据。
- 业务演示闭环已经有雏形：画像、学习路径、RAG 问答、资源生成、测验、报告、教师分析、管理员统计均有页面或接口，但“真实数据回流、画像动态更新、内容审核持久化、多智能体真实执行证据”仍不足。
- 当前最大短板是运行稳定性和“赛题 A3 说服力”：真实大模型默认未启用，个性化主要是规则或 mock，多智能体虽然有 LangGraph 代码，但展示层仍混有 demo/fallback 模板说明。
- 比赛前最优先修复：后端 `main.py` router 导入、`agent_workflow.py` 未定义变量、微信小程序 tutor 页缺失导出数据、演示报告过期，以及重新跑 `check-demo-ready` / `e2e_demo_flow_check`。
- 左侧菜单不再直接展示三端切换器，但顶部用户下拉仍提供“切换身份”，如果答辩话术强调“进入角色后不可跨端切换”，需要同步调整或解释为 demo 快捷入口。
- 小程序已注册 6 个页面，能形成轻量学生端演示线，但默认 `127.0.0.1:8000` 只适合开发者工具/本机演示，真机和正式上线需要 HTTPS 合法域名。
- 文档较完整，但部分文档与当前代码不一致：README 和提交文档仍写“不引入 LangGraph/Chroma/向量数据库”，而当前依赖和代码已经包含 `langgraph`、`chromadb`、`backend/app/rag/vector_store.py`。
- 现有 `docs/reports/demo_ready_check.md` 声称 2026-06-04 已 READY、后端 app 可加载、前端构建通过；但当前静态检查发现 P0 风险，比赛前必须重新生成验收报告，不能继续引用旧结论。

## 2. 问题优先级总表

| 编号 | 优先级 | 模块 | 问题描述 | 当前状态 | 影响 | 建议处理方式 |
| --- | --- | --- | --- | --- | --- | --- |
| P0-01 | P0 | 后端 | `backend/app/main.py` 未导入 `courses`、`knowledge_base`、`rag` 等 router 模块，却直接 `include_router` | 静态确认 | 后端可能无法启动，所有 API、Swagger、前端联动失效 | 补齐 `from app.api.routers import ...` 或显式导入每个 router，之后运行导入/健康检查 |
| P0-02 | P0 | 后端 | `backend/app/api/routers/agent_workflow.py` 的 `run_full_learning_flow` 引用未定义变量 `seed` | 静态确认 | 点击完整 Agent 流程可能 500，影响多智能体演示 | 移除该段错误事件记录或改为使用 `run` / `payload` 字段 |
| P0-03 | P0 | 小程序 | `miniprogram/pages/tutor/index.js` 引用 `tutorMessages`、`ragTutorFallback`，但 `demoData.js` 未导出 | 静态确认 | 小程序 AI 辅导页可能报错或显示 undefined | 补齐 demoData 导出，或在 tutor 页增加默认值 |
| P0-04 | P0 | 演示 | `docs/reports/demo_ready_check.md` 声称 READY，但当前代码已有新风险 | 静态确认 | 答辩引用旧报告可能被现场运行推翻 | 修复 P0 后重新运行并覆盖验收报告 |
| P0-05 | P0 | 后端 | `main.py` 中新增 `user_profile_ws.router` 也未导入；WebSocket 不进 OpenAPI | 静态确认 | 合并新增接口未真正可用或不可发现 | 跟随 router 导入一起修复，并补 WebSocket 使用说明 |
| P1-01 | P1 | 后端 | `content_review_service.py` 使用进程内 `REVIEW_RECORDS`，审核记录重启丢失 | 静态确认 | 内容审核不能形成真实治理闭环 | 持久化到 SQLite/SystemLog 或新增 Review 表 |
| P1-02 | P1 | 前端 | `AdminContentReview.vue` 的“通过/驳回/待审”只改本地状态，不调用后端审批接口 | 静态确认 | 管理员审核是页面模拟，不是真闭环 | 增加 approve/reject API 或接入 `/api/v1/events/admin-review` |
| P1-03 | P1 | 前端 | 顶部用户下拉仍可“切换身份” | 静态确认 | 角色边界和答辩说法不一致 | 比赛版保留则明确为 demo 快捷入口；正式版应移除 |
| P1-04 | P1 | 前端 | `UserProfileChart.vue` 未被引用，且内容是消费趋势/标签英文数据 | 静态确认 | 新增 WebSocket 用户画像功能未接入教育场景 | 删除演示入口外的遗留组件，或改造成教育画像实时面板并挂菜单 |
| P1-05 | P1 | 小程序 | 小程序默认 `http://127.0.0.1:8000` | 静态确认 | 真机无法访问本机后端，正式上线不符合小程序域名要求 | 文档声明“开发者工具演示”，或增加配置页/局域网地址说明 |
| P1-06 | P1 | 前后端 | 多处 API 使用 `courseId/studentId` 字符串 demo id，主数据表使用整数 `course_id/profile_id` | 静态确认 | 数据联动难统一，报告和画像回流不稳定 | 建立字段映射表和统一 API 契约 |
| P1-07 | P1 | A3 对应度 | 大模型默认 mock，资源生成和画像多为规则生成 | 静态确认 | “基于大模型”说服力不足 | 演示时明确 mock 边界；最好接一条真实 LLM 可验证链路 |
| P1-08 | P1 | A3 对应度 | 多智能体页面展示与真实 LangGraph 执行混合，模板仍写“未接真实 LangGraph” | 静态确认 | 评委可能认为多智能体只是概念展示 | 修复完整工作流接口，统一文案，展示一次真实 run 记录 |
| P1-09 | P1 | 文档 | README/提交文档写“不引入 LangGraph/Chroma”，与代码和依赖不一致 | 静态确认 | 技术说明互相矛盾 | 更新文档为“LangGraph/Chroma 已接入或可 fallback” |
| P1-10 | P1 | 演示脚本 | `start-dev.bat` 只检查 `frontend/node_modules`，不检查 Python 依赖和后端导入 | 静态确认 | 现场启动窗口打开后才暴露后端失败 | 增加启动前后端导入检查或运行 health 检查 |
| P2-01 | P2 | 前端 | 多个菜单入口是 `PlaceholderPage.vue` 占位 | 静态确认 | 项目完整度降低，但不会 404 | 比赛主线避开占位页，后续逐步补齐 |
| P2-02 | P2 | 前端 | 多个页面使用 fallbackRows、competitionData，本地 mock 与后端真实数据混合 | 静态确认 | 数据真实性和一致性不足 | 优先把主线页面接真实接口，保留 fallback 作为断网兜底 |
| P2-03 | P2 | 后端 | `llm_service.py` 捕获真实 LLM 异常后静默回退 mock | 静态确认 | 真实模型不可用时不易发现 | 在响应或日志中暴露 fallback reason |
| P2-04 | P2 | 工程 | 根目录、backend、frontend 下存在大量 `.log`、`.pid`、`dist`、`node_modules`、sqlite 运行时文件 | 静态确认，已被 `.gitignore` 覆盖 | 手工打包时容易误带 | 提交包按白名单整理 |
| P2-05 | P2 | 文档 | `docs/final-acceptance-report.md` 路由清单偏旧，缺少新增页面 | 静态确认 | 文档不能代表当前代码 | 重写最终验收报告 |
| P3-01 | P3 | 工程 | 缺少单元测试和前端自动化测试，仅有脚本级检查 | 静态确认 | 长期维护风险 | 后续补 pytest、vue-tsc、页面 smoke test |

## 3. 后端问题清单

### 3.1 `backend/app/main.py`

- 涉及文件：`backend/app/main.py`
- 问题描述：文件只导入了 `FastAPI`、`CORSMiddleware`、`settings`、`Base/engine`、`app.models.*` 和 `llm_service`，但第 30-48 行直接使用 `courses.router`、`knowledge_base.router`、`rag.router`、`content_review.router`、`user_profile_ws.router` 等名称。`backend/app/api/routers/__init__.py` 为空，`app.models.*` 不会导入 router。
- 风险等级：P0
- 可能影响：后端 `uvicorn app.main:app` 可能在导入阶段 `NameError`，导致 `/health`、`/docs`、全部业务 API 和前端请求不可用。
- 建议修复方式：显式加入 `from app.api.routers import courses, knowledge_base, rag, content_review, profiles, learning_paths, resources, profile_dialog, tutor, quizzes, reports, agent_workflow, system_settings, logs, events, demo_status, competition, dashboard, user_profile_ws`。
- 是否需要代码修改：是，比赛前必须改。

### 3.2 `backend/app/api/routers/user_profile_ws.py`

- 涉及文件：`backend/app/api/routers/user_profile_ws.py`、`frontend/src/components/UserProfileChart.vue`
- 问题描述：后端存在 `/ws/user-profile` WebSocket；`main.py` 也尝试注册，但未导入。前端 `UserProfileChart.vue` 没有被任何页面引用；组件内部仍是 `User Purchase Trend`、`purchase_trend`、`active_tags`、`developer/gamer` 等非教育画像字段。
- 风险等级：P1
- 可能影响：合并后新增 WebSocket 功能既没有教育业务语义，也没有进入实际页面，更不进入 Swagger/OpenAPI。WebSocket 本来也不会在 OpenAPI 中展示，需要单独文档。
- 建议修复方式：要么移除比赛主线之外的遗留 WebSocket，要么改成“学生画像实时更新/学习行为流”并接入学生画像页或管理员监控页。
- 是否需要代码修改：是。

### 3.3 `backend/app/api/routers/agent_workflow.py`

- 涉及文件：`backend/app/api/routers/agent_workflow.py`
- 问题描述：`run_full_learning_flow` 内第 363 行和第 369 行引用 `seed.workflow_name`、`seed.id`，但该函数没有定义 `seed`。`seed` 只属于后面的 `rerun(run_id)` 语义。
- 风险等级：P0
- 可能影响：`POST /api/v1/agent-workflow/run-full-learning-flow` 一旦调用就可能 500。该接口正对应多智能体完整闭环，比赛演示风险高。
- 建议修复方式：在 `run_full_learning_flow` 中用 `run.id`、`payload.learning_goal`、`course.title` 替代 `seed`，或先删掉这段错误的 `record_event`，保证主流程可执行。
- 是否需要代码修改：是。

### 3.4 Router 注册和 API 前缀一致性

- 涉及文件：`backend/app/main.py`、`frontend/src/views/*.vue`
- 问题描述：大多数后端路由设计为 `/api/v1/*`，但 `dashboard` 单独注册为 `/api/dashboard/*`。前端 `Dashboard.vue`、`TeacherHome.vue`、`StudentHome.vue` 使用 `/api/dashboard/summary`，当前是匹配的，但这是特殊例外，容易被后续统一前缀时误改。
- 风险等级：P2
- 可能影响：新开发者可能误以为所有接口都是 `/api/v1`，导致 dashboard 404。
- 建议修复方式：在 API 文档中明确 dashboard 例外，或新增 `/api/v1/dashboard/*` 兼容路由。
- 是否需要代码修改：可选。

### 3.5 competition / demo_status / reports / resources / rag / content-review / profile-dialog / generate-pack

- 涉及文件：`backend/app/api/routers/competition.py`、`demo_status.py`、`reports.py`、`resources.py`、`rag.py`、`content_review.py`、`profile_dialog.py`
- 问题描述：这些 router 文件本身存在，前端也有对应调用：例如 `/api/v1/knowledge-graph`、`/api/v1/quiz/chapter`、`/api/v1/admin/content-review`、`/api/v1/resources/generate-pack`、`/api/v1/rag/ask`。但是只要 `main.py` router 导入不修复，它们都不会进入 FastAPI app。
- 风险等级：P0
- 可能影响：新增接口无法访问，Swagger/OpenAPI 无法展示。
- 建议修复方式：先修 `main.py`，再打开 `/docs` 确认所有接口可见；注意 WebSocket 不会出现在 OpenAPI。
- 是否需要代码修改：是。

### 3.6 内容审核未持久化

- 涉及文件：`backend/app/services/content_review_service.py`、`backend/app/api/routers/content_review.py`
- 问题描述：审核记录保存在模块全局变量 `REVIEW_RECORDS`，服务重启即丢失。`/api/v1/content-review/check` 可产生审核结果，`/records` 可读，但不是数据库闭环。
- 风险等级：P1
- 可能影响：管理员端“内容审核中心”不能证明真实平台治理能力。
- 建议修复方式：短期写入 `SystemLog` metadata；中期新增 `ContentReviewRecord` 表，补 approve/reject/reason/status。
- 是否需要代码修改：是。

### 3.7 LLM 默认 mock 和异常静默 fallback

- 涉及文件：`backend/app/services/llm_service.py`
- 问题描述：默认 `LLM_PROVIDER=mock`；若配置 deepseek/qwen 但调用异常，`generate_json` 捕获所有异常并直接 `_mock`，没有把 fallback 原因返回给前端或日志。
- 风险等级：P2
- 可能影响：演示时看似在线模型可用，实际可能一直是 mock；答辩中容易被追问。
- 建议修复方式：响应中加入 `mode`、`provider`、`fallback_reason`，并写入日志。
- 是否需要代码修改：建议。

### 3.8 RAG 和向量库能力边界

- 涉及文件：`backend/app/rag/vector_store.py`、`backend/app/services/lightweight_rag_service.py`、`docs/course_kb/python_programming.json`
- 问题描述：存在 Chroma `PersistentClient` 和 fallback JSON；同时 `lightweight_rag_service.py` 使用固定 JSON 课程知识库做关键词规则排序。文档有些地方写“没有使用向量数据库”，但代码实际保留 Chroma。
- 风险等级：P1
- 可能影响：RAG 技术说明不一致，评委难判断真实实现。
- 建议修复方式：统一表述为“上传文档链路使用 Chroma/HashEmbedding 或 JSON fallback；比赛主线学生助手使用轻量课程 JSON RAG”。
- 是否需要代码修改：文档必须改；代码可后续优化。

### 3.9 SQLite / storage 路径风险

- 涉及文件：`backend/app/core/config.py`、`backend/app/db/session.py`
- 问题描述：默认 SQLite 位于 `./backend/storage/eduagent.sqlite3`，代码会自动创建父目录；根目录也存在 `storage/eduagent.sqlite3`，容易混淆旧库和新库。
- 风险等级：P2
- 可能影响：演示数据可能写入一个库，检查脚本或人工查看另一个库。
- 建议修复方式：文档只保留 `backend/storage/eduagent.sqlite3` 为当前默认；提交包不要带 sqlite 文件。
- 是否需要代码修改：否，文档和打包检查即可。

### 3.10 需要人工核查

- 是否实际能 `uvicorn app.main:app` 启动：本轮按用户要求未运行会改动缓存/服务状态的启动命令，结论来自静态检查。
- Swagger/OpenAPI 是否展示所有 HTTP router：必须在修复 `main.py` 后打开 `/docs` 核查。
- `python-docx` 报告导出在当前环境是否可用：依赖存在于 `requirements.txt`，但本轮未运行生成。
- MySQL 初始化脚本 `database/init_mysql.sql` 是否仍与 SQLAlchemy 模型一致：本轮未做深度比对。

## 4. 前端问题清单

### 4.1 路由完整性

- 涉及文件：`frontend/src/router/index.ts`
- 问题描述：学生端、教师端、管理员端路由整体完整，新增页面均已注册；不存在明显“菜单入口导致 404”的问题，因为未知路径会落到 `PlaceholderPage.vue`。
- 风险等级：已完成但仍需验证
- 可能影响：路由层不会直接 404，但占位页过多会影响项目完整度。
- 建议修复方式：比赛演示避开占位菜单；后续补齐业务页。
- 是否需要代码修改：P0 不需要。

### 4.2 菜单占位页较多

- 涉及文件：`frontend/src/config/roles.ts`、`frontend/src/router/index.ts`、`frontend/src/views/PlaceholderPage.vue`
- 问题描述：教师端 `班级学生管理`、`智能答疑管理`、`通知中心`、`教学日历 / 待办`，管理员端 `权限配置`、`通知公告管理`、`数据统计与导出` 均标注“占位”。
- 风险等级：P2
- 可能影响：评委点击非主线菜单会看到“演示占位”，影响完整度但不影响运行。
- 建议修复方式：至少在答辩前隐藏非主线占位入口，或把占位状态写入已知问题清单。
- 是否需要代码修改：建议。

### 4.3 角色边界仍有顶部切换

- 涉及文件：`frontend/src/components/AppSidebar.vue`、`frontend/src/components/AppHeader.vue`、`frontend/src/composables/useRole.ts`
- 问题描述：左侧菜单根据当前路径显示单一角色菜单，已不再直接切换三端；但 `AppHeader.vue` 第 287、307、310 行仍提供“切换身份”，`useRole.ts` 仍保存 `availableRoles`。
- 风险等级：P1
- 可能影响：如果答辩说“进入角色后不能跨端切换”，现场 UI 会打脸；如果说是 demo 快捷入口，则可接受。
- 建议修复方式：比赛版保留则改文案为“演示身份切换”；正式版移除顶部切换，必须返回登录页。
- 是否需要代码修改：取决于答辩策略。

### 4.4 API 路径与 fallback 混合

- 涉及文件：`frontend/src/views/StudentKnowledgeGraph.vue`、`StudentSmartQuiz.vue`、`TeacherAIWorkbench.vue`、`AdminContentReview.vue`、`AdminPlatformQuality.vue`
- 问题描述：新增比赛页面优先请求 `/api/v1/*` competition 接口，请求失败后使用本地 `competitionData.ts`。这提升演示稳定性，但真实数据闭环不足。
- 风险等级：P1
- 可能影响：后端不可用时页面仍显示正常，容易掩盖接口断裂；评委追问数据来源时说服力弱。
- 建议修复方式：页面显式标注数据来源，主线演示确保后端接口真实返回。
- 是否需要代码修改：建议。

### 4.5 WebSocket 用户画像组件未接入

- 涉及文件：`frontend/src/components/UserProfileChart.vue`
- 问题描述：组件未被引用；开发模式写死 `ws://localhost:8000/ws/user-profile`；页面文本和数据字段是英文消费画像，不是教育画像；含多处 `console.log`。
- 风险等级：P1
- 可能影响：合并新增 `user_profile_ws` 不能证明被使用，且会造成“用户画像”概念混乱。
- 建议修复方式：若保留，改为学习行为/掌握度实时图；改用环境变量；挂到管理员质量页或学生画像页。
- 是否需要代码修改：是。

### 4.6 TypeScript 和类型质量

- 涉及文件：`frontend/src/views/QuizEvaluate.vue`、`LearningPath.vue`、`StudentHome.vue`
- 问题描述：存在 `any[]`、`Record<string, any>` 等类型弱化。不是立即运行失败问题，但会降低类型保护。
- 风险等级：P3
- 可能影响：接口字段变动时不易发现。
- 建议修复方式：先为主线 API 建类型，不做大规模重构。
- 是否需要代码修改：后续优化。

### 4.7 UI 和交互完整性

- 涉及文件：`CourseManage.vue`、`LearningPath.vue`、`ReportCenter.vue`、`SystemSettings.vue`
- 问题描述：多个按钮提示“演示操作”“后续可接真实流程”“配置暂存”，说明页面交互未完全落库。
- 风险等级：P2
- 可能影响：评委深点功能会发现是 demo 操作。
- 建议修复方式：比赛主线只演示已闭环按钮；P1 修复管理员审核、教师任务布置、报告生成等关键操作。
- 是否需要代码修改：建议。

### 4.8 package.json / package-lock.json

- 涉及文件：`frontend/package.json`、`frontend/package-lock.json`
- 问题描述：两者开头依赖一致，未发现明显锁文件缺失；但项目目录存在 `frontend/node_modules` 和 `frontend/dist`，应避免提交。
- 风险等级：P2
- 可能影响：手工打包体积过大。
- 建议修复方式：按 `.gitignore` 和提交包白名单排除。
- 是否需要代码修改：否。

## 5. 小程序问题清单

### 5.1 页面注册

- 涉及文件：`miniprogram/app.json`
- 问题描述：已注册 `home/path/resources/tutor/quiz/report` 六个页面；tabBar 包含首页、路径、资源、辅导、报告，练习页通过跳转进入。
- 风险等级：已完成但仍需验证
- 可能影响：结构上能形成学生移动端闭环。
- 建议修复方式：用微信开发者工具逐页点一遍，特别是 tutor 页。
- 是否需要代码修改：P0 需要修 tutor 数据导出。

### 5.2 小程序 AI 辅导页缺少导出数据

- 涉及文件：`miniprogram/pages/tutor/index.js`、`miniprogram/utils/demoData.js`
- 问题描述：`tutor/index.js` 第 1 行引用 `tutorMessages`、`ragTutorFallback`，但 `demoData.js` 导出列表只有 `student/courses/weakPoints/todayTasks/learningPath/recommendedResources/generatedResourcePack/quizAnalysis/wrongQuestions/mastery/report`。
- 风险等级：P0
- 可能影响：辅导页初始化消息、后端失败兜底回答可能为 `undefined`，严重时 `ragTutorFallback.answer` 报错。
- 建议修复方式：在 `demoData.js` 补齐 `tutorMessages` 和 `ragTutorFallback`，或在页面中提供默认对象。
- 是否需要代码修改：是。

### 5.3 真机访问地址风险

- 涉及文件：`miniprogram/app.js`、`miniprogram/utils/request.js`
- 问题描述：默认后端地址为 `http://127.0.0.1:8000`。
- 风险等级：P1
- 可能影响：微信开发者工具可本机调试；真机中 `127.0.0.1` 指向手机自身，不能访问电脑后端；正式发布还需要 HTTPS 合法域名。
- 建议修复方式：比赛提交说明写清“小程序源码 + 微信开发者工具运行 + 录屏演示”；如需真机演示，改为局域网 IP 或内网穿透 HTTPS。
- 是否需要代码修改：可选，文档必须说明。

### 5.4 练习结果没有真实回流

- 涉及文件：`miniprogram/pages/quiz/index.js`
- 问题描述：练习页只展示本地 `quizAnalysis` 和 `wrongQuestions`，没有提交答题、评分、写入后端或同步 Web 报告。
- 风险等级：P1
- 可能影响：小程序端不能证明“智能练习 -> 错因分析 -> 画像更新 -> Web 同步”。
- 建议修复方式：短期接 `/api/v1/quiz/chapter`、`/api/v1/quiz/submit` 或 `/api/v1/events/demo-quiz`；失败时再 fallback。
- 是否需要代码修改：建议。

### 5.5 学习报告与 Web 数据不同步

- 涉及文件：`miniprogram/pages/report/index.js`
- 问题描述：报告页只读本地 `report/mastery/weakPoints`，不请求 `/api/v1/reports`。
- 风险等级：P1
- 可能影响：移动端报告不是 Web 报告中心的数据延伸。
- 建议修复方式：接 `/api/v1/reports` 或新增学生端报告摘要接口。
- 是否需要代码修改：建议。

### 5.6 小程序上线状态

- 涉及文件：`miniprogram/project.config.json`、`docs/miniprogram-guide.md`
- 问题描述：`appid` 为 `touristappid`，`urlCheck` 为 false，适合开发者工具体验。
- 风险等级：P2
- 可能影响：不适合直接作为正式上线小程序提交。
- 建议修复方式：比赛材料明确提交“小程序源码 + 微信开发者工具运行说明 + 录屏演示”，不要声称已上线。
- 是否需要代码修改：否。

## 6. 业务闭环缺口

| 环节 | 完成度 | 当前证据 | 缺口 | 修复建议 |
| --- | --- | --- | --- | --- |
| 课程知识库 | 部分完成 | `KnowledgeBase.vue`、`knowledge_base.py`、`docs/course_kb/python_programming.json`、Chroma/fallback | 示例资料较轻，上传知识库与学生 RAG JSON 并非完全同源 | 准备一门完整课程资料集，并统一 RAG 数据来源说明 |
| 学生画像 | 部分完成 | `profiles.py`、`profile_dialog.py`、`personalization_service.py` | 多为规则抽取和 demo student，画像更新不依赖练习历史 | 将测验结果和问答事件写回画像字段 |
| 学习路径 | 部分完成 | `learning_paths.py`、`StudentLearningPath.vue`、`LearningPath.vue` | 路径展示多于动态调整 | 练习后自动生成 `path_updated` 并更新下一任务 |
| AI 问答 | 部分完成 | `/api/v1/rag/ask`、`StudentAssistant.vue`、`TutorChat.vue` | RAG 以规则/JSON 为主，真实引用质量有限 | 主线用固定课程资料，展示引用来源和可信度；后续接真实 embedding |
| AI 资源生成 | 部分完成 | `/api/v1/resources/generate-pack` 生成 5 类资源 | 主要规则生成，个性化来源是 weakPoints 字符串 | 绑定学生画像、课程章节和知识库引用 |
| AI 题库生成 | 部分完成 | `/api/v1/quizzes/generate`、`/api/v1/quiz/chapter` | competition 章节题是集中 mock；真实题库生成和学生端练习分离 | 统一题库生成、章节题、提交评分接口 |
| 学生智能练习 | 部分完成 | `StudentSmartQuiz.vue` 可提交 `/api/v1/quiz/submit` | 提交结果不明显写入画像和报告 | 提交后写 `QuizSubmission`、`SystemLog`、更新画像薄弱点 |
| 自动评分与错因分析 | 部分完成 | `submit_quiz_answers`、`quizzes.py` analysis | 多为规则估计，错因标签未沉淀为长期学习数据 | 增加错因表或画像 JSON 字段 |
| 学生画像更新 | 未完成/概念有 | 有 `path_updated`、业务事件 | 缺少“练习后画像更新”的真实接口 | 增加 `profile_updated_by_quiz` 事件和画像更新逻辑 |
| 教师学情分析 | 部分完成 | `TeacherHome.vue`、`TeacherAnalysis.vue`、`quizzes/analysis` | 可视化较完整，但干预动作部分演示化 | 将任务布置和风险学生干预落库 |
| 管理员平台统计 | 部分完成 | `Dashboard.vue`、`AdminPlatformQuality.vue`、`logs.py` | 质量评价部分来自 competition mock | 用真实 logs/reports/quizzes 汇总替换 mock 指标 |

整体判断：项目能讲出完整闭环，但当前更像“可演示闭环”，还不是强数据驱动闭环。比赛前应优先把一条学生张三的主线跑通并留痕。

## 7. A3 赛题对应度问题

### 大模型

- 当前状态：默认 mock；`llm_service.py` 支持 DeepSeek/Qwen 兼容接口，但异常静默 fallback。
- 不足：答辩如果强调“基于大模型”，必须说明当前比赛稳定版默认 mock，真实模型需要 API Key。
- 建议：至少准备一段真实 LLM 调用演示或截图；否则把重点放在“可插拔大模型能力层和稳定 fallback”。

### 个性化资源生成

- 当前状态：`generate_resource_pack` 根据学生、课程、薄弱点生成 5 类资源。
- 不足：个性化主要来自 `weakPoints` 字符串，不一定基于长期画像、课程知识库和练习数据。
- 建议：将 `weakPoints` 来源明确绑定测验错因和画像诊断。

### 多智能体

- 当前状态：`backend/app/agents/graph.py` 有 LangGraph 六节点编排；`agent_workflow.py` 有工作流展示和记录。
- 不足：`run_full_learning_flow` 存在 P0 bug；页面模板文案仍写“未接真实 LangGraph”；真实执行与 demo 模板混合。
- 建议：修复接口，保留一次真实 run 记录，在页面展示每个 Agent 输入、输出、耗时和产物。

### 学习智能体

- 当前状态：Tutor、Planner、Resource、Evaluator、Reporter Agent 文件存在。
- 不足：学生练习后自动更新画像和路径不足。
- 建议：补“练后分析 -> 画像更新 -> 路径调整 -> 资源推荐”的事件链。

### 高等教育场景

- 当前状态：课程以 Python 程序设计、数据结构等高校课程为主。
- 不足：课程资料集规模较小，部分示例仍偏 demo。
- 建议：准备一门完整课程的章节、讲义、题库、实验任务、学习目标和评分标准。

### 工程完整性

- 当前状态：Web、小程序、FastAPI、脚本、文档齐全。
- 不足：后端入口和 Agent 接口存在 P0，测试报告过期。
- 建议：先修运行问题，再重新生成验收报告和演示录屏。

## 8. 演示风险清单

| 风险点 | 级别 | 证据 | 规避方案 |
| --- | --- | --- | --- |
| 后端启动失败 | P0 | `main.py` 未导入 router | 先修导入，启动后访问 `/health`、`/docs` |
| Agent 完整流程 500 | P0 | `agent_workflow.py` 未定义 `seed` | 修复后再演示运行；未修前只展示历史记录 |
| 小程序 AI 辅导页 undefined | P0 | `tutorMessages/ragTutorFallback` 未导出 | 补 demoData 或暂不点辅导页 |
| demo_ready_check 过期 | P0 | 报告写 READY，但当前发现新 P0 | 修复后重新运行并覆盖报告 |
| 端口冲突 | P1 | `start-dev.bat` 固定 8000/5173 | 演示前先执行 `stop-dev.bat` 或手工确认端口 |
| pid/log 残留 | P2 | 根目录、backend、frontend 均有 `.pid/.log` | 不影响运行，但打包排除 |
| 环境变量缺失 | P2 | `.env.example` 有 LLM Key 变量，默认 mock | 答辩说明未配 Key 时是 mock |
| 接口 404/500 | P0/P1 | 后端入口和 Agent bug | 用脚本覆盖 HTTP 检查，修复前不现场点 |
| 页面刷新状态丢失 | P2 | 多个页面状态仅在前端内存 | 主线演示按固定顺序，不依赖刷新后保存 |
| 小程序真机不可用 | P1 | 默认 127.0.0.1 | 用微信开发者工具演示；真机需局域网/HTTPS |
| Git 合并后未测试 | P0 | 文档和代码状态不一致 | 修复后重新 `git status`、build、健康检查 |

## 9. 文档与提交风险

- `review_problem.md` 原文件为乱码内容，已在本报告中重写为结构化审计报告。
- `README.md` 第 80 行写“不新增 LangChain、LangGraph、Chroma、FAISS 等重依赖”，但 `backend/requirements.txt` 含 `langgraph`、`chromadb`，代码也存在 LangGraph/Chroma。
- `docs/submission/系统开发说明.md` 第 46 行写“不使用向量数据库，也不引入 LangChain、LangGraph、Chroma、FAISS”，与当前代码不一致。
- `docs/submission/答辩演示脚本.md` 第 68 行写“当前没有使用向量数据库”，需要改成更准确的能力边界。
- `docs/final-acceptance-report.md` 路由清单偏旧，缺少 `/student/knowledge-graph`、`/student/smart-quiz`、`/teacher/ai-workbench`、`/admin/content-review`、`/admin/platform-quality` 等新增页面。
- `docs/reports/demo_ready_check.md` 声称 2026-06-04 检查 READY、FastAPI app 可加载、前端构建通过；当前 P0 修复前不应作为最终验收依据。
- `reports/demo_flow_check.md` 是 2026-06-01 的旧端到端报告，不能覆盖 2026-06-04 合并后的新问题。
- `docs/final-acceptance-report.md` 中出现 `python scripts\seed-demo-data.py`，但当前主脚本是 `scripts/seed_demo_data.py`，虽然也存在 `scripts/seed-demo-data.py`，文档命令应统一。
- `.gitignore` 已排除 `.env`、数据库、storage、日志、pid、node_modules、dist；但工作区实际存在这些内容，比赛提交包应按白名单整理。
- 缺少明确的“已知问题清单”文档，本文件可作为当前已知问题来源。
- 缺少最终 PPT 和演示视频文件本身；已有提交包目录结构说明，但需要实际产物。

## 10. 建议下一轮修复顺序

第 1 轮：必须先修的运行和合并问题

1. 修复 `backend/app/main.py` router 导入。
2. 修复 `backend/app/api/routers/agent_workflow.py` 中未定义 `seed`。
3. 修复小程序 `tutorMessages`、`ragTutorFallback` 缺失。
4. 启动后端，确认 `/health`、`/docs`、`/api/v1/demo-status`、`/api/v1/knowledge-graph`、`/api/v1/resources/generate-pack`。
5. 重新运行 `check-demo-ready` 和 `e2e_demo_flow_check`，覆盖旧报告。

第 2 轮：补齐主线闭环

1. 将 `StudentSmartQuiz.vue` 的提交结果写入后端测验记录和业务事件。
2. 增加“练后分析更新画像/路径”的最小接口或事件。
3. 将资源生成理由绑定画像、薄弱点、课程知识库引用。
4. 为张三主线准备一条稳定演示数据链。

第 3 轮：完善教师端和学生端

1. 教师端任务布置落库，并能在学生端学习路径/今日任务看到。
2. 教师分析页显示真实测验结果、薄弱点和干预建议。
3. 学生报告页显示最新测验和资源使用结果。
4. 隐藏或补齐教师端占位菜单。

第 4 轮：完善小程序和管理员端

1. 小程序练习页接后端提交接口，失败再 fallback。
2. 小程序报告页接后端报告摘要。
3. 管理员内容审核增加持久化 approve/reject。
4. 平台质量页尽量用真实 logs/quizzes/resources 汇总。

第 5 轮：文档、演示、答辩材料

1. 更新 README、系统开发说明、部署说明、答辩脚本中的 LangGraph/Chroma/RAG 表述。
2. 重写最终验收报告，删除过期 READY 结论。
3. 准备 PPT、7 分钟内录屏、截图目录。
4. 明确小程序提交方式：源码 + 微信开发者工具运行 + 录屏演示。
5. 打包前按白名单排除 `.env`、数据库、storage、logs、pid、node_modules、dist。

## 11. 可直接交给 Codex 的下一轮修复提示词

```text
只允许在当前 EduMind 项目目录内修改必要文件；不要安装依赖、不要删除文件、不要做无关重构。

目标：只修复 review_problem.md 中 P0 和 P1 问题，保证比赛主线可运行、可演示、可重新验收。

必须完成：
1. 修复 backend/app/main.py，显式导入并注册所有现有 router，确保 courses、knowledge_base、rag、content_review、profiles、learning_paths、resources、profile_dialog、tutor、quizzes、reports、agent_workflow、system_settings、logs、events、demo_status、competition、dashboard、user_profile_ws 都可用。
2. 修复 backend/app/api/routers/agent_workflow.py 中 run_full_learning_flow 引用未定义 seed 的问题，保证 POST /api/v1/agent-workflow/run-full-learning-flow 不会因 NameError 失败。
3. 修复 miniprogram/pages/tutor/index.js 与 miniprogram/utils/demoData.js 的不一致，补齐 tutorMessages 和 ragTutorFallback 或提供可靠默认值。
4. 核查 /api/v1/knowledge-graph、/api/v1/student/learning-tasks、/api/v1/quiz/chapter、/api/v1/quiz/submit、/api/v1/teacher/ai-workbench/generate、/api/v1/admin/content-review、/api/v1/admin/platform-quality、/api/v1/resources/generate-pack、/api/v1/rag/ask、/api/v1/content-review/check 是否能访问。
5. 管理员内容审核如时间允许，增加最小 approve/reject 后端接口或至少接入业务事件，避免只改前端本地状态。
6. 更新过期文档中与当前代码矛盾的表述，尤其是 LangGraph、Chroma、RAG、demo_ready_check READY 结论和小程序运行边界。

验证要求：
- 不要提交 node_modules、dist、storage 数据库、log、pid。
- 修复后运行后端健康检查、前端构建或等价检查，并重新生成 demo ready / e2e 报告。
- 最终说明只列出改动文件、验证结果和仍需人工核查项。
```