import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { hasDemoSession, readStoredRole } from '../composables/useRole';
import { roleHomePath, type UserRole } from '../config/roles';

const allRoles: UserRole[] = ['student', 'teacher', 'admin'];

function roleHomeRedirect() {
  return roleHomePath[readStoredRole() || 'student'];
}

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: roleHomeRedirect },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true, title: '登录' } },
  { path: '/unauthorized', name: 'Unauthorized', component: () => import('../views/Unauthorized.vue'), meta: { title: '无访问权限', roles: allRoles } },

  { path: '/student', name: 'StudentHome', component: () => import('../views/StudentHome.vue'), meta: { title: '学习总览', roles: ['student'] } },
  { path: '/student/profile', name: 'StudentProfile', component: () => import('../views/StudentProfile.vue'), meta: { title: '学生画像', roles: ['student'] } },
  { path: '/student/profile-dialog', name: 'ProfileDialog', component: () => import('../views/ProfileDialog.vue'), meta: { title: '画像构建', roles: ['student'] } },
  { path: '/student/courses', name: 'StudentCourses', component: () => import('../views/StudentCourses.vue'), meta: { title: '我的课程', roles: ['student'] } },
  { path: '/student/resources', name: 'StudentResources', component: () => import('../views/StudentResources.vue'), meta: { title: '学习资源', roles: ['student'] } },
  { path: '/student/learning-path', name: 'StudentLearningPath', component: () => import('../views/StudentLearningPath.vue'), meta: { title: '学习路径', roles: ['student'] } },
  { path: '/student/learning-paths', redirect: '/student/learning-path' },
  { path: '/student/knowledge-graph', name: 'StudentKnowledgeGraph', component: () => import('../views/StudentKnowledgeGraph.vue'), meta: { title: '知识图谱', roles: ['student'] } },
  { path: '/student/tasks', name: 'StudentTasks', component: () => import('../views/StudentTasks.vue'), meta: { title: '今日任务', roles: ['student'] } },
  { path: '/student/assistant', name: 'StudentAssistant', component: () => import('../views/StudentAssistant.vue'), meta: { title: '智能答疑', roles: ['student'] } },
  { path: '/student/tutor-chat', redirect: '/student/assistant' },
  { path: '/student/knowledge', name: 'StudentKnowledge', component: () => import('../views/StudentKnowledge.vue'), meta: { title: '知识库', roles: ['student'] } },
  { path: '/student/exams', name: 'StudentExamResult', component: () => import('../views/StudentExamResult.vue'), meta: { title: '测验成绩', roles: ['student'] } },
  { path: '/student/quiz', redirect: '/student/smart-quiz' },
  { path: '/student/evaluation', redirect: '/student/smart-quiz' },
  { path: '/student/quiz-evaluate', redirect: '/student/smart-quiz' },
  { path: '/student/smart-quiz', name: 'StudentSmartQuiz', component: () => import('../views/StudentSmartQuiz.vue'), meta: { title: '智能测验', roles: ['student'] } },
  { path: '/student/loop-game', name: 'StudentLoopGame', component: () => import('../views/StudentLoopGame.vue'), meta: { title: '循环闯关', roles: ['student'] } },
  { path: '/student/report', redirect: '/student/reports' },
  { path: '/student/reports', name: 'StudentReport', component: () => import('../views/StudentReport.vue'), meta: { title: '学习报告', roles: ['student'] } },
  { path: '/student/achievements', name: 'StudentAchievements', component: () => import('../views/StudentAchievements.vue'), meta: { title: '成就徽章', roles: ['student'] } },
  { path: '/student/points', name: 'StudentPoints', component: () => import('../views/StudentPoints.vue'), meta: { title: '积分等级', roles: ['student'] } },
  { path: '/student/notes', name: 'StudentNotes', component: () => import('../views/StudentNotes.vue'), meta: { title: '笔记本', roles: ['student'] } },
  { path: '/student/group', name: 'StudentGroup', component: () => import('../views/StudentGroup.vue'), meta: { title: '学习小组', roles: ['student'] } },

  { path: '/teacher', name: 'TeacherHome', component: () => import('../views/TeacherHome.vue'), meta: { title: '班级学情', roles: ['teacher'] } },
  { path: '/teacher/ai-workbench', name: 'TeacherAIWorkbench', component: () => import('../views/TeacherAIWorkbench.vue'), meta: { title: 'AI 教学工作台', roles: ['teacher'] } },
  { path: '/teacher/courses', name: 'CourseManage', component: () => import('../views/CourseManage.vue'), meta: { title: '课程管理', roles: ['teacher'] } },
  { path: '/teacher/knowledge-base', name: 'KnowledgeBase', component: () => import('../views/KnowledgeBase.vue'), meta: { title: '知识库', roles: ['teacher'] } },
  { path: '/teacher/profiles', name: 'TeacherStudentProfile', component: () => import('../views/StudentProfile.vue'), meta: { title: '学生画像', roles: ['teacher'] } },
  { path: '/teacher/learning-path', name: 'LearningPath', component: () => import('../views/LearningPath.vue'), meta: { title: '学习路径', roles: ['teacher'] } },
  { path: '/teacher/learning-paths', redirect: '/teacher/learning-path' },
  { path: '/teacher/analysis', name: 'TeacherAnalysis', component: () => import('../views/TeacherAnalysis.vue'), meta: { title: '学情分析', roles: ['teacher'] } },
  { path: '/teacher/reports', name: 'ReportCenter', component: () => import('../views/ReportCenter.vue'), meta: { title: '报告中心', roles: ['teacher'] } },
  { path: '/teacher/evaluation', name: 'QuizEvaluate', component: () => import('../views/QuizEvaluate.vue'), meta: { title: '测验评价', roles: ['teacher'] } },
  { path: '/teacher/quiz-evaluate', redirect: '/teacher/evaluation' },
  { path: '/teacher/resource-generation', name: 'ResourceGenerate', component: () => import('../views/ResourceGenerate.vue'), meta: { title: '资源生成中心', roles: ['teacher'] } },
  { path: '/teacher/review-center', redirect: '/teacher/arbitration' },
  { path: '/teacher/arbitration', name: 'TeacherArbitration', component: () => import('../views/TeachingDecisionCenter.vue'), meta: { title: '教师仲裁', roles: ['teacher'] } },
  { path: '/teacher/decision-center', redirect: '/teacher/arbitration' },
  { path: '/teacher/tutor-chat', name: 'TeacherTutorChat', component: () => import('../views/TutorChat.vue'), meta: { title: '智能答疑', roles: ['teacher'] } },

  { path: '/courses', redirect: '/teacher/courses' },
  { path: '/knowledge-base', redirect: '/teacher/knowledge-base' },
  { path: '/profiles', redirect: '/teacher/profiles' },
  { path: '/learning-path', redirect: '/teacher/learning-path' },
  { path: '/learning-paths', redirect: '/teacher/learning-path' },
  { path: '/teacher-analysis', redirect: '/teacher/analysis' },
  { path: '/reports', redirect: '/teacher/reports' },
  { path: '/evaluation', redirect: '/teacher/evaluation' },
  { path: '/quiz-evaluate', redirect: '/teacher/evaluation' },
  { path: '/resource-generation', redirect: '/teacher/resource-generation' },
  { path: '/review-center', redirect: '/teacher/arbitration' },
  { path: '/tutor-chat', redirect: '/teacher/tutor-chat' },

  { path: '/admin', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '平台总览', roles: ['admin'] } },
  { path: '/admin/knowledge-base', name: 'AdminKnowledgeBase', component: () => import('../views/KnowledgeBase.vue'), meta: { title: '知识库', roles: ['admin'] } },
  { path: '/admin/courses', name: 'AdminCourses', component: () => import('../views/AdminCourses.vue'), meta: { title: '课程治理', roles: ['admin'] } },
  { path: '/admin/reports', name: 'AdminReports', component: () => import('../views/AdminReports.vue'), meta: { title: '报告审核中心', roles: ['admin'] } },
  { path: '/admin/knowledge', name: 'AdminKnowledge', component: () => import('../views/AdminKnowledge.vue'), meta: { title: '知识库运营', roles: ['admin'] } },
  { path: '/admin/content-review', name: 'AdminContentReview', component: () => import('../views/AdminContentReview.vue'), meta: { title: '内容审核', roles: ['admin'] } },
  { path: '/admin/platform-quality', name: 'AdminPlatformQuality', component: () => import('../views/AdminPlatformQuality.vue'), meta: { title: '平台质量', roles: ['admin'] } },
  { path: '/admin/decision-center', name: 'TeachingDecisionCenter', component: () => import('../views/TeachingDecisionCenter.vue'), meta: { title: '教学决策中心', roles: ['admin'] } },
  { path: '/admin/users', name: 'UserRoleManage', component: () => import('../views/UserRoleManage.vue'), meta: { title: '用户与角色', roles: ['admin'] } },
  { path: '/admin/resource-generate', name: 'AdminResourceGenerate', component: () => import('../views/AdminResourceGenerate.vue'), meta: { title: '资源生成中心', roles: ['admin'] } },
  { path: '/admin/agent-workflow', name: 'AgentWorkflow', component: () => import('../views/AgentWorkflow.vue'), meta: { title: 'Agent 工作流', roles: ['admin'] } },
  { path: '/admin/logs', name: 'LogManagement', component: () => import('../views/LogManagement.vue'), meta: { title: '日志管理', roles: ['admin'] } },
  { path: '/admin/settings', name: 'SystemSettings', component: () => import('../views/SystemSettings.vue'), meta: { title: '系统设置', roles: ['admin'] } },
  { path: '/admin/demo-status', name: 'DemoStatus', component: () => import('../views/DemoStatus.vue'), meta: { title: '系统运行状态', roles: ['admin'] } },
  { path: '/users', redirect: '/admin/users' },
  { path: '/users-roles', redirect: '/admin/users' },
  { path: '/admin/resources', redirect: '/admin/resource-generate' },
  { path: '/admin/resources/generate', redirect: '/admin/resource-generate' },
  { path: '/resources', redirect: '/admin/resource-generate' },
  { path: '/agent-workflow', redirect: '/admin/agent-workflow' },
  { path: '/logs', redirect: '/admin/logs' },
  { path: '/log-management', redirect: '/admin/logs' },
  { path: '/settings', redirect: '/admin/settings' },
  { path: '/system-settings', redirect: '/admin/settings' },
  { path: '/demo-status', redirect: '/admin/demo-status' },

  { path: '/capability-boundary', name: 'CapabilityBoundary', component: () => import('../views/CapabilityBoundary.vue'), meta: { public: true, title: '平台能力说明' } },

  { path: '/profile', name: 'ProfileCenter', component: () => import('../views/ProfileCenter.vue'), meta: { title: '个人中心', roles: allRoles } },
  { path: '/account-settings', name: 'AccountSettings', component: () => import('../views/AccountSettings.vue'), meta: { title: '账号设置', roles: allRoles } },
  { path: '/help-center', name: 'HelpCenter', component: () => import('../views/HelpCenter.vue'), meta: { title: '帮助中心', roles: allRoles } },

  { path: '/:pathMatch(.*)*', redirect: roleHomeRedirect }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const currentRole = readStoredRole();

  if (to.path === '/login' && currentRole && hasDemoSession()) {
    return roleHomePath[currentRole];
  }
  if (to.meta.public) return true;
  if (!hasDemoSession() || !currentRole) return { path: '/login', query: { redirect: to.fullPath } };

  const allowedRoles = to.meta.roles as UserRole[] | undefined;
  if (allowedRoles?.length && !allowedRoles.includes(currentRole)) {
    return { path: '/unauthorized', query: { from: to.fullPath } };
  }

  return true;
});

export default router;
