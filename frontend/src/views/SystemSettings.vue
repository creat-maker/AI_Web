<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface SettingsSnapshot {
  overview?: {
    system_mode?: string;
    model_mode?: string;
    knowledge_base_status?: string;
    last_updated?: string;
  };
  model_config?: {
    llm_provider?: string;
    model_name?: string;
    api_key_status?: string;
    stream_enabled?: boolean;
  };
}

const settings = ref<SettingsSnapshot>({});
const loading = ref(true);
const error = ref('');
const message = ref('');

const basic = ref({
  platform: 'EduMind Studio',
  language: '简体中文',
  defaultRole: '学生'
});

const ai = ref({
  modelStatus: '运行正常',
  limit: 5000,
  generateEnabled: true,
  provider: 'Mock / 可切换'
});

const security = ref({
  loginPolicy: '账号密码 + 角色权限',
  passwordPolicy: '8 位以上，包含数字和字母',
  auditEnabled: true
});

const notification = ref({
  email: true,
  inbox: true,
  system: true
});

const backup = ref({
  cycle: '每日 02:00',
  last: '2024-05-31 02:00',
  status: '正常'
});

async function loadSettings() {
  loading.value = true;
  error.value = '';
  try {
    settings.value = await api.get<SettingsSnapshot>('/api/v1/settings');
    ai.value.provider = settings.value.model_config?.llm_provider || ai.value.provider;
    ai.value.modelStatus = settings.value.model_config?.api_key_status || ai.value.modelStatus;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '系统设置接口暂不可用，当前显示本地演示配置。';
  } finally {
    loading.value = false;
  }
}

function saveSettings() {
  message.value = '配置已在页面暂存。真实保存接口可继续沿用后端 /api/v1/settings 扩展。';
}

function resetSettings() {
  basic.value = { platform: 'EduMind Studio', language: '简体中文', defaultRole: '学生' };
  ai.value = { modelStatus: '运行正常', limit: 5000, generateEnabled: true, provider: 'Mock / 可切换' };
  security.value = { loginPolicy: '账号密码 + 角色权限', passwordPolicy: '8 位以上，包含数字和字母', auditEnabled: true };
  notification.value = { email: true, inbox: true, system: true };
  backup.value = { cycle: '每日 02:00', last: '2024-05-31 02:00', status: '正常' };
  message.value = '已恢复默认演示配置。';
}

onMounted(loadSettings);
</script>

<template>
  <section class="page">
    <PageHeader title="系统设置" description="配置平台基础信息、AI 服务、安全策略、通知和数据备份。">
      <template #actions>
        <button @click="saveSettings">保存设置</button>
        <button class="secondary" @click="resetSettings">重置</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载系统设置...</p>
    <p v-if="error" class="demo-banner">{{ error }}</p>
    <p v-if="message" class="panel muted">{{ message }}</p>

    <div class="stat-grid">
      <StatCard label="平台模式" :value="settings.overview?.system_mode || '本地演示'" icon="模" />
      <StatCard label="AI 服务" :value="ai.modelStatus" icon="AI" tone="green" />
      <StatCard label="知识库状态" :value="settings.overview?.knowledge_base_status || '可用'" icon="知" tone="purple" />
      <StatCard label="备份状态" :value="backup.status" icon="备" tone="cyan" />
    </div>

    <div class="settings-grid">
      <DataCard title="基础设置" subtitle="平台名称、默认语言和默认角色">
        <div class="form-grid">
          <label>平台名称<input v-model="basic.platform" /></label>
          <label>默认语言<select v-model="basic.language"><option>简体中文</option><option>English</option></select></label>
          <label>默认角色<select v-model="basic.defaultRole"><option>学生</option><option>教师</option><option>管理员</option></select></label>
        </div>
      </DataCard>

      <DataCard title="AI 服务设置" subtitle="模型服务状态、调用限制和生成开关">
        <div class="form-grid">
          <label>模型服务<input v-model="ai.provider" /></label>
          <label>每日调用限制<input v-model.number="ai.limit" type="number" /></label>
          <label class="toggle-row"><input v-model="ai.generateEnabled" type="checkbox" /> 启用 AI 生成</label>
          <div class="setting-status"><StatusBadge :label="ai.modelStatus" tone="success" /></div>
        </div>
      </DataCard>

      <DataCard title="安全设置" subtitle="登录策略、密码策略和审计开关">
        <div class="form-grid">
          <label>登录策略<input v-model="security.loginPolicy" /></label>
          <label>密码策略<input v-model="security.passwordPolicy" /></label>
          <label class="toggle-row"><input v-model="security.auditEnabled" type="checkbox" /> 开启审计日志</label>
        </div>
      </DataCard>

      <DataCard title="通知设置" subtitle="邮件、站内信和系统通知">
        <div class="switch-list">
          <label class="toggle-row"><input v-model="notification.email" type="checkbox" /> 邮件通知</label>
          <label class="toggle-row"><input v-model="notification.inbox" type="checkbox" /> 站内信通知</label>
          <label class="toggle-row"><input v-model="notification.system" type="checkbox" /> 系统通知</label>
        </div>
      </DataCard>

      <DataCard title="数据备份设置" subtitle="备份周期、最近备份时间和恢复入口">
        <div class="backup-card">
          <label>备份周期<input v-model="backup.cycle" /></label>
          <label>最近备份<input v-model="backup.last" /></label>
          <div class="row-actions">
            <button class="secondary">立即备份</button>
            <button class="ghost">恢复数据</button>
          </div>
        </div>
      </DataCard>

      <DataCard title="治理说明" subtitle="平台能力边界">
        <div class="list">
          <div class="item compact"><strong>接口路径</strong><StatusBadge label="/api/v1/settings" tone="info" /></div>
          <div class="item compact"><strong>敏感信息</strong><StatusBadge label="前端不展示 Key" tone="success" /></div>
          <div class="item compact"><strong>审计策略</strong><StatusBadge label="已开启" tone="purple" /></div>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
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

.switch-list,
.backup-card {
  display: grid;
  gap: 12px;
}

.setting-status {
  align-self: center;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

@media (max-width: 980px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
