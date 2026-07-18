# EduMind 已知限制

EduMind 当前是软件杯工程演示版本，目标是可运行、可解释、可演示和可测试，不宣称为完整商业生产系统。

## 尚未完成的人工与环境验收

- 教师 approve/revise/reject 三类 UI 已在 Q014 限定范围完成人工回归，但服务端课程授权仍是显式演示映射，不代表生产级跨班隔离。
- Web 学生、教师、管理员三角色尚未完成全部页面逐按钮、视觉和响应式穷举回归。
- 微信小程序尚未在开发者工具和真机验收。
- Docker Compose 已完成静态解析和文件存在检查；由于当前环境无 Docker CLI，动态构建与启动尚未验证。
- 尚未在 Python 3.11 + Node 20 的全新机器完成从零部署。
- 真实讯飞 TTS、Spark 和安全云调用尚未验证。

## DKVMN

当前实现是轻量在线门控记忆知识追踪，包含 softmax key 寻址、动态 value memory、erase/add 门控、掌握度更新、强弱项识别和画像映射。

没有论文规模训练数据、预训练 checkpoint 或论文级效果评估，因此不宣称复现 DKVMN 论文指标，也不称为训练完成的生产模型。

## RAG

- 检索优先使用课程向量/混合路径，无可用向量项时回退 JSON+TF-IDF。
- 本轮回归评价集只有 5 条，仅用于链路回归和演示验证。
- MRR、Recall@K、NDCG@K 不能宣传为大规模准确率。
- Precision@K 0.8267 和 CoverageRate 0.68 表明检索精度与证据覆盖仍有改进空间。
- 在线单次请求的引用数和置信度会随数据状态变化，不是固定产品指标。

## 外部 AI

默认 LLM 模式为 mock。DeepSeek、Qwen/DashScope 和讯飞工具均需单独配置。讯飞 TTS/Spark/安全适配器的 `not_configured` 或 fallback 状态不等于真实云调用成功。

当前主 LLM provider 不包含 xfyun，不能使用 `LLM_PROVIDER=xfyun` 作为有效配置。

## 多模态资源

当前资源生成目录为 9 类。TTS、MP4 等资源依赖外部服务或 FFmpeg；未配置时返回文本、HTML 动画、视频脚本或任务状态等 fallback，不应宣传为所有音视频均已真实生成。

## 接口数量

本轮 OpenAPI 统计为 111 个路径和 117 个 HTTP operation。该数量用于接口契约统计，不代表用户功能数量或核心创新数量。

## 依赖与兼容性

- 后端 requirements 多数未精确 pin，干净环境复现仍有依赖漂移风险。
- 第一轮测试产生 2696 warnings，第二轮复验产生 2696 warnings；差异来自触发次数。
- warnings 主要涉及 TestClient/httpx 兼容以及 `datetime.utcnow()` 在 Python 3.13 的弃用。
- 当前不阻断演示，但应在后续核心代码维护中处理。

## 数据与安全

- 本地演示数据库记录数会随初始化和 E2E 变化，不能作为固定平台规模。
- `.env`、`xfyun.env`、数据库、日志、缓存和媒体运行产物不得进入交付包。
- 当前审计日志提供工程追踪，不等同于不可篡改审计或第三方合规认证。
