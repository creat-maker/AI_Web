import json
import os
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import CourseProject
from app.schemas import ResponseModel
from app.services import ExportService, load_generation_project

router = APIRouter(prefix="/export", tags=["导出功能"])


@router.get("/ppt/{project_id}")
def export_ppt(project_id: int, db: Session = Depends(get_db)):
    project = load_generation_project(db, project_id)
    contents = {}
    if project.contents:
        try:
            contents = json.loads(project.contents) if isinstance(project.contents, str) else project.contents
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="项目内容解析失败")

    ppt_data = contents.get("ppt")
    if not ppt_data:
        raise HTTPException(status_code=404, detail="该项目尚未生成 PPT，请先生成")

    try:
        output: BytesIO = ExportService.generate_pptx(ppt_data, project.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filename = f"{project.name.replace(' ', '_')}_课件.pptx"
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/doc/{project_id}")
def export_doc(project_id: int, db: Session = Depends(get_db)):
    project = load_generation_project(db, project_id)
    contents = {}
    if project.contents:
        try:
            contents = json.loads(project.contents) if isinstance(project.contents, str) else project.contents
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="项目内容解析失败")

    markdown_data = contents.get("lesson-plan", "")
    if not markdown_data:
        raise HTTPException(status_code=404, detail="该项目尚未生成教案，请先生成")

    try:
        output: BytesIO = ExportService.generate_docx(markdown_data, project.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filename = f"{project.name.replace(' ', '_')}_教案.docx"
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/package/{project_id}")
def package_project(project_id: int, db: Session = Depends(get_db)):
    import zipfile
    from datetime import datetime

    project = db.query(CourseProject).filter(CourseProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        contents = {}
        if project.contents:
            try:
                contents = json.loads(project.contents) if isinstance(project.contents, str) else project.contents
            except json.JSONDecodeError:
                pass

        if contents.get("ppt"):
            try:
                ppt_io = ExportService.generate_pptx(contents["ppt"], project.name)
                zf.writestr(f"{project.name}_课件.pptx", ppt_io.getvalue())
            except ValueError:
                pass

        if contents.get("lesson-plan"):
            try:
                doc_io = ExportService.generate_docx(contents["lesson-plan"], project.name)
                zf.writestr(f"{project.name}_教案.docx", doc_io.getvalue())
            except ValueError:
                pass

        zf.writestr("metadata.json", json.dumps({
            "project_name": project.name,
            "project_id": project.id,
            "generated_at": datetime.utcnow().isoformat(),
            "contents_types": list(contents.keys()),
        }, ensure_ascii=False, indent=2))

    zip_buffer.seek(0)
    filename = f"{project.name.replace(' ', '_')}_全套资料.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
