# EduMind 竞赛级功能增强说明

## 背景

本轮在当前 dev 分支上继续开发，遵循“不重构整个项目、不破坏现有演示流程、不删除已有功能”的约束，围绕三端 Web、小程序和后端补齐智慧教学闭环。

## 竞品借鉴来源

参考平台：

- 智慧树/知到
- 超星学习通/泛雅
- 雨课堂
- 国家智慧教育公共服务平台

借鉴方向：

- 学生端：任务式学习、资源推荐、测验反馈、学习报告。
- 教师端：班级学情、备课出题辅助、风险学生干预。
- 管理端：内容审核、质量评价、平台治理。
- 移动端：轻量任务、资源、练习和报告展示。

## 新增核心闭环

学生画像 -> 知识图谱 -> 资源推荐 -> 智能测评 -> 错因分析 -> 教师干预 -> 平台治理。

闭环解释：

- 学生画像提供基础水平、目标、偏好、薄弱点和风险等级。
- 知识图谱把 Python 程序设计知识点组织成可点击关系图。
- 资源推荐根据薄弱知识点推送讲义、微课、Notebook、练习和项目任务。
- 智能测评通过章节练习生成得分。
- 错因分析按知识点和原因标签输出诊断。
- 教师干预给出风险学生、补救任务、推荐资源和提醒话术。
- 平台治理通过 AI 内容审核和课程质量评价控制发布风险。

## 学生端增强

新增 `/student/knowledge-graph`：

- 使用 ECharts graph 展示 Python 程序设计知识点关系。
- 节点包括变量与数据类型、条件语句、循环结构、函数、列表、字典、文件操作、异常处理。
- 节点状态包括已掌握、学习中、薄弱、未学习。
- 点击节点展示说明、掌握率、推荐资源、关联练习和 AI 学习建议。

增强 `/student/learning-path`：

- 升级为任务式学习路径。
- 支持基础薄弱型、考试冲刺型、项目实践型。
- 每个任务包含目标、知识点、资源、练习、完成条件、预计时间和 AI 建议。

新增 `/student/smart-quiz`：

- 展示章节练习题。
- 提交答案后生成得分、错因分析、薄弱知识点和推荐资源。
- 当前为规则判分和 mock 数据，便于后续替换真实题库。

增强 `/student/assistant`：

- 保持轻量 RAG / 本地知识库逻辑。
- 展示相关知识点、引用、推荐练习和内容审核链路。
- 不引入 LangChain、LangGraph、Chroma、FAISS 等重依赖。

## 教师端增强

新增 `/teacher/ai-workbench`：

- 支持 AI 生成教案、AI 生成测验、AI 生成学情分析。
- 输入课程、章节、学生基础、教学目标。
- 输出教学目标、重难点、课堂活动、随堂测验、课后任务、教学建议。
- 明确生成结果需审核后发布。

增强 `/teacher`：

- 增加班级完成率、平均正确率、学习活跃度。
- 增加薄弱知识点排行。
- 增加风险学生名单和干预建议。

增强 `/profiles`：

- 展示基础水平、学习目标、学习偏好、课程进度、薄弱知识点、错题分布、风险等级和教师干预建议。

增强 `/courses`：

- 展示知识点、资源、题目之间的关联。
- 当前为静态展示，后续可替换为编辑器。

## 管理员端增强

增强 `/dashboard`：

- 增加 AI 问答次数、资源生成次数、测验完成次数、内容审核通过率。
- 增加 AI 能力边界说明。

新增 `/admin/content-review`：

- 展示 AI 生成资源审核列表。
- 字段包括资源标题、资源类型、生成来源、风险标签、审核状态、审核意见。
- 支持模拟通过、驳回、待审核状态。

新增 `/admin/platform-quality`：

- 展示课程完成率、测验均分、资源使用率、薄弱知识点集中度、教师 AI 工具使用次数。

## 小程序端增强

- 首页：今日任务、课程进度、薄弱知识点。
- 路径页：任务式学习路径。
- 资源页：AI 推荐资源包。
- 练习页：测验得分和错因分析。
- 报告页：知识点掌握情况和学习建议。

## 后端接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/v1/knowledge-graph` | GET | 返回课程知识图谱、节点掌握率、推荐资源 |
| `/api/v1/student/learning-tasks` | GET | 返回任务式学习路径 |
| `/api/v1/quiz/chapter` | GET | 返回章节练习题 |
| `/api/v1/quiz/submit` | POST | 提交答案，返回得分、错因分析、薄弱点、推荐资源 |
| `/api/v1/teacher/ai-workbench/generate` | POST | 生成教案、测验或学情分析 |
| `/api/v1/admin/content-review` | GET | 返回 AI 生成内容审核列表 |
| `/api/v1/admin/platform-quality` | GET | 返回平台质量评价统计 |

## AI 能力边界

AI 生成内容仅作为教学辅助。关键教学资源、测评结果、学生画像诊断和教师干预建议必须经教师或管理员审核后使用。演示时应明确说明当前规则生成和 mock 数据不替代真实教学评价。

## 本轮新增/修改文件清单

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

## 启动方式

后端：

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm run dev
```

小程序：

使用微信开发者工具导入 `miniprogram` 目录。

## 比赛演示建议

1. 先讲学生端：知识图谱 -> 学习路径 -> 智能测验 -> 助教答疑 -> 报告。
2. 再讲教师端：班级学情 -> AI 工作台 -> 学生画像 -> 课程关联。
3. 最后讲管理员端：平台总览 -> 内容审核 -> 课程质量评价 -> 能力边界。
4. 移动端用小程序快速展示同一闭环在轻量端的同步。
