from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_PAGES = [
    ("/student", ["EduMind", "id=\"app\""]),
    ("/teacher", ["EduMind", "id=\"app\""]),
    ("/dashboard", ["EduMind", "id=\"app\""]),
    ("/demo-status", ["EduMind", "id=\"app\""]),
    ("/courses", ["EduMind", "id=\"app\""]),
    ("/profiles", ["EduMind", "id=\"app\""]),
    ("/learning-path", ["EduMind", "id=\"app\""]),
    ("/resource-generation", ["EduMind", "id=\"app\""]),
    ("/tutor-chat", ["EduMind", "id=\"app\""]),
    ("/evaluation", ["EduMind", "id=\"app\""]),
    ("/reports", ["EduMind", "id=\"app\""]),
    ("/agent-workflow", ["EduMind", "id=\"app\""]),
    ("/logs", ["EduMind", "id=\"app\""]),
    ("/settings", ["EduMind", "id=\"app\""]),
]

BAD_TOKENS = ["undefined", "NaN", "[object Object]"]


@dataclass
class PageCheck:
    path: str
    ok: bool
    reason: str


def fetch(url: str, timeout: int) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": "EduMind-demo-page-check/1.0"})
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
        return int(response.status), body


def check_page(base_url: str, path: str, keywords: list[str], timeout: int) -> PageCheck:
    url = f"{base_url.rstrip('/')}{path}"
    try:
        status, html = fetch(url, timeout)
    except URLError as exc:
        return PageCheck(path, False, f"request failed: {exc.reason}")
    except TimeoutError:
        return PageCheck(path, False, "request timed out")
    except Exception as exc:  # noqa: BLE001 - CLI diagnostic should report exact failure.
        return PageCheck(path, False, f"unexpected error: {exc}")

    if status != 200:
        return PageCheck(path, False, f"HTTP {status}")

    missing = [keyword for keyword in keywords if keyword not in html]
    if missing:
        return PageCheck(path, False, f"missing keyword(s): {', '.join(missing)}")

    found_bad = [token for token in BAD_TOKENS if token in html]
    if found_bad:
        return PageCheck(path, False, f"found abnormal token(s): {', '.join(found_bad)}")

    lowered = html.lower()
    if "vite" not in lowered and "/assets/" not in lowered and "/src/main.ts" not in lowered:
        return PageCheck(path, False, "response does not look like the EduMind frontend shell")

    return PageCheck(path, True, "ok")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check EduMind demo pages from the frontend dev server.")
    parser.add_argument("--base-url", default="http://localhost:5173", help="Frontend base URL.")
    parser.add_argument("--timeout", type=int, default=8, help="HTTP timeout seconds.")
    args = parser.parse_args()

    results = [check_page(args.base_url, path, keywords, args.timeout) for path, keywords in DEFAULT_PAGES]
    print("EduMind browser-level demo page check")
    print(f"Base URL: {args.base_url}")
    for item in results:
        prefix = "PASS" if item.ok else "FAIL"
        print(f"- {prefix} {item.path}: {item.reason}")

    failed = [item for item in results if not item.ok]
    if failed:
        print("\nResult: failed")
        print("Tip: start the frontend with `cd frontend && npm run dev` and make sure the backend is available.")
        return 1

    print("\nResult: passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
