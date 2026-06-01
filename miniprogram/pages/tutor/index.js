const { tutorMessages, weakPoints, ragTutorFallback } = require('../../utils/demoData');
const { request } = require('../../utils/request');

Page({
  data: {
    weakPoints,
    messages: tutorMessages,
    question: '',
    ragResult: ragTutorFallback,
    fromBackend: false,
    loading: false
  },
  onInput(event) {
    this.setData({ question: event.detail.value });
  },
  sendQuestion() {
    const question = this.data.question.trim();
    if (!question) return;

    this.setData({
      loading: true,
      messages: this.data.messages.concat([{ role: 'user', content: question }]),
      question: ''
    });

    request({
      url: '/api/v1/rag/ask',
      method: 'POST',
      data: {
        question,
        courseId: 'python-programming',
        studentId: 'demo-student-zhangsan'
      }
    })
      .then((ragResult) => {
        this.setData({
          ragResult,
          fromBackend: true,
          messages: this.data.messages.concat([{ role: 'assistant', content: ragResult.answer }])
        });
      })
      .catch(() => {
        this.setData({
          ragResult: ragTutorFallback,
          fromBackend: false,
          messages: this.data.messages.concat([{ role: 'assistant', content: ragTutorFallback.answer }])
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  }
});
