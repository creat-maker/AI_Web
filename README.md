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
# EduMind 赛题关键能力补强说明

当前版本围绕赛题核心要求补齐了低风险可演示能力：

- 对话式学生画像通过多轮自然对话抽取 6 个维度：知识基础、认知风格、学习偏好、易错点、学习进度、情感动机，并保留 current_level、learning_goal、weak_points、learning_preference、diagnosis、strategy 等旧字段兼容。
- 多模态资源包支持 9 类资源：知识讲义、思维导图、练习题、HTML/SVG 动画、视频讲解脚本、语音讲解资源、简易 MP4 视频、代码案例、项目任务。
- HTML/CSS 动画当前可在前端通过 sandbox iframe 预览；MP4 合成为 FFmpeg 可选部署能力，未配置 FFmpeg 时稳定返回 HTML 动画、视频脚本和 TTS 资源，不宣传为完整生产级数字人视频。
- 科大讯飞工具通过环境变量接入，优先支持 TTS；无 Key 时接口返回 `not_configured`，系统继续使用本地智能评测引擎稳定运行。
- 测验提交后返回 `evaluation` 与 `path_adjustment`，前端可展示“测 -> 评 -> 调”的动态学习路径调整结果。
- 内容安全采用“知识库引用 + 本地规则审核 + 可配置 AI 安全扩展”机制，AI 生成内容需经教师或管理员审核后进入正式教学资源。
# EduMind 个性化学习多智能体系统（A3 完整演示版）

EduMind 面向软件杯 A3「个性化学习多智能体系统」赛题，提供学生端、教师端、管理端和微信小程序端的可信个性化学习闭环。当前主线演示为「Python 程序设计 / 循环结构 / 李明」，覆盖画像对话、在线门控 DKVMN 知识追踪、课程约束 RAG、多模态资源生成、测验提交、路径动态调整、教师仲裁、学习报告和治理日志。

## 三端角色

- 学生端：画像构建、学习路径、RAG 答疑、资源预览、章节测验、学习报告。
- 教师端：课程管理、学情分析、资源生成、教师仲裁、报告中心。
- 管理端：系统总览、知识库/RAG、内容审核、Agent 工作流、审计日志、系统状态。
- 小程序端：学生端核心体验的轻量移动入口。

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite，Chroma 可选，JSON/TF-IDF fallback。
- 前端：Vue 3、Vite、TypeScript、ECharts。
- 小程序：微信小程序原生 WXML/WXSS/JS。
- 外部能力：LLM、讯飞 TTS/安全、FFmpeg、SentenceTransformer 均为可选接入，未配置时自动使用本地轻量能力。

## 核心创新落地

- DKVMN：`backend/app/services/dkvmn_tracker.py` 提供 softmax key 寻址、动态 value memory、erase/add 门控写入、掌握度更新、强弱点识别和 6 维画像映射。
- EduLLM：`document_parser.py`、`chunk_strategy.py`、`curriculum_constraint.py`、`embedding_interface.py` 形成课程约束 RAG，`/api/v1/rag/ask` 优先检索已导入课程向量库并返回真实引用、置信度、课程对齐和检索 debug，无命中时降级到课程 JSON。
- FACET：系统采用 12 节点教学智能体治理增强流程，包括 ProfileAgent、KnowledgeAgent、PlannerAgent、ResourcePlannerAgent、ResourceAgent、TutorAgent、EvaluatorAgent、AuditAgent、ComplianceAgent、AuditRetry、TeacherArbitration、ReporterAgent。高风险运行会持久化暂停；教师 approve/revise/reject 后分别进入报告、重生成复审或阻断发布，并通过 `/api/v1/agent-runs`、`/api/v1/audit-logs` 追踪状态。
- 多模态资源：支持讲义、思维导图、练习、HTML 动画、视频脚本、TTS 任务、MP4 可选合成、代码案例、小项目任务。

## 启动方式

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

cd ../frontend
npm install
npm run dev
```

演示数据：

```bash
python scripts/seed_demo_data.py
python scripts/check-demo-ready.py --skip-http
python scripts/eval_retrieval.py
```

## 演示账号

- 学生：李明（基础薄弱 + 代码实操偏好 + 中风险）
- 教师：王老师
- 管理员：demo_admin

## 能力边界与 Fallback

- LLM 未配置时使用本地规则和模板生成。
- 讯飞 TTS/安全 API 未配置时返回文本讲解、任务状态和本地规则审核结果。
- FFmpeg 未安装时降级为 HTML 动画与视频脚本。
- Chroma 不可用时自动使用 JSON/TF-IDF 检索。
- DKVMN 当前实现了在线门控 Key-Value Memory 推理核心，包含 `key_matrix`、softmax attention、按学生持久化的 `value_memory`、erase/add 写门、强弱点识别和画像映射；当前没有论文规模训练数据和预训练 checkpoint，不宣称复现论文指标。
- EduLLM 当前是课程大纲约束 + 轻量语义/规则混合评分 + RAG 引用证据，不是完整教育大模型微调。
- OCR、SentenceTransformer、DKVMN 离线训练与 checkpoint 加载均保留扩展边界，比赛工程默认使用可解释的在线更新模式。

## Docker 启动

演示级容器配置已补齐，保留本地启动方式：

```bash
cp .env.example .env
docker compose up --build
```

访问地址：

- Web 前端：http://localhost:3000
- 后端 API：http://localhost:8000/docs
- Chroma 可选 profile：`docker compose --profile chroma up --build`

常见问题：

- 如果 8000 或 3000 端口被占用，先停止本地 dev server 或修改 `docker-compose.yml` 端口映射。
- SQLite 数据通过 `backend/storage` volume 保留。
- Docker 不可用时仍按上方本地方式启动后端、前端和小程序。

## 小程序后端配置

小程序默认优先访问 `http://127.0.0.1:8000/api/v1`，配置在 `miniprogram/config/api.js`：

- 开发者工具可使用 `127.0.0.1`。
- 真机调试需改成电脑局域网 IP，例如 `http://192.168.1.8:8000/api/v1`，并确认手机与电脑在同一网络。
- `fallbackToDemoData: true` 时，后端不可达会展示“当前为本地示例数据”，页面不白屏。

## CI

`.github/workflows/ci.yml` 已加入基础检查：

- 后端：安装 `backend/requirements.txt`、`python -m compileall backend/app`、`pytest backend/tests`。
- 前端：`npm ci`、`npm run build`。

## Agent 节点口径

系统采用 12 节点教学智能体治理增强流程，包括 ProfileAgent、KnowledgeAgent、PlannerAgent、ResourcePlannerAgent、ResourceAgent、TutorAgent、EvaluatorAgent、AuditAgent、ComplianceAgent、AuditRetry、TeacherArbitration、ReporterAgent。

原始开发方案中的 9+1 是核心教学闭环，当前工程版在其基础上扩展了 ComplianceAgent、AuditRetry、TeacherArbitration 等治理节点，用于满足可信、安全、可追溯要求。当前表述保持比赛工程实现口径，不夸大为真实商业生产系统。
