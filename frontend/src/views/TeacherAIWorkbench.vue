<script setup lang="ts">
import { reactive, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface WorkbenchResult {
  type: string;
  title: string;
  course: string;
  chapter: string;
  input_summary: string;
  teaching_objectives: string[];
  key_difficulties: string[];
  class_activities: string[];
  in_class_quiz: string[];
  after_class_tasks: string[];
  teaching_suggestions: string[];
  review_required: boolean;
}

const form = reactive({
  type: 'lesson_plan',
  course: 'Python 程序设计',
  chapter: '循环结构',
  student_foundation: '班级基础差异较大，部分学生循环边界、变量更新和 break / continue 区分薄弱',
  teaching_goal: '掌握 for、while、break / continue 和循环嵌套，能完成循环结构代码实操'
});

const result = ref<WorkbenchResult | null>(null);
const loading = ref(false);
const error = ref('');

const typeCards = [
  { type: 'lesson_plan', title: 'AI 生成教案', desc: '生成教学目标、重难点、课堂活动和课后任务。' },
  { type: 'quiz', title: 'AI 生成测验', desc: '生成随堂题、知识点标签和练后诊断规则。' },
  { type: 'analysis', title: 'AI 生成学情分析', desc: '生成薄弱点、学习预警和教师干预建议。' }
];

function fallback(payloadType = form.type): WorkbenchResult {
  const title = typeCards.find((item) => item.type === payloadType)?.title || 'AI 教学建议';
  return {
    type: payloadType,
    title,
    course: form.course,
    chapter: form.chapter,
    input_summary: `学生基础：${form.student_foundation}；教学目标：${form.teaching_goal}`,
    teaching_objectives: [form.teaching_goal, '识别本章薄弱知识点并形成可干预任务', '完成测评、诊断、推荐闭环记录'],
    key_difficulties: ['循环边界条件', '变量更新时机', 'break / continue 区分'],
    class_activities: ['5 分钟错题导入', '15 分钟案例拆解', '10 分钟随堂测验', '8 分钟同伴互评'],
    in_class_quiz: ['判断 while 循环是否会终止', '写出前三轮变量变化', '区分 break 和 continue 的输出结果'],
    after_class_tasks: ['完成错题二刷', '提交循环嵌套输出表', '在 AI 助教中追问 1 个薄弱知识点'],
    teaching_suggestions: ['生成内容需教师审核后发布', '学习预警学生优先推送补救任务', '测验结果仅作为诊断参考，不直接替代教师评价'],
    review_required: true
  };
}

async function generate(type = form.type) {
  form.type = type;
  loading.value = true;
  error.value = '';
  try {
    result.value = await api.post<WorkbenchResult>('/api/v1/teacher/ai-workbench/generate', form);
  } catch (err) {
    error.value = err instanceof Error ? `后端生成接口暂不可用，已使用规则生成结果：${err.message}` : '后端生成接口暂不可用，已使用规则生成结果。';
    result.value = fallback(type);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="page teacher-ai-workbench">
    <PageHeader title="AI 教学工作台" description="面向教师备课、出题和学情分析的轻量生成工具，生成结果进入审核流程后再发布给学生。">
      <template #actions>
        <RouterLink class="btn secondary" to="/teacher">返回班级学情</RouterLink>
        <button @click="generate()">{{ loading ? '生成中...' : '生成内容' }}</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="生成能力" value="3" unit="类" hint="教案、测验、学情" icon="AI" />
      <StatCard label="审核要求" value="100" unit="%" hint="关键内容需教师确认" icon="审" tone="orange" />
      <StatCard label="关联闭环" value="7" unit="步" hint="画像到治理完整链路" icon="环" tone="purple" />
      <StatCard label="演示模式" value="规则" hint="稳定可控，可接大模型" icon="稳" tone="green" />
    </div>

    <div class="workbench-layout">
      <DataCard title="生成输入" subtitle="选择生成类型并填写课程、章节、学生基础和教学目标。">
        <div class="type-grid">
          <article
            v-for="item in typeCards"
            :key="item.type"
            :class="['type-card', { active: form.type === item.type }]"
            @click="generate(item.type)"
          >
            <strong>{{ item.title }}</strong>
            <p>{{ item.desc }}</p>
          </article>
        </div>
        <div class="form-grid">
          <label>课程<input v-model="form.course" /></label>
          <label>章节<input v-model="form.chapter" /></label>
          <label>学生基础<textarea v-model="form.student_foundation" /></label>
          <label>教学目标<textarea v-model="form.teaching_goal" /></label>
        </div>
      </DataCard>

      <DataCard title="审核边界" subtitle="AI 生成内容不是直接发布内容">
        <div class="boundary-box">
          <StatusBadge label="需教师审核" tone="warning" />
          <p>AI 生成教案、测验、学情分析仅作为教学辅助。关键教学资源、测评结果和学生干预建议必须经教师或管理员审核后使用。</p>
        </div>
      </DataCard>
    </div>

    <DataCard v-if="result" :title="result.title" :subtitle="`${result.course} · ${result.chapter}`">
      <template #action>
        <StatusBadge :label="result.review_required ? '待审核后发布' : '可发布'" :tone="result.review_required ? 'warning' : 'success'" />
      </template>
      <div class="result-grid">
        <section>
          <h3>教学目标</h3>
          <ul><li v-for="item in result.teaching_objectives" :key="item">{{ item }}</li></ul>
        </section>
        <section>
          <h3>教学重难点</h3>
          <ul><li v-for="item in result.key_difficulties" :key="item">{{ item }}</li></ul>
        </section>
        <section>
          <h3>课堂活动</h3>
          <ul><li v-for="item in result.class_activities" :key="item">{{ item }}</li></ul>
        </section>
        <section>
          <h3>随堂测验</h3>
          <ul><li v-for="item in result.in_class_quiz" :key="item">{{ item }}</li></ul>
        </section>
        <section>
          <h3>课后任务</h3>
          <ul><li v-for="item in result.after_class_tasks" :key="item">{{ item }}</li></ul>
        </section>
        <section>
          <h3>教学建议</h3>
          <ul><li v-for="item in result.teaching_suggestions" :key="item">{{ item }}</li></ul>
        </section>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.workbench-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.type-card {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
  cursor: pointer;
}

.type-card.active {
  border-color: #93c5fd;
  background: var(--color-primary-light);
}

.type-card p {
  margin: 8px 0 0;
  color: var(--color-text-sub);
  font-size: 13px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.boundary-box {
  display: grid;
  gap: 12px;
  border: 1px solid #fed7aa;
  border-radius: 12px;
  padding: 14px;
  background: #fff7ed;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.result-grid section {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: #fbfdff;
}

.result-grid h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.result-grid ul {
  margin: 0;
  padding-left: 18px;
}

@media (max-width: 1100px) {
  .workbench-layout,
  .type-grid,
  .form-grid,
  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>
