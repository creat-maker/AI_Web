<script setup lang="ts">
import { computed, ref } from 'vue';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface LoopGameLevel {
  title: string;
  knowledgePoint: string;
  question: string;
  code: string;
  options: string[];
  answer: number;
  explanation: string;
}

const levels: LoopGameLevel[] = [
  {
    title: '第一关：while 循环条件更新',
    knowledgePoint: 'while 循环',
    question: '下面代码要输出 0、1、2，空缺处最合适的是哪一项？',
    code: 'i = 0\nwhile i < 3:\n    print(i)\n    ____',
    options: ['i = 0', 'i += 1', 'i < 3', 'continue'],
    answer: 1,
    explanation: 'while 循环需要在循环体中更新变量。选择 i += 1 后，i 会逐步接近终止条件，避免死循环。'
  },
  {
    title: '第二关：break / continue 区分',
    knowledgePoint: 'break / continue',
    question: '如果希望遇到 3 时结束整个循环，应该填入哪一项？',
    code: 'for n in range(6):\n    if n == 3:\n        ____\n    print(n)',
    options: ['continue', 'break', 'pass', 'n += 1'],
    answer: 1,
    explanation: 'break 会结束当前循环；continue 只会跳过本轮剩余语句并进入下一轮。题目要求结束整个循环，所以选择 break。'
  },
  {
    title: '第三关：循环嵌套变量变化',
    knowledgePoint: '循环嵌套',
    question: '下面代码一共会输出几行？',
    code: 'for i in range(2):\n    for j in range(3):\n        print(i, j)',
    options: ['2 行', '3 行', '5 行', '6 行'],
    answer: 3,
    explanation: '外层循环执行 2 次；每次外层循环中，内层循环执行 3 次，所以总输出 2 x 3 = 6 行。'
  }
];

const currentIndex = ref(0);
const selectedOption = ref<number | null>(null);
const answered = ref(false);
const score = ref(0);
const feedback = ref('');
const completed = ref(false);

const currentLevel = computed(() => levels[currentIndex.value]);
const progress = computed(() => Math.round(((currentIndex.value + (answered.value || completed.value ? 1 : 0)) / levels.length) * 100));
const scoreLabel = computed(() => `${score.value} / ${levels.length * 10}`);

function selectOption(index: number) {
  if (answered.value) return;
  selectedOption.value = index;
}

function submitAnswer() {
  if (selectedOption.value === null || answered.value) return;
  answered.value = true;
  if (selectedOption.value === currentLevel.value.answer) {
    score.value += 10;
    feedback.value = '回答正确，已获得 10 分。';
  } else {
    feedback.value = `还需要再看一遍：${currentLevel.value.explanation}`;
  }
}

function nextLevel() {
  if (currentIndex.value >= levels.length - 1) {
    completed.value = true;
    return;
  }
  currentIndex.value += 1;
  selectedOption.value = null;
  answered.value = false;
  feedback.value = '';
}

function restartGame() {
  currentIndex.value = 0;
  selectedOption.value = null;
  answered.value = false;
  score.value = 0;
  feedback.value = '';
  completed.value = false;
}
</script>

<template>
  <section class="page loop-game-page">
    <PageHeader title="循环结构闯关练习" description="李明的 Python 循环结构互动练习，聚焦 while 循环、break / continue 和循环嵌套。">
      <template #actions>
        <RouterLink class="btn secondary" to="/student/learning-path">回到学习路径</RouterLink>
        <RouterLink class="btn" to="/student/reports">查看学习报告</RouterLink>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <DataCard title="当前关卡">
        <strong>{{ completed ? '全部完成' : `${currentIndex + 1} / ${levels.length}` }}</strong>
      </DataCard>
      <DataCard title="得分">
        <strong>{{ scoreLabel }}</strong>
      </DataCard>
      <DataCard title="进度">
        <div class="progress-track"><span :style="{ width: `${Math.min(progress, 100)}%` }"></span></div>
      </DataCard>
    </div>

    <DataCard v-if="!completed" :title="currentLevel.title" :subtitle="currentLevel.knowledgePoint">
      <div class="game-layout">
        <div>
          <p class="question">{{ currentLevel.question }}</p>
          <pre class="code-block">{{ currentLevel.code }}</pre>
        </div>

        <div class="option-list">
          <button
            v-for="(option, index) in currentLevel.options"
            :key="option"
            type="button"
            class="option-button"
            :class="{
              selected: selectedOption === index,
              correct: answered && index === currentLevel.answer,
              wrong: answered && selectedOption === index && index !== currentLevel.answer
            }"
            @click="selectOption(index)"
          >
            <span>{{ String.fromCharCode(65 + index) }}</span>
            {{ option }}
          </button>
        </div>
      </div>

      <div class="feedback-row">
        <StatusBadge :label="answered ? (selectedOption === currentLevel.answer ? '回答正确' : '需要巩固') : '等待作答'" :tone="answered && selectedOption === currentLevel.answer ? 'success' : answered ? 'warning' : 'info'" />
        <p v-if="feedback">{{ feedback }}</p>
        <p v-else>选择一个答案后提交，系统会给出得分反馈和答错讲解。</p>
      </div>

      <div class="game-actions">
        <button type="button" :disabled="selectedOption === null || answered" @click="submitAnswer">提交答案</button>
        <button type="button" class="secondary" :disabled="!answered" @click="nextLevel">
          {{ currentIndex === levels.length - 1 ? '完成闯关' : '下一关' }}
        </button>
      </div>
    </DataCard>

    <section v-else class="panel completion-panel">
      <div>
        <h2>闯关完成</h2>
        <p>本次得分 {{ scoreLabel }}。建议回到学习路径继续完成 while 循环条件更新和循环嵌套变量变化专项任务，也可以查看学习报告。</p>
      </div>
      <div class="game-actions">
        <RouterLink class="btn" to="/student/learning-path">回到学习路径</RouterLink>
        <RouterLink class="btn secondary" to="/student/reports">查看报告</RouterLink>
        <button type="button" class="ghost" @click="restartGame">重新闯关</button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.loop-game-page {
  gap: 18px;
}

.stat-grid strong {
  display: block;
  margin-top: 4px;
  font-size: 24px;
}

.progress-track {
  height: 10px;
  margin-top: 12px;
  border-radius: 999px;
  background: var(--border-soft);
  overflow: hidden;
}

.progress-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--color-primary);
}

.game-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.8fr);
  gap: 18px;
}

.question {
  margin: 0 0 12px;
  color: var(--color-text-main);
  font-weight: 700;
  line-height: 1.7;
}

.code-block {
  margin: 0;
  white-space: pre-wrap;
  border-radius: 8px;
  padding: 16px;
  color: #e2e8f0;
  background: #0f172a;
  line-height: 1.7;
}

.option-list {
  display: grid;
  gap: 10px;
}

.option-button {
  justify-content: flex-start;
  min-height: 52px;
  color: var(--color-text-main);
  background: #fff;
  border: 1px solid var(--color-border);
  box-shadow: none;
}

.option-button span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-weight: 800;
}

.option-button.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.option-button.correct {
  border-color: var(--status-success-border);
  background: var(--status-success-bg);
}

.option-button.wrong {
  border-color: var(--status-danger-border);
  background: var(--status-danger-bg);
}

.feedback-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}

.feedback-row p {
  margin: 0;
  color: var(--color-text-sub);
  line-height: 1.6;
}

.game-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.completion-panel {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.completion-panel h2 {
  margin: 0 0 8px;
}

.completion-panel p {
  margin: 0;
  color: var(--color-text-sub);
  line-height: 1.7;
}

@media (max-width: 920px) {
  .game-layout,
  .completion-panel {
    display: grid;
  }
}
</style>
