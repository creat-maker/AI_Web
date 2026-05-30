<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

interface StudentProfileItem {
  id: number;
  course_id?: number;
  student_name: string;
  current_level?: string;
  learning_goal?: string;
  weak_points?: string[] | string;
  learning_preference?: string;
  profile_json?: unknown;
  created_at?: string;
}

const { currentRole } = useRole();
const courses = ref<Course[]>([]);
const profiles = ref<StudentProfileItem[]>([]);
const events = ref<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>([]);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const taskForm = reactive({
  student_profile_id: 0,
  course_id: 0,
  weak_point: 'HTTP 请求',
  task_type: '完成练习',
  due_date: ''
});
const form = reactive({
  course_id: 0,
  student_name: '张三',
  current_level: '基础薄弱',
  learning_goal: '两周内掌握 Python 爬虫基础',
  weak_points_text: '函数,文件操作,HTTP请求',
  learning_preference: '案例驱动'
});

const pageCopy = computed(() => {
  if (currentRole.value === 'student') {
    return {
      title: '学生端 · 对话建画像',
      eyebrow: '对话式学习画像自主构建',
      description: '通过学习目标、基础水平、资源偏好和薄弱知识点生成个人画像，为个性化资源、学习路径和答疑提供依据。'
    };
  }
  if (currentRole.value === 'teacher') {
    return {
      title: '教师端 · 学生画像分析',
      eyebrow: '班级学情诊断',
      description: '查看班级学生画像、能力条、风险等级和干预建议，并生成个性化学习报告。'
    };
  }
  return {
    title: '管理员端 · 画像数据概览',
    eyebrow: '隐私与数据治理',
    description: '仅展示画像数据规模、字段边界和隐私权限提示，不默认暴露过多学生隐私细节。'
  };
});

const profileCount = computed(() => profiles.value.length);
const latestProfile = computed(() => profiles.value[0]);
const latestQuizEvent = computed(() => events.value.find((item) => item.event_type === 'quiz_completed'));
const statCards = computed(() => [
  { label: '画像数量', value: profileCount.value, unit: '份', hint: '来自学生画像接口' },
  { label: '画像完整度', value: 82, unit: '%', hint: 'demo/fallback 字段覆盖估计', tone: 'green' as const },
  { label: '薄弱点标签', value: 6, unit: '类', hint: '从画像和测评中归纳', tone: 'orange' as const },
  { label: currentRole.value === 'admin' ? '隐私字段' : '待干预学生', value: currentRole.value === 'admin' ? 4 : 2, unit: currentRole.value === 'admin' ? '类' : '人', hint: '演示指标', tone: 'purple' as const }
]);

function normalizeWeakPoints(profile: StudentProfileItem) {
  const value = profile.weak_points;
  if (Array.isArray(value)) return value;
  if (typeof value === 'string' && value.trim()) return value.split(',').map((item) => item.trim()).filter(Boolean);
  const raw = profile.profile_json as Record<string, unknown> | undefined;
  const fromJson = raw?.weak_points;
  return Array.isArray(fromJson) ? fromJson.map(String) : ['核心概念', '迁移应用'];
}

function rawProfile(profile: StudentProfileItem) {
  try {
    return JSON.stringify(profile.profile_json || profile, null, 2);
  } catch {
    return '原始画像数据无法序列化。';
  }
}

async function load() {
  loading.value = true;
  error.value = '';
  try {
    const [courseData, profileData, eventData] = await Promise.all([
      api.get<Course[]>('/api/v1/courses'),
      api.get<StudentProfileItem[]>('/api/v1/profiles'),
      api.get<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>('/api/v1/events?limit=30').catch(() => [])
    ]);
    courses.value = courseData;
    form.course_id = form.course_id || courses.value[0]?.id || 0;
    profiles.value = profileData;
    events.value = eventData;
    taskForm.student_profile_id = taskForm.student_profile_id || profiles.value[0]?.id || 0;
    taskForm.course_id = taskForm.course_id || profiles.value[0]?.course_id || courses.value[0]?.id || 0;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '画像数据加载失败，请确认后端已启动。';
  } finally {
    loading.value = false;
  }
}

async function createProfile() {
  operationMessage.value = '';
  try {
    await api.post('/api/v1/profiles/generate', {
      ...form,
      weak_points: form.weak_points_text.split(',').map((item) => item.trim()).filter(Boolean)
    });
    operationMessage.value = '画像已生成。';
    await load();
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '画像生成失败。';
  }
}

function demoAction(label: string) {
  operationMessage.value = `${label} 为演示操作，后续可接真实画像分析或报告生成流程。`;
}

async function assignTask() {
  operationMessage.value = '';
  try {
    const data = await api.post<{ task: Record<string, unknown>; status: string }>('/api/v1/events/assign-task', taskForm);
    operationMessage.value = `补强任务已布置：${data.task.task_type || taskForm.task_type}，学生端首页和学习路径可查看。`;
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '布置补强任务失败。';
  }
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

    <p v-if="loading" class="panel muted">正在加载画像数据...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <template v-if="!loading && !error">
      <div class="role-grid">
        <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
      </div>

      <p v-if="latestQuizEvent && currentRole === 'student'" class="panel demo-banner">
        最近测评更新了画像：{{ latestQuizEvent.description }} 推荐资源：{{ (latestQuizEvent.metadata?.quiz_result?.suggested_resources || ['分层练习题']).join('、') }}
      </p>

      <section v-if="currentRole === 'student'" class="panel">
        <div class="panel-title">
          <h2>对话式画像构建入口</h2>
          <span class="muted">demo/fallback 问卷式采集，后续可接真实对话建模</span>
        </div>
        <div class="form-grid">
          <label>课程<select v-model.number="form.course_id"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option></select></label>
          <label>学生<input v-model="form.student_name" /></label>
          <label>当前基础<input v-model="form.current_level" /></label>
          <label>学习偏好<input v-model="form.learning_preference" /></label>
          <label>薄弱知识点<input v-model="form.weak_points_text" /></label>
          <label>学习目标<textarea v-model="form.learning_goal" /></label>
          <button @click="createProfile">重新生成画像</button>
        </div>
      </section>

      <section v-if="currentRole === 'admin'" class="panel">
        <div class="panel-title">
          <h2>隐私与权限提示</h2>
          <span class="status-badge warning">演示模式</span>
        </div>
        <p>管理员端仅展示画像数据概览、字段边界和隐私合规提示。后续接真实鉴权后，应按最小权限原则限制原始画像访问。</p>
      </section>

      <section v-if="currentRole === 'teacher'" class="panel">
        <div class="panel-title">
          <h2>布置补强任务</h2>
          <span class="muted">提交后写入 task_assigned 事件，学生端可见</span>
        </div>
        <div class="form-grid">
          <label>学生<select v-model.number="taskForm.student_profile_id"><option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.student_name }}</option></select></label>
          <label>课程<select v-model.number="taskForm.course_id"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option></select></label>
          <label>薄弱知识点<input v-model="taskForm.weak_point" /></label>
          <label>任务类型<select v-model="taskForm.task_type"><option>阅读资料</option><option>完成练习</option><option>观看讲解</option><option>项目案例</option></select></label>
          <label>截止时间<input v-model="taskForm.due_date" type="date" /></label>
          <button @click="assignTask">布置补强任务</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>{{ currentRole === 'teacher' ? '班级学生画像列表' : currentRole === 'admin' ? '画像数据概览' : '我的画像详情' }}</h2>
          <span class="muted">{{ profiles.length }} 份画像</span>
        </div>
        <div class="profile-grid">
          <article v-for="profile in profiles" :key="profile.id" class="profile-card">
            <div class="panel-title">
              <div>
                <strong>{{ currentRole === 'admin' ? `学生画像 #${profile.id}` : profile.student_name }}</strong>
                <p class="muted">{{ profile.learning_goal || '暂无学习目标。' }}</p>
              </div>
              <span class="status-badge" :class="currentRole === 'teacher' ? 'warning' : 'success'">
                {{ currentRole === 'teacher' ? '需关注' : '已生成' }}
              </span>
            </div>
            <div class="ability-bars">
              <p><span>基础掌握</span><strong>68%</strong></p>
              <div class="progress-track"><span style="width: 68%"></span></div>
              <p><span>互动积极度</span><strong>76%</strong></p>
              <div class="progress-track"><span style="width: 76%"></span></div>
              <p><span>资源匹配度</span><strong>82%</strong></p>
              <div class="progress-track"><span style="width: 82%"></span></div>
            </div>
            <div class="reference-list">
              <small v-for="point in normalizeWeakPoints(profile)" :key="point">{{ point }}</small>
              <small>{{ profile.learning_preference || '案例驱动' }}</small>
            </div>
            <div class="quick-grid">
              <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('生成个性化学习报告')">生成报告</button>
              <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('添加干预建议')">干预建议</button>
              <RouterLink v-if="currentRole === 'student'" to="/resource-generation">生成资源</RouterLink>
              <RouterLink v-if="currentRole === 'student'" to="/learning-path">调整路径</RouterLink>
            </div>
            <details>
              <summary>原始画像数据（展开查看）</summary>
              <pre>{{ rawProfile(profile) }}</pre>
            </details>
          </article>
          <EmptyState v-if="!profiles.length" title="暂无画像" description="学生端生成画像或运行演示数据后会显示。" />
        </div>
      </section>

      <section v-if="latestProfile && currentRole !== 'admin'" class="role-layout">
        <article class="panel">
          <h2>画像更新时间线</h2>
          <div class="timeline-list">
            <p><strong>基础信息采集</strong><span>已完成</span></p>
            <p><strong>薄弱点归纳</strong><span>已完成</span></p>
            <p><strong>资源偏好同步</strong><span>待持续更新</span></p>
          </div>
        </article>
        <article class="panel">
          <h2>{{ currentRole === 'teacher' ? '教师干预建议' : '个性化下一步' }}</h2>
          <div class="list">
            <div class="item compact">围绕薄弱点追加分层练习</div>
            <div class="item compact">使用智能答疑进行追问式复盘</div>
            <div class="item compact">根据画像更新学习路径</div>
          </div>
        </article>
      </section>
    </template>
  </section>
</template>
