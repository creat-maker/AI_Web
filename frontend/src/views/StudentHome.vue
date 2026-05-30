<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';

interface DashboardSummary {
  metrics?: {
    course_count?: number;
    report_count?: number;
    quiz_submission_count?: number;
    knowledge_chunk_count?: number;
  };
  recent_questions?: Array<{ question?: string; status?: string; created_at?: string }>;
  student_risk_stats?: { weak_points?: Array<{ name: string; count: number }> };
}

interface ReportItem {
  id: number;
  title: string;
  status?: string;
  generated_at?: string;
  quality_score?: number;
}

interface Course {
  id: number;
  title: string;
  subject?: string;
}

const loading = ref(true);
const error = ref('');
const summary = ref<DashboardSummary | null>(null);
const reports = ref<ReportItem[]>([]);
const courses = ref<Course[]>([]);
const events = ref<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>([]);

const currentCourse = computed(() => courses.value[0]);
const latestReport = computed(() => reports.value[0]);

const recommendedResources = computed(() => [
  '基于课程资料的 10 分钟概念复盘',
  '薄弱知识点专项练习 3 题',
  '错题归因与追问式答疑清单'
]);
const assignedTasks = computed(() => events.value.filter((item) => item.event_type === 'task_assigned'));

async function loadPage() {
  loading.value = true;
  error.value = '';
  try {
    const [summaryResult, reportsResult, coursesResult, eventsResult] = await Promise.allSettled([
      api.get<DashboardSummary>('/api/dashboard/summary'),
      api.get<ReportItem[]>('/api/v1/reports'),
      api.get<Course[]>('/api/v1/courses'),
      api.get<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>('/api/v1/events?limit=20')
    ]);
    if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value;
    if (reportsResult.status === 'fulfilled') reports.value = reportsResult.value;
    if (coursesResult.status === 'fulfilled') courses.value = coursesResult.value;
    if (eventsResult.status === 'fulfilled') events.value = eventsResult.value;
    if ([summaryResult, reportsResult, coursesResult].every((item) => item.status === 'rejected')) {
      throw new Error('学生端首页数据加载失败，请确认后端已启动。');
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学生端首页加载失败。';
  } finally {
    loading.value = false;
  }
}

onMounted(loadPage);
</script>

<template>
  <section class="page role-home">
    <p class="demo-banner">演示数据：学生端首页优先复用 Dashboard、Reports 和 Courses 接口，缺失项使用 demo/fallback 文案补齐。</p>
    <p v-if="loading" class="panel muted">正在加载学生端学习总览...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>

    <template v-if="!loading && !error">
      <div class="role-grid">
        <StatCard label="今日学习目标" value="3" unit="项" hint="完成路径任务、一次答疑和一次测验复盘" />
        <StatCard label="当前课程进度" value="68" unit="%" hint="根据演示测评与学习路径估计" tone="green" />
        <StatCard label="测验记录" :value="summary?.metrics?.quiz_submission_count || 0" unit="次" hint="来自测评提交记录" tone="orange" />
        <StatCard label="学习报告" :value="summary?.metrics?.report_count || reports.length || 0" unit="份" hint="可查看证据链和建议" tone="purple" />
      </div>

      <div class="role-layout">
        <article class="panel role-panel">
          <div class="panel-title">
            <h2>个性化画像状态</h2>
            <span class="status-badge success">已生成画像</span>
          </div>
          <p>当前画像已覆盖学习目标、基础水平、薄弱知识点和互动偏好。后续可接真实对话建画像流程。</p>
          <RouterLink class="text-link" to="/profiles">进入对话建画像</RouterLink>
        </article>

        <article class="panel role-panel">
          <div class="panel-title">
            <h2>当前课程进度</h2>
            <span class="muted">{{ currentCourse?.subject || '课程体系' }}</span>
          </div>
          <strong>{{ currentCourse?.title || 'Python 程序设计演示课程' }}</strong>
          <div class="progress-track"><span style="width: 68%"></span></div>
          <p class="muted">课程资料、答疑记录和测评结果会进入学习闭环。</p>
        </article>
      </div>

      <div class="role-layout">
        <article class="panel">
          <h2>推荐资源</h2>
          <div class="list">
            <div v-for="item in recommendedResources" :key="item" class="item compact">{{ item }}</div>
          </div>
          <RouterLink class="text-link" to="/resource-generation">生成个性化资源</RouterLink>
        </article>

        <article class="panel">
          <h2>当前学习路径</h2>
          <div class="timeline-list">
            <p><strong>1. 复盘核心概念</strong><span>今日完成</span></p>
            <p><strong>2. 完成专项练习</strong><span>待完成</span></p>
            <p><strong>3. 查看学习报告</strong><span>建议今晚</span></p>
          </div>
          <RouterLink class="text-link" to="/learning-path">查看完整路径</RouterLink>
        </article>
      </div>

      <div class="role-layout">
        <article class="panel">
          <h2>今日任务</h2>
          <div class="list">
            <div v-for="task in assignedTasks.slice(0, 3)" :key="task.id" class="item compact">
              {{ task.metadata?.task?.task_type || task.title }}：{{ task.metadata?.task?.weak_point || task.description }}
              <span>{{ task.metadata?.task?.due_date || '待完成' }}</span>
            </div>
            <div class="item compact">完成 1 次启发式智能答疑</div>
            <div class="item compact">复习薄弱知识点：{{ summary?.student_risk_stats?.weak_points?.[0]?.name || '核心概念' }}</div>
            <div class="item compact">查看最新学习报告并确认学习建议</div>
          </div>
        </article>

        <article class="panel">
          <h2>快捷入口</h2>
          <div class="quick-grid">
            <RouterLink to="/tutor-chat">智能答疑</RouterLink>
            <RouterLink to="/evaluation">测验成绩</RouterLink>
            <RouterLink to="/reports">学习报告</RouterLink>
          </div>
        </article>
      </div>

      <article class="panel">
        <div class="panel-title">
          <h2>最近学习报告</h2>
          <span class="muted">成就 / 积分：1280 分</span>
        </div>
        <div v-if="latestReport" class="item">
          <strong>{{ latestReport.title }}</strong>
          <p class="muted">质量评分 {{ latestReport.quality_score ?? '-' }}，状态 {{ latestReport.status || '已生成' }}</p>
          <RouterLink class="text-link" to="/reports">查看报告详情</RouterLink>
        </div>
        <EmptyState v-else title="暂无学习报告" description="运行演示数据或生成报告后会在这里展示。" />
      </article>
    </template>
  </section>
</template>
