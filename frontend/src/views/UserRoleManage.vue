<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface AdminUser {
  id: string;
  name: string;
  account: string;
  role: string;
  org: string;
  status: string;
  level?: string;
  risk_level?: string;
  class_name?: string;
  last_login?: string;
}

interface RoleItem {
  role: string;
  label: string;
  count: number;
  permissions: string[];
}

const users = ref<AdminUser[]>([]);
const roles = ref<RoleItem[]>([]);
const loading = ref(false);
const error = ref('');
const success = ref('');
const keyword = ref('');
const roleFilter = ref('全部角色');
const statusFilter = ref('全部状态');

const filteredUsers = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return users.value.filter((user) => {
    const haystack = [user.name, user.account, user.role, user.org, user.status, user.level, user.risk_level, user.class_name]
      .join(' ')
      .toLowerCase();
    const matchWord = !word || haystack.includes(word);
    const matchRole = roleFilter.value === '全部角色' || user.role === roleFilter.value;
    const matchStatus = statusFilter.value === '全部状态' || user.status === statusFilter.value;
    return matchWord && matchRole && matchStatus;
  });
});

const roleOptions = computed(() => ['全部角色', ...Array.from(new Set(users.value.map((item) => item.role)))]);
const stats = computed(() => [
  { label: '用户总数', value: users.value.length },
  { label: '学生', value: users.value.filter((item) => item.role === 'student').length },
  { label: '教师', value: users.value.filter((item) => item.role === 'teacher').length },
  { label: '管理员', value: users.value.filter((item) => item.role === 'admin').length },
  { label: '当前结果', value: filteredUsers.value.length }
]);

async function loadData() {
  loading.value = true;
  error.value = '';
  try {
    const [userRows, roleRows] = await Promise.all([
      api.get<AdminUser[]>('/api/v1/admin/users'),
      api.get<RoleItem[]>('/api/v1/admin/roles')
    ]);
    users.value = userRows;
    roles.value = roleRows;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '用户与角色数据加载失败。';
  } finally {
    loading.value = false;
  }
}

async function toggleStatus(user: AdminUser) {
  try {
    const next = user.status === '启用' ? '禁用' : '启用';
    const updated = await api.patch<AdminUser>(`/api/v1/admin/users/${user.id}/status`, { status: next });
    Object.assign(user, updated);
    success.value = '用户状态已更新。';
  } catch (err) {
    error.value = err instanceof Error ? err.message : '状态更新失败。';
  }
}

async function assignRole(user: AdminUser, role: string) {
  try {
    const updated = await api.patch<AdminUser>(`/api/v1/admin/users/${user.id}/role`, { role });
    Object.assign(user, updated);
    success.value = '用户角色已更新。';
    await loadData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '角色更新失败。';
  }
}

async function resetPassword(user: AdminUser) {
  try {
    await api.post<{ temporary_password: string }>(`/api/v1/admin/users/${user.id}/reset-password`);
    success.value = `${user.name} 的一次性临时密码已生成，请通过线下安全渠道传递，勿截图或写入日志。`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '密码重置失败。';
  }
}

async function savePermissions(role: RoleItem) {
  try {
    await api.patch(`/api/v1/admin/roles/${role.role}/permissions`, { permissions: role.permissions });
    success.value = `${role.label}权限已保存。`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '权限保存失败。';
  }
}

function clearSearch() {
  keyword.value = '';
  roleFilter.value = '全部角色';
  statusFilter.value = '全部状态';
}

function roleLabel(role: string) {
  return roles.value.find((item) => item.role === role)?.label || role;
}

onMounted(loadData);
</script>

<template>
  <section class="page">
    <PageHeader title="用户与角色" description="统一管理学生、教师、管理员和端侧权限边界。">
      <template #actions>
        <button class="secondary" type="button" @click="clearSearch">清空搜索</button>
        <button type="button" @click="loadData">刷新数据</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="success" class="panel success-text">{{ success }}</p>
    <p v-if="loading" class="panel muted">正在加载用户与角色...</p>

    <div class="stat-grid">
      <article v-for="item in stats" :key="item.label" class="stat-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </article>
    </div>

    <div class="role-card-grid">
      <DataCard v-for="role in roles" :key="role.role">
        <div class="permission-card">
          <StatusBadge :label="role.label" tone="info" />
          <strong>{{ role.count }} 人</strong>
          <div class="permission-list">
            <label v-for="permission in role.permissions" :key="permission">
              <input v-model="role.permissions" :value="permission" type="checkbox" />
              {{ permission }}
            </label>
          </div>
          <button class="secondary" type="button" @click="savePermissions(role)">保存权限</button>
        </div>
      </DataCard>
    </div>

    <DataCard title="搜索用户" subtitle="按姓名、角色、学习水平、风险等级、班级和部门过滤">
      <div class="filter-grid">
        <input v-model="keyword" placeholder="搜索姓名、账号、班级、角色或风险等级" @keyup.enter.prevent />
        <select v-model="roleFilter">
          <option v-for="item in roleOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="statusFilter">
          <option>全部状态</option>
          <option>启用</option>
          <option>禁用</option>
        </select>
      </div>
    </DataCard>

    <DataCard title="用户列表" :subtitle="`${filteredUsers.length} 个用户`">
      <div class="table-wrap" v-if="filteredUsers.length">
        <table class="table">
          <thead>
            <tr>
              <th>姓名</th>
              <th>账号</th>
              <th>角色</th>
              <th>组织</th>
              <th>画像</th>
              <th>状态</th>
              <th>最近登录</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td><strong>{{ user.name }}</strong></td>
              <td>{{ user.account }}</td>
              <td>
                <select :value="user.role" @change="assignRole(user, ($event.target as HTMLSelectElement).value)">
                  <option v-for="role in roles" :key="role.role" :value="role.role">{{ role.label }}</option>
                </select>
              </td>
              <td>{{ user.org }}</td>
              <td>{{ user.level || '-' }} / {{ user.risk_level || '-' }}</td>
              <td><StatusBadge :label="user.status" :tone="user.status === '启用' ? 'success' : 'neutral'" /></td>
              <td>{{ user.last_login || '-' }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost" type="button" @click="toggleStatus(user)">{{ user.status === '启用' ? '禁用' : '启用' }}</button>
                  <button class="ghost" type="button" @click="resetPassword(user)">重置密码</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-else title="未找到相关用户" description="请更换关键词，或清空搜索后查看全部用户。" />
    </DataCard>
  </section>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 14px;
  background: #fff;
}

.stat-card strong {
  display: block;
  margin-top: 8px;
  color: var(--text-main);
  font-size: 26px;
}

.role-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.permission-card,
.permission-list {
  display: grid;
  gap: 10px;
}

.filter-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 160px 160px;
  gap: 12px;
}

.table-wrap {
  overflow-x: auto;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.error-text {
  color: #b91c1c;
}

.success-text {
  color: #047857;
}

@media (max-width: 960px) {
  .stat-grid,
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
