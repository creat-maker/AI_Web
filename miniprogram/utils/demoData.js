const student = {
  name: '李明',
  className: '计科大三 1 班',
  goal: '补齐 Python 循环结构，完成课程作业和基础代码实操',
  level: '学习状态：需巩固',
  todayFocus: 'while 循环、循环嵌套、break / continue'
};

const courses = [
  { name: 'Python 程序设计', icon: 'Py', teacher: '王老师', progress: 68, status: '进行中', weakPoint: '循环结构' },
  { name: '循环结构专项补弱课', icon: '循', teacher: 'AI 助教', progress: 42, status: '重点学习', weakPoint: 'while 循环条件更新' },
  { name: 'Python 代码实操案例课', icon: '码', teacher: '实训助教', progress: 55, status: '进行中', weakPoint: '循环嵌套变量变化' }
];

const weakPoints = [
  'while 循环终止条件不稳定',
  '循环嵌套内外层变量容易混用',
  'break / continue 使用场景容易混淆'
];

const todayTasks = [
  { title: '完成 while 循环终止条件补全题', time: '20 分钟', status: '进行中', knowledge: 'while 循环' },
  { title: '提交循环嵌套变量变化表', time: '15 分钟', status: '未开始', knowledge: '循环嵌套' },
  { title: '复盘 break / continue 易错题', time: '10 分钟', status: '未开始', knowledge: 'break / continue' }
];

const homeCards = [
  {
    type: 'advice',
    title: '今日学习建议',
    label: '优先级最高',
    content: '先做 20 分钟 while 循环终止条件补全，再复盘 2 道 break / continue 输出题。',
    action: '开始补弱'
  },
  {
    type: 'continue',
    title: '继续学习',
    label: '上次停在 56%',
    content: '继续完成「while 循环补弱」路径，下一步是变量变化表和死循环修复案例。',
    action: '继续'
  },
  {
    type: 'weak',
    title: '薄弱知识点',
    label: '持续跟踪',
    content: 'while 条件更新、循环嵌套变量、break / continue 区分仍需专项练习。',
    action: '查看'
  }
];

const learningPath = [
  {
    profileType: '基础薄弱 + 代码实操偏好型',
    title: 'while 循环补弱',
    goal: '能判断 while 循环是否会终止，并解释变量如何更新。',
    knowledge: 'while 循环、循环条件、变量更新',
    resource: 'while 死循环修复案例',
    practice: '完成 3 道 while 循环补全题。',
    completion: '正确率达到 80%，并写出前三轮变量变化。',
    aiAdvice: '先检查初始值、条件和更新语句，再运行代码验证。',
    status: '进行中',
    percent: 56
  },
  {
    profileType: '基础薄弱 + 代码实操偏好型',
    title: 'break / continue 对比',
    goal: '区分跳出循环和跳过本轮循环。',
    knowledge: 'break / continue',
    resource: '控制语句对比卡',
    practice: '完成 6 道输出结果判断题。',
    completion: '能解释每次输出变化。',
    aiAdvice: '把每轮输出写在表格中。',
    status: '推荐',
    percent: 20
  },
  {
    profileType: '基础薄弱 + 代码实操偏好型',
    title: '循环嵌套实操',
    goal: '跟踪内外层循环变量变化。',
    knowledge: 'for 循环、循环嵌套',
    resource: '循环嵌套变量变化表',
    practice: '补全九九乘法表程序。',
    completion: '代码通过 3 个边界用例。',
    aiAdvice: '外层变量一列，内层变量一列。',
    status: '未开始',
    percent: 0
  }
];

const recommendedResources = [
  { title: '循环结构讲解文档', icon: '文', course: 'Python 程序设计', type: '讲义', duration: '18 分钟', reason: '先补齐 for / while 基础概念。', joined: false },
  { title: 'while 死循环修复案例', icon: '码', course: 'Python 程序设计', type: '代码实操', duration: '12 分钟', reason: '匹配 while 循环终止条件薄弱点。', joined: false },
  { title: 'break / continue 专项练习', icon: '练', course: 'Python 程序设计', type: '专项练习', duration: '20 分钟', reason: '帮助区分跳出循环和跳过本轮。', joined: false },
  { title: '循环结构微课视频脚本', icon: '视', course: 'Python 程序设计', type: '视频脚本', duration: '8 分钟', reason: '用于课后快速复盘。', joined: false }
];

const generatedResourcePack = {
  packageTitle: 'Python 循环结构个性化补弱资源包',
  courseName: 'Python 程序设计',
  weakPoints: ['while 循环', '循环嵌套', 'break / continue'],
  resourceCount: 7,
  resources: [
    {
      resourceType: '讲解文档',
      title: '循环结构讲解文档',
      content: '解释 for 循环、while 循环、break / continue 和循环嵌套。',
      reason: '先补齐概念和步骤，降低直接写代码的挫败感。',
      relatedKnowledgePoints: ['for 循环', 'while 循环'],
      difficulty: '基础',
      estimatedMinutes: 18,
      joined: false
    },
    {
      resourceType: '专项练习',
      title: '循环结构分层练习',
      content: '包含 while 补全题、break / continue 输出题和循环嵌套变量题。',
      reason: '通过分层练习检查是否真正掌握薄弱知识点。',
      relatedKnowledgePoints: ['while 循环', 'break / continue'],
      difficulty: '中等',
      estimatedMinutes: 25,
      joined: false
    },
    {
      resourceType: '代码实操案例',
      title: 'while 死循环修复案例',
      content: '提供猜数字、计数器和输入校验案例，并标注变量更新位置。',
      reason: '把知识点迁移到可展示的实操任务。',
      relatedKnowledgePoints: ['while 循环', '循环嵌套'],
      difficulty: '进阶',
      estimatedMinutes: 35,
      joined: false
    }
  ],
  mode: 'local-learning-data'
};

const quizAnalysis = {
  score: 67,
  weakPoints: ['while 循环', '循环嵌套', 'break / continue'],
  causes: ['循环终止条件不清', '内外层变量混用', '循环控制语句使用场景混淆'],
  nextStep: '完成错题二刷后，系统会把 Python 循环结构补弱资源包加入学习路径。'
};

const wrongQuestions = [
  { course: 'Python 程序设计', title: 'while 循环变量忘记更新', answer: '先写终止条件，再检查循环体是否推进变量。', status: '待复习', cause: '循环终止条件不清' },
  { course: 'Python 程序设计', title: 'continue 输出结果判断错误', answer: 'continue 会跳过本轮剩余语句，不会结束整个循环。', status: '待复习', cause: '控制语句混淆' },
  { course: 'Python 程序设计', title: '循环嵌套变量变化表漏填', answer: '外层变量和内层变量分列记录，每轮分别更新。', status: '已订正', cause: '内外层变量混用' }
];

const mastery = [
  { name: 'for 循环', value: 70, status: '学习中' },
  { name: 'while 循环', value: 48, status: '薄弱' },
  { name: '循环嵌套', value: 43, status: '薄弱' },
  { name: 'break / continue', value: 55, status: '薄弱' }
];

const report = {
  score: 86,
  progress: 68,
  studyTime: '12h 24m',
  completion: '18 / 24',
  summary: '本周学习节奏基本稳定。Python while 循环、循环嵌套和 break / continue 仍需专项补强，建议先完成智能测验错因分析，再进入代码实操。',
  suggestions: [
    '每天 20 分钟完成 while 循环和循环嵌套专项题',
    '用错因标签复盘 3 道 break / continue 错题',
    '完成猜数字案例最小可运行版本'
  ]
};

module.exports = {
  student,
  courses,
  weakPoints,
  todayTasks,
  homeCards,
  learningPath,
  recommendedResources,
  generatedResourcePack,
  quizAnalysis,
  wrongQuestions,
  mastery,
  report
};
