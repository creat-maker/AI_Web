<script setup lang="ts">
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const courses = [
  { name: 'Python 爬虫基础与实践', teacher: '王老师', type: '技术课程', students: 1256, progress: 78, status: '进行中', updated: '05-30 10:25', alerts: 1 },
  { name: '机器学习与数据挖掘', teacher: '张老师', type: '技术课程', students: 856, progress: 62, status: '进行中', updated: '05-30 09:48', alerts: 0 },
  { name: '数据结构与算法', teacher: '陈老师', type: '基础课程', students: 987, progress: 91, status: '待审核', updated: '05-29 21:15', alerts: 2 },
  { name: 'Web 前端开发', teacher: '李老师', type: '通识课程', students: 642, progress: 45, status: '即将开始', updated: '05-29 18:40', alerts: 0 },
  { name: '计算机网络原理', teacher: '刘老师', type: '技术课程', students: 554, progress: 35, status: '已归档', updated: '05-28 16:22', alerts: 0 }
];

const quality = [
  { label: '课程完成率', value: 76, tone: 'success' as const },
  { label: '学生活跃度', value: 82, tone: 'primary' as const },
  { label: '资源完整度', value: 88, tone: 'primary' as const },
  { label: '异常提醒处理', value: 64, tone: 'warning' as const }
];

function statusTone(status: string) {
  if (status === '进行中') return 'success';
  if (status === '待审核') return 'warning';
  if (status === '已归档') return 'neutral';
  return 'info';
}
</script>

<template>
  <section class="page">
    <PageHeader title="课程管理" description="面向平台治理的课程审核、归档、进度监控与质量巡检。">
      <template #actions>
        <button>新建课程</button>
        <button class="secondary">批量审核</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard label="课程总数" value="128" unit="门" icon="课" />
      <StatCard label="进行中课程" value="96" unit="门" icon="行" tone="green" />
      <StatCard label="待审核课程" value="12" unit="门" icon="审" tone="orange" />
      <StatCard label="已归档课程" value="14" unit="门" icon="档" tone="purple" />
      <StatCard label="课程完成率" value="76.3" unit="%" icon="率" tone="cyan" />
    </div>

    <div class="content-with-aside">
      <DataCard title="平台课程列表" subtitle="课程名称、教师、类型、学生规模和审核状态">
        <template #action>
          <button class="secondary">导出数据</button>
        </template>
        <div class="filter-row admin-course-filter">
          <input placeholder="搜索课程名称、教师、分类..." />
          <select><option>全部类型</option><option>技术课程</option><option>基础课程</option><option>通识课程</option></select>
          <select><option>全部状态</option><option>进行中</option><option>即将开始</option><option>待审核</option><option>已归档</option></select>
          <select><option>全部教师</option><option>王老师</option><option>张老师</option><option>陈老师</option></select>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>课程名称</th>
              <th>教师</th>
              <th>类型</th>
              <th>学生数</th>
              <th>进度</th>
              <th>状态</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.name">
              <td><strong>{{ course.name }}</strong></td>
              <td>{{ course.teacher }}</td>
              <td><StatusBadge :label="course.type" :tone="course.type === '基础课程' ? 'purple' : 'info'" /></td>
              <td>{{ course.students.toLocaleString() }}</td>
              <td>
                <div class="table-progress">
                  <span>{{ course.progress }}%</span>
                  <ProgressBar :value="course.progress" :tone="course.progress > 70 ? 'success' : course.progress < 50 ? 'warning' : 'primary'" />
                </div>
              </td>
              <td><StatusBadge :label="course.status" :tone="statusTone(course.status)" /></td>
              <td>{{ course.updated }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost">查看</button>
                  <button class="ghost">审核</button>
                  <button class="ghost">归档</button>
                  <button class="ghost">更多</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <DataCard title="课程质量概览" subtitle="平台课程治理关键指标">
        <div class="quality-list">
          <div v-for="item in quality" :key="item.label" class="quality-row">
            <div>
              <strong>{{ item.label }}</strong>
              <span>{{ item.value }}%</span>
            </div>
            <ProgressBar :value="item.value" :tone="item.tone" />
          </div>
        </div>
        <div class="alert-card">
          <StatusBadge label="异常提醒" tone="warning" />
          <strong>3 门课程需要复核</strong>
          <p>包含资源缺失、完成率异常下降、待审核超过 24 小时等治理事件。</p>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.admin-course-filter {
  grid-template-columns: minmax(240px, 1fr) 150px 150px 150px;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.quality-list {
  display: grid;
  gap: 16px;
}

.quality-row {
  display: grid;
  gap: 8px;
}

.quality-row div {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-sub);
}

.quality-row strong {
  color: var(--color-text-main);
}

.alert-card {
  display: grid;
  gap: 8px;
  margin-top: 18px;
  border: 1px solid #fde68a;
  border-radius: 16px;
  padding: 14px;
  background: #fffbeb;
}

.alert-card p {
  margin: 0;
  line-height: 1.6;
}

@media (max-width: 980px) {
  .admin-course-filter {
    grid-template-columns: 1fr;
  }
}
</style>
