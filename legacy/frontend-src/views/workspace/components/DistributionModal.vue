<script setup lang="ts">
import { Loader2, X, Check } from 'lucide-vue-next';

const props = defineProps<{
  selectedChannels: string[];
  selectedClasses: string[];
  distributionChannels: { id: string; title: string; description: string }[];
  distributionClassOptions: string[];
  isDistributionReady: boolean;
  isDistributionMockLoading: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'toggle-channel', channelId: string): void;
  (e: 'toggle-class', className: string): void;
  (e: 'confirm'): void;
}>();
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-6">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="emit('close')"></div>
    <div class="relative w-full max-w-[560px] rounded-[36px] border border-white/80 bg-white/88 shadow-[0_30px_90px_rgba(99,102,241,0.12)] backdrop-blur-xl overflow-hidden flex flex-col">
      <div class="px-8 py-6 flex items-center justify-between border-b border-gray-50">
        <h3 class="text-xl font-black text-gray-900">分发教学任务</h3>
        <button @click="emit('close')" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all"><X class="w-5 h-5" /></button>
      </div>
      <div class="p-8 space-y-8">
        <div class="space-y-4">
          <div class="flex items-center justify-between gap-4"><h4 class="text-sm font-bold text-gray-900">选择分发渠道</h4><span class="rounded-full bg-indigo-50 px-3 py-1 text-[11px] font-black text-indigo-700">已选 {{ selectedChannels.length }} 项</span></div>
          <div class="grid grid-cols-1 gap-3">
            <button v-for="channel in distributionChannels" :key="channel.id" @click="emit('toggle-channel', channel.id)"
              class="group relative overflow-hidden rounded-[24px] border-2 p-4 text-left transition-all"
              :class="selectedChannels.includes(channel.id) ? 'border-indigo-500 bg-[linear-gradient(135deg,_rgba(238,242,255,0.95),_rgba(245,243,255,0.9))] shadow-[0_16px_40px_rgba(79,70,229,0.14)]' : 'border-gray-100 bg-white hover:border-indigo-200 hover:shadow-sm'">
              <div class="relative flex items-start gap-4">
                <div class="flex h-12 w-12 items-center justify-center rounded-2xl text-gray-500" :class="selectedChannels.includes(channel.id) ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'bg-gray-100'">📡</div>
                <div class="flex-1 min-w-0"><p class="text-sm font-bold text-gray-900">{{ channel.title }}</p><p class="mt-1 text-xs leading-5 text-gray-500">{{ channel.description }}</p></div>
                <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full border-2" :class="selectedChannels.includes(channel.id) ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-gray-300 text-transparent'"><Check class="w-3.5 h-3.5" /></div>
              </div>
            </button>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between gap-4"><h4 class="text-sm font-bold text-gray-900">选择目标班级</h4></div>
          <div class="flex flex-wrap gap-3">
            <button v-for="cls in distributionClassOptions" :key="cls" @click="emit('toggle-class', cls)"
              class="px-4 py-2.5 rounded-2xl text-sm font-bold transition-all border-2"
              :class="selectedClasses.includes(cls) ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-gray-100 bg-white text-gray-600 hover:border-indigo-200'">{{ cls }}</button>
          </div>
        </div>
      </div>
      <div class="px-8 py-6 bg-gray-50/50 flex gap-4">
        <button @click="emit('close')" class="liquid-glass-secondary-button flex-1 rounded-full px-6 py-4 text-sm font-bold text-gray-600">取消</button>
        <button @click="emit('confirm')"
          class="liquid-glass-primary-button flex-1 rounded-full px-6 py-4 text-sm font-bold transition-all flex items-center justify-center gap-2"
          :class="isDistributionReady && !isDistributionMockLoading ? 'text-indigo-700 hover:-translate-y-0.5' : 'text-indigo-400 cursor-not-allowed opacity-70'"
          :disabled="!isDistributionReady || isDistributionMockLoading">
          <Loader2 v-if="isDistributionMockLoading" class="w-4 h-4 animate-spin" />
          {{ isDistributionMockLoading ? '分发中...' : '确认分发' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.liquid-glass-primary-button,
.liquid-glass-secondary-button {
  position: relative; overflow: hidden;
  border: 1px solid rgba(255,255,255,0.82);
  background: linear-gradient(180deg, rgba(255,255,255,0.84), rgba(255,255,255,0.58));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 40px rgba(148,163,184,0.16);
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
}
.liquid-glass-primary-button { background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(238,242,255,0.9)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.96), 0 22px 48px rgba(129,140,248,0.2); }
.liquid-glass-secondary-button { background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.74)); }
</style>
