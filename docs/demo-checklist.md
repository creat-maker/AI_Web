# EduMind 比赛演示与验收清单

## 演示前准备

1. 确认当前分支为 `dev`，且不需要全局安装 npm 包。
2. 后端启动：`cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`。
3. 前端启动：`cd frontend && npm run dev`。
4. 小程序：微信开发者工具导入 `miniprogram` 目录。
5. 打开 `/demo-status` 查看演示状态。

## 竞品借鉴说明

本轮功能参考智慧树/知到、超星学习通/泛雅、雨课堂、国家智慧教育公共服务平台，重点吸收以下设计：

- 学生端任务、资源、测验和报告一体化。
- 教师端班级学情、风险学生和智能备课。
- 管理端内容审核、质量评价和平台治理。
- 移动端轻量查看任务、资源和学习报告。

## 核心闭环检查

闭环：学生画像 -> 知识图谱 -> 资源推荐 -> 智能测评 -> 错因分析 -> 教师干预 -> 平台治理。

必验页面：

- `/student/knowledge-graph`
- `/student/learning-path`
- `/student/smart-quiz`
- `/student/assistant`
- `/teacher`
- `/teacher/ai-workbench`
- `/profiles`
- `/courses`
- `/dashboard`
- `/admin/content-review`
- `/admin/platform-quality`

## 后端接口检查

```bash
curl http://127.0.0.1:8000/api/v1/knowledge-graph
curl http://127.0.0.1:8000/api/v1/student/learning-tasks
curl http://127.0.0.1:8000/api/v1/quiz/chapter
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/quiz/submit ^
  -H "Content-Type: application/json" ^
  -d "{\"answers\":{\"q1\":\"open('a.txt').read()\",\"q2\":\"忘记更新循环变量\",\"q3\":\"返回计算结果给调用方\"}}"
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/teacher/ai-workbench/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"type\":\"lesson_plan\",\"course\":\"Python 程序设计\",\"chapter\":\"循环结构与函数\",\"student_foundation\":\"基础差异较大\",\"teaching_goal\":\"掌握循环结构和函数封装\"}"
```

```bash
curl http://127.0.0.1:8000/api/v1/admin/content-review
curl http://127.0.0.1:8000/api/v1/admin/platform-quality
```

## 推荐讲解顺序

学生端：

1. `/student`：今日任务和学习总览。
2. `/student/knowledge-graph`：点击薄弱节点，展示掌握率、资源、练习和 AI 建议。
3. `/student/learning-path`：切换基础薄弱型、考试冲刺型、项目实践型。
4. `/student/smart-quiz`：提交测验，展示得分、错因和推荐资源。
5. `/student/assistant`：展示课程知识点绑定答疑。
6. `/student/reports`：查看学习报告。

教师端：

1. `/teacher`：班级完成率、正确率、活跃度、薄弱点排行、风险学生。
2. `/teacher/ai-workbench`：生成教案、测验、学情分析。
3. `/profiles`：查看学生画像和干预建议。
4. `/courses`：展示知识点、资源、题目关联。

管理员端：

1. `/dashboard`：AI 问答、资源生成、测验完成、审核通过率。
2. `/admin/content-review`：模拟通过、驳回、待审核。
3. `/admin/platform-quality`：课程质量评价。
4. `/demo-status`：展示验收状态。

小程序端：

1. 首页：今日任务、课程进度、薄弱知识点。
2. 路径：任务式路径。
3. 资源：AI 推荐资源包。
4. 练习：得分与错因分析。
5. 报告：知识点掌握情况和学习建议。

## AI 能力边界

演示时必须说明：AI 生成内容仅作为教学辅助，关键教学资源、测评结果、学生画像诊断和干预建议需教师或管理员审核后使用。

## 验收命令

```bash
git status --short
cd backend && python -m compileall app
cd frontend && npm run build
python scripts/check-demo-ready.py
```
