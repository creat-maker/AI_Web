const { BASE_URL, USE_BACKEND, API_PREFIX } = require('../config/api');

function buildUrl(url) {
  if (/^https?:\/\//.test(url)) return url;
  const normalized = String(url || '').replace(/^\//, '');
  const prefix = normalized.indexOf('api/') === 0 || normalized.indexOf('api/v1/') === 0
    ? ''
    : API_PREFIX.replace(/^\/|\/$/g, '') + '/';
  return BASE_URL.replace(/\/$/, '') + '/' + prefix + normalized;
}

function request(options) {
  const method = (options.method || 'GET').toUpperCase();
  const showLoading = options.showLoading !== false;

  if (!USE_BACKEND) {
    return Promise.reject({ friendlyMessage: '当前使用初始化课程数据，联网后可同步最新学习记录。' });
  }

  if (showLoading) {
    wx.showLoading({ title: options.loadingText || '加载中', mask: true });
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: buildUrl(options.url),
      method,
      data: options.data || {},
      header: Object.assign({ 'Content-Type': 'application/json' }, options.header || {}),
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject({
          statusCode: res.statusCode,
          data: res.data,
          friendlyMessage: '暂时无法同步最新数据，已保留本地学习内容。'
        });
      },
      fail() {
        reject({ friendlyMessage: '暂时无法连接学习服务，已保留本地学习内容。' });
      },
      complete() {
        if (showLoading) wx.hideLoading();
      }
    });
  });
}

function get(url, data, header, options = {}) {
  return request({ ...options, url, data, header, method: 'GET' });
}

function post(url, data, header, options = {}) {
  return request({ ...options, url, data, header, method: 'POST' });
}

module.exports = { request, get, post, buildUrl };
