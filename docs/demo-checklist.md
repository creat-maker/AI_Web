# EduMind 15 分钟黄金演示路线

## 演示主线

- 课程：Python 程序设计
- 主题：循环结构
- 学生：李明
- 画像：基础薄弱、代码实操偏好、中风险
- 闭环：画像 -> DKVMN -> 路径 -> RAG -> 资源 -> 测验 -> 错因 -> 路径调整 -> 教师仲裁 -> 报告 -> 治理日志

## 学生端点击顺序

1. `/student/profile-dialog`：一键载入李明画像，展示 6 维度和证据。
2. `/student/learning-path`：查看 while 循环补弱任务和路径调整时间线。
3. `/student/assistant`：提问“为什么我的 while 循环会死循环？”，查看引用、置信度、课程对齐。
4. `/student/resources`：预览讲义、HTML 动画、TTS/MP4 fallback、代码案例。
5. `/student/smart-quiz`：提交循环结构测验，触发 DKVMN 与路径调整。
6. `/student/reports`：查看学习报告和下一步建议。

## 教师端点击顺序

1. `/teacher`：查看班级学情。
2. `/teacher-analysis`：查看知识点掌握矩阵和预警学生。
3. `/resource-generation`：生成 9 类资源包。
4. `/review-center` 或 `/admin/decision-center`：处理教师仲裁 approve / revise / reject。
5. `/reports`：下载或预览学习报告。

## 管理端点击顺序

1. `/dashboard`：系统总览。
2. `/knowledge-base`：上传 PDF/DOCX/TXT/Markdown，检查解析与切片。
3. `/admin/content-review`：查看内容审核。
4. `/agent-workflow`：查看 AgentLogViewer 时间线、回流和仲裁状态。
5. `/logs` 与 `/demo-status`：查看治理日志和系统状态。

## 关键讲解话术

- DKVMN 是轻量工程化落地：不用训练深度模型，但保留 key/value 记忆、连续对错和未来模型替换接口。
- RAG 不只返回答案，还返回引用证据、课程对齐度、超纲提示和检索分数。
- FACET 治理把内容审核、回流重试、教师仲裁和日志追踪串成闭环。
- 讯飞、FFmpeg、Chroma 未配置时不会影响演示，系统自动降级到本地轻量能力。

## 异常兜底

- 后端不可用：前端和小程序展示本地示例数据。
- Chroma 不可用：JSON/TF-IDF fallback 检索。
- TTS 未配置：展示讲解文本和任务状态。
- FFmpeg 未安装：展示 HTML 动画和视频脚本。
- 上传解析依赖缺失：返回友好 warnings，不中断页面。
