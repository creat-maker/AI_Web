from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class CourseProject(Base):
    __tablename__ = "course_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="课程名称")
    description = Column(Text, nullable=True, comment="课程描述")
    grade = Column(String(50), nullable=True, comment="年级")
    subject = Column(String(50), nullable=True, comment="学科")
    status = Column(String(20), default="active", comment="状态")
    contents = Column(Text, nullable=True, comment="结构化生成内容(JSON)")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attachments = relationship(
        "Attachment", back_populates="project", cascade="all, delete-orphan"
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        Integer,
        ForeignKey("course_projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联课程ID",
    )
    filename = Column(String(255), nullable=False, comment="存储文件名")
    original_name = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(BigInteger, default=0, comment="文件大小(字节)")
    content_type = Column(String(100), nullable=True, comment="MIME类型")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("CourseProject", back_populates="attachments")
