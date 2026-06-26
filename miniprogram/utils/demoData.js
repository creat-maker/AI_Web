const student = {
  id: 'demo-basic',
  name: '李明',
  className: '计算机类 1 班',
  course: 'Python 程序设计',
  chapter: '循环结构',
  goal: '补齐 Python 循环结构，完成课程作业和基础代码实操',
  level: '学习状态：需巩固',
  todayFocus: 'while 循环、循环嵌套、break / continue'
};

const profileDimensions = [
  {
    name: '知识基础',
    explanation: '判断学生对 Python 基础语法和循环结构的掌握情况。',
    judgement: '基础薄弱，while 循环终止条件仍不稳定。',
    strategy: '先复习条件表达式和变量更新，再进入代码练习。'
  },
  {
    name: '认知风格',
    explanation: '识别更适合图解、步骤化拆解还是项目实践。',
    judgement: '更适合步骤化拆解和变量变化表。',
    strategy: '每道循环题先写前三轮变量变化，再运行验证。'
  },
  {
    name: '学习偏好',
    explanation: '记录学生更愿意使用的资源形态。',
    judgement: '偏好代码案例、图解和短练习。',
    strategy: '优先推荐代码案例、HTML 动画说明和分层练习。'
  },
  {
    name: '易错点',
    explanation: '沉淀最近测评和答疑中反复出现的问题。',
    judgement: '易混淆 while 条件更新、循环嵌套变量和 break / continue。',
    strategy: '安排错题二刷和控制语句输出判断题。'
  },
  {
    name: '学习进度',
    explanation: '同步当前章节路径、任务完成度和资源使用情况。',
    judgement: '循环结构章节进度 68%，仍需完成专项补弱。',
    strategy: '按路径完成 while 循环、break / continue、循环嵌套三个节点。'
  },
  {
    name: '情感动机',
    explanation: '识别学生信心、压力和目标驱动力。',
    judgement: '希望尽快完成课程作业，对死循环问题有挫败感。',
    strategy: '从可运行小案例开始，逐步增加综合任务。'
  }
];

const homeStats = [
  { label: '当前章节', value: '循环结构' },
  { label: '学习进度', value: '68%' },
  { label: '正确率', value: '67%' },
  { label: '推荐资源', value: '9 类' }
];

const learningPath = [
  { title: '条件判断复习', status: '已完成', percent: 100, goal: '复习 if 条件表达式，为 while 条件判断做准备。', tasks: ['完成条件表达式速查', '判断 5 个布尔表达式结果'], resources: ['条件判断复习卡'] },
  { title: 'for 循环', status: '已完成', percent: 82, goal: '掌握已知次数循环和序列遍历。', tasks: ['改写 2 段列表遍历代码'], resources: ['for / range 对照表'] },
  { title: 'while 循环', status: '进行中', percent: 56, goal: '判断 while 循环是否会终止，并解释变量如何更新。', tasks: ['完成 while 补全题', '记录前三轮变量变化'], resources: ['while 死循环修复案例'] },
  { title: 'break / continue', status: '推荐', percent: 30, goal: '区分结束循环和跳过本轮循环。', tasks: ['完成 6 道输出判断题'], resources: ['控制语句对比卡'] },
  { title: '循环嵌套', status: '待学习', percent: 10, goal: '追踪内外层循环变量变化。', tasks: ['补全九九乘法表'], resources: ['嵌套循环变量变化表'] },
  { title: '综合练习', status: '待学习', percent: 0, goal: '用循环完成列表统计小项目。', tasks: ['提交代码和运行截图'], resources: ['课程作业项目任务书'] }
];

const resourceTypeLabels = {
  handout: '知识讲义',
  mindmap: '思维导图',
  quiz: '练习题',
  animation_html: 'HTML/SVG 动画',
  video_script: '视频讲解脚本',
  tts_audio: '语音讲解资源',
  video_mp4: 'MP4 合成任务',
  code_case: '代码案例',
  project_task: '项目任务'
};

const resourcePack = {
  packageTitle: 'Python 循环结构个性化补弱资源包',
  courseName: 'Python 程序设计',
  chapter: '循环结构',
  weakPoints: ['while 循环', '循环嵌套', 'break / continue'],
  resourceCount: 9,
  resources: [
    { resource_type: 'handout', title: 'Python 循环结构知识讲义', content: '梳理 for、while、range、break、continue 与循环嵌套的核心概念。', knowledgePoints: ['for 循环', 'while 循环'], difficulty: '基础', estimatedMinutes: 18 },
    { resource_type: 'mindmap', title: '循环结构思维导图', content: '用中心主题串联 for 循环、while 循环、控制语句和嵌套循环。', knowledgePoints: ['循环结构'], difficulty: '基础', estimatedMinutes: 12 },
    { resource_type: 'quiz', title: '循环结构分层练习题', content: '包含基础判断、输出结果分析和代码补全题。', knowledgePoints: ['while 循环', 'break / continue'], difficulty: '中等', estimatedMinutes: 25 },
    { resource_type: 'animation_html', title: 'while 循环条件更新动画', content: '步骤：初始值 -> 判断条件 -> 执行循环体 -> 更新变量 -> 再次判断。', knowledgePoints: ['while 循环', '变量追踪'], difficulty: '基础', estimatedMinutes: 8, mobileNote: 'Web 端可预览动画，小程序端展示动画步骤。' },
    { resource_type: 'video_script', title: '循环结构视频讲解脚本', content: '先展示死循环代码，再标注初始值、条件、循环体和变量更新。', knowledgePoints: ['while 循环', '循环嵌套'], difficulty: '基础', estimatedMinutes: 8 },
    { resource_type: 'tts_audio', title: '循环结构语音讲解资源', content: '已生成讲解文本，生产环境可接入科大讯飞 TTS。', knowledgePoints: ['循环结构'], difficulty: '基础', estimatedMinutes: 6, tts_status: { status: 'not_configured', message: '已生成讲解文本，生产环境可接入科大讯飞 TTS。' } },
    { resource_type: 'video_mp4', title: 'Python 循环结构简易 MP4 视频', content: 'FFmpeg 可用时可合成 MP4；未检测到时保留 HTML 动画和视频脚本。', knowledgePoints: ['循环结构'], difficulty: '基础', estimatedMinutes: 6, status: 'ffmpeg_optional', description: 'MP4 合成为可选部署能力。' },
    { resource_type: 'code_case', title: 'while 死循环修复案例', content: '提供猜数字、计数器和输入校验案例，并标注变量更新位置。', knowledgePoints: ['while 循环'], difficulty: '进阶', estimatedMinutes: 35 },
    { resource_type: 'project_task', title: '循环结构课程作业任务', content: '完成一个成绩列表统计小项目，提交代码、运行截图和变量变化说明。', knowledgePoints: ['综合练习'], difficulty: '中等', estimatedMinutes: 45 }
  ]
};

const quizResult = {
  score: 67,
  accuracy: '67%',
  weak_points: ['while 循环条件更新', '循环嵌套变量变化', 'break / continue 区分'],
  error_analysis: ['while 循环变量更新位置不稳定', '内外层循环变量没有分列记录', 'break / continue 作用范围混淆'],
  path_adjustment_needed: true,
  path_adjustment: {
    adjusted: true,
    reason: '本次测评显示 while 循环和控制语句仍需巩固。',
    added_tasks: ['while 循环补全题 6 道', 'break / continue 输出判断题 6 道', '循环嵌套变量变化表'],
    recommended_resources: ['while 死循环修复案例', '控制语句对比卡', '循环结构分层练习题'],
    next_step: '先完成 while 循环补全，再进入 break / continue 对比练习。'
  }
};

const report = {
  title: 'Python 循环结构学习诊断报告',
  summary: '本周学习节奏基本稳定，while 循环、循环嵌套和 break / continue 仍需专项补强。',
  accuracy: '67%',
  progress: 68,
  weakPoints: quizResult.weak_points,
  recommendedResources: quizResult.path_adjustment.recommended_resources,
  nextPlan: ['完成 while 循环补全题', '复盘 break / continue 输出判断', '完成循环嵌套综合任务'],
  teacherAdvice: '建议教师课堂点拨变量更新位置，并要求学生提交变量变化表。',
  exportNote: '完整报告可在 Web 端导出。'
};

module.exports = {
  student,
  profileDimensions,
  homeStats,
  learningPath,
  resourceTypeLabels,
  resourcePack,
  quizResult,
  report
};
