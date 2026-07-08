from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.lightweight_rag_service import ask_rag  # noqa: E402
from app.services.retrieval_eval_service import evaluate_retrieval, retrieval_eval_service  # noqa: E402


def search(question: str, top_k: int) -> list[dict]:
    result = ask_rag(question, course_id="python-programming", student_id="demo-basic")
    return result.get("matchedChunks", [])[:top_k]


def main() -> int:
    result = evaluate_retrieval(search, top_k=5)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    output = ROOT_DIR / "reports" / "retrieval_eval.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"written: {output}")
    md_output = ROOT_DIR / "reports" / "retrieval_eval_report.md"
    retrieval_eval_service.export_eval_summary(result, md_output)
    print(f"written: {md_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
