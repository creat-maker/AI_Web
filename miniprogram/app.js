const { BASE_URL } = require('./utils/config');

App({
  globalData: {
    baseUrl: BASE_URL,
    student: {
      id: 1,
      name: '张三',
      course: 'Python 程序设计'
    }
  }
});
