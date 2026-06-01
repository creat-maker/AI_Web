const student = {
  name: '张三',
  className: '计科大三 1 班',
  goal: '夯实数学基础，提升 Python 与数据结构实践能力',
  level: '稳步提升',
  todayFocus: '函数、栈队列与英语阅读复盘'
};

const courses = [
  { name: '高等数学', icon: '数', teacher: '王老师', progress: 72, status: '进行中', weakPoint: '导数应用与极限计算' },
  { name: '大学英语', icon: '英', teacher: '陈老师', progress: 64, status: '进行中', weakPoint: '长难句阅读与词汇辨析' },
  { name: 'Python 程序设计', icon: 'Py', teacher: '张老师', progress: 81, status: '进行中', weakPoint: '函数封装与文件处理' },
  { name: '数据结构', icon: '栈', teacher: '王老师', progress: 58, status: '待加强', weakPoint: '栈、队列与递归分析' }
];

const weakPoints = [
  '高等数学：极限变形不熟练',
  '大学英语：阅读题定位速度慢',
  'Python：异常处理与文件读写易漏边界',
  '数据结构：递归复杂度分析薄弱'
];

const todayTasks = [
  { title: '完成高等数学极限专项练习', time: '20 分钟', status: '进行中' },
  { title: '复盘 Python 文件读写错题', time: '15 分钟', status: '未开始' },
  { title: '完成英语阅读 1 篇', time: '18 分钟', status: '未开始' }
];

const learningPath = [
  { title: '基础诊断', desc: '根据测验与作业识别薄弱点', status: '已完成', percent: 100 },
  { title: '专项补强', desc: '围绕极限、递归和文件处理安排任务', status: '进行中', percent: 65 },
  { title: '综合练习', desc: '完成跨课程综合题与项目任务', status: '未开始', percent: 20 },
  { title: '学习报告', desc: '生成阶段报告并给出下一步建议', status: '未开始', percent: 0 }
];

const recommendedResources = [
  { title: '极限计算 10 分钟速查', icon: '数', course: '高等数学', type: '微课', duration: '10 分钟', reason: '匹配极限变形薄弱点' },
  { title: 'Python 文件读写案例包', icon: 'Py', course: 'Python 程序设计', type: 'Notebook', duration: '25 分钟', reason: '用于补齐工程实践短板' },
  { title: '栈与队列动画讲解', icon: '栈', course: '数据结构', type: '交互演示', duration: '12 分钟', reason: '帮助理解入栈出栈过程' },
  { title: '英语长难句拆解清单', icon: '英', course: '大学英语', type: 'PDF', duration: '15 分钟', reason: '提升阅读定位与句法识别' }
];

const generatedResourcePack = {
  packageTitle: 'Python 程序设计个性化资源包',
  courseName: 'Python 程序设计',
  weakPoints: ['Python 文件读写与异常处理', '递归边界与复杂度分析', '代码调试与边界条件'],
  resourceCount: 5,
  resources: [
    {
      resourceType: '个性化讲义',
      title: 'Python 文件处理分步讲义',
      content: '解释 with open、读写模式、异常处理和常见边界问题，并附 5 分钟自检清单。',
      reason: '先补齐概念和步骤，降低直接写代码的挫败感。',
      relatedKnowledgePoints: ['文件读写', '异常处理'],
      difficulty: '基础',
      estimatedMinutes: 18
    },
    {
      resourceType: '练习题',
      title: '文件处理与递归分层练习 8 题',
      content: '包含基础题、变式题和综合题，每题提供提示、标准答案和错因标签。',
      reason: '通过分层练习检查是否真正掌握薄弱知识点。',
      relatedKnowledgePoints: ['文件读写', '递归边界'],
      difficulty: '中等',
      estimatedMinutes: 25
    },
    {
      resourceType: '代码案例或实验任务',
      title: '学生成绩文件分析小实验',
      content: '读取 CSV 成绩文件，统计平均分和低分名单，并处理文件不存在、空文件等异常。',
      reason: '把知识点迁移到可展示的实践任务。',
      relatedKnowledgePoints: ['文件读写', '列表处理', '异常处理'],
      difficulty: '进阶',
      estimatedMinutes: 35
    },
    {
      resourceType: '思维导图文本',
      title: '递归分析思维导图',
      content: '中心主题：递归。一级节点：终止条件、状态转移、调用栈、复杂度、典型错误。',
      reason: '帮助学生建立结构化认知，便于复盘。',
      relatedKnowledgePoints: ['递归', '调用栈'],
      difficulty: '基础',
      estimatedMinutes: 12
    },
    {
      resourceType: '视频脚本或项目任务书',
      title: '8 分钟文件处理讲解脚本',
      content: '问题引入、核心概念、代码演示、课后任务四段式脚本，并附提交物和评分点。',
      reason: '可直接用于教师端资源生成展示，也便于学生端按步骤完成任务。',
      relatedKnowledgePoints: ['文件处理', '异常分支'],
      difficulty: '中等',
      estimatedMinutes: 20
    }
  ],
  mode: 'local-fallback'
};

const tutorMessages = [
  { role: 'assistant', content: '你好张三，我会根据你的课程进度和薄弱点给出学习建议。' },
  { role: 'user', content: '数据结构递归题总是写不出来怎么办？' },
  { role: 'assistant', content: '先画递归树，明确终止条件，再写状态转移。建议先做“阶乘、斐波那契、二叉树遍历”三类题。' }
];

const ragTutorFallback = {
  answer: '根据《Python 程序设计》递归基础资料，递归题应先写递归出口，再写规模缩小的递推关系。建议先画调用树，再检查每次调用是否接近最小规模问题。',
  confidence: 0.86,
  citations: [
    {
      sourceFile: 'python_ch02_recursion.md',
      chapter: '第 2 章 函数与模块化',
      section: '递归基础',
      snippet: '递归函数必须包含递归出口和规模缩小的递推关系。'
    }
  ],
  recommendedExercises: ['用递归实现阶乘函数。', '画出 Fibonacci(5) 的递归调用树并说明重复计算。'],
  relatedKnowledgePoints: ['递归', '递归出口', '调用栈']
};

const wrongQuestions = [
  { course: '高等数学', title: '求极限时忽略等价无穷小条件', answer: '先判断趋近条件，再使用等价替换。', status: '待复习' },
  { course: 'Python 程序设计', title: '文件打开后未处理异常', answer: '使用 with open(...) 并补充 try/except。', status: '已订正' },
  { course: '数据结构', title: '递归出口设置错误', answer: '先写最小规模问题，再向一般情况扩展。', status: '待复习' }
];

const report = {
  score: 86,
  progress: 68,
  studyTime: '12h 24m',
  completion: '18 / 24',
  summary: '本周学习节奏稳定，Python 与英语完成度较好；高等数学和数据结构仍需专项补强。',
  suggestions: [
    '每天 20 分钟完成极限与导数专项题',
    '用递归树复盘 3 道数据结构错题',
    'Python 文件处理练习需补充异常分支'
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
  tutorMessages,
  ragTutorFallback,
  wrongQuestions,
  report
};
