# 开源依赖与 AI 工具说明

本项目未在本轮口径清理中引入新的重量级依赖。依赖版本以 `frontend/package.json`、`backend/requirements.txt` 和实际安装环境为准。

## 一、主要开源依赖

| 依赖 | 用途 | 版本或版本范围 | 许可类型 |
| --- | --- | --- | --- |
| FastAPI | 后端 Web API 框架 | 以 `requirements.txt` / 安装环境为准 | MIT |
| Uvicorn | ASGI 服务运行 | 以 `requirements.txt` / 安装环境为准 | BSD-3-Clause |
| Pydantic | 请求/响应数据校验 | 以 `requirements.txt` / 安装环境为准 | MIT |
| SQLAlchemy | 数据模型与数据库访问 | 以 `requirements.txt` / 安装环境为准 | MIT |
| Vue | 前端 UI 框架 | `^3.5.14` | MIT |
| Vite | 前端开发与构建工具 | `^6.3.5` | MIT |
| TypeScript | 前端类型系统 | `^5.8.3` | Apache-2.0 |
| ECharts | 可视化图表 | `^6.1.0` | Apache-2.0 |
| vue-router | 前端路由 | `^4.5.1` | MIT |
| 微信小程序原生框架 | 小程序页面、组件和运行环境 | 以微信开发者工具为准 | 微信平台规范 |

## 二、AI 能力使用边界

- AI 用于对话式画像、资源生成、学习路径建议、AI 学伴回答、报告生成辅助和内容审核辅助。
- 未配置真实大模型或数字人相关密钥时，系统使用本地 mock fallback。
- 生成内容需经过事实准确性、知识点匹配度、难度匹配度、引用依据完整性、敏感违规内容和人工复核建议检查。
- AI 生成内容不直接作为未经审核的最终教学事实依据。

## 三、数字人说明

当前项目只提供“数字人讲解脚本 / TTS 或数字人 API 预留”能力，不描述为完整实时数字人系统。
