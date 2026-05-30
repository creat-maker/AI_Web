# EduMind

EduMind 是一个面向个性化学习资源生成与学习多智能体流程的 MVP 项目。当前版本重点跑通教师建课、课程资料上传、知识库构建、学生画像、学习路径生成、资源生成、RAG 答疑、测验评价和学习报告导出的演示闭环。

项目默认支持无真实大模型密钥的 mock 模式，便于本地开发、课堂演示和 GitHub 协作。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Vue Router
- 后端：FastAPI、SQLAlchemy、Pydantic Settings
- Agent：EduMind 内置演示编排，预留 LangGraph / LangChain 扩展字段
- RAG：Chroma 或本地 fallback，支持课程资料检索演示
- 数据库：SQLite 演示模式，保留 MySQL 初始化脚本
- 大模型：DeepSeek / 通义千问 OpenAI-compatible API，可通过环境变量配置
- 报告：docxtpl、python-docx

## 功能模块

- 课程管理：创建课程并查看课程数据
- 知识库：上传课程资料，解析后写入向量库
- 学生画像：采集学生基础信息并生成画像
- 学习路径：生成个性化学习路径
- 资源生成：生成讲解、练习、学习材料等资源
- 智能答疑：基于课程知识库进行 RAG 问答，并保存最近问答记录
- 测验评价：提交测验答案并返回评分和错因分析
- 教师分析：展示测评次数、平均得分、薄弱知识点、学生表现分布和教学建议
- 报告中心：生成并下载 Word 学习报告
- Agent 工作流：串联画像、规划、资源、评价和报告流程
- 日志管理：聚合系统运行、问答、知识库、Agent 和报告生成记录

## 项目目录结构

```text
EduMind/
|-- backend/                 FastAPI 后端服务
|   |-- app/                  后端应用代码
|   |-- requirements.txt      Python 依赖
|   `-- storage/              本地运行时数据目录，默认不提交真实数据
|-- frontend/                Vue 3 前端应用
|   |-- src/                  前端源码
|   |-- package.json          前端脚本和依赖
|   `-- vite.config.ts        Vite 开发代理配置
|-- database/                数据库初始化脚本
|-- docs/                    后续项目文档
|-- demo/                    后续演示材料
|-- sample_data/             后续示例数据
|-- scripts/                 后续辅助脚本
|-- legacy/                  旧项目代码隔离区，不进入主流程
|-- .env.example             环境变量模板
|-- .gitignore               Git 忽略规则
`-- README.md                项目说明
```

## 环境变量配置方法

复制环境变量模板：

```bash
copy .env.example .env
```

macOS / Linux 可使用：

```bash
cp .env.example .env
```

常用变量说明：

```env
DATABASE_URL=
SQLITE_FALLBACK_PATH=./backend/storage/eduagent.sqlite3
LLM_PROVIDER=mock
DEEPSEEK_API_KEY=
DASHSCOPE_API_KEY=
QWEN_API_KEY=
CHROMA_PERSIST_DIR=./backend/storage/chroma
UPLOAD_DIR=./backend/storage/uploads
REPORT_DIR=./backend/storage/reports
CORS_ORIGINS=http://localhost:5173
VITE_API_BASE_URL=
```

说明：

- 不配置真实 API Key 时，后端使用 mock 模式。
- `DATABASE_URL` 为空时默认使用 SQLite。
- 后端读取项目根目录 `.env`。
- `UPLOAD_DIR`、`REPORT_DIR`、`CORS_ORIGINS` 会被后端配置读取。
- `VITE_API_BASE_URL` 本地开发可留空，前端通过 Vite proxy 访问后端；生产或非代理场景可通过 shell 环境变量或 `frontend/.env.local` 配置。
- 不要提交 `.env` 或任何包含真实密钥的文件。

## 后端启动步骤

在项目根目录打开终端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

macOS / Linux 激活虚拟环境：

```bash
source .venv/bin/activate
```

健康检查：

```text
http://localhost:8000/health
```

## 前端启动步骤

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

前端本地开发时，`/api` 和 `/health` 会代理到 `http://localhost:8000`。

## Windows 一键启动

首次使用前安装前端依赖：

```bash
cd frontend
npm install
```

一键启动后端 FastAPI 和前端 Vue 开发服务器：

```bash
start-dev.bat
```

也可以在 Windows 资源管理器中双击 `start-dev.bat`。脚本会分别打开后端和前端命令行窗口。

停止本地开发服务：

```bash
stop-dev.bat
```

也可以在 Windows 资源管理器中双击 `stop-dev.bat`。该脚本只会尝试关闭占用 `8000` 和 `5173` 的进程，不会删除文件。

常用访问地址：

```text
http://localhost:5173/dashboard
http://localhost:8000/docs
```

## 演示数据初始化

初始化本地演示数据：

```bash
python scripts/seed_demo_data.py
```

兼容旧入口仍可使用：

```bash
python scripts/seed-demo-data.py
```

Windows 也可以双击或运行：

```bat
seed-demo-data.bat
```

然后启动项目：

```bat
start-dev.bat
```

建议依次验证以下页面：

```text
http://localhost:5173/dashboard
http://localhost:5173/knowledge-base
http://localhost:5173/tutor-chat
http://localhost:5173/teacher-analysis
http://localhost:5173/agent-workflow
http://localhost:5173/reports
http://localhost:5173/logs
```

说明：

- 脚本不会清空数据库。
- 脚本不会删除用户已有数据或 storage 文件。
- 脚本会复用已存在的同名演示课程、学生、文档、测验、报告和 Agent 记录，避免重复插入。
- 脚本只生成演示业务数据和小型本地演示文件，不写入真实 API Key 或敏感信息。

## 演示流程

### 0. 三端角色化架构

EduMind 前端已进入“三端角色化架构第一阶段”，当前不接真实登录鉴权，使用前端 localStorage 保存当前身份，用于比赛演示不同用户端的信息架构和导航入口。

#### 三端角色说明

- 学生端：面向个性化学习主线，围绕画像、课程、资源、路径、答疑、测验和学习报告组织学习闭环。
- 教师端：面向教学干预和班级管理，围绕课程、学生、任务、测评、报告和教学提醒组织教学闭环。
- 管理员端：面向平台治理和系统运营，围绕资源生成、Agent 工作流、日志、知识库运营、权限和系统设置组织管理闭环。

#### 三端菜单说明

学生端菜单：

```text
学习总览 / 对话建画像 / 我的课程 / 资源生成 / 学习路径 / 智能答疑 / 知识库 / 课程资料 / 测验成绩 / 学习报告 / 笔记本 / 学习小组 / 设置
```

教师端菜单：

```text
班级概览 / 课程管理 / 班级学生管理 / 学生画像分析 / 学习路径与任务布置 / 资源库 / 测验评价与教师分析 / 智能答疑管理 / 报告中心 / 通知中心 / 教学日历 / 待办 / 设置中心
```

管理员端菜单：

```text
平台总览 / 课程管理 / 用户与角色 / 资源生成中心 / Agent 工作流 / 报告审核中心 / 日志管理 / 知识库运营 / 文档解析 / 权限配置 / 通知公告管理 / 数据统计与导出 / 系统设置
```

未完成的业务模块会进入占位页，占位页会说明模块用途和后续接入能力，不会伪装成已完成真实功能。

#### 三端首页说明

- 学生端首页 `/student`：展示今日学习目标、课程进度、画像状态、推荐资源、学习路径、今日任务、答疑入口、学习报告、测验提醒和积分简况。
- 教师端首页 `/teacher`：展示课程数、学生数、平均进度、风险学生、待处理事项、班级趋势、薄弱知识点和快捷操作。
- 管理员端首页 `/dashboard`：沿用平台总控台，展示平台统计、模块健康、最近事件、Agent 状态、报告、告警和数据闭环。

#### 角色切换方式

页面左侧显示“当前身份：学生端 / 教师端 / 管理员端”，点击角色切换按钮即可切换。当前角色会写入浏览器 localStorage，刷新页面后仍保持该身份。切换后侧边栏菜单和顶部页面说明会同步变化。

#### 旧路由兼容说明

旧业务页面仍可直接访问，不删除旧能力：

```text
/dashboard
/courses
/knowledge-base
/profiles
/learning-paths
/resources
/agent-workflow
/tutor-chat
/quiz-evaluate
/teacher-analysis
/reports
/logs
/settings
```

同时补充以下兼容入口：

```text
/learning-path
/resource-generation
/evaluation
/student
/teacher
/admin
```

#### 三端推荐演示路线

学生端：

```text
学习总览 → 对话建画像 → 资源生成 → 学习路径 → 智能答疑 → 测验成绩 → 学习报告
```

教师端：

```text
班级概览 → 课程管理 → 学生画像分析 → 路径与任务布置 → 测验评价 → 报告中心
```

管理员端：

```text
平台总览 → 资源生成中心 → Agent 工作流 → 日志管理 → 系统设置
```

#### 三端第二阶段：核心页面按角色包装

第二阶段在不改后端数据库、不接真实登录鉴权的前提下，对核心旧页面做 role-aware 包装。同一个路由会根据当前角色显示不同标题、说明、操作按钮和信息模块：

- `/courses`
  - 学生端：我的课程，突出课程进度、今日任务、课程资料、继续学习、测验和报告入口；隐藏删除等危险管理按钮。
  - 教师端：课程管理，突出新建课程、章节管理、布置任务、发布课程、课程报告和编辑删除。
  - 管理员端：平台课程管理，突出课程状态、审核、归档、教师归属、统计和内容合规。
- `/profiles`
  - 学生端：对话建画像，突出学习目标、当前基础、学习偏好、资源偏好、薄弱知识点、画像标签和重新生成画像。
  - 教师端：学生画像分析，突出班级学生、能力条、薄弱点、风险等级、学习趋势、干预建议和生成报告入口。
  - 管理员端：画像数据概览，突出隐私权限提示和数据治理，不默认展示过多学生隐私细节。
- `/resource-generation`
  - 学生端：个性化资源生成，突出画像摘要、薄弱点、8 类资源类型、一键生成资源包、加入路径、收藏下载。
  - 教师端：教学资源生成，突出按课程/班级/薄弱点生成分层练习、课件提纲、课堂案例、任务包和推送。
  - 管理员端：资源生成中心，突出生成任务、成功率、失败任务、类型分布、模板管理、内容审核和生成日志。
- `/reports`
  - 学生端：学习报告，突出学习总结、知识点掌握、薄弱点、下一步建议、推荐资源和路径调整。
  - 教师端：报告中心，突出学生/班级/课程/测验/风险报告、证据链、干预建议和下载分享。
  - 管理员端：报告审核中心，突出 AI 报告审核、内容安全、引用来源检查、通过、驳回重生成和审核日志。
- `/knowledge-base`
  - 学生端：知识库 / 课程资料，突出课程资料、资料搜索、引用来源、收藏和下载，弱化解析技术细节。
  - 教师端：资源库，突出上传课程资料、管理教学资源、关联课程、关联学习路径和推送给学生。
  - 管理员端：知识库运营 / 文档解析，突出解析状态、切片数量、向量化状态、失败原因、引用命中率、质量评分和 RAG 诊断。

原始 JSON 数据不会默认大面积裸露；画像原始数据折叠在“原始画像数据（展开查看）”中。所有 demo/mock/fallback 操作会在页面文案或反馈中说明边界。

第二阶段推荐演示路线：

```text
学生端：学习总览 → 对话建画像 → 个性化资源生成 → 学习路径 → 智能答疑 → 学习报告
教师端：班级概览 → 课程管理 → 学生画像分析 → 学习路径与任务布置 → 测验评价 → 报告中心
管理员端：平台总览 → 资源生成中心 → Agent 工作流 → 知识库运营 → 报告审核中心 → 日志管理
```

#### 三端第三阶段：关键业务闭环与事件日志

第三阶段新增轻量业务事件机制，复用 `system_logs` 表记录三端关键操作，不新增重型依赖、不接真实登录鉴权、不接真实 LangGraph/RAGFlow。业务事件通过 `/api/v1/events` 写入和读取，管理员端日志中心也能按 `business_event` 类型查看。

当前支持的事件类型包括：

```text
profile_generated
resource_generated
resource_added_to_path
path_updated
quiz_completed
report_generated
teacher_intervention_created
task_assigned
admin_review_completed
agent_workflow_rerun
knowledge_base_reparsed
question_answered
```

事件字段包含：`id`、`event_type`、`title`、`description`、`actor_role`、`actor_name`、`target_type`、`target_id`、`related_student`、`related_course`、`status`、`created_at`、`metadata`。

第三阶段闭环说明：

- 学生端画像到资源到路径：`/profiles` 生成画像写入 `profile_generated`；`/resource-generation` 生成 8 类资源包写入 `resource_generated`；加入学习路径写入 `resource_added_to_path` 和 `path_updated`；`/learning-path` 可看到资源包摘要。
- 学生端答疑到报告影响：`/tutor-chat` 提问写入 `question_answered`，保留引用来源；`/reports` 学生端展示最近答疑对薄弱点、推荐资源和路径建议的影响。
- 学生端测验到画像和路径：`/evaluation` 支持“完成一次 demo 测验”，写入 `quiz_completed`，画像页、资源生成页和学习路径页会读取测验事件展示影响。
- 教师端干预到学生任务：`/profiles` 教师端支持布置补强任务，写入 `teacher_intervention_created` 和 `task_assigned`；学生首页和学习路径页会展示该任务。
- 管理员端审核与日志：`/reports` 管理员端审核按钮写入 `admin_review_completed`；`/knowledge-base` 管理员重新解析写入 `knowledge_base_reparsed`；`/logs` 可查看业务事件；`/agent-workflow` 显示三类 demo 工作流和业务事件映射的模拟 run_id。

轻量 mock API 与真实写入边界：

- 真实写入 SQLite fallback：业务事件、资源包生成结果、学习路径更新、demo 测验提交、TutorChat 问答日志。
- demo/mock/fallback：资源包内容、多智能体节点输出、教师任务执行状态、管理员审核流、知识库重新解析动作本身。

第三阶段推荐演示路线：

```text
学生端：/student → /profiles 生成画像 → /resource-generation 生成资源包 → 加入学习路径 → /learning-path 查看路径 → /tutor-chat 提问 → /evaluation 完成测验 → /reports 查看报告
教师端：/teacher → /profiles 查看学生画像 → 布置补强任务 → /teacher-analysis 查看干预建议 → /reports 查看报告
管理员端：/dashboard → /agent-workflow 查看流程 → /resource-generation 查看资源任务 → /reports 审核报告 → /logs 查看事件日志
```

#### 第四阶段：一键端到端验收脚本

第四阶段新增轻量端到端验收脚本，用于比赛演示前检查主链路是否可用，并生成 Markdown 验收报告。脚本只使用 Python 标准库和后端 HTTP API，不引入 Playwright/Selenium 等重型依赖。

先启动后端：

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

然后在项目根目录运行：

```bash
python scripts/e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports/demo_flow_check.md
```

脚本会自动验证：

```text
画像生成 → 个性化资源包生成 → 资源包加入学习路径 → 教师布置补强任务 → demo 测验完成 → TutorChat 提问答疑 → 管理员报告审核 → 查询 events/logs/agent-workflow/learning-paths
```

报告内容包括验收时间、后端地址、总体通过率、每个步骤的接口和关键字段、关键 `event_type` 检查、真实能力说明、demo/fallback 能力说明和比赛演示建议路线。默认报告输出到 `reports/demo_flow_check.md`，目录不存在时脚本会自动创建。

#### 第五阶段：比赛演示模式面板

第五阶段新增管理员端“比赛演示模式”页面 `/demo-status`，用于答辩前快速查看系统是否适合现场演示。页面读取后端 `GET /api/v1/demo-status`，该接口会解析 `reports/demo_flow_check.md` 并返回端到端验收状态。

页面展示内容：

- 比赛演示状态：Ready / Missing Report / Warning。
- 通过率、最近验收时间、验收报告路径。
- 关键链路事件：画像生成、资源包生成、资源加入路径、路径更新、教师干预、任务布置、测验完成、智能答疑、管理员审核。
- 学生端、教师端、管理员端推荐演示路线。
- 当前真实能力和 demo/mock/fallback 能力边界。
- 刷新验收报告的终端命令。

刷新验收报告：

```bash
python scripts/e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports/demo_flow_check.md
```

浏览器不会直接执行本地 Python 脚本；运行命令后刷新 `/demo-status` 即可读取最新报告。

答辩前检查流程：

```text
1. 启动后端：cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000
2. 启动前端：cd frontend && npm run dev
3. 生成演示数据：python scripts/seed_demo_data.py
4. 运行端到端验收：python scripts/e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports/demo_flow_check.md
5. 打开 /demo-status 查看 Ready 状态和关键事件 PASS 情况
6. 按页面推荐路线进行学生端、教师端、管理员端演示
```

#### 第六阶段：答辩演示导航模式

第六阶段在 `/demo-status` 中增加“答辩演示导航模式”。该页面不只展示验收状态，还提供学生端、教师端、管理员端的固定演示路线、推荐讲解词、预期页面结果和一键跳转按钮，适合比赛现场按步骤稳定演示完整闭环。

导航模式包含：

- 演示总览：预计 7 分钟、当前系统状态、e2e 通过率、推荐路线“学生端 → 教师端 → 管理员端”。
- 学生端步骤：学习总览 → 对话建画像 → 个性化资源生成 → 学习路径 → 智能答疑 → 测验成绩 → 学习报告。
- 教师端步骤：班级概览 → 学生画像分析 → 布置补强任务 → 测验评价与教师分析 → 报告中心。
- 管理员端步骤：平台总览 → Agent 工作流 → 资源生成中心 → 报告审核 → 日志管理。
- 每个步骤展示页面路由、演示目标、推荐讲解词、预期结果，并提供“打开页面”和“复制讲解词”按钮。
- 点击步骤跳转时会同步切换当前身份，保证同一路由在不同角色下展示正确语义。

答辩前推荐操作顺序：

```text
1. 生成演示数据：python scripts/seed_demo_data.py
2. 启动后端：cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000
3. 启动前端：cd frontend && npm run dev
4. 运行端到端验收：python scripts/e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports/demo_flow_check.md
5. 打开 /demo-status，确认 Ready 状态、关键事件 PASS 和 100% 通过率
6. 点击“开始演示”，按页面导航依次演示学生端、教师端、管理员端闭环
```

说明：浏览器端不会直接执行本地 Python 脚本；如需刷新验收结果，请在终端运行验收命令后刷新 `/demo-status`。

### 1. 启动后端

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```text
http://localhost:8000/health
http://localhost:8000/docs
```

### 2. 启动前端

```bash
cd frontend
npm run dev
```

访问：

```text
http://localhost:5173/dashboard
```

Windows 可直接运行：

```bat
start-dev.bat
```

### 3. 生成演示数据

推荐使用新脚本入口：

```bash
python scripts/seed_demo_data.py
```

脚本会生成课程、学生画像、知识库文档记录、文档解析状态、TutorChat 问答记录、引用来源记录、测评结果、知识点掌握度数据、AgentWorkflow 运行记录、ReportCenter 报告记录、LogManagement 日志记录和 Dashboard 统计所需数据。脚本可重复运行，会优先复用已有演示数据，避免明显重复脏数据。

### 4. 比赛演示推荐路线

```text
1. Dashboard：先展示总控台、模块健康、最近事件流和数据闭环。
2. KnowledgeBase：展示文档解析状态、切片数量、TopK、引用命中率、质量评分、切片预览和可信 RAG 质量诊断。
3. TutorChat：选择课程提问，展示启发式答疑、不直接给答案模式、分层提示、错因识别、引用来源卡片和追问建议。
4. AgentWorkflow：展示 run_id、langgraph_run_id 预留字段、节点状态、耗时、错误信息和模拟重跑。
5. ReportCenter：展示报告列表、质量评分、生成依据、关键结论、Evidence Chain 证据链、引用文档、引用片段、学习路径和模拟重新生成。
6. LogManagement：按问答、知识库、Agent、报告、错误日志筛选，查看 metadata 和链路详情。
7. TeacherAnalysis / Settings：补充展示知识点掌握度矩阵、学生风险等级、班级掌握度分布、教师干预建议和系统配置脱敏状态。
```

### 4.1 可信 RAG 诊断说明

KnowledgeBase 页面新增“可信 RAG 质量诊断”区域，用于答辩时解释检索、引用和无依据回答风险：

- `document_count`、`chunk_count`、`average_chunk_length` 用于说明知识库规模。
- `top_k`、`retrieval_hit_rate`、`citation_coverage` 用于说明检索召回和引用覆盖情况。
- `unsupported_answer_rate` 用于提示可能存在无依据回答的风险。
- `knowledge_quality_score` 是面向比赛演示的综合质量评分。
- 最近检索诊断会展示用户问题、query rewrite 结果、TopK 片段、最终引用片段、未采用片段、引用置信度和风险标记。

当前指标基于 SQLite 中的文档、问答日志和检索分数做轻量规则估计，页面和接口均标注为 demo/fallback，不代表已经接入真实 RAGFlow 或生产级 RAG 评估器。

### 4.2 教学型对话说明

TutorChat 页面新增教学型答疑字段：

- 分层提示：轻提示 / 中提示 / 详细解释。
- 错因识别：概念混淆、计算错误、审题错误、知识缺漏等规则分类。
- `teaching_strategy`：展示当前采用的教学策略。
- `hint_level`、`detected_misconception`、`mastery_delta`：用于解释本次互动如何进入学情闭环。
- 开启“不直接给答案”后，回答优先返回引导式问题和提示。

当前教学策略和错因识别是规则型 demo/fallback 逻辑，后续可替换为真实模型诊断或教师知识追踪服务。

### 4.3 报告证据链说明

ReportCenter 报告详情新增 Evidence Chain / 证据链区域。每条结论包含：

- `conclusion`
- `evidence_type`：document / quiz / chat / mastery / agent_run
- `source_title`
- `source_excerpt`
- `confidence`
- `related_knowledge_point`

证据链用于展示“结论从哪里来”，便于讲清楚从知识库、测评、问答、掌握度和 Agent 运行到学习报告的闭环。当前证据链优先基于报告 JSON、引用记录和演示数据生成，后续可接真实引用追踪和报告质量评估器。

### 4.4 知识追踪说明

TeacherAnalysis 页面新增知识追踪区域：

- 知识点掌握度矩阵。
- 学生风险等级。
- 薄弱知识点 Top5。
- 班级掌握度分布。
- 学生进步趋势。
- 教师干预建议。

当前掌握度使用规则估计：

```text
mastery = correctness_rate * 0.6 + recent_performance * 0.3 + interaction_activity * 0.1
```

接口中保留 `bkt_dkt_reserved` 字段，后续可接 BKT/DKT 或其他知识追踪模型。

### 4.5 浏览器级验收脚本

启动前端开发服务后，可以运行轻量页面验收脚本：

```bash
python scripts/check_demo_pages.py --base-url http://localhost:5173
```

脚本会检查 `/dashboard`、`/knowledge-base`、`/tutor-chat`、`/agent-workflow`、`/reports`、`/logs` 是否可访问，并检查页面 HTML 中是否出现 `undefined`、`NaN`、`[object Object]` 等明显异常。该脚本不依赖 Playwright/Selenium，只使用 Python 标准库发起请求。

### 5. 当前真实能力

- FastAPI 接口、Vue 页面、路由和启动方式均为项目内真实实现。
- SQLite fallback 数据库真实持久化业务记录。
- 课程、学生画像、知识库文档、问答日志、测评、报告和 AgentRun 记录来自现有数据库表。
- 知识库上传、文本切片、检索和问答记录保存沿用项目内轻量 RAG/fallback 实现。
- 报告中心支持生成和下载本地 Word 报告文件。
- 日志中心会聚合真实业务表记录，并额外支持 `system_logs` 演示日志表。

### 6. 当前 demo/mock/fallback 能力

- 没有真实大模型 API Key 时，系统使用 mock LLM。
- AgentWorkflow 的“模拟重跑”是 EduMind 内部 demo/fallback 编排，没有接真实 LangGraph。
- `langgraph_run_id` 是预留字段，当前不会写入真实 LangGraph 运行 ID。
- KnowledgeBase 的质量评分、覆盖率、引用命中率、可信 RAG 质量诊断、query rewrite 和无依据回答风险识别是演示型统计。
- ReportCenter 的引用片段、质量评分、证据链和重新生成原因包含 demo/fallback 数据，用于比赛展示闭环。
- TutorChat 的启发式答疑、“不直接给答案”、分层提示、错因识别和掌握度变化是轻量规则逻辑，不代表真实商业产品能力。
- TeacherAnalysis 的知识追踪矩阵和学生风险等级是规则估计，预留 BKT/DKT 扩展字段。

### 7. 后续接真实 LangGraph/RAG 的扩展方向

- 在 `backend/app/api/routers/agent_workflow.py` 将模拟节点替换为真实 LangGraph 节点执行，并写入真实 `langgraph_run_id`。
- 在 `backend/app/rag/vector_store.py` 和 `backend/app/api/routers/knowledge_base.py` 接入真实向量库、文档解析任务、chunk 元数据和召回评估指标。
- 在 `backend/app/api/routers/tutor.py` 将 mock LLM 和轻量检索上下文替换为真实 RAG 问答链。
- 在 `backend/app/api/routers/reports.py` 接入真实引用追踪、报告质量评估器和异步重新生成任务。
- 在 `backend/app/api/routers/logs.py` 或统一日志服务中接入真实运行事件采集、错误堆栈脱敏和可观测性平台。
- 在 `backend/app/api/routers/quizzes.py` 或独立 knowledge tracing 服务中接入 BKT/DKT 模型，将当前 demo/fallback 掌握度估计替换为真实时序学习状态。

## 演示前检查

比赛现场完整手册见：[docs/demo-checklist.md](docs/demo-checklist.md)。

推荐比赛演示前按以下顺序准备：

```bat
seed-demo-data.bat
check-demo-ready.bat
start-dev.bat
```

也可以直接运行检查脚本：

```bash
python scripts/check-demo-ready.py
```

检查项包括课程、学生画像、知识库文档、问答日志、测评提交、学习报告、Agent 运行记录、学习路径、生成资源、关键 storage 目录和常用 Windows 脚本。

推荐演示页面顺序：

```text
http://localhost:5173/dashboard
http://localhost:5173/knowledge-base
http://localhost:5173/tutor-chat
http://localhost:5173/teacher-analysis
http://localhost:5173/agent-workflow
http://localhost:5173/reports
http://localhost:5173/logs
http://localhost:5173/settings
```

检查脚本只读取数据库和文件状态，不会清空数据库、删除用户数据或启动服务。

## 智能体工作流页面

进入方式：

```text
http://localhost:5173/agent-workflow
```

页面展示教学智能体工作流中心，包括今日运行次数、成功率、平均耗时、生成产物数量、运行记录和最近一次产物摘要。

流程节点包括：

```text
任务接收 -> 意图识别 -> 知识库检索 -> 答案生成 -> 学情分析 -> 教学建议 -> 报告生成
```

验证方式：先确认后端 `http://localhost:8000/docs` 可访问，再进入 `http://localhost:5173/agent-workflow`，选择课程并点击“运行完整学习流”。页面应展示节点状态、运行记录、答疑结果、知识库引用、薄弱点分析、教学建议和报告入口；接口失败时页面会显示错误和 fallback 内容，不应白屏。

## 报告中心

进入方式：

```text
http://localhost:5173/reports
```

报告中心展示报告总数、本周新增、已完成报告、平均质量评分，并支持按课程、状态和标题关键词筛选。

报告详情预览包括：

```text
学习表现摘要、薄弱知识点、推荐学习路径、教学建议、引用来源、报告生成时间
```

验证方式：先通过 `http://localhost:5173/agent-workflow` 运行一次完整学习流生成报告，再进入 `http://localhost:5173/reports`。页面应显示报告列表、预览区和下载入口；如果通过 AgentWorkflow 的报告入口进入，URL 可携带 `report_id` 用于预留选中对应报告。

## 日志管理中心

进入方式：

```text
http://localhost:5173/logs
http://localhost:5173/log-management
```

日志管理中心展示今日日志数、错误日志数、Agent 运行次数、问答记录数，并按系统日志、问答日志、知识库日志、Agent 日志、报告日志和错误日志分类查看。

页面聚合的数据包括：

```text
Dashboard 运行状态、TutorChat 问答记录、KnowledgeBase 文档上传与解析记录、AgentWorkflow 运行记录、ReportCenter 报告生成记录、Settings 脱敏配置检查记录
```

验证方式：先确认后端 `http://localhost:8000/docs` 可访问，再进入 `http://localhost:5173/logs`。页面应显示概览卡片、分类标签、筛选搜索、日志列表和详情预览；如果真实日志不足，会展示兼容 fallback 数据；如果接口失败，前端会显示错误和本地 fallback 内容，不应白屏。

安全说明：日志中心当前用于演示和运行追踪，只返回业务摘要、模块、状态、关联课程和记录 ID，不暴露 API Key、环境变量明文或上传文件敏感内容。

## 系统设置与算法配置

进入方式：

```text
http://localhost:5173/settings
```

系统设置页面展示 EduMind 的运行模式、模型模式、知识库状态、模型配置、RAG 知识库配置、教学策略配置和系统安全提示。

安全说明：

```text
页面只显示 API Key 是否已配置，不会在前端明文展示真实 API Key。
保存配置为当前页面暂存展示，不会修改系统环境变量。
```

验证方式：先确认后端 `http://localhost:8000/docs` 可访问，再进入 `http://localhost:5173/settings`。页面应显示概览卡片、模型配置、RAG 配置、教学策略、安全提示，并可点击“测试连接”查看脱敏检查结果；接口失败时页面会显示 fallback 配置，不应白屏。

## 常见问题

### 如何上传资料并检索知识库？

进入「知识库」页面，先选择课程，再拖拽或点击选择 PDF、Word、PPT、TXT 或 Markdown 资料，点击「上传并构建知识库」。解析完成后，页面会显示文档状态、知识切片数量和最近上传时间。

在「检索测试」区域输入关键词，点击「检索知识片段」，可查看来源文档、相似度分数和命中的知识片段。若检索无结果，先确认该课程已有已解析文档。

### 如何查看学情分析？

进入「教师分析」页面，可查看测评次数、参与学生数、平均得分、薄弱知识点、学生表现分布、教学建议和最近测评/报告记录。若真实测评数据不足，页面会使用兼容展示数据保证演示不空白。

### 没有大模型 API Key 能不能运行？

可以。保持 `LLM_PROVIDER=mock`，或不填写对应 API Key，后端会进入演示 mock 模式。

### 本地数据库在哪里？

默认 SQLite 文件在 `backend/storage/eduagent.sqlite3`。该文件属于运行时数据，不应提交到 GitHub。

### 上传文件、报告和向量库是否需要提交？

不需要。`backend/storage/` 和 `storage/` 下的上传文件、报告文件、向量库文件和日志都应作为本地运行时数据处理。

### 前端请求不到后端怎么办？

先确认后端 `http://localhost:8000/health` 可访问，再确认前端通过 `npm run dev` 启动。生产部署时需要按实际后端地址配置 `VITE_API_BASE_URL`。

### Windows 终端中文显示乱码怎么办？

源码按 UTF-8 保存。若 PowerShell 显示乱码，可尝试切换终端编码或使用支持 UTF-8 的终端。

## GitHub 协作开发流程

1. 从远程仓库拉取最新代码。
2. 基于 `main` 或团队指定分支创建功能分支。
3. 本地完成修改，并确认没有提交 `.env`、数据库、日志、上传文件、构建产物和依赖目录。
4. 运行必要的本地检查，例如后端启动、前端构建或页面联调。
5. 提交代码并推送到远程功能分支。
6. 发起 Pull Request，说明修改内容、验证方式和潜在影响。
7. 通过代码审查后合并。

## 分支说明

- `main`：稳定分支，保存可演示、可交付版本。
- `dev`：集成开发分支，用于合并阶段性功能。
- `feature/<name>`：功能开发分支。
- `fix/<name>`：缺陷修复分支。
- `docs/<name>`：文档修改分支。

## 提交信息规范

建议使用简洁的类型前缀：

```text
feat: add course import flow
fix: handle empty quiz answer
docs: update local setup guide
chore: improve gitignore rules
refactor: simplify report generation helper
test: add API smoke tests
```

常用类型：

- `feat`：新增功能
- `fix`：修复问题
- `docs`：文档变更
- `chore`：构建、配置、依赖、脚本等杂项
- `refactor`：不改变行为的代码重构
- `test`：测试相关修改

## 当前边界

当前阶段聚焦 MVP 演示闭环，不包含数字人视频生成、AR/VR、全网爬虫、复杂 OCR 阅卷、移动端、真实消息推送和复杂在线判题系统。
