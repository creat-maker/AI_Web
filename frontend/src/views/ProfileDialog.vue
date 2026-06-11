<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

interface ExtractedDimension {
  key: string;
  label: string;
  value: string | string[];
  isNew: boolean;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
}

const DIMENSION_LABELS: Record<string, string> = {
  current_level: '当前水平',
  learning_goal: '学习目标',
  weak_points: '薄弱知识点',
  learning_preference: '学习偏好',
  diagnosis: '学习诊断',
  strategy: '学习策略',
};

const courses = ref<Course[]>([]);
const loading = ref(false);
const error = ref('');
const userMessage = ref('');
const messages = ref<ChatMessage[]>([]);
const chatListEl = ref<HTMLElement | null>(null);

const sessionId = ref('');
const extracted = ref<Record<string, unknown>>({});
const ready = ref(false);
const completed = ref(false);
const profile = ref<Record<string, unknown> | null>(null);

const selectedCourseId = ref(0);
const studentName = ref('');
const started = ref(false);
const saving = ref(false);
const savedProfileId = ref<number | null>(null);
const { demoUserId, setDemoUserId } = useRole();
const demoUsers = [
  { id: 'demo-basic', label: '张三 · 基础薄弱型', name: '张三' },
  { id: 'demo-advanced', label: '李四 · 进阶提升型', name: '李四' },
  { id: 'demo-exam', label: '王五 · 考试冲刺型', name: '王五' }
];

function switchDemoUser(userId: string) {
  setDemoUserId(userId);
  const user = demoUsers.find((item) => item.id === userId);
  if (user && !started.value) studentName.value = user.name;
}

function getExtractedDimensions(): ExtractedDimension[] {
  return Object.entries(extracted.value).map(([key, value]) => ({
    key,
    label: DIMENSION_LABELS[key] || key,
    value: value as string | string[],
    isNew: false,
  }));
}

function getFilledCount(): number {
  return Object.keys(extracted.value).length;
}

function getProgressPercent(): number {
  return Math.round((getFilledCount() / 6) * 100);
}

async function scrollToBottom() {
  await nextTick();
  if (chatListEl.value) {
    chatListEl.value.scrollTop = chatListEl.value.scrollHeight;
  }
}

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
    const result = await api.post<{
      session_id: string;
      reply: string;
      extracted: Record<string, unknown>;
      ready: boolean;
      completed: boolean;
    }>('/api/v1/profile-dialog/start', {
      student_name: studentName.value.trim(),
      course_id: selectedCourseId.value,
    });
    sessionId.value = result.session_id;
    extracted.value = result.extracted || {};
    ready.value = result.ready || false;
    completed.value = result.completed || false;
    messages.value = [{ role: 'assistant', text: result.reply }];
    started.value = true;
    scrollToBottom();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '启动对话失败';
  } finally {
    loading.value = false;
  }
}

async function sendMessage() {
  if (!userMessage.value.trim() || !sessionId.value) return;
  const text = userMessage.value.trim();
  userMessage.value = '';
  messages.value.push({ role: 'user', text });
  scrollToBottom();

  loading.value = true;
  error.value = '';
  try {
    const result = await api.post<{
      reply: string;
      extracted: Record<string, unknown>;
      new_extracted: Record<string, unknown>;
      ready: boolean;
      completed: boolean;
      profile: Record<string, unknown> | null;
    }>('/api/v1/profile-dialog/continue', {
      session_id: sessionId.value,
      message: text,
    });
    extracted.value = result.extracted || {};
    ready.value = result.ready || false;
    completed.value = result.completed || false;
    if (result.profile) {
      profile.value = result.profile;
    }
    messages.value.push({ role: 'assistant', text: result.reply });
    scrollToBottom();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发送消息失败';
  } finally {
    loading.value = false;
  }
}

async function finishDialog() {
  if (!sessionId.value) return;
  loading.value = true;
  error.value = '';
  try {
    const result = await api.post<{
      completed: boolean;
      profile: Record<string, unknown>;
    }>('/api/v1/profile-dialog/finish', {
      session_id: sessionId.value,
    });
    completed.value = result.completed;
    if (result.profile) {
      profile.value = result.profile;
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '完成画像失败';
  } finally {
    loading.value = false;
  }
}

async function saveProfile() {
  if (!sessionId.value) return;
  saving.value = true;
  error.value = '';
  try {
    const result = await api.post<{ id: number }>('/api/v1/profile-dialog/save', {
      session_id: sessionId.value,
      user_id: demoUserId.value,
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
    <PageHeader title="对话式画像构建" description="通过自然对话，智能抽取你的学习画像，获得个性化学习内容。">
      <template #actions>
        <select :value="demoUserId" @change="switchDemoUser(($event.target as HTMLSelectElement).value)">
          <option v-for="user in demoUsers" :key="user.id" :value="user.id">{{ user.label }}</option>
        </select>
        <RouterLink class="btn secondary" to="/profiles">返回画像列表</RouterLink>
      </template>
    </PageHeader>

    <!-- 启动面板 -->
    <div v-if="!started" class="start-panel">
      <DataCard title="开始画像构建" subtitle="选择课程并输入姓名，AI 将通过对话了解你的学习情况">
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

    <!-- 对话主界面 -->
    <div v-else class="dialog-layout">
      <!-- 左侧：对话面板 -->
      <div class="dialog-main">
        <DataCard title="对话面板">
          <template #subtitle>
            <span class="subtitle-hint">自由聊天，AI 会自动从对话中抽取画像信息</span>
          </template>
          <div ref="chatListEl" class="chat-list">
            <div v-for="(msg, index) in messages" :key="index" :class="['chat-bubble', msg.role]">
              {{ msg.text }}
            </div>
            <div v-if="loading" class="chat-bubble assistant typing">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>

          <!-- 输入区 -->
          <div v-if="!completed" class="chat-input">
            <input
              v-model="userMessage"
              placeholder="输入你的回答..."
              :disabled="loading"
              @keyup.enter="sendMessage"
            />
            <button class="btn-send" :disabled="!userMessage.trim() || loading" @click="sendMessage">发送</button>
            <button v-if="ready" class="btn-finish" :disabled="loading" @click="finishDialog">完成画像</button>
          </div>

          <!-- 完成面板 -->
          <div v-else class="complete-panel">
            <div class="complete-badge">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/><path d="M6 10l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              画像构建完成
            </div>
            <div class="complete-actions">
              <button v-if="!savedProfileId" :disabled="saving" class="btn-save" @click="saveProfile">
                {{ saving ? '正在保存...' : '保存画像到数据库' }}
              </button>
              <span v-else class="saved-hint">画像已保存（ID: {{ savedProfileId }}）</span>
            </div>
          </div>
        </DataCard>
      </div>

      <!-- 右侧：画像维度面板 -->
      <aside class="dialog-side">
        <!-- 进度 -->
        <DataCard title="抽取进度" subtitle="AI 正在从对话中了解你的学习情况">
          <div class="progress-wrap">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getProgressPercent() + '%' }"></div>
            </div>
            <span class="progress-text">{{ getFilledCount() }} / 6 个维度</span>
          </div>
          <div class="dimension-checklist">
            <div v-for="dim in [
              { key: 'current_level', label: '当前水平' },
              { key: 'learning_goal', label: '学习目标' },
              { key: 'weak_points', label: '薄弱知识点' },
              { key: 'learning_preference', label: '学习偏好' },
              { key: 'diagnosis', label: '学习诊断' },
              { key: 'strategy', label: '学习策略' },
            ]" :key="dim.key" :class="['dim-item', { filled: dim.key in extracted }]">
              <span class="dim-check">{{ dim.key in extracted ? '✓' : '○' }}</span>
              <span class="dim-label">{{ dim.label }}</span>
              <span v-if="dim.key in extracted" class="dim-value">
                {{ Array.isArray(extracted[dim.key]) ? (extracted[dim.key] as string[]).join('、') : extracted[dim.key] }}
              </span>
            </div>
          </div>
        </DataCard>

        <!-- 完整画像结果 -->
        <DataCard v-if="completed && profile" title="完整画像" subtitle="6 维画像结果">
          <div class="profile-result">
            <div v-for="(value, key) in profile" :key="String(key)" class="profile-item">
              <strong>{{ DIMENSION_LABELS[String(key)] || key }}</strong>
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
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 16px;
  align-items: start;
}

.subtitle-hint {
  font-size: 12px;
  color: var(--text-muted);
}

/* Chat */
.chat-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 460px;
  overflow-y: auto;
  padding: 8px 0;
}

.chat-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  max-width: 85%;
  word-break: break-word;
}

.chat-bubble.assistant {
  background: var(--bg-card);
  border: 1px solid var(--color-border);
  align-self: flex-start;
}

.chat-bubble.user {
  color: var(--text-light);
  background: var(--color-primary);
  align-self: flex-end;
}

.chat-bubble.typing {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 12px 18px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: blink 1.2s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}

.chat-input {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.chat-input input {
  flex: 1;
}

.btn-send {
  white-space: nowrap;
}

.btn-finish {
  white-space: nowrap;
  background: var(--status-success-solid);
  color: var(--text-light);
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-finish:hover { opacity: 0.9; }
.btn-finish:disabled { opacity: 0.5; cursor: not-allowed; }

/* Complete */
.complete-panel {
  margin-top: 12px;
  text-align: center;
}

.complete-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--status-success-solid);
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 12px;
}

.complete-actions {
  display: flex;
  justify-content: center;
}

.btn-save {
  background: var(--color-primary);
  color: var(--text-light);
  border: none;
  border-radius: 6px;
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-save:hover { opacity: 0.9; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.saved-hint {
  color: var(--status-success-solid);
  font-size: 13px;
}

/* Progress */
.progress-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-neutral);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}

.dimension-checklist {
  display: grid;
  gap: 8px;
}

.dim-item {
  display: grid;
  grid-template-columns: 20px 80px minmax(0, 1fr);
  gap: 6px;
  align-items: baseline;
  font-size: 13px;
  padding: 4px 0;
  border-bottom: 1px solid var(--border-soft);
}

.dim-item:last-child { border-bottom: none; }

.dim-item.filled .dim-check { color: var(--status-success-solid); }
.dim-item.filled .dim-label { color: var(--text-main); }
.dim-item:not(.filled) .dim-check { color: var(--text-muted); }
.dim-item:not(.filled) .dim-label { color: var(--text-muted); }

.dim-check { font-size: 12px; }
.dim-label { font-weight: 500; }

.dim-value {
  color: var(--color-text-sub);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Profile result */
.profile-result {
  display: grid;
  gap: 10px;
}

.profile-item {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr);
  gap: 8px;
  align-items: baseline;
  font-size: 13px;
}

.profile-item strong {
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
