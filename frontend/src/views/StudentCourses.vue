<script setup lang="ts">
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const courses = [
  {
    title: 'Python 程序设计',
    subject: 'Python',
    teacher: '王老师',
    progress: 68,
    status: '进行中',
    last: '今天 10:24',
    hours: '18h 20m',
    focus: '当前学习重点：循环结构'
  },
  {
    title: '循环结构专项补弱课',
    subject: '循环',
    teacher: 'AI 助教',
    progress: 42,
    status: '重点学习',
    last: '今天 09:40',
    hours: '4h 15m',
    focus: 'while 循环、break / continue、循环嵌套'
  },
  {
    title: 'Python 代码实操案例课',
    subject: '实操',
    teacher: '实训助教',
    progress: 55,
    status: '进行中',
    last: '昨天 20:10',
    hours: '7h 35m',
    focus: '用短代码验证循环变量变化'
  }
];

const chapterRows = [
  { name: '基础语法', status: '已完成', progress: 82 },
  { name: '条件判断', status: '已完成', progress: 76 },
  { name: '循环结构', status: '重点学习', progress: 62 },
  { name: 'break / continue', status: '补弱重点', progress: 48 },
  { name: '循环嵌套', status: '补弱重点', progress: 42 },
  { name: '变量变化追踪', status: '后续巩固', progress: 36 },
  { name: '循环综合实操', status: '后续巩固', progress: 28 }
];

const recentRecords = [
  { title: '完成 while 循环终止条件练习', course: 'Python 程序设计', time: '今天 10:24' },
  { title: '阅读循环嵌套变量变化讲解', course: '循环结构专项补弱课', time: '今天 09:40' },
  { title: '提交 break / continue 对比题', course: 'Python 代码实操案例课', time: '昨天 20:10' }
];

const statCards = [
  { label: '进行中课程', value: 3, unit: '门', hint: '围绕当前学习计划', icon: '课' },
  { label: '今日重点', value: '循环', unit: '结构', hint: '当前补弱重点', icon: '循', tone: 'purple' as const },
  { label: '章节正确率', value: 62, unit: '%', hint: '需继续补强', icon: '测', tone: 'orange' as const },
  { label: '学习时长', value: '18h', unit: '20m', hint: 'Python 程序设计累计', icon: '时', tone: 'green' as const }
];
</script>

<template>
  <section class="page student-courses-page">
    <PageHeader
      title="我的课程"
      description="当前学习课程为 Python 程序设计，今日重点为循环结构。"
    >
      <template #actions>
        <button class="secondary">筛选课程</button>
        <button>继续学习循环结构</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="student-course-layout">
      <DataCard title="课程列表" subtitle="围绕李明的 Python 循环结构补弱组织">
        <div class="course-card-grid">
          <article v-for="course in courses" :key="course.title" class="course-card">
            <span class="course-icon">{{ course.subject.slice(0, 1) }}</span>
            <div>
              <strong>{{ course.title }}</strong>
              <p>{{ course.teacher }} / 最近学习 {{ course.last }} / 累计 {{ course.hours }}</p>
              <p class="focus">{{ course.focus }}</p>
              <ProgressBar :value="course.progress" :tone="course.status === '重点学习' ? 'warning' : 'primary'" />
            </div>
            <div class="course-meta">
              <span>{{ course.progress }}%</span>
              <StatusBadge :label="course.status" :tone="course.status === '重点学习' ? 'purple' : 'success'" />
            </div>
          </article>
        </div>
      </DataCard>

      <DataCard title="章节重点" subtitle="Python 程序设计课程结构">
        <div class="chapter-list">
          <article v-for="chapter in chapterRows" :key="chapter.name" class="chapter-row">
            <div>
              <strong>{{ chapter.name }}</strong>
              <StatusBadge :label="chapter.status" :tone="chapter.status === '重点学习' ? 'purple' : 'neutral'" />
            </div>
            <ProgressBar :value="chapter.progress" :tone="chapter.status === '重点学习' ? 'warning' : 'primary'" />
          </article>
        </div>
      </DataCard>
    </div>

    <DataCard title="最近学习记录" subtitle="全部记录围绕循环结构学习目标">
      <div class="record-grid">
        <article v-for="item in recentRecords" :key="item.title" class="record-row">
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.course }}</p>
          </div>
          <span class="muted">{{ item.time }}</span>
        </article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.student-course-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr);
  gap: 16px;
}

.course-card-grid,
.chapter-list,
.record-grid {
  display: grid;
  gap: 12px;
}

.course-card,
.record-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.course-icon {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  color: #fff;
  background: var(--color-primary);
  font-weight: 900;
}

.course-card p,
.record-row p {
  margin: 5px 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.focus {
  color: var(--color-primary-dark);
  font-weight: 700;
}

.course-meta {
  display: grid;
  justify-items: end;
  gap: 8px;
}

.course-meta > span {
  font-size: 22px;
  font-weight: 900;
}

.chapter-row {
  display: grid;
  gap: 8px;
}

.chapter-row > div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

@media (max-width: 1080px) {
  .student-course-layout,
  .course-card,
  .record-row {
    grid-template-columns: 1fr;
  }

  .course-meta {
    justify-items: start;
  }
}
</style>
