export interface ScoreDistributionItem {
  range: string;
  count: number;
  percent: number;
}

export interface TopErrorItem {
  question: string;
  topic: string;
  errorRate: string;
  affectedStudents?: string[];
  suggestion?: string;
}

export interface ExamResultData {
  reportTitle: string;
  sampleSize: number;
  submittedCount: number;
  questionCount: number;
  averageScore: number;
  passRate: string;
  excellentRate: string;
  highestScore: number;
  highestScorers: string;
  lowScoreCount: number;
  scoreDistribution: ScoreDistributionItem[];
  knowledgeMastery: KnowledgeMastery[];
  topErrors: TopErrorItem[];
  aiSuggestion: string;
  remediationPlan: string[];
}

export interface KnowledgeMastery {
  name: string;
  percent: number;
  color: 'emerald' | 'indigo' | 'amber' | 'rose';
}

export interface SmartGroup {
  title: string;
  count: number;
  tags: string;
  students: string[];
  focus?: string;
  action?: string;
}

export const DEFAULT_SCORE_DISTRIBUTION: ScoreDistributionItem[] = [
  { range: '90-100分', count: 3, percent: 60 },
  { range: '80-89分', count: 5, percent: 100 },
  { range: '70-79分', count: 4, percent: 80 },
  { range: '60-69分', count: 2, percent: 40 },
  { range: '不及格', count: 1, percent: 20 },
];

export const DEFAULT_TOP_ERRORS: TopErrorItem[] = [
  {
    question: '第3题 - 洛伦兹力方向判定 (左手定则)',
    topic: '正负电荷受力方向的镜像倒转混淆',
    errorRate: '46.7%',
    affectedStudents: ['李四', '赵六', '褚十四', '钱十一', '吴九', '冯十二'],
    suggestion: '用三维坐标系和手势投影图拆解磁场、速度、受力三个方向。',
  },
  {
    question: '第7题 - 带电粒子在匀强磁场中的圆周运动',
    topic: '轨道半径公式 (r=mv/qB) 的推导与计算',
    errorRate: '33.3%',
    affectedStudents: ['赵六', '冯十二', '陈十三', '吴九'],
    suggestion: '先复盘洛伦兹力提供向心力，再安排两道半径公式变式训练。',
  },
  {
    question: '第12题 - 复合场中的临界与极值问题',
    topic: '洛伦兹力不做功与动能定理的结合应用',
    errorRate: '26.7%',
    affectedStudents: ['李四', '孙八', '周十'],
    suggestion: '用能量守恒和轨迹边界双线索建立临界条件。',
  },
];

export const DEFAULT_KNOWLEDGE_MASTERY: KnowledgeMastery[] = [
  { name: '洛伦兹力基础概念', percent: 92, color: 'emerald' },
  { name: '公式计算 (F=qvB)', percent: 85, color: 'indigo' },
  { name: '圆周运动 (半径与周期)', percent: 68, color: 'amber' },
  { name: '左手定则空间判定', percent: 46, color: 'rose' },
];

export const DEFAULT_SMART_GROUPS: SmartGroup[] = [
  {
    title: '左手定则 - 空间感薄弱组',
    count: 6,
    tags: '已生成：3道3D空间受力判定题',
    students: ['李四', '赵六', '褚十四', '钱十一', '吴九', '冯十二'],
    focus: '方向判定与空间想象',
    action: '先做手势判定微课，再完成三维受力方向专项题。',
  },
  {
    title: '速度夹角分解 - 计算失误组',
    count: 4,
    tags: '已生成：2道非垂直入射推导题',
    students: ['赵六', '冯十二', '陈十三', '吴九'],
    focus: '速度分解与公式套用',
    action: '补一组入射角变化题，要求写出分解步骤和单位检查。',
  },
  {
    title: '圆周运动 - 全对拔高组',
    count: 3,
    tags: '已生成：1道回旋加速器拓展题',
    students: ['王五', '卫十五', '郑十'],
    focus: '高阶迁移应用',
    action: '推送回旋加速器和质谱仪情境题，训练综合建模能力。',
  },
];

export const DEFAULT_EXAM_RESULT: ExamResultData = {
  reportTitle: '《洛伦兹力专项测试》批阅与学情分析',
  sampleSize: 15,
  submittedCount: 15,
  questionCount: 12,
  averageScore: 75.6,
  passRate: '86.7%',
  excellentRate: '20.0%',
  highestScore: 92,
  highestScorers: '王五',
  lowScoreCount: 1,
  scoreDistribution: DEFAULT_SCORE_DISTRIBUTION,
  knowledgeMastery: DEFAULT_KNOWLEDGE_MASTERY,
  topErrors: DEFAULT_TOP_ERRORS,
  aiSuggestion: '本次测试聚焦高二物理《洛伦兹力》专题。班级整体对基础概念已有一定掌握，但在左手定则的空间判定、半径公式的建模套用，以及复合场中的受力平衡分析上仍存在明显短板。建议下节课先用动态轨迹图复盘第 3 题的方向判断，再通过典型例题专项讲解 r=mv/qB 的推导与使用，最后安排复合场运动轨迹的分层训练。优先讲评第 3 题（错误率 40.0%）与第 7 题（错误率 33.3%）。',
  remediationPlan: [
    '前 8 分钟用动态轨迹图讲评第 3 题，要求学生说出速度、磁场、受力三方向。',
    '安排 2 道半径公式变式题，重点检查单位换算和物理量含义。',
    '按错因分组推送 10 分钟巩固练习，课后收集二次正确率。',
  ],
};
