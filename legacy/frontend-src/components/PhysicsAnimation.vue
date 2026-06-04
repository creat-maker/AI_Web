<script setup lang="ts">
defineProps<{
  animationHtml: string;
}>();
</script>

<template>
  <div class="physics-animation-wrapper">
    <!-- Header badge -->
    <div class="flex items-center gap-2 mb-3 px-1">
      <div class="w-7 h-7 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600 text-sm">
        ⚛️
      </div>
      <span class="text-sm font-bold text-slate-700">交互式物理动画引擎</span>
      <span class="ml-auto text-[10px] font-black uppercase tracking-widest text-indigo-400 bg-indigo-50 px-2.5 py-1 rounded-full">
        LIVE DEMO
      </span>
    </div>

    <!-- Animation iframe container -->
    <div class="physics-frame-shell">
      <iframe
        :srcdoc="animationHtml"
        sandbox="allow-scripts"
        scrolling="auto"
        class="physics-iframe"
        title="洛伦兹力物理动画"
      />
    </div>

    <!-- Caption -->
    <p class="mt-3 px-1 text-[11px] font-medium text-slate-400 text-center">
      拖动滑块实时调节磁场强度 B 和粒子初速度 v，观察轨道半径的动态变化
    </p>
  </div>
</template>

<style scoped>
.physics-animation-wrapper {
  width: 100%;
  margin-bottom: 2rem;
}

.physics-frame-shell {
  width: 100%;
  border-radius: 24px;
  overflow: hidden;
  background: linear-gradient(160deg, #f0f4ff 0%, #fafbff 100%);
  box-shadow:
    0 0 0 1px rgba(99, 102, 241, 0.08),
    0 4px 6px -1px rgba(15, 23, 42, 0.04),
    0 20px 48px -8px rgba(99, 102, 241, 0.14);
  height: 560px;
}

.physics-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
  border-radius: inherit;
}
</style>
