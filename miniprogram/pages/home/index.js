const { student, courses, weakPoints, todayTasks, report } = require('../../utils/demoData');

Page({
  data: {
    student,
    courses,
    weakPoints,
    todayTasks,
    report
  },
  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  }
});
