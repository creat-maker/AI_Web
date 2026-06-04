<script setup lang="ts">
import { 
  Home, 
  BookOpen, 
  Layout, 
  UserCircle, 
  BarChart3, 
  Plus, 
  Settings, 
  HelpCircle,
  Sparkles,
  History
} from 'lucide-vue-next';

const props = defineProps<{
  currentView: string;
  isSidebarCollapsed: boolean;
}>();

const emit = defineEmits<{
  (e: 'switch-view', viewId: string): void;
  (e: 'toggle-sidebar'): void;
  (e: 'new-class'): void;
  (e: 'action', action: string): void;
}>();

const menuItems = [
  { id: 'home', name: '首页', icon: Home },
  { id: 'knowledge', name: '知识库', icon: BookOpen },
  { id: 'history', name: '历史档案', icon: History },
  { id: 'workspace', name: '工作台', icon: Layout },
  { id: 'digital-human', name: '数字人助教', icon: UserCircle },
  { id: 'analysis', name: '学情总结', icon: BarChart3 },
];
</script>

<template>
  <aside 
    class="flex-shrink-0 h-full bg-white transition-all duration-300 ease-in-out flex flex-col"
    :class="[isSidebarCollapsed ? 'w-20' : 'w-64']"
  >
    <!-- Logo -->
    <div class="p-6 flex items-center gap-3">
      <div class="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200 cursor-pointer" @click="emit('toggle-sidebar')">
        <Sparkles class="text-white w-6 h-6" />
      </div>
      <div v-if="!isSidebarCollapsed" class="flex flex-col">
        <span class="font-bold text-xl tracking-tight text-indigo-900">织课 AI</span>
        <span class="text-[10px] text-gray-400 uppercase tracking-widest font-semibold">AI Teaching Agent</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 py-4 space-y-1">
      <button 
        v-for="item in menuItems" 
        :key="item.id"
        @click="emit('switch-view', item.id)"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative"
        :class="[currentView === item.id ? 'bg-indigo-50 text-indigo-700' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900']"
      >
        <component :is="item.icon" class="w-5 h-5" :class="[currentView === item.id ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600']" />
        <span v-if="!isSidebarCollapsed" class="font-medium">{{ item.name }}</span>
        <div v-if="currentView === item.id" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-indigo-600 rounded-r-full"></div>
      </button>
    </nav>

    <!-- Bottom Actions -->
    <div class="p-4 space-y-4">
      <button 
        @click="emit('new-class')"
        class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-xl font-semibold shadow-lg shadow-indigo-100 hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
      >
        <Plus class="w-5 h-5" />
        <span v-if="!isSidebarCollapsed">新建课堂</span>
      </button>
      
      <div class="pt-4 space-y-1">
        <button @click="emit('action', '设置功能开发中')" class="w-full flex items-center gap-3 px-4 py-2 text-gray-500 hover:text-gray-900 transition-colors">
          <Settings class="w-5 h-5" />
          <span v-if="!isSidebarCollapsed" class="text-sm font-medium">设置</span>
        </button>
        <button @click="emit('action', '帮助中心功能开发中')" class="w-full flex items-center gap-3 px-4 py-2 text-gray-500 hover:text-gray-900 transition-colors">
          <HelpCircle class="w-5 h-5" />
          <span v-if="!isSidebarCollapsed" class="text-sm font-medium">帮助</span>
        </button>
      </div>

      <!-- User Profile -->
      <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-2xl mt-4">
        <div class="w-10 h-10 rounded-full overflow-hidden border-2 border-white shadow-sm">
          <img src="https://picsum.photos/seed/user/100/100" alt="User" class="w-full h-full object-cover" />
        </div>
        <div v-if="!isSidebarCollapsed" class="flex flex-col min-w-0">
          <span class="text-sm font-bold truncate">王老师</span>
        </div>
      </div>
    </div>
  </aside>
</template>
