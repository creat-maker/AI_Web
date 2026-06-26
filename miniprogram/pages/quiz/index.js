const { post } = require('../../utils/request');
const { quizResult } = require('../../utils/demoData');

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
    title: '循环结构测评',
    question: '下面哪一项最容易导致 while 循环无法结束？',
    options: ['循环体中更新变量', '循环条件最终变为 False', '循环变量没有更新', '使用 for 遍历列表'],
    selected: '',
    selectedStatus: '待选择',
    submitting: false,
    submitDisabled: false,
    submitted: false,
    result: normalizeResult(quizResult),
    syncMessage: '',
    submitText: '提交测评',
    progressText: '1 / 1',
    progressStyle: 'width: 100%;'
  },

  chooseOption(event) {
    if (this.data.submitted) return;
    this.setData({ selected: event.currentTarget.dataset.value, selectedStatus: '已选择' });
  },

  submitQuiz() {
    if (this.data.submitted || this.data.submitting) return;
    this.setData({ submitting: true, submitDisabled: true });
    post('/quizzes/submit', {
      quiz_id: 1,
      student_profile_id: 1,
      answers: { q1: this.data.selected || '循环变量没有更新' }
    }, null, { loadingText: '提交测评' })
      .then((res) => {
        const normalized = normalizeResult(res.data || res);
        this.applyResult(normalized);
      })
      .catch(() => {
        this.applyResult(normalizeResult(quizResult));
      })
      .finally(() => {
        this.setData({ submitting: false });
      });
  },

  applyResult(result) {
    wx.setStorageSync('latestPathAdjustment', result.path_adjustment);
    wx.setStorageSync('latestQuizResult', result);
    this.setData({
      submitted: true,
      result,
      syncMessage: '系统已根据本次测评表现更新学习路径',
      submitText: '已生成测评反馈',
      submitDisabled: true
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
    this.setData({
      selected: '',
      selectedStatus: '待选择',
      submitting: false,
      submitDisabled: false,
      submitted: false,
      syncMessage: '',
      submitText: '提交测评'
    });
  }
});
