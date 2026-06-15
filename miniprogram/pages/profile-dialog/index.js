const { student, weakPoints } = require('../../utils/demoData');

const fallbackWeakPoints = weakPoints && weakPoints.length ? weakPoints : ['while 循环终止条件', '循环嵌套变量', 'break / continue 区分'];

Page({
  data: {
    student: student || { name: '李明' },
    messages: [
      { role: 'ai', content: '你好李明，我会通过几个问题构建你的 Python 循环结构学习画像。' },
      { role: 'user', content: '我写 while 循环时经常不知道为什么会死循环。' },
      { role: 'ai', content: '已识别薄弱点：while 循环终止条件、循环嵌套变量变化、break / continue 区分。' }
    ],
    dimensions: [
      { name: '当前水平', value: '基础薄弱' },
      { name: '学习偏好', value: '代码实操偏好型' },
      { name: '学习状态', value: '需巩固' },
      { name: '主修课程', value: 'Python 程序设计' }
    ],
    weakPoints: fallbackWeakPoints,
    inputValue: ''
  },

  onInput(event) {
    this.setData({ inputValue: event.detail.value });
  },

  sendMessage() {
    const value = this.data.inputValue.trim();
    if (!value) return;
    this.setData({
      inputValue: '',
      messages: this.data.messages.concat(
        { role: 'user', content: value },
        { role: 'ai', content: '已记录你的补充信息，并会用于更新循环结构补弱路径。' }
      )
    });
  },

  goPath() {
    wx.switchTab({ url: '/pages/path/index' });
  }
});
