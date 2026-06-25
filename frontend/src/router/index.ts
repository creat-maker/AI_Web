import { createRouter, createWebHistory } from 'vue-router';
import { hasDemoSession, readStoredRole } from '../composables/useRole';
import { roleFromPath, roleHomePath } from '../config/roles';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true, title: '登录' } },
  { path: '/unauthorized', name: 'Unauthorized', component: () => import('../views/Unauthorized.vue'), meta: { public: true, title: '无访问权限' } },

  { path: '/student', name: 'StudentHome', component: () => import('../views/StudentHome.vue'), meta: { title: '学习总览' } },
  { path: '/student/profile-dialog', name: 'ProfileDialog', component: () => import('../views/ProfileDialog.vue'), meta: { title: '画像构建' } },
  { path: '/student/courses', name: 'StudentCourses', component: () => import('../views/StudentCourses.vue'), meta: { title: '我的课程' } },
  { path: '/student/resources', name: 'StudentResources', component: () => import('../views/StudentResources.vue'), meta: { title: '学习资源' } },
  { path: '/student/learning-path', name: 'StudentLearningPath', component: () => import('../views/StudentLearningPath.vue'), meta: { title: '学习路径' } },
  { path: '/student/learning-paths', redirect: '/student/learning-path' },
  { path: '/student/knowledge-graph', name: 'StudentKnowledgeGraph', component: () => import('../views/StudentKnowledgeGraph.vue'), meta: { title: '知识图谱' } },
  { path: '/student/tasks', name: 'StudentTasks', component: () => import('../views/StudentTasks.vue'), meta: { title: '今日任务' } },
  { path: '/student/assistant', name: 'StudentAssistant', component: () => import('../views/StudentAssistant.vue'), meta: { title: '智能答疑' } },
  { path: '/student/tutor-chat', redirect: '/student/assistant' },
  { path: '/student/knowledge', name: 'StudentKnowledge', component: () => import('../views/StudentKnowledge.vue'), meta: { title: '知识库' } },
  { path: '/student/exams', name: 'StudentExamResult', component: () => import('../views/StudentExamResult.vue'), meta: { title: '测验成绩' } },
  { path: '/student/evaluation', redirect: '/student/smart-quiz' },
  { path: '/student/quiz-evaluate', redirect: '/student/smart-quiz' },
  { path: '/student/smart-quiz', name: 'StudentSmartQuiz', component: () => import('../views/StudentSmartQuiz.vue'), meta: { title: '智能测验' } },
  { path: '/student/loop-game', name: 'StudentLoopGame', component: () => import('../views/StudentLoopGame.vue'), meta: { title: '循环闯关' } },
  { path: '/student/reports', name: 'StudentReport', component: () => import('../views/StudentReport.vue'), meta: { title: '学习报告' } },
  { path: '/student/achievements', name: 'StudentAchievements', component: () => import('../views/StudentAchievements.vue'), meta: { title: '成就徽章' } },
  { path: '/student/points', name: 'StudentPoints', component: () => import('../views/StudentPoints.vue'), meta: { title: '积分等级' } },
  { path: '/student/notes', name: 'StudentNotes', component: () => import('../views/StudentNotes.vue'), meta: { title: '笔记本' } },
  { path: '/student/group', name: 'StudentGroup', component: () => import('../views/StudentGroup.vue'), meta: { title: '学习小组' } },

  { path: '/teacher', name: 'TeacherHome', component: () => import('../views/TeacherHome.vue'), meta: { title: '班级学情' } },
  { path: '/teacher/ai-workbench', name: 'TeacherAIWorkbench', component: () => import('../views/TeacherAIWorkbench.vue'), meta: { title: 'AI 教学工作台' } },
  { path: '/courses', name: 'CourseManage', component: () => import('../views/CourseManage.vue'), meta: { title: '课程管理' } },
  { path: '/knowledge-base', name: 'KnowledgeBase', component: () => import('../views/KnowledgeBase.vue'), meta: { title: '知识库' } },
  { path: '/profiles', name: 'StudentProfile', component: () => import('../views/StudentProfile.vue'), meta: { title: '学生画像' } },
  { path: '/learning-path', name: 'LearningPath', component: () => import('../views/LearningPath.vue'), meta: { title: '学习路径' } },
  { path: '/learning-paths', redirect: '/learning-path' },
  { path: '/teacher-analysis', name: 'TeacherAnalysis', component: () => import('../views/TeacherAnalysis.vue'), meta: { title: '测评分析' } },
  { path: '/reports', name: 'ReportCenter', component: () => import('../views/ReportCenter.vue'), meta: { title: '报告中心' } },
  { path: '/evaluation', name: 'QuizEvaluate', component: () => import('../views/QuizEvaluate.vue'), meta: { title: '测验评价' } },
  { path: '/quiz-evaluate', redirect: '/evaluation' },
  { path: '/resource-generation', name: 'ResourceGenerate', component: () => import('../views/ResourceGenerate.vue'), meta: { title: '资源生成中心' } },

  { path: '/admin', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '平台总览' } },
  { path: '/admin/courses', name: 'AdminCourses', component: () => import('../views/AdminCourses.vue'), meta: { title: '课程治理' } },
  { path: '/admin/reports', name: 'AdminReports', component: () => import('../views/AdminReports.vue'), meta: { title: '报告审核中心' } },
  { path: '/admin/knowledge', name: 'AdminKnowledge', component: () => import('../views/AdminKnowledge.vue'), meta: { title: '知识库运营' } },
  { path: '/admin/content-review', name: 'AdminContentReview', component: () => import('../views/AdminContentReview.vue'), meta: { title: '内容审核' } },
  { path: '/admin/platform-quality', name: 'AdminPlatformQuality', component: () => import('../views/AdminPlatformQuality.vue'), meta: { title: '平台质量' } },
  { path: '/admin/decision-center', name: 'TeachingDecisionCenter', component: () => import('../views/TeachingDecisionCenter.vue'), meta: { title: '教学决策中心' } },
  { path: '/admin/users', name: 'UserRoleManage', component: () => import('../views/UserRoleManage.vue'), meta: { title: '用户与角色' } },
  { path: '/admin/resource-generate', name: 'AdminResourceGenerate', component: () => import('../views/AdminResourceGenerate.vue'), meta: { title: '资源生成中心' } },
  { path: '/users', redirect: '/admin/users' },
  { path: '/users-roles', redirect: '/admin/users' },
  { path: '/admin/resources', redirect: '/admin/resource-generate' },
  { path: '/admin/resources/generate', redirect: '/admin/resource-generate' },
  { path: '/resources', redirect: '/admin/resource-generate' },
  { path: '/agent-workflow', name: 'AgentWorkflow', component: () => import('../views/AgentWorkflow.vue'), meta: { title: 'Agent 工作流' } },
  { path: '/tutor-chat', name: 'TutorChat', component: () => import('../views/TutorChat.vue'), meta: { title: '智能答疑' } },
  { path: '/logs', name: 'LogManagement', component: () => import('../views/LogManagement.vue'), meta: { title: '日志管理' } },
  { path: '/log-management', redirect: '/logs' },
  { path: '/settings', name: 'SystemSettings', component: () => import('../views/SystemSettings.vue'), meta: { title: '系统设置' } },
  { path: '/system-settings', redirect: '/settings' },
  { path: '/capability-boundary', name: 'CapabilityBoundary', component: () => import('../views/CapabilityBoundary.vue'), meta: { public: true, title: '平台能力说明' } },
  { path: '/demo-status', name: 'DemoStatus', component: () => import('../views/DemoStatus.vue'), meta: { public: true, title: '系统运行状态' } },

  { path: '/profile', name: 'ProfileCenter', component: () => import('../views/ProfileCenter.vue'), meta: { title: '个人中心' } },
  { path: '/account-settings', name: 'AccountSettings', component: () => import('../views/AccountSettings.vue'), meta: { title: '账号设置' } },
  { path: '/help-center', name: 'HelpCenter', component: () => import('../views/HelpCenter.vue'), meta: { title: '帮助中心' } },

  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  if (to.meta.public) return true;
  if (!hasDemoSession()) return { path: '/login', query: { redirect: to.fullPath } };

  const targetRole = roleFromPath(to.path);
  const currentRole = readStoredRole();
  if (targetRole && currentRole && targetRole !== currentRole) {
    return { path: '/unauthorized', query: { from: to.fullPath } };
  }
  if (to.path === '/login' && currentRole) return roleHomePath[currentRole];
  return true;
});

export default router;
