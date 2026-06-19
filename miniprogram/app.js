const { BASE_URL } = require('./utils/config');

App({
  globalData: {
    baseUrl: BASE_URL,
    student: {
      id: 1,
      name: '李明',
      course: 'Python 程序设计'
    }
  }
});
