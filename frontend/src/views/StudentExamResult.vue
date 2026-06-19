<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { BarChart, LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

echarts.use([BarChart, LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

const trendEl = ref<HTMLDivElement | null>(null);
const distributionEl = ref<HTMLDivElement | null>(null);
let trendChart: echarts.ECharts | null = null;
let distributionChart: echarts.ECharts | null = null;

const records = [
  { title: 'Python 循环结构形成性测验', score: 76, date: '2026-06-11', status: '已生成报告' },
  { title: 'while 循环专项练习', score: 68, date: '2026-06-10', status: '需复盘' },
  { title: '循环嵌套小测', score: 72, date: '2026-06-09', status: '需复盘' },
  { title: 'break / continue 变式题', score: 78, date: '2026-06-08', status: '通过' }
];

const weakPoints = [
  { name: 'while 循环条件更新', value: 52 },
  { name: '循环嵌套变量变化', value: 48 },
  { name: 'break / continue 区分', value: 45 },
  { name: 'for 循环', value: 72 }
];
const syncMessage = ref('');
const submitted = ref(false);
const submitLoading = ref(false);
const reviewLoading = ref(false);
const latestResult = ref({
  score: 67,
  accuracy: 67,
  weakPoints: ['while 循环条件更新', '循环嵌套变量变化', 'break / continue 区分'],
  mistakeReasons: [
    'while 循环变量更新位置不稳定，容易导致终止条件失效。',
    '循环嵌套时内外层变量变化没有分列记录，容易漏掉执行顺序。',
    'break / continue 的作用范围混淆，输出结果判断不够稳定。'
  ],
  suggestedResources: [
    'while 循环条件更新专项练习',
    '循环嵌套变量变化表',
    'break / continue 输出判断题'
  ],
  nextLearningPath: ['诊断补弱', '案例实操', '练习测评']
});

function submitLoopQuiz() {
  submitLoading.value = true;
  submitted.value = true;
  syncMessage.value = '已同步更新学习建议';
  window.setTimeout(() => {
    submitLoading.value = false;
  }, 500);
}

function openReviewAdvice() {
  reviewLoading.value = true;
  syncMessage.value = '正在整理错题复盘建议...';
  window.setTimeout(() => {
    reviewLoading.value = false;
    syncMessage.value = '已为你打开错题复盘建议：先复盘 while 循环变量更新。';
  }, 400);
}

function safeList(list: string[] | undefined, emptyText = '暂无数据，系统将根据你的学习记录生成建议。') {
  return list?.length ? list.join('、') : emptyText;
}

function safePath(list: string[] | undefined) {
  return list?.length ? list.join(' -> ') : '暂无数据，系统将根据你的学习记录生成建议。';
}

function renderCharts() {
  if (trendEl.value) {
    trendChart = trendChart || echarts.init(trendEl.value);
    trendChart.setOption({
      color: ['#2f6bff'],
      tooltip: { trigger: 'axis' },
      grid: { left: 36, right: 14, top: 28, bottom: 28 },
      xAxis: { type: 'category', boundaryGap: false, data: ['04-20', '04-27', '05-04', '05-11', '05-18', '05-30'] },
      yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: '#edf2f8' } } },
      series: [{ type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: [72, 76, 80, 84, 88, 95] }]
    });
  }
  if (distributionEl.value) {
    distributionChart = distributionChart || echarts.init(distributionEl.value);
    distributionChart.setOption({
      color: ['#7c5cff'],
      tooltip: { trigger: 'axis' },
      grid: { left: 36, right: 14, top: 28, bottom: 28 },
      xAxis: { type: 'category', data: ['90-100', '80-89', '70-79', '60-69', '<60'] },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f8' } } },
      series: [{ type: 'bar', barWidth: 28, data: [2, 1, 1, 0, 0], itemStyle: { borderRadius: [8, 8, 0, 0] } }]
    });
  }
}

function resizeCharts() {
  trendChart?.resize();
  distributionChart?.resize();
}

onMounted(async () => {
  await nextTick();
  renderCharts();
  window.addEventListener('resize', resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  trendChart?.dispose();
  distributionChart?.dispose();
});
</script>

<template>
  <section class="page exam-page">
    <PageHeader title="Python 循环结构形成性评价报告" description="查看本次学习知识点、完成任务、正确率、错题知识点、错因分析和下一步路径。">
      <template #actions>
        <button class="secondary" :disabled="reviewLoading" @click="openReviewAdvice">{{ reviewLoading ? '整理中...' : '错题复盘' }}</button>
        <button :disabled="submitLoading" @click="submitLoopQuiz">{{ submitLoading ? '提交中...' : submitted ? '已提交' : '提交测验' }}</button>
      </template>
    </PageHeader>
    <p v-if="syncMessage" class="panel muted">{{ syncMessage }}</p>

    <div class="stat-grid">
      <StatCard label="平均分" value="86" unit="分" hint="较上次 +6" icon="均" />
      <StatCard label="最高分" value="98" unit="分" hint="Python 测验" icon="高" tone="green" />
      <StatCard label="测验次数" value="24" unit="次" hint="本学期" icon="测" tone="purple" />
      <StatCard label="通过率" value="92" unit="%" hint="4 次全部通过" icon="过" tone="cyan" />
    </div>

    <div class="two-column">
      <DataCard title="成绩趋势图" subtitle="最近测验成绩变化">
        <div ref="trendEl" class="chart-box"></div>
      </DataCard>
      <DataCard title="成绩分布图" subtitle="按分数段统计">
        <div ref="distributionEl" class="chart-box"></div>
      </DataCard>
    </div>

    <div class="two-column">
      <DataCard title="最近测验记录" subtitle="成绩、时间和状态">
        <div class="list">
          <article v-for="item in records" :key="item.title" class="item compact">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.date }} · {{ item.score }} 分</p>
            </div>
            <StatusBadge :label="item.status" tone="success" />
          </article>
        </div>
      </DataCard>
      <DataCard title="薄弱知识点建议" subtitle="按错题和掌握度生成">
        <div class="weak-list">
          <div v-for="item in weakPoints" :key="item.name" class="weak-row">
            <span>{{ item.name }}</span>
            <ProgressBar :value="item.value" :tone="item.value > 40 ? 'warning' : 'primary'" />
            <strong>{{ item.value }}%</strong>
          </div>
        </div>
      </DataCard>
    </div>

    <DataCard title="本次测验联动结果" subtitle="提交后同步更新画像、学习路径和报告">
      <p v-if="!submitted" class="empty-note">暂无数据，系统将根据你的学习记录生成建议。</p>
      <div class="formative-grid">
        <article><strong>正确率</strong><p>{{ latestResult.accuracy || 0 }}%</p></article>
        <article><strong>薄弱知识点</strong><p>{{ safeList(latestResult.weakPoints) }}</p></article>
        <article><strong>错因分析</strong><p>{{ latestResult.mistakeReasons?.length ? latestResult.mistakeReasons.join('；') : '暂无数据，系统将根据你的学习记录生成建议。' }}</p></article>
        <article><strong>推荐资源</strong><p>{{ safeList(latestResult.suggestedResources) }}</p></article>
        <article><strong>下一步路径</strong><p>{{ safePath(latestResult.nextLearningPath) }}</p></article>
        <article><strong>同步状态</strong><p>{{ submitted ? '已同步更新学习建议' : '等待提交测验' }}</p></article>
        <article><strong>画像更新</strong><p>系统发现循环结构掌握还不够稳定，建议继续专项巩固。</p></article>
      </div>
    </DataCard>

    <DataCard title="形成性评价摘要" subtitle="测验后自动生成，供学生复盘和教师干预使用。">
      <div class="formative-grid">
        <article><strong>本次学习知识点</strong><p>for 循环、while 循环、break / continue、循环嵌套</p></article>
        <article><strong>完成任务</strong><p>诊断测验、while 专项练习、循环嵌套代码题</p></article>
        <article><strong>错因分析</strong><p>while 循环变量更新遗漏，嵌套循环内外层变量混用。</p></article>
        <article><strong>AI 学习建议</strong><p>先画变量变化表，再运行最小代码验证循环条件。</p></article>
        <article><strong>推荐下一步路径</strong><p>核心概念学习 -> 案例实操 -> 练习测评。</p></article>
        <article><strong>教师干预建议</strong><p>课堂中用猜数字案例讲解 while 终止条件。</p></article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.weak-list {
  display: grid;
  gap: 12px;
}

.weak-row {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr) 46px;
  gap: 10px;
  align-items: center;
}

.formative-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.formative-grid article {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
}

.formative-grid p {
  margin: 8px 0 0;
  color: var(--color-text-sub);
  line-height: 1.6;
}

.empty-note {
  margin: 0 0 12px;
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--color-text-sub);
  background: #f8fafc;
}
</style>
