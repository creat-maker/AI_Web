const { BASE_URL } = require('./config/api');

App({
  globalData: {
    baseUrl: BASE_URL,
    student: {
      id: 'demo-basic',
      name: '李明',
      course: 'Python 程序设计',
      chapter: '循环结构'
    }
  }
});
