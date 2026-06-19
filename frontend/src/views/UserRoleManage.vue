<script setup lang="ts">
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const users = [
  { name: '李明', account: '2021123456', role: '学生', org: '计科大三 1 班', status: '启用', login: '05-31 09:20' },
  { name: '王老师', account: 'T2021001', role: '教师', org: '计算机科学与技术学院', status: '启用', login: '05-31 08:45' },
  { name: '李助教', account: 'A2023002', role: '助教', org: 'Python 课程组', status: '启用', login: '05-30 18:10' },
  { name: '赵管理员', account: 'admin01', role: '管理员', org: '平台运营中心', status: '启用', login: '05-30 15:42' },
  { name: '周同学', account: '2021123471', role: '学生', org: '计科大三 2 班', status: '禁用', login: '05-26 10:16' }
];

const roles = [
  { title: '学生', count: 1638, desc: '学习总览、课程资料、答疑、报告与小组协作', tone: 'info' as const },
  { title: '教师', count: 343, desc: '班级治理、课程任务、画像分析与报告生成', tone: 'success' as const },
  { title: '助教', count: 98, desc: '答疑协助、作业批改、资源审核和课堂运营', tone: 'purple' as const },
  { title: '管理员', count: 77, desc: '平台治理、用户权限、日志监控和系统配置', tone: 'warning' as const }
];
</script>

<template>
  <section class="page">
    <PageHeader title="用户与角色" description="统一管理学生、教师、助教、管理员和平台权限边界。">
      <template #actions>
        <button>新增用户</button>
        <button class="secondary">导入名单</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard label="总用户" value="8,345" unit="人" icon="用" />
      <StatCard label="学生" value="7,827" unit="人" icon="学" tone="cyan" />
      <StatCard label="教师" value="343" unit="人" icon="师" tone="green" />
      <StatCard label="管理员" value="77" unit="人" icon="管" tone="purple" />
      <StatCard label="今日新增" value="42" unit="人" icon="新" tone="orange" />
    </div>

    <div class="role-card-grid">
      <DataCard v-for="role in roles" :key="role.title">
        <div class="permission-card">
          <StatusBadge :label="role.title" :tone="role.tone" />
          <strong>{{ role.count }} 人</strong>
          <p>{{ role.desc }}</p>
          <button class="secondary">配置权限</button>
        </div>
      </DataCard>
    </div>

    <DataCard title="用户列表" subtitle="账号、角色、组织关系、启用状态与最近登录">
      <template #action>
        <button class="secondary">权限模板</button>
      </template>
      <div class="filter-row user-filter">
        <input placeholder="搜索姓名、账号、班级或部门..." />
        <select><option>全部角色</option><option>学生</option><option>教师</option><option>助教</option><option>管理员</option></select>
        <select><option>全部状态</option><option>启用</option><option>禁用</option></select>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>姓名</th>
            <th>账号</th>
            <th>角色</th>
            <th>所属班级/部门</th>
            <th>状态</th>
            <th>最近登录</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.account">
            <td><strong>{{ user.name }}</strong></td>
            <td>{{ user.account }}</td>
            <td><StatusBadge :label="user.role" :tone="user.role === '管理员' ? 'warning' : user.role === '教师' ? 'success' : user.role === '助教' ? 'purple' : 'info'" /></td>
            <td>{{ user.org }}</td>
            <td><StatusBadge :label="user.status" :tone="user.status === '启用' ? 'success' : 'neutral'" /></td>
            <td>{{ user.login }}</td>
            <td>
              <div class="row-actions">
                <button class="ghost">{{ user.status === '启用' ? '禁用' : '启用' }}</button>
                <button class="ghost">重置密码</button>
                <button class="ghost">分配角色</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </DataCard>
  </section>
</template>

<style scoped>
.role-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.permission-card {
  display: grid;
  gap: 10px;
}

.permission-card strong {
  font-size: 24px;
}

.permission-card p {
  min-height: 48px;
  margin: 0;
  line-height: 1.6;
}

.user-filter {
  grid-template-columns: minmax(260px, 1fr) 160px 160px;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

@media (max-width: 820px) {
  .user-filter {
    grid-template-columns: 1fr;
  }
}
</style>
