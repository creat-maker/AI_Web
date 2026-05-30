<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';

interface DashboardSummary {
  metrics?: {
    course_count?: number;
    qa_count?: number;
    report_count?: number;
  };
  student_risk_stats?: {
    risk_student_count?: number;
    weak_points?: Array<{ name: string; count: number }>;
  };
  tutor_chat_stats?: {
    today_questions?: number;
  };
  warning_items?: Array<{ module: string; level: string; message: string; count: number }>;
}

interface AnalysisData {
  summary?: {
    student_count?: number;
    average_score?: number;
  };
  knowledge_tracking?: {
    class_mastery_distribution?: Array<{ name: string; value: number }>;
    teacher_intervention_suggestions?: Array<{ title: string; content: string }>;
  };
}

const loading = ref(true);
const error = ref('');
const summary = ref<DashboardSummary | null>(null);
const analysis = ref<AnalysisData | null>(null);

const weakPoints = computed(() => summary.value?.student_risk_stats?.weak_points || []);
const suggestions = computed(() => analysis.value?.knowledge_tracking?.teacher_intervention_suggestions || []);

async function loadPage() {
  loading.value = true;
  error.value = '';
  try {
    const [summaryResult, analysisResult] = await Promise.allSettled([
      api.get<DashboardSummary>('/api/dashboard/summary'),
      api.get<AnalysisData>('/api/v1/quizzes/analysis')
    ]);
    if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value;
    if (analysisResult.status === 'fulfilled') analysis.value = analysisResult.value;
    if (summaryResult.status === 'rejected' && analysisResult.status === 'rejected') {
      throw new Error('教师端首页数据加载失败，请确认后端已启动。');
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '教师端首页加载失败。';
  } finally {
    loading.value = false;
  }
}

onMounted(loadPage);
</script>

<template>
  <section class="page role-home">
    <p class="demo-banner">演示数据：教师端首页复用 Dashboard 和 TeacherAnalysis 统计，待批改/待回复为 demo/fallback 展示指标。</p>
    <p v-if="loading" class="panel muted">正在加载教师端班级概览...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>

    <template v-if="!loading && !error">
      <div class="role-grid">
        <StatCard label="我的课程数" :value="summary?.metrics?.course_count || 0" unit="门" hint="来自课程表" />
        <StatCard label="班级学生数" :value="analysis?.summary?.student_count || 0" unit="人" hint="来自学生画像/测评数据" tone="green" />
        <StatCard label="平均学习进度" value="72" unit="%" hint="demo/fallback 进度估计" tone="orange" />
        <StatCard label="风险学生数量" :value="summary?.student_risk_stats?.risk_student_count || 0" unit="人" hint="结合测评和问答估计" tone="purple" />
      </div>

      <div class="role-layout">
        <article class="panel">
          <div class="panel-title">
            <h2>待处理事项</h2>
            <span class="status-badge warning">演示模式</span>
          </div>
          <div class="todo-grid">
            <div class="item compact"><strong>待批改作业</strong><span>6 份</span></div>
            <div class="item compact"><strong>待回复答疑</strong><span>{{ summary?.tutor_chat_stats?.today_questions || 2 }} 条</span></div>
            <div class="item compact"><strong>待生成报告</strong><span>{{ summary?.metrics?.report_count || 0 }} 份可复核</span></div>
          </div>
        </article>

        <article class="panel">
          <h2>快捷操作</h2>
          <div class="quick-grid">
            <RouterLink to="/courses">新建课程</RouterLink>
            <RouterLink to="/learning-path">布置任务</RouterLink>
            <RouterLink to="/reports">生成报告</RouterLink>
          </div>
        </article>
      </div>

      <div class="role-layout">
        <article class="panel">
          <h2>班级学习趋势</h2>
          <div class="trend-bars">
            <span style="height: 42%"></span>
            <span style="height: 58%"></span>
            <span style="height: 64%"></span>
            <span style="height: 72%"></span>
            <span style="height: 78%"></span>
          </div>
          <p class="muted">趋势为演示数据，用于说明学习行为、测评和报告形成闭环。</p>
        </article>

        <article class="panel">
          <h2>薄弱知识点 TOP</h2>
          <div v-if="weakPoints.length" class="list">
            <div v-for="item in weakPoints.slice(0, 5)" :key="item.name" class="item compact">
              <strong>{{ item.name }}</strong>
              <span class="muted">影响 {{ item.count }} 次记录</span>
            </div>
          </div>
          <EmptyState v-else title="暂无薄弱点" description="提交测评或运行演示数据后会显示。" />
        </article>
      </div>

      <article class="panel">
        <div class="panel-title">
          <h2>最近教学提醒</h2>
          <span class="muted">干预建议</span>
        </div>
        <div v-if="suggestions.length" class="list">
          <div v-for="item in suggestions" :key="item.title" class="item">
            <strong>{{ item.title }}</strong>
            <p>{{ item.content }}</p>
          </div>
        </div>
        <EmptyState v-else title="暂无教学提醒" description="教师分析接口返回知识追踪建议后会显示。" />
      </article>
    </template>
  </section>
</template>
