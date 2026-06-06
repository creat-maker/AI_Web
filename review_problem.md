# EduMind 方案符合度审计与待办清单

> **明确缺少项 · 可能缺少项 · 已实现项 · 后续优先级**
>
> 适用项目：EduMind / 中国软件杯 A3 方向 / 个性化学习资源与智能学习智能体系统
>
> 审计日期：2026-06-02（v3 更新 - 基于代码实际审查）

---

## 审计结论

当前 EduMind 已具备 **Web 三端演示系统**（学生端 / 教师端 / 管理员端）、登录入口与角色路由、LangGraph 多智能体工作流（6 Agent 顺序编排）、Chroma RAG 检索（HashEmbedding + JSON fallback）、Mock/真实 LLM 双模式（DeepSeek/通义千问）、Word 报告导出、Demo 状态页、一键验收脚本、学习行为采集、日志管理和系统设置等核心闭环能力。

**代码审查确认的核心实现：**
- ✅ LangGraph 多智能体：ProfileAgent → PlannerAgent → ResourceAgent → TutorAgent → EvaluatorAgent → ReporterAgent
- ✅ RAG 检索：Chroma 向量检索 + HashEmbedding + JSON fallback 双模式
- ✅ Mock/真实 LLM：DeepSeek / 通义千问 / Mock 三模式自动切换
- ✅ Agent 执行链路：`agent_workflow.py` 已实现步骤日志、耗时统计、状态追踪
- ✅ 知识库：支持 PDF/PPT/TXT/MD 上传、解析、分块、向量化
- ✅ 报告生成：python-docx 生成 Word 学习报告

对照软件杯方案，仍缺少或需要核验以下关键项：

- ❌ 微信小程序体验版（代码库无 `miniprogram` 目录）
- ❌ 对话式画像构建（当前仅问卷式输入 `profile_service.py`）
- ❌ 5 类资源生成（当前仅 4 类：讲义、案例、测验、任务）
- ⚠️ 课程知识库完整资料集（上传入口已有，需补完整课程文档）
- ⚠️ RAG 可信度评分（TutorAgent 返回 `source_file`，需增强可信度评分）
- ⚠️ 防幻觉审核中心（AdminReports.vue 有基础框架，需增加可信度评分和风险等级）
- ❌ 正式提交材料（PPT、视频、开发说明等）

---

## 1. 审计依据与范围

| 依据 | 内容 |
|------|------|
| 依据一 | 当前代码库实际实现：FastAPI 后端 + Vue3 前端 + LangGraph Agent + Chroma RAG |
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

> **总体判断**：已实现部分主要集中在 Web 三端产品化展示、三角色路由拆分、登录入口、Demo 状态页、一键验收脚本、LangGraph 多智能体工作流、Chroma RAG 检索和 Mock/真实 LLM 双模式。核心 AI 能力在 mock 模式下可用，真实 LLM 模式需配置 API Key。

| 模块 | 已实现内容 | 代码位置 | 状态 | 后续建议 |
|------|-----------|----------|------|----------|
| 统一 UI 与布局 | AppLayout、AppSidebar、AppHeader、DataCard、StatCard、StatusBadge 等公共组件 | [AppLayout.vue](file:///Users/xing/Desktop/EduMind/frontend/src/components/AppLayout.vue) | ✅ 已完成 | 继续只做小修 |
| 登录页与三角色入口 | `/login` 页面，学员/教师/管理员入口分别进入 `/student` `/teacher` `/dashboard` | [Login.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/Login.vue) | ✅ 已完成 | — |
| 三角色路由拆分 | 学生端 `/student/*`，教师端 `/teacher`，管理员端 `/dashboard` `/admin/*` | [router/index.ts](file:///Users/xing/Desktop/EduMind/frontend/src/router/index.ts) | ✅ 已完成 | — |
| 角色权限配置 | `useRole` composable + `roles.ts` 角色菜单、路由权限 | [useRole.ts](file:///Users/xing/Desktop/EduMind/frontend/src/composables/useRole.ts) | ✅ 已完成 | — |
| 学生端 Web 页面 | 学习总览、我的课程、学习路径、智能答疑、知识库、测验成绩、学习报告、任务、徽章、积分、笔记、小组 | [StudentHome.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/StudentHome.vue) 等 12 个页面 | ✅ 已完成 | 部分页面为占位，需补真实闭环 |
| 教师端 Web 页面 | 班级概览、课程管理、学生画像、学习路径与任务布置、测评分析、报告中心 | [TeacherHome.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/TeacherHome.vue) | ✅ 已完成 | — |
| 管理员端 Web 页面 | 平台总览、用户与角色、课程治理、资源生成、Agent 工作流、报告、知识库、日志、系统设置 | [AdminCourses.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/AdminCourses.vue) 等 | ✅ 已完成 | — |
| Demo 状态页 | `/demo-status` 前后端，展示 Ready、通过率、三端路线和关键能力 | [DemoStatus.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/DemoStatus.vue) + [demo_status.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/demo_status.py) | ✅ 已完成 | — |
| 统一演示数据 | 张三、李四、王五；王老师、陈老师、张老师；四门课程；两个班级 | [seed_demo_data.py](file:///Users/xing/Desktop/EduMind/scripts/seed_demo_data.py) | ✅ 已完成 | — |
| 一键验收脚本 | `seed-demo-data`、`check-demo-ready`、`e2e_demo_flow_check` | [scripts/](file:///Users/xing/Desktop/EduMind/scripts/) | ✅ 已完成 | — |
| 学习行为数据采集 | 业务事件记录、资源包生成、路径更新、测验完成等事件 | [events.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/events.py) | ✅ 已完成 | — |
| 日志管理 | QA、文档上传、Agent、报告、错误等多类型日志 | [logs.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/logs.py) | ✅ 已完成 | — |
| 系统设置 | 运行模式、fallback 数据源和能力边界 | [system_settings.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/system_settings.py) | ✅ 已完成 | — |
| 能力边界说明 | `/capability-boundary` 页面，说明 AI 资源正文可由 fallback 模板生成等 | [CapabilityBoundary.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/CapabilityBoundary.vue) | ✅ 已完成 | — |
| 课程管理 CRUD | 创建、编辑、删除课程 | [courses.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/courses.py) | ✅ 已完成 | — |
| 知识库上传与解析 | 支持 PDF/PPT/TXT/MD 上传、解析、分块、Chroma 向量化 | [knowledge_base.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/knowledge_base.py) | ✅ 已完成 | 补完整课程资料集 |
| RAG 检索 | Chroma 向量检索 + HashEmbedding + JSON fallback 双模式 | [vector_store.py](file:///Users/xing/Desktop/EduMind/backend/app/rag/vector_store.py) | ✅ 已完成 | embedding 质量待提升 |
| 学生画像生成 | 问卷式输入 → LLM/Mock 生成画像 | [profile_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/profile_service.py) | ⚠️ 部分实现 | 缺少对话式画像 |
| 学习路径规划 | LLM/Mock 生成 3 阶段学习路径 | [planner_agent.py](file:///Users/xing/Desktop/EduMind/backend/app/agents/planner_agent.py) | ⚠️ 部分实现 | 缺少动态调整 |
| 资源生成 | 4 类资源：讲义、案例、测验、任务 | [resource_agent.py](file:///Users/xing/Desktop/EduMind/backend/app/agents/resource_agent.py) | ⚠️ 部分实现 | 需补至 5 类 |
| 智能答疑 | 基于 RAG 的问答，返回引用来源 | [tutor_agent.py](file:///Users/xing/Desktop/EduMind/backend/app/agents/tutor_agent.py) | ⚠️ 部分实现 | 需增强可信度 |
| 测验评价 | 生成测验 → 提交答案 → 评分反馈 | [quiz_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/quiz_service.py) | ✅ 已完成 | — |
| Word 报告导出 | python-docx 生成学习报告 | [report_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/report_service.py) | ✅ 已完成 | — |
| LangGraph 多智能体 | 6 Agent 顺序工作流：Profile→Planner→Resource→Tutor→Evaluator→Reporter | [graph.py](file:///Users/xing/Desktop/EduMind/backend/app/agents/graph.py) | ✅ 已完成 | — |
| Agent 执行链路 | 步骤日志、耗时统计、状态追踪、输入输出摘要 | [agent_workflow.py](file:///Users/xing/Desktop/EduMind/backend/app/api/routers/agent_workflow.py) | ✅ 已完成 | — |
| Mock/真实 LLM 双模式 | DeepSeek / 通义千问 / Mock 三模式自动切换 | [llm_service.py](file:///Users/xing/Desktop/EduMind/backend/app/services/llm_service.py) | ✅ 已完成 | — |
| Dashboard 统计 | 课程/画像/资源/测验/报告/Agent 运行数 + 7 天趋势 | [Dashboard.vue](file:///Users/xing/Desktop/EduMind/frontend/src/views/Dashboard.vue) | ✅ 已完成 | — |
| .env.example | 环境变量样例文件 | [.env.example](file:///Users/xing/Desktop/EduMind/.env.example) | ✅ 已完成 | — |

---

## 3. 明确缺少项清单

> 以下项目是对照方案和赛题后，代码库中没有找到对应实现的内容。按优先级排列。

### P0 — 赛题硬要求，必须补齐

| # | 缺少项 | 判断依据 | 当前状态 | 建议补法 |
|---|--------|----------|----------|----------|
| 1 | **微信小程序学生端体验版** | 方案明确建议 Web 主系统 + 微信小程序体验版；代码库中无 `miniprogram` 目录 | ❌ 不存在 | 新增 `miniprogram`：今日学习、路径、资源、AI 辅导、练习/错题、报告；先 mock，预留 API |
| 2 | **对话式学习画像构建** | 赛题要求自然语言对话构建不少于 6 维画像；当前仅有问卷式输入（`profile_service.py` 使用 `llm_service.generate_json("profile", data)`） | ❌ 不存在 | 新增 `/student/profile-dialog` 或在画像页加入对话式生成流程、画像 JSON、手动修正 |
| 3 | **至少 5 类个性化资源生成** | 赛题硬要求；当前 ResourceAgent 仅生成 4 类（讲义、案例、测验、任务） | ⚠️ 仅 4 类 | 增加第 5 类资源（如思维导图/代码案例/视频脚本），实现演示级接口与页面输出 |
| 4 | **课程知识库与样例课程资料集** | 赛题要求自行构造至少一门完整高校专业课程知识库/文档集 | ⚠️ 仅有上传入口 | 准备一门完整课程：章节、知识点、讲义、题库、实验/项目材料；放入 `dataset` 或 `docs/course_kb` |
| 5 | **RAG 引用溯源与可信度评分** | 防幻觉和课程资料约束需要引用片段、来源文件、可信度；当前 TutorAgent 返回 `source_file` 但无可信度评分 | ⚠️ 有基础引用 | 增强 TutorAgent 返回：引用资料、可信度评分、推荐练习 |
| 6 | **防幻觉审核中心/审核记录** | 赛题非功能需求明确要求防幻觉与内容安全过滤；当前 AdminReports.vue 有基础框架 | ⚠️ 有基础框架 | 增加可信度评分、风险等级、审核状态、通过/退回/重生成 |

### P1 — 重要但非硬性截止

| # | 缺少项 | 判断依据 | 当前状态 | 建议补法 |
|---|--------|----------|----------|----------|
| 7 | **资源推荐理由** | 个性化系统必须能解释"为什么推荐" | ❌ 不存在 | 在学生课程/路径/资源/报告页加入推荐原因：薄弱点、测验证据、目标匹配 |
| 8 | **学习路径动态调整** | 当前有路径展示，但测验/答疑后不会自动调整 | ❌ 不存在 | 用规则演示：错题薄弱点变化后更新下一任务与推荐资源 |
| 9 | **正式文档包** | 赛题要求系统开发说明、测试说明、部署说明等 | ⚠️ 部分文档已有 | 补齐 docx：系统开发说明、测试说明、部署说明、AI 工具说明、开源协议说明、用户手册 |
| 10 | **演示 PPT 与 7 分钟视频** | 赛题明确提交 PPT 和 7 分钟以内演示视频 | ❌ 不存在 | 制作 PPT；录制固定三端路线 + demo-status + 资源生成/Agent |
| 11 | **提交包目录** | 方案建议整理完整提交目录 | ❌ 不存在 | 整理 `EduMind_Submission` 目录 |

---

## 4. 可能缺少 / 需代码核验项

> 这些内容不是一定没有，而是当前代码无法证明已经真实实现。需进一步确认。

| # | 可能缺少项 | 核验原因 | 代码审计结果 | 处理建议 |
|---|-----------|----------|-------------|----------|
| 1 | **真实登录鉴权与权限控制** | 当前为 Demo 角色入口，无 JWT/auth 中间件 | ⚠️ Demo 级 | 初赛可接受 Demo 登录；后续扩展真实鉴权 |
| 2 | **三角色路由拆分** | 已有 `/student/*` `/teacher` `/admin/*` 完整路由 | ✅ 已实现 | 确认各角色菜单不再跨角色切换 |
| 3 | **Demo 状态页** | `/demo-status` 前后端已实现 | ✅ 已实现 | 保持为答辩入口 |
| 4 | **一键验收脚本** | `seed-demo-data` `check-demo-ready` `e2e_demo_flow_check` 已实现 | ✅ 已实现 | 每次提交后必须重跑 |
| 5 | **生成进度追踪/流式输出** | 赛题建议流式输出或生成进度追踪；AgentWorkflow 页面已有步骤条 | ⚠️ 部分实现 | 可在资源生成/Agent 页面用步骤条模拟进度；真实 SSE 后续做 |
| 6 | **学习行为数据采集** | `events.py` 已实现业务事件记录 | ✅ 已实现 | — |
| 7 | **测验在线作答与错题本** | `QuizEvaluate` + `StudentExamResult` 已有在线作答 | ✅ 已实现 | 可增加错题本功能 |
| 8 | **知识点图谱/前置关系** | 学习路径页面有节点，但无知识图谱数据结构 | ❌ 不存在 | 用 JSON 表示知识点和 `prereq_ids` 即可 |
| 9 | **教师资源审核权限** | `AdminReports.vue` 报告审核中心已实现 | ✅ 已实现 | 可增加防幻觉审核到教师端核心菜单 |
| 10 | **开源协议与 AI Coding 使用说明** | `CapabilityBoundary.vue` 已实现能力边界说明 | ✅ 已实现 | 可补充独立文档 |
| 11 | **部署说明** | `.env.example` + `start-dev.bat` + `stop-dev.bat` 已有 | ✅ 已实现 | 可补充生产部署说明 |
| 12 | **截图与演示素材** | 未整理 screenshots 文件夹 | ❌ 不存在 | 导出关键页面截图 |
| 13 | **旧页面/未跟踪文件清理** | `legacy/` 目录存在大量旧代码 | ⚠️ 已隔离 | 确认 `.gitignore` 覆盖，提交时排除 |
| 14 | **移动端响应式** | Web 页面多为桌面布局 | ⚠️ 桌面优先 | Web 保持桌面演示；小程序负责移动端 |
| 15 | **接口契约一致性** | 前端 mock 与后端可能字段不一致 | ⚠️ 需核验 | 做 API schema 文档或字段映射表 |
| 16 | **测试覆盖** | `check-demo-ready` 验收脚本已有，但无单元测试 | ⚠️ 部分覆盖 | 保留 check-demo-ready 作为核心验收 |

---

## 5. 暂缓项 / 不建议现在强做

| 事项 | 不建议现在做的原因 | 推荐表述 |
|------|-------------------|----------|
| 完整 LangChain / LangGraph 接入 | 已接入 LangGraph，但复杂状态图调试和现场稳定性有风险 | 当前已接入 LangGraph，后续可优化状态图 |
| 真实向量数据库全量接入 | Chroma 已接入，但 embedding 质量待提升 | 当前使用 HashEmbedding，后续可替换为真实 embedding 模型 |
| 正式上线微信小程序 | 注册/审核/备案不确定，初赛不要求正式上线 | 提供开发版/体验版源码、运行说明和二维码 |
| 复杂权限系统 | RBAC、后端鉴权、权限矩阵会拖慢演示版本 | 当前 Demo 角色入口，后续生产化补强 |
| 真实多模态视频生成 | 生成视频成本高、时间不稳定、依赖外部模型 | 先生成视频脚本、分镜、旁白和画面提示词 |
| 完整 Docker/云部署 | 部署很加分但不是当前代码闭环的第一问题 | 若时间充足再补 `docker-compose` 和服务器演示地址 |

---

## 6. 按优先级的下一步开发路线

| 阶段 | 优先级 | 任务 | 目标 | 验收标准 |
|------|--------|------|------|----------|
| 第七阶段 | P0 | 小程序学生端体验版 | 补齐 Web + 小程序协同方案 | `miniprogram` 可用微信开发者工具打开；6 个页面可点击；README 完整 |
| 第八阶段 | P0 | 对话式画像 + 5 类资源生成 | 补齐赛题核心硬要求 | 输入张三画像/薄弱点，输出画像 JSON 和 5 类资源包 |
| 第九阶段 | P0 | 轻量 RAG + 引用 + 防幻觉审核 | 把智能答疑、资源生成和可信机制讲通 | 问答有引用来源；资源有可信度；审核记录可查看 |
| 第十阶段 | P1 | 正式文档、PPT、视频、提交包 | 完成初赛提交材料 | PPT、7 分钟视频、开发/测试/部署/AI 工具说明、提交目录齐全 |

---

## 7. 最小补齐方案（时间紧时只做这些）

- **小程序**：只做学生端 6 页，使用统一 demoData，不做教师端和管理员端
- **对话画像**：只做一个演示流程，抽取 6 个画像维度，支持保存到 demoData
- **资源生成**：固定课程 + 学生 + 薄弱点，生成 5 类资源，保留 Agent 时间线
- **RAG**：不用真实向量库，先做本地知识库关键词检索，返回引用来源和推荐练习
- **防幻觉**：做可信度评分、引用命中、风险等级、教师审核状态
- **视频**：录制一条固定路线，避免现场临时输入太多

---

## 8. 推荐审计提示词

> 使用方式：先做只读审计，不要马上修改代码。拿到审计结果后，再决定下一阶段先补小程序还是先补 RAG/资源生成。

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
| 产品形态 | ✅ 较好 | Web 三端完整；登录入口、角色路由、Demo 状态页、验收脚本均已就位；小程序学生端缺失 |
| 赛题核心功能 | ⚠️ 部分符合 | 页面与演示路线完整，但画像、5 类资源、RAG 可信度、防幻觉还不够真实 |
| 工程完整性 | ✅ 较好 | 有前后端、统一数据、演示数据脚本、验收脚本、LangGraph Agent、Chroma RAG、Mock/真实双模式 |
| 比赛展示效果 | ✅ 较好 | 登录页、三端路由、Demo 状态页、Agent 工作流已能支撑讲解；还需 PPT/视频/截图 |
| 技术深度 | ⚠️ 中等偏上 | Agent/RAG 已有基础实现；embedding 质量和防幻觉需加强 |
| 提交准备度 | ⚠️ 部分完成 | 正式文档、小程序、PPT、视频、提交包还需整理 |
