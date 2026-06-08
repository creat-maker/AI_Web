const { BASE_URL, USE_BACKEND } = require('./config');

function buildUrl(url) {
  if (/^https?:\/\//.test(url)) {
    return url;
  }
  return BASE_URL.replace(/\/$/, '') + '/' + String(url || '').replace(/^\//, '');
}

function request(options) {
  const method = (options.method || 'GET').toUpperCase();

  if (!USE_BACKEND) {
    return Promise.reject({
      message: '离线服务未连接后端',
      disabled: true
    });
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: buildUrl(options.url),
      method,
      data: options.data || {},
      header: Object.assign({
        'Content-Type': 'application/json'
      }, options.header || {}),
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject({
          message: 'HTTP ' + res.statusCode,
          statusCode: res.statusCode,
          data: res.data
        });
      },
      fail(err) {
        reject(err);
      }
    });
  });
}

function get(url, data, header) {
  return request({ url, data, header, method: 'GET' });
}

function post(url, data, header) {
  return request({ url, data, header, method: 'POST' });
}

module.exports = {
  request,
  get,
  post
};
