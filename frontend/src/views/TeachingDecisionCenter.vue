<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface DecisionOverview {
  title: string;
  metrics: Array<{ label: string; value: number | string; unit?: string }>;
  heatmap: Array<{ knowledgePoint: string; mastery: number }>;
  agentStatus: Array<{ name: string; status: string }>;
  miniprogramActive: { todayUsers: number; weeklyRetention: string };
  teacherEfficiency: { savedHours: number; autoReports: number; recommendedInterventions: number };
}

const defaultOverview: DecisionOverview = {
  title: 'EduMind 教学智能决策中心',
  metrics: [
    { label: 'AI 生成资源数', value: 286, unit: '份' },
    { label: '学生画像数量', value: 128, unit: '份' },
    { label: '学习预警人数', value: 12, unit: '人' },
    { label: '学习路径完成率', value: 76.8, unit: '%' },
    { label: '内容审核通过率', value: 91.2, unit: '%' },
    { label: 'AI 学伴使用次数', value: 18620, unit: '次' }
  ],
  heatmap: [
    { knowledgePoint: 'for 循环', mastery: 72 },
    { knowledgePoint: 'while 循环', mastery: 48 },
    { knowledgePoint: 'break / continue', mastery: 55 },
    { knowledgePoint: '循环嵌套', mastery: 43 }
  ],
  agentStatus: [
    { name: '画像构建 Agent', status: '运行正常' },
    { name: '知识检索 Agent', status: '运行正常' },
    { name: '资源生成 Agent', status: '运行正常' },
    { name: '内容安全与防幻觉审核 Agent', status: '待人工复核 3 项' }
  ],
  miniprogramActive: { todayUsers: 86, weeklyRetention: '68%' },
  teacherEfficiency: { savedHours: 42, autoReports: 56, recommendedInterventions: 18 }
};

const data = ref<DecisionOverview>(defaultOverview);
const message = ref('');
const loading = ref(false);

async function load() {
  loading.value = true;
  message.value = '正在刷新教学决策数据...';
  try {
    data.value = await api.get<DecisionOverview>('/api/v1/decision-center/overview');
    message.value = '教学决策数据已刷新。';
  } catch (err) {
    data.value = defaultOverview;
    message.value = '当前网络不稳定，已为你展示本地学习建议。';
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="page decision-center-page">
    <PageHeader :title="data.title" description="汇总资源生成、画像、风险、路径、审核、AI 学伴、小程序活跃和教师减负统计。">
      <template #actions>
        <button class="secondary" :disabled="loading" @click="load">{{ loading ? '刷新中...' : '刷新' }}</button>
      </template>
    </PageHeader>

    <p v-if="message" class="panel muted">{{ message }}</p>

    <div class="stat-grid">
      <StatCard v-for="item in data.metrics" :key="item.label" :label="item.label" :value="item.value" :unit="item.unit" icon="数" />
      <p v-if="!data.metrics.length" class="panel muted">暂无数据，系统将根据你的学习记录生成建议。</p>
    </div>

    <div class="two-column">
      <DataCard title="知识点掌握热力图" subtitle="Python 程序设计 / 循环结构">
        <div class="heatmap-list">
          <article v-for="item in data.heatmap" :key="item.knowledgePoint">
            <span>{{ item.knowledgePoint }}</span>
            <ProgressBar :value="item.mastery" :tone="item.mastery < 60 ? 'warning' : 'primary'" />
            <strong>{{ item.mastery }}%</strong>
          </article>
          <p v-if="!data.heatmap.length" class="muted">暂无数据，系统将根据你的学习记录生成建议。</p>
        </div>
      </DataCard>

      <DataCard title="多智能体运行状态" subtitle="核心 Agent 可观测状态">
        <div class="agent-status-list">
          <article v-for="item in data.agentStatus" :key="item.name">
            <strong>{{ item.name }}</strong>
            <StatusBadge :label="item.status" :tone="item.status.includes('复核') ? 'warning' : 'success'" />
          </article>
          <p v-if="!data.agentStatus.length" class="muted">暂无数据，系统将根据你的学习记录生成建议。</p>
        </div>
      </DataCard>
    </div>

    <div class="two-column">
      <DataCard title="小程序活跃情况">
        <p>今日活跃：{{ data.miniprogramActive.todayUsers }} 人</p>
        <p>周留存：{{ data.miniprogramActive.weeklyRetention }}</p>
      </DataCard>
      <DataCard title="教师减负统计">
        <p>节省备课与批改时间：{{ data.teacherEfficiency.savedHours }} 小时</p>
        <p>自动生成报告：{{ data.teacherEfficiency.autoReports }} 份</p>
        <p>推荐干预建议：{{ data.teacherEfficiency.recommendedInterventions }} 条</p>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.heatmap-list,
.agent-status-list {
  display: grid;
  gap: 12px;
}

.heatmap-list article {
  display: grid;
  grid-template-columns: 130px minmax(0, 1fr) 54px;
  gap: 10px;
  align-items: center;
}

.agent-status-list article {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
}
</style>
