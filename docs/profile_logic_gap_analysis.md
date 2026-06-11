# 对话式学习画像与个性化推荐链路审查报告

审查范围：前端登录与 demo 用户切换、后端画像/路径/资源/测评/问答接口、数据库模型与种子数据。结论基于当前代码静态审查，未修改业务代码。

## 1. 用户登录或 demo 用户切换

- 模块名称：用户登录态与 demo 用户切换
- 当前实现状态：部分实现
- 相关文件：
  - `frontend/src/views/Login.vue`
  - `frontend/src/composables/useRole.ts`
  - `frontend/src/components/RoleSwitcher.vue`
  - `frontend/src/api/client.ts`
  - `backend/app/services/demo_learning_service.py`
  - `backend/app/api/routers/profiles.py`
  - `backend/app/api/routers/learning_paths.py`
  - `backend/app/api/routers/competition.py`
- 存在问题：
  - 前端存在演示入口和角色切换，`useRole.ts` 使用 `localStorage` 保存 `edumind.demoRole`、兼容旧 key `edumind.currentRole`，并保存 `edumind.demoUserId`。
  - demo 学生用户包括 `demo-basic`、`demo-advanced`、`demo-exam`，后端 `demo_learning_service.py` 可按 `user_id` 映射不同 demo 学生。
  - 未发现真实登录、token、session、后端鉴权依赖或统一 `current_user` 解析逻辑。
  - API client 只封装 `fetch`，不会自动携带 token、用户头或当前 `demoUserId`；页面需要手动拼接 `user_id`。
  - `role` 仅由前端路由或 localStorage 决定，后端接口没有基于登录态识别 `role`、`student_id` 或 `user_id`。
- 风险等级：高
- 建议修改方式：
  - 增加统一用户上下文：真实登录可使用 token/session；演示模式至少统一由 API client 注入 `X-Demo-User-Id` 或查询参数。
  - 后端增加 `get_current_user` 或 demo 等价依赖，统一解析 `user_id`、`role`、`student_id`。
  - 避免各页面自行决定是否传 `user_id`，减少链路断裂。
- 是否建议立即修复：是

## 2. 根据 user_id 获取用户学习数据

- 模块名称：用户学习数据读取与 user_id 隔离
- 当前实现状态：部分实现
- 相关文件：
  - `backend/app/models/a3.py`
  - `database/init_mysql.sql`
  - `backend/app/api/routers/profiles.py`
  - `backend/app/api/routers/learning_paths.py`
  - `backend/app/api/routers/quizzes.py`
  - `backend/app/api/routers/tutor.py`
  - `backend/app/api/routers/reports.py`
  - `backend/app/services/demo_learning_service.py`
  - `scripts/seed_demo_data.py`
- 存在问题：
  - 数据模型包含 `StudentProfile`、`LearningPath`、`GeneratedResource`、`Quiz`、`QuizSubmission`、`TutorQuestionLog`、`LearningReport`，能覆盖画像、学习路径、资源、测评提交、问答日志和报告等学习数据。
  - 真实数据库主关联字段是 `student_profile_id`，`student_profiles` 表没有 `user_id`、`student_id`、`major`、班级/学号等稳定身份字段。
  - `profiles?user_id=...` 返回的是 `demo_learning_service.py` 内置 demo 数据，不查询数据库。
  - 问答日志 `TutorQuestionLog` 只有 `course_id`，没有 `student_profile_id` 或 `user_id`，无法按学生区分问答历史。
  - 测评相关真实接口按 `student_profile_id` 区分，但学生端 `StudentSmartQuiz.vue` 走 `/api/v1/quiz/submit`，固定提交 `student_id: 'demo-student-zhangsan'`，未使用当前 `demoUserId`。
- 风险等级：高
- 建议修改方式：
  - 给真实画像或用户表补充 `user_id/student_id` 字段，并为学习数据表建立可追溯的用户关联。
  - 将 `profiles?user_id=` 从纯 demo fallback 改为优先查库、缺失时再返回 demo。
  - 为 `TutorQuestionLog` 增加 `student_profile_id` 或 `user_id`，并在 `/tutor/ask`、`/tutor/history` 中按用户过滤。
  - 学生端测评、问答、路径、资源接口统一使用当前用户上下文。
- 是否建议立即修复：是

## 3. 自然语言对话抽取画像

- 模块名称：对话式画像抽取接口
- 当前实现状态：部分实现
- 相关文件：
  - `backend/app/api/routers/profile_dialog.py`
  - `backend/app/services/profile_dialog_service.py`
  - `backend/app/services/personalization_service.py`
  - `backend/app/services/mock_llm.py`
  - `frontend/src/views/ProfileDialog.vue`
  - `frontend/src/views/StudentAssistant.vue`
- 存在问题：
  - 已存在 `/api/v1/profile-dialog/run` 兼容单轮接口，以及 `/start`、`/continue`、`/finish`、`/save` 多轮接口。
  - 多轮服务能从自然语言中增量抽取 `current_level`、`learning_goal`、`weak_points`、`learning_preference`、`diagnosis`、`strategy`。
  - mock 模式主要依赖关键词规则和默认值补全；`run` 接口在传入 `studentId` 时会先从 demo 学生表注入姓名、课程、薄弱点和默认回答，存在演示数据强驱动。
  - `/save` 只保存 `student_name` 与 `course_id`，不绑定 `user_id` 或当前登录学生。
  - 抽取维度未覆盖 `major`、`available_time`、`mistake_pattern`、`resource_preference` 等更完整画像字段。
- 风险等级：中
- 建议修改方式：
  - 明确区分 `mock/rule-based` 与真实 LLM 抽取模式，在响应中保留 `source`、`confidence`、`evidence`。
  - 保存画像时绑定当前 `user_id/student_id`，避免姓名相同或不同入口保存后无法归属。
  - 扩展抽取 schema，加入专业、可用时间、错因模式、资源偏好等字段。
- 是否建议立即修复：是

## 4. 画像维度不少于 6 个

- 模块名称：画像字段与维度完整性
- 当前实现状态：部分实现
- 相关文件：
  - `backend/app/models/a3.py`
  - `backend/app/services/profile_dialog_service.py`
  - `backend/app/services/profile_service.py`
  - `backend/app/services/demo_learning_service.py`
  - `backend/app/services/personalization_service.py`
  - `scripts/seed_demo_data.py`
- 存在问题：
  - 数据库存储字段包括 `current_level`、`learning_goal`、`weak_points`、`learning_preference`、`profile_json`、`created_at`、`updated_at`。
  - 多轮对话定义 6 个维度：`current_level`、`learning_goal`、`weak_points`、`learning_preference`、`diagnosis`、`strategy`。
  - 单轮 `run` 接口返回 7 个展示维度：学习目标、基础水平、薄弱知识点、学习偏好、时间安排、学习风险、推荐策略。
  - demo 画像额外包含 `profile_type`、`risk_level`、`score`、`progress`、`resource_usage`、`recommended_strategy`。
  - 但当前字段命名与目标字段不一致，缺少或未稳定持久化 `major`、`knowledge_level`、`mistake_pattern`、`available_time`、`resource_preference`。
  - `learning_style` 与 `learning_preference` 概念接近，但未形成统一 schema。
- 风险等级：中
- 建议修改方式：
  - 定义统一 `StudentLearningProfile` schema，至少包含 `major`、`learning_goal`、`knowledge_level/current_level`、`weak_points`、`learning_style`、`mistake_pattern`、`available_time`、`resource_preference`、`risk_level`。
  - `profile_json` 内保留完整结构，表字段只做高频查询冗余。
  - 前后端统一字段名，避免同一含义在不同接口中出现 `foundationLevel/current_level/knowledge_level` 等多套命名。
- 是否建议立即修复：是

## 5. 不同用户画像不同

- 模块名称：用户画像隔离与 demo 用户差异
- 当前实现状态：部分实现
- 相关文件：
  - `backend/app/services/demo_learning_service.py`
  - `backend/app/api/routers/profiles.py`
  - `frontend/src/composables/useRole.ts`
  - `frontend/src/views/Login.vue`
  - `frontend/src/views/StudentProfile.vue`
  - `frontend/src/views/StudentAssistant.vue`
- 存在问题：
  - demo 数据层面，`demo-basic`、`demo-advanced`、`demo-exam` 的画像类型、目标、薄弱点、风险、策略不同。
  - 学生端 `StudentProfile.vue` 在学生角色下会请求 `/api/v1/profiles?user_id=${demoUserId}`，可以拿到不同 demo 画像。
  - `StudentAssistant.vue` 的画像和资源包会传 `demoUserId`，可以触发不同 demo 学生数据。
  - 真实数据库画像没有 `user_id` 字段；`/profile-dialog/save` 新增画像只按姓名和课程保存，不绑定当前 demo 用户或真实用户。
  - 教师端 `/api/v1/profiles` 返回全部画像；若学生端遗漏 `user_id`，容易退化为共用画像列表或 fallback 数据。
- 风险等级：高
- 建议修改方式：
  - 将 demo 用户和真实画像建立映射，保存对话画像时必须写入 `user_id/student_id`。
  - 所有学生端读取画像接口默认按当前用户过滤，教师端才允许按班级/课程查看多用户。
  - 增加测试覆盖：切换三个 demo 用户后，画像、路径、资源均应不同。
- 是否建议立即修复：是

## 6. 画像动态更新

- 模块名称：画像更新、变更记录与学习行为反馈
- 当前实现状态：部分实现
- 相关文件：
  - `backend/app/models/a3.py`
  - `backend/app/services/learning_path_service.py`
  - `backend/app/services/quiz_service.py`
  - `backend/app/api/routers/quizzes.py`
  - `backend/app/api/routers/events.py`
  - `backend/app/api/routers/tutor.py`
- 存在问题：
  - `StudentProfile` 有 `updated_at` 字段，数据库脚本也定义了自动更新时间。
  - `learning_path_service.adjust_learning_path` 会根据新增/已掌握薄弱点更新 `profile.weak_points` 和 `profile.profile_json`，并记录 `LearningPath.adjustment_log`。
  - `quiz_service.submit_quiz` 在评价结果包含 `path_adjustment_needed` 时会尝试自动调整路径并间接更新画像薄弱点。
  - 当前自动更新依赖 LLM/mock 返回特定字段；缺少稳定规则或服务层统一入口。
  - 问答记录没有学生维度，也不会回写画像。
  - `events/demo-quiz` 写入测评提交和事件，但没有真正更新 `StudentProfile`，描述中“反馈到画像”与代码行为不完全一致。
  - 没有画像变更历史表，只有路径调整日志；无法审计画像每次变化前后的字段差异。
- 风险等级：中
- 建议修改方式：
  - 增加统一 `profile_update_service`，由测评、学习记录、问答记录、资源完成情况共同调用。
  - 增加 `profile_change_logs` 或在现有事件表中结构化记录字段级 diff、来源、置信度。
  - 问答和学习进度表补充 `user_id/student_profile_id` 后再参与画像更新。
- 是否建议立即修复：是

## 7. 画像影响学习路径

- 模块名称：画像驱动学习路径
- 当前实现状态：部分实现
- 相关文件：
  - `backend/app/api/routers/learning_paths.py`
  - `backend/app/services/learning_path_service.py`
  - `backend/app/services/demo_learning_service.py`
  - `backend/app/services/mock_llm.py`
  - `frontend/src/views/StudentLearningPath.vue`
  - `frontend/src/views/LearningPath.vue`
- 存在问题：
  - 真实生成接口 `/api/v1/learning-paths/generate` 根据 `profile_id` 查询 `StudentProfile`，并把 `profile.profile_json` 传给 `llm_service.generate_json("learning_path", ...)`。
  - mock LLM 的路径生成会读取 `learning_goal` 和 `weak_points`，不同画像理论上会生成不同推荐理由和阶段内容。
  - demo 推荐接口 `/api/v1/learning-paths/recommend` 和 `/api/v1/student/learning-tasks` 使用 `demo_learning_service.build_learning_tasks(user_id=...)`，三个 demo 用户会返回不同路径。
  - 学生端 `StudentLearningPath.vue` 走 `/api/v1/student/learning-tasks?user_id=...`，主要读取内置 demo 数据，不读取数据库中通过对话保存的画像。
  - `/api/v1/learning-paths` 带 `user_id` 时同样返回 demo 任务；不带时返回全部真实路径，缺少按当前用户过滤。
- 风险等级：中
- 建议修改方式：
  - 学生端路径页优先获取当前用户最新画像，再调用真实路径生成/读取接口。
  - `learning-paths` 列表接口支持 `user_id/student_id` 查库过滤，demo fallback 只在没有真实数据时启用。
  - 建立“画像变更后路径失效/重算”的明确触发规则。
- 是否建议立即修复：是

## 8. 画像影响资源推荐

- 模块名称：画像驱动资源推荐与资源生成
- 当前实现状态：部分实现
- 相关文件：
  - `backend/app/api/routers/resources.py`
  - `backend/app/services/demo_learning_service.py`
  - `backend/app/services/personalization_service.py`
  - `backend/app/services/mock_llm.py`
  - `backend/app/agents/resource_agent.py`
  - `frontend/src/views/StudentAssistant.vue`
  - `frontend/src/views/ResourceGenerate.vue`
- 存在问题：
  - 真实接口 `/api/v1/resources/generate` 可传 `student_profile_id`，会读取画像和最新学习路径，再调用 `llm_service.generate_json("resources", ...)`。
  - mock 资源生成会读取画像 `weak_points` 和路径 `goal`，推荐理由包含薄弱点和学习目标。
  - `/api/v1/resources/generate-pack` 在传 `studentId` 时走 `demo_learning_service.build_resource_pack`，会按 demo 用户和弱点生成不同资源包。
  - `StudentAssistant.vue` 会先运行画像，再把画像薄弱点传入资源包生成接口，具备演示链路。
  - `ResourceGenerate.vue` 只加载 `/api/v1/resources` 全量资源，不带当前用户或画像筛选，也没有触发按当前画像生成。
  - 资源列表接口 `/api/v1/resources` 仅支持 `course_id`，不支持 `user_id/student_profile_id` 查询过滤。
- 风险等级：中
- 建议修改方式：
  - 资源列表和生成接口都支持当前用户上下文，学生端默认只看自己的推荐资源。
  - 对资源生成入参统一使用 `student_profile_id` 或 `user_id`，减少 `studentId`、`student_profile_id`、手动 `weakPoints` 混用。
  - 资源推荐应记录推荐依据：画像字段、路径阶段、最近测评/问答证据。
- 是否建议立即修复：是

## 总体结论

当前项目已经具备“可演示”的对话画像、demo 用户差异、画像驱动路径与资源生成雏形；但核心链路仍主要依赖内置 demo 数据、页面手动传参和 `student_profile_id`，没有形成统一的真实用户上下文。若目标是交付“不同登录用户拥有不同画像，并由画像持续影响学习路径和资源推荐”的产品级闭环，建议优先修复用户身份模型、画像归属、问答/测评/资源数据的 user_id 隔离，以及画像变更记录。
