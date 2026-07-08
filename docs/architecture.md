# EduMind 架构说明

## 系统架构图（文字版）

用户三端（Vue Web / 微信小程序） -> FastAPI API -> SQLAlchemy SQLite + JSON/Chroma fallback -> 服务层（DKVMN、RAG、资源、报告、治理） -> 可选外部能力（LLM、讯飞、FFmpeg、SentenceTransformer）。

## 后端模块

- `api/routers`：课程、画像、路径、资源、RAG、测验、报告、Agent、治理、日志。
- `services/dkvmn_tracker.py`：轻量知识追踪。
- `services/document_parser.py`、`chunk_strategy.py`、`curriculum_constraint.py`、`embedding_interface.py`：课程约束 RAG。
- `agents/graph.py`、`agents/governance_agent.py`：多智能体流转、审核回流、教师仲裁。
- `services/multimodal_resource_service.py`：多模态资源与 TTS/FFmpeg fallback。

## 前端模块

- 通用组件：PageHeader、SectionCard、MetricCard、StatusTag、EmptyState、CitationCard、AgentLogViewer、ResourcePreview、ProfileRadarCard、LearningPathTimeline。
- 学生端：画像、路径、答疑、资源、测验、报告。
- 教师端：课程、学情、资源生成、决策/仲裁、报告。
- 管理端：Dashboard、知识库、内容审核、Agent 工作流、日志、系统状态。

## 智能体工作流

系统采用 12 节点教学智能体治理增强流程，包括 ProfileAgent、KnowledgeAgent、PlannerAgent、ResourcePlannerAgent、ResourceAgent、TutorAgent、EvaluatorAgent、AuditAgent、ComplianceAgent、AuditRetry、TeacherArbitration、ReporterAgent。

原始开发方案中的 9+1 是核心教学闭环，当前工程版在其基础上扩展了 ComplianceAgent、AuditRetry、TeacherArbitration 等治理节点，用于满足可信、安全、可追溯要求。

当 ComplianceAgent 判定中高风险：

- 中风险且 retry_count < 3：AuditRetry 回流 ResourceAgent。
- 高风险或 3 次仍不通过：TeacherArbitration。
- 教师 approve/revise/reject 后写入 audit_logs。

## 数据流

画像对话生成 profile_json -> 测验提交写 QuizSubmission -> DKVMN 更新 cognitive_state -> LearningPath adjustment_log -> 资源与 RAG 证据进入报告 -> AgentRun/AuditLog 形成治理追踪。

## 治理闭环

规则引擎 7 维审核 + 讯飞安全 API 预留 + 教师仲裁 + 审计日志 + 前端 AgentLogViewer 可视化。
