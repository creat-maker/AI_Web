<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState.vue';
import { useRole } from '../composables/useRole';

const { currentRole } = useRole();
const paths = ref<any[]>([]);
const events = ref<any[]>([]);
const loading = ref(true);
const error = ref('');

const assignedTasks = computed(() => events.value.filter((item) => item.event_type === 'task_assigned'));
const pathUpdates = computed(() => events.value.filter((item) => ['resource_added_to_path', 'path_updated', 'quiz_completed'].includes(item.event_type)));

async function load() {
  loading.value = true;
  error.value = '';
  try {
    const [pathData, eventData] = await Promise.all([
      api.get<any[]>('/api/v1/learning-paths'),
      api.get<any[]>('/api/v1/events?limit=30')
    ]);
    paths.value = pathData;
    events.value = eventData;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学习路径数据加载失败。';
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="page">
    <article class="placeholder-hero">
      <span class="status-badge info">{{ currentRole === 'student' ? '学生端 · 学习路径' : currentRole === 'teacher' ? '教师端 · 学习路径与任务布置' : '管理员端 · 路径数据概览' }}</span>
      <h2>个性化学习路径</h2>
      <p>展示由画像、资源包、测验结果和教师任务共同影响的学习路径。新增资源包和补强任务会通过业务事件进入这里。</p>
    </article>

    <p v-if="loading" class="panel muted">正在加载学习路径...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>

    <template v-if="!loading && !error">
      <section v-if="pathUpdates.length" class="panel">
        <div class="panel-title">
          <h2>最近路径调整</h2>
          <span class="muted">来自资源包、测验和路径更新事件</span>
        </div>
        <div class="list">
          <article v-for="item in pathUpdates.slice(0, 5)" :key="item.id" class="item">
            <strong>{{ item.title }}</strong>
            <p>{{ item.description }}</p>
            <small class="muted">{{ item.related_student || '演示学生' }} · {{ item.related_course || '演示课程' }}</small>
          </article>
        </div>
      </section>

      <section v-if="assignedTasks.length" class="panel">
        <div class="panel-title">
          <h2>{{ currentRole === 'student' ? '我的补强任务' : '教师布置任务记录' }}</h2>
          <span class="muted">{{ assignedTasks.length }} 条</span>
        </div>
        <div class="list">
          <article v-for="item in assignedTasks.slice(0, 6)" :key="item.id" class="item">
            <strong>{{ item.metadata?.task?.task_type || '补强任务' }}：{{ item.metadata?.task?.weak_point || '薄弱知识点' }}</strong>
            <p>{{ item.description }}</p>
            <small class="muted">截止 {{ item.metadata?.task?.due_date || '待定' }} · 状态 {{ item.status }}</small>
          </article>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>路径节点</h2>
          <span class="muted">{{ paths.length }} 条路径</span>
        </div>
        <div class="list">
          <article v-for="path in paths" :key="path.id" class="item">
            <strong>{{ path.path_json.course_title || `课程 #${path.course_id}` }}：{{ path.path_json.goal || path.path_json.latest_adjustment_reason || '个性化学习路径' }}</strong>
            <div class="grid">
              <div v-for="stage in path.path_json.stages || []" :key="`${path.id}-${stage.name}-${stage.resource_package_id}`" class="item">
                <strong>{{ stage.name }}</strong>
                <p>目标：{{ stage.target || '继续完成当前阶段学习目标。' }}</p>
                <p v-if="stage.resource_package_id">资源包：{{ stage.resource_package_id }}</p>
                <p v-if="stage.resources?.length">资源：{{ stage.resources.join('、') }}</p>
                <p v-if="stage.practice">练习：{{ stage.practice }}</p>
                <p v-if="stage.mastery">掌握标准：{{ stage.mastery }}</p>
              </div>
            </div>
          </article>
          <EmptyState v-if="!paths.length" title="暂无学习路径" description="生成画像、资源包或运行演示数据后会显示。" />
        </div>
      </section>
    </template>
  </section>
</template>
