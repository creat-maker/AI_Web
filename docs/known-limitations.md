# EduMind Known Limitations

EduMind 当前是比赛工程演示版，目标是可运行、可解释、可演示、可测试，不宣称为完整商业生产系统。

## DKVMN

DKVMN 已实现 softmax key 寻址、动态 value memory 读取和 erase/add 门控写入，并包含概念转移矩阵、练习-概念矩阵、JSON 持久化和画像映射。当前采用在线更新，没有论文规模训练数据或预训练 checkpoint，因此不声称复现论文级指标。

## 多模态资源

多模态资源支持 html、markdown、audio、video 预览与 fallback。未配置 TTS 或 FFmpeg 时返回讲解文本、HTML 动画、视频脚本和可解释状态，不虚假宣传真实视频生成。

## 外部 AI 与安全 API

LLM、讯飞 TTS、讯飞安全 API、Chroma、SentenceTransformer 均为可配置能力。未配置时系统使用规则引擎、TF-IDF、JSON 知识库和 demoData fallback，保证比赛现场断网或服务未启动时不白屏。

## 数据规模

当前检索评估数据集较小，仅用于验证链路命中和引用结构，不代表大规模真实课堂评测结论。

## 小程序

小程序优先请求后端 API，失败后 fallback 到本地演示数据。真机调试需要把 `miniprogram/config/api.js` 中的后端地址改为局域网 IP。
