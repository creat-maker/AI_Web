const { student, dkvmnSummary, report, quizResult } = require('../../utils/demoData');
const { getReports } = require('../../utils/api');

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
    { title: '学习摘要', detail: nextReport.summary },
    { title: '错因分析', detail: '正确率、错因和资源使用情况已用于生成下一步学习计划。' },
    { title: '路径调整依据', detail: quizResult.path_adjustment.reason }
  ];
}

Page({
  data: {
    student,
    report,
    dkvmn: {
      masteryText: `${Math.round(dkvmnSummary.averageMastery * 100)}%`,
      weakText: dkvmnSummary.weakConcepts.join('、'),
      reason: dkvmnSummary.latestReason
    },
    evaluationItems: buildEvaluationItems(report),
    generatedAt: '今日更新',
    sourceLabel: '本地演示数据 fallback',
    loading: false,
    errorMessage: '',
    emptyMessage: '',
    previewUrl: '',
    downloadUrl: ''
  },

  onShow() {
    const nextReport = reportFromStorage();
    this.setData({
      report: nextReport,
      evaluationItems: buildEvaluationItems(nextReport)
    });
    this.loadReport();
  },

  loadReport() {
    this.setData({ loading: true, errorMessage: '', emptyMessage: '' });
    getReports()
      .then((res) => {
        const payload = res.data || res;
        const rows = Array.isArray(payload) ? payload : payload.items || payload.reports || [];
        const latest = rows[0] || payload;
        if (!latest || (Array.isArray(rows) && rows.length === 0 && !payload.report_id)) {
          this.setData({ emptyMessage: '暂无后端报告，展示本地诊断摘要。' });
          return;
        }
        const nextReport = {
          ...this.data.report,
          title: latest.report_title || latest.title || this.data.report.title,
          summary: latest.profile_summary || latest.summary || this.data.report.summary,
          weakPoints: latest.weak_concepts || latest.weakPoints || this.data.report.weakPoints,
          recommendedResources: latest.resource_recommendations || latest.recommendedResources || this.data.report.recommendedResources,
          teacherAdvice: Array.isArray(latest.teacher_suggestions) ? latest.teacher_suggestions.join('；') : latest.teacher_suggestions || this.data.report.teacherAdvice,
          exportNote: latest.export_path ? `报告已生成：${latest.export_path}` : this.data.report.exportNote
        };
        this.setData({
          report: nextReport,
          evaluationItems: buildEvaluationItems(nextReport),
          generatedAt: latest.generated_at || latest.created_at || '今日更新',
          sourceLabel: res.fallback ? '本地演示数据 fallback' : '后端 API',
          previewUrl: latest.preview_url || latest.download_url || '',
          downloadUrl: latest.download_url || ''
        });
      })
      .catch((error) => {
        this.setData({ errorMessage: error.friendlyMessage || '后端报告暂不可用，展示本地诊断摘要。', sourceLabel: '本地演示数据 fallback' });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  },

  goTutor() {
    wx.switchTab({ url: '/pages/tutor/index' });
  },

  previewReport() {
    wx.showToast({ title: this.data.previewUrl ? '预览入口已就绪' : '当前为本地预览', icon: 'none' });
  },

  downloadReport() {
    wx.showToast({ title: this.data.downloadUrl ? '下载入口已就绪' : '当前为本地报告', icon: 'none' });
  }
});
