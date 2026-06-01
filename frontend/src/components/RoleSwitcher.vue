<script setup lang="ts">
import { useRouter } from 'vue-router';
import { roleHomePath, type UserRole } from '../config/roles';
import { useRole } from '../composables/useRole';

const router = useRouter();
const { availableRoles, currentRole, roleLabels, setRole } = useRole();

function switchRole(role: UserRole) {
  setRole(role);
  router.push(roleHomePath[role]);
}
</script>

<template>
  <div class="role-switcher" aria-label="角色切换">
    <button
      v-for="role in availableRoles"
      :key="role"
      type="button"
      :class="{ active: currentRole === role }"
      @click="switchRole(role)"
    >
      {{ roleLabels[role] }}
    </button>
  </div>
</template>
