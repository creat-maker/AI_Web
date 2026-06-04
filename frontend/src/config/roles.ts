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
  student: '围绕画像、知识图谱、任务路径、答疑、测评和报告组织个人学习闭环。',
  teacher: '围绕班级学情、AI 教学工作台、学生画像、测评分析和干预建议组织教学管理闭环。',
  admin: '围绕平台总览、内容审核、课程质量评价、日志和能力边界组织平台治理闭环。'
};

export const roleMenus: Record<UserRole, RoleMenuItem[]> = {
  student: [
    { label: '学习总览', path: '/student', description: '查看今日任务、课程进度、薄弱知识点和报告摘要。' },
    { label: '我的课程', path: '/student/courses', description: '查看已加入课程、学习进度和最近学习记录。' },
    { label: '课程知识图谱', path: '/student/knowledge-graph', description: '查看 Python 知识点关系、掌握状态、推荐资源和关联练习。', badge: '新增' },
    { label: '任务式学习路径', path: '/student/learning-path', description: '按学生画像展示个性化任务、完成条件和 AI 推荐。', badge: '增强' },
    { label: '今日任务 / 日历', path: '/student/tasks', description: '查看今日任务、截止时间和完成状态。' },
    { label: '智能答疑', path: '/student/assistant', description: '基于课程知识点给出解释、资源和练习建议。', badge: '增强' },
    { label: '知识库 / 课程资料', path: '/student/knowledge', description: '查看课程资料、最近打开和热门下载。' },
    { label: '智能测验与练后分析', path: '/student/smart-quiz', description: '提交章节练习后生成得分、错因、薄弱点和推荐资源。', badge: '新增' },
    { label: '测验成绩', path: '/student/exams', description: '查看测验结果、成绩趋势和薄弱知识点建议。' },
    { label: '学习报告', path: '/student/reports', description: '查看学习报告、AI 建议和导出入口。' },
    { label: '成就徽章', path: '/student/achievements', description: '查看学习徽章、成长记录和荣誉进度。' },
    { label: '积分等级', path: '/student/points', description: '查看学习积分、等级成长和排行。' },
    { label: '笔记本', path: '/student/notes', description: '学习笔记、摘录和引用片段整理。' },
    { label: '学习小组', path: '/student/group', description: '小组协作、讨论和同伴互助学习。' }
  ],
  teacher: [
    { label: '班级学情', path: '/teacher', description: '查看班级完成率、正确率、活跃度、风险学生和干预建议。', badge: '增强' },
    { label: 'AI 教学工作台', path: '/teacher/ai-workbench', description: '生成教案、测验和学情分析，结果审核后发布。', badge: '新增' },
    { label: '课程管理', path: '/courses', description: '管理课程基础信息，并查看知识点、资源、题目关联。', badge: '增强' },
    { label: '班级学生管理', path: '/class-students', description: '班级学生名单、分层和学习状态管理。', badge: '占位' },
    { label: '学生画像分析', path: '/profiles', description: '查看学生基础水平、目标、偏好、薄弱点、风险和干预建议。', badge: '增强' },
    { label: '学习路径与任务布置', path: '/learning-path', description: '基于学习路径配置阶段任务。' },
    { label: '资源库', path: '/knowledge-base', description: '管理课程资料、知识库文档和切片状态。' },
    { label: '测验评价与教师分析', path: '/teacher-analysis', description: '查看测评结果、知识追踪和教学建议。' },
    { label: '智能答疑管理', path: '/tutor-management', description: '查看学生答疑问题、引用质量和待回复问题。', badge: '占位' },
    { label: '报告中心', path: '/reports', description: '生成和查看班级 / 学生学习报告。' },
    { label: '通知中心', path: '/notifications', description: '课程通知、学习提醒和报告发布。', badge: '占位' },
    { label: '教学日历 / 待办', path: '/teaching-calendar', description: '教学安排、待批改和待干预事项。', badge: '占位' }
  ],
  admin: [
    { label: '平台总览', path: '/dashboard', description: '展示平台健康、AI 问答、资源生成、测验完成和审核通过率。', badge: '增强' },
    { label: '比赛演示状态', path: '/demo-status', description: '答辩前查看端到端验收报告、关键事件和推荐演示路线。' },
    { label: '课程治理', path: '/admin/courses', description: '平台课程基础数据和运行治理。' },
    { label: 'AI 内容审核中心', path: '/admin/content-review', description: '审核 AI 生成资源、测验和个性化建议，防止直接发布。', badge: '新增' },
    { label: '课程质量评价', path: '/admin/platform-quality', description: '查看课程完成率、测验均分、资源使用率和教师 AI 使用次数。', badge: '新增' },
    { label: '用户与角色', path: '/admin/users', description: '用户、角色、组织和端侧权限配置。' },
    { label: '资源生成中心', path: '/resource-generation', description: '平台 AI 资源生成能力与任务统计。' },
    { label: 'Agent 工作流', path: '/agent-workflow', description: '观察 Agent 节点、运行历史和模拟重跑。' },
    { label: '报告审核中心', path: '/admin/reports', description: '报告列表、证据链和质量评分审核。' },
    { label: '日志管理', path: '/logs', description: '问答、上传、Agent、报告和错误日志检索。' },
    { label: '知识库运营 / 文档解析', path: '/admin/knowledge', description: '平台知识库文档解析、质量评分和 RAG 诊断。' },
    { label: '权限配置', path: '/permissions', description: '菜单、接口和角色权限策略配置。', badge: '占位' },
    { label: '通知公告管理', path: '/announcement-management', description: '平台公告、通知模板和发布范围。', badge: '占位' },
    { label: '数据统计与导出', path: '/data-export', description: '统计报表、导出任务和演示数据审计。', badge: '占位' },
    { label: '系统设置', path: '/settings', description: '系统运行模式、fallback 数据源和能力边界。' }
  ]
};

const teacherRoutePaths = new Set([
  '/teacher',
  '/teacher/ai-workbench',
  '/courses',
  '/profiles',
  '/learning-path',
  '/learning-paths',
  '/knowledge-base',
  '/teacher-analysis',
  '/reports',
  '/class-students',
  '/tutor-management',
  '/notifications',
  '/teaching-calendar',
  '/tutor-chat',
  '/evaluation',
  '/quiz-evaluate'
]);

const adminRoutePaths = new Set([
  '/dashboard',
  '/demo-status',
  '/resource-generation',
  '/agent-workflow',
  '/logs',
  '/log-management',
  '/settings',
  '/system-settings',
  '/capability-boundary',
  '/permissions',
  '/announcement-management',
  '/data-export'
]);

export function roleFromPath(path: string): UserRole | null {
  const normalizedPath = path.replace(/\/$/, '') || '/';
  if (normalizedPath.startsWith('/student')) return 'student';
  if (normalizedPath === '/teacher' || teacherRoutePaths.has(normalizedPath)) return 'teacher';
  if (normalizedPath === '/dashboard' || normalizedPath.startsWith('/admin') || adminRoutePaths.has(normalizedPath)) return 'admin';
  return null;
}

export function findMenuItem(role: UserRole, path: string) {
  const normalizedPath = path.replace(/\/$/, '') || '/';
  const aliases: Record<string, string> = {
    '/learning-paths': '/learning-path',
    '/resources': '/resource-generation',
    '/quiz-evaluate': '/evaluation',
    '/admin': '/dashboard',
    '/users': '/admin/users',
    '/users-roles': '/admin/users',
    '/admin/resources': '/resource-generation',
    '/student/course': '/student/courses',
    '/student/evaluation': '/student/smart-quiz',
    '/student/quiz-evaluate': '/student/smart-quiz',
    '/student/learning-paths': '/student/learning-path'
  };
  const lookupPath = aliases[normalizedPath] || normalizedPath;
  return roleMenus[role].find((item) => item.path === lookupPath);
}
