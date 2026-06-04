import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Attachment, CourseProject
from app.schemas import AttachmentOut, ProjectCreate, ProjectDetail, ProjectOut, ProjectUpdate, ResponseModel

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("/", response_model=ResponseModel[list[ProjectOut]])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(CourseProject).order_by(CourseProject.created_at.desc()).all()
    return ResponseModel(data=[ProjectOut.model_validate(p) for p in projects])


@router.post("/", response_model=ResponseModel[ProjectOut])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = CourseProject(
        name=payload.name,
        description=payload.description,
        grade=payload.grade,
        subject=payload.subject,
        contents="{}",
    )
    db.add(project)
    db.flush()

    if payload.attachment_ids:
        valid_ids = [aid for aid in payload.attachment_ids if isinstance(aid, int)]
        if valid_ids:
            db.query(Attachment).filter(
                Attachment.id.in_(valid_ids),
                Attachment.project_id.is_(None)
            ).update({Attachment.project_id: project.id}, synchronize_session=False)

    db.commit()
    db.refresh(project)
    return ResponseModel(data=ProjectOut.model_validate(project))


@router.get("/{project_id}", response_model=ResponseModel[ProjectDetail])
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return ResponseModel(data=ProjectDetail.model_validate(project))


@router.put("/{project_id}", response_model=ResponseModel[ProjectOut])
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return ResponseModel(data=ProjectOut.model_validate(project))


@router.delete("/{project_id}", response_model=ResponseModel[dict])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(project)
    db.commit()
    return ResponseModel(data={"deleted": project_id})


@router.post("/{project_id}/attachments", response_model=ResponseModel[AttachmentOut])
def create_attachment(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    import os, uuid, aiofiles
    upload_dir = os.path.join("uploads", str(project_id))
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1] or ""
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, stored_name)

    import asyncio
    async def save_file():
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

    asyncio.run(save_file())

    file_size = os.path.getsize(file_path)
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
    return ResponseModel(data=AttachmentOut.model_validate(attachment))


@router.get("/{project_id}/summary", response_model=ResponseModel[dict])
def get_project_summary(project_id: int, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    total_size = db.query(func.sum(Attachment.file_size)).filter(Attachment.project_id == project_id).scalar() or 0
    attachment_count = db.query(func.count(Attachment.id)).filter(Attachment.project_id == project_id).scalar() or 0

    contents_map = {}
    if project.contents:
        try:
            contents_map = json.loads(project.contents) if isinstance(project.contents, str) else project.contents
        except json.JSONDecodeError:
            pass

    return ResponseModel(data={
        "project_id": project_id,
        "attachment_count": attachment_count,
        "total_size_bytes": total_size,
        "generated_types": list(contents_map.keys()),
    })
