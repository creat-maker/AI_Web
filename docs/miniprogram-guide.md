# EduMind 小程序学生端体验版

`miniprogram` 是 EduMind 的原生微信小程序学生端体验版，用于比赛展示移动端学习闭环。当前版本不依赖后端即可打开，页面数据来自 `miniprogram/utils/demoData.js`。

## 目录结构

```text
miniprogram/
  app.js
  app.json
  app.wxss
  project.config.json
  utils/
    demoData.js
    request.js
  pages/
    home/index       今日学习
    path/index       学习路径
    resources/index  资源推荐
    tutor/index      AI 辅导
    quiz/index       练习错题
    report/index     学习报告
```

## 使用微信开发者工具打开

1. 打开微信开发者工具。
2. 选择“导入项目”。
3. 项目目录选择：`EduMind/miniprogram`。
4. AppID 可以选择“测试号”或使用无 AppID 模式；当前 `project.config.json` 使用 `touristappid`，适合本地预览。
5. 导入后点击“编译”，默认进入“今日学习”页面。

## 页面说明

- 首页：展示张三今日学习概览、课程进度、今日任务和薄弱点。
- 路径：展示个性化学习路径的阶段、状态和完成比例。
- 资源：根据薄弱点展示推荐微课、讲义、Notebook 和交互演示。
- 辅导：展示 AI 辅导对话体验，支持本地追加提问演示。
- 练习错题：展示错题清单、订正状态和复盘建议。
- 报告：展示综合评分、学习总结、改进建议和薄弱点。

## 切换后端地址

默认后端地址在两个位置保留：

- `miniprogram/app.js`：`globalData.baseUrl`
- `miniprogram/utils/request.js`：`DEFAULT_BASE_URL`

本地 FastAPI 默认值为：

```js
http://127.0.0.1:8000
```

如果要连接局域网后端，请把地址改为电脑局域网 IP，例如：

```js
http://192.168.1.8:8000
```

微信开发者工具中调试本地接口时，可在“详情 -> 本地设置”中勾选“不校验合法域名、web-view、TLS 版本以及 HTTPS 证书”。正式发布时需要配置微信小程序合法 request 域名，并使用 HTTPS。

## 接入真实 API 的建议

当前页面优先使用 `demoData.js`，后续可以逐步替换为真实接口：

1. 在页面 `onLoad` 中调用 `utils/request.js` 的 `request()`。
2. 对接 FastAPI 学生端接口，例如课程、学习路径、资源推荐、智能答疑、测验和报告。
3. 请求失败时继续回退到 `demoData.js`，保证比赛现场可演示。
4. 增加登录态后，可把学生 ID、班级 ID 或 token 存入 `wx.setStorageSync`。

示例：

```js
const { request } = require('../../utils/request');

request({ url: '/api/v1/learning-paths' })
  .then((data) => this.setData({ learningPath: data.items || data }))
  .catch(() => {
    // 保留 demoData fallback，避免现场断网或后端未启动时空白。
  });
```
