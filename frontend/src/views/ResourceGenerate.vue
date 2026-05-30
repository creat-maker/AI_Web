<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

interface GeneratedResource {
  id: number;
  title: string;
  resource_type?: string;
  difficulty?: string;
  source_agent?: string;
  content?: string;
  created_at?: string;
}

const { currentRole } = useRole();
const resources = ref<GeneratedResource[]>([]);
const courses = ref<Course[]>([]);
const profiles = ref<Array<{ id: number; student_name: string; course_id?: number }>>([]);
const events = ref<Array<{ id: number; event_type: string; title: string; metadata?: Record<string, any> }>>([]);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const latestPackageId = ref('');

const resourceTypes = ['知识讲义', 'PPT提纲', '分层练习题', '思维导图', '拓展阅读', '实验案例', '代码示例', '微课视频脚本'];
const agentSteps = ['画像分析 Agent', '知识解析 Agent', '资源规划 Agent', '内容生成 Agent', '多模态资源 Agent', '内容审核 Agent'];
const quizEvents = computed(() => events.value.filter((item) => item.event_type === 'quiz_completed'));

const pageCopy = computed(() => {
  if (currentRole.value === 'student') {
    return {
      title: '学生端 · 个性化资源生成',
      eyebrow: '个性化、多模态学习资源',
      description: '结合当前画像、课程目标和薄弱点，一键生成讲义、练习、案例、代码示例和微课脚本等资源包。'
    };
  }
  if (currentRole.value === 'teacher') {
    return {
      title: '教师端 · 教学资源生成',
      eyebrow: '分层教学与任务包生成',
      description: '按课程、班级和薄弱知识点生成分层练习、课件提纲、课堂案例和任务包，并推送给学生或分组。'
    };
  }
  return {
    title: '管理员端 · 资源生成中心',
    eyebrow: '资源任务监控与内容审核',
    description: '查看资源生成任务、成功率、失败任务、模板管理、内容审核和生成日志。'
  };
});

const statCards = computed(() => [
  { label: '资源总数', value: resources.value.length, unit: '份', hint: '来自资源接口' },
  { label: '资源类型', value: resourceTypes.length, unit: '类', hint: '覆盖多模态资源形态', tone: 'green' as const },
  { label: currentRole.value === 'admin' ? '生成成功率' : '推荐生成', value: currentRole.value === 'admin' ? 94 : 3, unit: currentRole.value === 'admin' ? '%' : '项', hint: 'demo/fallback 指标', tone: 'orange' as const },
  { label: currentRole.value === 'student' ? '加入路径' : currentRole.value === 'teacher' ? '待审核资源' : '失败任务', value: currentRole.value === 'admin' ? 1 : 4, unit: currentRole.value === 'admin' ? '项' : '份', hint: '演示指标', tone: 'purple' as const }
]);

async function load() {
  loading.value = true;
  error.value = '';
  try {
    resources.value = await api.get<GeneratedResource[]>('/api/v1/resources');
    courses.value = await api.get<Course[]>('/api/v1/courses').catch(() => []);
    profiles.value = await api.get<Array<{ id: number; student_name: string; course_id?: number }>>('/api/v1/profiles').catch(() => []);
    events.value = await api.get<Array<{ id: number; event_type: string; title: string; metadata?: Record<string, any> }>>('/api/v1/events?limit=30').catch(() => []);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '资源数据加载失败，请确认后端已启动。';
  } finally {
    loading.value = false;
  }
}

function demoAction(label: string) {
  operationMessage.value = `${label} 为 demo/fallback 操作，后续可接真实资源生成、审核或推送接口。`;
}

async function generatePackage() {
  operationMessage.value = '';
  try {
    const profile = profiles.value[0];
    const courseId = profile?.course_id || courses.value[0]?.id;
    const data = await api.post<{ package_id: string; resources: GeneratedResource[]; demo_fallback_note: string }>('/api/v1/events/resource-package', {
      course_id: courseId,
      student_profile_id: profile?.id,
      actor_role: currentRole.value,
      actor_name: profile?.student_name || 'demo_student'
    });
    latestPackageId.value = data.package_id;
    resources.value = [...data.resources, ...resources.value];
    operationMessage.value = `已生成资源包 ${data.package_id}，包含 8 类资源。${data.demo_fallback_note}`;
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '资源包生成失败。';
  }
}

async function addPackageToPath() {
  operationMessage.value = '';
  try {
    const profile = profiles.value[0];
    const courseId = profile?.course_id || courses.value[0]?.id;
    const packageId = latestPackageId.value || 'pkg-demo-latest';
    await api.post('/api/v1/events/add-resource-to-path', {
      package_id: packageId,
      course_id: courseId,
      student_profile_id: profile?.id,
      actor_role: currentRole.value,
      actor_name: profile?.student_name || 'demo_student'
    });
    operationMessage.value = `资源包 ${packageId} 已加入学习路径，可到学习路径页面查看。`;
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '加入学习路径失败。';
  }
}

async function recordAdminResourceAction(label: string) {
  await api.post('/api/v1/events', {
    event_type: 'admin_review_completed',
    title: label,
    description: `${label} 已记录到资源生成中心事件流。`,
    actor_role: 'admin',
    actor_name: 'demo_admin',
    target_type: 'resource_task',
    target_id: latestPackageId.value || 'resource-task-demo',
    status: 'success',
    metadata: { task_status: 'reviewing', demo: true }
  });
  operationMessage.value = `${label} 已写入事件日志。`;
}

onMounted(load);
</script>

<template>
  <section class="page role-aware-page">
    <article class="placeholder-hero">
      <span class="status-badge info">{{ pageCopy.eyebrow }}</span>
      <h2>{{ pageCopy.title }}</h2>
      <p>{{ pageCopy.description }}</p>
    </article>

    <p class="demo-banner">当前资源生成列表来自现有接口；一键生成、推送、审核等按钮为演示操作，不伪装成真实大模型生成任务。</p>
    <p v-if="loading" class="panel muted">正在加载资源生成数据...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <template v-if="!loading && !error">
      <div class="role-grid">
        <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
      </div>

      <section class="role-layout">
        <article class="panel">
          <div class="panel-title">
            <h2>{{ currentRole === 'admin' ? '资源生成任务总览' : '资源生成配置' }}</h2>
            <span class="muted">{{ currentRole === 'student' ? '基于当前画像和薄弱点' : currentRole === 'teacher' ? '面向课程和班级' : '平台级监控' }}</span>
          </div>
          <div class="reference-list">
            <small v-for="type in resourceTypes" :key="type">{{ type }}</small>
          </div>
          <div class="quick-grid">
            <button v-if="currentRole === 'student'" @click="generatePackage">一键生成个性化资源包</button>
            <button v-if="currentRole === 'student'" class="secondary" @click="addPackageToPath">加入学习路径</button>
            <button v-if="currentRole === 'student'" class="secondary" @click="demoAction('收藏/下载')">收藏/下载</button>
            <button v-if="currentRole === 'teacher'" @click="demoAction('按薄弱知识点生成分层练习')">生成分层练习</button>
            <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('生成课件提纲')">生成课件提纲</button>
            <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('推送给学生或分组')">推送给学生</button>
            <button v-if="currentRole === 'admin'" @click="recordAdminResourceAction('内容审核')">内容审核</button>
            <button v-if="currentRole === 'admin'" class="secondary" @click="recordAdminResourceAction('模板管理')">模板管理</button>
            <button v-if="currentRole === 'admin'" class="secondary" @click="recordAdminResourceAction('查看生成日志')">生成日志</button>
          </div>
        </article>

        <article class="panel">
          <h2>多智能体生成过程摘要</h2>
          <div class="agent-step-list">
            <div v-for="(step, index) in agentSteps" :key="step" class="item compact">
              <strong>{{ index + 1 }}. {{ step }}</strong>
              <span>{{ index < 5 ? 'success' : 'demo 审核' }}</span>
            </div>
          </div>
        </article>
      </section>

      <section v-if="currentRole === 'student'" class="role-layout">
        <article class="panel">
          <h2>当前画像摘要</h2>
          <div class="list">
            <div class="item compact">学习目标<span>掌握课程核心概念</span></div>
            <div class="item compact">当前薄弱点<span>HTTP 请求、函数、文件操作</span></div>
            <div class="item compact">资源偏好<span>案例驱动 + 分层练习</span></div>
          </div>
        </article>
        <article class="panel">
          <h2>基于测验薄弱点推荐</h2>
          <div v-if="quizEvents.length" class="list">
            <div v-for="item in quizEvents.slice(0, 3)" :key="item.id" class="item compact">
              {{ (item.metadata?.quiz_result?.weak_points || ['HTTP 请求']).join('、') }}
              <span>{{ (item.metadata?.quiz_result?.suggested_resources || ['分层练习题']).join('、') }}</span>
            </div>
          </div>
          <p v-else>暂无测验事件，优先生成知识讲义、代码示例、分层练习题和微课视频脚本。</p>
        </article>
      </section>

      <section v-if="currentRole === 'admin'" class="panel">
        <div class="panel-title">
          <h2>平台治理视角</h2>
          <span class="status-badge warning">审核与监控</span>
        </div>
        <div class="role-grid">
          <StatCard label="今日生成次数" value="32" unit="次" hint="demo/fallback 统计" />
          <StatCard label="失败任务" value="1" unit="项" hint="可进入日志排查" tone="orange" />
          <StatCard label="模板数量" value="8" unit="个" hint="按资源类型预置" tone="green" />
          <StatCard label="待审核内容" value="4" unit="份" hint="管理员治理入口" tone="purple" />
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>{{ currentRole === 'student' ? '我的推荐资源' : currentRole === 'teacher' ? '教学资源列表' : '生成任务与资源列表' }}</h2>
          <span class="muted">{{ resources.length }} 份资源</span>
        </div>
        <div class="resource-grid">
          <article v-for="item in resources" :key="item.id" class="resource-card">
            <div class="panel-title">
              <strong>{{ item.title }}</strong>
              <span class="status-badge success">{{ item.resource_type || '资源' }}</span>
            </div>
            <p class="muted">{{ item.difficulty || '适中' }} · {{ item.source_agent || 'EduMind demo agent' }}</p>
            <div class="markdown">{{ item.content || '暂无资源内容。' }}</div>
            <div class="quick-grid">
              <button v-if="currentRole === 'student'" class="secondary" @click="addPackageToPath">加入路径</button>
              <button v-if="currentRole === 'student'" class="secondary" @click="demoAction('收藏资源')">收藏</button>
              <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('教师审核与编辑')">审核编辑</button>
              <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('推送给学生')">推送</button>
              <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('内容安全检查')">安全检查</button>
              <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('查看生成日志')">日志</button>
            </div>
          </article>
          <EmptyState v-if="!resources.length" title="暂无生成资源" description="运行演示数据或接入生成接口后会显示。" />
        </div>
      </section>
    </template>
  </section>
</template>
