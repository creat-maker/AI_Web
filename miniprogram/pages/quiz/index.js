const { post } = require('../../utils/request');
const { quizResult, resourcePack } = require('../../utils/demoData');

function normalizeResult(data) {
  const source = data || quizResult;
  const adjustment = source.path_adjustment || source.pathAdjustment || quizResult.path_adjustment;
  return {
    score: source.score || quizResult.score,
    accuracy: source.accuracy ? `${source.accuracy}%`.replace('%%', '%') : quizResult.accuracy,
    weak_points: source.weak_points || source.weakPoints || quizResult.weak_points,
    error_analysis: source.error_analysis || source.mistakeReasons || source.mistake_reasons || quizResult.error_analysis,
    path_adjustment_needed: source.path_adjustment_needed !== undefined ? source.path_adjustment_needed : true,
    path_adjustment: {
      adjusted: adjustment.adjusted !== undefined ? adjustment.adjusted : true,
      reason: adjustment.reason || adjustment.summary || quizResult.path_adjustment.reason,
      added_tasks: adjustment.added_tasks || adjustment.addedTasks || quizResult.path_adjustment.added_tasks,
      recommended_resources: adjustment.recommended_resources || adjustment.recommendedResources || quizResult.path_adjustment.recommended_resources,
      next_step: adjustment.next_step || adjustment.nextStep || quizResult.path_adjustment.next_step
    }
  };
}

Page({
  data: {
    title: '循环结构专项测验',
    question: '下面哪一项最容易导致 while 循环无法结束？',
    options: ['循环体中更新变量', '循环条件最终变为 False', '循环变量没有更新', '使用 for 遍历列表'],
    selected: '',
    submitted: false,
    result: normalizeResult(quizResult),
    syncMessage: '',
    submitText: '提交测验'
  },

  chooseOption(event) {
    if (this.data.submitted) return;
    this.setData({ selected: event.currentTarget.dataset.value });
  },

  submitQuiz() {
    if (this.data.submitted) return;
    post('/quizzes/submit', {
      quiz_id: 1,
      student_profile_id: 1,
      answers: { q1: this.data.selected || '循环变量没有更新' }
    }, null, { loadingText: '提交测验' })
      .then((res) => {
        const normalized = normalizeResult(res.data || res);
        this.applyResult(normalized);
      })
      .catch(() => {
        this.applyResult(normalizeResult(quizResult));
      });
  },

  applyResult(result) {
    wx.setStorageSync('latestPathAdjustment', result.path_adjustment);
    wx.setStorageSync('latestQuizResult', result);
    this.setData({
      submitted: true,
      result,
      syncMessage: '系统已根据本次测评表现更新学习路径',
      submitText: '已生成测评反馈'
    });
    wx.showToast({ title: '已更新路径', icon: 'success' });
  },

  goResources() {
    wx.switchTab({ url: '/pages/resources/index' });
  },

  goPath() {
    wx.switchTab({ url: '/pages/path/index' });
  },

  resetQuiz() {
    this.setData({ selected: '', submitted: false, syncMessage: '', submitText: '提交测验' });
  }
});
