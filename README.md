# EduAgent Studio

EduAgent Studio 是面向中国软件杯 A3 赛题「基于大模型的个性化资源生成与学习多智能体系统开发」的第一版 MVP。

项目目标是跑通一条可演示闭环：教师创建课程，上传课程资料并建立 Chroma 知识库，学生填写基础问卷，系统通过 LangGraph 多智能体流程生成学生画像、个性化学习路径、学习资源、RAG 答疑、测验评价和 Word 学习报告。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript
- 后端：FastAPI + SQLAlchemy
- Agent：LangGraph + LangChain 生态依赖
- RAG：Chroma
- 数据库：SQLite 演示模式，保留 MySQL 初始化脚本
- 大模型：DeepSeek / 通义千问 OpenAI-compatible API，可配置；无 Key 自动进入 mock 模式
- 报告：docxtpl + python-docx

## 目录

```text
backend/                 FastAPI 后端
frontend/                Vue3 前端
database/init_mysql.sql  MySQL 初始化脚本
legacy/                  旧项目代码隔离区，不进入主路由
backend/storage/         SQLite、上传文件、Chroma 和报告输出
```

## 环境配置

复制 `.env.example` 为 `.env`，按需填写：

```env
DATABASE_URL=
SQLITE_FALLBACK_PATH=./backend/storage/eduagent.sqlite3
DEEPSEEK_API_KEY=
DASHSCOPE_API_KEY=
QWEN_API_KEY=
LLM_PROVIDER=mock
CHROMA_PERSIST_DIR=./backend/storage/chroma
```

没有 API Key 时后端不会崩溃，会显示并使用「演示 mock 模式」。

## 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：`http://localhost:8000/health`

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：`http://localhost:5173`

## MVP 演示流程

1. 在「课程管理」创建《Python 程序设计》。
2. 在「知识库」上传 Python 爬虫基础资料，系统解析并写入 Chroma。
3. 在「学生画像」填写张三的基础问卷。
4. 在「Agent 工作流」运行完整学习流。
5. 在「智能答疑」基于课程知识库提问，并查看引用来源。
6. 在「测验评价」提交测验答案，查看得分和错因分析。
7. 在「报告中心」下载 Word 学习报告。
8. 回到 Dashboard 查看真实数据库统计。

## 当前边界

第一阶段不包含数字人视频生成、AR/VR、全网爬虫、复杂 OCR 阅卷、移动端、真实消息推送和复杂在线判题系统。
