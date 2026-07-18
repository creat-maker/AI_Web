# EduMind 环境版本基线

## 推荐提交环境

| 组件 | 推荐版本 | 依据 |
|---|---|---|
| Python | 3.11.x | GitHub Actions 当前使用 3.11；适合作为正式复验基线 |
| Node.js | >=20 | GitHub Actions 当前使用 Node 20；本地最终构建复验使用 Node 24.14.0 |
| npm | 随 Node 配套版本 | 安装必须使用 `npm ci` 和 package-lock |
| OS | Windows 10/11 | BAT 和本地演示流程主要面向 Windows |

## 2026-07-16 本轮实测环境

| 组件 | 实测版本 |
|---|---:|
| Python | 3.13.9 |
| pip | 25.2 |
| FastAPI | 0.138.0 |
| pytest | 9.1.1 |
| SQLAlchemy | 2.0.51 |
| Pydantic | 2.12.3 |
| LangGraph | 1.2.6 |
| Chroma | 1.5.9 |
| Node.js | 24.14.0 |
| npm | 11.9.0 |

上述实测环境完成了后端全量 323 项测试、Q012—Q015 及 Q018 安全回归、前端生产构建、API E2E、页面壳和 readiness 检查。最终压缩前已补充 Python 3.11.9 干净 venv 后端依赖安装、18006 端口启动、`/health`、三角色登录和离线 readiness 复验；前端生产构建使用 Node.js 24.14.0 完成，Node 20 不再作为压缩硬门槛。

## 依赖管理现状

- 前端存在 `frontend/package-lock.json`，使用 `npm ci`。
- 后端 `backend/requirements.txt` 已固定直接依赖版本，版本来源为当前通过 323 项后端测试的顶层依赖集合，并在 Python 3.11.9 干净 venv 中完成安装复验。
- 未把全局 `pip freeze` 全量复制进 requirements；未加入未使用的大型依赖。
- `py -0p` 仅反映 Python Launcher 注册状态。只要明确使用 Python 3.11 解释器路径创建 venv，并由该 venv 的 `python.exe` 启动服务，即可满足本项目干净后端复验要求。

## 本地环境注意事项

- 项目根当前没有固定 `.venv`，首次安装建议自行创建。
- PowerShell 可能阻止 `npm.ps1`，可改用 `npm.cmd`。
- 若系统代理接管 localhost，请设置 `NO_PROXY=127.0.0.1,localhost`。
- 当前环境没有 Docker CLI；Docker Compose 已完成静态解析和文件存在检查，但动态 build/up/健康检查未验收。
- 真实密钥只通过根 `.env` 或临时环境变量注入，不写入仓库。
