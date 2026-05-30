<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

const { currentRole, currentRoleLabel } = useRole();
const courses = ref<Course[]>([]);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const form = reactive({
  title: 'Python 程序设计',
  subject: '计算机',
  teacher_name: '教师',
  description: 'Python 爬虫基础与实践'
});

const pageCopy = computed(() => {
  if (currentRole.value === 'student') {
    return {
      title: '学生端 · 我的课程',
      eyebrow: '个性化学习入口',
      description: '查看已加入课程、今日学习任务、课程资料和下一步学习入口。学生端隐藏删除等危险管理操作。'
    };
  }
  if (currentRole.value === 'teacher') {
    return {
      title: '教师端 · 课程管理',
      eyebrow: '教学组织与任务布置',
      description: '创建课程、管理章节、查看班级学生和课程进度，并为后续测验、报告和资源推送做准备。'
    };
  }
  return {
    title: '管理员端 · 平台课程管理',
    eyebrow: '平台治理与课程审核',
    description: '查看全平台课程数量、教师归属、课程状态、审核归档和内容合规状态。'
  };
});

const canManage = computed(() => currentRole.value !== 'student');
const statCards = computed(() => [
  { label: currentRole.value === 'student' ? '我的课程' : '课程总数', value: courses.value.length, unit: '门', hint: '来自课程接口' },
  { label: '活跃课程', value: Math.max(courses.value.length - 1, 0), unit: '门', hint: 'demo/fallback 状态估计', tone: 'green' as const },
  { label: currentRole.value === 'admin' ? '待审核课程' : '今日任务', value: currentRole.value === 'admin' ? 2 : 3, unit: currentRole.value === 'admin' ? '门' : '项', hint: '演示指标', tone: 'orange' as const },
  { label: currentRole.value === 'student' ? '平均进度' : '课程报告', value: currentRole.value === 'student' ? 68 : 5, unit: currentRole.value === 'student' ? '%' : '份', hint: 'demo/fallback 统计', tone: 'purple' as const }
]);

async function load() {
  loading.value = true;
  error.value = '';
  try {
    courses.value = await api.get<Course[]>('/api/v1/courses');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程数据加载失败，请确认后端已启动。';
  } finally {
    loading.value = false;
  }
}

async function createCourse() {
  operationMessage.value = '';
  try {
    await api.post<Course>('/api/v1/courses', form);
    operationMessage.value = '课程已保存。';
    await load();
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '保存课程失败。';
  }
}

async function removeCourse(id: number) {
  if (!canManage.value) return;
  operationMessage.value = '';
  try {
    await api.delete(`/api/v1/courses/${id}`);
    operationMessage.value = '课程已删除。';
    await load();
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '删除课程失败。';
  }
}

function demoAction(label: string) {
  operationMessage.value = `${label} 为 ${currentRoleLabel.value} 演示操作，后续可接真实业务流。`;
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

    <p v-if="loading" class="panel muted">正在加载课程数据...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <template v-if="!loading && !error">
      <div class="role-grid">
        <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
      </div>

      <section v-if="currentRole === 'student'" class="role-layout">
        <article class="panel">
          <h2>今日学习任务</h2>
          <div class="list">
            <div class="item compact">继续学习当前章节<span>20 分钟</span></div>
            <div class="item compact">完成课程测验<span>1 次</span></div>
            <div class="item compact">查看学习报告建议<span>今晚</span></div>
          </div>
        </article>
        <article class="panel">
          <h2>课程快捷入口</h2>
          <div class="quick-grid">
            <RouterLink to="/knowledge-base">课程资料</RouterLink>
            <RouterLink to="/evaluation">课程测验</RouterLink>
            <RouterLink to="/reports">学习报告</RouterLink>
            <RouterLink to="/resource-generation">推荐资源</RouterLink>
          </div>
        </article>
      </section>

      <section v-if="canManage" class="panel">
        <div class="panel-title">
          <h2>{{ currentRole === 'teacher' ? '新建课程' : '平台课程录入' }}</h2>
          <span class="muted">{{ currentRole === 'teacher' ? '教师可创建和维护课程' : '管理员用于平台课程治理' }}</span>
        </div>
        <div class="form-grid">
          <label>课程名称<input v-model="form.title" /></label>
          <label>学科<input v-model="form.subject" /></label>
          <label>教师<input v-model="form.teacher_name" /></label>
          <label>简介<input v-model="form.description" /></label>
          <button @click="createCourse">{{ currentRole === 'teacher' ? '保存课程' : '保存并进入审核' }}</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>{{ currentRole === 'student' ? '我的课程列表' : currentRole === 'teacher' ? '课程列表与教学管理' : '平台课程列表' }}</h2>
          <span class="muted">{{ courses.length }} 门课程</span>
        </div>
        <div class="course-table">
          <article v-for="course in courses" :key="course.id" class="course-row">
            <div>
              <strong>{{ course.title }}</strong>
              <p>{{ course.description || '暂无课程简介。' }}</p>
              <div class="reference-list">
                <small>{{ course.subject || '未设置学科' }}</small>
                <small>{{ course.teacher_name || '未设置教师' }}</small>
                <small v-if="currentRole === 'admin'">内容合规：已通过 demo 审核</small>
                <small v-else>课程进度：68%</small>
              </div>
            </div>
            <div class="course-actions">
              <RouterLink v-if="currentRole === 'student'" class="text-link" to="/learning-path">继续学习</RouterLink>
              <RouterLink v-if="currentRole === 'student'" class="text-link" to="/knowledge-base">查看资料</RouterLink>
              <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('章节管理')">章节管理</button>
              <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('布置任务')">布置任务</button>
              <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('发布课程')">发布课程</button>
              <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('课程审核')">审核</button>
              <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('课程归档')">归档</button>
              <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('批量操作')">批量操作</button>
              <button v-if="canManage" class="danger" @click="removeCourse(course.id)">删除</button>
            </div>
          </article>
          <EmptyState v-if="!courses.length" title="暂无课程" description="教师或管理员创建课程后会显示在这里。" />
        </div>
      </section>
    </template>
  </section>
</template>
