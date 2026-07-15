<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import StatusBadge from '../components/StatusBadge.vue';
import type { Course } from '../types';

interface CourseForm {
  title: string;
  course_code: string;
  teacher_name: string;
  description: string;
  chapter_count: number;
  status: string;
  tagsText: string;
  subject: string;
}

const courses = ref<Course[]>([]);
const loading = ref(false);
const saving = ref(false);
const error = ref('');
const success = ref('');
const showCreate = ref(false);
const keyword = ref('');
const statusFilter = ref('全部状态');

const form = reactive<CourseForm>({
  title: '',
  course_code: '',
  teacher_name: '王老师',
  description: '',
  chapter_count: 8,
  status: '启用',
  tagsText: 'Python, 循环结构',
  subject: '计算机'
});

const enrichedCourses = computed(() =>
  courses.value.map((course) => {
    const text = `${course.title || ''}\n${course.description || ''}`;
    const status = text.includes('状态：草稿') ? '草稿' : '启用';
    const courseCode = text.match(/课程编号：(.+)/)?.[1]?.trim() || `PY-${String(course.id).padStart(3, '0')}`;
    const chapterCount = text.match(/章节数：(\d+)/)?.[1] || '8';
    const tags = text.match(/知识点：(.+)/)?.[1]?.split(/[、,，]/).map((item) => item.trim()).filter(Boolean) || ['Python', '循环结构'];
    return {
      ...course,
      status,
      courseCode,
      chapterCount,
      tags
    };
  })
);

const filteredCourses = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return enrichedCourses.value.filter((course) => {
    const haystack = [
      course.title,
      course.subject,
      course.teacher_name,
      course.description,
      course.status,
      course.courseCode,
      course.tags.join(' ')
    ]
      .join(' ')
      .toLowerCase();
    const matchWord = !word || haystack.includes(word);
    const matchStatus = statusFilter.value === '全部状态' || course.status === statusFilter.value;
    return matchWord && matchStatus;
  });
});

const stats = computed(() => {
  const total = enrichedCourses.value.length;
  return [
    { label: '课程总数', value: total, hint: '来自课程接口' },
    { label: '启用课程', value: enrichedCourses.value.filter((item) => item.status === '启用').length, hint: '可被资源中心选择' },
    { label: '知识点标签', value: new Set(enrichedCourses.value.flatMap((item) => item.tags)).size, hint: '参与搜索过滤' },
    { label: '搜索结果', value: filteredCourses.value.length, hint: '当前筛选命中' }
  ];
});

function resetForm() {
  form.title = '';
  form.course_code = '';
  form.teacher_name = '王老师';
  form.description = '';
  form.chapter_count = 8;
  form.status = '启用';
  form.tagsText = 'Python, 循环结构';
  form.subject = '计算机';
}

async function loadCourses() {
  loading.value = true;
  error.value = '';
  try {
    courses.value = await api.get<Course[]>('/api/v1/courses');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程列表加载失败。';
  } finally {
    loading.value = false;
  }
}

async function createCourse() {
  success.value = '';
  error.value = '';
  if (!form.title.trim() || !form.course_code.trim() || !form.teacher_name.trim()) {
    error.value = '请填写课程名称、课程编号和授课教师。';
    return;
  }
  saving.value = true;
  try {
    const tags = form.tagsText
      .split(/[、,，]/)
      .map((item) => item.trim())
      .filter(Boolean);
    await api.post<Course>('/api/v1/courses', {
      title: form.title.trim(),
      course_code: form.course_code.trim(),
      teacher_name: form.teacher_name.trim(),
      description: form.description.trim(),
      chapter_count: Number(form.chapter_count) || 1,
      status: form.status,
      tags,
      subject: form.subject.trim() || '计算机'
    });
    success.value = '课程已创建，列表已刷新。';
    showCreate.value = false;
    resetForm();
    await loadCourses();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程创建失败。';
  } finally {
    saving.value = false;
  }
}

function clearSearch() {
  keyword.value = '';
  statusFilter.value = '全部状态';
}

onMounted(loadCourses);
</script>

<template>
  <section class="page course-page">
    <PageHeader title="课程管理" description="创建课程、维护基础信息，并将课程同步到资源生成和学习资源链路。">
      <template #actions>
        <RouterLink class="btn secondary" to="/teacher">返回教师首页</RouterLink>
        <button type="button" @click="showCreate = true">新建课程</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="success" class="panel success-text">{{ success }}</p>
    <p v-if="loading" class="panel muted">正在加载课程...</p>

    <div class="stat-grid">
      <article v-for="item in stats" :key="item.label" class="stat-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.hint }}</small>
      </article>
    </div>

    <DataCard title="搜索课程" subtitle="按课程名称、编号、教师、状态、学科、描述和知识点标签过滤">
      <form class="filter-grid" @submit.prevent>
        <input v-model="keyword" placeholder="搜索课程、教师、编号或知识点，例如：循环" @keyup.enter.prevent />
        <select v-model="statusFilter">
          <option>全部状态</option>
          <option>启用</option>
          <option>草稿</option>
        </select>
        <button class="secondary" type="button" @click="clearSearch">清空</button>
      </form>
    </DataCard>

    <DataCard title="课程列表" :subtitle="`${filteredCourses.length} 门课程`">
      <div v-if="filteredCourses.length" class="course-grid">
        <article v-for="course in filteredCourses" :key="course.id" class="course-card">
          <div class="course-main">
            <span class="course-icon">{{ course.title.slice(0, 1) }}</span>
            <div>
              <strong>{{ course.title }}</strong>
              <p>{{ course.courseCode }} / {{ course.teacher_name || '未设置教师' }} / {{ course.subject || '未设置学科' }}</p>
              <p class="desc">{{ course.description || '该课程暂无简介，可在后续编辑中补充课程目标和章节安排。' }}</p>
              <div class="tag-row">
                <span v-for="tag in course.tags" :key="tag">{{ tag }}</span>
              </div>
            </div>
          </div>
          <div class="course-side">
            <StatusBadge :label="course.status" :tone="course.status === '启用' ? 'success' : 'warning'" />
            <span>{{ course.chapterCount }} 章</span>
            <RouterLink class="btn ghost" :to="`/teacher/resource-generation?course_id=${course.id}`">生成资源</RouterLink>
          </div>
        </article>
      </div>
      <EmptyState v-else title="未找到相关课程" description="请更换关键词，或清空搜索条件后查看全部课程。" />
    </DataCard>

    <div v-if="showCreate" class="modal-mask" @click.self="showCreate = false">
      <form class="modal-card" @submit.prevent="createCourse">
        <header>
          <div>
            <h2>新建课程</h2>
            <p>提交后写入后端课程接口，刷新页面后仍可查看。</p>
          </div>
          <button class="ghost" type="button" @click="showCreate = false">关闭</button>
        </header>
        <div class="form-grid">
          <label>课程名称<input v-model="form.title" placeholder="例如：Python 程序设计" /></label>
          <label>课程编号<input v-model="form.course_code" placeholder="例如：PY-2026-01" /></label>
          <label>授课教师<input v-model="form.teacher_name" placeholder="例如：王老师" /></label>
          <label>章节数<input v-model.number="form.chapter_count" min="1" type="number" /></label>
          <label>状态
            <select v-model="form.status">
              <option>启用</option>
              <option>草稿</option>
            </select>
          </label>
          <label>学科<input v-model="form.subject" placeholder="例如：计算机" /></label>
          <label class="wide">知识点标签<input v-model="form.tagsText" placeholder="用逗号分隔，例如：Python, 循环结构, while" /></label>
          <label class="wide">课程简介<textarea v-model="form.description" placeholder="输入课程目标、适用学生和章节重点"></textarea></label>
        </div>
        <footer>
          <button class="secondary" type="button" @click="showCreate = false">取消</button>
          <button :disabled="saving" type="submit">{{ saving ? '正在保存...' : '提交课程' }}</button>
        </footer>
      </form>
    </div>
  </section>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 16px;
  background: #fff;
}

.stat-card span,
.stat-card small {
  color: var(--text-secondary);
}

.stat-card strong {
  display: block;
  margin: 8px 0;
  color: var(--text-main);
  font-size: 28px;
}

.filter-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 160px 120px;
  gap: 12px;
}

.course-grid {
  display: grid;
  gap: 12px;
}

.course-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px;
  gap: 16px;
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 16px;
  background: #fff;
}

.course-main {
  display: flex;
  gap: 12px;
}

.course-icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: #fff;
  background: var(--color-primary);
  font-weight: 900;
}

.course-card p {
  margin: 6px 0 0;
  color: var(--text-secondary);
}

.desc {
  line-height: 1.6;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag-row span {
  border-radius: 999px;
  padding: 5px 9px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-size: 12px;
  font-weight: 800;
}

.course-side {
  display: grid;
  justify-items: end;
  align-content: start;
  gap: 10px;
}

.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.42);
}

.modal-card {
  width: min(760px, 100%);
  border-radius: 18px;
  padding: 22px;
  background: #fff;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.25);
}

.modal-card header,
.modal-card footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.modal-card h2,
.modal-card p {
  margin: 0;
}

.modal-card p {
  color: var(--text-secondary);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 18px 0;
}

.form-grid label {
  display: grid;
  gap: 7px;
  color: var(--text-secondary);
  font-weight: 800;
}

.form-grid .wide {
  grid-column: 1 / -1;
}

textarea {
  min-height: 96px;
  resize: vertical;
}

.error-text {
  color: #b91c1c;
}

.success-text {
  color: #047857;
}

@media (max-width: 860px) {
  .stat-grid,
  .filter-grid,
  .course-card,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .course-side {
    justify-items: start;
  }
}
</style>
