import json
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Attachment, CourseProject
from app.schemas import GeneratedContentEntry, GeneratedContentOut, ResponseModel
from app.services import (
    build_generation_messages,
    call_qwen,
    extract_reference_bundle,
    get_config_value,
    load_generation_project,
    parse_generated_content,
    resolve_attachments,
    save_generated_content,
)

router = APIRouter(prefix="/generator", tags=["内容生成"])


@router.post("/compose", response_model=ResponseModel[GeneratedContentOut])
async def generator_compose(
    project_id: int,
    generator_type: str = "lesson-plan",
    user_requirement: str = "",
    attachment_ids: str = "",
    db: Session = Depends(get_db),
):
    project = load_generation_project(db, project_id)

    resolved_ids = []
    if attachment_ids:
        try:
            resolved_ids = [int(aid.strip()) for aid in attachment_ids.split(",") if aid.strip().isdigit()]
        except ValueError:
            raise HTTPException(status_code=400, detail="attachment_ids 格式错误")

    attachments = resolve_attachments(db, project_id, resolved_ids)
    bundle, source_files, readable_ids = extract_reference_bundle(attachments)

    messages = build_generation_messages(project.name, generator_type, user_requirement, bundle)

    api_key = get_config_value(db, "QWEN_API_KEY")
    reply_text = call_qwen(api_key, messages, temperature=0.8)

    content_format, content_data = parse_generated_content(generator_type, reply_text)
    entry = save_generated_content(
        project=project,
        generator_type=generator_type,
        content_format=content_format,
        content_data=content_data,
        raw_content=reply_text,
        attachment_ids=readable_ids,
        source_files=source_files,
        user_requirement=user_requirement,
    )

    return ResponseModel(data={
        "project_id": project_id,
        "generator_type": generator_type,
        "content": entry,
    })


@router.post("/generate", response_model=ResponseModel[dict])
async def generate_content(
    project_id: int,
    generator_type: str = "lesson-plan",
    requirement: str = "",
    db: Session = Depends(get_db),
):
    project = load_generation_project(db, project_id)

    attachments = db.query(Attachment).filter(
        Attachment.project_id == project_id
    ).order_by(Attachment.created_at.asc()).all()

    if not attachments:
        raise HTTPException(status_code=400, detail="当前项目还没有上传任何参考资料，请先上传 PDF、DOCX 等文档")

    bundle, source_files, readable_ids = extract_reference_bundle(attachments)
    messages = build_generation_messages(project.name, generator_type, requirement, bundle)

    api_key = get_config_value(db, "QWEN_API_KEY")
    reply_text = call_qwen(api_key, messages, temperature=0.8)

    content_format, content_data = parse_generated_content(generator_type, reply_text)
    entry = save_generated_content(
        project=project,
        generator_type=generator_type,
        content_format=content_format,
        content_data=content_data,
        raw_content=reply_text,
        attachment_ids=readable_ids,
        source_files=source_files,
        user_requirement=requirement,
    )

    return ResponseModel(data={
        "project_id": project_id,
        "generator_type": generator_type,
        "content": entry,
    })


@router.get("/{project_id}/content", response_model=ResponseModel[dict])
def get_generated_content(project_id: int, db: Session = Depends(get_db)):
    project = load_generation_project(db, project_id)
    contents = {}
    if project.contents:
        try:
            contents = json.loads(project.contents) if isinstance(project.contents, str) else project.contents
        except json.JSONDecodeError:
            pass
    return ResponseModel(data={"project_id": project_id, "contents": contents})


@router.post("/upload-material", response_model=ResponseModel[dict])
async def upload_material(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    import uuid
    upload_dir = os.path.join("uploads", str(project_id))
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1] or ""
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, stored_name)

    import aiofiles
    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    file_size = len(content)
    attachment = Attachment(
        project_id=project_id,
        filename=stored_name,
        original_name=file.filename or "unknown",
        file_path=file_path,
        file_size=file_size,
        content_type=file.content_type,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return ResponseModel(data={
        "attachment_id": attachment.id,
        "filename": attachment.filename,
        "original_name": attachment.original_name,
        "file_size": attachment.file_size,
    })
