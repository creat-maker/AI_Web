# EduMind 方案符合度审计与待办清单

> **明确缺少项 · 可能缺少项 · 已实现项 · 后续优先级**
>
> 适用项目：EduMind / 中国软件杯 A3 方向 / 个性化学习资源与智能学习智能体系统
>
> 审计日期：2026-06-08（v6 更新 - 全量代码逐文件复审，发现小程序/课程知识库已存在）

---

## 审计结论

当前 EduMind 已具备 **Web 三端演示系统** + **微信小程序学生端体验版** + **LangGraph 多智能体工作流** + **Chroma RAG 检索** + **Mock/真实 LLM 双模式** 的完整闭环能力。

**v6 审计发现（此前标记为缺失但实际已存在）：**
- ✅ 微信小程序学生端体验版：`miniprogram/` 目录已存在，含 6 个页面（首页/路径/资源/助教/测验/报告），5 个 tab 页，完整 demoData 支持
- ✅ 课程知识库与样例课程资料集：`docs/course_kb/python_programming.json` 已存在，覆盖 Python 基础语法、函数、文件处理、异常处理、递归和数据结构入门，含章节/知识点/讲义/练习/实验任务
- ✅ 知识图谱/前置关系：`StudentKnowledgeGraph.vue` 已实现 ECharts 力导向图，含节点掌握率/状态/前置关系，`competition_mock_service.py` 提供 `get_knowledge_graph()` API
- ✅ AI 内容审核中心：`AdminContentReview.vue` 已实现审核列表/筛选/通过/驳回操作，`content_review_service.py` 提供风险等级/可信度/引用覆盖/幻觉警告
- ✅ 课程质量评价：`AdminPlatformQuality.vue` 已实现课程完成率/测验均分/资源使用率/教师 AI 使用统计
- ✅ AI 教学工作台：`TeacherAIWorkbench.vue` 已实现教案/测验/学情分析三种 AI 生成模式
- ✅ 轻量 RAG 服务：`lightweight_rag_service.py` 基于 `docs/course_kb/python_programming.json` 实现关键词检索 + TF-IDF 评分
- ✅ WebSocket 实时通信：`user_profile_ws.py` 已实现 WebSocket 连接管理

**v5 已补齐的 P0/P1 项：**
- ✅ 对话式学习画像构建：profile_dialog_service 实现多轮自然对话增量抽取 6 维画像（start/continue/finish/save 四个 API）
- ✅ 5 类资源生成：新增 mindmap（思维导图）为第 5 类资源
- ✅ RAG 引用溯源与可信度评分：TutorAgent/MockLLM 返回 per-citation confidence + confidence_level + confidence_breakdown
- ✅ 防幻觉审核中心：ReportCenter.vue 展示 evidence_chain + citation_snippets + quality_score
- ✅ 资源推荐理由：学习路径每阶段 + 资源生成含 recommend_reason
- ✅ 学习路径动态调整：测验提交后自动触发路径重规划 + /adjust API + adjustment_log

**代码审查确认的核心实现：**
- ✅ LangGraph 多智能体：ProfileAgent → PlannerAgent → ResourceAgent → TutorAgent → EvaluatorAgent → ReporterAgent（[graph.py](file:///Users/xing/Desktop/EduMind/backend/app/agents/graph.py)）
- ✅ RAG 检索：Chroma 向量检索 + HashEmbedding + JSON fallback 双模式 + 轻量 RAG 服务（[vector_store.py](file:///Users/xing/Desktop/EduMind/backend/app/rag/vector_store.py) + [lightweight_rag_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/lightweight_rag_service.py)）
- ✅ Mock/真实 LLM：DeepSeek / 通义千问 / Mock 三模式自动切换，系统提示含防幻觉指令（[llm_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/llm_service.py)）
- ✅ Agent 执行链路：步骤日志、耗时统计、状态追踪（[agent_workflow.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/agent_workflow.py)）
- ✅ 知识库：支持 PDF/PPT/TXT/MD 上传、解析、分块、向量化（[knowledge_base.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/knowledge_base.py)）
- ✅ 报告生成：python-docx 生成 Word 学习报告，含证据链/引用片段/质量评分（[reports.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/reports.py)）
- ✅ 智能答疑引用：TutorAgent 返回 source_file + content + confidence 引用（[mock_llm.py](file:///Users/xing/Desktop/EduMind/backend/app/services/mock_llm.py)）
- ✅ Demo 状态与验收：能力清单、就绪检查、关键事件追踪、通过率统计（[demo_status.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/demo_status.py)）
- ✅ 微信小程序：6 页面 + 5 tab + demoData（[miniprogram/](file:///Users/xing/Desktop/EduMind/miniprogram/)）
- ✅ 课程知识库：Python 程序设计完整课程资料（[python_programming.json](file:///Users/xing/Desktop/EduMind/docs/course_kb/python_programming.json)）

对照软件杯方案，仍缺少或需要核验以下关键项：

- ⚠️ 文本分块质量（[text_splitter.py](file:///Users/xing/Desktop/EduMind/backend/app/rag/text_splitter.py) 仅按字符数切分，无语义分块）
- ⚠️ Embedding 质量（HashEmbedding 基于 MD5 哈希，非语义向量，检索质量有限）
- ⚠️ ProfileDialog 路由未注册（`/student/profile-dialog` 在 roles.ts 中有入口但 router/index.ts 缺少路由定义）
- ❌ 正式提交材料（PPT、视频、开发说明等）

---

## 1. 审计依据与范围

| 依据 | 内容 |
|------|------|
| 依据一 | 当前代码库实际实现：FastAPI 后端 + Vue3 前端 + 微信小程序 + LangGraph Agent + Chroma RAG |
| 依据二 | 《EduMind 软件杯开发方案》提出 Web 主系统 + 微信小程序体验版，多端共享后端 API |
| 依据三 | 《EduMind 软件杯赛题痛点分析与系统方案》强调对话式画像、多智能体协同、至少 5 类资源生成、学习路径、智能辅导、学习效果评估、防幻觉 |
| 依据四 | 软件杯赛题原文要求构建高等教育个性化学习资源体系与智能学习智能体系统，并提交源码、数据集/配置、PPT、7 分钟演示视频、配套文档 |

**分类标准：**

| 分类 | 判断标准 | 处理方式 |
|------|----------|----------|
| ✅ 已实现 | 代码库中已存在真实实现，且与方案模块对应 | 保留、验收、稳定版本打 tag |
| ❌ 明确缺少 | 方案/赛题要求中明确需要，但代码库中未找到 | 列为 P0/P1 待办 |
| ⚠️ 部分实现 | 已有基础框架或 mock，但缺少真实闭环证据 | 代码审计确认后补齐 |
| 🔜 暂缓 | 能增强但不是初赛稳定演示必须，且会显著增加复杂度 | 写入后续规划 |

---

## 2. 当前已实现项清单

> **总体判断**：Web 三端 + 微信小程序 + LangGraph 多智能体 + RAG 检索 + Mock/真实 LLM 双模式 + 对话式画像 + 动态路径调整 + 防幻觉审核 + 课程知识库，核心闭环已完整。

| 模块 | 已实现内容 | 代码位置 | 状态 | 后续建议 |
|------|-----------|----------|------|----------|
| 统一 UI 与布局 | AppLayout、AppSidebar、AppHeader、DataCard、StatCard、StatusBadge 等公共组件 | [AppLayout.vue](file:///Users/xing/Desktop/EduMind/frontend/src/components/AppLayout.vue) | ✅ 已完成 | — |
| 登录页与三角色入口 | `/login` 页面，学员/教师/管理员入口分别进入 `/student` `/teacher` `/dashboard` | [Login.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/Login.vue) | ✅ 已完成 | — |
| 三角色路由拆分 | 学生端 `/student/*`，教师端 `/teacher`，管理员端 `/dashboard` `/admin/*` | [router/index.ts](file:///Users/xing/Desktop/EduMind/frontend/src/router/index.ts) | ✅ 已完成 | — |
| 角色权限配置 | `useRole` composable + `roles.ts` 角色菜单、路由权限 | [useRole.ts](file:///Users/xing/Desktop/EduMind/frontend/src/composables/useRole.ts) | ✅ 已完成 | — |
| 学生端 Web 页面 | 学习总览、课程、学习路径、知识图谱、任务、智能答疑、知识库、测验、报告、成就、积分、笔记、小组（13 个页面） | [StudentHome.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/StudentHome.vue) 等 | ✅ 已完成 | — |
| 教师端 Web 页面 | 班级概览、AI 教学工作台、课程管理、学生画像、学习路径、测评分析、报告中心 | [TeacherHome.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/TeacherHome.vue) + [TeacherAIWorkbench.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/TeacherAIWorkbench.vue) | ✅ 已完成 | — |
| 管理员端 Web 页面 | 平台总览、用户与角色、课程治理、资源生成、Agent 工作流、报告审核、内容审核、课程质量评价、知识库运营、日志、系统设置 | [Dashboard.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/Dashboard.vue) 等 | ✅ 已完成 | — |
| 微信小程序学生端 | 7 页面（首页/路径/资源/助教/测验/报告/画像构建），5 tab，demoData，request 工具，对话式画像构建 | [miniprogram/](file:///Users/xing/Desktop/EduMind/miniprogram/) | ✅ 已完成 | — |
| Demo 状态页 | `/demo-status` 前后端，展示 Ready、通过率、三端路线和关键能力 | [DemoStatus.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/DemoStatus.vue) + [demo_status.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/demo_status.py) | ✅ 已完成 | — |
| 统一演示数据 | 张三、李四、王五；王老师、陈老师、张老师；四门课程；两个班级 | [seed_demo_data.py](file:///Users/xing/Desktop/EduMind/scripts/seed_demo_data.py) | ✅ 已完成 | — |
| 一键验收脚本 | `seed-demo-data`、`check-demo-ready`、`e2e_demo_flow_check` | [scripts/](file:///Users/xing/Desktop/EduMind/scripts/) | ✅ 已完成 | — |
| 学习行为数据采集 | 业务事件记录（9 类事件） | [events.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/events.py) | ✅ 已完成 | — |
| 日志管理 | QA、文档上传、Agent、报告、错误等多类型日志 | [logs.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/logs.py) | ✅ 已完成 | — |
| 系统设置 | 运行模式、fallback 数据源和能力边界 | [system_settings.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/system_settings.py) | ✅ 已完成 | — |
| 能力边界说明 | `/capability-boundary` 页面 | [CapabilityBoundary.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/CapabilityBoundary.vue) | ✅ 已完成 | — |
| 课程管理 CRUD | 创建、编辑、删除课程 | [courses.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/courses.py) | ✅ 已完成 | — |
| 课程知识库与资料集 | Python 程序设计完整课程：6 章、知识点、讲义、练习、实验任务 | [python_programming.json](file:///Users/xing/Desktop/EduMind/docs/course_kb/python_programming.json) | ✅ 已完成 | 可补更多课程 |
| 知识库上传与解析 | 支持 PDF/PPT/TXT/MD 上传、解析、分块、Chroma 向量化 | [knowledge_base.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/knowledge_base.py) | ✅ 已完成 | — |
| RAG 检索 | Chroma 向量检索 + HashEmbedding + JSON fallback + 轻量 RAG（基于课程知识库关键词+TF-IDF） | [vector_store.py](file:///Users/xing/Desktop/EduMind/backend/app/rag/vector_store.py) + [lightweight_rag_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/lightweight_rag_service.py) | ⚠️ 演示级 | HashEmbedding 非语义向量；文本分块仅按字符数切分 |
| 学生画像生成 | 问卷式 + 对话式画像构建（6 维增量抽取），前端 ProfileDialog.vue 完整对话界面 + 维度进度面板 | [profile_dialog_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/profile_dialog_service.py) + [ProfileDialog.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/ProfileDialog.vue) | ✅ 已完成 | ⚠️ 路由 `/student/profile-dialog` 未注册到 router |
| 学习路径规划 | 3 阶段路径 + recommend_reason + 动态调整（测验后自动触发 + 手动调整）+ adjustment_log | [learning_path_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/learning_path_service.py) | ✅ 已完成 | — |
| 资源生成 | 5 类资源：handout/example/quiz/task/mindmap，含 recommend_reason | [mock_llm.py](file:///Users/xing/Desktop/EduMind/backend/app/services/mock_llm.py) | ✅ 已完成 | — |
| 智能答疑 | RAG 问答 + per-citation confidence + confidence_level + confidence_breakdown；前端 TutorChat 展示可信度徽章/进度条/引用详情 | [TutorChat.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/TutorChat.vue) | ✅ 已完成 | — |
| 测验评价 | 生成测验 → 提交答案 → 评分反馈 → 自动触发路径调整 | [quiz_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/quiz_service.py) | ✅ 已完成 | — |
| Word 报告导出 | python-docx + evidence_chain + citation_snippets + quality_score；前端 ReportCenter 展示 | [ReportCenter.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/ReportCenter.vue) | ✅ 已完成 | — |
| 知识图谱 | ECharts 力导向图，含节点掌握率/状态/前置关系/AI 建议 | [StudentKnowledgeGraph.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/StudentKnowledgeGraph.vue) | ✅ 已完成 | — |
| AI 内容审核中心 | 审核列表/筛选/通过/驳回；风险等级/可信度/引用覆盖/幻觉警告 | [AdminContentReview.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/AdminContentReview.vue) + [content_review_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/content_review_service.py) | ✅ 已完成 | — |
| 课程质量评价 | 课程完成率/测验均分/资源使用率/教师 AI 使用统计 | [AdminPlatformQuality.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/AdminPlatformQuality.vue) | ✅ 已完成 | — |
| AI 教学工作台 | 教案/测验/学情分析三种 AI 生成模式 | [TeacherAIWorkbench.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/TeacherAIWorkbench.vue) | ✅ 已完成 | — |
| LangGraph 多智能体 | 6 Agent 顺序工作流：Profile→Planner→Resource→Tutor→Evaluator→Reporter | [graph.py](file:///Users/xing/Desktop/EduMind/backend/app/agents/graph.py) | ✅ 已完成 | — |
| Agent 执行链路 | 步骤日志、耗时统计、状态追踪 | [agent_workflow.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/agent_workflow.py) | ✅ 已完成 | — |
| Mock/真实 LLM 双模式 | DeepSeek / 通义千问 / Mock 三模式自动切换 | [llm_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/llm_service.py) | ✅ 已完成 | — |
| WebSocket 实时通信 | WebSocket 连接管理 + 广播 | [user_profile_ws.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/user_profile_ws.py) | ✅ 已完成 | — |
| Dashboard 统计 | 课程/画像/资源/测验/报告/Agent 运行数 + 7 天趋势 | [Dashboard.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/Dashboard.vue) | ✅ 已完成 | — |

---

## 3. 明确缺少项清单

> 以下项目是对照方案和赛题后，代码库中没有找到对应实现的内容。按优先级排列。

### P0 — 赛题硬要求，必须补齐

| # | 缺少项 | 判断依据 | 当前状态 | 建议补法 |
|---|--------|----------|----------|----------|
| ~~1~~ | ~~**微信小程序学生端体验版**~~ | ~~方案明确建议 Web 主系统 + 微信小程序体验版~~ | ✅ 已存在 | `miniprogram/` 目录已含 6 页面 + 5 tab + demoData |
| ~~2~~ | ~~**对话式学习画像构建**~~ | ~~赛题要求自然语言对话构建不少于 6 维画像~~ | ✅ 已补齐 | profile_dialog_service.py 已实现多轮对话式画像构建 |
| ~~3~~ | ~~**至少 5 类个性化资源生成**~~ | ~~赛题硬要求~~ | ✅ 已补齐 | MockLLM 已新增 mindmap 为第 5 类资源 |
| ~~4~~ | ~~**课程知识库与样例课程资料集**~~ | ~~赛题要求自行构造至少一门完整课程知识库~~ | ✅ 已存在 | `docs/course_kb/python_programming.json` 已含完整 Python 课程 |
| ~~5~~ | ~~**RAG 引用溯源与可信度评分**~~ | ~~防幻觉需要引用片段、来源文件、可信度~~ | ✅ 已补齐 | TutorAgent/MockLLM 已返回 confidence + confidence_level |
| ~~6~~ | ~~**防幻觉审核中心/审核记录**~~ | ~~赛题要求防幻觉与内容安全过滤~~ | ✅ 已补齐 | ReportCenter + AdminContentReview 已展示审核功能 |

### P1 — 重要但非硬性截止

| # | 缺少项 | 判断依据 | 当前状态 | 建议补法 |
|---|--------|----------|----------|----------|
| ~~7~~ | ~~**资源推荐理由**~~ | ~~个性化系统必须能解释"为什么推荐"~~ | ✅ 已补齐 | recommend_reason 已在路径/资源中实现 |
| ~~8~~ | ~~**学习路径动态调整**~~ | ~~路径生成后无后续触发更新机制~~ | ✅ 已补齐 | 测验后自动触发 + /adjust API + adjustment_log |
| 9 | **ProfileDialog 路由注册** | `roles.ts` 中有 `/student/profile-dialog` 入口，但 `router/index.ts` 缺少路由定义，点击会 404 | ⚠️ 路由缺失 | 在 router/index.ts 添加 `{ path: '/student/profile-dialog', name: 'ProfileDialog', component: () => import('../views/ProfileDialog.vue') }` |
| 10 | **正式文档包** | 赛题要求系统开发说明、测试说明、部署说明等 | ⚠️ 部分文档已有 | 补齐：系统开发说明、测试说明、部署说明、AI 工具说明、开源协议说明、用户手册 |
| 11 | **演示 PPT 与 7 分钟视频** | 赛题明确提交 PPT 和 7 分钟以内演示视频 | ❌ 不存在 | 制作 PPT；录制固定三端路线 + 小程序 + demo-status + Agent |
| 12 | **提交包目录** | 方案建议整理完整提交目录 | ❌ 不存在 | 整理 `EduMind_Submission` 目录 |

### P2 — 可增强项

| # | 缺少项 | 判断依据 | 当前状态 | 建议补法 |
|---|--------|----------|----------|----------|
| 13 | **小程序 profile-dialog 页面** | 小程序端缺少对话式画像构建页面 | ✅ 已补齐 | miniprogram/pages/profile-dialog/ 已实现对话式画像构建，含6维进度展示、后端/离线双模式、首页入口 |
| 14 | **语义文本分块** | text_splitter 仅按 800 字符切分，无语义分块 | ⚠️ 演示级 | 后续可引入 markdown header splitting 或递归字符分块 |
| 15 | **语义 Embedding** | HashEmbedding 基于 MD5 哈希，非语义向量 | ⚠️ 演示级 | 后续可替换为 bge-m3 等语义 embedding 模型 |
| 16 | **真实登录鉴权** | 当前为 Demo 角色入口，无 JWT/auth 中间件 | ⚠️ Demo 级 | 初赛可接受；后续扩展真实鉴权 |
| 17 | **生成进度追踪/流式输出** | AgentWorkflow 页面已有步骤条，但无真实 SSE | ⚠️ 部分实现 | 可用步骤条模拟进度；真实 SSE 后续做 |
| 18 | **错题本** | 测验有在线作答，但无错题本功能 | ⚠️ 缺失 | 可在 StudentSmartQuiz 或 StudentExamResult 中增加错题本 |
| 19 | **截图与演示素材** | 未整理 screenshots 文件夹 | ❌ 不存在 | 导出关键页面截图 |

---

## 4. 可能缺少 / 需代码核验项

> 这些内容不是一定没有，而是当前代码无法证明已经真实实现。需进一步确认。

| # | 可能缺少项 | 核验原因 | 代码审计结果 | 处理建议 |
|---|-----------|----------|-------------|----------|
| 1 | **三角色路由拆分** | 已有 `/student/*` `/teacher` `/admin/*` 完整路由 | ✅ 已实现 | 确认各角色菜单不再跨角色切换 |
| 2 | **Demo 状态页** | `/demo-status` 前后端已实现 | ✅ 已实现 | 保持为答辩入口 |
| 3 | **一键验收脚本** | `seed-demo-data` `check-demo-ready` `e2e_demo_flow_check` 已实现 | ✅ 已实现 | 每次提交后必须重跑 |
| 4 | **学习行为数据采集** | `events.py` 已实现 9 类事件 | ✅ 已实现 | — |
| 5 | **测验在线作答与错题本** | `QuizEvaluate` + `StudentExamResult` + `StudentSmartQuiz` 已有在线作答 | ✅ 已实现 | 可增加错题本功能 |
| 6 | **知识点图谱/前置关系** | `StudentKnowledgeGraph.vue` 已实现 ECharts 力导向图 | ✅ 已实现 | — |
| 7 | **教师资源审核权限** | `AdminReports.vue` + `AdminContentReview.vue` 已实现 | ✅ 已实现 | — |
| 8 | **开源协议与 AI Coding 使用说明** | `CapabilityBoundary.vue` + `demo_status.py` 已实现 | ✅ 已实现 | 可补充独立文档 |
| 9 | **部署说明** | `.env.example` + `start-dev.bat` + `stop-dev.bat` 已有 | ✅ 已实现 | 可补充生产部署说明 |
| 10 | **旧页面/未跟踪文件清理** | `legacy/` 目录存在大量旧代码 | ⚠️ 已隔离 | 确认 `.gitignore` 覆盖，提交时排除 |
| 11 | **移动端响应式** | Web 页面多为桌面布局 | ⚠️ 桌面优先 | Web 保持桌面演示；小程序负责移动端 |
| 12 | **接口契约一致性** | 前端 mock 与后端可能字段不一致 | ⚠️ 需核验 | 做 API schema 文档或字段映射表 |
| 13 | **测试覆盖** | `check-demo-ready` 验收脚本已有，但无单元测试 | ⚠️ 部分覆盖 | 保留 check-demo-ready 作为核心验收 |
| 14 | **LLM 防幻觉系统提示** | `llm_service.py` 系统提示含"不要编造不存在的课程资料引用" | ✅ 已实现 | 可增强为更细粒度的约束 |

---

## 5. 暂缓项 / 不建议现在强做

| 事项 | 不建议现在做的原因 | 推荐表述 |
|------|-------------------|----------|
| 完整 LangChain / LangGraph 接入 | 已接入 LangGraph，6 Agent 顺序编排已实现；复杂状态图调试和现场稳定性有风险 | 当前已接入 LangGraph，后续可优化为条件分支和循环状态图 |
| 真实向量数据库全量接入 | Chroma 已接入，但 HashEmbedding 为演示级 | 当前使用 HashEmbedding + JSON fallback，后续可替换为 bge-m3 等语义 embedding 模型 |
| 正式上线微信小程序 | 注册/审核/备案不确定，初赛不要求正式上线 | 提供开发版/体验版源码、运行说明和二维码 |
| 复杂权限系统 | RBAC、后端鉴权、权限矩阵会拖慢演示版本 | 当前 Demo 角色入口，后续生产化补强 |
| 真实多模态视频生成 | 生成视频成本高、时间不稳定、依赖外部模型 | 先生成视频脚本、分镜、旁白和画面提示词 |
| 完整 Docker/云部署 | 部署很加分但不是当前代码闭环的第一问题 | 若时间充足再补 `docker-compose` 和服务器演示地址 |
| 语义文本分块 | 当前 text_splitter 按 800 字符切分，对结构化文档效果不佳 | 后续可引入 markdown header splitting 或递归字符分块 |

---

## 6. 按优先级的下一步开发路线

| 阶段 | 优先级 | 任务 | 目标 | 验收标准 |
|------|--------|------|------|----------|
| 第九阶段 | P1 | 修复 ProfileDialog 路由注册 | 确保 `/student/profile-dialog` 可访问 | 点击侧边栏"画像构建"可正常打开对话式画像页面 |
| 第十阶段 | P1 | 正式文档包 | 完成赛题要求的配套文档 | 系统开发说明、测试说明、部署说明、AI 工具说明、开源协议说明、用户手册 |
| 第十一阶段 | P1 | 演示 PPT 与 7 分钟视频 | 完成初赛提交材料 | PPT、7 分钟视频（Web 三端 + 小程序 + demo-status + Agent） |
| 第十二阶段 | P1 | 提交包目录整理 | 整理完整提交目录 | `EduMind_Submission` 目录结构齐全 |
| 第十三阶段 | P2 | 小程序 profile-dialog 页面 | 小程序端支持对话式画像构建 | 小程序中可进入画像对话页面 |
| 第十四阶段 | P2 | 错题本功能 | 测验后可查看错题和推荐练习 | StudentSmartQuiz 页面有错题本 tab |

---

## 7. 最小补齐方案（时间紧时只做这些）

- **路由修复**：在 router/index.ts 添加 ProfileDialog 路由（1 行代码）
- **文档**：系统开发说明 + 测试说明 + 部署说明 + AI 工具说明（4 份文档）
- **PPT**：10-15 页，覆盖方案/架构/核心功能/演示路线
- **视频**：录制一条固定路线（Web 三端 + 小程序 + demo-status + Agent），7 分钟以内
- **提交包**：整理 `EduMind_Submission` 目录，含源码/数据集/文档/PPT/视频

---

## 8. 审计提示词（供后续复审使用）

```
请基于当前 EduMind 项目做一次"方案符合度补齐审计"，先不要修改代码。

对照软件杯赛题和当前项目方案，逐项检查当前代码是否真实具备以下能力：
1. 小程序学生端体验版
2. 对话式学习画像构建
3. 至少 5 类个性化资源生成
4. 课程知识库与完整样例课程资料集
5. RAG 检索与引用来源
6. 防幻觉审核与可信度评分
7. 多 Agent 编排与执行日志
8. 个性化学习路径动态调整
9. 学习效果评估与报告生成
10. PPT、视频、开发说明、测试说明、部署说明、AI 工具说明
11. 提交包目录结构

请输出：
- 已完成项
- 部分完成项
- 未完成项
- 每个缺口对应的文件/页面/接口
- 是否影响初赛提交
- 修复优先级 P0/P1/P2
- 下一阶段最应该做的 5 个任务

不要新增文件，不要改代码，不要安装依赖。
```

---

## 9. 最终判断

| 维度 | 当前判断 | 说明 |
|------|----------|------|
| 产品形态 | ✅ 较好 | Web 三端 + 微信小程序完整；登录入口、角色路由、Demo 状态页、验收脚本均已就位 |
| 赛题核心功能 | ✅ 基本符合 | 对话式画像 ✅ / 5 类资源 ✅ / 课程知识库 ✅ / RAG 引用+可信度 ✅ / 防幻觉审核 ✅ / 动态路径 ✅ / 知识图谱 ✅ / AI 教学工作台 ✅ |
| 工程完整性 | ✅ 较好 | 有前后端、小程序、统一数据、演示数据脚本、验收脚本、LangGraph Agent、Chroma RAG、Mock/真实双模式 |
| 比赛展示效果 | ✅ 较好 | 登录页、三端路由、小程序、Demo 状态页、Agent 工作流、知识图谱已能支撑讲解；还需 PPT/视频/截图 |
| 技术深度 | ⚠️ 中等偏上 | Agent/RAG 已有基础实现；HashEmbedding 为演示级；报告 API 证据链设计较完善；LLM 系统提示含防幻觉指令 |
| 提交准备度 | ⚠️ 部分完成 | 正式文档、PPT、视频、提交包还需整理；ProfileDialog 路由需修复 |
