<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';

interface SettingsSnapshot {
  overview: {
    system_mode: string;
    model_mode: string;
    knowledge_base_status: string;
    last_updated: string;
  };
  model_config: {
    llm_provider: string;
    model_name: string;
    temperature: number;
    max_tokens: number;
    stream_enabled: boolean;
    api_key_status: string;
  };
  rag_config: {
    chunk_size: number;
    chunk_overlap: number;
    top_k: number;
    similarity_threshold: number;
    vector_store_type: string;
    persist_dir: string;
  };
  teaching_strategy: {
    answer_mode: string;
    show_citations: boolean;
    record_qa_logs: boolean;
    generate_learning_suggestions: boolean;
    generate_reports: boolean;
  };
  security: {
    api_key_visible: boolean;
    upload_size_tip: string;
    local_dev_tip: string;
    database_path: string;
    vector_store_path: string;
  };
  runtime?: {
    llm_mode?: string;
    mock_mode?: boolean;
    parsed_document_count?: number;
    report_count?: number;
    qa_count?: number;
  };
}

interface TestResult {
  status: string;
  message: string;
  checks: Array<{ name: string; status: string; detail: string }>;
}

const defaultSnapshot: SettingsSnapshot = {
  overview: {
    system_mode: '本地开发模式',
    model_mode: 'Mock',
    knowledge_base_status: '等待构建',
    last_updated: new Date().toISOString()
  },
  model_config: {
    llm_provider: 'mock',
    model_name: 'mock-llm',
    temperature: 0.7,
    max_tokens: 2048,
    stream_enabled: false,
    api_key_status: '未配置'
  },
  rag_config: {
    chunk_size: 800,
    chunk_overlap: 120,
    top_k: 5,
    similarity_threshold: 0.2,
    vector_store_type: 'fallback JSON',
    persist_dir: './backend/storage/chroma'
  },
  teaching_strategy: {
    answer_mode: '严谨',
    show_citations: true,
    record_qa_logs: true,
    generate_learning_suggestions: true,
    generate_reports: true
  },
  security: {
    api_key_visible: false,
    upload_size_tip: '建议单个教学资料控制在 20MB 内，便于本地解析和演示。',
    local_dev_tip: '当前为本地开发展示配置，保存按钮不会写入真实密钥或系统环境变量。',
    database_path: './backend/storage/eduagent.sqlite3',
    vector_store_path: './backend/storage/chroma'
  }
};

const settings = ref<SettingsSnapshot>(structuredClone(defaultSnapshot));
const loading = ref(true);
const testing = ref(false);
const error = ref('');
const fallbackActive = ref(false);
const saveMessage = ref('');
const testResult = ref<TestResult | null>(null);

const overviewCards = computed(() => [
  { label: '系统运行模式', value: settings.value.overview.system_mode },
  { label: '当前模型模式', value: settings.value.overview.model_mode },
  { label: '知识库状态', value: settings.value.overview.knowledge_base_status },
  { label: '最后更新时间', value: formatDate(settings.value.overview.last_updated) }
]);

function cloneDefault() {
  return structuredClone(defaultSnapshot);
}

function formatDate(value?: string) {
  if (!value) return '暂无时间';
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function loadSettings() {
  loading.value = true;
  error.value = '';
  fallbackActive.value = false;
  try {
    settings.value = await api.get<SettingsSnapshot>('/api/v1/settings');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '系统设置加载失败';
    fallbackActive.value = true;
    settings.value = cloneDefault();
  } finally {
    loading.value = false;
  }
}

function saveSettings() {
  settings.value.overview.last_updated = new Date().toISOString();
  saveMessage.value = '配置已在当前页面暂存。后端暂未持久化敏感配置，也不会写入系统环境变量。';
  error.value = '';
}

function restoreDefaults() {
  settings.value = cloneDefault();
  saveMessage.value = '已恢复页面默认展示配置。';
  testResult.value = null;
}

async function testConnection() {
  testing.value = true;
  saveMessage.value = '';
  error.value = '';
  try {
    testResult.value = await api.post<TestResult>('/api/v1/settings/test');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测试连接失败，已保留页面配置展示。';
  } finally {
    testing.value = false;
  }
}

onMounted(loadSettings);
</script>

<template>
  <section class="page settings-page">
    <div class="panel settings-hero">
      <div>
        <p class="eyebrow">系统设置与算法配置中心</p>
        <h2>EduMind 运行参数、模型配置与教学策略</h2>
        <p class="muted">用于比赛展示系统如何配置模型、RAG 知识库和教学策略。真实 API Key 不会在前端明文展示。</p>
      </div>
      <div class="hero-action">
        <span>API Key 状态</span>
        <strong>{{ settings.model_config.api_key_status }}</strong>
      </div>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="fallbackActive" class="panel muted">接口暂不可用，页面已使用本地 fallback 配置，避免白屏。</p>
    <p v-else-if="loading" class="panel muted">正在加载系统设置...</p>
    <p v-if="saveMessage" class="panel muted">{{ saveMessage }}</p>

    <div class="overview-grid">
      <article v-for="item in overviewCards" :key="item.label" class="stat overview-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </article>
    </div>

    <div class="settings-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>模型配置</h2>
          <span class="muted">LLM Provider / 模型参数</span>
        </div>
        <div class="config-grid">
          <label>
            LLM Provider
            <select v-model="settings.model_config.llm_provider">
              <option value="mock">mock</option>
              <option value="deepseek">deepseek</option>
              <option value="qwen">qwen</option>
              <option value="dashscope">dashscope</option>
            </select>
          </label>
          <label>
            模型名称
            <input v-model="settings.model_config.model_name" />
          </label>
          <label>
            Temperature
            <input v-model.number="settings.model_config.temperature" type="number" min="0" max="2" step="0.1" />
          </label>
          <label>
            Max Tokens
            <input v-model.number="settings.model_config.max_tokens" type="number" min="256" step="128" />
          </label>
          <label class="toggle-row">
            <input v-model="settings.model_config.stream_enabled" type="checkbox" />
            启用流式输出
          </label>
          <div class="readonly-card">
            <span>API Key 状态</span>
            <strong>{{ settings.model_config.api_key_status }}</strong>
            <small>只显示配置状态，不展示真实 key。</small>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>RAG 知识库配置</h2>
          <span class="muted">切片、召回和向量库</span>
        </div>
        <div class="config-grid">
          <label>
            Chunk Size
            <input v-model.number="settings.rag_config.chunk_size" type="number" min="100" step="50" />
          </label>
          <label>
            Chunk Overlap
            <input v-model.number="settings.rag_config.chunk_overlap" type="number" min="0" step="10" />
          </label>
          <label>
            Top K
            <input v-model.number="settings.rag_config.top_k" type="number" min="1" max="20" />
          </label>
          <label>
            相似度阈值
            <input v-model.number="settings.rag_config.similarity_threshold" type="number" min="0" max="1" step="0.05" />
          </label>
          <label>
            向量库类型
            <select v-model="settings.rag_config.vector_store_type">
              <option value="Chroma">Chroma</option>
              <option value="fallback JSON">fallback JSON</option>
            </select>
          </label>
          <div class="readonly-card">
            <span>向量库路径</span>
            <strong>{{ settings.rag_config.persist_dir }}</strong>
          </div>
        </div>
      </section>
    </div>

    <div class="settings-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>教学策略配置</h2>
          <span class="muted">答疑、日志、建议与报告</span>
        </div>
        <div class="strategy-grid">
          <label>
            答疑模式
            <select v-model="settings.teaching_strategy.answer_mode">
              <option value="严谨">严谨</option>
              <option value="启发">启发</option>
              <option value="简洁">简洁</option>
            </select>
          </label>
          <label class="toggle-row">
            <input v-model="settings.teaching_strategy.show_citations" type="checkbox" />
            显示引用来源
          </label>
          <label class="toggle-row">
            <input v-model="settings.teaching_strategy.record_qa_logs" type="checkbox" />
            记录问答日志
          </label>
          <label class="toggle-row">
            <input v-model="settings.teaching_strategy.generate_learning_suggestions" type="checkbox" />
            生成学情建议
          </label>
          <label class="toggle-row">
            <input v-model="settings.teaching_strategy.generate_reports" type="checkbox" />
            生成报告
          </label>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>系统安全提示</h2>
          <span class="muted">本地开发与敏感配置</span>
        </div>
        <div class="security-list">
          <article class="security-card">
            <strong>API Key 保护</strong>
            <p>不在前端展示真实 API Key，仅显示“已配置/未配置”。</p>
          </article>
          <article class="security-card">
            <strong>上传文件大小建议</strong>
            <p>{{ settings.security.upload_size_tip }}</p>
          </article>
          <article class="security-card">
            <strong>本地开发模式提醒</strong>
            <p>{{ settings.security.local_dev_tip }}</p>
          </article>
          <article class="security-card">
            <strong>数据库和向量库路径</strong>
            <p>数据库：{{ settings.security.database_path }}</p>
            <p>向量库：{{ settings.security.vector_store_path }}</p>
          </article>
        </div>
      </section>
    </div>

    <section class="panel">
      <div class="panel-title">
        <h2>配置操作</h2>
        <span class="muted">保存为页面暂存，测试连接调用后端脱敏检查</span>
      </div>
      <div class="action-row">
        <button type="button" @click="saveSettings">保存配置</button>
        <button class="secondary" type="button" @click="restoreDefaults">恢复默认</button>
        <button class="secondary" type="button" :disabled="testing" @click="testConnection">
          {{ testing ? '测试中...' : '测试连接' }}
        </button>
      </div>
      <div v-if="testResult" class="test-result">
        <strong>{{ testResult.message }}</strong>
        <div class="check-grid">
          <article v-for="item in testResult.checks" :key="item.name" class="check-card">
            <span :class="['status-pill', item.status]">{{ item.status }}</span>
            <strong>{{ item.name }}</strong>
            <p>{{ item.detail }}</p>
          </article>
        </div>
      </div>
    </section>
  </section>
</template>

<style scoped>
.settings-page {
  gap: 18px;
}

.settings-hero,
.panel-title {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.settings-hero {
  align-items: center;
}

.settings-hero h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2264d1;
  font-size: 13px;
  font-weight: 700;
}

.hero-action,
.readonly-card,
.security-card,
.check-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.hero-action {
  width: 260px;
  background: #f8fbff;
}

.hero-action span,
.overview-card span,
.readonly-card span,
.readonly-card small {
  display: block;
  color: #66758a;
}

.hero-action strong,
.readonly-card strong {
  display: block;
  margin-top: 6px;
  word-break: break-word;
}

.overview-grid,
.settings-layout,
.config-grid,
.strategy-grid,
.security-list,
.check-grid {
  display: grid;
  gap: 12px;
}

.overview-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.overview-card {
  min-height: 112px;
}

.overview-card strong {
  font-size: 20px;
}

.settings-layout {
  grid-template-columns: minmax(0, 1fr) minmax(320px, 1fr);
  gap: 16px;
}

.config-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  align-items: end;
}

.strategy-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.toggle-row {
  display: flex;
  gap: 8px;
  align-items: center;
  min-height: 42px;
}

.toggle-row input {
  width: auto;
}

.security-card p,
.check-card p {
  margin: 8px 0 0;
  color: #66758a;
  line-height: 1.55;
  word-break: break-word;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.test-result {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.check-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.status-pill {
  display: inline-block;
  width: fit-content;
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
  color: #1f7a45;
  background: #effaf4;
}

.status-pill.warning {
  color: #955600;
  background: #fff7e8;
}

.error-text {
  color: #b42318;
}

@media (max-width: 980px) {
  .settings-layout,
  .settings-hero,
  .panel-title {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-action {
    width: auto;
  }
}
</style>
