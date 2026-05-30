<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { api } from '../api/client';
import { useRole } from '../composables/useRole';

interface DemoStatus {
  status: 'ready' | 'missing_report' | 'warning' | string;
  message: string;
  passed: number;
  total: number;
  pass_rate: string;
  report_path: string;
  last_checked_at: string;
  key_events: Array<{ event_type: string; label: string; status: string }>;
  demo_routes: Record<'student' | 'teacher' | 'admin', string[]>;
  real_capabilities: string[];
  demo_fallback_capabilities: string[];
  refresh_command: string;
}

interface DemoStep {
  step: number;
  title: string;
  route: string;
  goal: string;
  script: string;
  expected: string;
}

interface DemoGroup {
  key: 'student' | 'teacher' | 'admin';
  title: string;
  duration: string;
  steps: DemoStep[];
}

const router = useRouter();
const { setRole } = useRole();
const loading = ref(true);
const error = ref('');
const data = ref<DemoStatus | null>(null);
const activeStepKey = ref('student-1');
const scriptsExpanded = ref(true);
const toast = ref('');

const demoGroups: DemoGroup[] = [
  {
    key: 'student',
    title: '学生端演示步骤',
    duration: '约 3 分钟',
    steps: [
      { step: 1, title: '学习总览', route: '/student', goal: '展示学生个性化学习入口和今日学习状态', script: '学生进入系统后，首先看到学习总览，包括今日目标、课程进度、学习路径、推荐资源和学习报告入口。', expected: '页面显示学生端首页、画像状态、推荐资源、今日任务等信息。' },
      { step: 2, title: '对话建画像', route: '/profiles', goal: '展示系统如何通过对话生成学生画像', script: '系统通过自然语言采集学生专业、学习目标、基础水平、学习偏好和薄弱点，生成多维动态画像，后续资源生成和路径规划都会基于该画像。', expected: '显示画像维度、画像标签、薄弱点、资源偏好。' },
      { step: 3, title: '个性化资源生成', route: '/resource-generation', goal: '展示基于画像和课程知识库生成多模态资源包', script: '系统调用多智能体流程，生成知识讲义、PPT 提纲、分层练习题、思维导图、拓展阅读、实验案例、代码示例和微课视频脚本等资源。', expected: '资源包生成成功，并可加入学习路径。' },
      { step: 4, title: '学习路径', route: '/learning-path', goal: '展示资源包如何被组织为个性化路径', script: '系统将生成资源绑定到学习路径节点，每个节点包含学习目标、资源、任务、测验和完成条件。', expected: '学习路径中出现资源包摘要或路径更新提示。' },
      { step: 5, title: '智能答疑', route: '/tutor-chat', goal: '展示基于知识库引用和学生画像的智能辅导', script: '智能答疑不是普通聊天，而是结合学生画像、当前学习路径和课程知识库，提供引用来源、分层提示和追问建议。', expected: '显示回答、引用来源卡片和推荐追问。' },
      { step: 6, title: '测验成绩', route: '/evaluation', goal: '展示测验反馈如何影响薄弱点和画像', script: '系统根据测验结果识别薄弱知识点，并将结果反馈给画像和学习路径，实现动态个性化调整。', expected: '显示测验结果、薄弱点、推荐资源或路径建议。' },
      { step: 7, title: '学习报告', route: '/reports', goal: '展示学习报告和证据链', script: '学习报告汇总学习行为、测验结果、答疑记录和资源使用情况，并通过证据链解释每个结论的来源。', expected: '显示综合评分、薄弱点、学习建议、证据链。' }
    ]
  },
  {
    key: 'teacher',
    title: '教师端演示步骤',
    duration: '约 2 分钟',
    steps: [
      { step: 1, title: '班级概览', route: '/teacher', goal: '展示教师端教学管理入口', script: '教师端用于查看班级整体学习情况、风险学生、薄弱知识点和待处理任务。', expected: '显示课程数、学生数、风险学生、薄弱知识点和快捷操作。' },
      { step: 2, title: '学生画像分析', route: '/profiles', goal: '展示教师如何查看学生画像并进行干预', script: '教师可以查看单个学生的画像、能力雷达、薄弱点和学习趋势，并据此进行精准教学干预。', expected: '显示学生画像、风险等级、干预建议。' },
      { step: 3, title: '布置补强任务', route: '/profiles', goal: '展示教师干预如何联动学生端任务', script: '教师可根据画像和薄弱点布置补强任务，系统会将任务同步到学生端今日任务和学习路径中。', expected: '产生 task_assigned 或 teacher_intervention_created 事件。' },
      { step: 4, title: '测验评价与教师分析', route: '/evaluation', goal: '展示班级测验分析和教学建议', script: '教师可查看成绩分布、错题知识点和教学建议，辅助后续教学调整。', expected: '显示成绩分布、题型正确率、薄弱知识点和教学建议。' },
      { step: 5, title: '报告中心', route: '/reports', goal: '展示教师查看学生报告和班级报告', script: '报告中心支持学生报告、班级报告、课程报告和测验报告，帮助教师进行教学复盘。', expected: '显示报告列表、报告详情、证据链和干预建议。' }
    ]
  },
  {
    key: 'admin',
    title: '管理员端演示步骤',
    duration: '约 2 分钟',
    steps: [
      { step: 1, title: '平台总览', route: '/dashboard', goal: '展示平台整体运行状态', script: '管理员端负责平台治理和运行监控，可查看系统健康、AI 生成次数、报告数量、告警和日志。', expected: '显示平台总览和比赛演示状态卡。' },
      { step: 2, title: 'Agent 工作流', route: '/agent-workflow', goal: '展示多智能体协同流程', script: '系统通过画像 Agent、知识 Agent、资源规划 Agent、内容生成 Agent、审核 Agent 和推荐 Agent 协同完成学习服务。', expected: '显示节点状态、输入输出摘要、耗时和 run_id。' },
      { step: 3, title: '资源生成中心', route: '/resource-generation', goal: '展示资源生成任务监控', script: '管理员可以查看资源生成任务、生成状态、失败任务和内容审核情况。', expected: '显示任务列表、状态分布和审核入口。' },
      { step: 4, title: '报告审核', route: '/reports', goal: '展示 AI 生成报告审核机制', script: '管理员可对 AI 生成报告进行内容审核、引用来源检查和驳回重生成，保障生成内容安全可信。', expected: '显示审核按钮、审核状态和日志记录。' },
      { step: 5, title: '日志管理', route: '/logs', goal: '展示系统可观测性和事件追踪', script: '系统会记录画像生成、资源生成、路径更新、教师干预、测验完成、智能答疑和管理员审核等关键事件，便于审计和问题追踪。', expected: '日志中可筛选业务事件。' }
    ]
  }
];

const totalDemoSteps = computed(() => demoGroups.reduce((sum, group) => sum + group.steps.length, 0));

const statusTone = computed(() => {
  if (data.value?.status === 'ready') return 'success';
  if (data.value?.status === 'missing_report') return 'warning';
  return 'danger';
});

const statusLabel = computed(() => {
  if (data.value?.status === 'ready') return 'Ready';
  if (data.value?.status === 'missing_report') return 'Missing Report';
  return 'Warning';
});

async function loadPage() {
  loading.value = true;
  error.value = '';
  try {
    data.value = await api.get<DemoStatus>('/api/v1/demo-status');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '比赛演示状态加载失败。';
  } finally {
    loading.value = false;
  }
}

function startDemo() {
  setRole('student');
  activeStepKey.value = 'student-1';
  router.push('/student');
}

function openStep(group: DemoGroup, step: DemoStep) {
  setRole(group.key);
  activeStepKey.value = `${group.key}-${step.step}`;
  router.push(step.route);
}

async function copyScript(step: DemoStep) {
  try {
    if (!navigator.clipboard?.writeText) {
      toast.value = '当前浏览器不支持直接复制，请手动选中讲解词';
    } else {
      await navigator.clipboard.writeText(step.script);
      toast.value = `已复制讲解词：${step.title}`;
    }
  } catch {
    toast.value = '当前浏览器不支持直接复制，请手动选中讲解词';
  }
  window.setTimeout(() => {
    toast.value = '';
  }, 2200);
}

onMounted(loadPage);
</script>

<template>
  <section class="page role-aware-page">
    <article class="placeholder-hero">
      <StatusBadge :label="`比赛演示状态：${statusLabel}`" :tone="statusTone" />
      <h2>比赛演示模式面板</h2>
      <p>用于答辩前快速确认主链路、关键事件、三端路线和能力边界。浏览器不会执行本地脚本，请在终端运行验收命令刷新报告。</p>
    </article>

    <p v-if="loading" class="panel muted">正在读取最近一次验收报告...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="toast" class="panel success-text">{{ toast }}</p>

    <template v-if="!loading && !error && data">
      <div v-if="data.status === 'missing_report'" class="panel">
        <EmptyState title="尚未生成验收报告" :description="data.message" />
      </div>

      <div class="role-grid">
        <StatCard label="通过率" :value="data.pass_rate || '0%'" hint="端到端验收通过率" />
        <StatCard label="通过步骤" :value="`${data.passed}/${data.total}`" hint="主链路步骤" tone="green" />
        <StatCard label="最近验收时间" :value="data.last_checked_at || '未验收'" hint="来自 reports/demo_flow_check.md" tone="orange" />
        <StatCard label="报告路径" :value="data.report_path || 'reports/demo_flow_check.md'" hint="Markdown 验收报告" tone="purple" />
      </div>

      <section class="panel demo-overview-card">
        <div>
          <p class="eyebrow">答辩演示导航模式</p>
          <h2>7 分钟稳定演示路线</h2>
          <p class="muted">推荐顺序：学生端 → 教师端 → 管理员端。共 {{ totalDemoSteps }} 个步骤，当前系统状态 {{ statusLabel }}，e2e 通过率 {{ data.pass_rate }}。</p>
          <p class="demo-banner">该导航只负责跳转和讲解提示，不会执行本地脚本；所有真实/演示能力边界请以页面说明为准。</p>
        </div>
        <div class="demo-actions">
          <button @click="startDemo">开始演示</button>
          <button class="secondary" @click="scriptsExpanded = !scriptsExpanded">
            {{ scriptsExpanded ? '一键收起讲解词' : '一键展开讲解词' }}
          </button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>主链路通过情况</h2>
          <span class="muted">{{ data.message }}</span>
        </div>
        <div class="event-status-grid">
          <article v-for="item in data.key_events" :key="item.event_type" class="item compact">
            <strong>{{ item.label }}</strong>
            <StatusBadge :label="item.status" :tone="item.status === 'PASS' ? 'success' : item.status === 'UNKNOWN' ? 'warning' : 'danger'" />
          </article>
        </div>
      </section>

      <section class="demo-script-list">
        <article v-for="group in demoGroups" :key="group.key" class="panel">
          <div class="panel-title">
            <h2>{{ group.title }}</h2>
            <span class="muted">{{ group.duration }}</span>
          </div>
          <div class="demo-step-grid">
            <article
              v-for="step in group.steps"
              :key="`${group.key}-${step.step}`"
              :class="['demo-step-card', { active: activeStepKey === `${group.key}-${step.step}` }]"
            >
              <div class="step-card-head">
                <StatusBadge :label="`Step ${step.step}`" :tone="activeStepKey === `${group.key}-${step.step}` ? 'success' : 'info'" />
                <code>{{ step.route }}</code>
              </div>
              <h3>{{ step.title }}</h3>
              <p><strong>演示目标：</strong>{{ step.goal }}</p>
              <p v-if="scriptsExpanded"><strong>推荐讲解词：</strong>{{ step.script }}</p>
              <p><strong>预期结果：</strong>{{ step.expected }}</p>
              <div class="step-actions">
                <button class="secondary" @click="openStep(group, step)">打开页面</button>
                <button class="secondary" @click="copyScript(step)">复制讲解词</button>
              </div>
            </article>
          </div>
        </article>
      </section>

      <section class="role-layout">
        <article class="panel">
          <h2>真实能力</h2>
          <div class="list">
            <div v-for="item in data.real_capabilities" :key="item" class="item compact">{{ item }}</div>
          </div>
        </article>
        <article class="panel">
          <h2>demo/mock/fallback 能力</h2>
          <p class="demo-banner">以下能力用于比赛演示边界说明，不伪装成生产能力。</p>
          <div class="list">
            <div v-for="item in data.demo_fallback_capabilities" :key="item" class="item compact">{{ item }}</div>
          </div>
        </article>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>刷新验收报告命令</h2>
          <span class="muted">请在终端运行</span>
        </div>
        <pre>{{ data.refresh_command }}</pre>
        <p class="demo-banner">浏览器不会直接执行本地 Python 脚本。运行命令后刷新本页即可读取最新报告。</p>
      </section>
    </template>
  </section>
</template>

<style scoped>
.event-status-grid,
.demo-step-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.demo-overview-card {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
}

.demo-overview-card h2 {
  margin: 0 0 8px;
}

.demo-actions,
.step-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.demo-script-list {
  display: grid;
  gap: 16px;
}

.demo-step-card {
  border: 1px solid #e4e9f1;
  border-radius: 10px;
  padding: 14px;
  background: #fbfcff;
}

.demo-step-card.active {
  border-color: #2264d1;
  box-shadow: 0 8px 22px rgba(34, 100, 209, 0.12);
}

.demo-step-card h3 {
  margin: 10px 0 8px;
}

.demo-step-card p {
  color: #39475a;
  line-height: 1.6;
}

.step-card-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.step-card-head code {
  color: #1453aa;
}

@media (max-width: 820px) {
  .demo-overview-card {
    display: grid;
  }
}
</style>
