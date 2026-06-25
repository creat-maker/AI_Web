from __future__ import annotations

import shutil
from html import escape
from typing import Any

from app.services.xfyun_tts_service import xfyun_tts_service


RESOURCE_TYPE_CATALOG = [
    {"key": "handout", "label": "知识讲义"},
    {"key": "mindmap", "label": "知识图谱 / 思维导图"},
    {"key": "quiz", "label": "练习题"},
    {"key": "animation_html", "label": "HTML/SVG 动画"},
    {"key": "video_script", "label": "视频讲解脚本"},
    {"key": "tts_audio", "label": "语音讲解资源"},
    {"key": "code_case", "label": "代码案例"},
    {"key": "project_task", "label": "项目任务"},
]


def xfyun_tts_capability() -> dict:
    return xfyun_tts_service.status()


def ffmpeg_capability() -> dict:
    found = shutil.which("ffmpeg")
    return {
        "enabled": bool(found),
        "status": "available" if found else "not_available",
        "path": found,
        "message": "检测到 FFmpeg，可扩展导出简易 MP4。" if found else "当前未检测到 FFmpeg，保留 HTML 动画预览和讲解脚本。",
    }


def build_loop_animation_html(title: str = "while 循环条件更新动画") -> str:
    safe_title = escape(title)
    return f"""
<section class="edumind-loop-animation" aria-label="{safe_title}">
  <style>
    .edumind-loop-animation {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      border: 1px solid #dbe3ef; border-radius: 10px; padding: 16px; background: #f8fbff; color: #1f2937;
    }}
    .edumind-loop-animation .track {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 14px; }}
    .edumind-loop-animation .step {{ border: 1px solid #c7d2fe; border-radius: 8px; padding: 10px; background: #fff; min-height: 72px; }}
    .edumind-loop-animation .dot {{ width: 18px; height: 18px; border-radius: 50%; background: #2563eb; animation: walk 5s infinite steps(5); }}
    .edumind-loop-animation code {{ background: #eef2ff; padding: 2px 5px; border-radius: 4px; }}
    @keyframes walk {{ from {{ transform: translateX(0); }} to {{ transform: translateX(480px); }} }}
  </style>
  <strong>{safe_title}</strong>
  <p>变量 <code>i</code> 从 0 开始，每轮循环先判断 <code>i &lt; 3</code>，执行循环体后更新 <code>i += 1</code>。</p>
  <div class="dot" title="当前执行位置"></div>
  <div class="track">
    <div class="step"><b>1 初始值</b><br><code>i = 0</code></div>
    <div class="step"><b>2 判断条件</b><br><code>i &lt; 3</code></div>
    <div class="step"><b>3 执行循环体</b><br><code>print(i)</code></div>
    <div class="step"><b>4 更新变量</b><br><code>i += 1</code></div>
    <div class="step"><b>5 再次判断</b><br>条件不满足时结束</div>
  </div>
</section>
""".strip()


def build_multimodal_resources(weak_points: list[str] | None = None) -> list[dict[str, Any]]:
    weak_points = weak_points or ["while 循环", "循环嵌套", "break / continue"]
    tts_status = xfyun_tts_service.status()
    script = "本节围绕 while 循环条件更新、break / continue 区分和循环嵌套变量追踪进行讲解。"
    tts_result = xfyun_tts_service.synthesize(script)
    return [
        {
            "resourceType": "handout",
            "resource_type": "handout",
            "title": "Python 循环结构知识讲义",
            "content": "梳理 for、while、range、break、continue 与循环嵌套的核心概念。",
            "format": "markdown",
        },
        {
            "resourceType": "mindmap",
            "resource_type": "mindmap",
            "title": "循环结构思维导图",
            "content": "循环结构 -> for 循环 / while 循环 / break / continue / 循环嵌套 / 变量变化表。",
            "format": "text-mindmap",
        },
        {
            "resourceType": "quiz",
            "resource_type": "quiz",
            "title": "循环结构分层练习题",
            "content": "包含基础判断、输出结果分析和代码补全题，题目绑定错因标签。",
            "format": "question-set",
        },
        {
            "resourceType": "animation_html",
            "resource_type": "animation_html",
            "title": "while 循环条件更新动画",
            "description": "通过逐步高亮变量变化说明 while 循环执行过程。",
            "content": build_loop_animation_html(),
            "preview_url": "",
            "knowledge_points": ["while 循环", "条件更新", "变量追踪"],
            "format": "html",
        },
        {
            "resourceType": "video_script",
            "resource_type": "video_script",
            "title": "循环结构视频讲解脚本",
            "content": "先展示死循环代码，再逐行标注初始值、条件和更新语句，最后对比 break 与 continue。",
            "format": "script",
            "ffmpeg_status": ffmpeg_capability(),
        },
        {
            "resourceType": "tts_audio",
            "resource_type": "tts_audio",
            "title": "循环结构语音讲解资源",
            "content": script,
            "format": "tts-task",
            "tts_status": tts_status,
            "tts_result": tts_result,
        },
        {
            "resourceType": "code_case",
            "resource_type": "code_case",
            "title": "while 循环代码实操案例",
            "content": "用猜数字、累计求和和输入校验案例练习循环条件更新。",
            "format": "python-case",
        },
        {
            "resourceType": "project_task",
            "resource_type": "project_task",
            "title": "循环结构项目任务",
            "content": "完成一个成绩列表统计小项目，要求提交代码、运行截图和变量变化说明。",
            "format": "project-brief",
        },
    ]
