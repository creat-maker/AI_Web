# EduMind 比赛现场演示手册

本文档用于答辩、比赛现场或团队交接前的快速检查。目标是用最少操作确认环境、数据、页面和讲解链路都处于可演示状态。

## 1. 演示前准备

### 代码状态

- 确认当前分支：`git branch --show-current`
- 确认工作区状态：`git status --short`
- 如果现场需要提交或推送，先确认没有误加入 `.env`、数据库文件、日志、上传文件、`node_modules`、`dist`
- 不在现场临时重构代码，不做大范围合并

### 依赖状态

- 后端依赖已安装：`pip install -r backend/requirements.txt`
- 前端依赖已安装：`cd frontend && npm install`
- 不执行 `npm install -g`
- 不新增临时依赖

### 敏感信息检查

- 不展示真实 API Key
- 不打开包含真实密钥的 `.env`
- 不把真实学生、教师、学校或业务文件上传到演示环境
- SystemSettings 页面只展示配置状态和脱敏结果，不展示密钥明文

### 端口检查

- 后端端口：`8000`
- 前端端口：`5173`
- 如果端口被占用，先运行 `stop-dev.bat`，再重新运行 `start-dev.bat`

## 2. 推荐命令顺序

Windows 推荐顺序：

```bat
seed-demo-data.bat
check-demo-ready.bat
start-dev.bat
```

停止服务：

```bat
stop-dev.bat
```

如果不用 bat，也可以在项目根目录执行：

```bat
python scripts\seed-demo-data.py
python scripts\check-demo-ready.py
```

## 3. 演示页面顺序

### 1. `/dashboard`

打开页面：`http://localhost:5173/dashboard`

要展示什么：

- 课程总数、知识库文档、问答记录、报告数量
- 最近文档、最近问答、最近活动
- 7 天趋势图或趋势数据

讲解重点：

- 这是系统总览页，用于证明数据链路已经跑通
- Dashboard 数据来自后端聚合统计，不是纯静态页面
- 演示数据可通过 seed 脚本初始化，也可通过真实操作持续增加

### 2. `/knowledge-base`

打开页面：`http://localhost:5173/knowledge-base`

要展示什么：

- 课程知识库文档列表
- 文档解析状态、知识切片数量
- 检索测试区域和命中文档片段

讲解重点：

- 知识库是 RAG 答疑和 Agent 检索的基础
- 演示数据中写入的是文档元信息和安全示例文件，不包含敏感资料
- 如果现场有安全资料，可以上传后立即用于检索

### 3. `/tutor-chat`

打开页面：`http://localhost:5173/tutor-chat`

要展示什么：

- 选择课程后进行智能问答
- 展示回答内容和知识库引用
- 展示历史问答记录

讲解重点：

- 问答基于课程知识库上下文
- TutorQuestionLog 会沉淀为日志中心和 Dashboard 的数据来源
- mock 模式下也能演示完整交互链路

### 4. `/teacher-analysis`

打开页面：`http://localhost:5173/teacher-analysis`

要展示什么：

- 测评次数、平均得分、参与学生数
- 薄弱知识点分布
- 学生表现分布和教学建议
- 最近测评/报告记录

讲解重点：

- 分析页服务于教师教学决策
- 数据来自 Quiz、QuizSubmission、StudentProfile、LearningReport
- 薄弱点可回流到学习路径、资源生成和 AgentWorkflow

### 5. `/agent-workflow`

打开页面：`http://localhost:5173/agent-workflow`

要展示什么：

- 今日运行次数、成功率、平均耗时、产物数量
- 运行参数区
- 流程节点：任务接收、意图识别、知识库检索、答案生成、学情分析、教学建议、报告生成
- 最近运行记录和产物摘要

讲解重点：

- AgentWorkflow 是系统工程亮点，用节点化方式展示多智能体协作
- steps、artifacts、workflow_summary 都会记录下来
- 成功和失败状态都能进入日志中心，体现可观测性

### 6. `/reports`

打开页面：`http://localhost:5173/reports`

要展示什么：

- 报告总数、本周新增、已完成报告、质量评分
- 报告列表、筛选和详情预览
- 学习表现摘要、薄弱点、推荐路径、教学建议、引用来源

讲解重点：

- 报告中心把画像、测评、路径、答疑和 Agent 结果沉淀成可交付材料
- Word 报告用于教师、学生或家长查看
- 报告记录也会进入日志中心

### 7. `/logs`

打开页面：`http://localhost:5173/logs`

要展示什么：

- 今日日志数、错误日志数、Agent 运行次数、问答记录数
- 系统日志、问答日志、知识库日志、Agent 日志、报告日志、错误日志
- 日志详情预览：来源、摘要、关联课程、关联 ID、错误信息、处理建议

讲解重点：

- 日志中心不是复杂权限系统，而是轻量运行追踪
- 日志聚合已有业务记录，不额外暴露敏感信息
- 有助于比赛现场解释系统可信度和工程完整度

### 8. `/settings`

打开页面：`http://localhost:5173/settings`

要展示什么：

- 运行模式、模型模式、知识库状态
- 模型配置、RAG 配置、教学策略
- 测试连接和脱敏安全提示

讲解重点：

- 配置页只展示状态，不展示真实 API Key
- 支持 mock 模式和真实模型模式切换思路
- 体现系统可部署、可配置、可排查

## 4. 页面讲解话术

### Dashboard

展示点：

- 整体课程、文档、问答、报告、趋势和最近活动

技术点：

- 后端聚合统计 Course、CourseDocument、TutorQuestionLog、LearningReport、AgentRun
- 空数据时有兼容展示，演示数据初始化后可展示完整链路

评委可能会问什么：

- 这些数据是真实的吗？如何更新？
- 回答：演示数据由脚本初始化，真实使用时由上传、问答、测评、Agent 运行和报告生成自动写入。

### KnowledgeBase

展示点：

- 文档状态、知识切片、检索结果

技术点：

- 文档元信息存数据库，知识切片用于向量检索
- 检索结果会支撑 TutorChat 和 AgentWorkflow

评委可能会问什么：

- 没有真实资料能演示吗？
- 回答：可以，演示数据提供安全示例；真实环境上传课程资料后会进入同一链路。

### TutorChat

展示点：

- 课程问答、引用上下文、历史记录

技术点：

- RAG 答疑把用户问题和课程知识片段结合
- 问答日志写入 TutorQuestionLog

评委可能会问什么：

- 如果模型不可用怎么办？
- 回答：项目支持 mock 模式，保证课堂和比赛现场可稳定演示；配置真实模型后可切换真实生成。

### TeacherAnalysis

展示点：

- 测评结果、薄弱点、趋势、教学建议

技术点：

- 基于 QuizSubmission 和 StudentProfile 汇总学情
- 报告与 Agent 结果也能形成分析依据

评委可能会问什么：

- 如何避免只展示平均分？
- 回答：页面同时展示薄弱知识点、分布、最近记录和建议，强调可干预的教学信息。

### AgentWorkflow

展示点：

- 多节点流程、运行记录、产物摘要

技术点：

- steps 表示工作流节点，artifacts 表示中间与最终产物
- workflow_summary 支撑运行统计和日志追踪

评委可能会问什么：

- Agent 和普通接口调用有什么区别？
- 回答：AgentWorkflow 把任务拆成可观察节点，每一步都有输入摘要、输出摘要、状态和产物。

### ReportCenter

展示点：

- 报告概览、列表、预览、下载

技术点：

- LearningReport 存储报告元信息和结构化摘要
- 报告内容聚合画像、路径、测评、答疑和 Agent 结果

评委可能会问什么：

- 报告是否能导出？
- 回答：支持 Word 报告文件，演示数据也会生成安全的本地示例报告。

### LogManagement

展示点：

- 分类日志、筛选搜索、详情预览、错误处理建议

技术点：

- 通过聚合 TutorQuestionLog、LearningReport、AgentRun、CourseDocument 形成轻量日志中心
- 不返回密钥、环境变量明文或敏感文件内容

评委可能会问什么：

- 有没有真实日志表？
- 回答：当前阶段采用兼容聚合方案，适合 MVP 演示；后续可扩展独立审计日志表。

### SystemSettings

展示点：

- 运行模式、模型配置、RAG 配置、安全提示

技术点：

- 只展示配置状态和脱敏检查结果
- 不修改系统环境变量，不写入真实密钥

评委可能会问什么：

- 如何部署到真实环境？
- 回答：通过 `.env` 配置数据库、模型服务和跨域地址，前后端分离部署。

## 5. 常见异常处理

### 后端启动失败

现象：

- `http://localhost:8000/health` 打不开
- 前端页面提示接口失败

可能原因：

- Python 环境未激活
- 依赖未安装
- 端口 8000 被占用
- `.env` 配置异常

处理步骤：

1. 运行 `stop-dev.bat`
2. 进入 `backend`，确认依赖：`pip install -r requirements.txt`
3. 手动启动：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
4. 打开 `http://localhost:8000/health`

### 前端启动失败

现象：

- `http://localhost:5173` 打不开
- Vite 终端报错

可能原因：

- `frontend/node_modules` 不存在
- 端口 5173 被占用
- Node 版本或依赖安装异常

处理步骤：

1. 进入 `frontend`
2. 运行 `npm install`
3. 运行 `npm run dev`
4. 如果端口占用，先运行 `stop-dev.bat`

### 端口占用

现象：

- 后端或前端提示 address already in use

可能原因：

- 上一次服务没有关闭
- 其他程序占用 8000 或 5173

处理步骤：

1. 运行 `stop-dev.bat`
2. 等待几秒后重新运行 `start-dev.bat`
3. 如仍失败，用系统任务管理器检查占用进程

### 页面空数据

现象：

- Dashboard、报告、日志或分析页数据很少

可能原因：

- 数据库为空
- 未运行演示数据脚本

处理步骤：

1. 运行 `seed-demo-data.bat`
2. 运行 `check-demo-ready.bat`
3. 刷新页面

### GitHub push 失败

现象：

- `git push` 失败或提示认证问题

可能原因：

- 网络或代理异常
- 远程分支落后
- 凭据失效

处理步骤：

1. 先保存当前修改：`git status --short`
2. 检查远程：`git remote -v`
3. 重新拉取团队最新分支后再推送
4. 不要把 `.env`、数据库、上传文件和构建产物加入提交

### `npm run build` 有 chunk size warning

现象：

- 构建成功，但提示 some chunks are larger than 500 kB

可能原因：

- 依赖包或图表/渲染模块体积较大

处理步骤：

1. 确认最后有 `built` 或 `✓ built`
2. 如果构建成功，这是性能提示，不是阻断错误
3. 比赛前无需现场处理，可后续做 code-splitting 优化

### SQLite 数据库无数据

现象：

- 页面大面积 fallback 或空列表
- `check-demo-ready.bat` 显示 NOT READY

可能原因：

- 使用了新的 SQLite 文件
- 未运行 seed 脚本

处理步骤：

1. 运行 `python scripts/seed-demo-data.py`
2. 再运行 `python scripts/check-demo-ready.py`
3. 确认总体状态为 READY 或至少无关键 FAIL

### 知识库检索无结果

现象：

- KnowledgeBase 检索返回空
- TutorChat 引用片段为空

可能原因：

- 课程未选择正确
- 文档未解析
- 查询词和资料内容不匹配

处理步骤：

1. 切换到有文档记录的课程
2. 使用示例问题：`Python 函数参数如何理解？`
3. 如仍为空，先展示文档列表和日志中心，说明当前是安全演示数据或需要重新构建知识库

### `/docs` 打不开

现象：

- `http://localhost:8000/docs` 无法访问

可能原因：

- 后端未启动
- 端口 8000 被占用
- 启动命令报错

处理步骤：

1. 打开 `http://localhost:8000/health`
2. 若 health 也打不开，按“后端启动失败”处理
3. 若 health 正常但 docs 异常，刷新浏览器或重启后端

### Codex 中断或无法发送消息

现象：

- Codex 对话卡住
- 无法继续发送或接收

可能原因：

- 网络中断
- 会话上下文过长
- 工具执行还未完成

处理步骤：

1. 等待当前命令完成
2. 复制最新任务目标和关键状态，开启新对话继续
3. 不要在现场临时删除文件或重置仓库
4. 优先使用已有 bat 脚本和 README 流程恢复演示

## 6. 演示时禁止操作

- 不展示真实 API Key
- 不上传敏感文件
- 不现场删除数据库
- 不现场重构代码
- 不现场 `npm install -g`
- 不把 `node_modules`、`dist`、数据库文件提交到 GitHub
- 不执行 `git reset --hard`、批量删除或不确定影响范围的命令
- 不在答辩现场改系统环境变量

## 7. 答辩亮点总结

1. 前后端分离：Vue 3 + FastAPI，结构清晰，便于部署和扩展。
2. RAG 知识增强：课程资料进入知识库，用于智能答疑和 Agent 检索。
3. Agent 工作流：以节点化方式展示任务接收、检索、生成、分析、建议和报告。
4. 学情分析：基于测评提交和学生画像生成薄弱点分布与教学建议。
5. 报告中心：把学习过程沉淀为可预览、可下载的 Word 学习报告。
6. 日志可观测：聚合问答、知识库、报告和 Agent 记录，支持筛选和详情预览。
7. Demo 数据初始化：一条命令补齐比赛演示所需数据，不清空用户数据。
8. 演示健康检查：比赛前自动检查数据量、目录和关键脚本。
9. 配置脱敏：SystemSettings 只展示配置状态，不暴露真实密钥。
10. 一键启动：Windows 下可用 bat 脚本快速启动、停止和准备演示。

## 8. 最终演示流程压缩版

### 5 分钟演示版

- 30 秒：Dashboard，展示系统总体数据、趋势和最近活动。
- 45 秒：KnowledgeBase，展示课程文档、切片数量和检索测试。
- 60 秒：TutorChat，选择课程提问，展示 RAG 回答和引用。
- 60 秒：AgentWorkflow，展示工作流节点、运行记录和产物摘要。
- 45 秒：ReportCenter，展示报告列表、详情预览和下载入口。
- 40 秒：Logs + Settings，展示日志追踪、错误处理建议和配置脱敏。

### 10 分钟演示版

- 1 分钟：Dashboard，说明系统闭环和当前演示数据来源。
- 1 分钟：KnowledgeBase，说明资料上传、解析、切片和检索。
- 1.5 分钟：TutorChat，现场提问并解释 RAG 引用链路。
- 1.5 分钟：TeacherAnalysis，展示测评、薄弱点和教学建议。
- 2 分钟：AgentWorkflow，重点讲多智能体节点、产物和可观测状态。
- 1 分钟：ReportCenter，展示学习报告如何沉淀结果。
- 1 分钟：LogManagement，展示分类日志、错误日志和关联 ID。
- 1 分钟：SystemSettings + 总结，展示配置脱敏、mock/真实模型切换思路和工程亮点。

## 9. 最后确认清单

- `check-demo-ready.bat` 总体状态为 READY
- `http://localhost:8000/health` 可访问
- `http://localhost:8000/docs` 可访问
- `http://localhost:5173/dashboard` 可访问
- 演示页面按顺序打开过一次
- 浏览器没有打开真实密钥、真实学生信息或敏感文件
- 现场讲解优先走已验证流程，不临时改代码
