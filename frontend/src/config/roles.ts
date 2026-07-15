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

export const ROLE_HOME: Record<UserRole, string> = {
  student: '/student',
  teacher: '/teacher',
  admin: '/dashboard'
};

export const roleHomePath = ROLE_HOME;

export const roleDescriptions: Record<UserRole, string> = {
  student: '围绕画像、课程、学习路径、资源、答疑、测验和报告组织个人学习闭环。',
  teacher: '围绕课程、班级、资源生成、测评分析和报告组织教学管理闭环。',
  admin: '围绕平台治理、内容审核、资源生成、Agent 工作流、日志和系统状态组织治理闭环。'
};

export const roleMenus: Record<UserRole, RoleMenuItem[]> = {
  student: [
    { label: '学习总览', path: '/student', description: '汇总今日目标、课程进度、学习路径、资源和报告。' },
    { label: '学生画像', path: '/student/profile', description: '查看学习画像、能力雷达和个性化学习建议。' },
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
    { label: '课程管理', path: '/teacher/courses', description: '创建和管理课程基础信息。' },
    { label: '学情分析', path: '/teacher/analysis', description: '查看测评结果、知识追踪和教学建议。' },
    { label: '资源生成', path: '/teacher/resource-generation', description: '查看和管理 AI 生成的讲义、案例、测验、任务和思维导图。' },
    { label: '教师仲裁', path: '/teacher/arbitration', description: '复核 AI 生成的学习路径、资源包和学情报告。' },
    { label: '报告中心', path: '/teacher/reports', description: '生成和查看班级、学生学习报告。' }
  ],
  admin: [
    { label: '平台总览', path: '/dashboard', description: '查看平台健康、日志、Agent 和报告统计。' },
    { label: '知识库运营', path: '/admin/knowledge', description: '管理知识库文档解析、质量评分和 RAG 诊断。' },
    { label: '内容审核', path: '/admin/content-review', description: '审核 AI 生成内容、风险项和发布状态。' },
    { label: 'Agent 工作流', path: '/admin/agent-workflow', description: '观察 Agent 节点、运行历史和证据链。' },
    { label: '日志中心', path: '/admin/logs', description: '检索问答、上传、Agent、报告和错误日志。' },
    { label: '系统状态', path: '/admin/demo-status', description: '查看端到端验收、关键事件和推荐检查路线。' }
  ]
};

export function roleFromPath(path: string): UserRole | null {
  const normalizedPath = path.replace(/\/$/, '') || '/';
  if (normalizedPath.startsWith('/student')) return 'student';
  if (normalizedPath.startsWith('/teacher')) return 'teacher';
  if (normalizedPath === '/dashboard' || normalizedPath.startsWith('/admin')) return 'admin';
  return null;
}

export function findMenuItem(role: UserRole, path: string) {
  const normalizedPath = path.replace(/\/$/, '') || '/';
  const aliases: Record<string, string> = {
    '/student/course': '/student/courses',
    '/student/report': '/student/reports',
    '/student/quiz': '/student/smart-quiz',
    '/courses': '/teacher/courses',
    '/profiles': '/teacher/profiles',
    '/learning-path': '/teacher/learning-path',
    '/learning-paths': '/teacher/learning-path',
    '/knowledge-base': '/teacher/knowledge-base',
    '/resource-generation': '/teacher/resource-generation',
    '/review-center': '/teacher/arbitration',
    '/teacher-analysis': '/teacher/analysis',
    '/reports': '/teacher/reports',
    '/evaluation': '/teacher/evaluation',
    '/quiz-evaluate': '/teacher/evaluation',
    '/tutor-chat': '/teacher/tutor-chat',
    '/admin/resources': '/admin/resource-generate',
    '/admin/resources/generate': '/admin/resource-generate',
    '/resources': '/admin/resource-generate',
    '/agent-workflow': '/admin/agent-workflow',
    '/logs': '/admin/logs',
    '/log-management': '/admin/logs',
    '/settings': '/admin/settings',
    '/system-settings': '/admin/settings',
    '/demo-status': '/admin/demo-status',
    '/admin': '/dashboard',
    '/users': '/admin/users',
    '/users-roles': '/admin/users'
  };
  const lookupPath = aliases[normalizedPath] || normalizedPath;
  return roleMenus[role].find((item) => item.path === lookupPath);
}
