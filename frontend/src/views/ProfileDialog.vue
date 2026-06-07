<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import type { Course } from '../types';

interface DialogState {
  session_id: string;
  dimension: string;
  dimension_label: string;
  question: string;
  reply: string;
  progress: { current: number; total: number };
  completed: boolean;
  profile: Record<string, unknown> | null;
  extracted_so_far: Record<string, unknown>;
}

const courses = ref<Course[]>([]);
const loading = ref(false);
const error = ref('');
const userMessage = ref('');
const messages = ref<Array<{ role: 'user' | 'assistant'; text: string }>>([]);

const dialogState = reactive<DialogState>({
  session_id: '',
  dimension: '',
  dimension_label: '',
  question: '',
  reply: '',
  progress: { current: 0, total: 6 },
  completed: false,
  profile: null,
  extracted_so_far: {}
});

const selectedCourseId = ref(0);
const studentName = ref('');
const started = ref(false);
const saving = ref(false);
const savedProfileId = ref<number | null>(null);

async function loadCourses() {
  try {
    courses.value = await api.get<Course[]>('/api/v1/courses');
    if (courses.value.length) {
      selectedCourseId.value = courses.value[0].id;
    }
  } catch {
    error.value = '课程列表加载失败，请确认后端已启动。';
  }
}

async function startDialog() {
  if (!selectedCourseId.value || !studentName.value.trim()) {
    error.value = '请选择课程并输入学生姓名';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const result = await api.post<DialogState>('/api/v1/profile-dialog/start', {
      student_name: studentName.value.trim(),
      course_id: selectedCourseId.value
    });
    Object.assign(dialogState, result);
    messages.value = [{ role: 'assistant', text: result.question }];
    started.value = true;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '启动对话失败';
  } finally {
    loading.value = false;
  }
}

async function sendMessage() {
  if (!userMessage.value.trim() || !dialogState.session_id) return;
  const text = userMessage.value.trim();
  userMessage.value = '';
  messages.value.push({ role: 'user', text });

  loading.value = true;
  error.value = '';
  try {
    const result = await api.post<DialogState>('/api/v1/profile-dialog/continue', {
      session_id: dialogState.session_id,
      message: text
    });
    Object.assign(dialogState, result);
    if (result.reply) {
      messages.value.push({ role: 'assistant', text: result.reply });
    }
    if (!result.completed && result.question) {
      messages.value.push({ role: 'assistant', text: result.question });
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发送消息失败';
  } finally {
    loading.value = false;
  }
}

async function saveProfile() {
  if (!dialogState.session_id) return;
  saving.value = true;
  error.value = '';
  try {
    const result = await api.post<{ id: number }>('/api/v1/profile-dialog/save', {
      session_id: dialogState.session_id
    });
    savedProfileId.value = result.id;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存画像失败';
  } finally {
    saving.value = false;
  }
}

onMounted(loadCourses);
</script>

<template>
  <section class="page profile-dialog-page">
    <PageHeader title="对话式画像构建" description="通过多轮对话，智能抽取学生 6 维画像。">
      <template #actions>
        <RouterLink class="btn secondary" to="/profiles">返回画像列表</RouterLink>
      </template>
    </PageHeader>

    <div v-if="!started" class="start-panel">
      <DataCard title="开始画像构建" subtitle="选择课程并输入学生姓名">
        <div class="form-group">
          <label>课程</label>
          <select v-model="selectedCourseId">
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
          <p v-if="!courses.length" class="muted">暂无课程，请先在课程管理中创建。</p>
        </div>
        <div class="form-group">
          <label>学生姓名</label>
          <input v-model="studentName" placeholder="请输入学生姓名" @keyup.enter="startDialog" />
        </div>
        <button :disabled="!selectedCourseId || !studentName.trim() || loading" @click="startDialog">
          {{ loading ? '正在启动...' : '开始对话' }}
        </button>
      </DataCard>
    </div>

    <div v-else class="dialog-layout">
      <div class="dialog-main">
        <DataCard title="对话面板" :subtitle="`当前维度：${dialogState.dimension_label}`">
          <div class="progress-bar-wrap">
            <ProgressBar :value="Math.round((dialogState.progress.current / dialogState.progress.total) * 100)" />
            <span class="progress-text">{{ dialogState.progress.current }} / {{ dialogState.progress.total }}</span>
          </div>
          <div class="chat-list">
            <div v-for="(msg, index) in messages" :key="index" :class="['chat-bubble', msg.role]">
              {{ msg.text }}
            </div>
            <p v-if="loading" class="muted">AI 正在思考...</p>
          </div>
          <div v-if="!dialogState.completed" class="chat-input">
            <input
              v-model="userMessage"
              placeholder="输入你的回答..."
              :disabled="loading"
              @keyup.enter="sendMessage"
            />
            <button :disabled="!userMessage.trim() || loading" @click="sendMessage">发送</button>
          </div>
          <div v-else class="complete-panel">
            <p class="success-text">画像构建完成！</p>
            <button v-if="!savedProfileId" :disabled="saving" @click="saveProfile">
              {{ saving ? '正在保存...' : '保存画像到数据库' }}
            </button>
            <p v-else class="muted">画像已保存（ID: {{ savedProfileId }}）</p>
          </div>
        </DataCard>
      </div>

      <aside class="dialog-side">
        <DataCard title="已抽取信息" subtitle="实时更新的画像维度">
          <div v-if="Object.keys(dialogState.extracted_so_far).length" class="extracted-list">
            <div v-for="(value, key) in dialogState.extracted_so_far" :key="String(key)" class="extracted-item">
              <strong>{{ key }}</strong>
              <span>{{ Array.isArray(value) ? value.join('、') : value }}</span>
            </div>
          </div>
          <p v-else class="muted">对话开始后将实时显示抽取结果。</p>
        </DataCard>

        <DataCard v-if="dialogState.completed && dialogState.profile" title="完整画像" subtitle="6 维画像结果">
          <div class="profile-result">
            <div v-for="(value, key) in (dialogState.profile as Record<string, unknown>)" :key="String(key)" class="extracted-item">
              <strong>{{ key }}</strong>
              <span>{{ Array.isArray(value) ? value.join('、') : value }}</span>
            </div>
          </div>
        </DataCard>
      </aside>
    </div>

    <p v-if="error" class="panel muted error-text">{{ error }}</p>
  </section>
</template>

<style scoped>
.start-panel {
  max-width: 480px;
  margin: 0 auto;
}

.form-group {
  display: grid;
  gap: 6px;
  margin-bottom: 14px;
}

.form-group label {
  font-weight: 600;
  font-size: 13px;
}

.dialog-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 16px;
  align-items: start;
}

.progress-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.progress-text {
  font-size: 13px;
  color: var(--color-text-sub);
  white-space: nowrap;
}

.chat-list {
  display: grid;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
  padding: 8px 0;
}

.chat-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  max-width: 85%;
}

.chat-bubble.assistant {
  background: var(--bg-card);
  border: 1px solid var(--color-border);
  justify-self: start;
}

.chat-bubble.user {
  margin-left: auto;
  color: var(--text-light);
  background: var(--color-primary);
  justify-self: end;
}

.chat-input {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  margin-top: 12px;
}

.complete-panel {
  margin-top: 12px;
  text-align: center;
}

.success-text {
  color: var(--color-success);
  font-weight: 600;
  margin-bottom: 10px;
}

.extracted-list,
.profile-result {
  display: grid;
  gap: 10px;
}

.extracted-item {
  display: grid;
  grid-template-columns: 100px minmax(0, 1fr);
  gap: 8px;
  align-items: baseline;
  font-size: 13px;
}

.extracted-item strong {
  color: var(--color-text-sub);
  font-size: 12px;
}

.error-text {
  color: var(--color-error, #e53e3e);
}

@media (max-width: 820px) {
  .dialog-layout {
    grid-template-columns: 1fr;
  }
}
</style>
