import os
import uuid
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Attachment, CourseProject
from app.schemas import ResponseModel, StagedAttachmentOut

router = APIRouter(prefix="/attachments", tags=["附件管理"])


@router.post("/upload", response_model=ResponseModel[StagedAttachmentOut])
async def upload_staged_attachment(
    file: UploadFile = File(...),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    upload_dir = os.path.join("uploads", "staged", uuid.uuid4().hex)
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1] or ""
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, stored_name)

    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    file_size = len(content)
    temp_id = f"staged_{uuid.uuid4().hex[:12]}"

    if project_id:
        project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
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
            "temp_id": temp_id,
            "original_name": file.filename or "unknown",
            "file_size": file_size,
            "content_type": file.content_type,
        })

    return ResponseModel(data={
        "temp_id": temp_id,
        "original_name": file.filename or "unknown",
        "file_size": file_size,
        "content_type": file.content_type,
    })


@router.delete("/{attachment_id}", response_model=ResponseModel[dict])
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")

    try:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
    except OSError:
        pass

    db.delete(attachment)
    db.commit()
    return ResponseModel(data={"deleted": attachment_id})
