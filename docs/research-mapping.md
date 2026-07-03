# 论文方法到工程能力映射

## DKVMN -> 个性化画像与知识追踪

EduMind 使用参考 DKVMN 的轻量 Key-Value Memory 结构做知识追踪：Key 是 Python 知识点注册表和 `key_matrix`，Value 是按学生持久化的 `value_memory`。测验题目携带 concept_id 后，系统根据对错、难度、响应时长和得分更新 value 向量，再从 value 向量估计 mastery、连续对错、强弱点，并映射到知识基础、学习节奏、学习偏好、代码实操能力、易错知识点、学习风险 6 维画像。

边界：当前不是完整深度学习复现，不训练神经网络；`DKVMNModelInterface` 用于未来替换真实模型。

## EduLLM -> 课程约束 RAG

EduMind 将课程大纲约束、文档解析、章节分块、TF-IDF embedding、引用证据、超纲检测和课程对齐评分组合成可信教学问答。回答结构包含 answer、citations、confidence、curriculum_alignment_score、alignment_breakdown、matched_objectives、evidence_coverage_score、boundary_warning、suggested_actions 和 retrieval_debug。

边界：未配置 Chroma 或 embedding 模型时使用 JSON/TF-IDF fallback；OCR 仅预留。

## FACET -> 多智能体教师仲裁治理

EduMind 保留 9 个核心学习智能体节点，并新增 ComplianceAgent、AuditRetry 和 TeacherArbitration 3 个治理增强节点，因此实际为 12 节点扩展工作流。审核维度包括事实准确性、课程对齐度、超纲风险、隐私风险、不当内容、幻觉风险、学段适配。中高风险内容进入回流或教师仲裁，结果写入日志。

边界：讯飞安全 API 未配置时使用本地规则；并行 Agent 仅保留扩展结构，当前以顺序兜底保证演示稳定。

## 工程化原则

本项目强调可运行、可展示、可解释的轻量落地，不夸大为完整论文复现。所有外部依赖均有 fallback，优先保证比赛演示闭环稳定。
