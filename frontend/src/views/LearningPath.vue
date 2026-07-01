<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import type { Course } from '../types';

type TaskStatus = '未开始' | '进行中' | '待批改' | '已完成' | '逾期';

interface AdjustmentEntry {
  timestamp: string;
  trigger: string;
  reason: string;
  old_stages_summary: string[];
  new_stages_summary: string[];
  detected_new_weak_points: string[];
  resolved_weak_points: string[];
}

interface PathItem {
  id: number;
  course_id?: number;
  student_profile_id?: number;
  path_json?: {
    course_title?: string;
    goal?: string;
    stages?: Array<{ name?: string; target?: string; practice?: string; mastery?: string; recommend_reason?: string }>;
  };
  adjustment_log?: AdjustmentEntry[];
}

interface EventItem {
  id: number;
  event_type: string;
  title: string;
  description: string;
  status?: string;
  metadata?: Record<string, any>;
}

interface TaskRow {
  id: number;
  name: string;
  course: string;
  due: string;
  completed: number;
  total: number;
  status: TaskStatus;
}

const paths = ref<PathItem[]>([]);
const courses = ref<Course[]>([]);
const events = ref<EventItem[]>([]);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const classFilter = ref('计科大三 1 班');
const courseFilter = ref('全部课程');

const classOptions = ['计科大三 1 班', '计科大三 2 班', '计科大二 1 班', '计科大二 2 班'];
const fallbackStages = [
  { name: '诊断补弱', target: '定位 while 死循环、循环嵌套和 break / continue 的主要错因', status: 'done', recommend_reason: '最近测验中 while 死循环问题错误率较高' },
  { name: '核心概念学习', target: '复习 for、while、range、break、continue 的适用场景', status: 'done', recommend_reason: 'AI 求助集中在循环条件更新和循环嵌套' },
  { name: '案例实操', target: '完成猜数字、九九乘法表和列表统计代码案例', status: 'active', recommend_reason: '学生偏好代码案例和图解资源' },
  { name: '练习测评', target: '完成循环结构分层练习并标注错因', status: 'todo', recommend_reason: '形成性评价需要验证补弱效果' },
  { name: '项目拓展', target: '完成课程作业和基础项目中的循环结构任务', status: 'todo', recommend_reason: '对齐课程作业与基础项目目标' }
];

const fallbackTasks: TaskRow[] = [
  { id: 1, name: '李明 while 循环专项练习', course: 'Python 程序设计', due: '2026-06-12', completed: 18, total: 32, status: '进行中' },
  { id: 2, name: '循环嵌套章节测验', course: 'Python 程序设计', due: '2026-06-13', completed: 10, total: 32, status: '待批改' },
  { id: 3, name: '栈与队列课后作业', course: '数据结构与算法', due: '2026-06-01', completed: 38, total: 38, status: '已完成' },
  { id: 4, name: 'break / continue 变式题', course: 'Python 程序设计', due: '2026-06-14', completed: 8, total: 32, status: '未开始' },
  { id: 5, name: '循环结构补弱资源包反馈', course: 'Python 程序设计', due: '2026-06-15', completed: 6, total: 32, status: '逾期' }
];

const courseOptions = computed(() => ['全部课程', ...Array.from(new Set([...courses.value.map((item) => item.title), ...fallbackTasks.map((item) => item.course)]))]);

const selectedPath = computed(() => paths.value[0]);
const adjustmentLog = computed(() => selectedPath.value?.adjustment_log || []);
const stages = computed(() => {
  const realStages = selectedPath.value?.path_json?.stages;
  if (realStages?.length) {
    return realStages.map((stage, index) => ({
      name: stage.name || fallbackStages[index]?.name || `阶段 ${index + 1}`,
      target: stage.target || stage.practice || stage.mastery || fallbackStages[index]?.target || '继续完成当前阶段任务',
      recommend_reason: stage.recommend_reason || '',
      status: index < 2 ? 'done' : index === 2 ? 'active' : 'todo'
    }));
  }
  return fallbackStages;
});

const pathProgress = computed(() => Math.round((stages.value.filter((item) => item.status === 'done').length / Math.max(stages.value.length, 1)) * 100));

const taskRows = computed<TaskRow[]>(() => {
  const assigned = events.value.filter((item) => item.event_type === 'task_assigned').map((item, index) => {
    const fallback = fallbackTasks[index % fallbackTasks.length];
    return {
      id: item.id,
      name: item.metadata?.task?.task_type || item.title || fallback.name,
      course: item.metadata?.course_title || fallback.course,
      due: item.metadata?.task?.due_date || fallback.due,
      completed: fallback.completed,
      total: fallback.total,
      status: fallback.status
    } as TaskRow;
  });
  return assigned.length ? assigned.concat(fallbackTasks).slice(0, 8) : fallbackTasks;
});

const filteredTasks = computed(() => taskRows.value.filter((task) => courseFilter.value === '全部课程' || task.course === courseFilter.value));

const statCards = computed(() => [
  { label: '路径进度', value: pathProgress.value, unit: '%', hint: `${stages.value.length} 个节点`, icon: '路' },
  { label: '任务总数', value: taskRows.value.length, unit: '项', hint: '当前班级任务', icon: '任', tone: 'purple' as const },
  { label: '平均完成率', value: Math.round(taskRows.value.reduce((sum, item) => sum + (item.completed / item.total) * 100, 0) / taskRows.value.length), unit: '%', hint: '按任务人数估算', icon: '完', tone: 'green' as const },
  { label: '待批改', value: taskRows.value.filter((item) => item.status === '待批改').length, unit: '项', hint: '需教师处理', icon: '批', tone: 'orange' as const },
  { label: '逾期任务', value: taskRows.value.filter((item) => item.status === '逾期').length, unit: '项', hint: '需要提醒', icon: '逾', tone: 'red' as const }
]);

function statusTone(status: TaskStatus) {
  if (status === '已完成') return 'success';
  if (status === '进行中') return 'purple';
  if (status === '待批改') return 'warning';
  if (status === '逾期') return 'danger';
  return 'neutral';
}

async function load() {
  loading.value = true;
  error.value = '';
  try {
    const [pathData, eventData, courseData] = await Promise.all([
      api.get<PathItem[]>('/api/v1/learning-paths'),
      api.get<EventItem[]>('/api/v1/events?limit=30').catch(() => []),
      api.get<Course[]>('/api/v1/courses').catch(() => [])
    ]);
    paths.value = pathData;
    events.value = eventData;
    courses.value = courseData;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学习路径接口暂不可用，当前显示本地业务样例。';
    paths.value = [];
    events.value = [];
  } finally {
    loading.value = false;
  }
}

function demoAction(label: string) {
  operationMessage.value = `${label} 为演示操作，后续可接真实任务创建、批改和提醒流程。`;
}

async function adjustPath() {
  if (!selectedPath.value?.id) {
    operationMessage.value = '请先选择学生并生成学习路径。';
    return;
  }
  const profileId = selectedPath.value.student_profile_id;
  if (!profileId) {
    operationMessage.value = '当前路径无关联学生画像。';
    return;
  }
  operationMessage.value = '正在根据最新薄弱点调整路径...';
  try {
    const result = await api.post<PathItem>('/api/v1/learning-paths/adjust', {
      profile_id: profileId,
      trigger: 'manual',
    });
    // 更新本地数据
    const idx = paths.value.findIndex(p => p.id === result.id);
    if (idx >= 0) paths.value[idx] = result;
    else paths.value.unshift(result);
    operationMessage.value = '路径已根据最新薄弱点动态调整完成。';
  } catch (err) {
    operationMessage.value = `路径调整失败：${err instanceof Error ? err.message : '未知错误'}`;
  }
}

function formatTrigger(trigger: string) {
  if (trigger === 'quiz_submission') return '测验触发';
  if (trigger === 'manual') return '手动调整';
  return trigger;
}

onMounted(load);
</script>

<template>
  <section class="page path-page">
    <PageHeader title="教师视角路径管理" description="管理李明的 Python 循环结构专项补弱路径，跟踪任务完成率、路径更新原因和教师干预动作。">
      <template #actions>
        <button class="secondary" @click="adjustPath">动态调整路径</button>
        <button @click="demoAction('新建任务')">新建任务</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载学习路径...</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <DataCard title="筛选范围" subtitle="选择班级与课程后查看对应路径和任务">
      <div class="filter-grid">
        <select v-model="classFilter">
          <option v-for="item in classOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="courseFilter">
          <option v-for="item in courseOptions" :key="item">{{ item }}</option>
        </select>
        <button class="secondary" @click="demoAction('应用筛选')">应用筛选</button>
      </div>
    </DataCard>

    <div class="path-layout">
      <DataCard title="李明的 Python 循环结构专项补弱路径" :subtitle="`${classFilter} · ${courseFilter}`">
        <template #action>
          <StatusBadge :label="`${pathProgress}%`" tone="purple" />
        </template>
        <div class="path-progress">
          <ProgressBar :value="pathProgress" />
          <span>{{ stages.filter((item) => item.status === 'done').length }} / {{ stages.length }} 节点已完成</span>
        </div>
        <div class="path-timeline">
          <article v-for="(stage, index) in stages" :key="`${stage.name}-${index}`" :class="['path-stage', stage.status]">
            <span>{{ index + 1 }}</span>
            <div>
              <strong>{{ stage.name }}</strong>
              <p>{{ stage.target }}</p>
              <p v-if="stage.recommend_reason" class="stage-reason">{{ stage.recommend_reason }}</p>
            </div>
          </article>
        </div>
      </DataCard>

      <DataCard title="节点说明" subtitle="当前阶段与后续安排">
        <div class="list">
          <div class="item">
            <strong>当前节点</strong>
            <p>{{ stages.find((item) => item.status === 'active')?.name || '案例实操' }}</p>
          </div>
          <div class="item">
            <strong>推荐动作</strong>
            <p>为未达标学生追加专项练习，并在测验后同步更新路径。</p>
          </div>
          <div class="item">
            <strong>路径来源</strong>
            <p>综合学生画像、课程资源、测验评价和教师布置任务。</p>
          </div>
        </div>
      </DataCard>
    </div>

    <!-- 路径调整记录 -->
    <DataCard v-if="adjustmentLog.length" title="路径调整记录" :subtitle="`${adjustmentLog.length} 次调整`">
      <div class="adjustment-timeline">
        <article v-for="(entry, index) in adjustmentLog" :key="index" class="adjustment-entry">
          <div class="adjustment-header">
            <StatusBadge :label="formatTrigger(entry.trigger)" :tone="entry.trigger === 'quiz_submission' ? 'purple' : 'info'" />
            <span class="adjustment-time">{{ entry.timestamp?.slice(0, 19).replace('T', ' ') }}</span>
          </div>
          <p class="adjustment-reason">{{ entry.reason }}</p>
          <div class="adjustment-changes">
            <div v-if="entry.detected_new_weak_points?.length" class="change-group">
              <span class="change-label new">新增薄弱点</span>
              <span v-for="wp in entry.detected_new_weak_points" :key="wp" class="change-tag new-tag">{{ wp }}</span>
            </div>
            <div v-if="entry.resolved_weak_points?.length" class="change-group">
              <span class="change-label resolved">已掌握</span>
              <span v-for="wp in entry.resolved_weak_points" :key="wp" class="change-tag resolved-tag">{{ wp }}</span>
            </div>
          </div>
          <div class="adjustment-stages">
            <span class="stages-label">路径变化：</span>
            <span class="stages-old">{{ entry.old_stages_summary?.join(' → ') }}</span>
            <span class="stages-arrow">→</span>
            <span class="stages-new">{{ entry.new_stages_summary?.join(' → ') }}</span>
          </div>
        </article>
      </div>
    </DataCard>

    <DataCard title="任务布置列表" :subtitle="`${filteredTasks.length} 项任务`">
      <template #action>
        <button class="secondary" @click="demoAction('批量提醒')">批量提醒</button>
      </template>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>任务名称</th>
              <th>所属课程</th>
              <th>截止时间</th>
              <th>完成人数</th>
              <th>完成率</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in filteredTasks" :key="task.id">
              <td><strong>{{ task.name }}</strong></td>
              <td>{{ task.course }}</td>
              <td>{{ task.due }}</td>
              <td>{{ task.completed }} / {{ task.total }}</td>
              <td>
                <div class="task-progress">
                  <span>{{ Math.round((task.completed / task.total) * 100) }}%</span>
                  <ProgressBar :value="Math.round((task.completed / task.total) * 100)" :tone="task.status === '逾期' ? 'danger' : task.status === '待批改' ? 'warning' : 'primary'" />
                </div>
              </td>
              <td><StatusBadge :label="task.status" :tone="statusTone(task.status)" /></td>
              <td>
                <div class="row-actions">
                  <button class="ghost" @click="demoAction('查看任务')">查看</button>
                  <button class="secondary" @click="demoAction(task.status === '待批改' ? '批改任务' : '提醒学生')">{{ task.status === '待批改' ? '批改' : '提醒' }}</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-if="!filteredTasks.length" title="暂无任务" description="调整筛选或新建任务后会显示。" />
    </DataCard>
  </section>
</template>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: 220px 260px auto;
  gap: 12px;
  align-items: center;
}

.path-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.8fr);
  gap: 16px;
}

.path-progress {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

.path-progress span {
  color: var(--color-text-sub);
  font-size: 13px;
}

.path-timeline {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.path-stage {
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 12px;
  background: #fbfdff;
}

.path-stage > span {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  color: var(--text-secondary);
  background: var(--status-neutral-bg);
  font-weight: 800;
}

.path-stage.done > span {
  color: var(--status-success-text);
  background: var(--status-success-bg);
}

.path-stage.active {
  border-color: rgba(47, 107, 255, 0.5);
  background: var(--color-primary-light);
}

.path-stage.active > span {
  color: var(--text-light);
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.path-stage p {
  margin: 8px 0 0;
  font-size: 13px;
}

.stage-reason {
  margin-top: 6px !important;
  font-size: 12px !important;
  color: #64748b;
  background: #f1f5f9;
  padding: 6px 10px;
  border-radius: 8px;
  line-height: 1.5;
}

.adjustment-timeline {
  display: grid;
  gap: 12px;
}

.adjustment-entry {
  background: #fafbfc;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 14px 16px;
}

.adjustment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.adjustment-time {
  font-size: 12px;
  color: #94a3b8;
}

.adjustment-reason {
  margin: 0 0 10px;
  font-size: 13px;
  color: #334155;
  line-height: 1.5;
}

.adjustment-changes {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 10px;
}

.change-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.change-label {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
}

.change-label.new {
  color: #dc2626;
  background: #fef2f2;
}

.change-label.resolved {
  color: #16a34a;
  background: #f0fdf4;
}

.change-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
}

.new-tag {
  color: #b91c1c;
  background: #fee2e2;
}

.resolved-tag {
  color: #15803d;
  background: #dcfce7;
}

.adjustment-stages {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.stages-label {
  font-weight: 600;
}

.stages-old {
  color: #94a3b8;
  text-decoration: line-through;
}

.stages-arrow {
  color: #3b82f6;
  font-weight: 700;
}

.stages-new {
  color: #1e40af;
  font-weight: 500;
}

.table-wrap {
  overflow-x: auto;
}

.task-progress {
  display: grid;
  grid-template-columns: 42px minmax(110px, 1fr);
  gap: 8px;
  align-items: center;
  min-width: 160px;
}

.row-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 1180px) {
  .path-layout,
  .path-timeline {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
