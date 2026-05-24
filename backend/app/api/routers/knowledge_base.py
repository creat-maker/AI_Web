from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import CourseDocument
from app.rag.document_loader import load_document_text
from app.rag.text_splitter import split_text
from app.rag.vector_store import vector_store
from app.services.course_service import get_course


router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.post("/upload")
async def upload_document(
    course_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    suffix = Path(file.filename or "document.txt").suffix.lower()
    if suffix not in {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".md", ".markdown"}:
        raise HTTPException(status_code=400, detail="暂不支持该文件类型")

    upload_dir = settings.path_from_root(settings.upload_dir) / str(course_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    target = upload_dir / filename
    target.write_bytes(await file.read())

    doc = CourseDocument(
        course_id=course_id,
        filename=file.filename or filename,
        file_path=str(target),
        file_type=suffix.lstrip("."),
        parse_status="parsing",
        chunk_count=0,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    text = load_document_text(str(target))
    chunks = split_text(text)
    chunk_count = vector_store.add_chunks(course_id, doc.id, doc.filename, chunks)
    doc.parse_status = "parsed"
    doc.chunk_count = chunk_count
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/documents")
def list_documents(course_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(CourseDocument)
    if course_id:
        query = query.filter(CourseDocument.course_id == course_id)
    return query.order_by(CourseDocument.id.desc()).all()


@router.get("/search")
def search(course_id: int, query: str, top_k: int = 5):
    return {"items": vector_store.search(course_id, query, top_k)}
