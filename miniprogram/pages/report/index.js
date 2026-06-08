Page({
  data: {
    progress: 68,
    mastery: 68,
    studyTime: '12.5 小时',
    accuracy: '76%',
    weakRanks: [
      { name: '循环结构', value: 58, risk: '高频错题' },
      { name: '函数参数', value: 64, risk: '调用混淆' },
      { name: '列表操作', value: 70, risk: '索引易错' }
    ],
    profileUpdate: '系统已根据测验结果、资源学习记录和知识点掌握度更新学习画像。',
    abilities: [
      { name: '代码阅读能力', value: 72 },
      { name: '逻辑推理能力', value: 65 },
      { name: '调试纠错能力', value: 61 },
      { name: '综合应用能力', value: 58 }
    ],
    trends: [
      { date: '06-01', value: 42 },
      { date: '06-02', value: 50 },
      { date: '06-03', value: 46 },
      { date: '06-04', value: 58 },
      { date: '06-05', value: 62 },
      { date: '06-06', value: 66 },
      { date: '今日', value: 72 }
    ],
    suggestions: [
      '循环结构先画变量变化表，再运行代码验证边界条件。',
      '函数题先确认参数数量、默认值和返回值，不要把 print 当作 return。',
      '列表操作重点练习索引、切片、遍历和 append 的原地修改。'
    ],
    nextPlan: [
      { title: '复习循环结构', detail: '完成 12 分钟微课和 3 道边界条件题' },
      { title: '函数参数专项', detail: '完成默认参数、位置参数对比练习' },
      { title: '综合测验验证', detail: '提交测验后更新学习画像和下一轮推荐' }
    ],
    records: [
      { date: '06-06', title: '完成循环结构专项练习', result: '正确率 78%' },
      { date: '06-05', title: '观看函数参数微课', result: '学习 18 分钟' },
      { date: '06-04', title: '提交列表操作测验', result: '错题 2 道' }
    ]
  },

  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  },

  goTutor() {
    wx.switchTab({ url: '/pages/tutor/index' });
  }
});
