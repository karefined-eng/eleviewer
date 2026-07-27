#!/usr/bin/env python3
"""Validate Executive Summary paragraph count, word range, and bold opening headline.

Supports both English and Chinese reports.

Usage:
  python validate_exec_summary.py /path/to/report.md
  python validate_exec_summary.py /path/to/report.md --paragraphs 1
  python validate_exec_summary.py /path/to/report.md --min-words 150 --max-words 200
  python validate_exec_summary.py /path/to/report.md --min-words 250 --max-words 350 --lang zh
  python validate_exec_summary.py /path/to/report.md --target-words 180 --tolerance 30

Notes:
  - The heading matcher accepts both "Executive Summary" and the Chinese "执行摘要".
  - --lang zh counts CJK characters; --lang en counts English words;
    --lang auto (default) picks the counting mode from the summary content.
  - When CJK counting applies, default bounds become 250-350 characters
    (roughly equal to 150-200 English words).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(
    r"^##\s+\d*\.?\s*(Executive Summary|执行摘要(（Executive Summary）|\(Executive Summary\))?)\s*$",
    re.I | re.M,
)
NEXT_HEADING_RE = re.compile(r"^##\s+", re.M)
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def clean_text(text: str) -> str:
    clean = re.sub(r"[*_`#>\[\]()]", " ", text)
    clean = re.sub(r"https?://\S+", " ", clean)
    return clean


def english_word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’%.,-]+\b", clean_text(text)))


def chinese_char_count(text: str) -> int:
    return len(CJK_RE.findall(clean_text(text)))


def count_units(text: str, lang: str) -> tuple[int, str]:
    if lang == "zh":
        return chinese_char_count(text), "CJK characters"
    if lang == "en":
        return english_word_count(text), "words"
    cjk = chinese_char_count(text)
    total_alpha = english_word_count(text)
    if cjk > total_alpha:
        return cjk, "CJK characters"
    return total_alpha, "words"


def extract_summary(markdown: str) -> str:
    match = HEADING_RE.search(markdown)
    if not match:
        raise ValueError("Could not find a level-2 heading named 'Executive Summary' or '执行摘要'.")
    start = match.end()
    next_match = NEXT_HEADING_RE.search(markdown, start)
    end = next_match.start() if next_match else len(markdown)
    return markdown[start:end].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", help="Path to Markdown report")
    parser.add_argument("--paragraphs", type=int, default=1, help="Expected Executive Summary paragraph count")
    parser.add_argument("--min-words", type=int, default=None, help="Minimum units per paragraph; defaults to 150 (en) or 250 (zh)")
    parser.add_argument("--max-words", type=int, default=None, help="Maximum units per paragraph; defaults to 200 (en) or 350 (zh)")
    parser.add_argument("--target-words", type=int, default=None, help="Optional expected units per paragraph; overrides min/max when set")
    parser.add_argument("--tolerance", type=int, default=0, help="Allowed +/- tolerance when --target-words is set")
    parser.add_argument("--lang", choices=["auto", "zh", "en"], default="auto", help="Counting language; defaults to auto-detect")
    args = parser.parse_args()

    path = Path(args.report)
    text = path.read_text(encoding="utf-8")
    summary = extract_summary(text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", summary) if p.strip()]

    ok = True
    if len(paragraphs) != args.paragraphs:
        print(f"FAIL: Executive Summary has {len(paragraphs)} paragraphs; expected {args.paragraphs}.")
        ok = False
    else:
        print(f"PASS: Executive Summary has exactly {args.paragraphs} paragraph(s).")

    for idx, paragraph in enumerate(paragraphs, 1):
        count, unit = count_units(paragraph, args.lang)
        is_zh = unit == "CJK characters"
        default_min = 250 if is_zh else 150
        default_max = 350 if is_zh else 200
        if args.target_words is not None:
            lower = args.target_words - args.tolerance
            upper = args.target_words + args.tolerance
            label = f"expected {args.target_words} +/- {args.tolerance}"
        else:
            lower = args.min_words if args.min_words is not None else default_min
            upper = args.max_words if args.max_words is not None else default_max
            label = f"expected {lower}-{upper}"
        status = "PASS" if lower <= count <= upper else "FAIL"
        print(f"{status}: Paragraph {idx} has {count} {unit}; {label}.")
        if status == "FAIL":
            ok = False

    if paragraphs:
        first = paragraphs[0]
        if not first.startswith("**"):
            print("FAIL: Paragraph 1 should start with a bold audit headline.")
            ok = False
        else:
            print("PASS: Paragraph 1 starts with a bold audit headline.")

    forbidden = [
        "## 2. Scope and Data Used",
        "## Scope and Data Used",
        "## Robots, Indexation, and Canonical Control",
        "## Structured Data",
        "## 范围与所用数据",
        "## 2. 范围与所用数据",
        "## Robots、收录与 Canonical 控制",
        "## 结构化数据",
    ]
    for heading in forbidden:
        if heading.lower() in text.lower():
            print(f"FAIL: Forbidden standalone section found: {heading}")
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
