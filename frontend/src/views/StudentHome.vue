<script setup lang="ts">
import { RouterLink } from 'vue-router';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const courseCards = [
  { title: 'Python 程序设计', subject: 'Python', teacher: '王老师', progress: 68, status: '进行中' },
  { title: '循环结构专项补弱课', subject: '循环', teacher: 'AI 助教 + 王老师', progress: 42, status: '重点学习' },
  { title: '代码实操训练营', subject: '实操', teacher: '实训助教', progress: 55, status: '进行中' }
];

const statCards = [
  { label: '课程进度', value: 68, unit: '%', hint: 'Python 程序设计', icon: '课' },
  { label: '本章正确率', value: 62, unit: '%', hint: '循环结构专项测验', icon: '测', tone: 'orange' as const },
  { label: '学习状态', value: '需', unit: '巩固', hint: '建议重点练习循环结构', icon: '练', tone: 'orange' as const },
  { label: '资源完成', value: '3 / 7', hint: '补弱资源包进度', icon: '资', tone: 'green' as const }
];

const tasks = [
  { title: '完成 while 循环终止条件补全题', course: 'Python 程序设计 / 循环结构', time: '今天 23:59', done: false },
  { title: '提交循环嵌套变量变化表', course: '代码实操任务', time: '明天 18:00', done: false },
  { title: '复盘 break / continue 易错题', course: '形成性评价反馈', time: '明天 20:00', done: false },
  { title: '观看循环结构讲解视频脚本', course: '个性化资源包', time: '已完成', done: true }
];

const pathNodes = [
  { title: '循环概念回顾', status: 'done', reason: '已完成 for / while 基础概念复习。' },
  { title: 'while 循环条件更新', status: 'active', reason: '李明在死循环题上错误率较高，当前优先补强。' },
  { title: 'break / continue 区分', status: 'active', reason: '通过短代码运行结果判断控制语句作用。' },
  { title: '循环嵌套变量跟踪', status: 'locked', reason: '完成前两项后进入嵌套循环综合练习。' }
];

const weakPoints = [
  { name: 'while 循环条件更新', value: 48 },
  { name: '循环嵌套变量变化', value: 54 },
  { name: 'break / continue 区分', value: 58 }
];

const resources = [
  { title: '循环结构讲解文档', type: '讲义', desc: '用流程图说明 for 与 while 的适用场景。' },
  { title: 'while 死循环修复案例', type: '代码实操', desc: '从初始值、条件、更新语句三步定位问题。' },
  { title: 'break / continue 专项练习', type: '练习', desc: '用 6 道选择和填空题区分跳出与跳过。' },
  { title: '循环结构微课视频脚本', type: '视频脚本', desc: '适合数字人或 TTS 讲解，不描述为实时数字人系统。' }
];
</script>

<template>
  <section class="page student-dashboard">
    <PageHeader
      title="李明的 Python 程序设计学习驾驶舱"
      description="当前学习重点：循环结构。系统发现你在 while 循环和循环嵌套上还需要加强。"
    >
      <template #actions>
        <RouterLink class="btn secondary" to="/student/profile-dialog">构建画像</RouterLink>
        <RouterLink class="btn" to="/student/learning-path">继续补弱</RouterLink>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="student-shell">
      <main class="student-main">
        <div class="two-column">
          <DataCard title="我的课程" subtitle="当前学习课程：Python 程序设计">
            <div class="course-list">
              <article v-for="course in courseCards" :key="course.title" class="course-row">
                <span class="course-thumb">{{ course.subject.slice(0, 1) }}</span>
                <div>
                  <strong>{{ course.title }}</strong>
                  <p>{{ course.teacher }}</p>
                  <ProgressBar :value="course.progress" />
                </div>
                <StatusBadge :label="course.status" :tone="course.status === '重点学习' ? 'purple' : 'success'" />
              </article>
            </div>
          </DataCard>

          <DataCard title="今日任务" subtitle="围绕 while 循环、循环嵌套和 break / continue">
            <div class="task-list">
              <article v-for="task in tasks" :key="task.title" class="task-row">
                <span :class="['task-dot', { done: task.done }]"></span>
                <div>
                  <strong>{{ task.title }}</strong>
                  <p>{{ task.course }}</p>
                </div>
                <span class="task-time">{{ task.time }}</span>
              </article>
            </div>
          </DataCard>
        </div>

        <div class="two-column">
          <DataCard title="一人一堂学习路径" subtitle="李明的循环结构补弱路径">
            <div class="path-list">
              <article v-for="node in pathNodes" :key="node.title" :class="['path-node', node.status]">
                <span></span>
                <div>
                  <strong>{{ node.title }}</strong>
                  <p>{{ node.reason }}</p>
                </div>
              </article>
            </div>
          </DataCard>

          <DataCard title="薄弱知识点" subtitle="由测验和 AI 学伴对话共同更新">
            <div class="weak-list">
              <div v-for="item in weakPoints" :key="item.name" class="weak-row">
                <span>{{ item.name }}</span>
                <ProgressBar :value="item.value" tone="warning" />
                <strong>{{ item.value }}%</strong>
              </div>
            </div>
          </DataCard>
        </div>

        <DataCard title="推荐资源" subtitle="Python 循环结构个性化补弱资源包">
          <div class="resource-grid">
            <article v-for="item in resources" :key="item.title" class="resource-card">
              <StatusBadge :label="item.type" tone="purple" />
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </article>
          </div>
        </DataCard>
      </main>

      <aside class="ai-panel">
        <div class="ai-panel-header">
          <div>
            <h2>诊断式 AI 学伴</h2>
            <p class="muted">基于 Python 程序设计课程知识库回答</p>
          </div>
          <StatusBadge label="在线" tone="success" />
        </div>
        <div class="chat-window">
          <div class="message user">为什么我的 while 循环会死循环？</div>
          <div class="message assistant">
            先检查三个位置：循环变量初始值、循环条件、循环体内是否更新变量。李明当前最容易漏掉第三步，建议先手写前三轮变量变化，再运行代码验证。
          </div>
        </div>
        <div class="reference-card">
          <strong>引用依据</strong>
          <p>Python 程序设计课程知识库 / 循环结构章节</p>
          <p>知识点：while 循环、break / continue、循环嵌套</p>
        </div>
        <div class="question-chips">
          <button class="secondary">while 条件怎么写？</button>
          <button class="secondary">break 和 continue 区别？</button>
          <button class="secondary">循环嵌套怎么跟踪变量？</button>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.student-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
  align-items: start;
}

.student-main,
.course-list,
.task-list,
.path-list,
.weak-list {
  display: grid;
  gap: 12px;
}

.course-row,
.task-row,
.path-node,
.weak-row {
  display: grid;
  gap: 12px;
  align-items: center;
}

.course-row {
  grid-template-columns: 48px minmax(0, 1fr) auto;
}

.task-row {
  grid-template-columns: 14px minmax(0, 1fr) auto;
  border-bottom: 1px solid var(--border-table);
  padding-bottom: 10px;
}

.task-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.path-node {
  grid-template-columns: 16px minmax(0, 1fr);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}

.path-node > span,
.task-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--color-primary);
}

.path-node.locked > span {
  background: var(--text-muted);
}

.task-dot.done {
  background: var(--status-success-solid);
}

.course-thumb {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  color: #fff;
  background: var(--color-primary);
  font-weight: 900;
}

.weak-row {
  grid-template-columns: 150px minmax(0, 1fr) 48px;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.resource-card {
  display: grid;
  gap: 8px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.ai-panel {
  display: grid;
  gap: 14px;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 16px;
  background: var(--bg-card);
  box-shadow: var(--card-shadow);
}

.ai-panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.chat-window,
.reference-card,
.question-chips {
  display: grid;
  gap: 10px;
}

.message {
  border-radius: 12px;
  padding: 12px;
  line-height: 1.65;
}

.message.user {
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
}

.message.assistant,
.reference-card {
  border: 1px solid var(--border-light);
  background: #fff;
}

.question-chips {
  grid-template-columns: 1fr;
}

@media (max-width: 1180px) {
  .student-shell,
  .resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>
