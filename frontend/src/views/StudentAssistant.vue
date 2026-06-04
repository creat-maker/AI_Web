<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const messages = [
  { role: 'user', text: '什么是函数式编程？它和面向对象编程有什么区别？' },
  { role: 'assistant', text: '函数式编程强调函数组合、不可变性和无副作用；面向对象强调对象、状态和封装。学习 Python 时，可以把函数式思维用于数据处理，把面向对象用于复杂业务建模。' },
  { role: 'user', text: '给我一个 Python 里的高阶函数例子。' },
  { role: 'assistant', text: '例如 map、filter、sorted 的 key 参数都可以接收函数。你也可以把自定义函数作为参数传入另一个函数，用来复用处理逻辑。' }
];

const questions = ['纯函数是什么？', '如何使用 map/filter？', '给我一个爬虫项目示例', '这道题为什么错？'];
const references = [
  { title: '计算机科学导论', page: '第 7 章 函数式编程范式', type: 'PDF' },
  { title: 'Python 高级编程', page: '第 18 章 函数式编程工具', type: 'PDF' },
  { title: '函数式编程实战', page: '第 2 章 核心概念', type: 'DOCX' }
];
</script>

<template>
  <section class="page assistant-page">
    <PageHeader title="智能答疑" description="基于课程资料的学习问答，展示引用来源和推荐追问。">
      <template #actions>
        <StatusBadge label="AI 在线" tone="success" />
      </template>
    </PageHeader>

    <div class="assistant-layout">
      <DataCard title="对话面板" subtitle="当前为 UI 演示，不接入新的大模型依赖">
        <div class="chat-list">
          <div v-for="message in messages" :key="message.text" :class="['chat-bubble', message.role]">
            {{ message.text }}
          </div>
        </div>
        <div class="assistant-input">
          <input placeholder="继续提问或输入 / 选择技能..." />
          <button>发送</button>
        </div>
      </DataCard>

      <aside class="assistant-side">
        <DataCard title="推荐问题" subtitle="根据当前课程和薄弱点生成">
          <div class="question-list">
            <button v-for="item in questions" :key="item" class="secondary">{{ item }}</button>
          </div>
        </DataCard>

        <DataCard title="参考资料" subtitle="回答依据和可追溯来源">
          <div class="list">
            <article v-for="item in references" :key="item.title" class="item">
              <strong>{{ item.title }}</strong>
              <p>{{ item.page }}</p>
              <StatusBadge :label="item.type" tone="info" />
            </article>
          </div>
        </DataCard>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.assistant-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
}

.assistant-side,
.chat-list,
.question-list {
  display: grid;
  gap: 12px;
}

.chat-list {
  min-height: 520px;
  align-content: start;
}

.chat-bubble {
  max-width: 76%;
  border-radius: 18px;
  padding: 13px 15px;
  line-height: 1.7;
}

.chat-bubble.user {
  justify-self: end;
  color: #fff;
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.chat-bubble.assistant {
  justify-self: start;
  background: #f8fbff;
  border: 1px solid var(--color-border);
}

.assistant-input {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  margin-top: 14px;
}

@media (max-width: 1180px) {
  .assistant-layout {
    grid-template-columns: 1fr;
  }
}
</style>
