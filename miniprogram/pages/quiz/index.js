const questions = [
  {
    id: 1,
    title: '下面哪种情况更适合使用 while 循环？',
    options: ['遍历一个固定列表', '不知道循环次数，只知道停止条件', '输出 1 到 10', '遍历字符串中的每个字符'],
    answer: 1,
    answerText: '不知道循环次数，只知道停止条件',
    analysis: 'while 循环适合循环次数不固定，但停止条件明确的场景。'
  },
  {
    id: 2,
    title: '调用 def add(a, b=1): 时，哪个写法是正确的？',
    options: ['add()', 'add(3)', 'add(a=1, 2)', 'add(1, b, 3)'],
    answer: 1,
    answerText: 'add(3)',
    analysis: '参数 a 没有默认值，必须传入；b 有默认值，可以省略。'
  },
  {
    id: 3,
    title: '列表 nums = [1, 2, 3] 执行 nums.append(4) 后结果是？',
    options: ['[4, 1, 2, 3]', '[1, 2, 3, 4]', '[1, 2, 4]', '返回一个新列表，原列表不变'],
    answer: 1,
    answerText: '[1, 2, 3, 4]',
    analysis: 'append 会在原列表末尾追加元素，原列表变为 [1, 2, 3, 4]。'
  }
];

Page({
  data: {
    course: 'Python 程序设计',
    questions,
    selected: {},
    submitted: false,
    score: 0
  },

  chooseAnswer(event) {
    if (this.data.submitted) return;
    const qid = event.currentTarget.dataset.qid;
    const optionIndex = event.currentTarget.dataset.index;
    this.setData({ ['selected.' + qid]: optionIndex });
  },

  submitQuiz() {
    let score = 0;
    questions.forEach((question) => {
      if (this.data.selected[question.id] === question.answer) {
        score += 1;
      }
    });
    this.setData({ submitted: true, score });
  },

  resetQuiz() {
    this.setData({ selected: {}, submitted: false, score: 0 });
  },

  goReport() {
    wx.switchTab({ url: '/pages/report/index' });
  }
});
