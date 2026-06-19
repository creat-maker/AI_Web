const { post } = require('../../utils/request');

const examples = [
  '为什么我的 while 循环会死循环？',
  'break 和 continue 有什么区别？',
  '循环嵌套为什么容易看不懂？',
  'for 循环和 while 循环怎么选择？'
];

const scriptReadyText = '讲解脚本已生成，可用于后续语音播报或数字人服务。';
const reference = 'Python 程序设计课程知识库 / 循环结构章节';

function defaultAnswer(question) {
  if (question.indexOf('for') >= 0 && question.indexOf('while') >= 0) {
    return '次数明确、遍历序列时优先用 for；次数不固定、需要满足条件才结束时优先用 while。';
  }
  if (question.indexOf('break') >= 0 || question.indexOf('continue') >= 0) {
    return 'break 会直接结束当前循环；continue 会跳过本轮剩余语句进入下一轮。while 循环里使用 continue 时要特别注意不要跳过变量更新。';
  }
  if (question.indexOf('嵌套') >= 0) {
    return '循环嵌套建议把外层变量和内层变量分列记录。先写每一轮变量变化，再运行代码验证输出。';
  }
  return 'while 死循环通常是循环条件一直为 True，或循环变量没有在循环体内更新。请按“初始值、循环条件、变量更新”三步检查。';
}

function structuredAnswer(question) {
  if (question.indexOf('for') >= 0 && question.indexOf('while') >= 0) {
    return [
      { title: '问题诊断', items: ['你需要根据循环次数是否明确来选择循环结构。'] },
      { title: '简明解释', items: ['次数明确、遍历序列时优先用 for；次数不固定、按条件结束时优先用 while。'] },
      { title: '错误示例', items: ['while i < len(nums): print(nums[i])；只是遍历列表时容易忘记初始化或更新 i。'] },
      { title: '正确示例', items: ['for item in nums: print(item)；while password != "ok": 继续输入密码。'] },
      { title: '常见错误', items: ['把所有循环都写成 while，或在输入校验场景强行使用 for。'] },
      { title: '推荐练习', items: ['把 2 个列表遍历题改写成 for，再把 2 个输入校验题改写成 while。'] },
      { title: '下一步路径', items: ['先完成 for / while 选择题，再进入 while 条件更新专项练习。'] },
      { title: '引用依据', items: [reference] },
      { title: '依据风险', items: ['低'] },
      { title: '讲解脚本', items: [`${scriptReadyText}先用列表遍历和密码输入两个场景对比 for 与 while。`] }
    ];
  }
  if (question.indexOf('break') >= 0 || question.indexOf('continue') >= 0) {
    return [
      { title: '问题诊断', items: ['你主要卡在循环控制语句的作用范围。'] },
      { title: '简明解释', items: ['break 结束当前循环；continue 跳过本轮剩余语句进入下一轮。'] },
      { title: '错误示例', items: ['把 continue 当成结束整个循环。'] },
      { title: '正确示例', items: ['如果要结束循环，应在条件满足时使用 break。'] },
      { title: '常见错误', items: ['把 continue 误认为结束循环；在 continue 前没有更新 while 循环变量。'] },
      { title: '推荐练习', items: ['完成 6 道输出结果判断题，并解释每一轮是否继续执行。'] },
      { title: '下一步路径', items: ['先做 break / continue 对比卡，再进入循环嵌套综合练习。'] },
      { title: '引用依据', items: [reference] },
      { title: '依据风险', items: ['低'] },
      { title: '讲解脚本', items: [`${scriptReadyText}逐行追踪程序执行到 break 或 continue 后的行为。`] }
    ];
  }
  if (question.indexOf('嵌套') >= 0) {
    return [
      { title: '问题诊断', items: ['你主要需要跟踪内外层循环变量的变化顺序。'] },
      { title: '简明解释', items: ['外层循环每执行一次，内层循环通常会完整执行一轮。'] },
      { title: '错误示例', items: ['内外层变量都写成 i，会让追踪过程混乱。'] },
      { title: '正确示例', items: ['外层使用 i，内层使用 j，并记录每一轮 i、j 的变化。'] },
      { title: '常见错误', items: ['内外层变量同名；只看输出结果，不记录变量变化。'] },
      { title: '推荐练习', items: ['补全九九乘法表，并写出前 3 轮 i、j 的变化。'] },
      { title: '下一步路径', items: ['先画变量变化表，再完成循环嵌套代码补全。'] },
      { title: '引用依据', items: [reference] },
      { title: '依据风险', items: ['低'] },
      { title: '讲解脚本', items: [`${scriptReadyText}把外层循环理解成行，内层循环理解成每一行里的列。`] }
    ];
  }
  return [
    { title: '问题诊断', items: ['while 死循环通常来自循环条件一直为 True，或循环变量没有在循环体内更新。'] },
    { title: '简明解释', items: ['按“初始值、循环条件、变量更新”三步检查。'] },
    { title: '错误示例', items: ['i = 0; while i < 5: print(i)，缺少 i += 1。'] },
    { title: '正确示例', items: ['i = 0; while i < 5: print(i); i += 1。'] },
    { title: '常见错误', items: ['忘记更新变量；条件方向写反；continue 跳过变量更新。'] },
    { title: '推荐练习', items: ['完成 3 道 while 循环补全题，写出前三轮变量变化。'] },
    { title: '下一步路径', items: ['进入“诊断补弱 -> 核心概念学习 -> 案例实操”的前三个节点。'] },
    { title: '引用依据', items: [reference] },
    { title: '依据风险', items: ['低'] },
    { title: '讲解脚本', items: [`${scriptReadyText}先定位循环条件为什么一直成立，再展示变量更新。`] }
  ];
}

function makeAiMessage(content, source = '学习建议', sections) {
  return {
    role: 'ai',
    content,
    source,
    sections: sections || [],
    references: {
      knowledgeBase: reference,
      profile: '李明：循环结构需巩固，建议优先完成代码实操练习'
    }
  };
}

Page({
  data: {
    examples,
    question: '为什么我的 while 循环会死循环？',
    loading: false,
    scriptMessage: '',
    messages: [
      makeAiMessage('你好，我是 EduMind AI 学伴。可以结合李明的画像，诊断 while 循环、循环嵌套和 break / continue 问题，并给出下一步练习建议。')
    ]
  },

  onLoad() {
    if (!this.data.messages || !this.data.messages.length) {
      this.setData({ messages: [makeAiMessage(defaultAnswer(this.data.question))] });
    }
  },

  onInput(event) {
    this.setData({ question: event.detail.value });
  },

  useExample(event) {
    this.setData({ question: event.currentTarget.dataset.question || '' });
  },

  sendQuestion() {
    const question = (this.data.question || '').trim();
    if (!question || this.data.loading) return;

    const userMessage = { role: 'user', content: question };
    this.setData({
      question: '',
      loading: true,
      messages: this.data.messages.concat(userMessage)
    });

    post('/api/v1/ai-tutor/ask', {
      question,
      student_name: '李明',
      course: 'Python 程序设计',
      chapter: '循环结构'
    })
      .then((res) => {
        const data = res.data || res;
        const answer = data.answer || data.content || defaultAnswer(question);
        const sections = data.cards && data.cards.length
          ? data.cards.map((card) => ({ title: card.title, items: [card.content] }))
          : structuredAnswer(question);
        this.setData({ messages: this.data.messages.concat(makeAiMessage(answer, 'AI 学伴', sections)) });
      })
      .catch(() => {
        this.setData({ messages: this.data.messages.concat(makeAiMessage(defaultAnswer(question), '学习建议', structuredAnswer(question))) });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  generateScript() {
    this.setData({ scriptMessage: scriptReadyText });
  }
});
