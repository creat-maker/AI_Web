const { post } = require('../../utils/request');

const DIMENSIONS = [
  { key: 'current_level', label: '当前水平' },
  { key: 'learning_goal', label: '学习目标' },
  { key: 'weak_points', label: '薄弱知识点' },
  { key: 'learning_preference', label: '学习偏好' },
  { key: 'diagnosis', label: '学习诊断' },
  { key: 'strategy', label: '学习策略' }
];

const FALLBACK_QUESTIONS = {
  current_level: '你目前 Python 编程大概是什么水平？比如能不能独立写出函数和循环？',
  learning_goal: '你这学期 Python 课程的学习目标是什么？比如通过考试、完成项目还是提升编程能力？',
  weak_points: '你在 Python 学习中，哪些知识点觉得最难或最容易出错？',
  learning_preference: '你更喜欢哪种学习方式？看视频、读讲义、做练习还是动手写项目？',
  diagnosis: '你觉得目前学习最大的障碍是什么？是概念理解、代码实践还是时间安排？',
  strategy: '你平时是怎么安排 Python 学习的？有没有固定的复习或练习习惯？'
};

const FALLBACK_REPLIES = {
  current_level: '了解了你的编程基础，我会据此调整学习内容的深度。',
  learning_goal: '目标已记录，后续推荐资源会围绕你的目标来安排。',
  weak_points: '薄弱点已识别，系统会优先推荐针对性的练习和讲义。',
  learning_preference: '偏好已保存，后续资源类型会匹配你的学习风格。',
  diagnosis: '诊断信息已更新，我会帮你制定更有针对性的学习计划。',
  strategy: '学习策略已记录，后续任务安排会考虑你的学习节奏。'
};

function detectDimension(text) {
  const lower = text.toLowerCase();
  if (/水平|基础|掌握|会写|能写|入门|初级|中级|高级/.test(lower)) return 'current_level';
  if (/目标|目的|想|希望|考试|通过|项目|提升/.test(lower)) return 'learning_goal';
  if (/薄弱|难点|出错|不会|困难|容易错|搞不懂/.test(lower)) return 'weak_points';
  if (/偏好|喜欢|方式|视频|讲义|练习|项目|动手/.test(lower)) return 'learning_preference';
  if (/障碍|问题|卡|理解|实践|时间|安排|拖延/.test(lower)) return 'diagnosis';
  if (/策略|习惯|复习|计划|节奏|安排/.test(lower)) return 'strategy';
  return null;
}

function getNextDimension(extracted) {
  for (const dim of DIMENSIONS) {
    if (!extracted[dim.key]) return dim.key;
  }
  return null;
}

Page({
  data: {
    studentName: '张三',
    sessionId: '',
    userInput: '',
    loading: false,
    fromBackend: false,
    completed: false,
    ready: false,
    filledCount: 0,
    progressPercent: 0,
    extracted: {},
    dimensions: DIMENSIONS.map(d => ({ ...d, filled: false, value: '' })),
    messages: []
  },

  onLoad() {
    const opening = '你好，我是 EduMind 画像助手！我会通过几个问题帮你构建学习画像，这样系统就能为你推荐最适合的学习内容。\n\n让我们开始吧——' + FALLBACK_QUESTIONS.current_level;
    this.setData({
      messages: [{ role: 'ai', content: opening }]
    });
    this._tryStartBackend();
  },

  _tryStartBackend() {
    post('/api/v1/profile-dialog/start', {
      student_name: '张三',
      course_id: 1
    })
      .then(res => {
        const data = res.data || res;
        if (data.session_id) {
          this.setData({
            sessionId: data.session_id,
            fromBackend: true,
            messages: [{ role: 'ai', content: data.reply || this.data.messages[0].content }]
          });
          if (data.extracted) {
            this._updateExtracted(data.extracted);
          }
          if (data.ready) {
            this.setData({ ready: true });
          }
        }
      })
      .catch(() => {
        this.setData({ fromBackend: false });
      });
  },

  onInput(event) {
    this.setData({ userInput: event.detail.value });
  },

  sendMessage() {
    const text = this.data.userInput.trim();
    if (!text || this.data.loading) return;

    const userMsg = { role: 'user', content: text };
    const messages = this.data.messages.concat(userMsg);
    this.setData({ userInput: '', loading: true, messages });

    if (this.data.sessionId && this.data.fromBackend) {
      this._sendBackend(text);
    } else {
      this._sendFallback(text);
    }
  },

  _sendBackend(text) {
    post('/api/v1/profile-dialog/continue', {
      session_id: this.data.sessionId,
      message: text
    })
      .then(res => {
        const data = res.data || res;
        const aiMsg = { role: 'ai', content: data.reply || '请继续描述你的学习情况。' };
        const messages = this.data.messages.concat(aiMsg);
        this.setData({ messages, loading: false });
        if (data.extracted) {
          this._updateExtracted(data.extracted);
        }
        if (data.ready) {
          this.setData({ ready: true });
        }
        if (data.completed) {
          this.setData({ completed: true });
        }
      })
      .catch(() => {
        this._sendFallback(text);
      });
  },

  _sendFallback(text) {
    const dim = detectDimension(text);
    const extracted = { ...this.data.extracted };

    if (dim && !extracted[dim]) {
      extracted[dim] = text;
    } else if (!dim) {
      const nextDim = getNextDimension(extracted);
      if (nextDim && !extracted[nextDim]) {
        extracted[nextDim] = text;
      }
    }

    const nextDim = getNextDimension(extracted);
    let reply;
    if (nextDim) {
      const lastDim = dim || Object.keys(extracted).pop();
      reply = (lastDim && FALLBACK_REPLIES[lastDim] ? FALLBACK_REPLIES[lastDim] + '\n\n' : '') + FALLBACK_QUESTIONS[nextDim];
    } else {
      reply = '太好了！我已经收集了全部 6 个维度的信息，你的学习画像已经构建完成。点击"完成画像"按钮保存。';
    }

    const aiMsg = { role: 'ai', content: reply };
    const messages = this.data.messages.concat(aiMsg);
    this.setData({ messages, loading: false });
    this._updateExtracted(extracted);

    if (!nextDim) {
      this.setData({ ready: true });
    }
  },

  _updateExtracted(extracted) {
    const filledCount = Object.keys(extracted).length;
    const dimensions = DIMENSIONS.map(d => ({
      ...d,
      filled: !!extracted[d.key],
      value: extracted[d.key] || ''
    }));
    this.setData({
      extracted,
      filledCount,
      progressPercent: Math.round((filledCount / 6) * 100),
      dimensions
    });
  },

  finishDialog() {
    if (this.data.sessionId && this.data.fromBackend) {
      post('/api/v1/profile-dialog/finish', {
        session_id: this.data.sessionId
      })
        .then(res => {
          const data = res.data || res;
          if (data.extracted) {
            this._updateExtracted(data.extracted);
          }
          this.setData({ completed: true });
        })
        .catch(() => {
          this.setData({ completed: true });
        });
    } else {
      this.setData({ completed: true });
    }
  },

  goPath() {
    wx.switchTab({ url: '/pages/path/index' });
  }
});
