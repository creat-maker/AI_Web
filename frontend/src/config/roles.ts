export type UserRole = 'student' | 'teacher' | 'admin';

export interface RoleMenuItem {
  label: string;
  path: string;
  description: string;
  badge?: string;
}

export const roleLabels: Record<UserRole, string> = {
  student: '学生端',
  teacher: '教师端',
  admin: '管理员端'
};

export const roleHomePath: Record<UserRole, string> = {
  student: '/student',
  teacher: '/teacher',
  admin: '/dashboard'
};

export const roleDescriptions: Record<UserRole, string> = {
  student: '围绕画像、资源、路径、答疑、测评和报告组织个人学习闭环。',
  teacher: '围绕课程、班级、测评、报告和干预建议组织教学管理闭环。',
  admin: '围绕平台运营、资源生成、Agent 工作流、日志和系统配置组织治理闭环。'
};

export const roleMenus: Record<UserRole, RoleMenuItem[]> = {
  student: [
    { label: '学习总览', path: '/student', description: '学生端首页，汇总今日目标、课程进度、路径、资源和报告。' },
    { label: '对话建画像', path: '/profiles', description: '通过学生画像能力沉淀基础信息、偏好和薄弱点。' },
    { label: '我的课程', path: '/courses', description: '复用课程管理页面，学生端用于查看已加入课程。' },
    { label: '资源生成', path: '/resource-generation', description: '面向学生生成个性化讲解、练习和学习材料。' },
    { label: '学习路径', path: '/learning-path', description: '查看个性化学习路径和阶段任务。' },
    { label: '智能答疑', path: '/tutor-chat', description: '基于课程资料进行可信引用答疑和引导式提示。' },
    { label: '知识库 / 课程资料', path: '/knowledge-base', description: '查看课程资料、切片预览和 RAG 质量诊断。' },
    { label: '测验成绩', path: '/evaluation', description: '查看测验结果、错因和学习建议。' },
    { label: '学习报告', path: '/reports', description: '查看学习报告、证据链和后续学习建议。' },
    { label: '笔记本', path: '/notebook', description: '学习笔记、摘录和引用片段整理。', badge: '占位' },
    { label: '学习小组', path: '/study-groups', description: '小组协作、讨论和同伴互助学习。', badge: '占位' },
    { label: '设置', path: '/settings', description: '学生端演示模式、数据来源和配置说明。' }
  ],
  teacher: [
    { label: '班级概览', path: '/teacher', description: '教师端首页，聚焦班级趋势、风险学生和干预任务。' },
    { label: '课程管理', path: '/courses', description: '创建和管理课程基础信息。' },
    { label: '班级学生管理', path: '/class-students', description: '班级学生名单、分层和学习状态管理。', badge: '占位' },
    { label: '学生画像分析', path: '/profiles', description: '复用学生画像页面，支持教师查看画像基础数据。' },
    { label: '学习路径与任务布置', path: '/learning-path', description: '基于学习路径布置阶段任务。' },
    { label: '资源库', path: '/knowledge-base', description: '管理课程资料、知识库文档和切片状态。' },
    { label: '测验评价与教师分析', path: '/teacher-analysis', description: '查看测评结果、知识追踪和教学建议。' },
    { label: '智能答疑管理', path: '/tutor-management', description: '查看学生答疑问题、引用质量和待回复问题。', badge: '占位' },
    { label: '报告中心', path: '/reports', description: '生成和查看班级/学生学习报告。' },
    { label: '通知中心', path: '/notifications', description: '课程通知、学习提醒和报告发布。', badge: '占位' },
    { label: '教学日历 / 待办', path: '/teaching-calendar', description: '教学安排、待批改和待干预事项。', badge: '占位' },
    { label: '设置中心', path: '/settings', description: '教师端演示模式、数据来源和配置说明。' }
  ],
  admin: [
    { label: '平台总览', path: '/dashboard', description: '管理员端首页，展示平台健康度、日志、Agent 和报告统计。' },
    { label: '比赛演示模式', path: '/demo-status', description: '答辩前查看端到端验收报告、关键事件和推荐演示路线。' },
    { label: '课程管理', path: '/courses', description: '平台课程基础数据管理。' },
    { label: '用户与角色', path: '/users-roles', description: '用户、角色、组织和端侧权限配置。', badge: '占位' },
    { label: '资源生成中心', path: '/resource-generation', description: '平台 AI 资源生成能力与任务统计。' },
    { label: 'Agent 工作流', path: '/agent-workflow', description: '观察 Agent 节点、运行历史和模拟重跑。' },
    { label: '报告审核中心', path: '/reports', description: '报告列表、证据链和质量评分审核。' },
    { label: '日志管理', path: '/logs', description: '问答、上传、Agent、报告和错误日志检索。' },
    { label: '知识库运营 / 文档解析', path: '/knowledge-base', description: '平台知识库文档解析、质量评分和 RAG 诊断。' },
    { label: '权限配置', path: '/permissions', description: '菜单、接口和角色权限策略配置。', badge: '占位' },
    { label: '通知公告管理', path: '/announcement-management', description: '平台公告、通知模板和发布范围。', badge: '占位' },
    { label: '数据统计与导出', path: '/data-export', description: '统计报表、导出任务和演示数据审计。', badge: '占位' },
    { label: '系统设置', path: '/settings', description: '系统运行模式、fallback 数据源和能力边界。' }
  ]
};

export function findMenuItem(role: UserRole, path: string) {
  const normalizedPath = path.replace(/\/$/, '') || '/';
  const aliases: Record<string, string> = {
    '/learning-paths': '/learning-path',
    '/resources': '/resource-generation',
    '/quiz-evaluate': '/evaluation',
    '/admin': '/dashboard'
  };
  const lookupPath = aliases[normalizedPath] || normalizedPath;
  return roleMenus[role].find((item) => item.path === lookupPath);
}
