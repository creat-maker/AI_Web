<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';
import { platformQuality } from '../api/mocks/competitionData';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

type PlatformQuality = typeof platformQuality;

const data = ref<PlatformQuality>(platformQuality);
const loading = ref(true);
const error = ref('');

async function load() {
  loading.value = true;
  error.value = '';
  try {
    data.value = await api.get<PlatformQuality>('/api/v1/admin/platform-quality');
  } catch (err) {
    error.value = err instanceof Error ? `课程质量接口暂不可用，已使用本地业务样例：${err.message}` : '课程质量接口暂不可用，已使用本地业务样例。';
    data.value = platformQuality;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="page admin-platform-quality">
    <PageHeader title="课程质量评价" description="从课程完成率、测验均分、资源使用率、薄弱知识点集中度和教师 AI 工具使用情况评价课程运行质量。">
      <template #actions>
        <RouterLink class="btn secondary" to="/admin/content-review">内容审核</RouterLink>
        <RouterLink class="btn" to="/dashboard">平台总览</RouterLink>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载课程质量评价...</p>
    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="课程完成率" :value="data.summary.course_completion_rate" unit="%" hint="平台课程平均" icon="课" />
      <StatCard label="测验均分" :value="data.summary.average_quiz_score" unit="分" hint="章节测验统计" icon="测" tone="green" />
      <StatCard label="资源使用率" :value="data.summary.resource_usage_rate" unit="%" hint="推荐资源访问" icon="资" tone="purple" />
      <StatCard label="教师 AI 使用" :value="data.summary.teacher_ai_tool_uses" unit="次" hint="工作台生成记录" icon="AI" tone="orange" />
    </div>

    <div class="quality-layout">
      <DataCard title="AI 平台治理指标" subtitle="统计 AI 问答、资源生成、测验完成和审核通过率。">
        <div class="metric-list">
          <article>
            <span>AI 问答次数</span>
            <strong>{{ data.ai_metrics.qa_count }}</strong>
          </article>
          <article>
            <span>资源生成次数</span>
            <strong>{{ data.ai_metrics.resource_generation_count }}</strong>
          </article>
          <article>
            <span>测验完成次数</span>
            <strong>{{ data.ai_metrics.quiz_completion_count }}</strong>
          </article>
          <article>
            <span>内容审核通过率</span>
            <strong>{{ data.ai_metrics.review_pass_rate }}%</strong>
          </article>
        </div>
      </DataCard>

      <DataCard title="AI 能力边界" subtitle="平台治理说明">
        <div class="boundary-box">
          <StatusBadge label="审核后使用" tone="warning" />
          <p>{{ data.ai_boundary }}</p>
        </div>
      </DataCard>
    </div>

    <DataCard title="课程质量维度" subtitle="用于发现课程运行问题并形成治理建议。">
      <div class="dimension-list">
        <article v-for="item in data.quality_dimensions" :key="item.name">
          <div>
            <strong>{{ item.name }}</strong>
            <span>{{ item.suggestion }}</span>
          </div>
          <div class="dimension-progress">
            <span>{{ item.value }}%</span>
            <ProgressBar :value="item.value" :tone="item.value >= 80 ? 'success' : item.value >= 60 ? 'primary' : 'warning'" />
          </div>
        </article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.quality-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
}

.metric-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.metric-list article,
.dimension-list article,
.boundary-box {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.metric-list span,
.dimension-list span {
  display: block;
  color: var(--color-text-sub);
  font-size: 13px;
}

.metric-list strong {
  display: block;
  margin-top: 8px;
  font-size: 24px;
}

.boundary-box {
  display: grid;
  gap: 12px;
  background: #fff7ed;
  border-color: #fed7aa;
}

.dimension-list {
  display: grid;
  gap: 12px;
}

.dimension-list article {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 16px;
  align-items: center;
}

.dimension-progress {
  display: grid;
  gap: 8px;
}

@media (max-width: 1100px) {
  .quality-layout,
  .metric-list,
  .dimension-list article {
    grid-template-columns: 1fr;
  }
}
</style>
