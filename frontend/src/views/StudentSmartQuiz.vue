<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import { chapterQuiz, fallbackQuizResult } from '../api/mocks/competitionData';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

type ChapterQuiz = typeof chapterQuiz;
interface QuizResult {
  score: number;
  correct_count: number;
  total: number;
  weak_points: string[];
  wrong_items: Array<{ question_id: string; stem?: string; selected?: string; correct_answer?: string; knowledge_point: string; reason: string; recommendation: string }>;
  cause_analysis: Array<{ type: string; detail: string }>;
  recommended_resources: Array<{ title: string; knowledge_point?: string; minutes?: number; type?: string; reason?: string }>;
  next_step: string;
  path_adjustment?: {
    adjusted: boolean;
    reason: string;
    added_tasks: string[];
    difficulty_change: string;
    recommended_resources: Array<{ title: string; type?: string; reason?: string }>;
    next_learning_step: string;
  };
  evaluation?: {
    score: number;
    weak_points: string[];
    error_analysis: string;
    path_adjustment_needed: boolean;
    next_steps: string[];
  };
}

const quiz = ref<ChapterQuiz>(chapterQuiz);
const answers = reactive<Record<string, string>>({});
const result = ref<QuizResult | null>(null);
const loading = ref(true);
const submitting = ref(false);
const error = ref('');

const answeredCount = computed(() => Object.values(answers).filter(Boolean).length);

async function loadQuiz() {
  loading.value = true;
  error.value = '';
  try {
    quiz.value = await api.get<ChapterQuiz>('/api/v1/quiz/chapter');
  } catch (err) {
    error.value = err instanceof Error ? `章节测验接口暂不可用，已使用本地演示题库：${err.message}` : '章节测验接口暂不可用，已使用本地演示题库。';
    quiz.value = chapterQuiz;
  } finally {
    loading.value = false;
  }
}

async function submitQuiz() {
  submitting.value = true;
  error.value = '';
  try {
    result.value = await api.post<QuizResult>('/api/v1/quiz/submit', {
      quiz_id: quiz.value.quiz_id,
      student_id: 'demo-student-zhangsan',
      answers
    });
  } catch (err) {
    error.value = err instanceof Error ? `提交接口暂不可用，已展示本地练后分析：${err.message}` : '提交接口暂不可用，已展示本地练后分析。';
    result.value = fallbackQuizResult;
  } finally {
    submitting.value = false;
  }
}

onMounted(loadQuiz);
</script>

<template>
  <section class="page smart-quiz-page">
    <PageHeader title="智能测验与练后分析" description="通过章节练习完成即时判分、错因诊断、薄弱知识点识别和下一步资源推荐，演示测评—诊断—推荐闭环。">
      <template #actions>
        <RouterLink class="btn secondary" to="/student/knowledge-graph">查看知识图谱</RouterLink>
        <button :disabled="submitting || answeredCount < quiz.questions.length" @click="submitQuiz">
          {{ submitting ? '分析中...' : '提交并生成分析' }}
        </button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载章节练习题...</p>
    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="章节" value="基础语法" hint="Python 程序设计" icon="章" />
      <StatCard label="题目数" :value="quiz.questions.length" unit="题" hint="规则判分演示" icon="题" tone="purple" />
      <StatCard label="已作答" :value="answeredCount" unit="题" hint="提交前自动检查" icon="答" tone="cyan" />
      <StatCard label="闭环产物" value="4" unit="类" hint="得分、错因、薄弱点、资源" icon="诊" tone="green" />
    </div>

    <div class="quiz-layout">
      <DataCard :title="quiz.title" :subtitle="quiz.chapter">
        <div class="question-list">
          <article v-for="(question, index) in quiz.questions" :key="question.id" class="question-card">
            <div class="question-head">
              <strong>{{ index + 1 }}. {{ question.stem }}</strong>
              <StatusBadge :label="question.knowledge_point" tone="info" />
            </div>
            <label v-for="option in question.options" :key="option" class="option-row">
              <input v-model="answers[question.id]" type="radio" :name="question.id" :value="option" />
              <span>{{ option }}</span>
            </label>
          </article>
        </div>
      </DataCard>

      <DataCard title="练后诊断" subtitle="提交后自动生成错因分析和资源推荐">
        <div v-if="!result" class="empty-analysis">
          <strong>等待提交</strong>
          <p>完成全部题目后提交，系统将生成得分、错题、薄弱知识点和下一步路径建议。</p>
        </div>
        <div v-else class="analysis-panel">
          <div class="score-ring">
            <strong>{{ result.score }}</strong>
            <span>分</span>
          </div>
          <ProgressBar :value="result.score" :tone="result.score >= 85 ? 'success' : result.score >= 70 ? 'primary' : 'warning'" />
          <p class="muted-text">正确 {{ result.correct_count }} / {{ result.total }}，薄弱知识点：{{ result.weak_points.join('、') || '暂无' }}</p>

          <div class="analysis-block">
            <span>错因分析</span>
            <article v-for="item in result.cause_analysis" :key="item.type">
              <strong>{{ item.type }}</strong>
              <p>{{ item.detail }}</p>
            </article>
          </div>

          <div class="analysis-block">
            <span>错题明细</span>
            <article v-for="item in result.wrong_items" :key="item.question_id">
              <strong>{{ item.knowledge_point }}：{{ item.reason }}</strong>
              <p>{{ item.recommendation }}</p>
            </article>
          </div>

          <div class="analysis-block">
            <span>推荐资源</span>
            <article v-for="item in result.recommended_resources" :key="item.title">
              <strong>{{ item.title }}</strong>
              <p>{{ item.knowledge_point }} · 预计 {{ item.minutes }} 分钟</p>
            </article>
          </div>

          <div v-if="result.path_adjustment" class="analysis-block path-adjustment">
            <span>学习路径动态调整</span>
            <article>
              <strong>{{ result.path_adjustment.adjusted ? '已根据测评结果调整学习路径' : '当前路径保持不变' }}</strong>
              <p>{{ result.path_adjustment.reason }}</p>
              <p>难度变化：{{ result.path_adjustment.difficulty_change }}</p>
              <p v-if="result.path_adjustment.added_tasks.length">新增任务：{{ result.path_adjustment.added_tasks.join('、') }}</p>
              <p>下一步：{{ result.path_adjustment.next_learning_step }}</p>
            </article>
          </div>

          <div class="next-step">{{ result.next_step }}</div>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.quiz-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(340px, 0.42fr);
  gap: 16px;
}

.question-list,
.analysis-panel {
  display: grid;
  gap: 14px;
}

.question-card {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 14px;
  background: #fbfdff;
}

.question-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 34px;
  color: var(--color-text-sub);
}

.option-row input {
  width: auto;
}

.empty-analysis,
.next-step {
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 14px;
  background: var(--color-primary-light);
}

.score-ring {
  display: inline-grid;
  place-items: center;
  width: 110px;
  height: 110px;
  border-radius: 999px;
  color: var(--color-primary-dark);
  background: radial-gradient(circle at center, #fff 56%, #dbeafe 58%);
  border: 10px solid #93c5fd;
}

.score-ring strong {
  font-size: 32px;
}

.score-ring span,
.muted-text,
.analysis-block > span {
  color: var(--color-text-sub);
  font-size: 13px;
}

.analysis-block {
  display: grid;
  gap: 8px;
  border-top: 1px solid var(--color-border);
  padding-top: 12px;
}

.path-adjustment article {
  border: 1px solid #bbf7d0;
  background: #f0fdf4;
}

.analysis-block article {
  border-radius: 10px;
  padding: 10px;
  background: #f8fafc;
}

.analysis-block p {
  margin: 6px 0 0;
}

@media (max-width: 1100px) {
  .quiz-layout {
    grid-template-columns: 1fr;
  }
}
</style>
