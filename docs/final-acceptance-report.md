# EduMind 当前验收报告

> 验收日期：2026-07-16
> 分支：`submission-materials-20260716`
> 代码基线：`4d8b658`
> 核心功能提交：`43f49d6`

本报告只记录实际运行或代码/自动测试已证明的事实。统一表述规则见 [fact-baseline.md](fact-baseline.md)。

## 验收结论

当前版本具备可运行的本地演示闭环。后端全量自动化测试、安全回归、前端生产构建、API 演示链路、页面壳、离线/在线就绪和小规模 RAG 回归评价均已执行。教师三类仲裁已在 Q014 限定范围完成人工回归；真实讯飞、Docker 动态部署、微信真机和 Python 3.11 + Node 20 干净机部署尚未验证。

## 运行结果

| 验收项 | 命令或入口 | 结果 | 范围说明 |
|---|---|---:|---|
| Python 编译 | `python -m compileall backend/app` | 通过 | 语法/编译检查 |
| 后端测试 | `python -m pytest backend/tests -q` | 323/323 通过 | 单元、服务和部分集成测试 |
| 前端安装 | `npm.cmd ci` | 通过 | 58 packages；当次 audit 为 0 vulnerabilities |
| 前端构建 | `npm.cmd run build` | 通过 | 797 modules；类型检查和 Vite 构建 |
| API E2E | `scripts/e2e_demo_flow_check.py` | 16/16 通过 | 演示 API 链路 |
| Web 页面壳 | `scripts/check_demo_pages.py` | 14/14 通过 | 页面壳可访问，不是完整 UI 自动化 |
| 离线就绪 | `scripts/check-demo-ready.py --skip-http` | 39/39 通过 | 本地数据、文件、源码契约和脚本 |
| 在线就绪 | `scripts/check-demo-ready.py` | 72/72 通过 | 本地 HTTP；不含真实讯飞云验证 |
| A3 检查 | `scripts/check-a3-program.py` | 33 PASS / 1 WARN / 0 FAIL | WARN 为项目 `.venv` 不存在 |
| RAG 回归 | `scripts/eval_retrieval.py` | 成功 | 评价集 5 条 |
| Agent 真图 | `run_full_learning_graph` | 进入 pending_review | 3 次重试后到 TeacherArbitration |
| OpenAPI | `/openapi.json` | 111 paths / 117 operations | operation 不是功能数 |

## Warning 说明

最终冻结验收记录为后端全量 `323 passed / 2696 warnings`，Q012—Q015 及 Q018 安全回归为 `241 passed / 2573 warnings`。warning 数量是当前测试路径触发结果，不能作为功能数量或生产质量声明。

当前 warning 分类：

- FastAPI/Starlette TestClient 与 httpx 兼容弃用：1 次。
- SQLAlchemy 模型默认值中 `datetime.utcnow()` 弃用：24 次。
- 项目自身 `datetime.utcnow()` 弃用：108 次，集中在 Agent workflow、governance、DKVMN、profile 和 report 服务。
- 未观察到独立的 Pydantic warning 或 pytest 框架 warning。

这些 warning 当前不阻断交付演示，但 Python 3.13 已明确提示未来移除风险，应在后续核心代码维护中迁移为 timezone-aware UTC。

完整分类见 `交付成果_最新版/01_验收日志/warnings分类说明.md`。

## 已验证能力

- 12 节点 Agent 图工作流及 pass/retry/arbitration 条件路由。
- Agent 运行持久化、pending_review 暂停和教师决策续跑。
- ResourceAgent 消费重试上下文和教师修订内容。
- 课程向量/混合 RAG 优先与 JSON+TF-IDF fallback。
- 引用、置信度、课程对齐、证据覆盖和边界告警。
- 轻量在线门控记忆知识追踪和画像/路径联动。
- 七维审核、重试回流、教师仲裁和审计日志。
- 9 类资源生成目录及音视频 fallback。

## RAG 评价

| 指标 | 值 |
|---|---:|
| Dataset size | 5 |
| MRR | 1.0000 |
| Recall@K | 1.0000 |
| NDCG@K | 0.9751 |
| Precision@K | 0.8267 |
| CoverageRate | 0.6800 |

该结果用于回归测试和演示验证，不足以代表复杂真实教学场景的泛化效果。Precision@K 和 CoverageRate 仍有改进空间。

## 外部能力状态

- 当前 LLM 模式：mock。
- 讯飞 TTS、Spark、安全：本轮未配置真实凭据，真实云调用未验证。
- FFmpeg：可选；未安装时返回 HTML 动画、视频脚本和其他 fallback。
- Chroma/SentenceTransformer：可选；本轮特定 E2E RAG 请求走 JSON/TF-IDF fallback。
- Docker：Compose/Dockerfile 静态检查通过；当前环境无 Docker CLI，动态构建和启动未验证。

## 尚未验证

- 教师 approve/revise/reject 三类完整 UI 人工演练。
- Web 三角色逐按钮、权限、视觉和响应式回归。
- 微信开发者工具和真机。
- Python 3.11 + Node 20 全新机器从零部署。
- Docker Compose 构建、启动和健康检查。
- 真实讯飞云请求。
- 压力、并发、长稳、安全渗透和生产数据评估。

## 验收边界

“323 项后端自动化测试全部通过”不等于系统全部质量无风险；“在线就绪 72/72”不等于真实讯飞成功；“117 个 HTTP operation”不等于 117 项核心功能；5 条 RAG 评价不能宣传为大规模准确率。
