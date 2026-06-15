<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

const chartEl = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const suggestions = [
  { title: '补强 while 循环', content: '本周 while 死循环问题错误率偏高，建议完成 3 道变量更新练习。' },
  { title: '复盘循环嵌套', content: '先画行列关系和变量变化表，再完成九九乘法表代码案例。' },
  { title: '调整资源策略', content: '优先使用代码案例和图解资源，减少纯文本讲义比例。' }
];
const message = ref('');
const exportLoading = ref(false);
const reportLoading = ref(false);
const quizResult = {
  score: 67,
  accuracy: 67,
  weakPoints: ['while 循环条件更新', '循环嵌套变量变化', 'break / continue 区分'],
  mistakeReasons: ['变量更新遗漏', '内外层变量混用', '循环控制语句作用范围混淆'],
  abilityScores: [
    { name: '概念理解', value: 62 },
    { name: '代码应用', value: 58 },
    { name: '答题稳定性', value: 64 }
  ],
  recommendedPractice: ['while 循环补全题', '循环嵌套变量变化表', 'break / continue 输出判断题'],
  nextPath: ['while 循环专项练习', '循环嵌套变量变化表', 'break / continue 输出判断题'],
  teacherSuggestion: '建议教师安排 10 分钟 while 循环代码讲解，并推送循环结构补弱资源包。'
};

function joinList(list: string[] | undefined, emptyText = '暂无数据，系统将根据你的学习记录生成建议。') {
  return list?.length ? list.join('、') : emptyText;
}

function exportReport() {
  exportLoading.value = true;
  message.value = '正在准备报告导出...';
  window.setTimeout(() => {
    exportLoading.value = false;
    message.value = '报告导出任务已准备，可在报告中心继续查看。';
  }, 400);
}

function generateReport() {
  reportLoading.value = true;
  message.value = '正在刷新形成性评价报告...';
  window.setTimeout(() => {
    reportLoading.value = false;
    message.value = '已根据最近一次测验结果刷新形成性评价报告。';
  }, 500);
}

function renderChart() {
  if (!chartEl.value) return;
  chart = chart || echarts.init(chartEl.value);
  chart.setOption({
    color: ['#2f6bff', '#22c55e', '#f97316'],
    tooltip: { trigger: 'axis' },
    grid: { left: 34, right: 16, top: 28, bottom: 28 },
    xAxis: { type: 'category', boundaryGap: false, data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f8' } } },
    series: [
      { name: '学习时长', type: 'line', smooth: true, data: [1.2, 1.5, 1.1, 2.1, 1.8, 2.4, 2.3] },
      { name: '完成任务', type: 'line', smooth: true, data: [2, 3, 2, 4, 3, 5, 4] },
      { name: '正确率', type: 'line', smooth: true, data: [72, 76, 78, 80, 82, 84, 86] }
    ]
  });
}

function resizeChart() {
  chart?.resize();
}

onMounted(async () => {
  await nextTick();
  renderChart();
  window.addEventListener('resize', resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  chart?.dispose();
});
</script>

<template>
  <section class="page student-report-page">
    <PageHeader title="Python 循环结构形成性评价报告" description="查看李明的学习摘要、需加强原因、能力评分、AI 建议和教师反馈。">
      <template #actions>
        <button class="secondary" :disabled="exportLoading" @click="exportReport">{{ exportLoading ? '准备中...' : '导出报告' }}</button>
        <button :disabled="reportLoading" @click="generateReport">{{ reportLoading ? '生成中...' : '生成报告' }}</button>
      </template>
    </PageHeader>
    <p v-if="message" class="panel muted">{{ message }}</p>

    <DataCard title="本周学习报告" subtitle="2026-05-25 至 2026-05-31">
      <div class="stat-grid">
        <StatCard label="学习时长" value="12h 24m" hint="较上周 +15%" icon="时" />
        <StatCard label="完成任务" value="18" unit="项" hint="较上周 +20%" icon="任" tone="green" />
        <StatCard label="正确率" value="82" unit="%" hint="较上周 +6%" icon="准" tone="purple" />
        <StatCard label="掌握知识点" value="126" unit="个" hint="较上周 +12%" icon="知" tone="orange" />
      </div>
    </DataCard>

    <DataCard title="趋势图" subtitle="学习时长、任务和正确率变化">
      <div ref="chartEl" class="chart-box"></div>
    </DataCard>

    <DataCard title="最近一次测验结果" subtitle="循环结构专项测验已同步更新形成性评价">
      <div class="suggestion-grid">
        <article class="item"><strong>本次正确率</strong><p>{{ quizResult.accuracy || 0 }}%</p></article>
        <article class="item"><strong>错因摘要</strong><p>{{ joinList(quizResult.mistakeReasons) }}</p></article>
        <article class="item">
          <strong>能力评分</strong>
          <p>{{ quizResult.abilityScores.length ? quizResult.abilityScores.map((item) => `${item.name} ${item.value}分`).join('；') : '暂无能力评分' }}</p>
        </article>
        <article class="item"><strong>推荐练习</strong><p>{{ joinList(quizResult.recommendedPractice) }}</p></article>
      </div>
    </DataCard>

    <DataCard title="本次测验结果" subtitle="循环结构专项测验已同步到报告">
      <div class="suggestion-grid">
        <article class="item"><strong>得分 / 正确率</strong><p>{{ quizResult.score }} 分 / {{ quizResult.accuracy }}%</p></article>
        <article class="item"><strong>薄弱点</strong><p>{{ joinList(quizResult.weakPoints) }}</p></article>
        <article class="item"><strong>错因分析</strong><p>{{ joinList(quizResult.mistakeReasons, '暂无错因分析') }}</p></article>
      </div>
    </DataCard>

    <DataCard title="能力维度评分" subtitle="概念理解、代码应用、答题稳定性、学习活跃度、资源利用率和知识迁移能力">
      <div class="suggestion-grid">
        <article v-for="item in [
          { title: '概念理解', content: '62 / 100' },
          { title: '代码应用', content: '58 / 100' },
          { title: '答题稳定性', content: '64 / 100' },
          { title: '学习活跃度', content: '76 / 100' },
          { title: '资源利用率', content: '68 / 100' },
          { title: '知识迁移能力', content: '55 / 100' }
        ]" :key="item.title" class="item">
          <strong>{{ item.title }}</strong>
          <p>{{ item.content }}</p>
        </article>
      </div>
    </DataCard>

    <DataCard title="AI 学习建议与教师反馈" subtitle="基于本周学习行为、测验结果和学习表现">
      <div class="suggestion-grid">
        <article v-for="item in suggestions" :key="item.title" class="item">
          <strong>{{ item.title }}</strong>
          <p>{{ item.content }}</p>
        </article>
      </div>
    </DataCard>

    <DataCard title="下一步学习路径与教师干预建议" subtitle="根据最近一次测验更新">
      <div class="suggestion-grid">
        <article v-for="item in quizResult.nextPath" :key="item" class="item">
          <strong>{{ item }}</strong>
          <p>完成后继续更新循环结构形成性评价。</p>
        </article>
        <article class="item">
          <strong>教师干预建议</strong>
          <p>{{ quizResult.teacherSuggestion }}</p>
        </article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 980px) {
  .suggestion-grid {
    grid-template-columns: 1fr;
  }
}
</style>
