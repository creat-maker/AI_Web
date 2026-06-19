import { createRouter, createWebHistory } from 'vue-router';

const placeholder = (title: string, description: string, nextSteps?: string[]) => ({
  title,
  description,
  nextSteps
});

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },

  { path: '/student', name: 'StudentHome', component: () => import('../views/StudentHome.vue'), meta: { title: '学习总览' } },
  { path: '/student/profile-dialog', name: 'ProfileDialog', component: () => import('../views/ProfileDialog.vue'), meta: { title: '对话式画像构建' } },
  { path: '/student/courses', name: 'StudentCourses', component: () => import('../views/StudentCourses.vue'), meta: { title: '我的课程' } },
  { path: '/student/learning-path', name: 'StudentLearningPath', component: () => import('../views/StudentLearningPath.vue'), meta: { title: '任务式学习路径' } },
  { path: '/student/learning-paths', redirect: '/student/learning-path' },
  { path: '/student/knowledge-graph', name: 'StudentKnowledgeGraph', component: () => import('../views/StudentKnowledgeGraph.vue'), meta: { title: '课程知识图谱' } },
  { path: '/student/tasks', name: 'StudentTasks', component: () => import('../views/StudentTasks.vue'), meta: { title: '今日任务 / 日历' } },
  { path: '/student/assistant', name: 'StudentAssistant', component: () => import('../views/StudentAssistant.vue'), meta: { title: '智能答疑' } },
  { path: '/student/tutor-chat', redirect: '/student/assistant' },
  { path: '/student/knowledge', name: 'StudentKnowledge', component: () => import('../views/StudentKnowledge.vue'), meta: { title: '知识库 / 课程资料' } },
  { path: '/student/exams', name: 'StudentExamResult', component: () => import('../views/StudentExamResult.vue'), meta: { title: '测验成绩' } },
  { path: '/student/evaluation', redirect: '/student/smart-quiz' },
  { path: '/student/quiz-evaluate', redirect: '/student/smart-quiz' },
  { path: '/student/smart-quiz', name: 'StudentSmartQuiz', component: () => import('../views/StudentSmartQuiz.vue'), meta: { title: '智能测验与练后分析' } },
  { path: '/student/reports', name: 'StudentReport', component: () => import('../views/StudentReport.vue'), meta: { title: '学习报告' } },
  { path: '/student/achievements', name: 'StudentAchievements', component: () => import('../views/StudentAchievements.vue'), meta: { title: '成就徽章' } },
  { path: '/student/points', name: 'StudentPoints', component: () => import('../views/StudentPoints.vue'), meta: { title: '积分等级' } },
  { path: '/student/notes', name: 'StudentNotes', component: () => import('../views/StudentNotes.vue'), meta: { title: '笔记本' } },
  { path: '/student/group', name: 'StudentGroup', component: () => import('../views/StudentGroup.vue'), meta: { title: '学习小组' } },

  { path: '/teacher', name: 'TeacherHome', component: () => import('../views/TeacherHome.vue'), meta: { title: '班级学情' } },
  { path: '/teacher/ai-workbench', name: 'TeacherAIWorkbench', component: () => import('../views/TeacherAIWorkbench.vue'), meta: { title: 'AI 教学工作台' } },
  { path: '/courses', name: 'CourseManage', component: () => import('../views/CourseManage.vue'), meta: { title: '课程管理' } },
  { path: '/knowledge-base', name: 'KnowledgeBase', component: () => import('../views/KnowledgeBase.vue'), meta: { title: '知识库 / 课程资料' } },
  { path: '/profiles', name: 'StudentProfile', component: () => import('../views/StudentProfile.vue'), meta: { title: '学生画像' } },
  { path: '/learning-path', name: 'LearningPath', component: () => import('../views/LearningPath.vue'), meta: { title: '学习路径与任务布置' } },
  { path: '/learning-paths', redirect: '/learning-path' },
  { path: '/teacher-analysis', name: 'TeacherAnalysis', component: () => import('../views/TeacherAnalysis.vue'), meta: { title: '测评分析' } },
  { path: '/reports', name: 'ReportCenter', component: () => import('../views/ReportCenter.vue'), meta: { title: '报告中心' } },
  { path: '/evaluation', name: 'QuizEvaluate', component: () => import('../views/QuizEvaluate.vue'), meta: { title: '测验评价' } },
  { path: '/quiz-evaluate', redirect: '/evaluation' },

  { path: '/admin', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '平台总览' } },
  { path: '/admin/courses', name: 'AdminCourses', component: () => import('../views/AdminCourses.vue'), meta: { title: '课程治理' } },
  { path: '/admin/reports', name: 'AdminReports', component: () => import('../views/AdminReports.vue'), meta: { title: '报告审核中心' } },
  { path: '/admin/knowledge', name: 'AdminKnowledge', component: () => import('../views/AdminKnowledge.vue'), meta: { title: '知识库运营 / 文档解析' } },
  { path: '/admin/content-review', name: 'AdminContentReview', component: () => import('../views/AdminContentReview.vue'), meta: { title: 'AI 内容审核中心' } },
  { path: '/admin/platform-quality', name: 'AdminPlatformQuality', component: () => import('../views/AdminPlatformQuality.vue'), meta: { title: '课程质量评价' } },
  { path: '/admin/decision-center', name: 'TeachingDecisionCenter', component: () => import('../views/TeachingDecisionCenter.vue'), meta: { title: '教学智能决策中心' } },
  { path: '/admin/users', name: 'UserRoleManage', component: () => import('../views/UserRoleManage.vue'), meta: { title: '用户与角色' } },
  { path: '/users', redirect: '/admin/users' },
  { path: '/users-roles', redirect: '/admin/users' },
  { path: '/admin/resources', redirect: '/resource-generation' },
  { path: '/resources', redirect: '/resource-generation' },
  { path: '/resource-generation', name: 'ResourceGenerate', component: () => import('../views/ResourceGenerate.vue'), meta: { title: 'AI 资源生成' } },
  { path: '/agent-workflow', name: 'AgentWorkflow', component: () => import('../views/AgentWorkflow.vue'), meta: { title: 'Agent 工作流' } },
  { path: '/tutor-chat', name: 'TutorChat', component: () => import('../views/TutorChat.vue'), meta: { title: '智能答疑' } },
  { path: '/logs', name: 'LogManagement', component: () => import('../views/LogManagement.vue'), meta: { title: '日志管理' } },
  { path: '/log-management', redirect: '/logs' },
  { path: '/settings', name: 'SystemSettings', component: () => import('../views/SystemSettings.vue'), meta: { title: '系统设置' } },
  { path: '/system-settings', redirect: '/settings' },
  { path: '/capability-boundary', name: 'CapabilityBoundary', component: () => import('../views/CapabilityBoundary.vue'), meta: { title: '系统能力边界说明' } },
  { path: '/demo-status', name: 'DemoStatus', component: () => import('../views/DemoStatus.vue'), meta: { title: '演示验收状态' } },

  {
    path: '/notebook',
    name: 'NotebookPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('笔记本', '用于整理学习笔记、资料摘录、引用片段和个人复盘记录。', ['接入笔记列表与编辑器', '关联智能答疑引用片段', '支持按课程和知识点检索'])
  },
  {
    path: '/study-groups',
    name: 'StudyGroupsPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('学习小组', '用于支持小组学习、同伴互助、讨论主题和协作任务。', ['接入小组列表和成员管理', '关联课程任务和讨论记录', '支持教师查看小组活跃度'])
  },
  {
    path: '/class-students',
    name: 'ClassStudentsPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('班级学生管理', '用于教师查看班级学生、风险等级、学习进度和干预记录。', ['接入学生列表', '关联知识追踪风险等级', '支持批量布置任务'])
  },
  {
    path: '/tutor-management',
    name: 'TutorManagementPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('智能答疑管理', '用于教师查看学生答疑问题、引用质量和待回复问题。', ['接入问答日志列表', '标记高风险无依据回答', '支持教师补充追问建议'])
  },
  {
    path: '/notifications',
    name: 'NotificationsPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('通知中心', '用于课程通知、学习提醒、报告发布和干预任务触达。', ['接入通知模板', '支持按班级或学生发送', '记录通知阅读状态'])
  },
  {
    path: '/teaching-calendar',
    name: 'TeachingCalendarPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('教学日历 / 待办', '用于教师安排教学节奏、待批改任务和班级干预事项。', ['接入日历视图', '同步测验和报告任务', '生成本周教学待办'])
  },
  {
    path: '/permissions',
    name: 'PermissionsPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('权限配置', '用于配置菜单权限、接口权限和三端访问边界。', ['接入权限策略表', '支持角色菜单配置', '对接后端鉴权中间件'])
  },
  {
    path: '/announcement-management',
    name: 'AnnouncementPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('通知公告管理', '用于平台公告、活动通知和系统维护提醒。', ['接入公告编辑', '支持定向发布', '记录公告阅读数据'])
  },
  {
    path: '/data-export',
    name: 'DataExportPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('数据统计与导出', '用于平台统计、报表导出和演示数据审计。', ['接入统计报表', '支持 CSV/Excel 导出', '记录导出任务日志'])
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'FallbackPlaceholder',
    component: () => import('../views/PlaceholderPage.vue'),
    meta: placeholder('规划中模块', '该路径尚未接入正式页面，当前以三端架构占位方式展示，避免出现空白或 404。')
  }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
