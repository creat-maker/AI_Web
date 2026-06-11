from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.models import Course, CourseDocument  # noqa: E402
from app.rag.document_loader import load_document_text  # noqa: E402
from app.rag.text_splitter import split_text  # noqa: E402
from app.rag.vector_store import vector_store  # noqa: E402


DATASET_DIR = ROOT_DIR / "sample_data" / "course_kb" / "python_programming"
COURSE_TITLE = "Python 程序设计：从基础语法到爬虫实践"


@dataclass(frozen=True)
class SourceDoc:
    relative_path: str
    source: str
    module: str
    license_note: str


APACHE_DOCS = [
    SourceDoc("python-tutorial-master/README.md", "python-tutorial", "课程总览", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/README.md", "python-tutorial", "Python 基础", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/01_字符串类型_str.ipynb", "python-tutorial", "字符串", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/02_列表类型_list.ipynb", "python-tutorial", "列表", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/04_字典类型_dict.ipynb", "python-tutorial", "字典", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/06_条件判断_if.ipynb", "python-tutorial", "分支结构", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/08_循环结构_loop.ipynb", "python-tutorial", "循环结构", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/09_函数和模块.ipynb", "python-tutorial", "函数和模块", "Apache-2.0"),
    SourceDoc("python-tutorial-master/01_base/10_文件和异常.ipynb", "python-tutorial", "文件和异常", "Apache-2.0"),
    SourceDoc("python-tutorial-master/02_advanced/03_高阶函数.ipynb", "python-tutorial", "高阶函数", "Apache-2.0"),
    SourceDoc("python-tutorial-master/02_advanced/07_面向对象编程.ipynb", "python-tutorial", "面向对象", "Apache-2.0"),
    SourceDoc("python-tutorial-master/05_spider/README.md", "python-tutorial", "爬虫总览", "Apache-2.0"),
    SourceDoc("python-tutorial-master/05_spider/01_爬虫介绍.ipynb", "python-tutorial", "爬虫介绍", "Apache-2.0"),
    SourceDoc("python-tutorial-master/05_spider/02_网页解析和存储.ipynb", "python-tutorial", "网页解析和存储", "Apache-2.0"),
    SourceDoc("python-tutorial-master/06_tool/logger.py", "python-tutorial", "日志工具代码案例", "Apache-2.0"),
]


PYTHON_100_DAYS_LICENSE = "已获团队授权确认，提交文档需标注来源与授权依据"


PYTHON_100_DAYS_DOCS = [
    SourceDoc("Python-100-Days-master/README.md", "Python-100-Days", "课程总览", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day01-20/03.Python语言中的变量.md", "Python-100-Days", "变量和类型", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day01-20/05.分支结构.md", "Python-100-Days", "分支结构", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day01-20/06.循环结构.md", "Python-100-Days", "循环结构", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day01-20/08.常用数据结构之列表-1.md", "Python-100-Days", "列表", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day01-20/13.常用数据结构之字典.md", "Python-100-Days", "字典", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day01-20/14.函数和模块.md", "Python-100-Days", "函数和模块", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day01-20/18.面向对象编程入门.md", "Python-100-Days", "面向对象", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day21-30/21.文件读写和异常处理.md", "Python-100-Days", "文件读写和异常", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day21-30/30.正则表达式的应用.md", "Python-100-Days", "正则表达式", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day61-65/61.网络数据采集概述.md", "Python-100-Days", "网络数据采集概述", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day61-65/62.用Python获取网络资源-1.md", "Python-100-Days", "requests 获取网络资源", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day61-65/62.用Python解析HTML页面-2.md", "Python-100-Days", "HTML 解析", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day61-65/63.并发编程在爬虫中的应用.md", "Python-100-Days", "爬虫并发", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day61-65/64.使用Selenium抓取网页动态内容.md", "Python-100-Days", "Selenium 动态页面", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/Day61-65/65.爬虫框架Scrapy简介.md", "Python-100-Days", "Scrapy 框架", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/番外篇/常见反爬策略及应对方案.md", "Python-100-Days", "反爬策略", PYTHON_100_DAYS_LICENSE),
    SourceDoc("Python-100-Days-master/番外篇/PEP8风格指南.md", "Python-100-Days", "代码风格", PYTHON_100_DAYS_LICENSE),
]


EDUMIND_CURATED_DOCS = [
    SourceDoc("edumind_curated/00_course_syllabus.md", "EduMind", "课程大纲", "EduMind original"),
    SourceDoc("edumind_curated/01_data_structures.md", "EduMind", "数据结构讲义", "EduMind original"),
    SourceDoc("edumind_curated/02_files_exceptions.md", "EduMind", "文件与异常讲义", "EduMind original"),
    SourceDoc("edumind_curated/03_web_crawler_practice.md", "EduMind", "爬虫实践讲义", "EduMind original"),
    SourceDoc("edumind_curated/04_question_bank.md", "EduMind", "课程题库", "EduMind original"),
]


def _course(db, title: str) -> Course:
    item = db.query(Course).filter(Course.title == title).first()
    if item:
        item.description = item.description or "面向软件杯演示的 Python 程序设计课程知识库，覆盖基础语法、文件异常、函数模块、面向对象和网络爬虫实践。"
        item.subject = item.subject or "计算机科学"
        item.teacher_name = item.teacher_name or "王老师"
        db.commit()
        db.refresh(item)
        return item
    item = Course(
        title=title,
        description="面向软件杯演示的 Python 程序设计课程知识库，覆盖基础语法、文件异常、函数模块、面向对象和网络爬虫实践。",
        subject="计算机科学",
        teacher_name="王老师",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _document_name(doc: SourceDoc) -> str:
    return f"Python程序设计/{doc.source}/{doc.module}/{Path(doc.relative_path).name}"


def _ensure_document(db, course: Course, doc: SourceDoc) -> tuple[CourseDocument, bool]:
    source_path = DATASET_DIR / doc.relative_path
    filename = _document_name(doc)
    item = (
        db.query(CourseDocument)
        .filter(CourseDocument.course_id == course.id, CourseDocument.filename == filename)
        .first()
    )
    created = False
    if item:
        item.file_path = str(source_path)
        item.file_type = source_path.suffix.lower().lstrip(".") or "file"
        item.parse_status = "parsing"
        item.chunk_count = 0
    else:
        item = CourseDocument(
            course_id=course.id,
            filename=filename,
            file_path=str(source_path),
            file_type=source_path.suffix.lower().lstrip(".") or "file",
            parse_status="parsing",
            chunk_count=0,
        )
        db.add(item)
        created = True
    db.commit()
    db.refresh(item)
    return item, created


def import_docs(docs: list[SourceDoc], course_title: str) -> dict[str, int]:
    Base.metadata.create_all(bind=engine)
    stats = {"created": 0, "updated": 0, "missing": 0, "failed": 0, "chunks": 0}
    db = SessionLocal()
    try:
        course = _course(db, course_title)
        for doc in docs:
            source_path = DATASET_DIR / doc.relative_path
            if not source_path.exists():
                print(f"[MISS] {doc.relative_path}")
                stats["missing"] += 1
                continue
            try:
                item, created = _ensure_document(db, course, doc)
                raw_text = load_document_text(str(source_path))
                text = (
                    f"# {doc.module}\n\n"
                    f"来源：{doc.source}\n\n"
                    f"授权标记：{doc.license_note}\n\n"
                    f"原始路径：{doc.relative_path}\n\n"
                    f"{raw_text}"
                )
                chunks = split_text(text, chunk_size=900, overlap=140)
                chunk_count = vector_store.add_chunks(course.id, item.id, item.filename, chunks)
                item.parse_status = "parsed"
                item.chunk_count = chunk_count
                db.commit()
                stats["created" if created else "updated"] += 1
                stats["chunks"] += chunk_count
                print(f"[OK] {item.filename} -> {chunk_count} chunks")
            except Exception as exc:
                db.rollback()
                stats["failed"] += 1
                print(f"[FAIL] {doc.relative_path}: {exc}")
        print(f"[COURSE] id={course.id} title={course.title}")
        return stats
    finally:
        db.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Python programming sample knowledge base into EduMind RAG.")
    parser.add_argument("--course-title", default=COURSE_TITLE)
    parser.add_argument(
        "--include-python-100-days",
        action="store_true",
        help="Also import selected Python-100-Days files after confirming authorization for competition submission.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docs = [*EDUMIND_CURATED_DOCS, *APACHE_DOCS]
    if args.include_python_100_days:
        docs.extend(PYTHON_100_DAYS_DOCS)
    stats = import_docs(docs, args.course_title)
    print(
        "[DONE] "
        f"created={stats['created']} updated={stats['updated']} "
        f"missing={stats['missing']} failed={stats['failed']} chunks={stats['chunks']}"
    )


if __name__ == "__main__":
    main()
