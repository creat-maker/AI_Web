<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { api } from '../api/client';
import { demoClasses, demoCourses, demoRoutes, demoStudents, demoTeachers } from '../api/mocks';

interface DemoStatus {
  status: 'ready' | 'missing_report' | 'warning' | 'error' | string;
  message: string;
  passed: number;
  total: number;
  pass_rate: string;
  report_path: string;
  ready_report_path?: string;
  last_checked_at: string;
  key_events: Array<{ event_type: string; label: string; status: string }>;
  demo_routes: Record<'student' | 'teacher' | 'admin', string[]>;
  readiness_checks: Array<{ name: string; status: string; detail: string }>;
  capability_checklist: Array<{ name: string; status: string; detail?: string }>;
  real_capabilities: string[];
  demo_fallback_capabilities: string[];
  feature_status?: {
    profile_dialog?: { supported: boolean; status?: string; dimensions?: number; dimension_count: number; dimension_labels?: string[]; update_mode?: string };
    multimodal_resources?: { status: string; resource_types: number; animation_html: boolean; tts_audio: string; video_script: boolean };
    assessment_adjustment?: { status: string; flow: string };
    multimodal_resource_type_count?: number;
    animation_html?: { supported: boolean; preview: string };
    tts_audio?: { status: string; message: string };
    ffmpeg?: { status: string; message: string };
    content_safety?: { status: string; message?: string; rule_based?: boolean; citation_check?: boolean; xfyun_safety?: string; provider_status?: { status: string; message: string } };
    evaluation_adjustment_loop?: { supported: boolean; fields: string[] };
    production_upgrade_path?: string[];
  };
  refresh_command: string;
}

type DemoRole = 'student' | 'teacher' | 'admin';

const router = useRouter();
const loading = ref(true);
const error = ref('');
const data = ref<DemoStatus | null>(null);
const activeStepKey = ref('student-1');
const scriptsExpanded = ref(true);
const toast = ref('');

const roleTitles: Record<DemoRole, string> = {
  student: '学生端推荐演示路线',
  teacher: '教师端推荐演示路线',
  admin: '管理员端推荐演示路线'
};

const roleDurations: Record<DemoRole, string> = {
  student: '约 3 分钟',
  teacher: '约 2 分钟',
  admin: '约 2 分钟'
};

const roleScripts: Record<DemoRole, string[]> = {
  student: [
    '学生进入系统后，先看到个人学习总览，随后进入课程、路径、答疑、测验和报告，形成完整学习闭环。',
    '课程页展示核心课程，学习路径页承接画像与资源生成结果。',
    '智能答疑演示基于课程资料的引用回答，测验与报告页展示结果沉淀。'
  ],
  teacher: [
    '教师先从班级概览识别需关注学生和薄弱知识点，再进入课程、画像和路径页面进行干预。',
    '测评分析页用于解释班级共性问题，报告中心用于沉淀学生和班级改进建议。',
    '教师端重点回答“如何从数据发现问题并完成教学干预”。'
  ],
  admin: [
    '管理员从平台总览进入治理视角，检查用户角色、课程治理、资源生成、Agent、日志和设置。',
    'Agent 工作流展示多智能体节点和运行产物，日志管理展示事件追踪和可观测性。',
    '管理员端重点回答“平台如何稳定、可信、可治理地支撑三端演示”。'
  ]
};

const demoGroups = (Object.keys(demoRoutes) as DemoRole[]).map((key) => ({
  key,
  title: roleTitles[key],
  duration: roleDurations[key],
  steps: demoRoutes[key].map((item, index) => ({
    step: index + 1,
    title: item.title,
    route: item.route,
    goal: item.goal,
    script: roleScripts[key][Math.min(index, roleScripts[key].length - 1)],
    expected: `页面可访问，并展示 ${item.title} 相关演示数据或能力边界说明。`
  }))
}));

const totalDemoSteps = computed(() => demoGroups.reduce((sum, group) => sum + group.steps.length, 0));

const statusTone = computed(() => {
  if (data.value?.status === 'ready') return 'success';
  if (data.value?.status === 'missing_report' || data.value?.status === 'warning') return 'warning';
  return 'danger';
});

const statusLabel = computed(() => {
  if (data.value?.status === 'ready') return 'Ready';
  if (data.value?.status === 'missing_report') return 'Missing Report';
  if (data.value?.status === 'warning') return 'Warning';
  return 'Error';
});

function tone(status: string) {
  if (status === 'PASS' || status === 'READY') return 'success';
  if (status === 'WARN' || status === 'UNKNOWN' || status === 'WARNING') return 'warning';
  return 'danger';
}

async function loadPage() {
  loading.value = true;
  error.value = '';
  try {
    data.value = await api.get<DemoStatus>('/api/v1/demo-status');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '验收状态加载失败。';
  } finally {
    loading.value = false;
  }
}

function startDemo() {
  activeStepKey.value = '';
  router.push('/login');
}

function openStep(group: { key: DemoRole }, step: { step: number; route: string }) {
  activeStepKey.value = `${group.key}-${step.step}`;
  router.push('/login');
}

async function copyScript(step: { title: string; script: string }) {
  try {
    if (!navigator.clipboard?.writeText) {
      toast.value = '当前浏览器不支持直接复制，请手动选中讲解词。';
    } else {
      await navigator.clipboard.writeText(step.script);
      toast.value = `已复制讲解词：${step.title}`;
    }
  } catch {
    toast.value = '当前浏览器不支持直接复制，请手动选中讲解词。';
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
      <StatusBadge :label="`演示状态：${statusLabel}`" :tone="statusTone" />
      <h2>演示闭环与最终验收</h2>
      <p>用于答辩前确认三端路由、后端健康、演示数据、关键能力、Agent 工作流和最近验收报告。</p>
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
        <StatCard label="最近验收" :value="data.last_checked_at || '未验收'" hint="来自验收报告" tone="orange" />
        <StatCard label="报告路径" :value="data.ready_report_path || data.report_path" hint="Markdown 验收报告" tone="purple" />
      </div>

      <section class="panel">
        <div class="panel-title">
          <h2>统一演示数据口径</h2>
          <span class="muted">前后端样例数据均围绕以下对象组织</span>
        </div>
        <div class="data-grid">
          <div class="item compact"><strong>学生</strong><span>{{ demoStudents.join('、') }}</span></div>
          <div class="item compact"><strong>教师</strong><span>{{ demoTeachers.join('、') }}</span></div>
          <div class="item compact"><strong>班级</strong><span>{{ demoClasses.join('、') }}</span></div>
          <div class="item compact"><strong>课程</strong><span>{{ demoCourses.join('、') }}</span></div>
        </div>
      </section>

      <section class="panel demo-overview-card">
        <div>
          <p class="eyebrow">答辩演示导航模式</p>
          <h2>7 分钟三端推荐演示路线</h2>
          <p class="muted">推荐顺序：学生端 -> 教师端 -> 管理员端。共 {{ totalDemoSteps }} 个步骤，当前系统状态 {{ statusLabel }}。</p>
          <p class="demo-banner">本页面负责路线说明和跳转，验收脚本需在终端运行，运行后刷新本页读取最新结果。</p>
        </div>
        <div class="demo-actions">
          <button @click="startDemo">前往登录页</button>
          <button class="secondary" @click="scriptsExpanded = !scriptsExpanded">
            {{ scriptsExpanded ? '收起讲解词' : '展开讲解词' }}
          </button>
        </div>
      </section>

      <section class="role-layout">
        <article class="panel">
          <div class="panel-title">
            <h2>演示状态检查</h2>
            <span class="muted">{{ data.message }}</span>
          </div>
          <div class="list">
            <div v-for="item in data.readiness_checks" :key="item.name" class="item compact">
              <strong>{{ item.name }}</strong>
              <span>{{ item.detail }}</span>
              <StatusBadge :label="item.status" :tone="tone(item.status)" />
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-title">
            <h2>关键能力清单</h2>
            <span class="muted">Ready / Warning / Error</span>
          </div>
          <div class="list">
            <div v-for="item in data.capability_checklist" :key="item.name" class="item compact">
              <strong>{{ item.name }}</strong>
              <span>{{ item.detail || '已纳入演示闭环' }}</span>
              <StatusBadge :label="item.status" :tone="tone(item.status)" />
            </div>
          </div>
        </article>
      </section>

      <section class="panel" v-if="data.feature_status">
        <div class="panel-title">
          <h2>赛题关键能力状态</h2>
          <span class="muted">画像、多模态资源、讯飞工具、内容安全与闭环</span>
        </div>
        <div class="event-status-grid">
          <article class="item compact">
            <strong>对话式画像</strong>
            <span>{{ data.feature_status.profile_dialog?.dimension_count || 6 }} 个画像维度</span>
            <StatusBadge label="PASS" tone="success" />
          </article>
          <article class="item compact">
            <strong>多模态资源</strong>
            <span>{{ data.feature_status.multimodal_resource_type_count || 0 }} 类资源</span>
            <StatusBadge label="PASS" tone="success" />
          </article>
          <article class="item compact">
            <strong>动画资源</strong>
            <span>{{ data.feature_status.animation_html?.preview || 'sandbox iframe' }}</span>
            <StatusBadge label="PASS" tone="success" />
          </article>
          <article class="item compact">
            <strong>讯飞 TTS</strong>
            <span>{{ data.feature_status.tts_audio?.message || '按环境变量配置接入' }}</span>
            <StatusBadge :label="data.feature_status.tts_audio?.status || 'not_configured'" :tone="data.feature_status.tts_audio?.status === 'configured' ? 'success' : 'warning'" />
          </article>
          <article class="item compact">
            <strong>内容安全</strong>
            <span>{{ data.feature_status.content_safety?.message || '本地规则审核已启用' }}</span>
            <StatusBadge label="PASS" tone="success" />
          </article>
          <article class="item compact">
            <strong>测评闭环</strong>
            <span>{{ data.feature_status.evaluation_adjustment_loop?.fields.join(' / ') || 'evaluation / path_adjustment' }}</span>
            <StatusBadge label="PASS" tone="success" />
          </article>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>主链路事件</h2>
          <span class="muted">来自 e2e_demo_flow_check 与业务事件日志</span>
        </div>
        <div class="event-status-grid">
          <article v-for="item in data.key_events" :key="item.event_type" class="item compact">
            <strong>{{ item.label }}</strong>
            <code>{{ item.event_type }}</code>
            <StatusBadge :label="item.status" :tone="tone(item.status)" />
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
                <button class="secondary" @click="openStep(group, step)">从登录页进入</button>
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
          <h2>演示能力边界</h2>
          <p class="demo-banner">以下内容用于说明演示能力边界，不伪装成生产能力。</p>
          <div class="list">
            <div v-for="item in data.demo_fallback_capabilities" :key="item" class="item compact">{{ item }}</div>
          </div>
        </article>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>刷新验收报告命令</h2>
          <span class="muted">请在项目根目录终端运行</span>
        </div>
        <pre>{{ data.refresh_command }}</pre>
      </section>
    </template>
  </section>
</template>

<style scoped>
.event-status-grid,
.demo-step-grid,
.data-grid {
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
  border-radius: 8px;
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
