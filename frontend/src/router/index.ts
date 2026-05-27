import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/courses', name: 'CourseManage', component: () => import('../views/CourseManage.vue') },
  { path: '/knowledge-base', name: 'KnowledgeBase', component: () => import('../views/KnowledgeBase.vue') },
  { path: '/profiles', name: 'StudentProfile', component: () => import('../views/StudentProfile.vue') },
  { path: '/learning-paths', name: 'LearningPath', component: () => import('../views/LearningPath.vue') },
  { path: '/resources', name: 'ResourceGenerate', component: () => import('../views/ResourceGenerate.vue') },
  { path: '/agent-workflow', name: 'AgentWorkflow', component: () => import('../views/AgentWorkflow.vue') },
  { path: '/tutor-chat', name: 'TutorChat', component: () => import('../views/TutorChat.vue') },
  { path: '/quiz-evaluate', name: 'QuizEvaluate', component: () => import('../views/QuizEvaluate.vue') },
  { path: '/teacher-analysis', name: 'TeacherAnalysis', component: () => import('../views/TeacherAnalysis.vue') },
  { path: '/reports', name: 'ReportCenter', component: () => import('../views/ReportCenter.vue') },
  { path: '/logs', name: 'LogManagement', component: () => import('../views/LogManagement.vue') },
  { path: '/log-management', redirect: '/logs' },
  { path: '/settings', name: 'SystemSettings', component: () => import('../views/SystemSettings.vue') },
  { path: '/system-settings', redirect: '/settings' }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
