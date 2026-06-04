<script setup lang="ts">
import { computed } from 'vue';
import { TrendingUp } from 'lucide-vue-next';
import type { ScoreDistributionItem, KnowledgeMastery } from '@/api/mocks/data';

const props = defineProps<{
  averageScore: number;
  passRate: string;
  highestScore: number;
  highestScorers: string;
  scoreDistribution: ScoreDistributionItem[];
  knowledgeMastery?: KnowledgeMastery[];
  sampleSize?: number;
}>();

const distributionData = computed(() =>
  props.scoreDistribution.map((item) => ({
    label: item.range,
    value: item.count,
    percent: item.percent,
    barColor: item.range === '不及格' ? 'bg-rose-400' : item.range === '60-69分' ? 'bg-indigo-400' : 'bg-indigo-500',
    valueColor: item.range === '不及格' ? 'text-rose-500' : item.range === '60-69分' ? 'text-indigo-400' : 'text-indigo-600',
  }))
);

const maxCount = computed(() => {
  const counts = distributionData.value.map((d) => d.value);
  return Math.max(...counts) || 1;
});

const defaultKnowledgeMastery: KnowledgeMastery[] = [
  { name: '洛伦兹力基础概念', percent: 92, color: 'emerald' },
  { name: '公式计算 (F=qvB)', percent: 85, color: 'indigo' },
  { name: '圆周运动 (半径与周期)', percent: 68, color: 'amber' },
  { name: '左手定则空间判定', percent: 46, color: 'rose' },
];

const masteryData = computed(() => props.knowledgeMastery || defaultKnowledgeMastery);

const masteryColorClass = (color: KnowledgeMastery['color']) => {
  switch (color) {
    case 'emerald': return 'bg-emerald-500';
    case 'indigo': return 'bg-indigo-500';
    case 'amber': return 'bg-amber-400';
    case 'rose': return 'bg-rose-400';
  }
};

const masteryTextClass = (color: KnowledgeMastery['color']) => {
  switch (color) {
    case 'emerald': return 'text-emerald-600';
    case 'indigo': return 'text-indigo-600';
    case 'amber': return 'text-amber-500';
    case 'rose': return 'text-rose-500';
  }
};
</script>

<template>
  <div class="col-span-2 flex flex-col gap-6">
    <div class="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm flex-1">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-lg font-bold text-gray-800">班级分数段分布</h3>
        <span class="text-xs font-medium text-gray-400 bg-gray-50 px-2 py-1 rounded">样本总量: {{ sampleSize || 15 }}人</span>
      </div>
      <div class="flex items-end h-48 gap-4 px-2 border-b border-gray-100">
        <div
          v-for="bar in distributionData"
          :key="bar.label"
          class="flex-1 h-full flex flex-col justify-end items-center group"
        >
          <div class="relative w-full flex flex-col justify-end items-center transition-all duration-500" :style="{ height: `${(bar.value / maxCount) * 100}%` }">
            <span class="text-sm font-bold mb-1 opacity-0 group-hover:opacity-100 transition-opacity" :class="bar.valueColor">{{ bar.value }}人</span>
            <div class="w-full h-full rounded-t-md shadow-sm" :class="bar.barColor"></div>
          </div>
          <span class="text-[11px] text-gray-500 mt-3 whitespace-nowrap font-medium">{{ bar.label }}</span>
        </div>
      </div>
    </div>

    <div class="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
      <h3 class="text-lg font-bold text-gray-800 mb-6">核心知识点掌握分析</h3>
      <div class="space-y-5">
        <div v-for="item in masteryData" :key="item.name">
          <div class="flex justify-between text-sm mb-2">
            <span class="font-bold text-gray-700">{{ item.name }}</span>
            <span class="font-bold" :class="masteryTextClass(item.color)">{{ item.percent }}% 掌握</span>
          </div>
          <div class="w-full bg-gray-100 rounded-full h-2.5">
            <div class="h-2.5 rounded-full" :class="masteryColorClass(item.color)" :style="{ width: item.percent + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
