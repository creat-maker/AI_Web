# EduMind 个性化学习多智能体系统

EduMind 面向软件杯个性化学习多智能体场景，围绕“学生画像—课程检索—资源生成—测验反馈—路径调整—教师仲裁—报告与审计”构建可运行、可解释、可降级的教学辅助闭环。

当前代码基线为 `4d8b658`，核心 Agent、RAG 与治理实现来自 `43f49d6`。本文档是项目最新版唯一入口；所有材料数字应以 [统一事实基线](docs/fact-baseline.md) 和实际验收日志为准。

## 当前状态

| 能力 | 当前状态 | 表达边界 |
|---|---|---|
| 后端 | FastAPI 服务、数据库、业务接口和测试可运行 | 323 项后端自动化测试全部通过，不代表系统不存在质量风险 |
| Web | Vue 3 学生、教师、管理员角色页面可构建 | 生产构建和 14 个页面壳检查通过；三角色完整人工 UI 回归尚未完成 |
| 微信小程序 | 7 个学生端页面及后端失败 fallback 已实现 | 尚未完成微信开发者工具和真机验收 |
| Agent | 12 节点图工作流、重试、暂停、教师仲裁和续跑已实现 | 自动测试通过；approve/revise/reject 三类 UI 已在 Q014 限定范围完成人工回归；服务端课程授权为显式演示映射 |
| RAG | 课程向量/混合检索优先，JSON+TF-IDF 稳定降级 | 5 条小规模回归评价，仅用于链路回归和演示验证 |
| DKVMN | 轻量在线门控记忆知识追踪 | 无预训练检查点、训练实验和论文级效果验证 |
| 外部 AI | LLM 与讯飞工具可选配置 | 当前验收为 mock 模式；真实讯飞云调用未验证 |
| Docker | 仓库含 Compose/Dockerfile，静态解析检查通过 | 当前验收环境无 Docker CLI，动态构建和启动未验证 |

## 产品范围

### Web 学生端

- 学生画像与对话式补全
- 学习路径和任务
- 课程知识与 RAG 问答
- 多模态资源预览
- 测验、错因反馈与学习报告

### Web 教师端

- 课程、学情、画像与学习路径管理
- 教学资源生成和任务布置
- 高风险内容仲裁
- approve、revise、reject 决策入口
- 报告与干预信息

### Web 管理员端

- 系统状态与演示能力检查
- 知识库、内容审核和平台治理
- Agent 工作流与审计日志
- 用户、课程和报告管理

### 微信小程序学生端

`miniprogram/app.json` 当前注册 7 个页面：home、path、resources、tutor、quiz、report、profile-dialog。页面优先请求后端，失败时可回退本地演示数据。真机状态尚未验证。

## 技术架构

- 后端：FastAPI、SQLAlchemy、Pydantic、SQLite 演示数据库
- Agent：LangGraph 12 节点图工作流
- RAG：课程向量/混合检索、TF-IDF embedding、课程语义约束、JSON fallback；Chroma 为可选能力
- 知识追踪：轻量在线门控 Key-Value Memory 更新
- 前端：Vue 3、TypeScript、Vite、Vue Router、ECharts
- 移动端：原生微信小程序 WXML/WXSS/JavaScript
- 外部能力：DeepSeek/Qwen/DashScope LLM、讯飞 TTS/Spark/安全适配器、FFmpeg、SentenceTransformer，均为可选配置

详细架构见 [docs/architecture.md](docs/architecture.md)。

## 12 节点 Agent 工作流

当前 `backend/app/agents/graph.py` 注册以下节点：

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

主链为：

```text
Profile -> Knowledge -> Planner -> ResourcePlanner -> Resource
        -> Tutor -> Evaluator -> Audit -> Compliance
```

ComplianceAgent 根据审核结果进入 ReporterAgent、AuditRetry 或 TeacherArbitration。中风险内容最多回流 ResourceAgent 3 次；高风险或重试仍未通过时，运行持久化为 `pending_review`，等待教师决策：

- approve：进入 ReporterAgent 并完成报告。
- revise：携带教师意见回到 ResourceAgent，再生成并复审。
- reject：阻断发布并结束运行。

12 节点图和三种决策路由已通过自动测试；教师端完整人工 UI 演练尚待完成。

## RAG 与降级路径

RAG 问答入口为 `POST /api/v1/rag/ask`。

```text
课程查询
  -> 已导入课程向量/混合检索
  -> 课程语义约束与证据重排
  -> 引用、置信度、课程边界和检索调试信息
  -> 无可用向量项时回退 JSON + TF-IDF/关键词检索
  -> 证据不足或超出课程范围时返回明确 fallback_reason
```

内置 `TfidfEmbeddingProvider` 支持中英文轻量特征；SentenceTransformer 是可选适配器。本项目不把 fallback 描述为向量检索成功，也不把单次引用数量当作固定指标。

当前回归评价集只有 5 条：

| 指标 | 本轮结果 |
|---|---:|
| MRR | 1.0000 |
| Recall@K | 1.0000 |
| NDCG@K | 0.9751 |
| Precision@K | 0.8267 |
| CoverageRate | 0.6800 |

这些结果只用于回归测试和演示验证，不代表复杂真实教学场景中的大规模准确率或泛化效果。详见 [reports/retrieval_eval_report.md](reports/retrieval_eval_report.md)。

## 轻量知识追踪边界

`backend/app/services/dkvmn_tracker.py` 实现了 softmax key 寻址、按学生维护的 value memory、erase/add 门控更新、掌握度估计、强弱项识别和六维画像映射。

准确表述是“轻量在线门控记忆知识追踪实现”。当前没有预训练检查点、论文规模训练数据或论文级模型效果验证，不宣称完成论文复现或训练出生产级 DKVMN 模型。

## 治理与教师仲裁

系统采用本地规则审核、可选讯飞安全适配、课程证据检查、重试回流、教师仲裁和 AuditLog 记录。进入待仲裁状态时不会提前生成最终报告。

审计日志用于演示和工程追踪，不等同于第三方合规认证或不可篡改审计系统。

## 推荐环境

正式提交和干净环境复验推荐：

- Windows 10/11
- Python 3.11.x（已在 3.11.9 干净 venv 中完成后端依赖安装与启动复验）
- Node.js >=20（前端锁文件使用 `npm ci`；本轮实际构建验证版本为 Node.js 24.14.0）
- npm 使用 `frontend/package-lock.json` 对应的 `npm ci`

本轮全量测试环境为 Python 3.13.9、Node.js 24.14.0、npm 11.9.0；最终压缩前已补充 Python 3.11.9 干净 venv 后端依赖安装和 18006 端口启动复验。`py -0p` 只作为 Python Launcher 注册状态参考，不作为项目启动硬门槛。关键依赖实测版本见 [docs/environment-baseline.md](docs/environment-baseline.md)。

## 首次安装

在仓库根目录执行：

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt

cd frontend
npm.cmd ci
cd ..

copy .env.example .env
python scripts\seed_demo_data.py
```

PowerShell 若因执行策略无法运行 `npm.ps1`，请使用 `npm.cmd`。

## 快捷启动

依赖已经安装并初始化后，可以运行：

```bat
START_EDUMIND.bat
```

`START_EDUMIND.bat` 是 Windows 兼容入口，内部调用同目录 `start-dev.bat`；该启动链路是“已安装环境下的快捷启动”，不会创建虚拟环境，也不会自动安装 Python/npm 依赖。停止服务使用 `stop-dev.bat`。

## 手动启动

后端：

```bat
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bat
cd frontend
npm.cmd run dev
```

默认地址：

- 后端健康检查：<http://127.0.0.1:8000/health>
- OpenAPI：<http://127.0.0.1:8000/docs>
- Web：<http://127.0.0.1:5173>

如果系统代理拦截 localhost 请求，请设置：

```bat
set NO_PROXY=127.0.0.1,localhost
set no_proxy=127.0.0.1,localhost
```

## 离线验收与测试

无需真实密钥的离线就绪检查：

```bat
docs\check-demo-ready.bat
```

等价命令为 `python scripts\check-demo-ready.py --skip-http`。

其他验收：

```bat
python -m compileall backend\app
python -m pytest backend\tests -q

cd frontend
npm.cmd run build
cd ..

python scripts\eval_retrieval.py
```

后端与前端服务启动后，可执行：

```bat
python scripts\e2e_demo_flow_check.py --base-url http://127.0.0.1:8000/api/v1
python scripts\check_demo_pages.py
python scripts\check-demo-ready.py
```

## 当前验证结果

| 验收项 | 已验证结果 | 范围 |
|---|---:|---|
| 后端自动化测试 | 323/323 通过 | 单元/服务/部分集成测试；存在弃用 warnings |
| API E2E | 16/16 通过 | 演示 API 链路，不是浏览器自动化 |
| Web 页面壳 | 14/14 通过 | 页面可访问壳，不等于完整 UI 验收 |
| 离线就绪检查 | 39/39 通过 | 数据、文件、源码契约和脚本 |
| 在线就绪检查 | 72/72 通过 | 本地 HTTP 服务；不等于真实讯飞成功 |
| 前端生产构建 | 通过 | 797 modules |
| RAG 回归评价 | 5 条数据集运行成功 | 小规模回归与演示验证 |
| OpenAPI | 111 个路径、117 个 HTTP operation | operation 数量不是用户功能数量 |

最终冻结验收记录为后端全量 `323 passed / 2696 warnings`；Q012—Q015 及 Q018 安全回归为 `241 passed / 2573 warnings`。warnings 主要是第三方兼容弃用和项目内 `datetime.utcnow()` 弃用，数量会受测试路径影响，不能作为功能数量或质量无风险声明。

## 讯飞配置

当前代码从仓库根目录未跟踪的 `.env` 或进程环境变量读取讯飞配置；`xfyun.env` 可作为本地受忽略密钥文件保存，但需要人工加载为环境变量或复制为同样受忽略的 `.env` 后再启动。只复制模板，不要提交真实文件：

```dotenv
XFYUN_ENABLED=true
XFYUN_APP_ID=your_app_id
XFYUN_API_KEY=your_api_key
XFYUN_API_SECRET=your_api_secret
```

配置后重启后端，先访问 `GET /api/v1/xfyun/status`。TTS 调用入口为 `POST /api/v1/xfyun/tts`。

注意：

- 当前主 LLM provider 只支持 `mock`、`deepseek`、`qwen`、`dashscope`；不要设置 `LLM_PROVIDER=xfyun`。
- 讯飞 Spark 当前具备配置状态与签名 URL 构造能力，尚未形成当前 main 中可直接执行的完整实调脚本。
- 讯飞 TTS 具备 WebSocket 调用实现和 `/api/v1/xfyun/tts` 路由，但最终冻结前未使用真实凭据实调。
- 讯飞云安全审核当前为配置/状态占位，不应描述为真实云审核已调用。
- 当前仓库验收未配置真实讯飞凭据，真实云调用状态是“尚未验证”。
- status 中的 `not_configured` 或本地 fallback 不能写成云调用成功。

## Mock 与真实云调用

默认 `LLM_PROVIDER=mock`。mock 模式使用本地规则、模板、TF-IDF、JSON 知识库和演示数据，目的是在无外网或无密钥环境中保持链路可运行。

真实云调用必须同时满足：对应 provider 和凭据已配置、状态明确为 configured、实际请求收到云端成功响应，并且日志不泄露密钥。页面可用、在线就绪 72/72 或 fallback 成功，都不能替代真实云调用验证。

## 已知限制

- 教师 approve/revise/reject 三类 UI 已在 Q014 限定范围完成人工回归；服务端课程授权为显式演示映射，不代表生产级跨班隔离。
- 微信小程序开发者工具和真机尚未验证。
- Docker 静态检查通过，构建与 Compose 启动尚未验证。
- 全新机器从零安装尚未验证。
- 真实讯飞云调用尚未验证。
- RAG 评价集只有 5 条。
- DKVMN 没有预训练检查点和论文级效果。
- 后端 requirements 尚未精确锁定全部版本。

详见 [docs/known-limitations.md](docs/known-limitations.md)。

## 安全与密钥

- 真实密钥只允许通过未跟踪的 `.env` 或临时环境变量注入。
- `.env`、`xfyun.env`、`*.env`、私钥和常见本地凭据文件均应被 `.gitignore` 排除。
- `.env.example` 只能保留空值或占位符。
- 微信小程序配置模板为 `project.config.example.json`，使用 `touristappid`；根目录真实 `project.config.json` 不进入官网源码包。
- 不把数据库、虚拟环境、node_modules、缓存、日志、媒体运行产物或真实用户数据放入交付包。
- `sample_data/` 含第三方扩展课程资料和教程示例，默认排除出官网源码包；如未来需要分发，必须先完成来源、许可证、授权和署名确认。
- 提交前执行 `git check-ignore -v .env xfyun.env` 和脱敏扫描。

## 最终材料入口

- 第一轮事实基线与验收：[交付成果_最新版](交付成果_最新版/)
- 统一事实引用规范：[docs/fact-baseline.md](docs/fact-baseline.md)
- 环境版本基线：[docs/environment-baseline.md](docs/environment-baseline.md)
- 架构说明：[docs/architecture.md](docs/architecture.md)
- 验收报告：[docs/final-acceptance-report.md](docs/final-acceptance-report.md)
- 已知限制：[docs/known-limitations.md](docs/known-limitations.md)
