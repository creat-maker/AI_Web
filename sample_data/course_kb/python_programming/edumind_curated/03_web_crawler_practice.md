# Python 网络爬虫实践

## HTTP 请求响应模型

网络爬虫的基本过程是：客户端向服务器发送 HTTP 请求，服务器返回 HTTP 响应，程序从响应内容中提取需要的数据。一次常见的网页采集流程包括 URL、请求方法、请求头、状态码、响应正文和解析规则。

## requests 发送请求的基本步骤

1. 导入 `requests` 库。
2. 准备目标 URL。
3. 使用 `requests.get()` 或 `requests.post()` 发送请求。
4. 检查 `response.status_code` 是否为 200。
5. 使用 `response.text` 获取网页文本，或使用 `response.content` 获取二进制内容。
6. 解析网页并保存结果。

```python
import requests

url = "https://example.com"
response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
if response.status_code == 200:
    html = response.text
    print(html[:200])
else:
    print("请求失败", response.status_code)
```

## 请求失败时应该先检查什么

爬虫请求失败时，建议按以下顺序检查：

1. URL 是否正确。
2. 网络是否可达。
3. 状态码是否为 200、403、404、500 等。
4. 是否缺少 `User-Agent` 等请求头。
5. 是否需要登录、Cookie 或 Token。
6. 是否触发了网站反爬限制。
7. 是否设置了合理的超时时间。

## 网页解析方式

常见解析方式包括正则表达式、BeautifulSoup、lxml 和 Selenium。正则表达式适合简单文本匹配，但面对复杂 HTML 容易脆弱；BeautifulSoup 更适合按标签、属性和层级解析静态网页；Selenium 可以处理 JavaScript 动态渲染页面，但速度较慢、资源消耗较高。

## 数据保存方式

小型项目可以把数据保存为 CSV 或 JSON。CSV 适合表格型数据，JSON 适合结构化对象数据。保存文件时建议使用 `with open`，并明确编码。

## 合规要求

爬虫实践必须遵守网站 robots 协议、访问频率限制和数据使用边界。课程练习应优先使用公开示例网站、教师提供的静态 HTML 或本地测试页面。

## 实践任务

设计一个“课程公告采集器”：从教师提供的 HTML 页面中提取公告标题、发布时间和链接，保存为 CSV 文件，并记录请求失败时的错误信息。
