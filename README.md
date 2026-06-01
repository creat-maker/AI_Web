# EduMind

EduMind 是一个面向比赛演示的三端教育智能体系统。当前版本重点固化“打开即可演示”的闭环：学生端学习闭环、教师端教学干预闭环、管理员端平台治理闭环、AI Agent 工作流展示闭环，以及一键演示状态检查。

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

## 当前已完成能力

- 三端角色入口与核心路由
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
