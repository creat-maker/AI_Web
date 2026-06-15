<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useRole } from '../composables/useRole';
import type { UserRole } from '../config/roles';

const router = useRouter();
const { setDemoUserId, setRole } = useRole();

const roleCards: Array<{
  role: UserRole;
  title: string;
  description: string;
  account: string;
  button: string;
  home: string;
  tone: string;
  userId?: string;
}> = [
  {
    role: 'student',
    title: '李明 / 基础薄弱 + 代码实操偏好型',
    description: '进入学生端，查看对话式画像、Python 循环结构补弱、诊断式 AI 学伴和形成性评价。',
    account: 'demo_student / 李明',
    button: '以李明进入',
    home: '/student',
    tone: 'blue',
    userId: 'demo-basic'
  },
  {
    role: 'teacher',
    title: '王老师 / Python 程序设计教师',
    description: '进入教师端，查看循环结构班级学情、需关注学生李明、资源推送和干预建议。',
    account: 'demo_teacher / 王老师',
    button: '进入教师端',
    home: '/teacher',
    tone: 'green'
  },
  {
    role: 'admin',
    title: '管理员 / 内容审核与决策中心',
    description: '进入管理端，演示多智能体资源生成、内容审核、Agent 工作流和教学智能决策中心。',
    account: 'demo_admin / 管理员',
    button: '进入管理端',
    home: '/dashboard',
    tone: 'purple'
  }
];

const highlights = ['对话式画像', 'Python 循环结构补弱', '多智能体资源生成', '诊断式 AI 学伴', '形成性评价', '内容审核与决策'];

function enter(role: UserRole, home: string, userId?: string) {
  setRole(role);
  if (userId) setDemoUserId(userId);
  router.push(home);
}
</script>

<template>
  <section class="login-page">
    <div class="login-brand-panel">
      <div class="login-brand">
        <span class="brand-mark">E</span>
        <div>
          <strong>EduMind Studio</strong>
          <span>个性化教学质量提升演示平台</span>
        </div>
      </div>

      <div class="login-copy">
        <p class="eyebrow">EduMind learning platform</p>
        <h1>围绕 Python 循环结构的一人一堂教学闭环</h1>
        <p>
          平台以《Python 程序设计》循环结构章节为当前重点，串联李明的对话式画像、个性化资源生成、学习路径、诊断式 AI 学伴、形成性评价和内容审核。
        </p>
      </div>

      <div class="highlight-grid">
        <span v-for="item in highlights" :key="item">{{ item }}</span>
      </div>
    </div>

    <div class="login-card-panel">
      <div class="login-card-heading">
        <h2>选择演示角色</h2>
        <p>请选择角色进入对应工作台，查看学生、教师和管理员三端如何围绕同一课程学习数据协同。</p>
      </div>

      <article v-for="item in roleCards" :key="item.role" :class="['login-role-card', item.tone]">
        <div class="role-icon">{{ item.title.slice(0, 1) }}</div>
        <div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
          <span>演示账号：{{ item.account }}</span>
        </div>
        <button type="button" @click="enter(item.role, item.home, item.userId)">{{ item.button }}</button>
      </article>
    </div>
  </section>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(390px, 0.75fr);
  gap: 28px;
  align-items: center;
  padding: 42px;
  background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-page) 100%);
}

.login-brand-panel,
.login-card-panel {
  border: 1px solid var(--border-light);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--card-shadow);
}

.login-brand-panel {
  min-height: 620px;
  display: grid;
  align-content: space-between;
  padding: 34px;
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark,
.role-icon {
  display: grid;
  place-items: center;
  width: 50px;
  height: 50px;
  border-radius: 12px;
  color: #fff;
  background: var(--color-primary);
  font-weight: 900;
}

.login-brand strong {
  display: block;
  color: var(--text-main);
  font-size: 20px;
}

.login-brand span {
  display: block;
  margin-top: 4px;
  color: var(--text-secondary);
}

.login-copy {
  max-width: 700px;
}

.login-copy h1 {
  margin: 10px 0 14px;
  color: var(--text-main);
  font-size: 42px;
  line-height: 1.15;
  letter-spacing: 0;
}

.login-copy p {
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1.8;
}

.highlight-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.highlight-grid span {
  border: 1px solid var(--color-primary-border);
  border-radius: 10px;
  padding: 12px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-weight: 800;
}

.login-card-panel {
  display: grid;
  gap: 14px;
  padding: 24px;
}

.login-card-heading h2 {
  margin: 0 0 6px;
  color: var(--text-main);
  font-size: 24px;
}

.login-card-heading p,
.login-role-card p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.login-role-card {
  display: grid;
  grid-template-columns: 50px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
  background: var(--bg-card);
}

.login-role-card h3 {
  margin: 0 0 6px;
  color: var(--text-main);
  font-size: 17px;
}

.login-role-card span {
  display: block;
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 13px;
}

.login-role-card button {
  grid-column: 1 / -1;
  width: 100%;
}

@media (max-width: 980px) {
  .login-page,
  .highlight-grid {
    grid-template-columns: 1fr;
  }

  .login-page {
    padding: 20px;
  }
}
</style>
