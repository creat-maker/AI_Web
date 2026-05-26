# EduMind

EduMind 是一个面向个性化学习资源生成与学习多智能体流程的 MVP 项目。当前版本重点跑通教师建课、课程资料上传、知识库构建、学生画像、学习路径生成、资源生成、RAG 答疑、测验评价和学习报告导出的演示闭环。

项目默认支持无真实大模型密钥的 mock 模式，便于本地开发、课堂演示和 GitHub 协作。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Vue Router
- 后端：FastAPI、SQLAlchemy、Pydantic Settings
- Agent：LangGraph、LangChain 生态
- RAG：Chroma，带本地 fallback 能力
- 数据库：SQLite 演示模式，保留 MySQL 初始化脚本
- 大模型：DeepSeek / 通义千问 OpenAI-compatible API，可通过环境变量配置
- 报告：docxtpl、python-docx

## 功能模块

- 课程管理：创建课程并查看课程数据
- 知识库：上传课程资料，解析后写入向量库
- 学生画像：采集学生基础信息并生成画像
- 学习路径：生成个性化学习路径
- 资源生成：生成讲解、练习、学习材料等资源
- 智能答疑：基于课程知识库进行 RAG 问答，并保存最近问答记录
- 测验评价：提交测验答案并返回评分和错因分析
- 教师分析：展示测评次数、平均得分、薄弱知识点、学生表现分布和教学建议
- 报告中心：生成并下载 Word 学习报告
- Agent 工作流：串联画像、规划、资源、评价和报告流程

## 项目目录结构

```text
EduMind/
|-- backend/                 FastAPI 后端服务
|   |-- app/                  后端应用代码
|   |-- requirements.txt      Python 依赖
|   `-- storage/              本地运行时数据目录，默认不提交真实数据
|-- frontend/                Vue 3 前端应用
|   |-- src/                  前端源码
|   |-- package.json          前端脚本和依赖
|   `-- vite.config.ts        Vite 开发代理配置
|-- database/                数据库初始化脚本
|-- docs/                    后续项目文档
|-- demo/                    后续演示材料
|-- sample_data/             后续示例数据
|-- scripts/                 后续辅助脚本
|-- legacy/                  旧项目代码隔离区，不进入主流程
|-- .env.example             环境变量模板
|-- .gitignore               Git 忽略规则
`-- README.md                项目说明
```

## 环境变量配置方法

复制环境变量模板：

```bash
copy .env.example .env
```

macOS / Linux 可使用：

```bash
cp .env.example .env
```

常用变量说明：

```env
DATABASE_URL=
SQLITE_FALLBACK_PATH=./backend/storage/eduagent.sqlite3
LLM_PROVIDER=mock
DEEPSEEK_API_KEY=
DASHSCOPE_API_KEY=
QWEN_API_KEY=
CHROMA_PERSIST_DIR=./backend/storage/chroma
UPLOAD_DIR=./backend/storage/uploads
REPORT_DIR=./backend/storage/reports
CORS_ORIGINS=http://localhost:5173
VITE_API_BASE_URL=
```

说明：

- 不配置真实 API Key 时，后端使用 mock 模式。
- `DATABASE_URL` 为空时默认使用 SQLite。
- 后端读取项目根目录 `.env`。
- `UPLOAD_DIR`、`REPORT_DIR`、`CORS_ORIGINS` 会被后端配置读取。
- `VITE_API_BASE_URL` 本地开发可留空，前端通过 Vite proxy 访问后端；生产或非代理场景可通过 shell 环境变量或 `frontend/.env.local` 配置。
- 不要提交 `.env` 或任何包含真实密钥的文件。

## 后端启动步骤

在项目根目录打开终端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

macOS / Linux 激活虚拟环境：

```bash
source .venv/bin/activate
```

健康检查：

```text
http://localhost:8000/health
```

## 前端启动步骤

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

前端本地开发时，`/api` 和 `/health` 会代理到 `http://localhost:8000`。

## 常见问题

### 如何上传资料并检索知识库？

进入「知识库」页面，先选择课程，再拖拽或点击选择 PDF、Word、PPT、TXT 或 Markdown 资料，点击「上传并构建知识库」。解析完成后，页面会显示文档状态、知识切片数量和最近上传时间。

在「检索测试」区域输入关键词，点击「检索知识片段」，可查看来源文档、相似度分数和命中的知识片段。若检索无结果，先确认该课程已有已解析文档。

### 如何查看学情分析？

进入「教师分析」页面，可查看测评次数、参与学生数、平均得分、薄弱知识点、学生表现分布、教学建议和最近测评/报告记录。若真实测评数据不足，页面会使用兼容展示数据保证演示不空白。

### 没有大模型 API Key 能不能运行？

可以。保持 `LLM_PROVIDER=mock`，或不填写对应 API Key，后端会进入演示 mock 模式。

### 本地数据库在哪里？

默认 SQLite 文件在 `backend/storage/eduagent.sqlite3`。该文件属于运行时数据，不应提交到 GitHub。

### 上传文件、报告和向量库是否需要提交？

不需要。`backend/storage/` 和 `storage/` 下的上传文件、报告文件、向量库文件和日志都应作为本地运行时数据处理。

### 前端请求不到后端怎么办？

先确认后端 `http://localhost:8000/health` 可访问，再确认前端通过 `npm run dev` 启动。生产部署时需要按实际后端地址配置 `VITE_API_BASE_URL`。

### Windows 终端中文显示乱码怎么办？

源码按 UTF-8 保存。若 PowerShell 显示乱码，可尝试切换终端编码或使用支持 UTF-8 的终端。

## GitHub 协作开发流程

1. 从远程仓库拉取最新代码。
2. 基于 `main` 或团队指定分支创建功能分支。
3. 本地完成修改，并确认没有提交 `.env`、数据库、日志、上传文件、构建产物和依赖目录。
4. 运行必要的本地检查，例如后端启动、前端构建或页面联调。
5. 提交代码并推送到远程功能分支。
6. 发起 Pull Request，说明修改内容、验证方式和潜在影响。
7. 通过代码审查后合并。

## 分支说明

- `main`：稳定分支，保存可演示、可交付版本。
- `dev`：集成开发分支，用于合并阶段性功能。
- `feature/<name>`：功能开发分支。
- `fix/<name>`：缺陷修复分支。
- `docs/<name>`：文档修改分支。

## 提交信息规范

建议使用简洁的类型前缀：

```text
feat: add course import flow
fix: handle empty quiz answer
docs: update local setup guide
chore: improve gitignore rules
refactor: simplify report generation helper
test: add API smoke tests
```

常用类型：

- `feat`：新增功能
- `fix`：修复问题
- `docs`：文档变更
- `chore`：构建、配置、依赖、脚本等杂项
- `refactor`：不改变行为的代码重构
- `test`：测试相关修改

## 当前边界

当前阶段聚焦 MVP 演示闭环，不包含数字人视频生成、AR/VR、全网爬虫、复杂 OCR 阅卷、移动端、真实消息推送和复杂在线判题系统。
