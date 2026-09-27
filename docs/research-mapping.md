# 研究方法到工程能力映射

本文档说明论文/方法概念在 EduMind 中的工程化范围，不把工程演示实现描述为论文完整复现。

## DKVMN：轻量在线门控记忆知识追踪

工程实现位于 `backend/app/services/dkvmn_tracker.py`：

- Key：课程概念注册表和 `key_matrix`。
- 寻址：softmax attention。
- Value：按学生维护的 `value_memory`。
- 更新：根据作答、难度、时间等信息执行 erase/add 门控更新。
- 输出：掌握度、强弱项及六维画像映射。

边界：没有论文规模训练集、预训练 checkpoint 或论文级指标验证；准确表述为“轻量在线门控记忆知识追踪实现”。

## 课程约束 RAG

工程实现组合：

- 课程文档解析和分块；
- TF-IDF embedding 接口；
- 课程向量/混合检索优先；
- JSON+TF-IDF fallback；
- 引用、置信度、课程对齐、证据覆盖和边界告警；
- 可选 Chroma 与 SentenceTransformer。

边界：本轮评价集只有 5 条，仅用于回归和演示验证；OCR 仍是扩展边界。

## 多智能体教师仲裁治理

工程采用 12 节点 LangGraph：

ProfileAgent、KnowledgeAgent、PlannerAgent、ResourcePlannerAgent、ResourceAgent、TutorAgent、EvaluatorAgent、AuditAgent、ComplianceAgent、AuditRetry、TeacherArbitration、ReporterAgent。

中风险内容回流再生成，高风险或达到重试上限后暂停等待教师。approve、revise、reject 分别进入报告、重新生成复审或阻断发布，并写入运行状态和审计日志。

边界：这是教师中心的工程治理流程，不宣称完整复现特定论文系统；教师端三类决策的完整 UI 人工演练尚未完成。

## 工程化原则

- 外部能力不可用时明确 fallback，不把 fallback 冒充云服务成功。
- 所有研究映射同时写明未训练、未验证或未接入的边界。
- 评价数字必须引用 [统一事实基线](fact-baseline.md)。
