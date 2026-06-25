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
  student: '围绕画像、课程、学习路径、资源、答疑、测验和报告组织个人学习闭环。',
  teacher: '围绕课程、班级、资源生成、测评分析和报告组织教学管理闭环。',
  admin: '围绕平台治理、内容审核、资源生成、Agent 工作流、日志和系统状态组织治理闭环。'
};

export const roleMenus: Record<UserRole, RoleMenuItem[]> = {
  student: [
    { label: '学习总览', path: '/student', description: '汇总今日目标、课程进度、学习路径、资源和报告。' },
    { label: '画像构建', path: '/student/profile-dialog', description: '通过自然对话构建学习画像，获得个性化学习建议。' },
    { label: '我的课程', path: '/student/courses', description: '查看已加入课程、学习进度和最近学习记录。' },
    { label: '学习资源', path: '/student/resources', description: '查看讲义、案例、测验、任务和思维导图等学习资源。' },
    { label: '学习路径', path: '/student/learning-path', description: '查看个性化学习路径、当前节点和阶段任务。' },
    { label: '今日任务', path: '/student/tasks', description: '查看今日任务、截止时间和完成状态。' },
    { label: '智能答疑', path: '/student/assistant', description: '基于课程资料进行可引用答疑和引导式提示。' },
    { label: '知识库', path: '/student/knowledge', description: '查看课程资料、最近打开和热门下载。' },
    { label: '循环闯关', path: '/student/loop-game', description: '围绕 Python 循环结构进行互动练习。' },
    { label: '测验成绩', path: '/student/exams', description: '查看测验结果、成绩趋势和薄弱知识点建议。' },
    { label: '学习报告', path: '/student/reports', description: '查看学习报告、AI 建议和导出入口。' }
  ],
  teacher: [
    { label: '班级概览', path: '/teacher', description: '聚焦班级趋势、学习预警和干预任务。' },
    { label: 'AI 教学工作台', path: '/teacher/ai-workbench', description: '组织课程备课、资源生成、学情分析和教学建议。' },
    { label: '课程管理', path: '/courses', description: '创建和管理课程基础信息。' },
    { label: '学生画像分析', path: '/profiles', description: '查看学生画像、分层和干预建议。' },
    { label: '学习路径与任务', path: '/learning-path', description: '基于学习路径配置阶段任务。' },
    { label: '资源库', path: '/knowledge-base', description: '管理课程资料、知识库文档和切片状态。' },
    { label: '资源生成中心', path: '/resource-generation', description: '查看和管理 AI 生成的讲义、案例、测验、任务和思维导图。' },
    { label: '测评分析', path: '/teacher-analysis', description: '查看测评结果、知识追踪和教学建议。' },
    { label: '报告中心', path: '/reports', description: '生成和查看班级、学生学习报告。' }
  ],
  admin: [
    { label: '平台总览', path: '/dashboard', description: '查看平台健康、日志、Agent 和报告统计。' },
    { label: '系统运行状态', path: '/demo-status', description: '查看端到端验收、关键事件和推荐检查路线。' },
    { label: '教学决策中心', path: '/admin/decision-center', description: '汇总画像、资源、路径、审核、AI 辅导和教师减负统计。' },
    { label: '课程治理', path: '/admin/courses', description: '管理平台课程基础数据和运行状态。' },
    { label: '用户与角色', path: '/admin/users', description: '管理用户、角色、组织和端侧权限配置。' },
    { label: '资源生成中心', path: '/admin/resource-generate', description: '管理平台资源生成能力与任务统计。' },
    { label: 'Agent 工作流', path: '/agent-workflow', description: '观察 Agent 节点、运行历史和证据链。' },
    { label: '报告审核中心', path: '/admin/reports', description: '查看报告列表、证据链和质量评分。' },
    { label: '日志管理', path: '/logs', description: '检索问答、上传、Agent、报告和错误日志。' },
    { label: '知识库运营', path: '/admin/knowledge', description: '管理知识库文档解析、质量评分和 RAG 诊断。' },
    { label: '内容审核', path: '/admin/content-review', description: '审核 AI 生成内容、风险项和发布状态。' },
    { label: '平台质量', path: '/admin/platform-quality', description: '查看课程质量、资源质量和服务运行指标。' },
    { label: '系统设置', path: '/settings', description: '配置系统运行模式、本地数据源和能力边界。' }
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
  '/resource-generation',
  '/teacher-analysis',
  '/reports',
  '/evaluation',
  '/quiz-evaluate',
  '/tutor-chat'
]);

const adminRoutePaths = new Set([
  '/dashboard',
  '/demo-status',
  '/admin/resource-generate',
  '/agent-workflow',
  '/logs',
  '/log-management',
  '/settings',
  '/system-settings',
  '/capability-boundary'
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
    '/resources': '/admin/resource-generate',
    '/admin/resources': '/admin/resource-generate',
    '/admin/resources/generate': '/admin/resource-generate',
    '/quiz-evaluate': '/evaluation',
    '/admin': '/dashboard',
    '/users': '/admin/users',
    '/users-roles': '/admin/users',
    '/student/course': '/student/courses'
  };
  const lookupPath = aliases[normalizedPath] || normalizedPath;
  return roleMenus[role].find((item) => item.path === lookupPath);
}
