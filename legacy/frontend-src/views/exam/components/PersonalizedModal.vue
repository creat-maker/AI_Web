<script setup lang="ts">
import { Loader2, X } from 'lucide-vue-next';
import type { SmartGroup } from '@/api/mocks/data';

defineProps<{
  smartGroups: SmartGroup[];
  isDistributing: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm'): void;
}>();
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-6">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="!isDistributing && emit('close')"></div>

    <div class="relative bg-white w-full max-w-[600px] rounded-[32px] shadow-2xl overflow-hidden flex flex-col">
      <div class="px-8 py-6 flex items-center justify-between border-b border-gray-50">
        <h3 class="text-xl font-black text-gray-900">AI 智能错题组卷与分发</h3>
        <button @click="emit('close')" :disabled="isDistributing" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all disabled:opacity-50">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="p-8 space-y-6 bg-gray-50/30">
        <div
          v-for="(group, idx) in smartGroups"
          :key="idx"
          class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm space-y-4"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-sm font-bold text-gray-900">
              {{ group.title }}
              <span class="text-gray-400 font-medium">({{ group.count }}人)</span>
            </h4>
            <span class="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg">{{ group.tags }}</span>
          </div>
          <div v-if="group.focus || group.action" class="rounded-xl bg-gray-50 p-3 text-xs leading-relaxed text-gray-600 space-y-1">
            <p v-if="group.focus"><span class="font-bold text-gray-700">诊断：</span>{{ group.focus }}</p>
            <p v-if="group.action"><span class="font-bold text-gray-700">任务：</span>{{ group.action }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(stu, si) in group.students"
              :key="si"
              class="px-3 py-1 bg-gray-50 text-gray-600 text-xs font-medium rounded-lg border border-gray-100"
            >{{ stu }}</span>
          </div>
        </div>
      </div>

      <div class="px-8 py-6 bg-white border-t border-gray-50 flex">
        <button
          @click="emit('confirm')"
          :disabled="isDistributing"
          class="w-full py-4 rounded-2xl text-sm font-bold shadow-xl shadow-indigo-100 transition-all flex items-center justify-center gap-2"
          :class="isDistributing ? 'bg-indigo-400 text-white cursor-not-allowed' : 'bg-indigo-600 text-white hover:opacity-90'"
        >
          <Loader2 v-if="isDistributing" class="w-5 h-5 animate-spin" />
          {{ isDistributing ? '正在推送...' : '一键分发至学生终端' }}
        </button>
      </div>
    </div>
  </div>
</template>
