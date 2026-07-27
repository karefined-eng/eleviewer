#!/usr/bin/env python3
"""Validate that a v3 SEO report includes generated chart assets.

Usage:
  python validate_report_assets.py --report /path/report.md --charts-dir /path/charts

The validator checks that Markdown image links resolve and that a minimum chart set is
present. Use --allow-missing-critical only when the report explicitly documents data
limitations that prevent a critical chart from being generated.

It also checks that the report opens with the "Strategies Worth Reviewing & Replicating"
section, which must appear before the Executive Narrative.
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

STRATEGIES_HEADING_RE = re.compile(r"^#{1,3}\s+strategies worth reviewing\s*&?\s*(?:and\s+)?replicating", re.I | re.M)
EXEC_NARRATIVE_RE = re.compile(r"^#{1,3}\s+executive narrative", re.I | re.M)


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


def check_strategies_section(text: str) -> list[str]:
    """Verify the report opens with the Strategies Worth Reviewing & Replicating section."""
    issues: list[str] = []
    strategies = STRATEGIES_HEADING_RE.search(text)
    narrative = EXEC_NARRATIVE_RE.search(text)
    if not strategies:
        issues.append("Missing required opening section: 'Strategies Worth Reviewing & Replicating'.")
    elif narrative and strategies.start() > narrative.start():
        issues.append("'Strategies Worth Reviewing & Replicating' must appear BEFORE the Executive Narrative.")
    return issues


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

    for issue in check_strategies_section(text):
        errors.append(issue)

    result = {
        "report": str(report_path),
        "image_count": len(images),
        "resolved_images": resolved_names,
        "supporting_found": supporting_found,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
