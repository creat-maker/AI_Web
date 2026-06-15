const { quizAnalysis, wrongQuestions, recommendedResources } = require('../../utils/demoData');

const safeQuizAnalysis = quizAnalysis || {};
const safeWrongQuestions = wrongQuestions && wrongQuestions.length ? wrongQuestions : [
  { course: 'Python 程序设计', title: 'while 循环变量更新', answer: '检查循环体是否推进变量。', status: '待复习', cause: '循环终止条件不清' }
];
const safeResources = recommendedResources && recommendedResources.length ? recommendedResources : [
  { title: 'while 循环条件更新专项练习', type: '专项练习', duration: '20 分钟', reason: '针对死循环和变量更新遗漏。' }
];

Page({
  data: {
    title: '循环结构专项测验',
    score: safeQuizAnalysis.score || 67,
    accuracy: `${safeQuizAnalysis.score || 67}%`,
    weakPoints: safeQuizAnalysis.weakPoints && safeQuizAnalysis.weakPoints.length ? safeQuizAnalysis.weakPoints : ['while 循环条件更新', '循环嵌套变量变化', 'break / continue 区分'],
    causes: safeQuizAnalysis.causes && safeQuizAnalysis.causes.length ? safeQuizAnalysis.causes : ['循环终止条件不清'],
    nextStep: safeQuizAnalysis.nextStep || '完成错题复盘后进入下一步补弱路径。',
    recommendedResources: safeResources,
    wrongQuestions: safeWrongQuestions,
    submitted: false,
    submitText: '提交测验并查看错因',
    syncMessage: ''
  },

  onLoad() {
    this.setData({
      score: safeQuizAnalysis.score || 67,
      accuracy: `${safeQuizAnalysis.score || 67}%`,
      weakPoints: safeQuizAnalysis.weakPoints && safeQuizAnalysis.weakPoints.length ? safeQuizAnalysis.weakPoints : ['while 循环条件更新', '循环嵌套变量变化', 'break / continue 区分'],
      causes: safeQuizAnalysis.causes && safeQuizAnalysis.causes.length ? safeQuizAnalysis.causes : ['循环终止条件不清'],
      nextStep: safeQuizAnalysis.nextStep || '完成错题复盘后进入下一步补弱路径。',
      recommendedResources: safeResources,
      wrongQuestions: safeWrongQuestions
    });
  },

  submitQuiz() {
    if (this.data.submitted) return;
    this.setData({
      submitted: true,
      submitText: '错因已生成，可查看报告',
      syncMessage: '已同步更新学习建议'
    });
    wx.showToast({ title: '已生成错因分析', icon: 'success' });
    setTimeout(() => {
      wx.setStorageSync('reportFromQuiz', true);
      wx.switchTab({ url: '/pages/report/index' });
    }, 1300);
  },

  goReport() {
    wx.switchTab({ url: '/pages/report/index' });
  }
});
