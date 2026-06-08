Page({
  data: {
    weakPoints: ['循环结构', '函数参数', '列表操作'],
    knowledgeGraph: [
      {
        name: '循环结构',
        progress: 58,
        status: '高频错题',
        action: '进入循环专项视频'
      },
      {
        name: '函数参数',
        progress: 64,
        status: '调用混淆',
        action: '阅读函数参数讲义'
      },
      {
        name: '列表操作',
        progress: 71,
        status: '基本掌握',
        action: '完成巩固练习'
      },
      {
        name: '综合应用',
        progress: 62,
        status: '需要训练',
        action: '开始综合测验'
      }
    ],
    stages: [
      {
        name: '阶段一：基础语法巩固',
        status: '已完成',
        progress: 100,
        goal: '复盘变量、条件判断和基础输入输出，为后续专项训练打底。',
        tasks: ['完成基础语法快测', '订正常见语法错误']
      },
      {
        name: '阶段二：循环与函数专项',
        status: '进行中',
        progress: 62,
        goal: '集中突破循环边界、函数参数传递和返回值理解。',
        tasks: ['循环结构专项 6 题', '函数参数对比练习']
      },
      {
        name: '阶段三：综合练习与测验',
        status: '待开始',
        progress: 0,
        goal: '通过列表操作综合题和测验检验知识迁移能力。',
        tasks: ['列表操作综合题', 'Python 综合测验']
      }
    ]
  },

  goResources() {
    wx.switchTab({ url: '/pages/resources/index' });
  },

  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  }
});
