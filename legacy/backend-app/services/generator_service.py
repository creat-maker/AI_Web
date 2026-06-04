import json
import re
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Attachment, CourseProject
from app.services.document_parser import extract_text_from_file


JSON_GENERATORS = {"ppt", "video", "game"}


def load_generation_project(db: Session, project_id: int) -> CourseProject:
    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="课程项目不存在")
    return project


def resolve_attachments(db: Session, project_id: int, attachment_ids: list[int]) -> list[Attachment]:
    query = db.query(Attachment).filter(Attachment.project_id == project_id)
    if attachment_ids:
        query = query.filter(Attachment.id.in_(attachment_ids))
    attachments = query.order_by(Attachment.created_at.asc()).all()
    return attachments


def extract_reference_bundle(attachments: list[Attachment]) -> tuple[str, list[str], list[int]]:
    chunks: list[str] = []
    source_files: list[str] = []
    readable_ids: list[int] = []
    unsupported_files: list[str] = []

    for attachment in attachments:
        try:
            extracted = extract_text_from_file(attachment.file_path)
        except ValueError:
            unsupported_files.append(attachment.original_name)
            continue

        if extracted.strip():
            source_files.append(attachment.original_name)
            readable_ids.append(attachment.id)
            chunks.append(f"【文件：{attachment.original_name}】\n{extracted.strip()}")

    if not chunks:
        suffix = f"；不支持的文件：{'、'.join(unsupported_files)}" if unsupported_files else ""
        raise HTTPException(status_code=400, detail=f"未能从附件中提取到可用文本，请上传 PDF、DOCX、PPTX、TXT、Markdown 或图片扫描件（PNG/JPG/WebP/TIFF）{suffix}")

    bundle = "\n\n".join(chunks)
    if len(bundle) > 18000:
        bundle = bundle[:18000] + "\n\n【文本过长，已截取前 18000 个字符用于生成】"

    return bundle, source_files, readable_ids


def _generator_instruction(generator_type: str) -> tuple[str, str]:
    if generator_type == "ppt":
        return (
            "json-object",
            (
                "你必须且只能返回一个标准的 JSON 对象，格式必须符合以下严格限制：\n"
                "{\"slides\": [\n"
                "  {\"title\": \"课程名称\", \"type\": \"cover\", \"subtitle\": \"王老师 | XX高中\"},\n"
                "  {\"title\": \"目录大纲\", \"type\": \"toc\", \"bullets\": [\"章节1\", \"章节2\"]},\n"
                "  {\"title\": \"第一章：章节名称\", \"type\": \"section\", \"subtitle\": \"章节导语一句话\"},\n"
                "  {\"title\": \"正文页标题\", \"type\": \"slide\", \"bullets\": [\"短语1\", \"短语2\", \"短语3\"]}\n"
                "}]}。\n"
                "slides 数组必须严格按照以下固定结构组织，共 8-12 页：\n"
                "第1页（封面页）：type 必须为 \"cover\"，包含 title（课程名）和 subtitle（教师信息）。\n"
                "第2页（目录页）：type 必须为 \"toc\"，title 为「目录大纲」，bullets 列出各章节标题。\n"
                "第3页（章节转场页）：type 必须为 \"section\"，title 为第一个章节标题，subtitle 为一句章节导语。\n"
                "第4页及后续正文页：type 为 \"slide\"，bullets 必须是简短短语列表，每条不超过15个字，严禁大段长句！\n"
                "可在适当位置插入更多 type=\"section\" 的章节转场页来分隔内容。\n"
                "绝对禁止输出 Markdown 语法包裹（如 ``` json）。"
            ),
        )
    if generator_type == "lesson-plan":
        return (
            "markdown",
            "如果是生成教案，必须返回带有清晰层级（##, ###）的 Markdown 文本，不要输出代码块围栏。",
        )
    if generator_type == "video":
        return (
            "json-object",
            (
                "你必须且只能返回一个标准的 JSON 对象，"
                "格式为 {\"scenes\": [{\"title\": \"镜头标题\", \"narration\": \"旁白\", \"visuals\": [\"画面元素1\", \"画面元素2\"]}]}，"
                "scenes 数组不少于 5 项，不要包含任何 Markdown 标记。"
            ),
        )
    if generator_type == "game":
        return (
            "json-object",
            (
                "你必须且只能返回一个标准的 JSON 对象，"
                "格式为 {\"cards\": [{\"front\": \"卡片正面问题\", \"back\": \"卡片背面解释\"}]}，"
                "cards 数组不少于 8 项，不要包含任何 Markdown 标记。"
            ),
        )
    if generator_type == "blog":
        return (
            "markdown",
            "请返回适合直接发布的 Markdown 博文，至少包含 ## 二级标题和 ### 三级标题，不要输出代码块围栏。",
        )
    raise HTTPException(status_code=400, detail=f"不支持的生成类型: {generator_type}")


def build_generation_messages(project_name: str, generator_type: str, user_requirement: str, reference_text: str) -> list[dict[str, str]]:
    output_format, generator_instruction = _generator_instruction(generator_type)

    effective_requirement = user_requirement.strip() if user_requirement.strip() else (
        f"请根据项目【{project_name}】的主题，发挥专业能力，自主决策并生成一份结构完整的{generator_type}初稿"
    )

    has_reference = bool(reference_text.strip())
    reference_section = (
        f"以下是老师上传的参考资料文本：\n【{reference_text}】\n\n"
        "请根据上述资料内容进行生成，内容必须忠实参考资料。"
        if has_reference else
        f"当前项目名称为【{project_name}】，无附件资料，请根据项目名称和老师要求发挥专业知识自主生成内容。"
    )

    system_prompt = (
        "你是一个具有极强自主决策能力的顶级教学专家和课程设计师。\n"
        "【铁律一】绝对禁止反问：无论用户输入多短或多模糊，你绝对不允许向用户反问、要求补充信息、说「请告诉我」。\n"
        "【铁律二】强制自主生成：如果信息不足，你必须根据项目名称和给定主题发散思维；若当前生成类型是 PPT，必须严格生成 8-12 页（固定结构：第1页封面、第2页目录、第3页章节转场、后续正文页使用短语列表，严禁大段长句），否则生成一份完整可用的高质量内容。\n"
        "【铁律三】强制结构化输出：无论用户输入多简短，你都必须直接输出符合业务格式的完整 JSON 对象（对于 PPT/游戏/视频）或 Markdown（对于教案/博客），不得输出任何商量、反问或废话。\n"
        f"{reference_section}\n"
        f"当前项目：{project_name}。"
    )
    if generator_type in JSON_GENERATORS:
        system_prompt += "\n你必须且只能返回一个标准的 JSON 对象，不要包含任何 Markdown 标记。"

    user_prompt = (
        f"老师要求：{effective_requirement}\n\n"
        f"请直接为我生成类型为 [{generator_type}] 的完整内容初稿。\n"
        f"输出格式要求：{generator_instruction}\n"
        f"求居格式为 {output_format}，绝对不得在输出中加入任何追问、序言或提示词。"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def parse_generated_content(generator_type: str, reply_text: str) -> tuple[str, Any]:
    if generator_type in JSON_GENERATORS:
        try:
            parsed = json.loads(reply_text)
            if generator_type == "ppt":
                return "json", parsed["slides"]
            if generator_type == "video":
                return "json", parsed["scenes"]
            if generator_type == "game":
                return "json", parsed["cards"]
        except (KeyError, ValueError, json.JSONDecodeError):
            if generator_type == "ppt":
                return "json", [{"title": "AI 生成结果", "bullets": [reply_text.strip()[:500] or "暂无内容"]}]
            if generator_type == "game":
                return "json", [{"front": "AI 生成结果", "back": reply_text.strip()[:500] or "暂无内容"}]
            return "json", [{"title": "AI 生成结果", "narration": reply_text.strip()[:500] or "暂无内容", "visuals": []}]

    cleaned = re.sub(r"```(?:markdown)?", "", reply_text).replace("```", "").strip()
    return "markdown", cleaned


def _load_contents_map(project: CourseProject) -> dict[str, Any]:
    if not project.contents:
        return {}
    try:
        loaded = json.loads(project.contents)
        return loaded if isinstance(loaded, dict) else {}
    except json.JSONDecodeError:
        return {}


def save_generated_content(
    project: CourseProject,
    generator_type: str,
    content_format: str,
    content_data: Any,
    raw_content: str,
    attachment_ids: list[int],
    source_files: list[str],
    user_requirement: str,
) -> dict[str, Any]:
    contents_map = _load_contents_map(project)
    entry = {
        "format": content_format,
        "data": content_data,
        "raw_content": raw_content,
        "attachment_ids": attachment_ids,
        "source_files": source_files,
        "user_requirement": user_requirement,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    contents_map[generator_type] = entry
    project.contents = json.dumps(contents_map, ensure_ascii=False)
    return entry
