# EduMind Demo Flow

## 主线

画像构建 -> DKVMN 掌握更新 -> 学习路径 -> RAG 答疑 -> 资源生成 -> 内容审核 -> AuditRetry 或 TeacherArbitration -> 测验提交 -> 报告生成 -> 日志验收。

## 学生端

1. `/student/profile-dialog` 查看画像维度和证据。
2. `/student/learning-path` 查看路径、任务和 DKVMN 弱点。
3. `/student/assistant` 提问 while 循环问题，检查引用和课程边界。
4. `/student/resources` 查看讲义、练习、HTML 动画、TTS/视频 fallback。
5. `/student/smart-quiz` 提交测验，查看 DKVMN 更新、弱知识点和路径调整。
6. `/student/reports` 查看报告生成时间、下载入口和教师建议。

## 教师端

1. `/teacher` 查看班级学情。
2. `/teacher-analysis` 查看薄弱知识点和风险学生。
3. `/resource-generation` 生成资源包。
4. `/teacher/arbitration` 对待审核内容执行 approve、revise 或 reject。
5. `/reports` 查看报告中心。

## 管理端

1. `/dashboard` 查看平台状态。
2. `/knowledge-base` 检查课程资料。
3. `/agent-workflow` 查看 12 节点教学智能体治理增强流程。
4. `/logs` 查看审计日志。
5. `/demo-status` 查看验收脚本结果和服务健康字段。

## 验收脚本

```bash
python scripts/check-demo-ready.py
python scripts/e2e_demo_flow_check.py
python scripts/eval_retrieval.py
```
