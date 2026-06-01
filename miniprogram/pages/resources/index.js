const { recommendedResources, weakPoints, generatedResourcePack } = require('../../utils/demoData');
const { request } = require('../../utils/request');

Page({
  data: {
    recommendedResources,
    weakPoints,
    resourcePack: generatedResourcePack,
    packFromBackend: false,
    loadingPack: false
  },
  onLoad() {
    this.loadResourcePack();
  },
  loadResourcePack() {
    this.setData({ loadingPack: true });
    request({
      url: '/api/v1/resources/generate-pack',
      method: 'POST',
      data: {
        studentId: 'demo-student-zhangsan',
        courseId: 'demo-course-python',
        courseName: 'Python 程序设计',
        weakPoints: generatedResourcePack.weakPoints
      }
    })
      .then((resourcePack) => {
        this.setData({ resourcePack, packFromBackend: true });
      })
      .catch(() => {
        this.setData({ resourcePack: generatedResourcePack, packFromBackend: false });
      })
      .finally(() => {
        this.setData({ loadingPack: false });
      });
  }
});
