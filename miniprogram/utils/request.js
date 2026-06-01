const DEFAULT_BASE_URL = 'http://127.0.0.1:8000';

function getBaseUrl() {
  const app = getApp();
  return app.globalData.baseUrl || DEFAULT_BASE_URL;
}

function setBaseUrl(baseUrl) {
  const app = getApp();
  app.globalData.baseUrl = baseUrl || DEFAULT_BASE_URL;
}

function request(options) {
  const baseUrl = getBaseUrl();
  const url = /^https?:\/\//.test(options.url) ? options.url : `${baseUrl}${options.url}`;

  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'content-type': 'application/json',
        ...(options.header || {})
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      },
      fail: reject
    });
  });
}

module.exports = {
  DEFAULT_BASE_URL,
  getBaseUrl,
  setBaseUrl,
  request
};
