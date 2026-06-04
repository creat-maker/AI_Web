<script setup lang="ts">
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const templates = [
  { title: '平台数据报告', desc: '平台用户、课程、资源与 AI 调用总体表现', icon: '数' },
  { title: '课程质量报告', desc: '课程完成率、活跃度、资源完整度与异常提醒', icon: '课' },
  { title: '学生学习报告', desc: '学习进度、任务完成、测验表现与成长趋势', icon: '学' },
  { title: 'AI 服务报告', desc: '生成成功率、调用量、失败原因与服务健康', icon: 'AI' },
  { title: '系统运行报告', desc: '日志告警、接口异常、存储与备份状态', icon: '稳' }
];

const reports = [
  { name: 'EduMind 平台 5 月运营月报', type: '平台数据报告', time: '2024-05-31 18:00', status: '已完成', owner: 'Admin' },
  { name: 'Python 爬虫课程质量报告', type: '课程质量报告', time: '2024-05-30 20:15', status: '待审核', owner: '王老师' },
  { name: 'AI 服务调用稳定性报告', type: 'AI 服务报告', time: '2024-05-30 11:42', status: '生成中', owner: '系统任务' },
  { name: '系统运行与告警周报', type: '系统运行报告', time: '2024-05-29 09:10', status: '失败', owner: '监控服务' }
];

function reportTone(status: string) {
  if (status === '已完成') return 'success';
  if (status === '待审核' || status === '生成中') return 'warning';
  return 'danger';
}
</script>

<template>
  <section class="page">
    <PageHeader title="报告审核中心" description="管理平台数据报告、课程质量报告、AI 服务报告和系统运行报告。">
      <template #actions>
        <button>一键生成平台月报</button>
        <button class="secondary">批量导出</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard label="报告总数" value="216" unit="份" icon="报" />
      <StatCard label="今日生成" value="32" unit="份" icon="今" tone="green" />
      <StatCard label="待审核" value="18" unit="份" icon="审" tone="orange" />
      <StatCard label="下载次数" value="1,286" unit="次" icon="下" tone="purple" />
    </div>

    <div class="three-column report-template-grid">
      <DataCard v-for="item in templates" :key="item.title">
        <div class="template-card">
          <span>{{ item.icon }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.desc }}</p>
          <button class="secondary">生成报告</button>
        </div>
      </DataCard>
    </div>

    <div class="content-with-aside">
      <DataCard title="最近生成报告" subtitle="报告状态、创建人与操作入口">
        <table class="table">
          <thead>
            <tr>
              <th>报告名称</th>
              <th>类型</th>
              <th>生成时间</th>
              <th>状态</th>
              <th>创建人</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="report in reports" :key="report.name">
              <td><strong>{{ report.name }}</strong></td>
              <td>{{ report.type }}</td>
              <td>{{ report.time }}</td>
              <td><StatusBadge :label="report.status" :tone="reportTone(report.status)" /></td>
              <td>{{ report.owner }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost">预览</button>
                  <button class="ghost">下载</button>
                  <button class="ghost">重新生成</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <DataCard title="报告预览" subtitle="平台月报摘要">
        <div class="preview-card">
          <StatusBadge label="已完成" tone="success" />
          <h3>EduMind 平台 5 月运营月报</h3>
          <p>本月注册用户增长 8.6%，课程完成率 76.3%，AI 生成任务成功率 94.8%，系统健康度稳定在 99.8%。</p>
          <div class="preview-metrics">
            <span>用户 8,345</span>
            <span>课程 128</span>
            <span>资源 2,846</span>
          </div>
          <button>查看完整预览</button>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.report-template-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.template-card,
.preview-card {
  display: grid;
  gap: 10px;
}

.template-card span {
  display: inline-grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.template-card p,
.preview-card p {
  margin: 0;
  line-height: 1.65;
}

.preview-card h3 {
  margin: 0;
  font-size: 18px;
}

.preview-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.preview-metrics span {
  border-radius: 12px;
  padding: 10px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-weight: 700;
  text-align: center;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
