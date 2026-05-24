import csv
import json
import os
import re
import uuid
import zipfile
from pathlib import Path
from typing import Any, Literal
from xml.etree import ElementTree

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import ResponseModel
from app.services import call_qwen, get_config_value
from app.services.document_parser import extract_text_from_file

router = APIRouter(prefix="/exam-analysis", tags=["学情分析"])

AnalysisMode = Literal["auto", "score_sheet", "answer_card", "free_paper"]


def _normalize_percent(value: float) -> str:
    return f"{value:.1f}%"


def _detect_mode(filename: str, requested_mode: AnalysisMode) -> str:
    if requested_mode != "auto":
        return requested_mode
    suffix = Path(filename).suffix.lower()
    if suffix in {".csv", ".tsv", ".txt", ".xlsx"}:
        return "score_sheet"
    if any(keyword in filename for keyword in ["答题卡", "答题卷", "涂卡", "答题纸"]):
        return "answer_card"
    return "free_paper"


def _split_table_line(line: str) -> list[str]:
    if "\t" in line:
        return [cell.strip() for cell in line.split("\t")]
    return [cell.strip() for cell in next(csv.reader([line]))]


def _read_text_table(file_path: str) -> tuple[list[str], list[list[str]]]:
    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return [], []
    return _split_table_line(lines[0]), [_split_table_line(line) for line in lines[1:]]


def _xlsx_column_index(cell_ref: str) -> int:
    letters = re.sub(r"[^A-Z]", "", cell_ref.upper())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return max(index - 1, 0)


def _read_xlsx_table(file_path: str) -> tuple[list[str], list[list[str]]]:
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    with zipfile.ZipFile(file_path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("main:si", ns):
                texts = [node.text or "" for node in item.findall(".//main:t", ns)]
                shared_strings.append("".join(texts))

        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        first_sheet = workbook.find(".//main:sheets/main:sheet", ns)
        if first_sheet is None:
            return [], []
        rel_id = first_sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")

        rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = None
        for rel in rels:
            if rel.attrib.get("Id") == rel_id:
                target = rel.attrib.get("Target")
                break
        if not target:
            return [], []

        sheet_path = f"xl/{target.lstrip('/')}"
        sheet = ElementTree.fromstring(archive.read(sheet_path))
        rows: list[list[str]] = []
        for row in sheet.findall(".//main:sheetData/main:row", ns):
            values: list[str] = []
            for cell in row.findall("main:c", ns):
                ref = cell.attrib.get("r", "")
                index = _xlsx_column_index(ref)
                while len(values) <= index:
                    values.append("")
                raw_value = cell.findtext("main:v", default="", namespaces=ns)
                if cell.attrib.get("t") == "s" and raw_value.isdigit():
                    value = shared_strings[int(raw_value)] if int(raw_value) < len(shared_strings) else ""
                else:
                    value = raw_value
                values[index] = value.strip()
            if any(values):
                rows.append(values)
        if len(rows) < 2:
            return [], []
        return rows[0], rows[1:]


def _is_wrong_answer(value: str) -> bool:
    return value.strip().lower() in {"0", "错", "错误", "x", "×", "false", "f", "no", "n", "未得分"}


def _is_correct_answer(value: str) -> bool:
    return value.strip().lower() in {"1", "对", "正确", "√", "true", "t", "yes", "y", "得分"}


def _score_distribution(scores: list[float]) -> list[dict[str, Any]]:
    ranges = [
        ("90-100分", lambda score: score >= 90),
        ("80-89分", lambda score: 80 <= score < 90),
        ("70-79分", lambda score: 70 <= score < 80),
        ("60-69分", lambda score: 60 <= score < 70),
        ("不及格", lambda score: score < 60),
    ]
    counts = [sum(1 for score in scores if test(score)) for _, test in ranges]
    max_count = max(max(counts), 1)
    return [
        {"range": label, "count": count, "percent": round(count / max_count * 100)}
        for (label, _), count in zip(ranges, counts)
    ]


def _analyze_score_sheet(file_path: str, filename: str) -> dict[str, Any]:
    suffix = Path(filename).suffix.lower()
    headers, rows = _read_xlsx_table(file_path) if suffix == ".xlsx" else _read_text_table(file_path)
    if not headers or not rows:
        raise ValueError("成绩单至少需要包含表头和一行学生数据")

    name_index = next((i for i, h in enumerate(headers) if re.search(r"姓名|学生|name", h, re.I)), 0)
    score_index = next((i for i, h in enumerate(headers) if re.search(r"总分|得分|成绩|score", h, re.I)), -1)
    if score_index < 0:
        raise ValueError("未找到总分/成绩列，请确认表头包含“总分、得分、成绩或 score”")

    scores: list[float] = []
    normalized_rows: list[list[str]] = []
    for row in rows:
        if score_index >= len(row):
            continue
        try:
            score = float(row[score_index])
        except ValueError:
            continue
        scores.append(score)
        normalized_rows.append(row)
    if not scores:
        raise ValueError("成绩单中未识别到有效分数")

    average_score = round(sum(scores) / len(scores), 1)
    pass_rate = _normalize_percent(sum(1 for score in scores if score >= 60) / len(scores) * 100)
    excellent_rate = _normalize_percent(sum(1 for score in scores if score >= 90) / len(scores) * 100)
    highest_score = max(scores)
    highest_scorers = "、".join(
        row[name_index] if name_index < len(row) and row[name_index] else f"学生{index + 1}"
        for index, row in enumerate(normalized_rows)
        if score_index < len(row) and float(row[score_index]) == highest_score
    )

    question_columns = [
        (index, header)
        for index, header in enumerate(headers)
        if index not in {name_index, score_index} and re.search(r"题|q\d+|question", header, re.I)
    ]
    top_errors: list[dict[str, Any]] = []
    for index, header in question_columns:
        wrong_students: list[str] = []
        for row_index, row in enumerate(normalized_rows):
            value = row[index] if index < len(row) else ""
            numeric_zero = False
            try:
                numeric_zero = float(value) == 0
            except ValueError:
                numeric_zero = False
            if _is_wrong_answer(value) or (not _is_correct_answer(value) and numeric_zero):
                wrong_students.append(row[name_index] if name_index < len(row) and row[name_index] else f"学生{row_index + 1}")
        if not wrong_students:
            continue
        error_rate = len(wrong_students) / len(normalized_rows) * 100
        top_errors.append({
            "question": header,
            "topic": f"{header} 对应知识点需复盘",
            "errorRate": _normalize_percent(error_rate),
            "affectedStudents": wrong_students[:8],
            "suggestion": "建议列入下节课讲评，并推送同类变式题。" if error_rate >= 30 else "可作为课后订正检查项。",
        })
    top_errors.sort(key=lambda item: float(item["errorRate"].rstrip("%")), reverse=True)

    if not top_errors:
        top_errors = [{
            "question": "综合表现",
            "topic": "成绩单未提供逐题得分，暂按总分分层诊断",
            "errorRate": _normalize_percent(sum(1 for score in scores if score < 60) / len(scores) * 100),
            "affectedStudents": [],
            "suggestion": "建议补充逐题得分列，以生成更精确的错因分析。",
        }]

    colors = ["rose", "amber", "indigo", "emerald"]
    mastery = [
        {
            "name": item["topic"],
            "percent": max(0, min(100, round(100 - float(item["errorRate"].rstrip("%"))))),
            "color": colors[index] if index < len(colors) else "indigo",
        }
        for index, item in enumerate(top_errors[:4])
    ]

    return {
        "reportTitle": f"{Path(filename).stem} 学情分析报告",
        "sampleSize": len(scores),
        "submittedCount": len(scores),
        "questionCount": len(question_columns) or 1,
        "averageScore": average_score,
        "passRate": pass_rate,
        "excellentRate": excellent_rate,
        "highestScore": highest_score,
        "highestScorers": highest_scorers,
        "lowScoreCount": sum(1 for score in scores if score < 60),
        "scoreDistribution": _score_distribution(scores),
        "knowledgeMastery": mastery,
        "topErrors": top_errors[:5],
        "aiSuggestion": f"已从成绩单识别 {len(scores)} 名学生，平均分 {average_score}，及格率 {pass_rate}，优秀率 {excellent_rate}。建议优先处理错误率最高的 {top_errors[0]['question']}，并对低分学生安排基础巩固。",
        "remediationPlan": [
            "先讲评错误率最高的 2 道题，要求学生标注错因。",
            "对低于 60 分学生推送基础概念和例题仿练。",
            "对 90 分以上学生推送综合应用题，保持拔高训练。",
        ],
    }


def _build_ai_prompt(mode: str, filename: str, extracted_text: str, answer_key: str | None) -> str:
    mode_name = "标准答题卡" if mode == "answer_card" else "原卷/作业"
    review_rule = (
        "标准答题卡模式下，请重点识别学生信息、选择题作答、主观题区域和疑似低置信度项。"
        if mode == "answer_card"
        else "原卷/作业模式下，请先根据题号切分题目，区分印刷题干和学生作答，并标出需要老师复核的题目。"
    )
    return "\n".join([
        f"请基于{mode_name}文件「{filename}」生成班级学情分析 JSON。",
        review_rule,
        f"标准答案或评分细则：{answer_key or '未提供，请基于文本内容进行保守诊断，并提醒老师补充标准答案。'}",
        "必须返回 JSON，字段包含 reportTitle、sampleSize、submittedCount、questionCount、averageScore、passRate、excellentRate、highestScore、highestScorers、lowScoreCount、scoreDistribution、knowledgeMastery、topErrors、aiSuggestion、remediationPlan、reviewItems。",
        "reviewItems 每项包含 question、reason、confidence、suggestion。",
        "以下是 OCR/文档解析文本：",
        extracted_text[:12000] or "未提取到有效文本，请给出保守的待复核分析。",
    ])


def _normalize_ai_result(raw: str, filename: str, mode: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    match = re.search(r"\{[\s\S]*\}", raw)
    parsed: dict[str, Any] = {}
    if match:
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            parsed = {}

    review_items = parsed.get("reviewItems") if isinstance(parsed.get("reviewItems"), list) else []
    result = {
        "reportTitle": str(parsed.get("reportTitle") or f"{Path(filename).stem} 学情分析报告"),
        "sampleSize": int(parsed.get("sampleSize") or 1),
        "submittedCount": int(parsed.get("submittedCount") or 1),
        "questionCount": int(parsed.get("questionCount") or 1),
        "averageScore": float(parsed.get("averageScore") or 0),
        "passRate": str(parsed.get("passRate") or "0.0%"),
        "excellentRate": str(parsed.get("excellentRate") or "0.0%"),
        "highestScore": float(parsed.get("highestScore") or 0),
        "highestScorers": str(parsed.get("highestScorers") or "待复核"),
        "lowScoreCount": int(parsed.get("lowScoreCount") or 0),
        "scoreDistribution": parsed.get("scoreDistribution") if isinstance(parsed.get("scoreDistribution"), list) else _score_distribution([0]),
        "knowledgeMastery": parsed.get("knowledgeMastery") if isinstance(parsed.get("knowledgeMastery"), list) else [
            {"name": "待确认知识点", "percent": 0, "color": "rose"}
        ],
        "topErrors": parsed.get("topErrors") if isinstance(parsed.get("topErrors"), list) else [
            {
                "question": "待复核题目",
                "topic": "OCR 结果置信度不足",
                "errorRate": "0.0%",
                "affectedStudents": [],
                "suggestion": "请老师确认题目切分、标准答案和学生作答后再生成最终报告。",
            }
        ],
        "aiSuggestion": str(parsed.get("aiSuggestion") or raw[:500] or "当前材料需要人工复核后生成精确学情分析。"),
        "remediationPlan": parsed.get("remediationPlan") if isinstance(parsed.get("remediationPlan"), list) else [
            "确认题目切分与标准答案。",
            "复核 OCR 低置信度答案。",
            "复核完成后重新生成正式学情报告。",
        ],
    }

    if not review_items and mode in {"answer_card", "free_paper"}:
        review_items = [{
            "question": "整卷",
            "reason": "非成绩单材料需要老师确认题目切分、答案区域和评分细则",
            "confidence": 0.72 if mode == "answer_card" else 0.58,
            "suggestion": "进入复核页确认后再批量发布成绩。",
        }]
    return result, review_items


@router.post("/analyze", response_model=ResponseModel[dict])
async def analyze_exam_material(
    mode: AnalysisMode = Form("auto"),
    answer_key: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename or "unknown"
    resolved_mode = _detect_mode(filename, mode)
    upload_dir = Path("uploads") / "exam_analysis" / uuid.uuid4().hex
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename
    content = await file.read()
    file_path.write_bytes(content)

    try:
        if resolved_mode == "score_sheet":
            result = _analyze_score_sheet(str(file_path), filename)
            return ResponseModel(data={
                "mode": resolved_mode,
                "status": "completed",
                "result": result,
                "reviewItems": [],
            })

        extracted_text = extract_text_from_file(str(file_path))
        api_key = get_config_value(db, "QWEN_API_KEY")
        prompt = _build_ai_prompt(resolved_mode, filename, extracted_text, answer_key)
        raw = call_qwen(
            api_key,
            [
                {"role": "system", "content": "你是严谨的阅卷与学情分析助手，只返回合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        result, review_items = _normalize_ai_result(raw, filename, resolved_mode)
        return ResponseModel(data={
            "mode": resolved_mode,
            "status": "needs_review" if review_items else "completed",
            "result": result,
            "reviewItems": review_items,
            "extractedTextPreview": extracted_text[:500],
        })
    except Exception as exc:
        return ResponseModel(
            code=422,
            message=str(exc),
            data={
                "mode": resolved_mode,
                "status": "failed",
                "result": None,
                "reviewItems": [{
                    "question": "文件处理",
                    "reason": str(exc),
                    "confidence": 0,
                    "suggestion": "请检查文件格式，或切换为成绩单模式上传 CSV/Excel。",
                }],
            },
        )
