from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=True)
    teacher_name = Column(String(100), nullable=True)

    documents = relationship("CourseDocument", cascade="all, delete-orphan")


class CourseDocument(Base, TimestampMixin):
    __tablename__ = "course_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    parse_status = Column(String(50), default="pending", nullable=False)
    chunk_count = Column(Integer, default=0, nullable=False)


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    current_level = Column(String(100), nullable=True)
    learning_goal = Column(Text, nullable=True)
    weak_points = Column(Text, nullable=True)
    learning_preference = Column(String(100), nullable=True)
    profile_json = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningPath(Base, TimestampMixin):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_profile_id = Column(
        Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    path_json = Column(Text, nullable=False)
    adjustment_log = Column(Text, nullable=True)


class GeneratedResource(Base, TimestampMixin):
    __tablename__ = "generated_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_profile_id = Column(
        Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=True
    )
    resource_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=True)
    source_agent = Column(String(100), nullable=False)
    recommend_reason = Column(Text, nullable=True)


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_profile_id = Column(
        Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=True
    )
    quiz_json = Column(Text, nullable=False)


class QuizSubmission(Base, TimestampMixin):
    __tablename__ = "quiz_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    student_profile_id = Column(
        Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )
    answers_json = Column(Text, nullable=False)
    score = Column(Float, default=0)
    feedback_json = Column(Text, nullable=True)


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_profile_id = Column(Integer, nullable=True)
    workflow_name = Column(String(100), nullable=False)
    input_json = Column(Text, nullable=False)
    output_json = Column(Text, nullable=True)
    status = Column(String(50), default="running", nullable=False)


class TutorQuestionLog(Base, TimestampMixin):
    __tablename__ = "tutor_question_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer_json = Column(Text, nullable=False)
    contexts_json = Column(Text, nullable=False)
    mode = Column(String(50), nullable=False)


class SystemLog(Base, TimestampMixin):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    level = Column(String(20), default="INFO", nullable=False)
    module = Column(String(100), nullable=False)
    user = Column(String(100), default="demo_teacher", nullable=False)
    related_id = Column(String(100), nullable=True)
    duration_ms = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="success", nullable=False)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)


class LearningReport(Base, TimestampMixin):
    __tablename__ = "learning_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_profile_id = Column(
        Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    report_title = Column(String(200), nullable=False)
    report_path = Column(String(500), nullable=False)
    report_json = Column(Text, nullable=False)
