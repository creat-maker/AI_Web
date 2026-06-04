export const statusMeta: Record<string, { label: string; color: string; bg: string; tone: 'success' | 'info' | 'warning' | 'neutral' | 'danger' | 'purple' }> = {
  mastered: { label: '已掌握', color: '#16a34a', bg: '#dcfce7', tone: 'success' },
  learning: { label: '学习中', color: '#2563eb', bg: '#dbeafe', tone: 'info' },
  weak: { label: '薄弱', color: '#ea580c', bg: '#ffedd5', tone: 'warning' },
  not_started: { label: '未学习', color: '#64748b', bg: '#f1f5f9', tone: 'neutral' }
};

export const knowledgeGraph = {
  course_id: 'python-programming',
  course_name: 'Python 程序设计',
  recommendation_policy: '根据掌握率、错题标签、学习路径任务和答疑记录综合推荐资源。',
  nodes: [
    { id: 'variables', name: '变量与数据类型', status: 'mastered', status_label: '已掌握', mastery: 92, description: '理解变量命名、数字/字符串/布尔值类型转换和基础输入输出。', resources: ['变量命名规范速查', '类型转换 10 分钟微课'], exercises: ['完成 5 道类型转换选择题', '编写 BMI 计算小程序'], ai_suggestion: '已具备后续学习基础，可通过小项目巩固变量命名和类型边界。' },
    { id: 'conditions', name: '条件语句', status: 'learning', status_label: '学习中', mastery: 76, description: '掌握 if/elif/else 分支、布尔表达式和嵌套条件拆解。', resources: ['分支结构案例讲义', '条件表达式错题集'], exercises: ['成绩等级判断', '会员折扣规则实现'], ai_suggestion: '建议先画条件表，再写代码，减少漏分支问题。' },
    { id: 'loops', name: '循环结构', status: 'weak', status_label: '薄弱', mastery: 58, description: '理解 for/while、循环控制、嵌套循环和边界条件。', resources: ['循环边界专项微课', 'for/while 对比练习'], exercises: ['九九乘法表', '统计列表中满足条件的元素'], ai_suggestion: '先写循环不变量和停止条件，再补充循环体，避免死循环和少算一次。' },
    { id: 'functions', name: '函数', status: 'learning', status_label: '学习中', mastery: 69, description: '掌握函数定义、参数、返回值、作用域和模块化拆分。', resources: ['函数封装案例包', '参数与返回值导学单'], exercises: ['封装成绩统计函数', '拆分温度转换程序'], ai_suggestion: '把重复代码先圈出来，再抽象输入、处理和输出。' },
    { id: 'lists', name: '列表', status: 'mastered', status_label: '已掌握', mastery: 88, description: '掌握列表索引、切片、遍历、增删改查和常用方法。', resources: ['列表操作速查表', '列表推导式入门'], exercises: ['学生成绩排序', '筛选偶数列表'], ai_suggestion: '可以进入列表与循环结合的综合题，提升数据处理速度。' },
    { id: 'dicts', name: '字典', status: 'not_started', status_label: '未学习', mastery: 34, description: '理解键值对、字典遍历、统计计数和嵌套数据结构。', resources: ['字典计数案例', 'JSON 与字典对照讲义'], exercises: ['词频统计', '课程成绩表查询'], ai_suggestion: '建议在掌握列表遍历后进入，重点理解 key 的唯一性。' },
    { id: 'files', name: '文件操作', status: 'weak', status_label: '薄弱', mastery: 52, description: '掌握 with open、读写模式、编码、CSV 读写和异常边界。', resources: ['文件读写分步讲义', 'CSV 成绩分析 Notebook'], exercises: ['读取日志并统计关键字', '学生成绩 CSV 汇总'], ai_suggestion: '先复习异常处理，再练习文件不存在、空文件、编码错误三类边界。' },
    { id: 'exceptions', name: '异常处理', status: 'not_started', status_label: '未学习', mastery: 28, description: '理解 try/except/finally、异常类型和可恢复错误处理。', resources: ['异常处理情境卡', '常见异常类型清单'], exercises: ['输入合法性校验', '文件读取异常兜底'], ai_suggestion: '结合文件操作一起练，重点区分错误提示和程序崩溃。' }
  ],
  links: [
    { source: 'variables', target: 'conditions', relation: '表达式基础' },
    { source: 'conditions', target: 'loops', relation: '循环控制' },
    { source: 'loops', target: 'functions', relation: '封装重复逻辑' },
    { source: 'loops', target: 'lists', relation: '遍历数据' },
    { source: 'lists', target: 'dicts', relation: '结构化数据' },
    { source: 'dicts', target: 'files', relation: '持久化数据' },
    { source: 'files', target: 'exceptions', relation: '边界兜底' },
    { source: 'functions', target: 'files', relation: '工程封装' }
  ]
};

export const learningTaskPaths = {
  student_id: 'demo-student-zhangsan',
  course_name: 'Python 程序设计',
  active_profile_type: '基础薄弱型',
  paths: [
    {
      profile_type: '基础薄弱型',
      summary: '先补齐变量、条件、循环和函数的概念断点，用短任务建立可见进步。',
      ai_recommendation: '每天 25 分钟，优先完成可自动判分的小练习，降低挫败感。',
      tasks: [
        { title: '循环边界修复任务', goal: '能判断 for/while 的起止条件并解释循环次数。', knowledge_points: ['循环结构', '条件语句'], resources: ['循环边界专项微课', 'for/while 对比练习'], practice: '完成 6 道循环边界题并提交 1 个九九乘法表程序。', completion_rule: '练习正确率达到 80%，且代码通过 3 个边界用例。', estimated_minutes: 30, ai_suggestion: '先手写前三轮循环变量变化，再运行代码验证。', status: '进行中' },
        { title: '函数封装入门', goal: '把重复逻辑抽取为函数，说明参数和返回值。', knowledge_points: ['函数', '变量与数据类型'], resources: ['函数封装案例包', '参数与返回值导学单'], practice: '封装成绩平均分、最高分、及格率三个函数。', completion_rule: '完成函数定义并通过样例输入输出。', estimated_minutes: 25, ai_suggestion: '用输入、处理、输出三列拆解函数职责。', status: '未开始' }
      ]
    },
    {
      profile_type: '考试冲刺型',
      summary: '围绕高频考点和错题分布安排测评、纠错和二次练习。',
      ai_recommendation: '先做诊断测验，再按薄弱知识点刷题，最后生成错题复盘卡。',
      tasks: [
        { title: '章节诊断测验', goal: '定位循环、函数、文件操作三类高频失分点。', knowledge_points: ['循环结构', '函数', '文件操作'], resources: ['Python 章节诊断卷', '错题原因标签说明'], practice: '完成 8 道章节练习题。', completion_rule: '提交测验并查看错因分析。', estimated_minutes: 20, ai_suggestion: '不要立即看答案，先标注每道题的卡点。', status: '推荐' },
        { title: '错题二刷', goal: '把错因从概念不清转化为可执行检查清单。', knowledge_points: ['文件操作', '异常处理'], resources: ['文件读写错题集', '异常处理情境卡'], practice: '重做错题并写出每题 1 条防错规则。', completion_rule: '二刷正确率达到 90%。', estimated_minutes: 35, ai_suggestion: '每道错题只记录一个主错因，避免复盘过载。', status: '未开始' }
      ]
    },
    {
      profile_type: '项目实践型',
      summary: '用小项目串联列表、字典、文件和异常处理，强化迁移应用。',
      ai_recommendation: '适合已有基础的学生，建议用项目产物替代单点刷题。',
      tasks: [
        { title: '成绩文件分析器', goal: '读取 CSV 成绩文件，输出统计结果和风险学生名单。', knowledge_points: ['列表', '字典', '文件操作', '异常处理'], resources: ['CSV 成绩分析 Notebook', '字典计数案例'], practice: '实现文件读取、异常兜底、平均分统计和结果写出。', completion_rule: '项目通过 5 个测试数据文件，提交运行截图。', estimated_minutes: 60, ai_suggestion: '先完成最小可运行版本，再补充异常处理和输出格式。', status: '推荐' }
      ]
    }
  ]
};

export const chapterQuiz = {
  quiz_id: 'python-chapter-1',
  title: 'Python 程序设计章节练习',
  chapter: '基础语法到文件操作',
  questions: [
    { id: 'q1', type: 'single', stem: '以下哪个写法最适合安全读取文本文件？', options: ["open('a.txt').read()", "with open('a.txt', encoding='utf-8') as f", "eval(open('a.txt'))", "input('a.txt')"], answer: "with open('a.txt', encoding='utf-8') as f", knowledge_point: '文件操作' },
    { id: 'q2', type: 'single', stem: 'while 循环最容易出现的典型错误是？', options: ['忘记更新循环变量', '变量名太短', '注释太少', '函数名重复'], answer: '忘记更新循环变量', knowledge_point: '循环结构' },
    { id: 'q3', type: 'single', stem: '函数 return 的主要作用是？', options: ['打印结果', '结束程序', '返回计算结果给调用方', '创建变量'], answer: '返回计算结果给调用方', knowledge_point: '函数' }
  ]
};

export const fallbackQuizResult = {
  score: 67,
  correct_count: 2,
  total: 3,
  weak_points: ['文件操作'],
  wrong_items: [
    { question_id: 'q1', stem: '以下哪个写法最适合安全读取文本文件？', selected: "open('a.txt').read()", correct_answer: "with open('a.txt', encoding='utf-8') as f", knowledge_point: '文件操作', reason: '文件资源管理不熟', recommendation: '复习「文件操作」资源包，并完成 2 道同类变式题。' }
  ],
  cause_analysis: [
    { type: '概念理解', detail: '对文件上下文管理存在混淆。' },
    { type: '边界意识', detail: '文件不存在、编码错误等边界检查不足。' }
  ],
  recommended_resources: [
    { title: '文件读写分步讲义', knowledge_point: '文件操作', minutes: 18 },
    { title: '异常处理情境卡', knowledge_point: '异常处理', minutes: 12 }
  ],
  next_step: '系统已把薄弱知识点写入学习路径，建议完成错题二刷后再进入项目任务。'
};

export const classInsight = {
  metrics: [
    { label: '班级完成率', value: 78, unit: '%', hint: '较上周 +6.4%', icon: '完', tone: 'green' as const },
    { label: '平均正确率', value: 82, unit: '%', hint: '章节测验统计', icon: '测', tone: 'purple' as const },
    { label: '学习活跃度', value: 91, unit: '%', hint: '答疑、练习、资源访问', icon: '活', tone: 'cyan' as const },
    { label: '风险学生', value: 6, unit: '人', hint: '需要教师干预', icon: '险', tone: 'orange' as const }
  ],
  weakRanking: [
    { name: '文件操作', value: 42 },
    { name: '循环结构', value: 37 },
    { name: '函数返回值', value: 31 },
    { name: '异常处理', value: 28 }
  ],
  riskStudents: [
    { name: '王五', risk: '高风险', progress: 42, weak: ['文件操作', '异常处理'], suggestion: '推送文件读写分步讲义，布置 15 分钟补救任务，提醒话术：先完成最小可运行代码，再补异常。' },
    { name: '赵六', risk: '需关注', progress: 56, weak: ['循环结构'], suggestion: '安排循环边界二刷，课堂中点名讲解一次变量变化表。' },
    { name: '孙七', risk: '需关注', progress: 61, weak: ['函数'], suggestion: '推荐函数封装案例包，要求提交参数和返回值说明。' }
  ]
};

export const profileInsight = {
  base_level: '中等偏弱',
  learning_goal: '两周内补齐循环、函数和文件操作，完成成绩文件分析器小项目。',
  preference: '案例驱动、短视频讲解、可运行 Notebook',
  progress: 68,
  weak_points: ['文件操作', '循环结构', '异常处理'],
  wrong_distribution: [
    { name: '概念混淆', value: 38 },
    { name: '边界遗漏', value: 31 },
    { name: '代码规范', value: 18 },
    { name: '审题偏差', value: 13 }
  ],
  risk_level: '需关注',
  intervention: ['推送文件读写资源包', '布置循环边界补救任务', '教师 1 对 1 提醒：先画变量变化表再写代码']
};

export const courseRelation = {
  knowledge_points: ['变量与数据类型', '条件语句', '循环结构', '函数', '列表', '字典', '文件操作', '异常处理'],
  resources: [
    { title: '循环边界专项微课', related: ['循环结构', '条件语句'], type: '微课' },
    { title: '函数封装案例包', related: ['函数'], type: '案例' },
    { title: 'CSV 成绩分析 Notebook', related: ['列表', '字典', '文件操作'], type: 'Notebook' }
  ],
  questions: [
    { title: 'while 循环终止条件判断', related: ['循环结构'], difficulty: '基础' },
    { title: '封装成绩统计函数', related: ['函数', '列表'], difficulty: '中等' },
    { title: '读取 CSV 并处理异常', related: ['文件操作', '异常处理'], difficulty: '进阶' }
  ]
};

export const adminReview = {
  items: [
    { id: 'cr-001', title: '循环结构专项微课脚本', resource_type: '微课脚本', source: '教师工作台生成', risk_tags: ['需核对示例代码', '避免直接给答案'], status: '待审核', review_opinion: '等待课程负责人确认代码样例与教学目标一致。' },
    { id: 'cr-002', title: '文件操作章节测验', resource_type: '测验', source: 'AI 生成测验', risk_tags: ['题目难度需校准'], status: '已通过', review_opinion: '已补充答案解析，可发布到学生端。' },
    { id: 'cr-003', title: '异常处理学习建议', resource_type: '个性化推荐', source: '练后分析生成', risk_tags: ['诊断结论不可绝对化'], status: '已驳回', review_opinion: '建议语气过于确定，需改为教学辅助建议。' }
  ],
  policy: 'AI 生成内容仅作为教学辅助，关键资源、测评结果和干预结论需教师或管理员审核后使用。'
};

export const platformQuality = {
  summary: {
    course_completion_rate: 76.8,
    average_quiz_score: 82.4,
    resource_usage_rate: 68.5,
    weak_point_concentration: 42.0,
    teacher_ai_tool_uses: 286,
    content_review_pass_rate: 91.2
  },
  ai_metrics: {
    qa_count: 18620,
    resource_generation_count: 1324,
    quiz_completion_count: 4286,
    review_pass_rate: 91.2
  },
  quality_dimensions: [
    { name: '课程完成率', value: 76.8, suggestion: '关注进度低于 50% 的课程。' },
    { name: '测验均分', value: 82.4, suggestion: '保持章节测验难度梯度。' },
    { name: '资源使用率', value: 68.5, suggestion: '提升薄弱知识点资源曝光。' },
    { name: '薄弱知识点集中度', value: 42.0, suggestion: '集中在循环、文件、异常处理，建议专项治理。' }
  ],
  ai_boundary: 'AI 生成内容仅作为教学辅助，关键教学资源、测评结论和学生干预建议必须经教师或管理员审核。'
};
