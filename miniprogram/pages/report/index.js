const { student, report, weakPoints, mastery } = require('../../utils/demoData');

Page({
  data: {
    student,
    report,
    weakPoints,
    mastery
  },
  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  }
});
