<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useRole } from '../composables/useRole';
import type { UserRole } from '../config/roles';

const router = useRouter();
const { setRole } = useRole();

const roleCards: Array<{
  role: UserRole;
  title: string;
  description: string;
  account: string;
  button: string;
  home: string;
  tone: string;
}> = [
  {
    role: 'student',
    title: '学员登录',
    description: '进入个人学习空间，查看课程、路径、答疑、测验和学习报告。',
    account: 'demo_student / 张三',
    button: '进入学生端',
    home: '/student',
    tone: 'blue'
  },
  {
    role: 'teacher',
    title: '教师登录',
    description: '进入教学工作台，查看班级概览、学生画像、测评分析和干预任务。',
    account: 'demo_teacher / 王老师',
    button: '进入教师端',
    home: '/teacher',
    tone: 'green'
  },
  {
    role: 'admin',
    title: '管理员登录',
    description: '进入平台治理视角，查看用户角色、资源生成、Agent 工作流和日志。',
    account: 'demo_admin / 管理员',
    button: '进入管理员端',
    home: '/dashboard',
    tone: 'purple'
  }
];

const highlights = ['学习画像', '个性化路径', '智能答疑', '资源生成', '教学分析', 'Agent 工作流'];

function enter(role: UserRole, home: string) {
  setRole(role);
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
          <span>个性化学习资源与教学智能体平台</span>
        </div>
      </div>

      <div class="login-copy">
        <p class="eyebrow">Competition Demo Ready</p>
        <h1>三端教育智能体演示工作台</h1>
        <p>
          面向学生、教师和管理员，串联学习画像、路径规划、智能答疑、资源生成、报告沉淀和 Agent 工作流治理。
        </p>
      </div>

      <div class="highlight-grid">
        <span v-for="item in highlights" :key="item">{{ item }}</span>
      </div>
    </div>

    <div class="login-card-panel">
      <div class="login-card-heading">
        <h2>选择演示角色</h2>
        <p>当前为演示级入口，不做复杂鉴权；进入后可通过侧边栏切换角色。</p>
      </div>

      <article v-for="item in roleCards" :key="item.role" :class="['login-role-card', item.tone]">
        <div class="role-icon">{{ item.title.slice(0, 1) }}</div>
        <div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
          <span>演示账号：{{ item.account }}</span>
        </div>
        <button type="button" @click="enter(item.role, item.home)">{{ item.button }}</button>
      </article>
    </div>
  </section>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(420px, 0.8fr);
  gap: 28px;
  align-items: center;
  padding: 42px;
  background:
    radial-gradient(circle at 15% 10%, rgba(37, 99, 235, 0.12), transparent 28rem),
    radial-gradient(circle at 92% 18%, rgba(124, 58, 237, 0.12), transparent 26rem),
    linear-gradient(180deg, #f8fbff 0%, var(--bg-page) 100%);
}

.login-brand-panel,
.login-card-panel {
  border: 1px solid var(--border-light);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: var(--card-shadow);
  backdrop-filter: blur(18px);
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
  max-width: 680px;
}

.login-copy h1 {
  margin: 10px 0 14px;
  color: var(--text-main);
  font-size: 42px;
  line-height: 1.12;
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
  border: 1px solid #bfdbfe;
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

.login-card-heading p {
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
  background: #fff;
}

.login-role-card h3 {
  margin: 0 0 6px;
  color: var(--text-main);
  font-size: 17px;
}

.login-role-card p {
  margin: 0 0 8px;
  color: var(--text-secondary);
  line-height: 1.55;
}

.login-role-card span {
  color: var(--text-muted);
  font-size: 13px;
}

.login-role-card button {
  grid-column: 1 / -1;
  width: 100%;
}

.role-icon {
  display: grid;
  place-items: center;
  width: 50px;
  height: 50px;
  border-radius: 12px;
  color: var(--text-light);
  font-weight: 900;
  background: linear-gradient(135deg, var(--color-primary-dark), var(--color-primary));
}

.login-role-card.green .role-icon {
  background: linear-gradient(135deg, #15803d, #16a34a);
}

.login-role-card.purple .role-icon {
  background: linear-gradient(135deg, #6d28d9, #7c3aed);
}

@media (max-width: 980px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 20px;
  }

  .login-brand-panel {
    min-height: auto;
    gap: 36px;
  }

  .login-copy h1 {
    font-size: 32px;
  }
}

@media (max-width: 640px) {
  .highlight-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
