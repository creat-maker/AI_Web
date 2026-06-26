const { student, homeStats, learningPath, resourcePack, report } = require('../../utils/demoData');

const tabPages = ['/pages/home/index', '/pages/path/index', '/pages/resources/index', '/pages/tutor/index', '/pages/report/index'];
const entryMeta = [
  { icon: '画', accent: 'blue' },
  { icon: '路', accent: 'purple' },
  { icon: '资', accent: 'green' },
  { icon: '问', accent: 'cyan' },
  { icon: '测', accent: 'orange' },
  { icon: '报', accent: 'indigo' }
];

Page({
  data: {
    studentName: student.name,
    courseTitle: 'Python 程序设计',
    chapterTitle: '循环结构',
    positioning: '学生端移动学习入口',
    subtitle: '围绕 Python 循环结构的个性化学习闭环',
    flowText: '画像诊断 -> 学习路径 -> 资源推荐 -> 智能答疑 -> 测验评价 -> 学习报告',
    flowSteps: ['画像诊断', '学习路径', '资源推荐', '智能答疑', '测验评价', '学习报告'],
    stats: homeStats,
    entries: [
      { name: '画像诊断', desc: '查看 6 维对话式学习画像', path: '/pages/profile-dialog/index' },
      { name: '学习路径', desc: '按章节推进补弱任务', path: '/pages/path/index' },
      { name: '学习资源', desc: '查看 9 类多模态资源', path: '/pages/resources/index' },
      { name: '智能答疑', desc: '围绕循环结构提问', path: '/pages/tutor/index' },
      { name: '测验评价', desc: '提交练习并更新路径', path: '/pages/quiz/index' },
      { name: '学习报告', desc: '查看诊断报告和建议', path: '/pages/report/index' }
    ].map((item, index) => ({
      ...item,
      icon: entryMeta[index].icon,
      accent: entryMeta[index].accent
    })),
    currentTask: (() => {
      const task = learningPath.find((item) => item.status === '进行中') || learningPath[2];
      return {
        ...task,
        description: task.description || task.goal
      };
    })(),
    todayAdvice: [
      '先完成 while 循环条件更新动画',
      '再完成 break / continue 对比练习',
      '最后查看学习诊断报告'
    ],
    resourceCount: resourcePack.resourceCount,
    reportSummary: report.summary,
    reportAccuracy: report.accuracy
  },

  goPage(event) {
    const path = event.currentTarget.dataset.path;
    if (!path) return;
    if (tabPages.indexOf(path) >= 0) {
      wx.switchTab({ url: path });
      return;
    }
    wx.navigateTo({ url: path });
  }
});
