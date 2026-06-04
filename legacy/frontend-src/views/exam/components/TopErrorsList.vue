<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next';
import type { TopErrorItem } from '@/api/mocks/data';

const props = defineProps<{
  topErrors: TopErrorItem[];
}>();

const emit = defineEmits<{
  (e: 'generate-personalized'): void;
}>();
</script>

<template>
  <div class="bg-white p-8 rounded-[32px] shadow-sm border border-gray-50 flex flex-col">
    <h3 class="text-lg font-bold text-gray-900 mb-6">高频错题 Top {{ topErrors.length || 0 }}</h3>
    <div class="flex-1 flex flex-col gap-4">
      <template v-if="topErrors.length > 0">
        <div
          v-for="(err, idx) in topErrors"
          :key="idx"
          class="border p-4 rounded-xl flex justify-between items-start mb-4"
          :class="[
            idx === 0 ? 'bg-rose-50 border-rose-100' : idx === 1 ? 'bg-orange-50 border-orange-100' : 'bg-amber-50 border-amber-100'
          ]"
        >
          <div class="min-w-0">
            <h4 class="font-bold text-gray-800 text-sm mb-1">{{ err.question }}</h4>
            <p class="text-xs text-gray-500">知识漏洞：{{ err.topic }}</p>
            <p v-if="err.suggestion" class="text-xs text-gray-500 mt-2 leading-relaxed">{{ err.suggestion }}</p>
            <div v-if="err.affectedStudents?.length" class="flex flex-wrap gap-1.5 mt-3">
              <span
                v-for="student in err.affectedStudents.slice(0, 6)"
                :key="student"
                class="px-2 py-0.5 rounded-md bg-white/70 border border-white text-[10px] font-bold text-gray-500"
              >
                {{ student }}
              </span>
            </div>
          </div>
          <div class="flex flex-col items-end ml-4 flex-shrink-0">
            <span
              class="text-xs font-bold px-2 py-0.5 rounded"
              :class="[idx === 0 ? 'text-rose-500 bg-rose-100' : idx === 1 ? 'text-orange-500 bg-orange-100' : 'text-amber-600 bg-amber-100']"
            >预计错误率</span>
            <span
              class="font-extrabold text-lg"
              :class="[idx === 0 ? 'text-rose-600' : idx === 1 ? 'text-orange-600' : 'text-amber-600']"
            >{{ err.errorRate }}</span>
          </div>
        </div>
      </template>
      <div v-else class="text-center text-gray-400 text-sm py-6">上传试卷后将显示高频错题</div>
    </div>

    <button
      @click="emit('generate-personalized')"
      class="w-full mt-4 py-3 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-100 transition-colors flex items-center justify-center font-medium"
    >
      <Sparkles class="w-4 h-4 mr-2" />
      基于错题生成个性化练习
    </button>
  </div>
</template>
