Page({
  data: {
    studentName: '张三',
    course: 'Python 程序设计',
    todayTaskCount: 4,
    progress: 68,
    todayAdvice: '先复习循环结构，再完成函数参数专项训练',
    weakPoints: ['循环结构', '函数参数', '列表操作'],
    stats: [
      { label: '今日任务', value: '4 项' },
      { label: '综合掌握度', value: '68%' },
      { label: '最近正确率', value: '76%' },
      { label: '连续学习', value: '6 天' }
    ],
    tasks: [
      { title: '循环结构错题复盘', status: '进行中', detail: '完成 3 道边界条件题，识别循环终止条件' },
      { title: '函数参数专项训练', status: '待开始', detail: '区分形参、实参、默认参数和返回值' },
      { title: '列表操作微课', status: '已安排', detail: '复习切片、遍历、append 与索引范围' }
    ],
    aiAdvice: 'EduMind 根据近期测验和错题标签，判断你在循环边界、函数参数传递、列表追加三个知识点上掌握度偏低。今日建议按“复习知识点 - 专项练习 - 测验验证”的顺序完成。',
    personalizedTasks: [
      { title: '复习循环结构', time: '预计 8 分钟', priority: '高', status: '待完成', path: '/pages/path/index' },
      { title: '完成函数参数专项练习', time: '预计 12 分钟', priority: '高', status: '待完成', path: '/pages/quiz/index' },
      { title: '查看 AI 推荐资源', time: '预计 5 分钟', priority: '中', status: '待完成', path: '/pages/resources/index' },
      { title: '完成课后小测', time: '预计 10 分钟', priority: '中', status: '待完成', path: '/pages/quiz/index' }
    ],
    shortcuts: [
      { name: '开始今日任务', path: '/pages/path/index', style: 'primary' },
      { name: '生成资源包', path: '/pages/resources/index', style: 'secondary' },
      { name: '咨询 AI 助教', path: '/pages/tutor/index', style: 'secondary' },
      { name: '查看学习报告', path: '/pages/report/index', style: 'secondary' },
      { name: '画像构建', path: '/pages/profile-dialog/index', style: 'secondary' }
    ]
  },

  goPage(event) {
    const path = event.currentTarget.dataset.path;
    if (!path) return;
    const tabPages = ['/pages/home/index', '/pages/path/index', '/pages/resources/index', '/pages/tutor/index', '/pages/report/index'];
    if (tabPages.indexOf(path) >= 0) {
      wx.switchTab({ url: path });
      return;
    }
    wx.navigateTo({ url: path });
  }
});
