const { post } = require('../../utils/request');
const { student, resourcePack, resourceTypeLabels } = require('../../utils/demoData');

const resourceTypeMeta = {
  handout: { icon: '讲', className: 'type-blue', audience: '基础复习' },
  mindmap: { icon: '图', className: 'type-purple', audience: '结构梳理' },
  quiz: { icon: '练', className: 'type-orange', audience: '测后巩固' },
  animation_html: { icon: '动', className: 'type-cyan', audience: '步骤理解' },
  video_script: { icon: '稿', className: 'type-indigo', audience: '讲解复盘' },
  tts_audio: { icon: '听', className: 'type-green', audience: '通勤复习' },
  video_mp4: { icon: '视', className: 'type-red', audience: '视频学习' },
  code_case: { icon: '码', className: 'type-slate', audience: '实操训练' },
  project_task: { icon: '项', className: 'type-teal', audience: '综合应用' }
};

function normalizeResource(item) {
  const type = item.resource_type || item.resourceType || 'handout';
  const label = resourceTypeLabels[type] || item.resourceType || item.type || '学习资源';
  const knowledgePoints = item.knowledgePoints || item.knowledge_points || item.relatedKnowledgePoints || ['循环结构'];
  const meta = resourceTypeMeta[type] || resourceTypeMeta.handout;
  let note = item.description || item.content || '';

  if (type === 'animation_html') {
    note = item.mobileNote || 'Web 端可预览动画，小程序端展示动画步骤与学习要点。';
  }

  if (type === 'tts_audio') {
    const ttsResult = item.tts_result || {};
    const ttsStatus = item.tts_status || {};
    note = ttsResult.message || ttsStatus.message || '已生成讲解文本，生产环境可接入科大讯飞 TTS。';
  }

  if (type === 'video_mp4') {
    note = item.status === 'generated'
      ? `可生成 MP4：${item.file_path || '视频文件'}`
      : '当前运行环境未检测到 FFmpeg 时，系统已提供 HTML 动画与视频脚本。';
  }

  return {
    ...item,
    type,
    label,
    icon: meta.icon,
    typeClass: meta.className,
    audience: item.audience || meta.audience,
    title: item.title || label,
    content: item.content || item.description || label,
    knowledgeText: knowledgePoints.join('、'),
    knowledgeTags: knowledgePoints,
    difficultyText: item.difficulty || '基础',
    estimateText: item.estimatedMinutes || 15,
    note,
    joined: false,
    taskText: '加入学习'
  };
}

function normalizePack(pack) {
  const source = pack && pack.resources && pack.resources.length ? pack : resourcePack;
  return {
    ...source,
    packageTitle: source.packageTitle || 'Python 循环结构个性化补弱资源包',
    courseName: source.courseName || student.course,
    chapter: source.chapter || student.chapter,
    weakPoints: source.weakPoints || source.weak_points || resourcePack.weakPoints,
    resourceCount: source.resourceCount || source.resource_type_count || source.resources.length,
    resources: source.resources.map(normalizeResource)
  };
}

Page({
  data: {
    pack: normalizePack(resourcePack),
    keyword: '循环',
    typeFilter: '全部',
    typeOptions: ['全部'].concat(Object.values(resourceTypeLabels)),
    filteredResources: normalizePack(resourcePack).resources,
    emptyText: '',
    sourceMessage: ''
  },

  onLoad() {
    this.loadResources();
  },

  loadResources() {
    post('/resources/generate-pack', {
      studentId: student.id,
      courseId: 'python-programming',
      courseName: student.course,
      knowledgePoints: resourcePack.weakPoints,
      learningGoal: student.goal
    }, null, { loadingText: '加载资源' })
      .then((res) => {
        const pack = normalizePack(res.data || res);
        this.setData({ pack, sourceMessage: '' });
        this.applyFilter();
      })
      .catch(() => {
        this.setData({ pack: normalizePack(resourcePack), sourceMessage: '当前展示初始化课程资源。' });
        this.applyFilter();
      });
  },

  onKeyword(event) {
    this.setData({ keyword: event.detail.value });
    this.applyFilter();
  },

  onTypeChange(event) {
    this.setData({ typeFilter: this.data.typeOptions[Number(event.detail.value)] || '全部' });
    this.applyFilter();
  },

  clearFilter() {
    this.setData({ keyword: '', typeFilter: '全部' });
    this.applyFilter();
  },

  applyFilter() {
    const word = (this.data.keyword || '').trim().toLowerCase();
    const typeFilter = this.data.typeFilter;
    const rows = this.data.pack.resources.filter((item) => {
      const haystack = [item.title, item.content, item.label, item.knowledgeText, this.data.pack.courseName, this.data.pack.chapter].join(' ').toLowerCase();
      const matchWord = !word || haystack.indexOf(word) >= 0;
      const matchType = typeFilter === '全部' || item.label === typeFilter;
      return matchWord && matchType;
    });
    this.setData({
      filteredResources: rows,
      emptyText: rows.length ? '' : '暂未找到相关资源'
    });
  },

  addResourceTask(event) {
    const index = Number(event.currentTarget.dataset.index);
    const resources = this.data.filteredResources.slice();
    if (!resources[index]) return;
    resources[index].joined = true;
    resources[index].taskText = '已加入';
    this.setData({ filteredResources: resources });
    wx.showToast({ title: '已加入学习', icon: 'success' });
  },

  previewResource(event) {
    const index = Number(event.currentTarget.dataset.index);
    const item = this.data.filteredResources[index];
    if (!item) return;
    wx.showModal({
      title: item.title,
      content: `${item.label}｜${item.knowledgeText}\n\n${item.note || item.content}`,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  goTutor() {
    wx.switchTab({ url: '/pages/tutor/index' });
  }
});
