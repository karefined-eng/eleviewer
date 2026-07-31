#!/usr/bin/env python3
"""Generate standard SEO report charts from normalized CSV files.

Usage:
  python generate_seo_charts.py --project-dir /path/to/project --output-dir /path/to/project/charts --title "example.com"

The script is intentionally tolerant of missing datasets. It generates every chart that
can be supported by available normalized CSV files and writes a manifest documenting
created charts and missing inputs.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Iterable, Optional

import matplotlib.pyplot as plt
import pandas as pd


CSV_CANDIDATES = {
    "traffic_trend": ["traffic_trend.csv", "organic_traffic_trend.csv", "similarweb_total_visits_6m.csv", "semrush_traffic_trend.csv"],
    "country_trend": ["country_trend.csv", "semrush_country_history.csv", "country_history.csv"],
    "country_traffic": ["country_traffic.csv", "top_countries.csv", "semrush_top20_countries.csv"],
    "page_type_summary": ["page_type_summary.csv", "landing_page_clusters.csv", "cluster_summary.csv"],
    "top_pages": ["top_pages.csv", "top_pages_sample.csv", "landing_pages.csv"],
    "branded_nonbranded": ["branded_nonbranded.csv", "keyword_brand_summary.csv", "keyword_intent.csv"],
    "keyword_sample": ["keyword_sample.csv", "top_300_keywords.csv", "organic_keywords.csv"],
    "page_losses": ["page_losses.csv", "six_month_page_losses.csv", "largest_page_losses.csv"],
    "keyword_losses": ["keyword_losses.csv", "six_month_keyword_losses.csv", "largest_keyword_losses.csv"],
    "anchor_mix": ["backlink_anchor_mix.csv", "anchor_mix.csv"],
    "destination_mix": ["backlink_destination_mix.csv", "backlink_page_type_mix.csv", "destination_page_type_mix.csv"],
}

VALUE_COLUMNS = ["organic_traffic", "organic_visits", "traffic", "clicks", "estimated_clicks", "visits", "value", "count", "rows"]
DATE_COLUMNS = ["date", "month", "period"]
PALETTE = ["#2563eb", "#f97316", "#16a34a", "#9333ea", "#dc2626", "#0891b2", "#ca8a04", "#4f46e5"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]
    return df


def find_csv(project_dir: Path, key: str) -> Optional[Path]:
    for name in CSV_CANDIDATES[key]:
        direct = project_dir / name
        if direct.exists():
            return direct
        matches = sorted(project_dir.rglob(name))
        if matches:
            return matches[0]
    return None


def read_csv(project_dir: Path, key: str) -> tuple[Optional[pd.DataFrame], Optional[Path], Optional[str]]:
    path = find_csv(project_dir, key)
    if not path:
        return None, None, f"Missing {key}: expected one of {CSV_CANDIDATES[key]}"
    try:
        df = normalize_columns(pd.read_csv(path))
    except Exception as exc:  # pragma: no cover - defensive for mixed exports
        return None, path, f"Could not read {path.name}: {exc}"
    if df.empty:
        return None, path, f"{path.name} is empty"
    return df, path, None


def first_col(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False), errors="coerce")


def clean_label(value: object, max_len: int = 42) -> str:
    text = str(value).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def style_plot(title: str, ylabel: str = "", xlabel: str = "") -> None:
    plt.title(title, fontsize=15, weight="bold", pad=16)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()


def save(fig_path: Path) -> str:
    plt.savefig(fig_path, dpi=180, bbox_inches="tight")
    plt.close()
    return fig_path.name


def plot_traffic_trend(df: pd.DataFrame, out: Path, title: str) -> Optional[str]:
    date_col = first_col(df, DATE_COLUMNS)
    value_col = first_col(df, ["organic_search_visits", "organic_visits", "organic_traffic", "traffic", "visits"])
    paid_col = first_col(df, ["paid_search_visits", "paid_visits", "paid_traffic"])
    if not date_col or not value_col:
        return None
    chart = df[[date_col, value_col] + ([paid_col] if paid_col else [])].dropna(subset=[date_col]).copy()
    chart[value_col] = coerce_numeric(chart[value_col])
    if paid_col:
        chart[paid_col] = coerce_numeric(chart[paid_col])
    chart = chart.dropna(subset=[value_col])
    if chart.empty:
        return None
    plt.figure(figsize=(10.5, 5.8))
    plt.plot(chart[date_col].astype(str), chart[value_col], marker="o", linewidth=2.6, color=PALETTE[0], label="Organic search")
    if paid_col and chart[paid_col].notna().any():
        plt.plot(chart[date_col].astype(str), chart[paid_col], marker="o", linewidth=2.2, color=PALETTE[1], label="Paid search")
        plt.legend(frameon=False)
    plt.xticks(rotation=35, ha="right")
    style_plot(f"{title}: Estimated Organic Search Trend", "Estimated visits / traffic")
    return save(out / "global_organic_trend.png")


def plot_country_traffic(df: pd.DataFrame, out: Path, title: str) -> Optional[str]:
    country_col = first_col(df, ["country", "location", "market"])
    value_col = first_col(df, ["six_month_organic_traffic_sum", "organic_traffic", "traffic", "visits", "clicks"])
    if not country_col or not value_col:
        return None
    chart = df[[country_col, value_col]].copy()
    chart[value_col] = coerce_numeric(chart[value_col])
    chart = chart.dropna().sort_values(value_col, ascending=False).head(10)
    if chart.empty:
        return None
    plt.figure(figsize=(10.5, 6.2))
    plt.barh(chart[country_col].map(clean_label), chart[value_col], color=PALETTE[0])
    plt.gca().invert_yaxis()
    style_plot(f"{title}: Top Organic Search Countries", "", "Estimated organic traffic")
    return save(out / "top_countries_bar.png")


def plot_country_trend(df: pd.DataFrame, out: Path, title: str) -> Optional[str]:
    date_col = first_col(df, DATE_COLUMNS)
    country_col = first_col(df, ["country", "location", "market"])
    value_col = first_col(df, ["organic_traffic", "traffic", "visits", "clicks"])
    if not date_col or not country_col or not value_col:
        return None
    chart = df[[date_col, country_col, value_col]].copy()
    chart[value_col] = coerce_numeric(chart[value_col])
    chart = chart.dropna(subset=[date_col, country_col, value_col])
    if chart.empty:
        return None
    top = chart.groupby(country_col)[value_col].sum().sort_values(ascending=False).head(5).index
    chart = chart[chart[country_col].isin(top)]
    plt.figure(figsize=(11, 6.2))
    for i, (country, group) in enumerate(chart.groupby(country_col)):
        plt.plot(group[date_col].astype(str), group[value_col], marker="o", linewidth=2.2, label=str(country), color=PALETTE[i % len(PALETTE)])
    plt.xticks(rotation=35, ha="right")
    plt.legend(frameon=False)
    style_plot(f"{title}: Organic Traffic by Country Trend", "Estimated organic traffic")
    return save(out / "country_trend.png")


def plot_page_type(df: pd.DataFrame, out: Path, title: str) -> Optional[str]:
    type_col = first_col(df, ["page_type", "cluster", "organic_landing_page_cluster", "category"])
    value_col = first_col(df, ["estimated_clicks", "clicks", "organic_traffic", "traffic", "visits"])
    if not type_col or not value_col:
        return None
    chart = df[[type_col, value_col]].copy()
    chart[value_col] = coerce_numeric(chart[value_col])
    chart = chart.dropna().sort_values(value_col, ascending=True).tail(10)
    if chart.empty:
        return None
    plt.figure(figsize=(11, 6.4))
    plt.barh(chart[type_col].map(clean_label), chart[value_col], color=PALETTE[1])
    style_plot(f"{title}: Organic Clicks by Landing-Page Type", "", "Estimated organic clicks / traffic")
    return save(out / "page_type_traffic_bar.png")


def plot_top_pages(df: pd.DataFrame, out: Path, title: str) -> Optional[str]:
    page_col = first_col(df, ["landing_page", "url", "page", "target_url"])
    value_col = first_col(df, ["estimated_clicks", "clicks", "organic_traffic", "traffic", "visits"])
    if not page_col or not value_col:
        return None
    chart = df[[page_col, value_col]].copy()
    chart[value_col] = coerce_numeric(chart[value_col])
    chart = chart.dropna().sort_values(value_col, ascending=True).tail(10)
    if chart.empty:
        return None
    labels = chart[page_col].map(lambda x: clean_label(str(x).replace("https://", "").replace("http://", ""), 48))
    plt.figure(figsize=(11, 6.8))
    plt.barh(labels, chart[value_col], color=PALETTE[2])
    style_plot(f"{title}: Highest-Traffic Landing Pages", "", "Estimated organic clicks / traffic")
    return save(out / "top_landing_pages_bar.png")


def build_brand_summary(project_dir: Path) -> tuple[Optional[pd.DataFrame], Optional[str]]:
    df, _, err = read_csv(project_dir, "branded_nonbranded")
    if df is not None:
        return df, None
    kw, _, kw_err = read_csv(project_dir, "keyword_sample")
    if kw is None:
        return None, err or kw_err
    brand_col = first_col(kw, ["brand_type", "branded_non_branded", "branded", "segment", "category"])
    value_col = first_col(kw, ["clicks", "traffic", "organic_traffic", "estimated_clicks"])
    if not brand_col or not value_col:
        return None, "Keyword sample exists but lacks brand/category and traffic columns"
    kw[value_col] = coerce_numeric(kw[value_col])
    summary = kw.groupby(brand_col, dropna=False).agg(clicks=(value_col, "sum"), keywords=(brand_col, "size")).reset_index()
    summary = summary.rename(columns={brand_col: "segment"})
    return summary, None


def plot_branded_nonbranded(df: pd.DataFrame, out: Path, title: str) -> Optional[str]:
    segment_col = first_col(df, ["segment", "category", "brand_type", "branded_non_branded", "intent"])
    click_col = first_col(df, ["clicks", "traffic", "organic_traffic", "estimated_clicks"])
    kw_col = first_col(df, ["keywords", "keyword_count", "count"])
    if not segment_col or not (click_col or kw_col):
        return None
    chart = df.copy()
    if click_col:
        chart[click_col] = coerce_numeric(chart[click_col])
    if kw_col:
        chart[kw_col] = coerce_numeric(chart[kw_col])
    chart = chart.dropna(subset=[segment_col])
    if chart.empty:
        return None
    metrics = []
    if kw_col:
        metrics.append(("Keywords", kw_col))
    if click_col:
        metrics.append(("Clicks / traffic", click_col))
    x = range(len(chart))
    width = 0.38 if len(metrics) == 2 else 0.6
    plt.figure(figsize=(9.5, 5.8))
    for i, (label, col) in enumerate(metrics):
        offsets = [p + (i - (len(metrics)-1)/2) * width for p in x]
        plt.bar(offsets, chart[col], width=width, label=label, color=PALETTE[i])
    plt.xticks(list(x), chart[segment_col].map(clean_label), rotation=0)
    if len(metrics) > 1:
        plt.legend(frameon=False)
    style_plot(f"{title}: Branded vs Non-Branded Search", "Count / estimated clicks")
    return save(out / "branded_nonbranded_comparison.png")


def plot_losses(df: pd.DataFrame, out: Path, title: str, kind: str) -> Optional[str]:
    item_col = first_col(df, ["landing_page", "url", "page", "keyword", "query", "item"])
    loss_col = first_col(df, ["estimated_traffic_loss", "traffic_loss", "loss", "change_abs", "delta"])
    start_col = first_col(df, ["start_traffic", "start", "baseline"])
    end_col = first_col(df, ["end_traffic", "end", "current"])
    if not item_col:
        return None
    chart = df.copy()
    if not loss_col and start_col and end_col:
        chart[start_col] = coerce_numeric(chart[start_col])
        chart[end_col] = coerce_numeric(chart[end_col])
        chart["computed_loss"] = chart[start_col] - chart[end_col]
        loss_col = "computed_loss"
    if not loss_col:
        return None
    chart[loss_col] = coerce_numeric(chart[loss_col]).abs()
    chart = chart[[item_col, loss_col]].dropna().sort_values(loss_col, ascending=True).tail(10)
    if chart.empty:
        return None
    plt.figure(figsize=(11, 6.7))
    plt.barh(chart[item_col].map(lambda x: clean_label(str(x).replace("https://", ""), 54)), chart[loss_col], color=PALETTE[4])
    style_plot(f"{title}: Largest {kind} Losses", "", "Estimated traffic loss")
    return save(out / f"largest_{kind.lower()}_losses_bar.png")


def plot_mix(df: pd.DataFrame, out: Path, title: str, label_col_candidates: list[str], filename: str, chart_title: str) -> Optional[str]:
    label_col = first_col(df, label_col_candidates)
    value_col = first_col(df, ["count", "rows", "backlinks", "referring_domains", "value"])
    if not label_col or not value_col:
        return None
    chart = df[[label_col, value_col]].copy()
    chart[value_col] = coerce_numeric(chart[value_col])
    chart = chart.dropna().sort_values(value_col, ascending=True).tail(10)
    if chart.empty:
        return None
    plt.figure(figsize=(10.5, 6.2))
    plt.barh(chart[label_col].map(clean_label), chart[value_col], color=PALETTE[3])
    style_plot(f"{title}: {chart_title}", "", "Rows / count")
    return save(out / filename)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate standard SEO report charts from normalized CSV files.")
    parser.add_argument("--project-dir", required=True, help="Directory containing normalized CSV files.")
    parser.add_argument("--output-dir", default=None, help="Directory for generated charts. Defaults to <project-dir>/charts.")
    parser.add_argument("--title", default="Target domain", help="Report/chart title prefix, usually the domain.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    out = Path(args.output_dir).expanduser().resolve() if args.output_dir else project_dir / "charts"
    out.mkdir(parents=True, exist_ok=True)

    created = []
    missing = []

    for key, plotter in [
        ("traffic_trend", plot_traffic_trend),
        ("country_traffic", plot_country_traffic),
        ("country_trend", plot_country_trend),
        ("page_type_summary", plot_page_type),
        ("top_pages", plot_top_pages),
    ]:
        df, path, err = read_csv(project_dir, key)
        if df is None:
            missing.append(err)
            continue
        name = plotter(df, out, args.title)
        if name:
            created.append({"dataset": key, "source": str(path), "file": name})
        else:
            missing.append(f"{key}: available file {path.name if path else ''} lacked required columns")

    brand_df, brand_err = build_brand_summary(project_dir)
    if brand_df is not None:
        name = plot_branded_nonbranded(brand_df, out, args.title)
        if name:
            created.append({"dataset": "branded_nonbranded", "source": "branded_nonbranded or keyword_sample", "file": name})
        else:
            missing.append("branded_nonbranded: available data lacked required columns")
    else:
        missing.append(brand_err)

    for key, kind in [("page_losses", "Page"), ("keyword_losses", "Keyword")]:
        df, path, err = read_csv(project_dir, key)
        if df is None:
            missing.append(err)
            continue
        name = plot_losses(df, out, args.title, kind)
        if name:
            created.append({"dataset": key, "source": str(path), "file": name})
        else:
            missing.append(f"{key}: available file {path.name if path else ''} lacked required columns")

    for key, labels, filename, chart_title in [
        ("anchor_mix", ["anchor_type", "segment", "category"], "backlink_anchor_mix_bar.png", "Backlink Anchor Mix"),
        ("destination_mix", ["page_type", "destination_type", "cluster", "category"], "backlink_destination_mix_bar.png", "Backlink Destination Page-Type Mix"),
    ]:
        df, path, err = read_csv(project_dir, key)
        if df is None:
            missing.append(err)
            continue
        name = plot_mix(df, out, args.title, labels, filename, chart_title)
        if name:
            created.append({"dataset": key, "source": str(path), "file": name})
        else:
            missing.append(f"{key}: available file {path.name if path else ''} lacked required columns")

    manifest = {
        "project_dir": str(project_dir),
        "output_dir": str(out),
        "created_count": len(created),
        "created": created,
        "missing_or_skipped": [m for m in missing if m],
    }
    (out / "asset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    md_lines = ["# SEO Chart Asset Manifest", "", f"Generated charts: **{len(created)}**", ""]
    if created:
        md_lines.append("## Markdown Snippets")
        md_lines.append("")
        for item in created:
            alt = item["file"].replace("_", " ").replace(".png", "")
            md_lines.append(f"![{alt}](charts/{item['file']})")
        md_lines.append("")
    if missing:
        md_lines.append("## Missing or Skipped Inputs")
        md_lines.append("")
        for item in missing:
            if item:
                md_lines.append(f"- {item}")
        md_lines.append("")
    (out / "asset_manifest.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps(manifest, indent=2))
    return 0 if created else 2


if __name__ == "__main__":
    raise SystemExit(main())
