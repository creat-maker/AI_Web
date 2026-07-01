from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
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
    dimension_scores = Column(Text, nullable=True)
    evidence_items = Column(Text, nullable=True)
    cognitive_state = Column(Text, nullable=True)
    profile_history = Column(Text, nullable=True)
    risk_level = Column(String(50), nullable=True)
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
    current_difficulty = Column(String(50), nullable=True)
    inserted_tasks = Column(Text, nullable=True)
    teacher_arbitration_required = Column(Boolean, default=False, nullable=False)


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
    file_path = Column(String(500), nullable=True)
    resource_url = Column(String(500), nullable=True)
    preview_type = Column(String(50), nullable=True)
    rating = Column(Float, nullable=True)
    generation_status = Column(String(50), default="generated", nullable=False)
    audit_status = Column(String(50), default="pending_review", nullable=False)


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
    run_id = Column(String(100), nullable=True)
    current_node = Column(String(100), nullable=True)
    state = Column(Text, nullable=True)
    messages = Column(Text, nullable=True)
    audit_result = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    teacher_arbitration_result = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    finished_at = Column(DateTime, nullable=True)


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


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(String(100), nullable=True)
    actor_name = Column(String(100), nullable=True)
    actor_role = Column(String(50), nullable=False, default="guest")
    action = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=False)
    target_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="success")
    detail = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    xfyun_result = Column(Text, nullable=True)
    rule_engine_result = Column(Text, nullable=True)
    risk_level = Column(String(50), nullable=True)
    arbitration_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AITaskRun(Base):
    __tablename__ = "ai_task_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    actor_id = Column(String(100), nullable=True)
    actor_role = Column(String(50), nullable=False, default="teacher")
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    confidence = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    trace_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ReviewItem(Base):
    __tablename__ = "review_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String(100), nullable=False)
    item_title = Column(String(200), nullable=False)
    source_task_id = Column(Integer, ForeignKey("ai_task_runs.id", ondelete="SET NULL"), nullable=True)
    content_json = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending_review")
    reviewer_id = Column(String(100), nullable=True)
    reviewer_name = Column(String(100), nullable=True)
    review_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String(100), nullable=False)
    item_key = Column(String(200), nullable=False)
    version_no = Column(Integer, nullable=False, default=1)
    content_json = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    is_active = Column(Boolean, nullable=False, default=False)
    source_task_id = Column(Integer, ForeignKey("ai_task_runs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
