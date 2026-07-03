const config = require('./config');
const request = require('./request');
const demoData = require('./demoData');

function fallback(payloadKey, friendlyMessage) {
  return Promise.resolve({
    data: demoData[payloadKey],
    fallback: true,
    message: friendlyMessage || '当前为本地示例数据'
  });
}

function requestOrFallback(options, payloadKey) {
  if (!config.fallbackToDemoData) {
    return request.request(options);
  }
  return request.request(options).then((data) => ({ data, fallback: false })).catch((error) => {
    const message = error && error.friendlyMessage ? error.friendlyMessage : '当前为本地示例数据';
    return fallback(payloadKey, message);
  });
}

function getDemoStatus() {
  return requestOrFallback({ url: '/demo-status', showLoading: false }, 'homeStats');
}

function getProfileVisualization() {
  return requestOrFallback({ url: '/student-profile/demo', showLoading: false }, 'student');
}

function getLearningPathSummary() {
  return requestOrFallback({ url: '/learning-paths/recommend', showLoading: false }, 'learningPath');
}

function getQuizList() {
  return requestOrFallback({ url: '/quizzes', showLoading: false }, 'quizResult');
}

function submitQuiz(payload) {
  return requestOrFallback({ url: '/quizzes/submit', method: 'POST', data: payload, loadingText: '提交测评' }, 'quizResult');
}

function getReports() {
  return requestOrFallback({ url: '/reports', showLoading: false }, 'report');
}

module.exports = {
  config,
  requestOrFallback,
  getDemoStatus,
  getProfileVisualization,
  getLearningPathSummary,
  getQuizList,
  submitQuiz,
  getReports
};
