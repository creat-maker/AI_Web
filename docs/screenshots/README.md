# EduMind 截图清单

本目录用于整理比赛提交和 PPT 制作所需截图。建议截图统一使用 16:9 画幅，Web 页面使用浏览器桌面宽度，小程序页面使用微信开发者工具模拟器截图。

## Web 截图

1. 登录页：`/login`
2. 学生首页：`/student`
3. 学生智能辅导：`/student/assistant`
4. 5 类资源生成：`/student/assistant` 或 `/resource-generation`
5. RAG 引用来源：`/student/assistant`
6. 防幻觉审核：`/student/assistant` 或 `/resource-generation`
7. AgentWorkflow：`/agent-workflow`
8. demo-status：`/demo-status`

## 小程序截图

1. 小程序首页：`pages/home/index`
2. 小程序 AI 辅导：`pages/tutor/index`
3. 小程序资源推荐：`pages/resources/index`
4. 小程序学习报告：`pages/report/index`

## 命名建议

```text
01-login.png
02-student-home.png
03-student-assistant.png
04-resource-pack.png
05-rag-citations.png
06-content-review.png
07-agent-workflow.png
08-demo-status.png
09-mp-home.png
10-mp-tutor.png
11-mp-resources.png
12-mp-report.png
```

## 截图注意事项

- 截图前先运行 `check-demo-ready.py` 确认状态正常。
- Web 截图建议使用同一浏览器宽度，避免不同截图风格不一致。
- 小程序截图建议保持同一模拟设备。
- 不展示真实 API Key、真实学生隐私数据或本地敏感路径。
