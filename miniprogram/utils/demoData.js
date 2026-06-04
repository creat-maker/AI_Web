const student = {
  name: '张三',
  className: '计科大三 1 班',
  goal: '补齐循环、函数和文件操作，完成 Python 成绩文件分析器小项目',
  level: '需关注',
  todayFocus: '循环结构、文件操作与错题二刷'
};

const courses = [
  { name: 'Python 程序设计', icon: 'Py', teacher: '王老师', progress: 68, status: '进行中', weakPoint: '文件操作与循环边界' },
  { name: '数据结构', icon: '栈', teacher: '陈老师', progress: 58, status: '待加强', weakPoint: '递归复杂度分析' },
  { name: '大学英语', icon: '英', teacher: '李老师', progress: 74, status: '进行中', weakPoint: '长难句定位' },
  { name: '高等数学', icon: '数', teacher: '赵老师', progress: 72, status: '进行中', weakPoint: '极限变形' }
];

const weakPoints = [
  'Python：文件读写与异常处理容易漏边界',
  'Python：while 循环终止条件不稳定',
  '数据结构：递归调用栈和复杂度分析薄弱'
];

const todayTasks = [
  { title: '完成 Python 章节诊断测验', time: '20 分钟', status: '进行中', knowledge: '循环结构 / 文件操作' },
  { title: '复盘文件读写错题 2 道', time: '15 分钟', status: '未开始', knowledge: '文件操作' },
  { title: '观看循环边界专项微课', time: '10 分钟', status: '未开始', knowledge: '循环结构' }
];

const learningPath = [
  {
    profileType: '基础薄弱型',
    title: '循环边界修复任务',
    goal: '能判断 for/while 的起止条件并解释循环次数。',
    knowledge: '循环结构、条件语句',
    resource: '循环边界专项微课',
    practice: '完成 6 道循环边界题并提交九九乘法表程序。',
    completion: '正确率达到 80%，代码通过 3 个边界用例。',
    aiAdvice: '先手写前三轮循环变量变化，再运行代码验证。',
    status: '进行中',
    percent: 56
  },
  {
    profileType: '考试冲刺型',
    title: '章节诊断测验',
    goal: '定位循环、函数、文件操作三类高频失分点。',
    knowledge: '循环结构、函数、文件操作',
    resource: 'Python 章节诊断卷',
    practice: '完成 8 道章节练习题。',
    completion: '提交测验并查看错因分析。',
    aiAdvice: '不要立即看答案，先标注每道题的卡点。',
    status: '推荐',
    percent: 20
  },
  {
    profileType: '项目实践型',
    title: '成绩文件分析器',
    goal: '读取 CSV 成绩文件，输出统计结果和风险学生名单。',
    knowledge: '列表、字典、文件操作、异常处理',
    resource: 'CSV 成绩分析 Notebook',
    practice: '实现读取、异常兜底、平均分统计和结果写出。',
    completion: '项目通过 5 个测试数据文件，提交运行截图。',
    aiAdvice: '先完成最小可运行版本，再补异常处理和输出格式。',
    status: '未开始',
    percent: 0
  }
];

const recommendedResources = [
  { title: '循环边界专项微课', icon: '循', course: 'Python 程序设计', type: '微课', duration: '10 分钟', reason: '匹配 while 终止条件薄弱点' },
  { title: '文件读写分步讲义', icon: '文', course: 'Python 程序设计', type: '讲义', duration: '18 分钟', reason: '用于补齐 with open、编码和异常边界' },
  { title: 'CSV 成绩分析 Notebook', icon: '表', course: 'Python 程序设计', type: 'Notebook', duration: '35 分钟', reason: '把列表、字典、文件操作串成项目任务' },
  { title: '错题原因标签说明', icon: '诊', course: 'Python 程序设计', type: '清单', duration: '8 分钟', reason: '帮助学生把错题归因到概念、边界或审题' }
];

const generatedResourcePack = {
  packageTitle: 'Python 个性化资源包',
  courseName: 'Python 程序设计',
  weakPoints: ['文件操作', '循环结构', '异常处理'],
  resourceCount: 4,
  resources: [
    {
      resourceType: '个性化讲义',
      title: 'Python 文件处理分步讲义',
      content: '解释 with open、读写模式、编码和常见边界问题。',
      reason: '先补齐概念和步骤，降低直接写代码的挫败感。',
      relatedKnowledgePoints: ['文件操作', '异常处理'],
      difficulty: '基础',
      estimatedMinutes: 18
    },
    {
      resourceType: '练习题',
      title: '循环与文件操作分层练习',
      content: '包含基础题、变式题和综合题，每题带错因标签。',
      reason: '通过分层练习检查是否真正掌握薄弱知识点。',
      relatedKnowledgePoints: ['循环结构', '文件操作'],
      difficulty: '中等',
      estimatedMinutes: 25
    },
    {
      resourceType: '项目任务书',
      title: '成绩文件分析器',
      content: '读取 CSV 成绩文件，统计平均分和低分名单，并处理文件异常。',
      reason: '把知识点迁移到可展示的实践任务。',
      relatedKnowledgePoints: ['列表', '字典', '文件操作'],
      difficulty: '进阶',
      estimatedMinutes: 35
    }
  ],
  mode: 'local-fallback'
};

const quizAnalysis = {
  score: 67,
  weakPoints: ['文件操作', '循环结构'],
  causes: ['文件资源管理不熟', '循环终止条件不清'],
  nextStep: '完成错题二刷后，系统会把文件操作资源包加入学习路径。'
};

const wrongQuestions = [
  { course: 'Python 程序设计', title: '安全读取文本文件的写法选择错误', answer: "推荐使用 with open('a.txt', encoding='utf-8') as f", status: '待复习', cause: '文件资源管理不熟' },
  { course: 'Python 程序设计', title: 'while 循环变量忘记更新', answer: '先写终止条件，再检查循环体是否推进变量。', status: '待复习', cause: '循环终止条件不清' },
  { course: '数据结构', title: '递归出口设置错误', answer: '先写最小规模问题，再向一般情况扩展。', status: '已订正', cause: '递归边界混淆' }
];

const mastery = [
  { name: '变量与数据类型', value: 92, status: '已掌握' },
  { name: '循环结构', value: 58, status: '薄弱' },
  { name: '函数', value: 69, status: '学习中' },
  { name: '文件操作', value: 52, status: '薄弱' },
  { name: '异常处理', value: 28, status: '未学习' }
];

const report = {
  score: 86,
  progress: 68,
  studyTime: '12h 24m',
  completion: '18 / 24',
  summary: '本周学习节奏稳定，Python 文件操作和循环边界仍需专项补强，建议先完成智能测验错因分析，再进入项目实践。',
  suggestions: [
    '每天 20 分钟完成循环边界和文件操作专项题',
    '用错因标签复盘 3 道文件读写错题',
    '完成成绩文件分析器最小可运行版本'
  ]
};

module.exports = {
  student,
  courses,
  weakPoints,
  todayTasks,
  learningPath,
  recommendedResources,
  generatedResourcePack,
  quizAnalysis,
  wrongQuestions,
  mastery,
  report
};
