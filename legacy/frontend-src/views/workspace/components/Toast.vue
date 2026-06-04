<script setup lang="ts">
defineProps<{
  message: string;
}>();
</script>

<template>
  <div class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[60]">
    <div class="bg-gray-900 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3 border border-white/10 backdrop-blur-md">
      <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
      <span class="text-sm font-bold">{{ message }}</span>
    </div>
  </div>
</template>
