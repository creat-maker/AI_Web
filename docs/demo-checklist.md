# EduMind 比赛演示与验收手册

## 演示前准备

1. 安装依赖：后端 `pip install -r backend/requirements.txt`，前端 `cd frontend && npm install`。
2. 初始化演示数据：`python scripts/seed_demo_data.py`。
3. 启动服务：后端 `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`，前端 `npm run dev`。
4. 打开 `/demo-status`，确认三端路线、能力清单和最近验收结果。

## 一键脚本

```bat
seed-demo-data.bat
check-demo-ready.bat
start-dev.bat
stop-dev.bat
```

## 核心检查命令

```bash
python scripts/check-demo-ready.py
python scripts/e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports/demo_flow_check.md
cd frontend && npm run build
```

## 必验路由

- 学生端：`/student`、`/student/courses`、`/student/learning-path`、`/student/assistant`、`/student/knowledge`、`/student/exams`、`/student/reports`
- 教师端：`/teacher`、`/courses`、`/profiles`、`/learning-path`、`/teacher-analysis`、`/reports`
- 管理员端：`/dashboard`、`/admin/users`、`/admin/courses`、`/admin/reports`、`/admin/knowledge`、`/resource-generation`、`/agent-workflow`、`/logs`、`/settings`
- 验收页：`/demo-status`

## 推荐讲解顺序

学生端：学习总览 -> 我的课程 -> 学习路径 -> 智能答疑 -> 测验成绩 -> 学习报告。

教师端：班级概览 -> 课程管理 -> 学生画像 -> 学习路径与任务布置 -> 测评分析 -> 报告中心。

管理员端：平台总览 -> 用户与角色 -> 课程治理 -> AI 资源生成 -> Agent 工作流 -> 日志管理 -> 系统设置。

## 演示数据口径

- 学生：张三、李四、王五
- 教师：王老师、陈老师、张老师
- 课程：Python 爬虫基础与实践、人工智能导论、数据结构与算法、Web 开发技术
- 班级：计科大三 1 班、计科大三 2 班

## 常见问题

- 页面数据为空：运行 `python scripts/seed_demo_data.py` 后刷新。
- 后端不可访问：检查 `http://127.0.0.1:8000/health`，确认 8000 端口未被占用。
- 前端路由返回失败：确认 Vite 开发服务运行在 `http://127.0.0.1:5173`。
- 构建出现 chunk size warning：只要 `npm run build` 最终成功即可，不影响本阶段验收。
- `/demo-status` 显示 Missing Report：运行 `python scripts/e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports/demo_flow_check.md` 后刷新。

## 现场禁忌

- 不展示真实 API Key。
- 不上传真实敏感资料。
- 不现场删除数据库或重置仓库。
- 不现场大规模重构 UI。
- 不把 `.env`、数据库、上传文件、日志、`node_modules` 或 `dist` 加入提交。
