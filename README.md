# EduMind

EduMind 是一个面向比赛演示的三端教育智能体系统。当前版本重点固化“打开即可演示”的闭环：学生端学习闭环、教师端教学干预闭环、管理员端平台治理闭环、AI Agent 工作流展示闭环，以及一键演示状态检查。

## 项目简介

EduMind Studio 面向个性化学习资源与教学智能体场景，提供 Web 三端和原生微信小程序学生端体验版。系统当前为比赛演示与验收版本，采用本地演示数据、轻量 RAG 和规则化 Agent 编排，展示从学习画像、知识检索、资源生成、内容审核到学习报告的完整闭环。

## 核心创新点

- 双端展示：Web 学生端、教师端、管理员端 + 原生微信小程序学生端。
- 画像驱动：通过对话式回答生成学习目标、基础水平、薄弱点、偏好、时间安排、风险和推荐策略。
- 个性化资源：围绕薄弱点生成讲义、练习题、代码案例或实验任务、思维导图文本、视频脚本或项目任务书。
- 轻量 RAG：基于《Python 程序设计》课程知识库做关键词检索和引用来源展示。
- 防幻觉审核：对无引用、引用覆盖不足、绝对化承诺等内容给出风险等级和修改建议。
- Agent 链路：展示画像构建、知识检索、路径规划、资源生成、内容审核、学习报告六步执行过程。

## 技术架构概览

- Web 前端：Vue 3、Vite、TypeScript、Vue Router、ECharts。
- 后端服务：FastAPI、SQLAlchemy、Pydantic Settings。
- 小程序：原生微信小程序结构，不使用 uni-app 或 Taro。
- 数据与知识库：SQLite 演示库 + `docs/course_kb/python_programming.json`。
- AI 演示：规则化画像、资源生成、轻量 RAG、防幻觉审核和 AgentWorkflow，不接真实大模型 API。

## 小程序学生端体验版

项目新增 `miniprogram` 目录，提供原生微信小程序学生端体验版，不使用 uni-app 或 Taro。小程序面向比赛移动端展示，包含“今日学习、学习路径、资源推荐、AI 辅导、练习错题、学习报告”六个页面，默认使用 `miniprogram/utils/demoData.js` 本地演示数据，不依赖后端也可打开。

- 打开方式：微信开发者工具 -> 导入项目 -> 选择 `miniprogram` 目录。
- AppID：本地体验可使用测试号或无 AppID 模式，`project.config.json` 默认使用 `touristappid`。
- 后端预留：`miniprogram/utils/request.js` 封装了 FastAPI 请求，默认 `baseUrl` 为 `http://127.0.0.1:8000`。
- 使用说明：见 `docs/miniprogram-guide.md`。

## 对话式画像与 5 类资源生成

本版本补齐软件杯演示核心能力，新增稳定规则生成接口，不接真实大模型 API：

- `POST /api/v1/profile-dialog/run`：输入学生自然语言回答，输出学习目标、基础水平、薄弱知识点、学习偏好、时间安排、学习风险、推荐策略等画像维度。
- `POST /api/v1/resources/generate-pack`：输入 `studentId`、`courseId`、`weakPoints`，输出 5 类资源：个性化讲义、练习题、代码案例或实验任务、思维导图文本、视频脚本或项目任务书。

Web 学生端 `/student/assistant` 可展示画像对话和资源包结果；小程序资源页会优先请求资源包接口，失败时自动回退 `demoData.js`，保证比赛现场稳定。

## 课程知识库、RAG 与防幻觉审核

本版本新增轻量可演示的课程知识库与 RAG 引用链路，不引入向量数据库、不接真实大模型：

- 知识库文件：`docs/course_kb/python_programming.json`，包含《Python 程序设计》的课程章节、知识点、讲义片段、练习题、实验任务、来源文件名和章节名。
- `POST /api/v1/rag/ask`：基于关键词匹配和规则排序返回答案、引用来源、匹配片段、可信度、推荐练习和相关知识点。
- `POST /api/v1/content-review/check`：对生成内容做引用覆盖和夸张承诺检查，返回风险等级、可信度、引用覆盖率、防幻觉警告、审核状态和修改建议。
- `GET /api/v1/content-review/records`：返回最近内容审核记录，供 Web 展示。

Web 学生端 `/student/assistant` 展示 RAG 回答、引用来源、可信度和推荐练习；管理员端 `/resource-generation` 展示 AI 内容审核 / 防幻觉审核记录；`/agent-workflow` 展示“画像构建 -> 知识检索 -> 路径规划 -> 资源生成 -> 内容审核 -> 学习报告”的完整执行链路。小程序 AI 辅导页会优先请求 `/api/v1/rag/ask`，后端不可用时回退本地 `demoData.js`。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Vue Router、ECharts
- 后端：FastAPI、SQLAlchemy、Pydantic Settings
- 数据：默认 SQLite fallback，保留 MySQL 初始化脚本
- AI / Agent：内置 mock/fallback 演示链路，预留 LangGraph、LangChain、RAGFlow/Dify/FastGPT 扩展边界
- 知识库：本地文档元数据与轻量检索演示，预留 Chroma 持久化目录
- 报告：python-docx / docxtpl 生成本地 Word 学习报告

## 三端角色

- 学生端：围绕课程、学习路径、智能答疑、测验成绩和学习报告形成个人学习闭环。
- 教师端：围绕班级概览、课程管理、学生画像、路径任务、测评分析和报告中心形成教学干预闭环。
- 管理员端：围绕平台总览、用户角色、课程治理、AI 资源生成、Agent 工作流、日志和系统设置形成平台治理闭环。

## 统一演示数据

第五阶段统一使用以下核心演示对象：

- 学生：张三、李四、王五
- 教师：王老师、陈老师、张老师
- 课程：Python 爬虫基础与实践、人工智能导论、数据结构与算法、Web 开发技术
- 班级：计科大三 1 班、计科大三 2 班

前端集中演示数据位于 `frontend/src/api/mocks/demoData.ts`。后端演示种子数据由 `scripts/seed_demo_data.py` 写入数据库，不清空用户数据。

## 本地启动

首次安装前端依赖：

```bash
cd frontend
npm install
```

启动后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动前端：

```bash
cd frontend
npm run dev
```

Windows 一键启动：

```bat
start-dev.bat
```

停止本地 8000 / 5173 端口服务：

```bat
stop-dev.bat
```

## 演示数据初始化

```bat
seed-demo-data.bat
```

或：

```bash
python scripts/seed_demo_data.py
```

脚本会补齐课程、学生画像、课程资料记录、学习路径、资源、测验、报告、AgentRun 和业务事件日志。

## 推荐演示路线

学生端：

1. `/student` 学习总览
2. `/student/courses` 我的课程
3. `/student/learning-path` 学习路径
4. `/student/assistant` 智能答疑
5. `/student/exams` 测验成绩
6. `/student/reports` 学习报告

教师端：

1. `/teacher` 班级概览
2. `/courses` 课程管理
3. `/profiles` 学生画像
4. `/learning-path` 学习路径与任务布置
5. `/teacher-analysis` 测评分析
6. `/reports` 报告中心

管理员端：

1. `/dashboard` 平台总览
2. `/admin/users` 用户与角色
3. `/admin/courses` 课程治理
4. `/resource-generation` AI 资源生成
5. `/agent-workflow` Agent 工作流
6. `/logs` 日志管理
7. `/settings` 系统设置

演示状态页：`/demo-status`。该页面展示三端路线、关键能力、最近验收结果和刷新验收报告命令。

## 验收脚本

演示状态检查：

```bash
python scripts/check-demo-ready.py
```

生成报告位置：`docs/reports/demo_ready_check.md`。

端到端闭环检查：

```bash
python scripts/e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports/demo_flow_check.md
```

生成报告位置：`reports/demo_flow_check.md`。

前端构建：

```bash
cd frontend
npm run build
```

## 双端演示路线

Web 演示建议：

1. `/login` 选择角色入口。
2. `/student` 展示学生学习总览。
3. `/student/assistant` 展示画像对话、5 类资源、RAG 引用、防幻觉审核。
4. `/teacher` 展示教师班级概览和教学干预入口。
5. `/dashboard` 展示管理员平台总览。
6. `/resource-generation` 展示资源生成和内容审核。
7. `/agent-workflow` 展示六步 Agent 执行链路。
8. `/demo-status` 展示 Ready 状态。

小程序演示建议：

1. 微信开发者工具导入 `miniprogram` 目录。
2. 展示首页“今日学习”。
3. 展示“资源推荐”中的个性化资源。
4. 展示“AI 辅导”中的 RAG 回答、引用来源、可信度和推荐练习。
5. 展示“学习报告”。

## 快速启动命令

Windows 一键启动：

```bat
start-dev.bat
```

手动启动：

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm run dev
```

## 提交材料说明

比赛提交材料已整理到 `docs/submission`：

- `系统开发说明.md`
- `系统测试说明.md`
- `部署运行说明.md`
- `用户使用手册.md`
- `AI工具使用说明.md`
- `开源依赖与许可证说明.md`
- `答辩演示脚本.md`
- `提交包目录结构.md`

截图清单位于 `docs/screenshots/README.md`。建议最终提交包包含 `backend`、`frontend`、`miniprogram`、`docs`、`docs/course_kb`、`reports`、`README.md`、演示视频和 PPT，不包含 `node_modules`、`dist`、`.env`、本地数据库、上传文件或日志。

## 当前已完成能力

- 三端角色入口与核心路由
- 原生微信小程序学生端体验版
- 对话式学习画像规则生成接口
- 5 类个性化资源包规则生成接口
- 《Python 程序设计》课程知识库示例资料集
- 轻量 RAG 引用问答接口与小程序 fallback 链路
- AI 内容审核 / 防幻觉审核接口与最近记录展示
- Agent 六步执行链路展示
- 学生端课程、路径、答疑、知识库、测验、报告等页面
- 教师端班级概览、课程管理、学生画像、路径任务、测评分析、报告中心
- 管理员端平台总览、用户角色、课程治理、报告审核、知识库运营、日志、设置
- AI 资源生成、Agent 工作流、业务事件日志和报告中心演示闭环
- 统一演示数据初始化脚本
- `/demo-status` 比赛演示状态页
- 一键验收报告输出到 `docs/reports` 和 `reports`

## 后续扩展方向

- 接入真实登录鉴权与角色权限中间件
- 接入真实 LangGraph / LangChain 编排
- 接入真实 RAGFlow、Dify、FastGPT 或生产级向量检索服务
- 扩展独立审计日志表、通知中心、班级学生管理和数据导出
- 增加 Playwright 端到端浏览器自动化测试

## 演示注意事项

- 不展示真实 API Key，不上传敏感学生或教师数据。
- `.env`、数据库文件、上传文件、日志、`node_modules` 和构建产物不应提交到仓库。
- 比赛现场优先运行已验证脚本，不临时大规模重构页面。
