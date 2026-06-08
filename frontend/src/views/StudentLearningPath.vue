<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import { learningTaskPaths } from '../api/mocks/competitionData';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

type LearningTaskPaths = typeof learningTaskPaths;

const data = ref<LearningTaskPaths>(learningTaskPaths);
const activeProfile = ref(learningTaskPaths.active_profile_type);
const loading = ref(true);
const error = ref('');

const activePath = computed(() => data.value.paths.find((item) => item.profile_type === activeProfile.value) || data.value.paths[0]);
const allTasks = computed(() => data.value.paths.flatMap((path) => path.tasks));

function taskTone(status: string) {
  if (status === '进行中') return 'purple';
  if (status === '推荐') return 'info';
  if (status === '已完成') return 'success';
  return 'neutral';
}

async function loadTasks(profileType?: string) {
  loading.value = true;
  error.value = '';
  try {
    const query = profileType ? `?profile_type=${encodeURIComponent(profileType)}` : '';
    data.value = await api.get<LearningTaskPaths>(`/api/v1/student/learning-tasks${query}`);
    activeProfile.value = profileType || data.value.active_profile_type;
  } catch (err) {
    error.value = err instanceof Error ? `后端学习任务接口暂不可用，已使用本地演示数据：${err.message}` : '后端学习任务接口暂不可用，已使用本地演示数据。';
    data.value = learningTaskPaths;
  } finally {
    loading.value = false;
  }
}

function switchProfile(profileType: string) {
  activeProfile.value = profileType;
  loadTasks(profileType);
}

onMounted(() => loadTasks());
</script>

<template>
  <section class="page student-path-page">
    <PageHeader title="任务式学习路径" description="根据学生画像生成不同学习路径，把学习目标、知识点、资源、练习、完成条件和 AI 建议组织成可执行任务。">
      <template #actions>
        <RouterLink class="btn secondary" to="/student/knowledge-graph">知识图谱</RouterLink>
        <RouterLink class="btn" to="/student/smart-quiz">章节测验</RouterLink>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载个性化学习路径...</p>
    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="当前课程" value="Python" hint="程序设计" icon="Py" />
      <StatCard label="画像类型" :value="activePath.profile_type" hint="可切换演示策略" icon="像" tone="purple" />
      <StatCard label="路径任务" :value="activePath.tasks.length" unit="项" hint="按完成条件推进" icon="任" tone="green" />
      <StatCard label="预计时间" :value="activePath.tasks.reduce((sum, item) => sum + item.estimated_minutes, 0)" unit="分钟" hint="本阶段建议投入" icon="时" tone="orange" />
    </div>

    <DataCard title="个性化路径策略" subtitle="对标主流智慧教学平台的任务驱动学习体验">
      <div class="profile-tabs">
        <button
          v-for="path in data.paths"
          :key="path.profile_type"
          :class="{ secondary: activeProfile !== path.profile_type }"
          @click="switchProfile(path.profile_type)"
        >
          {{ path.profile_type }}
        </button>
      </div>
      <div class="strategy-card">
        <div>
          <strong>{{ activePath.summary }}</strong>
          <p>{{ activePath.ai_recommendation }}</p>
        </div>
        <StatusBadge label="AI 推荐路径" tone="success" />
      </div>
    </DataCard>

    <div class="task-grid">
      <DataCard v-for="task in activePath.tasks" :key="task.title" :title="task.title" :subtitle="task.goal">
        <template #action>
          <StatusBadge :label="task.status" :tone="taskTone(task.status)" />
        </template>
        <div class="task-card-body">
          <div class="chip-row">
            <span v-for="point in task.knowledge_points" :key="point">{{ point }}</span>
          </div>
          <div class="task-line">
            <strong>推荐资源</strong>
            <p>{{ task.resources.join('、') }}</p>
          </div>
          <div class="task-line">
            <strong>练习任务</strong>
            <p>{{ task.practice }}</p>
          </div>
          <div class="task-line">
            <strong>完成条件</strong>
            <p>{{ task.completion_rule }}</p>
          </div>
          <div class="task-bottom">
            <span>预计 {{ task.estimated_minutes }} 分钟</span>
            <ProgressBar :value="task.status === '进行中' ? 56 : task.status === '推荐' ? 20 : 0" tone="primary" />
          </div>
          <div class="ai-advice">{{ task.ai_suggestion }}</div>
        </div>
      </DataCard>
    </div>

    <DataCard title="路径总览" subtitle="所有画像路径共用同一知识图谱和测评诊断结果，后续可替换为真实推荐引擎。">
      <div class="overview-list">
        <article v-for="task in allTasks" :key="`${task.title}-${task.status}`">
          <strong>{{ task.title }}</strong>
          <span>{{ task.knowledge_points.join(' / ') }}</span>
          <StatusBadge :label="task.status" :tone="taskTone(task.status)" />
        </article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.profile-tabs,
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.strategy-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-top: 14px;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 14px;
  background: var(--color-primary-light);
}

.strategy-card p {
  margin: 8px 0 0;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.task-card-body {
  display: grid;
  gap: 12px;
}

.chip-row span {
  border-radius: 999px;
  padding: 6px 10px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-size: 12px;
  font-weight: 700;
}

.task-line strong,
.task-bottom span {
  color: var(--color-text-sub);
  font-size: 13px;
}

.task-line p {
  margin: 6px 0 0;
}

.task-bottom {
  display: grid;
  gap: 8px;
}

.ai-advice {
  border-left: 4px solid var(--color-primary);
  border-radius: 10px;
  padding: 10px 12px;
  background: #f8fafc;
  color: var(--color-text-main);
}

.overview-list {
  display: grid;
  gap: 10px;
}

.overview-list article {
  display: grid;
  grid-template-columns: minmax(160px, 0.8fr) minmax(220px, 1fr) auto;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}

.overview-list span {
  color: var(--color-text-sub);
}

@media (max-width: 1100px) {
  .task-grid,
  .overview-list article {
    grid-template-columns: 1fr;
  }
}
</style>
