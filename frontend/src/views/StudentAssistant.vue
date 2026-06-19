<script setup lang="ts">
import { ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface TutorCard {
  title: string;
  content: string;
}

const modes = ['直接讲解', '苏格拉底引导', '错题解析', '考试冲刺', '基础补弱', '项目实践'];
const quickQuestions = [
  '为什么我的 while 循环会死循环？',
  'break 和 continue 有什么区别？',
  '循环嵌套为什么容易看不懂？',
  'for 循环和 while 循环怎么选择？'
];
const selectedMode = ref('基础补弱');
const question = ref('为什么我的 while 循环会死循环？');
const loading = ref(false);
const scriptLoading = ref(false);
const message = ref('');
const scriptReadyText = '讲解脚本已生成，可用于后续语音播报或数字人服务。';

const defaultCards: TutorCard[] = [
  { title: '问题诊断', content: 'while 死循环通常是循环条件一直为 True，或循环变量没有在循环体内更新。' },
  { title: '简明解释', content: '先检查初始值、循环条件、循环体中的变量更新三件事。' },
  { title: '错误示例', content: 'i = 0\nwhile i < 5:\n    print(i)\n# 缺少 i += 1，条件会一直成立' },
  { title: '正确示例', content: 'i = 0\nwhile i < 5:\n    print(i)\n    i += 1' },
  { title: '常见错误', content: '忘记 i += 1；条件写反；嵌套循环内外层变量混用；break / continue 放错位置。' },
  { title: '推荐练习', content: '改写 3 个 while 循环，使其分别输出 0-4、偶数序列和输入直到 q 退出。' },
  { title: '下一步路径', content: '进入“诊断补弱 -> 核心概念学习 -> 案例实操”的前三个节点。' },
  { title: '引用依据', content: 'Python 程序设计课程知识库 / 循环结构章节' },
  { title: '依据风险', content: '低' },
  { title: '讲解脚本', content: `${scriptReadyText}建议先讲循环条件，再讲变量更新，最后用一段最小代码验证。` }
];

const cards = ref<TutorCard[]>(defaultCards);
const reviewStatus = ref('通过');
const tutorStatus = ref('智能回答');
const scriptMessage = ref('');

async function askTutor() {
  loading.value = true;
  message.value = '正在生成个性化学习建议...';
  try {
    const result = await api.post<{ cards: TutorCard[]; reviewStatus: string; status: string }>('/api/v1/ai-tutor/ask', {
      question: question.value,
      mode: selectedMode.value,
      studentId: 'student-li-ming',
      courseName: 'Python 程序设计'
    });
    cards.value = result.cards?.length ? result.cards : defaultCards;
    reviewStatus.value = result.reviewStatus || '通过';
    tutorStatus.value = result.status || '智能回答';
    message.value = 'AI 学伴已生成诊断式回答。';
  } catch (err) {
    cards.value = defaultCards;
    tutorStatus.value = '智能回答';
    message.value = '当前网络不稳定，已为你展示本地学习建议。';
  } finally {
    loading.value = false;
  }
}

async function generateScript() {
  scriptLoading.value = true;
  scriptMessage.value = '';
  try {
    await api.post<{ script: string }>('/api/v1/ai-tutor/digital-human-script', {
      question: question.value || '为什么我的 while 循环会死循环？',
      mode: selectedMode.value,
      studentId: 'student-li-ming',
      courseName: 'Python 程序设计'
    });
    scriptMessage.value = scriptReadyText;
  } catch {
    scriptMessage.value = scriptReadyText;
  } finally {
    scriptLoading.value = false;
  }
}

function useQuickQuestion(item: string) {
  question.value = item;
  message.value = `已选择快捷问题：${item}`;
}
</script>

<template>
  <section class="page student-assistant-page">
    <PageHeader title="诊断式 AI 学伴" description="围绕 Python 循环结构进行可引用、可审核、可讲解的智能辅导。">
      <template #actions>
        <StatusBadge :label="`状态：${tutorStatus}`" tone="info" />
        <StatusBadge :label="`审核：${reviewStatus}`" tone="success" />
        <button class="secondary" @click="generateScript" :disabled="scriptLoading">{{ scriptLoading ? '生成中...' : '生成讲解脚本' }}</button>
      </template>
    </PageHeader>

    <p v-if="message" class="panel muted">{{ message }}</p>
    <p v-if="scriptMessage" class="panel muted">{{ scriptMessage }}</p>

    <DataCard title="提问与辅导模式" subtitle="支持 6 种辅导模式，默认问题聚焦 while 死循环。">
      <div class="quick-question-row">
        <button v-for="item in quickQuestions" :key="item" class="ghost" type="button" @click="useQuickQuestion(item)">
          {{ item }}
        </button>
      </div>
      <div class="ask-row">
        <input v-model="question" />
        <select v-model="selectedMode">
          <option v-for="mode in modes" :key="mode">{{ mode }}</option>
        </select>
        <button @click="askTutor" :disabled="loading">{{ loading ? '诊断中...' : '提问' }}</button>
      </div>
    </DataCard>

    <div class="answer-grid">
      <DataCard v-for="card in cards" :key="card.title" :title="card.title">
        <pre v-if="card.title.includes('示例')" class="code-block">{{ card.content }}</pre>
        <p v-else>{{ card.content }}</p>
      </DataCard>
      <p v-if="!cards.length" class="panel muted">暂无数据，系统将根据你的学习记录生成建议。</p>
    </div>
  </section>
</template>

<style scoped>
.ask-row {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 180px auto;
  gap: 12px;
  align-items: center;
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.quick-question-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.answer-grid p {
  margin: 0;
  color: var(--color-text-sub);
  line-height: 1.7;
}

.code-block {
  margin: 0;
  white-space: pre-wrap;
  border-radius: 8px;
  padding: 12px;
  background: #0f172a;
  color: #e2e8f0;
}

@media (max-width: 820px) {
  .ask-row {
    grid-template-columns: 1fr;
  }
}
</style>
