<script setup lang="ts">
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const statCards = [
  { label: '班级人数', value: 36, unit: '人', hint: 'Python 程序设计', icon: '班' },
  { label: '章节均分', value: 74, unit: '分', hint: '循环结构专项测验', icon: '分', tone: 'purple' as const },
  { label: '学习预警', value: 6, unit: '人', hint: '李明为重点关注对象', icon: '预', tone: 'orange' as const },
  { label: '补弱资源', value: 7, unit: '类', hint: '已生成资源包', icon: '资', tone: 'green' as const }
];

const weakPoints = [
  { name: 'while 循环条件更新', value: 52, students: 18 },
  { name: '循环嵌套变量变化', value: 47, students: 15 },
  { name: 'break / continue 区分', value: 39, students: 13 },
  { name: 'for 循环边界判断', value: 32, students: 10 }
];

const warningStudents = [
  {
    name: '李明',
    profile: '基础薄弱 + 代码实操偏好型',
    risk: '干预优先级：中',
    weak: ['while 循环条件更新', '循环嵌套变量变化', 'break / continue 区分'],
    suggestion: '推送循环结构补弱资源包，安排 10 分钟代码讲解，布置 3 道 while 循环补全题。'
  },
  {
    name: '陈思',
    profile: '概念理解较弱型',
    risk: '需关注',
    weak: ['for 循环边界判断', '循环嵌套变量变化'],
    suggestion: '先完成变量变化表，再进行循环嵌套短代码练习。'
  },
  {
    name: '赵雨',
    profile: '答题稳定性不足型',
    risk: '需关注',
    weak: ['break / continue 区分'],
    suggestion: '用 6 道控制语句判断题强化跳出与跳过的差异。'
  }
];

const quizzes = [
  { title: '循环结构专项测验', score: 74, status: '已完成', time: '06-11 10:20' },
  { title: 'while 循环补全题', score: 62, status: '已完成', time: '06-11 09:30' },
  { title: 'break / continue 对比练习', score: 68, status: '待讲评', time: '06-10 18:00' },
  { title: '循环嵌套变量追踪题', score: 59, status: '需复盘', time: '06-10 16:20' }
];

const interventions = [
  { title: '推送循环结构补弱资源包', content: '向李明推送讲解文档、代码实操案例、专项练习和视频脚本，优先覆盖 while 循环死循环问题。' },
  { title: '安排 10 分钟代码讲解', content: '课堂中用三段短代码演示初始值、循环条件和变量更新的关系。' },
  { title: '布置 3 道 while 循环补全题', content: '要求学生先写变量变化表，再提交可运行代码，避免只背概念。' }
];
</script>

<template>
  <section class="page analysis-page">
    <PageHeader
      title="Python 循环结构学情分析"
      description="面向《Python 程序设计》循环结构章节，聚焦李明画像、薄弱点分布和教师干预策略。"
    >
      <template #actions>
        <button class="secondary">导出分析</button>
        <button>生成干预任务</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="analysis-layout">
      <DataCard title="最近测验与练习" subtitle="循环结构形成性评价记录">
        <div class="quiz-list">
          <article v-for="quiz in quizzes" :key="quiz.title" class="quiz-row">
            <div>
              <strong>{{ quiz.title }}</strong>
              <p>{{ quiz.time }} / 平均 {{ quiz.score }} 分</p>
            </div>
            <StatusBadge :label="quiz.status" :tone="quiz.status === '已完成' ? 'success' : 'warning'" />
          </article>
        </div>
      </DataCard>

      <DataCard title="班级薄弱点" subtitle="错误率越高越需要优先干预">
        <div class="weak-list">
          <div v-for="item in weakPoints" :key="item.name" class="weak-row">
            <span>{{ item.name }}</span>
            <ProgressBar :value="item.value" tone="warning" />
            <strong>{{ item.students }} 人</strong>
          </div>
        </div>
      </DataCard>
    </div>

    <DataCard title="需关注学生画像" subtitle="重点关注李明的循环结构掌握情况">
      <div class="student-grid">
        <article v-for="student in warningStudents" :key="student.name" class="student-card">
          <div class="student-head">
            <div>
              <strong>{{ student.name }}</strong>
              <p>{{ student.profile }}</p>
            </div>
            <StatusBadge :label="student.risk" :tone="student.risk.includes('中') ? 'warning' : 'neutral'" />
          </div>
          <div class="tag-list">
            <span v-for="item in student.weak" :key="item">{{ item }}</span>
          </div>
          <p>{{ student.suggestion }}</p>
        </article>
      </div>
    </DataCard>

    <DataCard title="教师干预建议" subtitle="围绕李明的循环结构补弱路径执行">
      <div class="suggestion-grid">
        <article v-for="item in interventions" :key="item.title" class="suggestion-card">
          <strong>{{ item.title }}</strong>
          <p>{{ item.content }}</p>
        </article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.analysis-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 0.9fr);
  gap: 16px;
}

.quiz-list,
.weak-list,
.student-grid,
.suggestion-grid {
  display: grid;
  gap: 12px;
}

.quiz-row,
.student-card,
.suggestion-card {
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.quiz-row,
.student-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.quiz-row p,
.student-card p,
.suggestion-card p {
  margin: 6px 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.weak-row {
  display: grid;
  grid-template-columns: 160px minmax(0, 1fr) 56px;
  gap: 10px;
  align-items: center;
}

.student-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.suggestion-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag-list span {
  border-radius: 999px;
  padding: 5px 9px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-size: 12px;
  font-weight: 700;
}

@media (max-width: 1080px) {
  .analysis-layout,
  .student-grid,
  .suggestion-grid {
    grid-template-columns: 1fr;
  }
}
</style>
