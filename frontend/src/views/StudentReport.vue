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
  { title: '巩固数据解析', content: '本周数据解析错误率偏高，建议完成 3 道 BeautifulSoup 选择器练习。' },
  { title: '提升工程实践', content: '尝试把采集结果保存到 SQLite，形成一个可复用的小项目。' },
  { title: '保持学习节奏', content: '本周连续学习 7 天，建议继续保持每日 30 分钟节奏。' }
];

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
    <PageHeader title="学习报告" description="查看本周学习报告、趋势和 AI 学习建议。">
      <template #actions>
        <button class="secondary">导出报告</button>
        <button>生成报告</button>
      </template>
    </PageHeader>

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

    <DataCard title="AI 学习建议" subtitle="基于本周学习行为和测验结果">
      <div class="suggestion-grid">
        <article v-for="item in suggestions" :key="item.title" class="item">
          <strong>{{ item.title }}</strong>
          <p>{{ item.content }}</p>
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
