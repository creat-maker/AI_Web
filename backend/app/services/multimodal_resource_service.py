from __future__ import annotations

import re
import shutil
import subprocess
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.xfyun_tts_service import xfyun_tts_service


RESOURCE_TYPE_CATALOG = [
    {"key": "handout", "label": "知识讲义"},
    {"key": "mindmap", "label": "知识图谱 / 思维导图"},
    {"key": "quiz", "label": "练习题"},
    {"key": "animation_html", "label": "HTML/SVG 动画"},
    {"key": "video_script", "label": "视频讲解脚本"},
    {"key": "tts_audio", "label": "语音讲解资源"},
    {"key": "video_mp4", "label": "简易 MP4 视频"},
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
        "message": (
            "检测到 FFmpeg，可合成最小 MP4 教学视频。"
            if found
            else "当前运行环境未检测到 FFmpeg；HTML 动画为当前稳定预览能力，MP4 合成为可选部署能力。"
        ),
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


def _safe_video_filename(topic: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", topic or "loop-learning").strip("-").lower()
    stem = normalized[:48] or "loop-learning"
    suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{stem}-{suffix}.mp4"


def _video_output_dir() -> Path:
    output_dir = settings.path_from_root("backend/storage/generated/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _relative_to_root(path: Path) -> str:
    try:
        return path.relative_to(settings.path_from_root(".")).as_posix()
    except ValueError:
        return path.as_posix()


def _video_response(
    *,
    status: str,
    topic: str,
    script: str,
    description: str,
    preview_supported: bool,
    file_path: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "type": "video_mp4",
        "resourceType": "video_mp4",
        "resource_type": "video_mp4",
        "status": status,
        "title": f"{topic or 'Python Loop'} 简易 MP4 视频",
        "description": description,
        "format": "mp4",
        "content": script,
        "script": script,
        "preview_supported": preview_supported,
        "fallback_resources": ["animation_html", "video_script", "tts_audio"],
    }
    if file_path:
        response["file_path"] = file_path
    if error:
        response["error"] = error
    return response


def generate_ffmpeg_video_task(topic: str, script: str, animation_html: str | None = None) -> dict[str, Any]:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        return _video_response(
            status="ffmpeg_not_available",
            topic=topic,
            script=script,
            description="当前运行环境未检测到 FFmpeg，系统已提供 HTML 动画和视频脚本，生产部署可启用 FFmpeg 合成 MP4。",
            preview_supported=False,
        )

    output_path = _video_output_dir() / _safe_video_filename(topic)
    drawtext = "text='Python Loop Learning':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=(h-text_h)/2"
    command = [
        ffmpeg_path,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x10233f:s=1280x720:d=6,drawtext={drawtext}",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(output_path),
    ]
    fallback_command = [
        ffmpeg_path,
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x10233f:s=1280x720:d=6",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(output_path),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        if result.returncode != 0:
            result = subprocess.run(fallback_command, capture_output=True, text=True, timeout=20, check=False)
        if result.returncode != 0:
            return _video_response(
                status="failed",
                topic=topic,
                script=script,
                description="FFmpeg 已检测到，但本次 MP4 合成未完成；HTML 动画和视频脚本仍可稳定使用。",
                preview_supported=False,
                error=(result.stderr or result.stdout or "ffmpeg failed")[-500:],
            )
    except Exception as exc:  # noqa: BLE001
        return _video_response(
            status="failed",
            topic=topic,
            script=script,
            description="FFmpeg 已检测到，但本次 MP4 合成未完成；HTML 动画和视频脚本仍可稳定使用。",
            preview_supported=False,
            error=str(exc),
        )

    return _video_response(
        status="generated",
        topic=topic,
        script=script,
        description="基于 FFmpeg 合成的最小教学视频示例。",
        preview_supported=True,
        file_path=_relative_to_root(output_path),
    )


def build_multimodal_resources(weak_points: list[str] | None = None) -> list[dict[str, Any]]:
    weak_points = weak_points or ["while 循环", "循环嵌套", "break / continue"]
    tts_status = xfyun_tts_service.status()
    script = "本节围绕 while 循环条件更新、break / continue 区分和循环嵌套变量追踪进行讲解。"
    tts_result = xfyun_tts_service.synthesize(script)
    animation_html = build_loop_animation_html()
    video_mp4 = generate_ffmpeg_video_task("Python Loop Learning", script, animation_html)
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
            "type": "animation_html",
            "title": "while 循环条件更新动画",
            "description": "通过逐步高亮变量变化说明 while 循环执行过程。",
            "content": animation_html,
            "preview_url": "",
            "knowledge_points": ["while 循环", "条件更新", "变量追踪"],
            "format": "html",
            "preview_supported": True,
        },
        {
            "resourceType": "video_script",
            "resource_type": "video_script",
            "type": "video_script",
            "title": "循环结构视频讲解脚本",
            "content": "先展示死循环代码，再逐行标注初始值、条件和更新语句，最后对比 break 与 continue。",
            "format": "script",
            "ffmpeg_status": ffmpeg_capability(),
        },
        {
            "resourceType": "tts_audio",
            "resource_type": "tts_audio",
            "type": "tts_audio",
            "title": "循环结构语音讲解资源",
            "content": script,
            "format": "tts-task",
            "tts_status": tts_status,
            "tts_result": tts_result,
        },
        video_mp4,
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


class MultimodalResourceService:
    def generate_animation_html(self, topic: str, knowledge_points: list[str]) -> dict:
        title = f"{topic or 'while 循环条件更新'}动画"
        return {
            "type": "animation_html",
            "resourceType": "animation_html",
            "resource_type": "animation_html",
            "title": title,
            "description": "通过逐步高亮变量变化说明 while 循环执行过程",
            "format": "html",
            "content": build_loop_animation_html(title),
            "knowledge_points": knowledge_points or ["while 循环", "条件更新", "变量追踪"],
            "preview_supported": True,
        }

    def generate_video_script(self, topic: str, knowledge_points: list[str]) -> dict:
        points = knowledge_points or ["while 循环", "break / continue", "循环嵌套"]
        return {
            "type": "video_script",
            "resourceType": "video_script",
            "resource_type": "video_script",
            "title": f"{topic or '循环结构'}视频讲解脚本",
            "description": "用于录制微课或后续接入视频生成工具的分镜脚本",
            "format": "script",
            "content": "开场说明学习目标；演示变量初始值、循环条件、循环体和变量更新；对比 break 与 continue；最后用嵌套循环案例复盘。",
            "knowledge_points": points,
            "preview_supported": True,
            "ffmpeg_status": ffmpeg_capability(),
        }

    def generate_tts_audio_task(self, text: str) -> dict:
        result = xfyun_tts_service.synthesize(text)
        return {
            "type": "tts_audio",
            "resourceType": "tts_audio",
            "resource_type": "tts_audio",
            "title": "语音讲解资源",
            "description": "语音服务未配置时，已生成讲解文本和接入任务",
            "format": "tts-task",
            "content": text,
            "tts_status": xfyun_tts_service.status(),
            "tts_result": result,
            "preview_supported": result.get("status") == "success",
        }

    def generate_ffmpeg_video_task(self, topic: str, script: str, animation_html: str | None = None) -> dict:
        return generate_ffmpeg_video_task(topic, script, animation_html)

    def generate_resource_pack(self, course: str, chapter: str, topic: str) -> dict:
        resources = build_multimodal_resources([topic or chapter or "while 循环"])
        return {
            "course": course,
            "chapter": chapter,
            "topic": topic,
            "resource_types": [item["resource_type"] for item in resources],
            "resource_type_count": len(resources),
            "resources": resources,
            "runtime_capabilities": {
                "xfyun_tts": xfyun_tts_capability(),
                "ffmpeg": ffmpeg_capability(),
            },
        }


multimodal_resource_service = MultimodalResourceService()
