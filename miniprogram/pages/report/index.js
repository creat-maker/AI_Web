const { student, report, weakPoints } = require('../../utils/demoData');

Page({
  data: {
    student,
    report,
    weakPoints
  },
  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  }
});
