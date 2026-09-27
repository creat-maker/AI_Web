# EduMind 架构说明

> 事实基线：`4d8b658`；核心功能提交：`43f49d6`。
> 统一口径见 [fact-baseline.md](fact-baseline.md)。

## 总体架构

```text
Web 学生/教师/管理员 + 微信小程序学生端
                    |
                FastAPI API
                    |
     业务服务、Agent、RAG、DKVMN、治理
                    |
      SQLAlchemy + SQLite 演示数据与审计日志
                    |
 可选外部能力：LLM、讯飞工具、Chroma、FFmpeg、
              SentenceTransformer
```

未配置外部能力时，系统使用 mock、规则引擎、TF-IDF、JSON 知识库和本地演示数据 fallback。fallback 可保持演示链路运行，但不等同于真实云调用成功。

## 访问端范围

- Web 学生端：画像、路径、资源、RAG 问答、测验和报告。
- Web 教师端：课程、学情、资源生成、任务和教师仲裁。
- Web 管理员端：系统状态、内容治理、Agent 工作流和审计日志。
- 微信小程序：7 个学生端页面；尚未完成开发者工具和真机验收。

## 后端模块

- `backend/app/api/routers/`：业务路由与演示契约。
- `backend/app/agents/`：Agent 状态、节点实现和 LangGraph 图。
- `backend/app/services/lightweight_rag_service.py`：RAG 检索、课程约束、引用和 fallback。
- `backend/app/services/embedding_interface.py`：TF-IDF 与可选 SentenceTransformer embedding 接口。
- `backend/app/services/dkvmn_tracker.py`：轻量在线门控记忆知识追踪。
- `backend/app/services/governance_service.py`：治理、教师仲裁、续跑和审计持久化。
- `backend/app/services/multimodal_resource_service.py`：9 类资源目录及 TTS/FFmpeg fallback。

## 12 节点 Agent 图

`backend/app/agents/graph.py` 注册：

1. ProfileAgent
2. KnowledgeAgent
3. PlannerAgent
4. ResourcePlannerAgent
5. ResourceAgent
6. TutorAgent
7. EvaluatorAgent
8. AuditAgent
9. ComplianceAgent
10. AuditRetry
11. TeacherArbitration
12. ReporterAgent

```text
ProfileAgent
  -> KnowledgeAgent
  -> PlannerAgent
  -> ResourcePlannerAgent
  -> ResourceAgent
  -> TutorAgent
  -> EvaluatorAgent
  -> AuditAgent
  -> ComplianceAgent
       ├─ pass -> ReporterAgent -> END
       ├─ retry -> AuditRetry -> ResourceAgent
       └─ teacher_arbitration -> TeacherArbitration
                                     ├─ approve -> ReporterAgent
                                     ├─ revise -> ResourceAgent
                                     └─ reject -> END
```

中风险内容在 `retry_count < 3` 时回流；高风险或达到重试上限时进入教师仲裁。待仲裁运行持久化为 `pending_review`，资源保持待审状态，不提前生成最终报告。

三类决策路由、资源再生成和审计持久化已通过自动测试；教师端完整人工 UI 演练尚未完成。

## Agent 状态与持久化

`AgentState` 包含运行标识、当前节点、画像、检索证据、学习路径、资源、测验、审核、报告、消息、错误、重试上下文、教师意见、发布阻断和拒绝原因等字段。

`AgentRun` 保存运行状态；教师决策通过治理服务恢复图执行，并同步资源、测验、报告和 `AuditLog`。

## RAG 数据流

```text
问题
 -> 课程标识解析
 -> 已导入课程向量/混合检索
 -> 课程语义约束与证据重排
 -> citations / confidence / retrieval_debug
 -> 无可用向量项时 JSON + TF-IDF fallback
 -> 证据不足或超范围时返回 boundary_warning/fallback_reason
```

本地 TF-IDF provider 是默认轻量 embedding。Chroma 和 SentenceTransformer 是可选能力。本轮 E2E 的特定 RAG 请求实际使用 JSON/TF-IDF fallback。

## 知识追踪数据流

```text
测验题 concept_id + 作答结果
 -> softmax key 寻址
 -> 读取学生 value memory
 -> erase/add 门控更新
 -> mastery / 强弱项
 -> 六维画像与学习路径调整
```

当前是轻量在线门控记忆实现，无预训练检查点、训练数据和论文级效果验证。

## 治理与审计

治理链路包含七维规则审核、课程证据检查、可选讯飞安全适配、风险分级、最多 3 次回流、教师仲裁和 AuditLog。

该实现提供工程可追踪性，不应描述为第三方合规认证或不可篡改审计。

## 接口口径

本轮运行时 OpenAPI 统计为 111 个路径、117 个 HTTP operation。该数字用于接口契约统计，不是用户功能数量。完整接口应从同一提交的 `/openapi.json` 导出。
