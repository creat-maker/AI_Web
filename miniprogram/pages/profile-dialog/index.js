const { post } = require('../../utils/request');
const { student, profileDimensions } = require('../../utils/demoData');

function normalizeDimensions(rows) {
  const source = rows && rows.length ? rows : profileDimensions;
  return source.map((item) => ({
    name: item.name || item.label || item.key,
    explanation: item.explanation || item.description || '对话式画像维度，随学习过程持续更新。',
    judgement: item.judgement || item.value || '已形成当前判断。',
    strategy: item.strategy || '根据当前判断推荐匹配的学习资源和路径。'
  }));
}

Page({
  data: {
    student,
    sourceLabel: '对话式画像构建',
    updateNote: '画像会随测验、答疑和资源使用记录持续更新。',
    messages: [
      { role: 'ai', content: '你好李明，我会通过对话构建你的 Python 循环结构学习画像。' },
      { role: 'user', content: '我写 while 循环时，经常不知道为什么会死循环。' },
      { role: 'ai', content: '已记录你的主要薄弱点：while 循环条件更新、循环嵌套变量变化、break / continue 区分。' }
    ],
    dimensions: normalizeDimensions(profileDimensions),
    weakPoints: ['while 循环', '循环嵌套', 'break / continue'],
    inputValue: '',
    loading: false
  },

  onLoad() {
    this.loadProfile();
  },

  loadProfile() {
    this.setData({ loading: true });
    post('/profile-dialog/run', {
      studentId: student.id,
      studentName: student.name,
      courseName: student.course,
      answer: '我正在学习 Python 循环结构，while 循环和循环嵌套比较薄弱。'
    }, null, { loadingText: '同步画像' })
      .then((res) => {
        const data = res.data || res;
        this.setData({
          sourceLabel: '对话式画像构建',
          dimensions: normalizeDimensions(data.dimensions),
          weakPoints: data.weak_points || data.weakKnowledgePoints || this.data.weakPoints
        });
      })
      .catch(() => {
        this.setData({ sourceLabel: '初始化画像样例', dimensions: normalizeDimensions(profileDimensions) });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  onInput(event) {
    this.setData({ inputValue: event.detail.value });
  },

  sendMessage() {
    const value = (this.data.inputValue || '').trim();
    if (!value) return;
    this.setData({
      inputValue: '',
      messages: this.data.messages.concat(
        { role: 'user', content: value },
        { role: 'ai', content: '已记录补充信息，并会用于更新循环结构补弱路径。' }
      )
    });
  },

  goPath() {
    wx.switchTab({ url: '/pages/path/index' });
  }
});
