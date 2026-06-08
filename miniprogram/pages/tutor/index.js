const { post } = require('../../utils/request');

const examples = [
  'Python 中 for 循环和 while 循环有什么区别？',
  '函数参数为什么会传错？',
  '如何提升列表操作题的正确率？'
];

const referenceBasis = {
  knowledgeBase: 'Python 程序设计',
  points: '循环结构 / 函数参数 / 列表操作',
  profile: '当前知识点掌握度偏低',
  wrongQuestions: '条件判断、参数传递、列表追加'
};

const followUpSuggestions = [
  '能不能举一个 for 循环例子？',
  'while 循环什么时候容易死循环？',
  '给我出一道循环结构练习题。'
];

function fallbackAnswer(question) {
  if (question.indexOf('while') >= 0 || question.indexOf('for') >= 0 || question.indexOf('循环') >= 0) {
    return 'for 循环更适合遍历已知序列，例如列表或 range；while 循环适合条件满足时持续执行。做题时先判断循环次数是否明确，再检查终止条件是否会被更新。';
  }
  if (question.indexOf('参数') >= 0) {
    return '函数参数常见错误包括实参数量不匹配、默认参数位置错误、把返回值和打印混淆。建议先写函数定义，再逐个标注每个参数的含义和调用时传入的值。';
  }
  if (question.indexOf('列表') >= 0) {
    return '列表题要先确认索引范围，再区分遍历元素和值的位置。练习时重点复盘 append、切片、len 和 for item in list 的用法。';
  }
  return '建议把问题拆成知识点、代码现象和期望结果三部分。你可以先写出最小代码片段，再对照输出定位错误。';
}

function makeAiMessage(content, source) {
  return {
    role: 'ai',
    content,
    source,
    references: referenceBasis,
    followUps: followUpSuggestions
  };
}

Page({
  data: {
    examples,
    question: '',
    loading: false,
    fromBackend: false,
    messages: [
      makeAiMessage('你好，我是 EduMind AI 助教。可以结合你的学习画像，讲解 Python 循环、函数参数和列表操作，并给出下一步练习建议。', '离线服务')
    ]
  },

  onInput(event) {
    this.setData({ question: event.detail.value });
  },

  useExample(event) {
    this.setData({ question: event.currentTarget.dataset.question || '' });
  },

  useFollowUp(event) {
    this.setData({ question: event.currentTarget.dataset.question || '' });
  },

  sendQuestion() {
    const question = this.data.question.trim();
    if (!question || this.data.loading) return;

    const userMessage = { role: 'user', content: question };
    this.setData({
      question: '',
      loading: true,
      messages: this.data.messages.concat(userMessage)
    });

    post('/api/v1/rag/ask', {
      question,
      student_id: 1,
      student_name: '张三',
      course: 'Python 程序设计'
    })
      .then((res) => {
        const data = res.data || res;
        const answer = data.answer || data.content || fallbackAnswer(question);
        this.setData({
          fromBackend: true,
          messages: this.data.messages.concat(makeAiMessage(answer, '后端 RAG'))
        });
      })
      .catch(() => {
        this.setData({
          fromBackend: false,
          messages: this.data.messages.concat(makeAiMessage(fallbackAnswer(question), '离线服务'))
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  }
});
