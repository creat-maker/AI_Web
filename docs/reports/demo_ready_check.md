# EduMind 演示状态检查报告

- 检查时间：2026-07-14T17:30:25
- 总体状态：READY
- 通过 / 警告 / 失败：39 / 0 / 0
- 后端地址：http://127.0.0.1:8000
- 前端地址：http://127.0.0.1:5173

## 核心演示对象

- 学生：李明、张三、李四、王五
- 教师：王老师、陈老师、张老师
- 课程：Python 程序设计、Python 爬虫基础与实践、人工智能导论、数据结构与算法、Web 开发技术
- 班级：计科大三 1 班、计科大三 2 班

## 检查明细

| 分类 | 项目 | 状态 | 当前 | 期望 | 建议 |
| --- | --- | --- | --- | --- | --- |
| data | courses | PASS | 6 | 5 | 满足演示要求 |
| data | core_courses | PASS | 5 | 5 | 满足演示要求 |
| data | student_profiles | PASS | 5 | 4 | 满足演示要求 |
| data | core_students | PASS | 5 | 4 | 满足演示要求 |
| data | core_teachers | PASS | 3 | 3 | 满足演示要求 |
| data | course_documents | PASS | 46 | 3 | 满足演示要求 |
| data | tutor_question_logs | PASS | 6 | 5 | 满足演示要求 |
| data | quizzes | PASS | 5 | 1 | 满足演示要求 |
| data | quiz_submissions | PASS | 4 | 1 | 满足演示要求 |
| data | learning_reports | PASS | 5 | 3 | 满足演示要求 |
| data | agent_runs | PASS | 5 | 3 | 满足演示要求 |
| data | learning_paths | PASS | 5 | 3 | 满足演示要求 |
| data | generated_resources | PASS | 23 | 3 | 满足演示要求 |
| data | audit_logs | PASS | 19 | 3 | 满足演示要求 |
| data | business_events | PASS | 11 | 9 | 满足演示要求 |
| file | backend/storage/uploads | PASS | exists | exists | 文件或目录已存在 |
| file | backend/storage/reports | PASS | exists | exists | 文件或目录已存在 |
| file | backend/storage/chroma | PASS | exists | exists | 文件或目录已存在 |
| file | frontend/dist/index.html | PASS | exists | exists | 文件或目录已存在 |
| file | docs/course_kb/python_programming.json | PASS | exists | exists | 文件或目录已存在 |
| source | report_service_methods | PASS | ok | all patterns present | 满足演示要求 |
| source | profile_service_methods | PASS | ok | all patterns present | 满足演示要求 |
| source | quiz_service_methods | PASS | ok | all patterns present | 满足演示要求 |
| source | rag_citations_contract | PASS | ok | all patterns present | 满足演示要求 |
| source | teacher_arbitration_decisions | PASS | ok | all patterns present | 满足演示要求 |
| miniprogram | miniprogram_request_or_fallback | PASS | ok | all patterns present | 满足演示要求 |
| script | start-dev.bat | PASS | exists | exists | 文件或目录已存在 |
| script | stop-dev.bat | PASS | exists | exists | 文件或目录已存在 |
| script | seed-demo-data.bat | PASS | exists | exists | 文件或目录已存在 |
| script | check-demo-ready.bat | PASS | exists | exists | 文件或目录已存在 |
| script | scripts/seed_demo_data.py | PASS | exists | exists | 文件或目录已存在 |
| script | scripts/e2e_demo_flow_check.py | PASS | exists | exists | 文件或目录已存在 |
| script | scripts/eval_retrieval.py | PASS | exists | exists | 文件或目录已存在 |
| script | docker-compose.yml | PASS | exists | exists | 文件或目录已存在 |
| script | backend/Dockerfile | PASS | exists | exists | 文件或目录已存在 |
| script | frontend/Dockerfile | PASS | exists | exists | 文件或目录已存在 |
| script | frontend/nginx.conf | PASS | exists | exists | 文件或目录已存在 |
| script | .env.example | PASS | exists | exists | 文件或目录已存在 |
| script | .github/workflows/ci.yml | PASS | exists | exists | 文件或目录已存在 |

## 三端推荐演示路线

### 学生端
1. /student 学习总览
2. /student/courses 我的课程
3. /student/learning-path 学习路径
4. /student/assistant 智能答疑
5. /student/exams 测验成绩
6. /student/reports 学习报告

### 教师端
1. /teacher 班级概览
2. /courses 课程管理
3. /profiles 学生画像
4. /learning-path 学习路径与任务布置
5. /teacher-analysis 测评分析
6. /reports 报告中心

### 管理员端
1. /dashboard 平台总览
2. /admin/users 用户与角色
3. /admin/courses 课程治理
4. /resource-generation AI 资源生成
5. /agent-workflow Agent 工作流
6. /logs 日志管理
7. /settings 系统设置
