const { post } = require('../../utils/request');
const { student } = require('../../utils/demoData');

const examples = [
  '为什么我的 while 循环会一直运行？',
  'break 和 continue 有什么区别？',
  '循环嵌套为什么容易看不懂？',
  'for 循环和 while 循环怎么选择？'
];

const reference = '依据课程知识库：Python 程序设计 / 循环结构章节';

function localAnswer(question) {
  if (question.indexOf('break') >= 0 || question.indexOf('continue') >= 0) {
    return 'break 会结束当前循环；continue 会跳过本轮剩余语句进入下一轮。while 循环中使用 continue 时，要特别注意不要跳过变量更新。';
  }
  if (question.indexOf('嵌套') >= 0) {
    return '循环嵌套建议把外层变量和内层变量分列记录。先写每一轮变量变化，再运行代码验证输出。';
  }
  if (question.indexOf('for') >= 0 && question.indexOf('while') >= 0) {
    return '次数明确、遍历序列时优先使用 for；次数不固定、按条件结束时优先使用 while。';
  }
  return 'while 循环一直运行，常见原因是循环条件一直为 True，或循环变量没有在循环体内更新。建议按“初始值、循环条件、变量更新”三步检查。';
}

function makeMessage(role, content, source) {
  return {
    role,
    content,
    source: source || '',
    suggestions: role === 'ai'
      ? ['复习 while 循环条件更新', '完成变量变化表', '查看课程资料或咨询教师']
      : []
  };
}

Page({
  data: {
    student,
    examples,
    question: examples[0],
    loading: false,
    scriptMessage: '',
    messages: [
      makeMessage('ai', '你好，我可以围绕 Python 循环结构回答 while 循环、循环嵌套、break / continue 等问题。', reference)
    ]
  },

  onInput(event) {
    this.setData({ question: event.detail.value });
  },

  useExample(event) {
    this.setData({ question: event.currentTarget.dataset.question || '' });
  },

  sendQuestion() {
    const question = (this.data.question || '').trim();
    if (!question || this.data.loading) return;
    this.setData({
      question: '',
      loading: true,
      messages: this.data.messages.concat(makeMessage('user', question))
    });

    post('/rag/ask', {
      question,
      user_id: student.id,
      course_id: 'python-programming'
    }, null, { loadingText: '生成回答' })
      .then((res) => {
        const data = res.data || res;
        const answer = data.answer || data.content || localAnswer(question);
        const source = data.citations && data.citations.length ? '依据课程知识库和引用片段' : reference;
        this.setData({ messages: this.data.messages.concat(makeMessage('ai', answer, source)) });
      })
      .catch(() => {
        this.setData({ messages: this.data.messages.concat(makeMessage('ai', localAnswer(question), reference)) });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  generateScript() {
    this.setData({ scriptMessage: '讲解脚本已生成：先定位循环条件，再追踪变量更新，最后用练习题验证。' });
  }
});
