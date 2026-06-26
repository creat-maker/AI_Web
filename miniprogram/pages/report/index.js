const { student, report, quizResult } = require('../../utils/demoData');

function reportFromStorage() {
  const latest = wx.getStorageSync('latestQuizResult');
  if (!latest) return report;

  const adjustment = latest.path_adjustment || {};
  return {
    ...report,
    accuracy: latest.accuracy || report.accuracy,
    weakPoints: latest.weak_points || report.weakPoints,
    recommendedResources: adjustment.recommended_resources || report.recommendedResources,
    nextPlan: adjustment.added_tasks || report.nextPlan,
    summary: '学习诊断报告已结合最近一次测评结果更新。',
    teacherAdvice: report.teacherAdvice
  };
}

function buildEvaluationItems(nextReport) {
  return [
    { title: '学习诊断报告', detail: nextReport.summary },
    { title: '形成性评价', detail: '正确率、错因和资源使用情况已用于生成下一步学习计划。' },
    { title: '路径调整依据', detail: quizResult.path_adjustment.reason }
  ];
}

Page({
  data: {
    student,
    report,
    evaluationItems: buildEvaluationItems(report)
  },

  onShow() {
    const nextReport = reportFromStorage();
    this.setData({
      report: nextReport,
      evaluationItems: buildEvaluationItems(nextReport)
    });
  },

  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  },

  goTutor() {
    wx.switchTab({ url: '/pages/tutor/index' });
  }
});
