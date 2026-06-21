<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { api } from '../api/client';
import { learningTaskPaths } from '../api/mocks/competitionData';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { demoStudents as selectableStudents, useRole } from '../composables/useRole';

type LearningTaskPaths = typeof learningTaskPaths;

const data = ref<LearningTaskPaths>(learningTaskPaths);
const activeProfile = ref(learningTaskPaths.active_profile_type);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const replanLoading = ref(false);
const { demoUserId: selectedUserId, setDemoUserId: setSelectedUserId } = useRole();
const selectableUsers = selectableStudents;
const updateReasons = [
  '根据最近一次测验更新：while 循环条件更新仍需优先巩固',
  '最近测验中 while 死循环问题错误率较高',
  'AI 求助集中在循环条件更新和循环嵌套',
  '学生偏好代码案例和图解资源'
];
const emptyPath = {
  profile_type: '基础薄弱 + 代码实操偏好型',
  summary: '暂无路径数据，系统将展示循环结构补弱建议。',
  ai_recommendation: '建议先完成 while 循环条件更新专项练习。',
  tasks: [
    {
      title: 'while 循环专项练习',
      goal: '巩固 while 循环终止条件和变量更新。',
      status: '进行中',
      knowledge_points: ['while 循环'],
      resources: ['while 循环条件更新专项练习'],
      practice: '完成 3 道变量更新补全题。',
      completion_rule: '正确率达到 80%，并写出前三轮变量变化。',
      estimated_minutes: 20,
      ai_suggestion: '先画变量变化表，再运行代码验证。'
    }
  ]
};

const activePath = computed(() => data.value.paths.find((item) => item.profile_type === activeProfile.value) || data.value.paths[0] || emptyPath);
const allTasks = computed(() => {
  const tasks = data.value.paths.flatMap((path) => path.tasks || []);
  return tasks.length ? tasks : emptyPath.tasks;
});

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
    const params = new URLSearchParams({ user_id: selectedUserId.value });
    if (profileType) params.set('profile_type', profileType);
    const query = `?${params.toString()}`;
    data.value = await api.get<LearningTaskPaths>(`/api/v1/student/learning-tasks${query}`);
    activeProfile.value = profileType || data.value.active_profile_type;
  } catch (err) {
    error.value = '当前网络不稳定，已为你展示本地学习建议。';
    data.value = learningTaskPaths;
  } finally {
    loading.value = false;
  }
}

function switchProfile(profileType: string) {
  activeProfile.value = profileType;
  operationMessage.value = `已切换到「${profileType}」路径策略。`;
  loadTasks(profileType);
}

function taskReason(task: LearningTaskPaths['paths'][number]['tasks'][number]) {
  return (task as unknown as Record<string, string>).recommendation_reason || (task as unknown as Record<string, string>).ai_suggestion || '-';
}

function taskField(task: LearningTaskPaths['paths'][number]['tasks'][number], key: string, defaultValue = '-') {
  return (task as unknown as Record<string, string>)[key] || defaultValue;
}

function replanPath() {
  replanLoading.value = true;
  operationMessage.value = '正在根据最新测验错因和 AI 求助记录重新规划路径...';
  window.setTimeout(() => {
    replanLoading.value = false;
    operationMessage.value = '已根据最新测验错因和 AI 求助记录重新规划路径，当前展示最新动态更新结果。';
  }, 500);
}

onMounted(() => loadTasks());
watch(selectedUserId, () => loadTasks());
</script>

<template>
  <section class="page student-path-page">
    <PageHeader title="一人一堂学习路径" description="李明的 Python 循环结构专项补弱路径，按诊断补弱、核心概念学习、案例实操、练习测评、项目拓展推进。">
      <template #actions>
        <select :value="selectedUserId" @change="setSelectedUserId(($event.target as HTMLSelectElement).value)">
          <option v-for="user in selectableUsers" :key="user.id" :value="user.id">{{ user.label }}</option>
        </select>
        <RouterLink class="btn secondary" to="/student/knowledge-graph">知识图谱</RouterLink>
        <RouterLink class="btn" to="/student/smart-quiz">章节测验</RouterLink>
        <RouterLink class="btn secondary" to="/student/loop-game">循环结构闯关</RouterLink>
        <button type="button" class="secondary" :disabled="replanLoading" @click="replanPath">{{ replanLoading ? '规划中...' : '重新规划路径' }}</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载个性化学习路径...</p>
    <p v-if="error" class="panel warning-text">{{ error }}</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>
    <p class="panel muted">学习路径已根据最近一次循环结构测验更新。</p>

    <div class="stat-grid">
      <StatCard label="当前课程" value="Python 程序设计" hint="循环结构" icon="Py" />
      <StatCard label="学习特点" :value="activePath.profile_type" hint="可切换学习策略" icon="像" tone="purple" />
      <StatCard label="路径任务" :value="activePath.tasks.length || 0" unit="项" hint="按完成条件推进" icon="任" tone="green" />
      <StatCard label="预计时间" :value="activePath.tasks.reduce((sum, item) => sum + (item.estimated_minutes || 0), 0)" unit="分钟" hint="本阶段建议投入" icon="时" tone="orange" />
    </div>

    <DataCard title="个性化路径策略" subtitle="对标主流智慧教学平台的任务驱动学习体验">
      <div class="profile-tabs">
        <button
          v-for="path in data.paths"
          :key="path.profile_type"
          :class="{ secondary: activeProfile !== path.profile_type }"
          @click="switchProfile(path.profile_type)"
          :disabled="loading"
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

    <DataCard title="路径更新原因" subtitle="路径根据测验、AI 求助和资源偏好动态更新">
      <div class="overview-list reason-list">
        <article v-for="item in updateReasons" :key="item">
          <strong>{{ item }}</strong>
          <span>已写入李明的 Python 循环结构专项补弱路径</span>
          <StatusBadge label="已采纳" tone="success" />
        </article>
      </div>
    </DataCard>

    <DataCard title="互动练习资源" subtitle="面向李明的循环结构闯关练习，完成后可回到学习路径或查看报告">
      <div class="interactive-resource">
        <div>
          <strong>循环结构闯关练习</strong>
          <p>3 关覆盖 while 循环条件更新、break / continue 区分、循环嵌套变量变化。</p>
        </div>
        <RouterLink class="btn" to="/student/loop-game">开始闯关</RouterLink>
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
            <strong>前置知识点</strong>
            <p>{{ taskField(task, 'prerequisites', '变量与条件表达式') }}</p>
          </div>
          <div class="task-line">
            <strong>当前掌握度</strong>
            <p>{{ taskField(task, 'mastery', task.status === '进行中' ? '46%' : '待完成') }}</p>
          </div>
          <div class="task-line">
            <strong>练习任务</strong>
            <p>{{ task.practice }}</p>
          </div>
          <div class="task-line">
            <strong>完成条件</strong>
            <p>{{ task.completion_rule }}</p>
          </div>
          <div class="task-line recommend-reason">
            <strong>推荐理由</strong>
            <p>{{ taskReason(task) }}</p>
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

.interactive-resource {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.interactive-resource p {
  margin: 6px 0 0;
  color: var(--color-text-sub);
}

@media (max-width: 1100px) {
  .task-grid,
  .overview-list article {
    grid-template-columns: 1fr;
  }

  .interactive-resource {
    display: grid;
  }
}
</style>
