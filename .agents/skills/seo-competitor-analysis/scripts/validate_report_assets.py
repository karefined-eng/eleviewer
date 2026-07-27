#!/usr/bin/env python3
"""Validate that a v3 SEO report includes generated chart assets and stays analytical.

Usage:
  python validate_report_assets.py --report /path/report.md --charts-dir /path/charts

The validator checks that Markdown image links resolve and that a minimum chart set is
present. Use --allow-missing-critical only when the report explicitly documents data
limitations that prevent a critical chart from being generated.

It also scans the report body for prescriptive-language patterns (recommendations,
action plans, roadmaps aimed at the target domain) and reports them as warnings.
Resolve every prescriptive-language warning before delivery.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CRITICAL_CHART_KEYWORDS = {
    "trend": ["global_organic_trend", "traffic_trend", "country_trend"],
    "page_type": ["page_type_traffic", "organic_clicks_by_landing", "landing_page_type"],
    "countries": ["top_countries", "country_trend"],
    "branded_nonbranded": ["branded_nonbranded", "brand"],
}

SUPPORTING_CHART_KEYWORDS = {
    "top_pages": ["top_landing_pages", "highest_traffic", "top_pages"],
    "losses": ["largest_page_losses", "largest_keyword_losses", "losses"],
    "backlinks": ["backlink_anchor", "backlink_destination", "anchor_mix"],
}

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

PRESCRIPTIVE_PATTERNS = [
    r"\bthe action is to\b",
    r"\b(?:should|must|needs? to)\s+(?:focus|review|improve|fix|audit|prioriti[sz]e|protect|shift|invest|consolidate|rebuild)\b",
    r"\brecovery plan\b",
    r"\b(?:7|30|60|90)[- ]day (?:plan|roadmap)\b",
    r"\broadmap\b",
    r"\bwe recommend\b|\brecommendations?\b",
    r"\bnext steps?\b",
]
PRESCRIPTIVE_RE = re.compile("|".join(PRESCRIPTIVE_PATTERNS), re.I)
CODE_BLOCK_RE = re.compile(r"```.*?```", re.S)


def extract_images(markdown: str) -> list[str]:
    return [m.group(1).split()[0].strip("<>") for m in IMAGE_RE.finditer(markdown)]


def resolve_image(report_path: Path, charts_dir: Path | None, link: str) -> Path | None:
    if link.startswith(("http://", "https://")):
        return None
    raw = Path(link)
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append((report_path.parent / raw).resolve())
        if charts_dir:
            candidates.append((charts_dir / raw.name).resolve())
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else None


def matches_any(name: str, needles: list[str]) -> bool:
    low = name.lower()
    return any(needle.lower() in low for needle in needles)


def scan_prescriptive_language(text: str) -> list[str]:
    """Return line-numbered prescriptive-language hits, skipping code blocks."""
    body = CODE_BLOCK_RE.sub("", text)
    hits: list[str] = []
    for lineno, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(">"):
            continue  # skip blockquotes (often quoted definitions or notes)
        match = PRESCRIPTIVE_RE.search(stripped)
        if match:
            snippet = stripped if len(stripped) <= 120 else stripped[:117] + "..."
            hits.append(f"line {lineno}: '{match.group(0)}' in: {snippet}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SEO report chart assets.")
    parser.add_argument("--report", required=True, help="Final Markdown report path.")
    parser.add_argument("--charts-dir", default=None, help="Directory containing generated charts.")
    parser.add_argument("--min-images", type=int, default=3, help="Minimum required image references in report. Default: 3.")
    parser.add_argument("--allow-missing-critical", action="store_true", help="Allow missing critical chart categories when limitations are explicit.")
    args = parser.parse_args()

    report_path = Path(args.report).expanduser().resolve()
    charts_dir = Path(args.charts_dir).expanduser().resolve() if args.charts_dir else None
    if not report_path.exists():
        print(f"ERROR: report not found: {report_path}")
        return 2
    text = report_path.read_text(encoding="utf-8")
    images = extract_images(text)

    errors: list[str] = []
    warnings: list[str] = []
    if len(images) < args.min_images:
        errors.append(f"Report has {len(images)} image references; expected at least {args.min_images}.")

    resolved_names = []
    for link in images:
        resolved = resolve_image(report_path, charts_dir, link)
        if resolved is None:
            warnings.append(f"Remote image not checked: {link}")
            resolved_names.append(Path(link).name)
        elif not resolved.exists():
            errors.append(f"Missing referenced image: {link} (looked for {resolved})")
        else:
            resolved_names.append(resolved.name)

    for category, needles in CRITICAL_CHART_KEYWORDS.items():
        if not any(matches_any(name, needles) for name in resolved_names):
            message = f"Missing critical chart category: {category}. Expected filename containing one of {needles}."
            if args.allow_missing_critical:
                warnings.append(message)
            else:
                errors.append(message)

    supporting_found = {category: any(matches_any(name, needles) for name in resolved_names) for category, needles in SUPPORTING_CHART_KEYWORDS.items()}
    if not any(supporting_found.values()):
        warnings.append("No supporting chart category found for top pages, losses, or backlinks. This may be acceptable only when the report states data limitations.")

    prescriptive_hits = scan_prescriptive_language(text)
    for hit in prescriptive_hits:
        warnings.append(f"Prescriptive language detected ({hit}). Competitor reports must not advise the target domain; rewrite as analysis.")

    result = {
        "report": str(report_path),
        "image_count": len(images),
        "resolved_images": resolved_names,
        "supporting_found": supporting_found,
        "prescriptive_language_hits": len(prescriptive_hits),
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
