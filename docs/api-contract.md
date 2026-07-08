# EduMind API Contract

本文档记录比赛演示版稳定接口口径。所有新增错误响应建议使用统一结构：`code`、`message`、`detail`、`request_id`。

## Health

- `GET /health`
- `GET /api/v1/health`

返回字段：

- `status`
- `llm_mode`
- `services.database`
- `services.rag`
- `services.dkvmn`
- `services.arbitration`
- `services.report`
- `services.version`

## Demo Status

- `GET /api/v1/demo-status`

返回演示检查状态、三端路线、能力清单、外部能力 fallback 状态和 `service_health`。

## RAG

- `POST /api/v1/rag/ask`

核心返回字段：

- `answer`
- `citations`
- `matchedChunks`
- `retrieved_chunks`
- `confidence`
- `parser_warnings`
- `curriculum_alignment`
- `alignment_breakdown`
- `fallback_reason`

## Quiz

- `POST /api/v1/quizzes/submit`
- `POST /api/v1/quiz/submit`

提交后返回得分、错因、弱知识点、DKVMN 更新结果和路径调整建议。兼容字段包括 `score`、`correct_count`、`total_count`、`concept_mastery_delta`、`weak_concepts`、`wrong_reason_analysis`、`recommended_tasks`、`dkvmn_updated`。

## Reports

- `GET /api/v1/reports`
- `POST /api/v1/reports`

报告服务输出 `report_id`、`student_name`、`course_name`、`profile_summary`、`mastery_summary`、`weak_concepts`、`learning_path_summary`、`quiz_summary`、`resource_recommendations`、`teacher_suggestions`、`evidence_items`、`generated_at`、`export_path`、`download_url`。

## Teacher Arbitration

- `GET /api/v1/teacher-arbitrations`
- `POST /api/v1/teacher-arbitration/{item_id}/decision`

`decision` 只能是 `approve`、`revise`、`reject`。服务会记录 `run_id`、`item_id`、`decision`、`teacher_comment`、`previous_status`、`next_status`、`retry_count`、`timestamp`，并推进下一节点。
