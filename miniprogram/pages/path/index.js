const { student, learningPath } = require('../../utils/demoData');

const fallbackPath = [
  {
    profileType: '基础薄弱 + 代码实操偏好型',
    title: 'while 循环补弱',
    goal: '能判断循环是否会终止。',
    knowledge: 'while 循环',
    resource: 'while 死循环修复案例',
    practice: '完成 3 道补全题。',
    aiAdvice: '先写变量变化表，再运行代码。',
    status: '进行中',
    percent: 56
  }
];

Page({
  data: {
    student: student || { name: '李明' },
    pathTitle: '李明的一人一堂循环结构补弱路径',
    learningPath: learningPath && learningPath.length ? learningPath : fallbackPath,
    updateMessage: '学习路径已根据最近一次循环结构测验更新。'
  },

  onLoad() {
    this.setData({
      student: student || { name: '李明' },
      learningPath: learningPath && learningPath.length ? learningPath : fallbackPath,
      updateMessage: '学习路径已根据最近一次循环结构测验更新。'
    });
  },

  goResources() {
    wx.switchTab({ url: '/pages/resources/index' });
  }
});
