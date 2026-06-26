const { student, learningPath, quizResult } = require('../../utils/demoData');

function decoratePath(rows) {
  return rows.map((item) => ({
    ...item,
    resourceText: (item.resources || []).join('、')
  }));
}

function normalizeAdjustment(value) {
  const source = value || quizResult.path_adjustment;
  return {
    adjusted: source.adjusted !== false,
    adjustedText: source.adjusted !== false ? '已调整' : '保持原路径',
    reason: source.reason || quizResult.path_adjustment.reason,
    added_tasks: source.added_tasks || source.addedTasks || quizResult.path_adjustment.added_tasks,
    recommended_resources: source.recommended_resources || source.recommendedResources || quizResult.path_adjustment.recommended_resources,
    next_step: source.next_step || source.nextStep || quizResult.path_adjustment.next_step
  };
}

Page({
  data: {
    student,
    pathTitle: 'Python 循环结构专项学习路径',
    learningPath: decoratePath(learningPath),
    adjustment: normalizeAdjustment(),
    updateMessage: '学习路径会根据测评表现持续调整。'
  },

  onShow() {
    const latest = wx.getStorageSync('latestPathAdjustment');
    this.setData({
      adjustment: normalizeAdjustment(latest),
      updateMessage: latest ? '已读取最近一次测评后的路径调整。' : '当前展示循环结构专项路径。'
    });
  },

  goResources() {
    wx.switchTab({ url: '/pages/resources/index' });
  },

  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  }
});
