const { generatedResourcePack, recommendedResources } = require('../../utils/demoData');

function withTaskState(resources) {
  const safeResources = resources && resources.length
    ? resources
    : [{ title: 'while 死循环修复案例', resourceType: '代码实操', type: '代码实操', difficulty: '基础', estimatedMinutes: 12, duration: '12 分钟', content: '检查初始值、循环条件和变量更新。', reason: '用于快速补齐 while 循环薄弱点。' }];
  return safeResources.map((item) => ({
    ...item,
    joined: Boolean(item.joined),
    taskText: item.joined ? '已加入今日任务' : '加入今日任务'
  }));
}

Page({
  data: {
    pack: {
      ...(generatedResourcePack || {}),
      resources: withTaskState(generatedResourcePack && generatedResourcePack.resources),
      weakPoints: (generatedResourcePack && generatedResourcePack.weakPoints) || ['while 循环']
    },
    recommendedResources: withTaskState(recommendedResources),
    statusText: '加入今日学习任务',
    taskJoined: false
  },

  onLoad() {
    const safePack = generatedResourcePack || { resources: [], weakPoints: [], resourceCount: 0 };
    this.setData({
      pack: {
        ...safePack,
        packageTitle: safePack.packageTitle || 'Python 循环结构个性化补弱资源包',
        courseName: safePack.courseName || 'Python 程序设计',
        weakPoints: safePack.weakPoints && safePack.weakPoints.length ? safePack.weakPoints : ['while 循环'],
        resources: withTaskState(safePack.resources)
      },
      recommendedResources: withTaskState(recommendedResources)
    });
  },

  goTutor() {
    wx.switchTab({ url: '/pages/tutor/index' });
  },

  addResourceTask(event) {
    const index = Number(event.currentTarget.dataset.index);
    const resources = this.data.pack.resources.slice();
    if (!resources[index] || resources[index].joined) return;
    resources[index] = {
      ...resources[index],
      joined: true,
      taskText: '已加入今日任务'
    };
    this.setData({ 'pack.resources': resources });
    wx.showToast({ title: '已加入今日任务', icon: 'success' });
  },

  pushPack() {
    const resources = this.data.pack.resources.map((item) => ({
      ...item,
      joined: true,
      taskText: '已加入今日任务'
    }));
    this.setData({
      'pack.resources': resources,
      statusText: '已加入今日任务',
      taskJoined: true
    });
    wx.showToast({ title: '已加入今日任务', icon: 'success' });
  }
});
