const { student, report, mastery, quizAnalysis } = require('../../utils/demoData');

Page({
  data: {
    student: student || { name: '李明' },
    reportTitle: 'Python 循环结构形成性评价报告',
    mastery: report.progress || 68,
    accuracy: `${quizAnalysis.score || 67}%`,
    studyTime: report.studyTime || '12h 24m',
    completion: report.completion || '18 / 24',
    summary: report.summary || '本次循环结构形成性评价已生成。',
    causes: quizAnalysis.causes || ['循环终止条件不清'],
    abilities: [
      { name: '概念理解', value: 66 },
      { name: '代码应用', value: 58 },
      { name: '答题稳定性', value: 61 },
      { name: '学习活跃度', value: 78 },
      { name: '资源利用率', value: 72 },
      { name: '知识迁移能力', value: 55 }
    ],
    weakRanks: mastery,
    suggestions: report.suggestions,
    nextPlan: [
      { title: 'while 循环补全题', detail: '先写变量变化表，再运行代码验证。' },
      { title: 'break / continue 对比题', detail: '通过输出结果判断跳出和跳过的区别。' },
      { title: '循环嵌套综合任务', detail: '补全九九乘法表并解释内外层变量变化。' }
    ],
    records: [
      { date: '06-11', title: '循环结构专项测验', result: '正确率 67%' },
      { date: '06-10', title: 'while 死循环修复案例', result: '已完成' }
    ],
    formativeItems: [
      { title: '形成性评价', detail: '本次测验显示循环结构掌握仍不稳定，需要继续巩固 while 条件更新和循环嵌套变量变化。' },
      { title: '错因摘要', detail: '主要问题集中在变量更新遗漏、内外层变量混用和 break / continue 作用范围混淆。' },
      { title: '下一步建议', detail: '先完成 while 循环补全题，再做 break / continue 输出判断，最后进入循环嵌套综合任务。' }
    ]
  },

  onLoad() {
    this.refreshReport();
  },

  onShow() {
    if (wx.getStorageSync('reportFromQuiz')) {
      wx.removeStorageSync('reportFromQuiz');
      wx.showToast({ title: '报告已更新', icon: 'success' });
    }
    this.refreshReport();
  },

  refreshReport() {
    this.setData({
      suggestions: report.suggestions && report.suggestions.length ? report.suggestions : ['每天完成 20 分钟 while 循环专项练习'],
      weakRanks: mastery && mastery.length ? mastery : [{ name: 'while 循环', value: 48, status: '薄弱' }],
      causes: quizAnalysis.causes && quizAnalysis.causes.length ? quizAnalysis.causes : ['循环终止条件不清'],
      summary: report.summary || '本次循环结构形成性评价已生成。',
      formativeItems: this.data.formativeItems && this.data.formativeItems.length ? this.data.formativeItems : [
        { title: '形成性评价', detail: '本次循环结构形成性评价已生成。' },
        { title: '下一步建议', detail: '继续完成 while 循环专项练习。' }
      ]
    });
  },

  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  },

  goTutor() {
    wx.switchTab({ url: '/pages/tutor/index' });
  }
});
