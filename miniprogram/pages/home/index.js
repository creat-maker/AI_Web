const demoData = require('../../utils/demoData');

const {
  student = {},
  weakPoints = [],
  todayTasks = [],
  recommendedResources = [],
  homeCards = [],
  report = {}
} = demoData;

const fallbackWeakPoints = weakPoints.length ? weakPoints : ['while 循环终止条件', '循环嵌套变量', 'break / continue 区分'];
const fallbackTasks = todayTasks.length
  ? todayTasks
  : [{ title: '完成 while 循环补弱练习', time: '20 分钟', status: '进行中', knowledge: 'while 循环' }];
const fallbackResources = recommendedResources.length
  ? recommendedResources
  : [{ title: 'while 死循环修复案例', type: '代码实操', duration: '12 分钟', icon: '码', reason: '用于检查条件和变量更新。' }];
const cardRoutes = ['/pages/path/index', '/pages/path/index', '/pages/report/index'];
const tabPages = ['/pages/home/index', '/pages/path/index', '/pages/resources/index', '/pages/tutor/index', '/pages/report/index'];

Page({
  data: {
    studentName: student.name || '李明',
    course: 'Python 程序设计 / 循环结构',
    progress: report.progress || 68,
    todayAdvice: '先完成 while 循环终止条件补全，再复盘 break / continue 输出题。',
    homeCards: (homeCards.length ? homeCards : [
      { title: '今日学习建议', label: '优先级最高', content: '先完成 while 循环补全题，再做 break / continue 输出判断。', action: '开始' },
      { title: '继续学习', label: '上次停在 56%', content: '继续完成 while 循环补弱路径。', action: '继续' },
      { title: '薄弱知识点', label: '持续跟踪', content: 'while 条件更新、循环嵌套变量和控制语句仍需复盘。', action: '查看' }
    ]).map((item, index) => ({
      ...item,
      path: cardRoutes[index] || '/pages/path/index'
    })),
    stats: [
      { label: '章节正确率', value: '67%' },
      { label: '风险等级', value: student.level || '学习状态：需巩固' },
      { label: '补弱资源', value: '7 类' },
      { label: '学习进度', value: `${report.progress || 68}%` }
    ],
    weakPoints: fallbackWeakPoints,
    tasks: fallbackTasks.map((item) => ({
      ...item,
      detail: `${item.knowledge} / ${item.time}`
    })),
    resources: fallbackResources,
    aiAdvice: report.summary || '系统建议先修复 while 循环条件和变量更新，再进入循环嵌套综合练习。',
    shortcuts: [
      { name: '一人一堂路径', path: '/pages/path/index', style: 'primary' },
      { name: '补弱资源包', path: '/pages/resources/index' },
      { name: 'AI 学伴', path: '/pages/tutor/index' },
      { name: '形成性报告', path: '/pages/report/index' }
    ]
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
