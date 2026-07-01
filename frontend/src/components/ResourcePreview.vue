<script setup lang="ts">
const props = defineProps<{ resource: { title?: string; content?: string; preview_type?: string; resource_type?: string; resource_url?: string; file_path?: string; fallback_message?: string } }>();

function previewType() {
  return props.resource.preview_type || (props.resource.resource_type === 'animation_html' ? 'html' : props.resource.resource_type === 'video_mp4' ? 'video' : props.resource.resource_type === 'tts_audio' ? 'audio' : 'markdown');
}
</script>

<template>
  <div class="resource-preview">
    <iframe v-if="previewType() === 'html'" :srcdoc="resource.content || ''" sandbox="" :title="resource.title || '资源预览'"></iframe>
    <audio v-else-if="previewType() === 'audio' && resource.resource_url" :src="resource.resource_url" controls />
    <video v-else-if="previewType() === 'video' && resource.resource_url" :src="resource.resource_url" controls />
    <pre v-else>{{ resource.content || resource.fallback_message || '暂无可预览内容，当前展示本地轻量 fallback。' }}</pre>
    <p v-if="resource.fallback_message">{{ resource.fallback_message }}</p>
  </div>
</template>

<style scoped>
.resource-preview {
  margin-top: 12px;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}
iframe,
video {
  display: block;
  width: 100%;
  min-height: 220px;
  border: 0;
}
audio {
  width: 100%;
  padding: 12px;
}
pre {
  margin: 0;
  white-space: pre-wrap;
  color: var(--text-secondary);
}
p {
  margin: 0;
  padding: 10px 12px;
  color: var(--status-warning-text);
  background: var(--status-warning-banner-bg);
}
</style>
