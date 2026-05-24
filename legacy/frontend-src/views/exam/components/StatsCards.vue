<script setup lang="ts">
import { Award, TrendingUp, Users } from 'lucide-vue-next';

defineProps<{
  averageScore: number;
  passRate: string;
  excellentRate?: string;
  highestScore: number;
  highestScorers: string;
  sampleSize?: number;
  lowScoreCount?: number;
}>();
</script>

<template>
  <div class="grid grid-cols-4 gap-5">
    <div class="bg-white p-6 rounded-[24px] shadow-sm border border-gray-50 flex flex-col justify-between">
      <span class="text-sm font-bold text-gray-500">平均分</span>
      <div class="mt-4 flex items-end gap-3">
        <span class="text-5xl font-black text-gray-900">{{ averageScore || '--' }}</span>
        <div v-if="averageScore" class="flex items-center gap-1 text-green-500 bg-green-50 px-2 py-1 rounded-lg text-xs font-bold mb-1">
          <TrendingUp class="w-3 h-3" />
          已完成分析
        </div>
      </div>
    </div>

    <div class="bg-white p-6 rounded-[24px] shadow-sm border border-gray-50 flex flex-col justify-between">
      <div class="flex items-center justify-between">
        <span class="text-sm font-bold text-gray-500">及格率</span>
        <span class="text-3xl font-black text-gray-900">{{ passRate || '0%' }}</span>
      </div>
      <div class="mt-6 h-2 w-full bg-gray-100 rounded-full overflow-hidden">
        <div class="h-full bg-indigo-500 rounded-full" :style="{ width: typeof passRate === 'string' ? passRate : (passRate + '%') }"></div>
      </div>
    </div>

    <div class="bg-white p-6 rounded-[24px] shadow-sm border border-gray-50 flex flex-col justify-between">
      <div class="flex items-center justify-between">
        <span class="text-sm font-bold text-gray-500">优秀率</span>
        <Award class="w-5 h-5 text-amber-400" />
      </div>
      <div class="mt-4 flex flex-col gap-2">
        <span class="text-4xl font-black text-gray-900">{{ excellentRate || '0%' }}</span>
        <span class="text-xs font-medium text-gray-400">低分预警 {{ lowScoreCount ?? 0 }} 人</span>
      </div>
    </div>

    <div class="bg-white p-6 rounded-[24px] shadow-sm border border-gray-50 flex flex-col justify-between">
      <div class="flex items-center justify-between">
        <span class="text-sm font-bold text-gray-500">最高分</span>
        <Users class="w-5 h-5 text-indigo-400" />
      </div>
      <div class="mt-4 flex flex-col gap-1">
        <span class="text-5xl font-black text-gray-900">{{ highestScore || '--' }}</span>
        <span class="text-xs font-medium text-gray-400">{{ highestScorers || '暂无数据' }} · 样本 {{ sampleSize || 0 }} 人</span>
      </div>
    </div>
  </div>
</template>
