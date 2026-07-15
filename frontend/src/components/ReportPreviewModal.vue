<script setup lang="ts">
defineProps<{
  visible: boolean;
  report: any | null;
}>();

defineEmits<{
  close: [];
  download: [report: any];
}>();
</script>

<template>
  <div v-if="visible && report" class="modal-mask" @click.self="$emit('close')">
    <article class="modal-card">
      <header>
        <div>
          <h2>{{ report.report_title }}</h2>
          <p>{{ report.course_title }} / {{ report.student_name }} / {{ report.report_type }}</p>
        </div>
        <button class="ghost" type="button" @click="$emit('close')">关闭</button>
      </header>

      <section class="preview-body">
        <div class="preview-section">
          <strong>报告摘要</strong>
          <p>{{ report.summary?.report_abstract }}</p>
        </div>
        <div class="preview-section">
          <strong>关键结论</strong>
          <ul>
            <li v-for="item in report.summary?.key_conclusions || []" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="preview-section">
          <strong>薄弱知识点</strong>
          <div class="tag-row">
            <span v-for="item in report.summary?.weak_points || []" :key="item">{{ item }}</span>
          </div>
        </div>
        <div class="preview-section">
          <strong>证据链</strong>
          <article v-for="item in report.summary?.evidence_chain || []" :key="item.source_title" class="evidence-row">
            <span>{{ item.source_title }}</span>
            <p>{{ item.source_excerpt }}</p>
          </article>
        </div>
      </section>

      <footer>
        <button class="secondary" type="button" @click="$emit('close')">返回列表</button>
        <button type="button" @click="$emit('download', report)">导出报告</button>
      </footer>
    </article>
  </div>
</template>

<style scoped>
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.45);
}

.modal-card {
  width: min(860px, 100%);
  max-height: min(760px, 92vh);
  overflow: auto;
  border-radius: 18px;
  padding: 22px;
  background: #fff;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.25);
}

header,
footer {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
}

h2,
p {
  margin: 0;
}

header p,
.preview-section p {
  color: var(--text-secondary);
  line-height: 1.65;
}

.preview-body {
  display: grid;
  gap: 14px;
  margin: 18px 0;
}

.preview-section,
.evidence-row {
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 14px;
  background: #fff;
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

.evidence-row {
  margin-top: 10px;
}

.evidence-row span {
  font-weight: 800;
}
</style>
