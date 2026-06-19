# EduMind

EduMind 是基于大模型的“一人一堂”个性化资源生成与学习多智能体系统，包含 Web 学生端、教师端、管理员端、原生微信小程序学生端和 FastAPI 后端。本轮在当前 dev 分支上做局部增强，不重构项目、不删除原有演示入口，主演示课程统一为《Python 程序设计》，主演示章节为“循环结构”，主演示学生为“李明”。

## 竞品借鉴

本轮功能设计参考智慧树/知到、超星学习通/泛雅、雨课堂、国家智慧教育公共服务平台等主流智慧教学平台：

- 学生端强调课程进度、任务路径、资源推荐和练后反馈。
- 教师端强调班级学情、风险学生识别、备课出题辅助和干预闭环。
- 管理员端强调 AI 内容审核、课程质量评价和平台治理指标。
- 小程序端保持轻量，服务移动端快速查看任务、资源、练习和报告。

## 核心闭环

本轮新增和强化的演示闭环：

1. 学生画像：基础水平、学习目标、学习偏好、薄弱点、错题分布和风险等级。
2. 知识图谱：Python 程序设计知识点关系、掌握状态、点击诊断。
3. 资源推荐：根据薄弱知识点推荐讲义、微课、Notebook、练习和项目任务。
4. 智能测评：章节练习提交后即时判分。
5. 错因分析：按知识点和错因标签生成诊断。
6. 教师干预：班级学情、风险学生、补救任务、提醒话术。
7. 平台治理：AI 内容审核、课程质量评价、AI 能力边界说明。

## 新增 Web 演示入口

学生端：

- `/student/knowledge-graph`：课程知识图谱。
- `/student/learning-path`：任务式学习路径。
- `/student/smart-quiz`：智能测验与练后分析。
- `/student/assistant`：保留轻量 RAG / 本地知识库答疑链路。

教师端：

- `/teacher/ai-workbench`：AI 教学工作台。
- `/teacher`：增强班级学情。
- `/profiles`：增强学生画像。
- `/courses`：增强课程知识点、资源、题目关联。

管理员端：

- `/dashboard`：增强平台 AI 治理指标。
- `/admin/content-review`：AI 内容审核中心。
- `/admin/platform-quality`：课程质量评价。

## 新增后端接口

- `GET /api/v1/knowledge-graph`
- `GET /api/v1/student/learning-tasks`
- `GET /api/v1/quiz/chapter`
- `POST /api/v1/quiz/submit`
- `POST /api/v1/teacher/ai-workbench/generate`
- `GET /api/v1/admin/content-review`
- `GET /api/v1/admin/platform-quality`

接口当前使用集中 mock 数据，响应结构稳定，字段语义明确，后续可替换为数据库、知识追踪模型或真实大模型 API。

## 小程序增强

小程序位于 `miniprogram`，仍使用原生微信小程序结构，不引入复杂依赖。

- 首页展示今日任务、课程进度、薄弱知识点。
- 学习路径页展示任务式路径。
- 资源页展示 AI 推荐资源包。
- 练习页展示测验得分和错因分析。
- 报告页展示知识点掌握情况和学习建议。

## AI 能力边界

AI 生成内容仅作为教学辅助。关键教学资源、测评结论、学生画像诊断和教师干预建议必须经教师或管理员审核后使用，不直接替代教师评价和平台治理决策。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Vue Router、ECharts。
- 后端：FastAPI、SQLAlchemy、Pydantic。
- 小程序：原生微信小程序。
- 数据：SQLite 演示数据、本地 mock、课程知识库 JSON。
- AI 演示：规则生成、轻量 RAG、本地知识库、内容审核 mock，不新增 LangChain、LangGraph、Chroma、FAISS 等重依赖。

## 启动方式

后端：

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

前端构建：

```bash
cd frontend
npm run build
```

小程序：

1. 打开微信开发者工具。
2. 导入 `miniprogram` 目录。
3. AppID 可使用测试号或无 AppID 模式。

Windows 一键脚本：

```bat
start-dev.bat
stop-dev.bat
seed-demo-data.bat
check-demo-ready.bat
```

## 比赛演示路线

学生端：

1. `/student` 查看今日任务和学习概览。
2. `/student/knowledge-graph` 点击薄弱知识点，展示资源、练习和 AI 建议。
3. `/student/learning-path` 切换三类画像路径。
4. `/student/smart-quiz` 提交章节练习，展示得分和错因分析。
5. `/student/assistant` 展示知识点绑定答疑和推荐练习。
6. `/student/reports` 查看学习报告。

教师端：

1. `/teacher` 展示班级完成率、正确率、活跃度、薄弱点排行和风险学生。
2. `/teacher/ai-workbench` 生成教案、测验或学情分析。
3. `/profiles` 查看学生画像和干预建议。
4. `/courses` 展示知识点、资源、题目关联。
5. `/teacher-analysis` 查看测评分析。

管理员端：

1. `/dashboard` 展示平台治理指标和 AI 能力边界。
2. `/admin/content-review` 模拟 AI 生成内容通过、驳回、待审核。
3. `/admin/platform-quality` 展示课程质量评价。
4. `/logs` 查看运行日志。
5. `/demo-status` 查看演示状态。

小程序端：

1. 首页：今日任务、课程进度、薄弱点。
2. 路径：任务式学习路径。
3. 资源：AI 推荐资源包。
4. 练习：测验得分和错因分析。
5. 报告：知识点掌握情况和学习建议。

## 本轮新增/修改文件

后端：

- `backend/app/services/competition_mock_service.py`
- `backend/app/api/routers/competition.py`
- `backend/app/main.py`

前端：

- `frontend/src/api/mocks/competitionData.ts`
- `frontend/src/views/StudentKnowledgeGraph.vue`
- `frontend/src/views/StudentSmartQuiz.vue`
- `frontend/src/views/TeacherAIWorkbench.vue`
- `frontend/src/views/AdminContentReview.vue`
- `frontend/src/views/AdminPlatformQuality.vue`
- `frontend/src/views/StudentLearningPath.vue`
- `frontend/src/views/TeacherHome.vue`
- `frontend/src/views/StudentProfile.vue`
- `frontend/src/views/CourseManage.vue`
- `frontend/src/views/Dashboard.vue`
- `frontend/src/router/index.ts`
- `frontend/src/config/roles.ts`

小程序：

- `miniprogram/utils/demoData.js`
- `miniprogram/app.json`
- `miniprogram/pages/home/index.wxml`
- `miniprogram/pages/path/index.wxml`
- `miniprogram/pages/path/index.wxss`
- `miniprogram/pages/resources/index.wxml`
- `miniprogram/pages/quiz/index.js`
- `miniprogram/pages/quiz/index.wxml`
- `miniprogram/pages/quiz/index.wxss`
- `miniprogram/pages/report/index.js`
- `miniprogram/pages/report/index.wxml`

文档：

- `README.md`
- `docs/demo-checklist.md`
- `docs/reports/demo_ready_check.md`
- `docs/competition-enhancement.md`

## 验收命令

```bash
git status --short
```

```bash
cd backend
python -m compileall app
```

```bash
cd frontend
npm run build
```

```bash
python scripts/check-demo-ready.py
```
