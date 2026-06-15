export const demoStudents = ['李明', '陈思', '赵雨'];
export const demoTeachers = ['王老师', '陈老师', '李老师'];
export const demoCourses = ['Python 程序设计', '循环结构专项补弱课', 'Python 代码实操案例课', '形成性评价与学习报告'];
export const demoClasses = ['计科大三 1 班', 'Python 程序设计 2 班'];

export const teacherAnalysisDemoSource = '内置演示样例，仅用于本地答辩演示；正式统计来自后端数据库记录。';

export const demoRoutes = {
  student: [
    { route: '/student', title: '学习总览', goal: '查看学生端学习闭环入口、今日任务、课程进度和报告摘要。' },
    { route: '/student/courses', title: '我的课程', goal: '查看 Python 程序设计课程、循环结构章节和学习进度。' },
    { route: '/student/learning-path', title: '学习路径', goal: '查看个性化阶段任务、推荐资源和完成条件。' },
    { route: '/student/assistant', title: '智能答疑', goal: '展示基于课程资料的问答、引用和追问建议。' },
    { route: '/student/exams', title: '测验成绩', goal: '查看测验结果、薄弱点和下一步建议。' },
    { route: '/student/reports', title: '学习报告', goal: '查看学习报告、证据链和改进建议。' }
  ],
  teacher: [
    { route: '/teacher', title: '班级概览', goal: '查看 Python 循环结构班级趋势、李明学习预警和待处理任务。' },
    { route: '/courses', title: '课程管理', goal: '维护 Python 程序设计章节结构和循环结构主推资源。' },
    { route: '/profiles', title: '学生画像', goal: '查看李明 8 维画像、循环结构薄弱点和干预建议。' },
    { route: '/learning-path', title: '学习路径与任务布置', goal: '查看循环结构补弱路径并布置 while 循环练习。' },
    { route: '/teacher-analysis', title: '测评分析', goal: '查看 while 循环、循环嵌套和 break / continue 薄弱项。' },
    { route: '/reports', title: '报告中心', goal: '查看学生/班级报告和证据链。' }
  ],
  admin: [
    { route: '/dashboard', title: '平台总览', goal: '查看平台指标、循环结构资源包、学习预警和内容审核状态。' },
    { route: '/admin/users', title: '用户与角色', goal: '查看学生、教师、管理员角色与权限入口。' },
    { route: '/admin/courses', title: '课程治理', goal: '查看课程运行状态与治理动作。' },
    { route: '/resource-generation', title: 'AI 资源生成', goal: '查看资源生成任务、类型和审核状态。' },
    { route: '/agent-workflow', title: 'Agent 工作流', goal: '展示多智能体节点、运行记录和产物摘要。' },
    { route: '/logs', title: '日志管理', goal: '追踪问答、资源、报告、Agent 和系统事件。' },
    { route: '/settings', title: '系统设置', goal: '展示运行模式、脱敏配置和能力边界。' }
  ]
} as const;
