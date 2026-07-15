const { post } = require('../../utils/request');
const { student } = require('../../utils/demoData');

const examples = [
  'break 和 continue 有什么区别？',
  'for 循环怎么遍历列表？',
  'while 循环为什么停不下来？'
];

const statusPills = [
  '课程知识库已加载',
  '支持错因追问',
  '可推荐学习资源'
];

const quickActions = [
  { label: 'break 和 continue 有什么区别？', question: 'break 和 continue 有什么区别？', action: 'question' },
  { label: 'for 循环怎么遍历列表？', question: 'for 循环怎么遍历列表？', action: 'question' },
  { label: 'while 循环为什么停不下来？', question: 'while 循环为什么停不下来？', action: 'question' },
  { label: '生成讲解脚本', question: '', action: 'script' }
];

const reference = '依据课程知识库：Python 程序设计 / 循环结构章节';
let messageId = 0;

function localAnswer(question) {
  if (question.indexOf('break') >= 0 || question.indexOf('continue') >= 0) {
    return 'break 会结束当前循环；continue 会跳过本轮剩余语句进入下一轮。while 循环中使用 continue 时，要特别注意不要跳过变量更新。';
  }
  if (question.indexOf('嵌套') >= 0) {
    return '循环嵌套建议把外层变量和内层变量分列记录。先写每一轮变量变化，再运行代码验证输出。';
  }
  if (question.indexOf('变量变化表') >= 0) {
    return '变量变化表可以按“轮次、条件判断、变量当前值、循环体执行结果、变量更新后值”记录。先填前两轮，再观察规律。';
  }
  if (question.indexOf('for') >= 0 && question.indexOf('列表') >= 0) {
    return 'for 循环遍历列表时，可以写成 for item in list。每一轮 item 会依次取得列表中的元素，适合做累加、筛选和输出。';
  }
  if (question.indexOf('for') >= 0 && question.indexOf('while') >= 0) {
    return '次数明确、遍历序列时优先使用 for；次数不固定、按条件结束时优先使用 while。';
  }
  return 'while 循环一直运行，常见原因是循环条件一直为 True，或循环变量没有在循环体内更新。建议按“初始值、循环条件、变量更新”三步检查。';
}

function makeMessage(role, content, source) {
  return {
    id: `${role}-${messageId++}`,
    role,
    speaker: role === 'ai' ? 'AI 学习助手' : '我',
    avatarText: role === 'ai' ? 'AI' : '我',
    bubbleClass: role === 'ai' ? 'ai-message' : 'user-message',
    content,
    source: source || '',
    suggestions: role === 'ai'
      ? ['复习 while 循环条件更新', '完成变量变化表', '查看课程资料', '咨询教师']
      : []
  };
}

Page({
  data: {
    student,
    examples,
    statusPills,
    quickActions,
    question: '',
    canSend: false,
    loading: false,
    scriptMessage: '',
    messages: [
      makeMessage('ai', '你好，我可以围绕 Python 循环结构回答 while 循环、循环嵌套、break / continue 等问题。', reference)
    ]
  },

  onInput(event) {
    const question = event.detail.value || '';
    this.setData({
      question,
      canSend: !!question.trim()
    });
  },

  useExample(event) {
    const question = event.currentTarget.dataset.question || '';
    this.setData({
      question,
      canSend: !!question.trim()
    });
  },

  handleQuickAction(event) {
    const action = event.currentTarget.dataset.action;
    if (action === 'script') {
      this.generateScript();
      return;
    }
    this.useExample(event);
  },

  handleSuggestion(event) {
    const suggestion = event.currentTarget.dataset.suggestion || '';
    if (suggestion.indexOf('课程资料') >= 0) {
      wx.switchTab({ url: '/pages/resources/index' });
      return;
    }

    const suggestionQuestions = {
      '复习 while 循环条件更新': '请帮我复习 while 循环中条件更新的检查方法。',
      '完成变量变化表': '请带我完成一个 while 循环变量变化表。',
      '咨询教师': '请帮我整理一个可以咨询教师的循环结构问题。'
    };
    const question = suggestionQuestions[suggestion] || suggestion;
    this.setData({
      question,
      canSend: !!question.trim()
    });
  },

  sendQuestion() {
    const question = (this.data.question || '').trim();
    if (!question || this.data.loading) return;
    this.setData({
      question: '',
      canSend: false,
      loading: true,
      messages: this.data.messages.concat(makeMessage('user', question))
    }, () => {
      this.scrollToBottom();
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
        this.setData({ messages: this.data.messages.concat(makeMessage('ai', answer, source)) }, () => {
          this.scrollToBottom();
        });
      })
      .catch(() => {
        wx.showToast({
          title: '当前网络不可用，已为你保留本地学习建议',
          icon: 'none'
        });
        const answer = `${localAnswer(question)} 当前网络不可用，已为你保留本地学习建议。`;
        this.setData({ messages: this.data.messages.concat(makeMessage('ai', answer, reference)) }, () => {
          this.scrollToBottom();
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  generateScript() {
    this.setData({
      scriptMessage: '先说明循环目标，再标注初始值、循环条件、循环体和变量更新，最后用一组输入输出样例验证。'
    });
  },

  scrollToBottom() {
    const scroll = () => {
      if (wx.pageScrollTo) {
        wx.pageScrollTo({
          selector: '#chat-bottom',
          duration: 240
        });
      }
    };
    if (wx.nextTick) {
      wx.nextTick(scroll);
      return;
    }
    setTimeout(scroll, 50);
  }
});
