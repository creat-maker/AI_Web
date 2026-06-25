# EduMind 科大讯飞 API 接口文档

> 项目：EduMind —— 基于大模型的个性化资源生成与学习多智能体系统  
> 赛题：A3-基于大模型的个性化资源生成与学习多智能体系统开发  
> 版本：V1.0  
> 建议存放位置：`docs/科大讯飞_API_接口文档.md`  
> 适用范围：Web 主系统、微信小程序体验版、后端 AI 能力层、多智能体编排模块

---

## 1. 文档目标

本文档用于说明 EduMind 系统中可能接入的科大讯飞开放平台能力，并将其整理为项目后端可落地的接口设计。

EduMind 不建议将“科大讯飞 API”简单写成“星火大模型 API”，而应根据赛题功能拆分为以下几类能力：

1. 星火认知大模型：负责文本生成、结构化推理、画像抽取、题库生成、路径规划、学习报告生成。
2. 星火知识库：负责课程资料上传、文档切分、向量检索、RAG 问答、引用溯源、防幻觉。
3. 大模型安全护栏：负责学生输入、模型输出、多模态内容的安全审核。
4. OCR 与图片理解：负责拍照提问、课程图片识别、图文问答。
5. 语音听写与语音合成：负责小程序语音提问、讲解音频、视频旁白。
6. 图片生成与 PPT 生成：负责多模态学习资源扩展。
7. 讯飞星辰 Agent：可选，用于展示科大讯飞智能体平台能力。

---

## 2. API 选型总览

| 优先级 | 科大讯飞 API | EduMind 中的用途 | 对应模块 / Agent |
|---|---|---|---|
| P0 必须 | 星火认知大模型 HTTP API | 学生画像抽取、学习路径规划、讲义生成、题库生成、代码案例生成、智能辅导、学习报告生成 | 画像 Agent、资源规划 Agent、文档 Agent、题库 Agent、代码 Agent、路径 Agent、评估 Agent |
| P0 必须 | 星火知识库 API / ChatDoc API | 上传课程大纲、教材、PPT、实验指导书，做 RAG 检索、文档问答、引用溯源、防幻觉 | 课程解析 Agent、检索 Agent、审核 Agent |
| P0 必须 | 大模型安全护栏 API | 对学生输入、模型输出、图片输入/输出做安全过滤，满足赛题“防幻觉与内容安全”要求 | 审核 Agent、`/api/audit` |
| P1 强烈建议 | 通用文档识别 OCR 大模型 / 通用文字识别 API | 拍照提问、试卷/板书/课件截图识别、文档图片转文本 | 小程序 AI 辅导页、拍照提问 |
| P1 强烈建议 | 图片理解 API | 学生上传图片后，让模型理解图片内容并结合问题答疑 | 多模态 Agent、小程序拍照问答 |
| P1 强烈建议 | 语音听写流式 API | 小程序语音提问、移动端即时答疑输入 | 小程序 AI 辅导页 |
| P1 强烈建议 | 在线语音合成 / 超拟人语音合成 API | 将讲解文本、视频脚本、错题解析转成语音旁白 | 多模态 Agent、视频/动画资源生成 |
| P2 可选加分 | 图片生成 API / HiDream 图片生成 API | 生成知识点配图、概念插图、封面图、学习卡片图 | 多模态 Agent |
| P2 可选加分 | 智能 PPT 生成 API | 根据知识点/讲义生成课程 PPT 或复习 PPT | 资源生成页、教师端资源生成 |
| P2 可选替代架构 | 讯飞星辰 Agent 开发平台 / 工作流 API | 可将部分 Agent 发布成 API；否则也可以使用自研 Agent 编排器 | Agent 工作流页、管理/评审端 |

---

## 3. 系统内部封装原则

### 3.1 推荐封装架构

```text
frontend / miniprogram
        ↓
EduMind Backend API
        ↓
ai_provider/xfyun/
        ├─ spark_llm.py
        ├─ spark_kb.py
        ├─ spark_safety.py
        ├─ spark_ocr.py
        ├─ spark_vision.py
        ├─ spark_asr.py
        ├─ spark_tts.py
        ├─ spark_image.py
        └─ spark_ppt.py
        ↓
科大讯飞开放平台 API
```

### 3.2 封装原则

1. Web 前端和微信小程序只调用 EduMind 自己的后端 API。
2. 前端和小程序不直接保存或传输科大讯飞密钥。
3. 所有科大讯飞 API 调用统一在后端 `ai_provider/xfyun/` 中封装。
4. 所有 AI 生成任务都应记录到 `agent_tasks` 表。
5. 所有安全审核结果都应记录到 `audit_records` 表。
6. 长耗时生成任务应提供任务状态查询接口，避免前端白屏等待。
7. 文本生成类接口优先使用流式输出。
8. 结构化结果，如画像、题库、学习路径、学习报告，应要求模型输出 JSON。

---

## 4. 环境变量配置

建议在 `.env.example` 中加入以下配置。

```env
# =========================
# Xunfei Spark LLM
# =========================
XF_SPARK_HTTP_BASE_URL=https://spark-api-open.xf-yun.com/v1
XF_SPARK_API_PASSWORD=your_api_password
XF_SPARK_MODEL_FAST=lite
XF_SPARK_MODEL_MAIN=4.0Ultra
XF_SPARK_MODEL_JSON=4.0Ultra

# =========================
# Xunfei General App Auth
# =========================
XF_APP_ID=your_app_id
XF_API_KEY=your_api_key
XF_API_SECRET=your_api_secret

# =========================
# Xunfei ChatDoc / Knowledge Base
# =========================
XF_CHATDOC_APP_ID=your_chatdoc_app_id
XF_CHATDOC_SECRET=your_chatdoc_secret
XF_CHATDOC_BASE_URL=https://chatdoc.xfyun.cn/openapi

# =========================
# Xunfei Safety Guard
# =========================
XF_SAFETY_APP_ID=your_safety_app_id
XF_SAFETY_ACCESS_KEY_ID=your_access_key_id
XF_SAFETY_ACCESS_KEY_SECRET=your_access_key_secret
XF_SAFETY_BASE_URL=http://audit-api-spark-dx.iflyaisol.com

# =========================
# Xunfei PPT
# =========================
XF_PPT_APP_ID=your_ppt_app_id
XF_PPT_API_SECRET=your_ppt_api_secret
XF_PPT_BASE_URL=https://zwapi.xfyun.cn
```

---

## 5. 星火认知大模型接口

### 5.1 用途

星火认知大模型是 EduMind 的核心文本生成与推理能力，主要用于：

- 学生画像抽取
- 学习路径规划
- 个性化讲义生成
- 思维导图文本生成
- 练习题生成
- 代码案例生成
- AI 辅导答疑
- 错题解析
- 学习效果评估
- 学习报告生成
- Agent 任务计划生成
- 审核解释与可信度说明

---

### 5.2 你们系统内部接口

```http
POST /api/ai/spark/chat
```

### 5.3 对接讯飞接口

```http
POST https://spark-api-open.xf-yun.com/v1/chat/completions
```

### 5.4 请求头

```http
Authorization: Bearer ${XF_SPARK_API_PASSWORD}
Content-Type: application/json
```

### 5.5 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `scene` | string | 否 | EduMind 内部场景，例如 `profile_extract`、`resource_generate` |
| `student_id` | string | 否 | 学生 ID |
| `course_id` | string | 否 | 课程 ID |
| `model` | string | 是 | 星火模型名称，例如 `4.0Ultra` |
| `messages` | array | 是 | 对话消息 |
| `stream` | boolean | 否 | 是否流式输出 |
| `temperature` | number | 否 | 随机性 |
| `max_tokens` | number | 否 | 最大输出长度 |
| `response_format` | object/string | 否 | 可要求 JSON 输出 |
| `tools` | array | 否 | Function Call 工具定义 |

---

### 5.6 学生画像抽取示例

#### 请求

```json
{
  "scene": "profile_extract",
  "student_id": "stu_001",
  "model": "4.0Ultra",
  "stream": false,
  "response_format": {
    "type": "json_object"
  },
  "messages": [
    {
      "role": "system",
      "content": "你是 EduMind 的画像 Agent。请根据学生自然语言描述，抽取结构化学习画像。必须输出 JSON，不要输出解释性文字。"
    },
    {
      "role": "user",
      "content": "我是计算机专业研一学生，机器学习基础一般，想两周内学会神经网络。我更喜欢图解和代码案例，数学公式有点吃力。"
    }
  ]
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "profile": {
      "major": "计算机",
      "education_level": "研一",
      "knowledge_base": "机器学习基础一般",
      "learning_goal": "两周内掌握神经网络",
      "cognitive_style": "图解和案例驱动",
      "weaknesses": ["数学公式理解", "神经网络基础", "反向传播"],
      "preferred_resource_types": ["图解", "代码案例", "练习题"],
      "available_time": null,
      "error_prone_points": ["公式推导", "梯度计算"]
    },
    "provider": "xfyun_spark",
    "model": "4.0Ultra"
  }
}
```

---

### 5.7 题库生成示例

```http
POST /api/generate/questions
```

#### 请求

```json
{
  "student_id": "stu_001",
  "course_id": "ai_001",
  "knowledge_point_id": "kp_bp_001",
  "question_types": ["single_choice", "multiple_choice", "judge", "short_answer", "coding"],
  "difficulty": "adaptive",
  "count": 10
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "questions": [
      {
        "type": "single_choice",
        "stem": "反向传播算法主要用于解决什么问题？",
        "options": ["A. 数据归一化", "B. 梯度计算", "C. 模型部署", "D. 数据采样"],
        "answer": "B",
        "explanation": "反向传播通过链式法则高效计算损失函数对各层参数的梯度。",
        "difficulty": "easy",
        "knowledge_point_id": "kp_bp_001"
      }
    ]
  }
}
```

---

### 5.8 参数建议

| 场景 | `stream` | `temperature` | `response_format` |
|---|---:|---:|---|
| 画像抽取 | false | 0.2 | JSON |
| 学习路径生成 | false | 0.3 | JSON |
| 题库生成 | false | 0.4 | JSON |
| 代码案例生成 | true | 0.3 | Markdown / JSON |
| AI 辅导 | true | 0.5 | Markdown |
| 视频脚本 | true | 0.7 | Markdown / JSON |
| 学习报告 | false | 0.3 | JSON |

---

## 6. 星火知识库 / ChatDoc 接口

### 6.1 用途

星火知识库主要用于构建课程 RAG 系统，支撑：

- 课程资料上传
- 文档切分
- 文档向量化
- 课程知识检索
- 文档问答
- 引用溯源
- 防幻觉审核
- 教师端课程知识库管理

---

### 6.2 创建课程知识库

#### 系统内部接口

```http
POST /api/ai/kb/repos
```

#### 对接讯飞接口

```http
POST https://chatdoc.xfyun.cn/openapi/v1/repo/create
```

#### 请求

```json
{
  "course_id": "ai_001",
  "repo_name": "人工智能导论课程知识库",
  "repo_desc": "课程大纲、讲义、实验指导书、课件与参考资料",
  "repo_tags": "AI,机器学习,神经网络"
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "repo_id": "xf_repo_xxx",
    "course_id": "ai_001"
  }
}
```

---

### 6.3 上传课程文档

#### 系统内部接口

```http
POST /api/ai/kb/files
Content-Type: multipart/form-data
```

#### 对接讯飞接口

```http
POST https://chatdoc.xfyun.cn/openapi/v1/file/upload
```

#### 请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `course_id` | string | 是 | 本地课程 ID |
| `repo_id` | string | 是 | 讯飞知识库 ID |
| `file` | file | 是 | 课程文件 |
| `source_type` | string | 否 | `syllabus` / `ppt` / `lab` / `textbook` |

#### 返回

```json
{
  "code": 0,
  "data": {
    "file_id": "xf_file_xxx",
    "repo_id": "xf_repo_xxx",
    "file_status": "uploaded"
  }
}
```

---

### 6.4 文档切分与向量化

#### 系统内部接口

```http
POST /api/ai/kb/files/{file_id}/embedding
```

#### 对接讯飞接口

```http
POST https://chatdoc.xfyun.cn/openapi/v1/file/embedding
```

#### 请求

```json
{
  "repo_id": "xf_repo_xxx",
  "file_id": "xf_file_xxx"
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "file_id": "xf_file_xxx",
    "embedding_status": "processing"
  }
}
```

---

### 6.5 课程知识检索

#### 系统内部接口

```http
POST /api/ai/kb/search
```

#### 对接讯飞接口

```http
POST https://chatdoc.xfyun.cn/openapi/v1/vector/search
```

#### 请求

```json
{
  "repo_id": "xf_repo_xxx",
  "query": "反向传播算法的链式法则如何理解？",
  "top_k": 5
}
```

#### 返回

```json
{
  "code": 0,
  "data": [
    {
      "content": "反向传播算法通过链式法则计算损失函数对每层参数的梯度……",
      "score": 83.2,
      "file_id": "xf_file_xxx",
      "source": "神经网络讲义第3章"
    }
  ]
}
```

---

### 6.6 文档 / 知识库问答

#### 系统内部接口

```http
POST /api/ai/kb/chat
```

#### 对接讯飞接口

```text
wss://chatdoc.xfyun.cn/openapi/chat?appId=xxx&timestamp=xxx&signature=xxx
```

#### 请求

```json
{
  "repo_id": "xf_repo_xxx",
  "student_id": "stu_001",
  "question": "反向传播为什么要从输出层往前传播？",
  "use_profile": true
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "answer": "反向传播从输出层开始，是因为损失函数首先直接依赖输出层结果……",
    "references": [
      {
        "file_id": "xf_file_xxx",
        "source": "神经网络讲义第3章",
        "content": "……"
      }
    ]
  }
}
```

---

## 7. 大模型安全护栏接口

### 7.1 用途

安全护栏用于满足赛题中的“防幻觉与内容安全过滤机制”要求。

主要用于：

- 学生输入审核
- 模型输出审核
- 图片输入审核
- 图片输出审核
- 流式输出分段审核
- 生成内容风险等级记录
- 教师端审核中心展示

---

### 7.2 用户输入审核

#### 系统内部接口

```http
POST /api/ai/safety/input
```

#### 对接讯飞接口

```http
POST http://audit-api-spark-dx.iflyaisol.com/audit/v3/aichat/input
```

#### 请求

```json
{
  "student_id": "stu_001",
  "chat_sid": "chat_20260531_001",
  "content": "学生输入的问题",
  "intention": "dialog"
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "action": "none",
    "ctx_control": null,
    "risk_level": "safe"
  }
}
```

---

### 7.3 模型输出审核

#### 系统内部接口

```http
POST /api/ai/safety/output
```

#### 对接讯飞接口

```http
POST http://audit-api-spark-dx.iflyaisol.com/audit/v3/aichat/output
```

#### 请求

```json
{
  "chat_sid": "chat_20260531_001",
  "content": "模型生成的第1段回答",
  "pindex": 1,
  "is_end": 0,
  "intention": "dialog"
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "action": "none",
    "risk_level": "safe",
    "suggestion": "pass"
  }
}
```

---

### 7.4 图片输入审核

#### 系统内部接口

```http
POST /api/ai/safety/input-media
```

#### 对接讯飞接口

```http
POST http://audit-api-spark-dx.iflyaisol.com/audit/v3/aichat/inputMedia
```

#### 请求

```json
{
  "student_id": "stu_001",
  "chat_sid": "chat_20260531_002",
  "image_base64": "base64_image",
  "image_format": "jpg",
  "scene": "photo_question"
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "action": "none",
    "risk_level": "safe"
  }
}
```

---

## 8. OCR 接口

## 8.1 通用文档识别 OCR 大模型

### 用途

适合识别复杂文档、课件截图、实验指导书截图、试卷图片、公式、表格、栏目等内容。

### 系统内部接口

```http
POST /api/ai/ocr/document
```

### 对接讯飞接口

```http
POST https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm
```

### 请求

```json
{
  "image_base64": "base64_image",
  "image_format": "jpg",
  "scene": "homework_photo"
}
```

### 返回

```json
{
  "code": 0,
  "data": {
    "text": "识别出的文档内容……",
    "blocks": [
      {
        "type": "paragraph",
        "text": "反向传播算法……"
      },
      {
        "type": "formula",
        "text": "dL/dw = dL/dy * dy/dw"
      }
    ]
  }
}
```

---

## 8.2 通用文字识别

### 用途

适合普通图片中的印刷体或手写文字识别，例如课堂板书、学生笔记、题目截图。

### 系统内部接口

```http
POST /api/ai/ocr/text
```

### 对接讯飞接口

```http
POST https://api.xf-yun.com/v1/private/sf8e6aca1
```

### 请求

```json
{
  "image_base64": "base64_image",
  "image_format": "png"
}
```

### 返回

```json
{
  "code": 0,
  "data": {
    "text": "识别出的文字内容……"
  }
}
```

---

## 9. 图片理解接口

### 9.1 用途

图片理解 API 用于多模态问答，例如：

- 学生拍一道题问“这题怎么做？”
- 学生上传神经网络结构图问“这张图是什么意思？”
- 教师上传流程图，让系统生成知识点讲解。
- 识别实验截图中的错误现象，并给出排查建议。

---

### 9.2 系统内部接口

```http
POST /api/ai/vision/understand
```

### 9.3 对接讯飞接口

```text
wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image
```

### 9.4 请求

```json
{
  "student_id": "stu_001",
  "course_id": "ai_001",
  "image_base64": "base64_image",
  "question": "请解释这张神经网络结构图，并指出每一层的作用。"
}
```

### 9.5 返回

```json
{
  "code": 0,
  "data": {
    "answer": "这张图展示了一个前馈神经网络结构……",
    "detected_concepts": ["输入层", "隐藏层", "输出层", "权重", "激活函数"],
    "recommended_resources": [
      {
        "type": "lecture",
        "title": "神经网络结构入门讲义"
      }
    ]
  }
}
```

---

## 10. 语音听写接口

### 10.1 用途

语音听写用于小程序端“按住说话”，把语音问题实时转换成文字，再交给 AI 辅导模块处理。

---

### 10.2 系统内部接口

```http
WebSocket /api/ai/asr/stream
```

### 10.3 对接讯飞接口

```text
wss://iat-api.xfyun.cn/v2/iat
```

### 10.4 前端流程

```text
小程序录音
    ↓
后端 WebSocket 代理
    ↓
讯飞语音听写
    ↓
返回实时文本
    ↓
调用 /api/tutor/chat
```

### 10.5 返回示例

```json
{
  "code": 0,
  "data": {
    "text": "请帮我解释一下反向传播算法",
    "is_final": true
  }
}
```

---

## 11. 语音合成接口

### 11.1 用途

语音合成用于把文本讲解转成音频，支持：

- 错题语音讲解
- 知识点音频讲解
- 视频脚本旁白
- 小程序学习卡片音频播放

---

### 11.2 系统内部接口

```http
POST /api/ai/tts/synthesize
```

### 11.3 对接讯飞接口

```text
wss://tts-api.xfyun.cn/v2/tts
```

### 11.4 请求

```json
{
  "text": "反向传播算法的核心思想是利用链式法则，从输出层向输入层逐层计算梯度。",
  "voice": "xiaoyan",
  "speed": 50,
  "format": "mp3"
}
```

### 11.5 返回

```json
{
  "code": 0,
  "data": {
    "audio_url": "/static/generated/tts/lesson_001.mp3",
    "duration": 18.5
  }
}
```

---

## 12. 图片生成接口

### 12.1 用途

图片生成用于生成辅助型学习图片，例如：

- 知识点封面图
- 学习卡片配图
- 概念插图
- 课程海报

注意：严格学术流程图、算法图、思维导图不建议完全依赖图片生成模型。更推荐让星火大模型生成 Mermaid，再由前端渲染，以保证结构准确。

---

### 12.2 系统内部接口

```http
POST /api/ai/image/generate
```

### 12.3 对接讯飞接口

```http
POST https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti
```

### 12.4 请求

```json
{
  "prompt": "生成一张用于解释神经网络前向传播的简洁教育风格插图，包含输入层、隐藏层、输出层",
  "width": 1024,
  "height": 768,
  "style": "education"
}
```

### 12.5 返回

```json
{
  "code": 0,
  "data": {
    "image_url": "/static/generated/images/nn_forward_001.png",
    "prompt": "生成一张用于解释神经网络前向传播的简洁教育风格插图……"
  }
}
```

---

## 13. 智能 PPT 生成接口

### 13.1 用途

智能 PPT 生成适合比赛演示，能够体现系统生成多模态学习资源的能力。

应用场景：

- 根据知识点生成课程 PPT。
- 根据讲义生成复习 PPT。
- 根据学生薄弱点生成个性化补救 PPT。
- 教师端一键生成课堂辅助 PPT。

---

### 13.2 创建 PPT 任务

#### 系统内部接口

```http
POST /api/ai/ppt/create
```

#### 对接讯飞接口

```http
POST https://zwapi.xfyun.cn/api/ppt/v2/create
```

#### 请求

```json
{
  "course_id": "ai_001",
  "knowledge_point_id": "kp_bp_001",
  "query": "请生成一份面向计算机专业本科生的反向传播算法入门PPT，包含概念、公式直觉、代码示例和练习题。",
  "language": "cn",
  "is_card_note": true,
  "is_figure": true
}
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "sid": "ppt_sid_xxx",
    "title": "反向传播算法入门",
    "cover_img_src": "https://...",
    "status": "building"
  }
}
```

---

### 13.3 查询 PPT 生成进度

#### 系统内部接口

```http
GET /api/ai/ppt/progress?sid=ppt_sid_xxx
```

#### 对接讯飞接口

```http
GET https://zwapi.xfyun.cn/api/ppt/v2/progress?sid=ppt_sid_xxx
```

#### 返回

```json
{
  "code": 0,
  "data": {
    "sid": "ppt_sid_xxx",
    "status": "done",
    "ppt_url": "https://example.com/generated.pptx"
  }
}
```

---

## 14. 讯飞星辰 Agent 接口

### 14.1 用途

EduMind 当前推荐采用“自研轻量 Agent 编排器”，每个 Agent 由以下部分组成：

- Prompt 模板
- 输入 Schema
- 输出 Schema
- 工具函数
- 日志记录
- 前端 Agent 时间线展示

如果比赛答辩时想进一步强调“科大讯飞相关工具”，可以将部分 Agent 配置到讯飞星辰 Agent 开发平台中，并发布为专属 API。

---

### 14.2 推荐接入的星辰 Agent

| Agent 名称 | 是否推荐接入星辰 Agent | 说明 |
|---|---:|---|
| 课程资料摘要 Agent | 推荐 | 输入课程文档，输出知识点摘要 |
| 拍照答疑 Agent | 推荐 | 输入图片和问题，输出图文解释 |
| PPT 大纲生成 Agent | 推荐 | 输入知识点，输出 PPT 大纲 |
| 画像 Agent | 可选 | 自研更容易控制 JSON 输出 |
| 审核 Agent | 可选 | 可自研，也可结合安全护栏 API |
| 路径 Agent | 可选 | 自研更容易结合数据库掌握度 |

---

### 14.3 系统内部接口

```http
POST /api/ai/xingchen/agent/run
```

### 14.4 请求

```json
{
  "agent_id": "xc_agent_course_summary",
  "inputs": {
    "course_id": "ai_001",
    "knowledge_point": "反向传播算法",
    "student_profile": {
      "knowledge_base": "机器学习基础一般",
      "preferred_resource_types": ["图解", "代码案例"]
    }
  }
}
```

### 14.5 返回

```json
{
  "code": 0,
  "data": {
    "agent_id": "xc_agent_course_summary",
    "output": "反向传播算法是神经网络训练中的核心算法……",
    "trace": [
      {
        "step": "知识检索",
        "status": "success"
      },
      {
        "step": "摘要生成",
        "status": "success"
      }
    ]
  }
}
```

---

# 15. EduMind 后端统一接口清单

## 15.1 学生画像

```http
POST /api/profile/extract
```

### 调用链

```text
安全护栏输入审核
    ↓
星火大模型 JSON 抽取
    ↓
保存 student_profiles
    ↓
返回画像
```

### 使用讯飞 API

- 大模型安全护栏 API
- 星火认知大模型 HTTP API

---

## 15.2 学习路径生成

```http
POST /api/paths/generate
```

### 调用链

```text
读取 student_profiles
    ↓
知识库检索课程结构
    ↓
星火大模型生成路径 JSON
    ↓
保存 learning_paths / learning_tasks
```

### 使用讯飞 API

- 星火知识库 API
- 星火认知大模型 HTTP API

---

## 15.3 多智能体资源生成

```http
POST /api/generate/resource-package
```

### 请求

```json
{
  "student_id": "stu_001",
  "course_id": "ai_001",
  "knowledge_point_id": "kp_bp_001",
  "resource_types": ["lecture", "mindmap", "questions", "code_case", "video_script", "ppt"],
  "difficulty": "adaptive"
}
```

### 调用链

```text
检索 Agent
    ↓
资源规划 Agent
    ↓
文档 Agent
    ↓
题库 Agent
    ↓
代码 Agent
    ↓
多模态 Agent
    ↓
审核 Agent
```

### 使用讯飞 API

- 星火知识库 API
- 星火认知大模型 HTTP API
- 大模型安全护栏 API
- 可选：图片生成 API
- 可选：智能 PPT 生成 API
- 可选：语音合成 API

---

## 15.4 AI 辅导

```http
POST /api/tutor/chat
```

### 请求

```json
{
  "student_id": "stu_001",
  "course_id": "ai_001",
  "question": "为什么反向传播要从输出层往前算？",
  "input_type": "text",
  "need_multimodal": true
}
```

### 调用链

```text
输入审核
    ↓
RAG 检索
    ↓
星火大模型个性化解释
    ↓
输出审核
    ↓
推荐补救资源
```

### 使用讯飞 API

- 大模型安全护栏 API
- 星火知识库 API
- 星火认知大模型 HTTP API
- 可选：语音合成 API

---

## 15.5 小程序拍照问答

```http
POST /api/mobile/tutor/photo
Content-Type: multipart/form-data
```

### 调用链

```text
图片安全审核
    ↓
OCR / 图片理解
    ↓
RAG 检索
    ↓
星火大模型答疑
    ↓
输出审核
```

### 使用讯飞 API

- 大模型安全护栏 API
- 通用文档识别 OCR 大模型
- 图片理解 API
- 星火知识库 API
- 星火认知大模型 HTTP API

---

## 15.6 小程序语音问答

```http
WebSocket /api/mobile/tutor/voice
```

### 调用链

```text
语音听写
    ↓
文本输入审核
    ↓
RAG 检索
    ↓
星火大模型答疑
    ↓
输出审核
    ↓
可选语音合成
```

### 使用讯飞 API

- 语音听写流式 API
- 大模型安全护栏 API
- 星火知识库 API
- 星火认知大模型 HTTP API
- 在线语音合成 API

---

## 15.7 学习效果评估

```http
POST /api/reports/generate
```

### 调用链

```text
读取 answers / learning_events
    ↓
星火大模型分析薄弱点
    ↓
更新 student_profiles
    ↓
生成学习报告
```

### 使用讯飞 API

- 星火认知大模型 HTTP API
- 可选：星火知识库 API

---

# 16. Agent 与讯飞 API 对应关系

| EduMind Agent | 主要职责 | 主要调用 API |
|---|---|---|
| 画像 Agent | 从自然语言中抽取学生画像 | 星火大模型、安全护栏 |
| 课程解析 Agent | 解析课程资料、拆分知识点 | 星火知识库、OCR、星火大模型 |
| 检索 Agent | 从课程知识库查找相关资料 | 星火知识库 |
| 资源规划 Agent | 决定生成哪些个性化资源 | 星火大模型 |
| 文档 Agent | 生成个性化讲义和 Markdown 内容 | 星火大模型、星火知识库 |
| 题库 Agent | 生成单选、多选、判断、简答、编程题 | 星火大模型 |
| 代码 Agent | 生成代码案例和注释说明 | 星火大模型 |
| 多模态 Agent | 生成思维导图、视频脚本、语音旁白、配图、PPT | 星火大模型、语音合成、图片生成、PPT 生成 |
| 路径 Agent | 生成学习路径和每日任务 | 星火大模型、星火知识库 |
| 评估 Agent | 分析练习结果和学习行为 | 星火大模型 |
| 审核 Agent | 检查事实、引用、敏感内容、幻觉风险 | 安全护栏、星火知识库、星火大模型 |

---

# 17. 数据库表建议

## 17.1 `agent_tasks`

```sql
CREATE TABLE agent_tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(64) NOT NULL,
    student_id VARCHAR(64),
    course_id VARCHAR(64),
    agent_name VARCHAR(64) NOT NULL,
    task_type VARCHAR(64) NOT NULL,
    input_json JSON,
    output_json JSON,
    provider VARCHAR(64),
    model_name VARCHAR(64),
    status VARCHAR(32),
    error_message TEXT,
    started_at DATETIME,
    finished_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 17.2 `audit_records`

```sql
CREATE TABLE audit_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    audit_id VARCHAR(64) NOT NULL,
    student_id VARCHAR(64),
    task_id VARCHAR(64),
    content_type VARCHAR(32),
    content TEXT,
    risk_level VARCHAR(32),
    action VARCHAR(32),
    provider VARCHAR(64),
    raw_result JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 17.3 `course_kb_files`

```sql
CREATE TABLE course_kb_files (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(64) NOT NULL,
    repo_id VARCHAR(128),
    file_id VARCHAR(128),
    file_name VARCHAR(255),
    file_type VARCHAR(64),
    source_type VARCHAR(64),
    embedding_status VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

# 18. 推荐落地顺序

## 第一阶段：核心闭环

优先完成以下 API：

1. 星火认知大模型 HTTP API
2. 星火知识库 API
3. 大模型安全护栏 API

可支撑：

- 对话式学生画像
- 个性化学习路径
- 8 类资源生成
- RAG 防幻觉
- AI 辅导
- 学习报告

---

## 第二阶段：小程序多模态体验

继续完成：

1. OCR API
2. 图片理解 API
3. 语音听写 API

可支撑：

- 拍照提问
- 图片题目识别
- 语音提问
- 移动端即时答疑

---

## 第三阶段：多模态资源加分

继续完成：

1. 语音合成 API
2. 图片生成 API
3. 智能 PPT 生成 API

可支撑：

- 知识点语音讲解
- 视频脚本旁白
- 学习卡片配图
- 课程 PPT 自动生成

---

## 第四阶段：智能体平台增强

可选完成：

1. 讯飞星辰 Agent
2. 星辰工作流 API
3. Agent 专属 API 发布

可支撑：

- 答辩中强调“接入科大讯飞智能体平台”
- 将部分 Agent 独立发布为可复用工作流
- 增强项目技术亮点

---

# 19. 建议写入项目文档 / PPT 的表述

可以在“AI 工具使用说明”中加入如下表述：

> 本系统接入科大讯飞开放平台相关能力，形成 EduMind 的 AI 能力底座。其中，星火认知大模型 HTTP API 用于学生画像抽取、个性化讲义生成、题库生成、代码案例生成、学习路径规划与学习报告生成；星火知识库 API 用于课程资料上传、文档切分、向量化检索和 RAG 问答，以降低大模型幻觉；大模型安全护栏 API 用于学生输入、模型输出和多模态内容的安全审核；通用文档识别 OCR 大模型、图片理解 API、语音听写 API、语音合成 API 用于小程序端拍照提问、语音提问和多模态讲解；可选接入图片生成 API、智能 PPT 生成 API 生成多模态学习资源。系统后端统一封装上述能力，前端和小程序不直接暴露讯飞密钥。

---

# 20. 官方文档参考链接

> 实际开发前请以科大讯飞开放平台最新文档为准。

| API | 文档链接 |
|---|---|
| 星火认知大模型 HTTP API | https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html |
| 星火知识库 / ChatDoc API | https://www.xfyun.cn/doc/spark/ChatDoc-API.html |
| 大模型安全护栏 API | https://www.xfyun.cn/doc/spark/safety.html |
| 通用文档识别 OCR 大模型 | https://www.xfyun.cn/doc/words/OCRforLLM/API.html |
| 通用文字识别 API | https://www.xfyun.cn/doc/words/universal_character_recognition/API.html |
| 图片理解 API | https://www.xfyun.cn/doc/spark/ImageUnderstanding.html |
| 语音听写流式 API | https://www.xfyun.cn/doc/asr/voicedictation/API.html |
| 在线语音合成 API | https://www.xfyun.cn/doc/tts/online_tts/API.html |
| 图片生成 API | https://www.xfyun.cn/doc/spark/ImageGeneration.html |
| 智能 PPT 生成 API | https://www.xfyun.cn/doc/spark/PPTv2.html |
| 讯飞星辰 Agent 开发平台 | https://www.xfyun.cn/doc/spark/Agent01-%E5%B9%B3%E5%8F%B0%E4%BB%8B%E7%BB%8D.html |

---

# 21. 最终结论

EduMind 项目中最核心、最应该优先实现的科大讯飞 API 是：

1. 星火认知大模型 HTTP API
2. 星火知识库 / ChatDoc API
3. 大模型安全护栏 API

这三类 API 能直接支撑赛题的核心评分点：

- 对话式学习画像
- 多智能体资源生成
- 个性化学习路径规划
- RAG 防幻觉
- 智能辅导
- 学习效果评估
- 内容安全审核

小程序端和多模态加分项则建议继续接入：

1. OCR API
2. 图片理解 API
3. 语音听写 API
4. 语音合成 API
5. 图片生成 API
6. 智能 PPT 生成 API

讯飞星辰 Agent 平台不是必须项，但可以作为答辩亮点，用于证明系统不仅调用大模型，还能结合科大讯飞智能体平台进行工作流化、多工具化开发。
