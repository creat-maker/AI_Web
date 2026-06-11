# 论文依据到系统功能差距分析

> 分析范围：基于 `docs/research_mapping.md`、`docs/research_summary_table.md`、`docs/research_to_feature_mapping.md`，并阅读当前 EduMind 前后端代码。本文只做资料和代码阅读结论，不包含业务代码修改。

## 总体结论

当前 EduMind 已经具备“演示级闭环”：学生画像、学习路径、资源生成、课程知识库问答、Agent 工作流、教师分析、管理员内容审核等页面和接口都能展示核心概念。但从论文依据要求的“个体建模 + 动态推荐 + RAG/KG 可信答疑 + 多智能体协作 + 教师诊断 + 内容治理”来看，系统仍主要停留在 demo/fallback、规则估计和显式 `student_profile_id` 传参阶段，尚未形成以登录用户 `user_id` 为主线的真实个性化数据闭环。

## 能力差距清单

| 能力 | 当前实现状态 | 相关代码文件 | 缺口说明 | 对应论文依据 | 建议修改方案 | 风险等级 |
|---|---|---|---|---|---|---|
| 用户登录后绑定 `user_id` | 未实现 | `frontend/src/views/Login.vue`、`frontend/src/composables/useRole.ts`、`frontend/src/api/client.ts`、`backend/app/main.py`、`backend/app/models/a3.py` | 登录页只是选择学生/教师/管理员演示角色；前端仅把角色写入 `localStorage` 的 `edumind.demoRole`；API 客户端不携带 token 或用户信息；后端无 User/Account 模型、无认证路由、无 `current_user` 依赖；系统日志默认用户仍是 `demo_teacher`。 | `2402.01666v2.pdf`、肖君等在线学习者画像、`3766918.3766987.pdf` 都强调学生建模和个性化服务必须以可识别学习者为对象。 | 新增用户表、角色表或简化账户表；实现登录接口与 JWT/session；前端保存 token 并在 `api/client.ts` 注入 Authorization；后端路由通过 `current_user` 获取 `user_id`；为演示账号做种子数据，不再把角色切换等同登录。 | 高 |
| 不同用户有不同学生画像 | 部分实现 | `backend/app/models/a3.py`、`backend/app/api/routers/profiles.py`、`backend/app/services/profile_service.py`、`backend/app/api/routers/profile_dialog.py`、`frontend/src/views/StudentProfile.vue` | `StudentProfile` 可存多条画像，但只有 `student_name`、`course_id`、`profile_json`，没有 `user_id`；画像列表接口默认返回全局画像；对话画像和学生端存在 `demo-student`、张三等演示 ID；无法保证不同登录用户只能读取自己的画像。 | 肖君等 ODAS 画像、师亚飞等学习画像路径推荐、Solari 等兴趣画像、`3690931.3690992.pdf`。 | 给 `StudentProfile` 增加 `user_id` 外键和唯一约束策略，例如 `user_id + course_id`；画像查询默认按当前用户过滤，教师端按班级/课程授权查看；把对话画像产物写回当前用户画像；迁移 demo 数据到明确 demo 用户。 | 高 |
| 学生画像影响学习路径推荐 | 部分实现 | `backend/app/services/learning_path_service.py`、`backend/app/api/routers/learning_paths.py`、`backend/app/services/mock_llm.py`、`backend/app/services/quiz_service.py`、`frontend/src/views/LearningPath.vue` | 后端生成路径时会读取 `profile.profile_json`，mock LLM 会使用 `learning_goal` 和 `weak_points` 写推荐理由；测评提交后也能按薄弱点变化触发路径调整。但入口依赖显式 `profile_id`，未绑定当前登录用户；路径主要是规则/LLM prompt 生成，未接课程知识图谱、知识追踪或可解释路径约束。 | 师亚飞等“学习元”动态路径、刘昕等“一人一堂”、`2502.15709v2.pdf` TutorLLM、`electronics-15-00238.pdf` KG 路径综述、`3745238.3745265.pdf`。 | 以当前用户画像作为路径默认输入；引入知识点掌握度、前后测、答疑日志和资源完成情况；用课程知识图谱约束路径节点与先修关系；保存每次路径推荐理由、触发事件、预期指标和实际学习效果。 | 中 |
| 学生画像影响资源生成/推荐 | 部分实现 | `backend/app/api/routers/resources.py`、`backend/app/services/mock_llm.py`、`backend/app/services/personalization_service.py`、`frontend/src/views/ResourceGenerate.vue`、`miniprogram/pages/resources/index.js` | `/resources/generate` 在传入 `student_profile_id` 时会读取画像和最新路径生成资源，mock LLM 会按薄弱点生成讲义、案例、测验、任务、思维导图；但 `/resources/generate-pack` 仍以请求里的 `studentId/weakPoints` 和演示事件为主；资源列表默认全局可见；没有真实用户画像、学习反馈、推荐算法和审核状态闭环。 | PLORS `s40595-015-0049-6.pdf`、本体推荐 `3368691.3368700.pdf`、K12 推荐框架 `s10639-022-11489-4.pdf`、`sustainability-16-03034-v2.pdf`、赵晶等教学资源库论文。 | 资源生成默认读取当前用户画像、当前路径、知识点掌握度；为资源补充知识点、难度、类型、来源、适用画像标签、审核状态等元数据；记录点击、完成、评分等反馈；先实现规则 + 内容标签混合推荐，再扩展协同过滤或知识图谱推荐。 | 中 |
| RAG 问答是否基于课程知识库 | 部分实现 | `backend/app/api/routers/rag.py`、`backend/app/services/lightweight_rag_service.py`、`docs/course_kb/python_programming.json`、`backend/app/api/routers/tutor.py`、`backend/app/api/routers/knowledge_base.py`、`backend/app/rag/retriever.py`、`backend/app/rag/vector_store.py` | 存在两套问答路径：`/rag/ask` 固定读取 `docs/course_kb/python_programming.json`，基本忽略传入 `courseId/studentId`；`/tutor/ask` 可按 `course_id` 从上传课程资料的向量库检索，并返回引用来源，但 embedding 是 hash/fallback 方案，尚未做 KG-RAG、学生画像检索偏置、严格引用覆盖校验和多课程统一入口。 | `2311.17696v7.pdf` KG-RAG、`2502.15709v2.pdf` TutorLLM、`2504.09720v3.pdf` NotebookLM RAG 导师、`2509.00646v1.pdf` RAG-PRISM、张勇等学科知识图谱。 | 合并 `/rag/ask` 与 `/tutor/ask` 的能力边界，统一为课程知识库 RAG；按 `course_id`、知识点、章节、资源类型和学生薄弱点检索；引入真实 embedding 或可替换向量服务；答案强制携带 citation、confidence、unsupported claim 检查；逐步接入课程知识图谱增强检索。 | 中 |
| 多智能体工作流是否体现画像 Agent、资源 Agent、问答 Agent、诊断 Agent、审核 Agent | 部分实现 | `backend/app/agents/graph.py`、`backend/app/agents/profile_agent.py`、`backend/app/agents/planner_agent.py`、`backend/app/agents/resource_agent.py`、`backend/app/agents/tutor_agent.py`、`backend/app/agents/evaluator_agent.py`、`backend/app/agents/reporter_agent.py`、`backend/app/api/routers/agent_workflow.py`、`frontend/src/views/AgentWorkflow.vue`、`frontend/src/components/CapabilityBoundary.vue` | 实际 Agent 图包含 `ProfileAgent`、`PlannerAgent`、`ResourceAgent`、`TutorAgent`、`EvaluatorAgent`、`ReporterAgent`，能覆盖画像、路径、资源、问答、测评、报告。但缺少明确的 `AuditAgent/ReviewAgent`；诊断主要由 `EvaluatorAgent` 负责，不是独立诊断 Agent；`agent_workflow.py` 中 `review_agent` 更偏演示模板；部分界面提示当前 Agent 工作流仍是内置演示编排或 fallback。 | `2501.00083v1.pdf` von Neumann MAS、`2503.11733v2.pdf` LLM Agents for Education、`2509.20369v1.pdf` VITA、`2508.14109v1.pdf` PAPPL。 | 定义真实 Agent 合约：输入、输出、工具、状态、失败策略；将 `DiagnosisAgent` 从测评和学习分析中独立出来；新增 `AuditAgent` 调用内容审核服务并决定资源是否入库/发布；把每个 Agent 的输入输出、耗时、风险和人工干预记录持久化。 | 高 |
| 教师端是否有学习分析和学生薄弱点诊断 | 部分实现 | `frontend/src/views/TeacherHome.vue`、`frontend/src/views/TeacherAnalysis.vue`、`backend/app/api/routers/quizzes.py`、`backend/app/services/dashboard_service.py`、`backend/app/api/routers/reports.py` | 教师端页面已展示班级概览、薄弱知识点、风险学生和教学建议；`/quizzes/analysis` 会聚合测评提交、画像薄弱点和答疑互动，预留 BKT/DKT 字段。但前端仍有大量静态课程、学生、热力图、fallback 数据；后端掌握度是规则估计；教师与课程/班级没有权限关系；`_performance_distribution` 目前疑似缺少正常 return，成绩分布可能回落到前端 fallback。 | `2509.20369v1.pdf` VITA、`j.issn.1009-8097.2025.11.009.pdf`、`s44217-025-00815-w.pdf`、智慧教育研究综述。 | 建立课程-教师-班级-学生关系；用测验、答疑、资源完成、路径调整事件形成学习分析数据层；先修复现有分析返回结构，再引入掌握度趋势、薄弱点变化、干预建议和干预效果回收；教师端只展示授权班级。 | 中 |
| 管理员端是否有 AI 生成内容审核 | 部分实现 | `frontend/src/views/AdminContentReview.vue`、`backend/app/api/routers/content_review.py`、`backend/app/services/content_review_service.py`、`backend/app/api/routers/competition.py`、`backend/app/services/competition_mock_service.py`、`backend/app/models/a3.py` | 有 `/content-review/check` 规则审核接口，可检查引用数量、引用覆盖和绝对化表达，并把记录保存在进程内存 `REVIEW_RECORDS`；管理员页 `/api/v1/admin/content-review` 读取的是竞赛演示 mock 数据，前端“通过/驳回”只改本地状态；`GeneratedResource` 模型无 `review_status`、`review_opinion`、`reviewed_by` 等字段；AI 生成资源没有自动进入审核队列。 | `education-15-00706.pdf` RAG 原创性评价、`2509.00646v1.pdf` RAG-PRISM 内容对齐评价、`2503.11733v2.pdf` 教育 Agent 风险与伦理。 | 新增持久化内容审核表或资源审核字段；资源生成后默认进入待审核队列；审核接口支持列表、详情、通过、驳回、要求重生成；`AuditAgent` 自动给出风险标签、引用覆盖、幻觉风险和建议；管理员操作写入审计日志。 | 高 |

## 关键证据摘录

1. 登录与用户：`Login.vue` 明确写明“当前为演示级入口，不做复杂鉴权”；`useRole.ts` 只维护 `edumind.demoRole`；`api/client.ts` 未注入认证头。
2. 画像数据：`StudentProfile` 只有 `student_name`、`course_id`、`weak_points`、`profile_json` 等字段，没有 `user_id`。
3. 画像驱动路径和资源：`learning_path_service.py` 与 `resources.py` 均可读取 `profile_json`，但依赖传入 `student_profile_id`，没有当前用户上下文。
4. RAG：`lightweight_rag_service.py` 固定 `docs/course_kb/python_programming.json`；`tutor.py` 走课程向量库检索，课程知识库能力存在但尚未统一。
5. Agent：`graph.py` 的实际节点没有审核 Agent；`agent_workflow.py` 的 `review_agent` 主要出现在模板节点中。
6. 教师分析：`quizzes.py` 有掌握度矩阵和 BKT/DKT 预留字段，但说明当前为规则估计；前端教师页仍有静态课程、学生和 fallback 图表。
7. 内容审核：`content_review_service.py` 使用进程内存 `REVIEW_RECORDS`；`AdminContentReview.vue` 的审核按钮只修改本地列表。

## 答辩与方案优先级建议

1. 最值得写进答辩核心闭环：画像驱动路径与资源推荐、课程知识库 RAG、教师诊断、内容审核。
2. 最需要在答辩中如实说明的边界：当前登录和用户隔离尚未完成；Agent 和审核仍偏演示；RAG 已有课程知识库基础但不是完整 KG-RAG。
3. 最值得优先补齐的工程项：`user_id` 绑定、画像归属、资源审核持久化、统一课程 RAG、Agent 审核节点。
