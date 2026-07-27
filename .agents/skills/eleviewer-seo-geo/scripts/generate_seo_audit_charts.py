#!/usr/bin/env python3
"""Generate standard evidence-led SEO audit charts from normalized CSV inputs.

This script is intentionally data-availability based. It generates every standard
chart for which a matching CSV exists and writes a manifest showing generated,
skipped, and missing charts. It does not fabricate data.

Expected usage:
    python generate_seo_audit_charts.py --data-dir /path/to/chart_data --output-dir /path/to/output/assets

Optional:
    python generate_seo_audit_charts.py --data-dir chart_data --output-dir output/assets --manifest output/chart_manifest.md

Supported CSV files and minimum columns:
    organic_traffic_trend.csv
        period, organic_clicks_or_visits
        optional: change_pct, main_driver, keyword_driver

    top_organic_countries.csv
        country, traffic_share_pct
        optional: market_catered_to, winning_page_or_content_type, leading_keyword_or_intent

    page_type_analysis.csv
        page_type, traffic_share_pct
        optional: pages, organic_traffic_or_clicks, keyword_coverage

    branded_nonbranded.csv
        search_type, traffic_share_pct
        optional: clicks, top_keywords

    keyword_portfolio.csv
        keyword, clicks_or_traffic, brand_type
        optional: share_pct, landing_page_or_intent

    content_clusters.csv
        landing_page_cluster, clicks
        optional: number_of_pages, keywords_ranked, traffic_share_pct

    locale_analysis.csv
        locale, traffic_share_pct
        optional: pages, clicks_or_traffic, leading_page_type

    site_architecture_depth.csv
        click_depth, pages
        optional: indexable_pages, important_pages

    backlink_referring_domains.csv
        period, referring_domains
        optional: new_referring_domains, lost_referring_domains

    backlink_quality.csv
        quality_bucket, referring_domains
        optional: share_pct

    core_web_vitals.csv
        metric, value
        optional: threshold, status

All output charts use a fixed report-safe visual style so future reports remain
consistent. If input files use common alternative column names, the script will
normalize them where possible.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BRAND_NAVY = "#172554"
BRAND_BLUE = "#2563EB"
BRAND_SKY = "#38BDF8"
BRAND_GREEN = "#10B981"
BRAND_ORANGE = "#F59E0B"
BRAND_RED = "#EF4444"
BRAND_GRAY = "#64748B"
GRID = "#E2E8F0"
TEXT = "#0F172A"

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.dpi": 160,
        "savefig.dpi": 220,
        "font.family": "DejaVu Sans",
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "text.color": TEXT,
        "axes.titlesize": 14,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
    }
)


@dataclass
class ChartResult:
    name: str
    status: str
    output_file: str = ""
    reason: str = ""
    rows: int = 0


def slugify(value: str) -> str:
    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [slugify(c) for c in df.columns]
    aliases = {
        "organic_clicks": "organic_clicks_or_visits",
        "month": "period",
        "date": "period",
        "traffic_share": "traffic_share_pct",
        "share": "traffic_share_pct",
        "traffic_share_percent": "traffic_share_pct",
        "share_percent": "traffic_share_pct",
        "content_cluster": "landing_page_cluster",
        "cluster": "landing_page_cluster",
        "url_depth": "click_depth",
        "depth": "click_depth",
        "page_count": "pages",
        "count": "pages",
        "rds": "referring_domains",
        "ref_domains": "referring_domains",
        "quality": "quality_bucket",
        "brand_nonbrand": "brand_type",
        "branded_type": "brand_type",
        "keyword_clicks": "clicks_or_traffic",
    }
    df = df.rename(columns={c: aliases.get(c, c) for c in df.columns})
    return df


def read_csv(data_dir: Path, file_name: str) -> Optional[pd.DataFrame]:
    path = data_dir / file_name
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame()
    return normalize_columns(df)


def require_columns(df: pd.DataFrame, required: Sequence[str]) -> Tuple[bool, str]:
    missing = [c for c in required if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"
    if df.empty:
        return False, "CSV exists but contains no rows"
    return True, ""


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


def save_fig(output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    plt.tight_layout(pad=1.4)
    plt.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close()
    return path


def add_bar_labels(ax, values: Sequence[float], percent: bool = False) -> None:
    for patch, value in zip(ax.patches, values):
        if pd.isna(value):
            continue
        label = f"{value:.1f}%" if percent else f"{value:,.0f}"
        width = patch.get_width()
        ax.text(
            width + max(values) * 0.012 if max(values) else width,
            patch.get_y() + patch.get_height() / 2,
            label,
            va="center",
            ha="left",
            fontsize=8,
            color=BRAND_GRAY,
        )


def chart_organic_traffic_trend(df: pd.DataFrame, output_dir: Path) -> Path:
    plot_df = df.copy()
    if "organic_clicks_or_visits" not in plot_df.columns:
        for candidate in ["clicks", "visits", "traffic", "sessions"]:
            if candidate in plot_df.columns:
                plot_df = plot_df.rename(columns={candidate: "organic_clicks_or_visits"})
                break
    ok, reason = require_columns(plot_df, ["period", "organic_clicks_or_visits"])
    if not ok:
        raise ValueError(reason)
    plot_df["organic_clicks_or_visits"] = to_numeric(plot_df["organic_clicks_or_visits"])
    plot_df = plot_df.dropna(subset=["organic_clicks_or_visits"])
    if plot_df.empty:
        raise ValueError("No numeric traffic values available")
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    x = np.arange(len(plot_df))
    y = plot_df["organic_clicks_or_visits"].to_numpy()
    ax.plot(x, y, color=BRAND_BLUE, linewidth=2.6, marker="o", markersize=5)
    ax.fill_between(x, y, alpha=0.10, color=BRAND_BLUE)
    ax.set_title("Six-Month Global Organic Traffic Trend", loc="left", fontweight="bold")
    ax.set_ylabel("Organic Clicks / Visits")
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["period"].astype(str), rotation=30, ha="right")
    ax.grid(axis="y", color=GRID)
    ax.grid(axis="x", visible=False)
    ax.spines[["top", "right"]].set_visible(False)
    for i, value in enumerate(y):
        ax.annotate(f"{value:,.0f}", (i, value), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8, color=BRAND_GRAY)
    return save_fig(output_dir, "organic_traffic_trend.png")


def horizontal_bar(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    output_dir: Path,
    filename: str,
    title: str,
    xlabel: str,
    percent: bool = False,
    max_rows: int = 12,
    color: str = BRAND_BLUE,
) -> Path:
    ok, reason = require_columns(df, [label_col, value_col])
    if not ok:
        raise ValueError(reason)
    plot_df = df.copy()
    plot_df[value_col] = to_numeric(plot_df[value_col])
    plot_df = plot_df.dropna(subset=[value_col]).sort_values(value_col, ascending=False).head(max_rows)
    if plot_df.empty:
        raise ValueError(f"No numeric values available for {value_col}")
    plot_df = plot_df.iloc[::-1]
    fig_height = max(4.2, 0.42 * len(plot_df) + 1.6)
    fig, ax = plt.subplots(figsize=(8.5, fig_height))
    values = plot_df[value_col].to_numpy()
    ax.barh(plot_df[label_col].astype(str), values, color=color, alpha=0.92)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    add_bar_labels(ax, values, percent=percent)
    ax.set_xlim(0, max(values) * 1.18 if max(values) else 1)
    return save_fig(output_dir, filename)


def chart_top_organic_countries(df: pd.DataFrame, output_dir: Path) -> Path:
    return horizontal_bar(
        df,
        "country",
        "traffic_share_pct",
        output_dir,
        "top_organic_countries.png",
        "Top Organic Countries by Traffic Share",
        "Traffic Share (%)",
        percent=True,
        color=BRAND_BLUE,
    )


def chart_page_type_analysis(df: pd.DataFrame, output_dir: Path) -> Path:
    return horizontal_bar(
        df,
        "page_type",
        "traffic_share_pct",
        output_dir,
        "page_type_traffic_share.png",
        "Organic Traffic Share by Page Type",
        "Traffic Share (%)",
        percent=True,
        color=BRAND_GREEN,
    )


def chart_branded_nonbranded(df: pd.DataFrame, output_dir: Path) -> Path:
    ok, reason = require_columns(df, ["search_type", "traffic_share_pct"])
    if not ok:
        raise ValueError(reason)
    plot_df = df.copy()
    plot_df["traffic_share_pct"] = to_numeric(plot_df["traffic_share_pct"])
    plot_df = plot_df.dropna(subset=["traffic_share_pct"])
    if plot_df.empty:
        raise ValueError("No numeric branded/non-branded share values available")
    colors = [BRAND_NAVY if "brand" in str(v).lower() and "non" not in str(v).lower() else BRAND_SKY for v in plot_df["search_type"]]
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    wedges, texts, autotexts = ax.pie(
        plot_df["traffic_share_pct"],
        labels=plot_df["search_type"].astype(str),
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=90,
        counterclock=False,
        colors=colors,
        textprops={"fontsize": 10, "color": TEXT},
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Branded vs Non-Branded Organic Search Mix", loc="left", fontweight="bold")
    return save_fig(output_dir, "branded_nonbranded_mix.png")


def chart_keyword_portfolio(df: pd.DataFrame, output_dir: Path) -> Path:
    ok, reason = require_columns(df, ["keyword", "clicks_or_traffic", "brand_type"])
    if not ok:
        raise ValueError(reason)
    plot_df = df.copy()
    plot_df["clicks_or_traffic"] = to_numeric(plot_df["clicks_or_traffic"])
    grouped = plot_df.dropna(subset=["clicks_or_traffic"]).groupby("brand_type", dropna=False)["clicks_or_traffic"].sum().reset_index()
    if grouped.empty:
        raise ValueError("No numeric keyword click/traffic values available")
    colors = [BRAND_NAVY if "brand" in str(v).lower() and "non" not in str(v).lower() else BRAND_SKY for v in grouped["brand_type"]]
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    wedges, texts, autotexts = ax.pie(
        grouped["clicks_or_traffic"],
        labels=grouped["brand_type"].astype(str),
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=90,
        counterclock=False,
        colors=colors,
        textprops={"fontsize": 10, "color": TEXT},
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Keyword Portfolio: Branded vs Non-Branded Click Mix", loc="left", fontweight="bold")
    return save_fig(output_dir, "keyword_portfolio_brand_mix.png")


def chart_content_clusters(df: pd.DataFrame, output_dir: Path) -> Path:
    return horizontal_bar(
        df,
        "landing_page_cluster",
        "clicks",
        output_dir,
        "content_cluster_clicks.png",
        "Clicks by Landing-Page Content Cluster",
        "Clicks",
        percent=False,
        color=BRAND_BLUE,
    )


def chart_locale_analysis(df: pd.DataFrame, output_dir: Path) -> Path:
    return horizontal_bar(
        df,
        "locale",
        "traffic_share_pct",
        output_dir,
        "locale_traffic_share.png",
        "Organic Traffic Share by Locale",
        "Traffic Share (%)",
        percent=True,
        color=BRAND_ORANGE,
    )


def chart_site_architecture_depth(df: pd.DataFrame, output_dir: Path) -> Path:
    ok, reason = require_columns(df, ["click_depth", "pages"])
    if not ok:
        raise ValueError(reason)
    plot_df = df.copy()
    plot_df["click_depth"] = to_numeric(plot_df["click_depth"])
    plot_df["pages"] = to_numeric(plot_df["pages"])
    plot_df = plot_df.dropna(subset=["click_depth", "pages"]).sort_values("click_depth")
    if plot_df.empty:
        raise ValueError("No numeric click-depth values available")
    colors = [BRAND_RED if depth >= 4 else BRAND_BLUE for depth in plot_df["click_depth"]]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bars = ax.bar(plot_df["click_depth"].astype(int).astype(str), plot_df["pages"], color=colors, alpha=0.92)
    ax.axvline(2.5, color=BRAND_ORANGE, linestyle="--", linewidth=1.4, label="3+ clicks needs review")
    ax.set_title("Indexable Pages by Homepage Click Depth", loc="left", fontweight="bold")
    ax.set_xlabel("Click Depth from Homepage")
    ax.set_ylabel("Pages")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID)
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, plot_df["pages"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:,.0f}", ha="center", va="bottom", fontsize=8, color=BRAND_GRAY)
    ax.legend(frameon=False, loc="upper right")
    return save_fig(output_dir, "site_architecture_click_depth.png")


def chart_backlink_referring_domains(df: pd.DataFrame, output_dir: Path) -> Path:
    ok, reason = require_columns(df, ["period", "referring_domains"])
    if not ok:
        raise ValueError(reason)
    plot_df = df.copy()
    plot_df["referring_domains"] = to_numeric(plot_df["referring_domains"])
    plot_df = plot_df.dropna(subset=["referring_domains"])
    if plot_df.empty:
        raise ValueError("No numeric referring-domain values available")
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    x = np.arange(len(plot_df))
    ax.bar(x, plot_df["referring_domains"], color=BRAND_NAVY, alpha=0.88)
    ax.set_title("Referring Domains Over Time", loc="left", fontweight="bold")
    ax.set_ylabel("Referring Domains")
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["period"].astype(str), rotation=30, ha="right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID)
    ax.grid(axis="x", visible=False)
    return save_fig(output_dir, "backlink_referring_domains.png")


def chart_backlink_quality(df: pd.DataFrame, output_dir: Path) -> Path:
    return horizontal_bar(
        df,
        "quality_bucket",
        "referring_domains",
        output_dir,
        "backlink_quality_distribution.png",
        "Referring Domains by Quality Bucket",
        "Referring Domains",
        percent=False,
        color=BRAND_NAVY,
    )


def chart_core_web_vitals(df: pd.DataFrame, output_dir: Path) -> Path:
    ok, reason = require_columns(df, ["metric", "value"])
    if not ok:
        raise ValueError(reason)
    plot_df = df.copy()
    plot_df["value"] = to_numeric(plot_df["value"])
    plot_df = plot_df.dropna(subset=["value"])
    if plot_df.empty:
        raise ValueError("No numeric Core Web Vitals values available")
    status_colors = []
    for _, row in plot_df.iterrows():
        status = str(row.get("status", "")).lower()
        if "poor" in status or "fail" in status:
            status_colors.append(BRAND_RED)
        elif "need" in status or "warn" in status or "improvement" in status:
            status_colors.append(BRAND_ORANGE)
        else:
            status_colors.append(BRAND_GREEN)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    bars = ax.bar(plot_df["metric"].astype(str), plot_df["value"], color=status_colors, alpha=0.92)
    ax.set_title("Core Web Vitals Snapshot", loc="left", fontweight="bold")
    ax.set_ylabel("Metric Value")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID)
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, plot_df["value"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:g}", ha="center", va="bottom", fontsize=8, color=BRAND_GRAY)
    return save_fig(output_dir, "core_web_vitals_snapshot.png")


CHARTS: Dict[str, Tuple[str, Callable[[pd.DataFrame, Path], Path]]] = {
    "organic_traffic_trend": ("organic_traffic_trend.csv", chart_organic_traffic_trend),
    "top_organic_countries": ("top_organic_countries.csv", chart_top_organic_countries),
    "page_type_analysis": ("page_type_analysis.csv", chart_page_type_analysis),
    "branded_nonbranded": ("branded_nonbranded.csv", chart_branded_nonbranded),
    "keyword_portfolio": ("keyword_portfolio.csv", chart_keyword_portfolio),
    "content_clusters": ("content_clusters.csv", chart_content_clusters),
    "locale_analysis": ("locale_analysis.csv", chart_locale_analysis),
    "site_architecture_depth": ("site_architecture_depth.csv", chart_site_architecture_depth),
    "backlink_referring_domains": ("backlink_referring_domains.csv", chart_backlink_referring_domains),
    "backlink_quality": ("backlink_quality.csv", chart_backlink_quality),
    "core_web_vitals": ("core_web_vitals.csv", chart_core_web_vitals),
}


def write_manifest(results: List[ChartResult], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    generated = [r for r in results if r.status == "generated"]
    skipped = [r for r in results if r.status != "generated"]
    lines = ["# SEO Audit Chart Manifest", "", f"Generated charts: **{len(generated)}**", f"Skipped charts: **{len(skipped)}**", ""]
    lines.append("## Generated")
    lines.append("")
    if generated:
        lines.append("| Chart | File | Rows Used |")
        lines.append("|---|---|---:|")
        for r in generated:
            lines.append(f"| {r.name} | `{r.output_file}` | {r.rows} |")
    else:
        lines.append("No charts generated. Provide supported CSV files with the required columns.")
    lines.append("")
    lines.append("## Skipped")
    lines.append("")
    if skipped:
        lines.append("| Chart | Reason |")
        lines.append("|---|---|")
        for r in skipped:
            lines.append(f"| {r.name} | {r.reason} |")
    else:
        lines.append("No charts skipped.")
    lines.append("")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(data_dir: Path, output_dir: Path, manifest_path: Path) -> List[ChartResult]:
    results: List[ChartResult] = []
    for chart_name, (file_name, chart_func) in CHARTS.items():
        df = read_csv(data_dir, file_name)
        if df is None:
            results.append(ChartResult(chart_name, "skipped", reason=f"Missing input file: {file_name}"))
            continue
        try:
            output_file = chart_func(df, output_dir)
            results.append(ChartResult(chart_name, "generated", output_file=str(output_file), rows=len(df)))
        except Exception as exc:  # pragma: no cover - operational manifest matters more than stack trace
            plt.close("all")
            results.append(ChartResult(chart_name, "skipped", reason=str(exc), rows=len(df)))
    write_manifest(results, manifest_path)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fixed-format charts for evidence-led SEO audit reports.")
    parser.add_argument("--data-dir", required=True, help="Directory containing normalized CSV chart inputs.")
    parser.add_argument("--output-dir", required=True, help="Directory where PNG chart assets should be written.")
    parser.add_argument("--manifest", default=None, help="Optional path for Markdown chart manifest.")
    parser.add_argument("--json", default=None, help="Optional path for JSON chart manifest.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else output_dir.parent / "chart_manifest.md"

    if not data_dir.exists():
        raise SystemExit(f"Data directory does not exist: {data_dir}")

    results = run(data_dir, output_dir, manifest_path)
    if args.json:
        json_path = Path(args.json).expanduser().resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps([r.__dict__ for r in results], indent=2), encoding="utf-8")

    generated_count = sum(1 for r in results if r.status == "generated")
    skipped_count = len(results) - generated_count
    print(f"Generated {generated_count} charts. Skipped {skipped_count}. Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
