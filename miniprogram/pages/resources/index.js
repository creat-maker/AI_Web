const { post } = require('../../utils/request');

const generationSteps = [
  '正在分析学习画像',
  '正在匹配薄弱知识点',
  '正在生成视频、文档、练习组合',
  '已生成个性化资源包'
];

const basis = {
  weakPoints: ['循环结构', '函数参数', '列表操作'],
  weakPointsText: '循环结构、函数参数、列表操作',
  accuracy: '72%',
  strategy: '先知识点复习，再专项练习，最后综合测验'
};

const matchReasons = [
  '因为循环结构正确率仅 58%，优先推荐循环专项视频。',
  '因为函数参数题出现调用混淆，推荐函数参数讲义。',
  '因为列表操作已基本掌握，推荐巩固练习。',
  '推荐策略：先知识点复习，再专项练习，最后综合测验。'
];

const demoPack = {
  source: '智能推荐已加载',
  videos: [
    { title: '循环结构边界条件微课', duration: '12 分钟', tag: '视频', reason: '帮助复盘 for / while 的适用场景和终止条件。' },
    { title: '函数参数传递动画讲解', duration: '10 分钟', tag: '视频', reason: '对比位置参数、默认参数和返回值。' }
  ],
  documents: [
    { title: 'Python 函数参数速查表', duration: '8 分钟', tag: '文档', reason: '用于快速复盘易错定义和调用方式。' },
    { title: '列表操作常用方法清单', duration: '6 分钟', tag: '文档', reason: '聚焦 append、切片、索引和遍历。' }
  ],
  practices: [
    { title: '循环结构专项 6 题', duration: '20 分钟', tag: '练习', reason: '围绕循环边界和变量更新进行专项训练。' },
    { title: '列表遍历与切片综合题', duration: '18 分钟', tag: '练习', reason: '完成后进入测验验证掌握情况。' }
  ],
  order: ['先看循环结构微课', '再读函数参数速查表', '完成循环专项题', '最后做列表综合题']
};

function normalizeResources(items, pattern) {
  return (items || []).filter((item) => pattern.test(item.resourceType || item.type || item.title || ''));
}

function normalizePack(data) {
  if (!data) return demoPack;
  const pack = data.data || data;
  const resources = pack.resources || [];
  if (!resources.length && !pack.videos && !pack.documents && !pack.practices) {
    return demoPack;
  }
  return {
    source: '后端接口',
    videos: pack.videos || normalizeResources(resources, /视频|微课/),
    documents: pack.documents || normalizeResources(resources, /文档|讲义|资料|清单/),
    practices: pack.practices || normalizeResources(resources, /练习|任务|测验/),
    order: pack.order || pack.recommendedOrder || ['按视频、文档、练习的顺序完成资源包']
  };
}

Page({
  data: {
    loading: false,
    fromBackend: false,
    generationSteps,
    currentStep: 3,
    basis,
    matchReasons,
    weakPoints: basis.weakPoints,
    pack: demoPack
  },

  onLoad() {
    this.generatePack();
  },

  runGenerationSteps() {
    this.setData({ currentStep: 0 });
    generationSteps.forEach((step, index) => {
      setTimeout(() => {
        if (this.data.loading || index === generationSteps.length - 1) {
          this.setData({ currentStep: index });
        }
      }, index * 420);
    });
  },

  generatePack() {
    if (this.data.loading) return;
    this.setData({ loading: true });
    this.runGenerationSteps();
    post('/api/v1/resources/generate-pack', {
      student_id: 1,
      student_name: '张三',
      course: 'Python 程序设计',
      weak_points: basis.weakPoints
    })
      .then((res) => {
        this.setData({ pack: normalizePack(res), fromBackend: true });
      })
      .catch(() => {
        this.setData({ pack: demoPack, fromBackend: false });
      })
      .finally(() => {
        this.setData({ loading: false, currentStep: generationSteps.length - 1 });
      });
  },

  goQuiz() {
    wx.navigateTo({ url: '/pages/quiz/index' });
  }
});
