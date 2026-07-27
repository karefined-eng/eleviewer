---
name: seo-competitor-analysis
description: Create simplified, target-first SEO organic competitor reports modeled on the approved example report style. Use for `/seo-competitor-analysis`, simplified SEO reports, organic visibility diagnosis, country traffic trend reports, Ahrefs/Semrush/Similarweb/GSC organic data analysis, page-type SEO analysis, branded versus non-branded keyword review, and backlink strategy analysis. Always generate supporting charts from normalized data before writing the report. This report is written from the perspective of someone competing against the target domain — it explains the domain's strategy, not how to improve it.
---

# SEO Competitor Analysis

Create **simplified, evidence-led SEO competitor reports** that read like the approved style example: direct, target-first, concise, and analytical. The goal is to help the reader — who is a **competitor** of the target domain — understand the target's SEO strategy, strengths, weaknesses, and dependencies. The report does NOT advise the target domain on what to do; it dissects what the target is doing so the reader can compete against them more effectively.

If more style guidance is needed, read `references/style_example.md` (a fictionalized AI-tool site; its clusters and numbers apply only to that vertical and must never be reused). If normalizing chart input files, read `references/data_dictionary.md`.

## Core Output Standard

Write the final deliverable as a polished Markdown report unless the user asks for another format. Use complete paragraphs, clear tables, and chart images embedded with Markdown image syntax. Use numeric reference-style citations for all tool exports, public pages, and derived analysis files.

Do not make unsupported causal claims. Use phrasing such as **"the data shows," "the available data cannot confirm," "this suggests,"** and **"this should be validated with additional data."** Avoid saying a change happened "because" of an algorithm update, content issue, or link activity unless the data directly proves it.

**Critical rule: Do NOT include any recommendations, action plans, roadmaps, or prescriptive advice for the target domain.** This report is purely analytical — it explains what the domain is doing and how their strategy works. The reader will draw their own competitive conclusions.

## Mandatory Workflow

1. **Collect source data.** Pull the best available organic search data from Ahrefs, Semrush, Similarweb, GSC, GA4, sitemap/robots.txt, and public pages depending on user access. If the user specifically asks to use Ahrefs, prioritize Ahrefs exports and state where other data is unavailable or only directional.
2. **Normalize analysis tables.** Save CSV files in the project directory using the names in `references/data_dictionary.md` whenever possible.
3. **Generate charts before writing.** Run:

```bash
python /home/ubuntu/skills/seo-competitor-analysis/scripts/generate_seo_charts.py \
  --project-dir /path/to/project \
  --output-dir /path/to/project/charts \
  --title "target.com"
```

4. **Use the chart manifest.** Review `/path/to/project/charts/asset_manifest.md` and embed relevant chart snippets in the final report. If a critical chart cannot be generated, add an explicit data limitation instead of inventing values.
5. **Write the report.** Follow the report structure below. Preserve the style example's direct narrative style. Remember: no recommendations — only analysis of the target's strategy.
6. **Validate assets before delivery.** Run:

```bash
python /home/ubuntu/skills/seo-competitor-analysis/scripts/validate_report_assets.py \
  --report /path/to/project/final_report.md \
  --charts-dir /path/to/project/charts
```

Use `--allow-missing-critical` only when missing critical charts are explicitly explained in the report. The validator also scans the report body for prescriptive-language patterns (e.g., "the action is to," "should focus," "recovery plan," "90-day roadmap"); resolve every such warning before delivery.

## Standard Report Structure

Use this structure by default. Rename sections only when the user's request clearly requires it.

```markdown
# SEO Competitor Report: [target.com]

**Prepared by:** Manus AI  
**Date:** [Month Day, Year]  
**Primary data sources:** [Ahrefs/Semrush/Similarweb/GSC/GA4/public crawl/sitemap]

## Executive Narrative

[Paragraph 1: state the main trend and the most important strategic implication for competitors. Keep it concise, numeric, and direct.]

[Paragraph 2: state what the target site depends on, what changed, and what this means for the competitive landscape.]

![Global organic trend](charts/global_organic_trend.png)

---

# Part 1: Organic Search Performance

## 1. Business Context and SEO Footprint
## 2. Page Type Analysis: Where Organic Demand Lands
## 3. Organic Visibility by Country
## 4. Traffic Trend: Is Organic Search Growing or Declining?
## 5. Branded vs Non-Branded Search

---

# Part 2: Backlink Strategy Evidence

## 6. Backlinks: How Is [target] Building Links?

---

# Part 3: Strategic Assessment

## 7. Key Dependencies and Vulnerabilities

---

## References
```

## Section Writing Rules

Open most sections with a **bold finding sentence** that answers the section title. Follow with one or two evidence paragraphs. Keep each section focused on interpretation rather than metric listing.

For the Executive Narrative, write two compact paragraphs. The first paragraph should name the main organic trend and size it. The second should explain what the site currently depends on and what this means for competitors observing this domain.

For Page Type Analysis, classify landing pages by meaningful SEO intent, not just URL folder. Derive clusters from the target's actual business rather than copying clusters from the style example or past reports. Common patterns include product/tool pages, core feature or category pages, localized pages, content hubs/blog, homepage/brand, comparison/alternative pages, pricing, apps/extensions, and support — for example, an AI-tool site may cluster around model access, detection, and writing utilities, while an e-commerce site clusters around category, product, and guide pages. Include a table with page type, evidence, traffic/click share where available, and interpretation.

For Country Visibility, compare country-level traffic and keyword footprint where possible. If only a current snapshot exists, do not imply trend. If trend data exists, state whether each priority market ended higher or lower than it started.

For Branded vs Non-Branded Search, report both keyword count and click/traffic weight. The key question is whether non-branded breadth has become non-branded click strength.

For Backlinks, answer whether the pattern looks homepage/brand-led, PR-led, SEO-page-led, or low-quality/manipulative. Separate link quantity from link quality. Use anchor mix and destination page type charts whenever data exists.

For Key Dependencies and Vulnerabilities, identify what the target domain relies on most heavily (specific page types, specific countries, branded vs non-branded traffic, specific link sources) and where they appear exposed. Frame this as a strategic intelligence section — what a competitor should understand about the target's position. Do NOT provide recommendations or action plans for the target domain.

## Mandatory Charts and Graphs

Generate and embed every chart supported by the available data. The report should normally include at least three charts, and stronger reports include five or more.

| Chart | Default filename | Use when |
|---|---|---|
| Global organic trend | `global_organic_trend.png` | Any traffic trend data exists. Place immediately after Executive Narrative. |
| Top countries | `top_countries_bar.png` | Country-level traffic snapshot exists. |
| Country trend | `country_trend.png` | Country-level history exists. |
| Page type distribution | `page_type_traffic_bar.png` | Landing pages can be grouped by page type. |
| Top landing pages | `top_landing_pages_bar.png` | Page-level traffic/click data exists. |
| Branded vs non-branded | `branded_nonbranded_comparison.png` | Keyword brand classification exists. |
| Largest page losses | `largest_page_losses_bar.png` | Six-month page loss data exists. |
| Largest keyword losses | `largest_keyword_losses_bar.png` | Six-month keyword loss data exists. |
| Backlink anchor mix | `backlink_anchor_mix_bar.png` | Anchor text classification exists. |
| Backlink destination mix | `backlink_destination_mix_bar.png` | Backlink destination page-type data exists. |

If the chart script cannot create a mandatory chart because an input file is missing, include a plain-language limitation in the relevant section and cite the chart manifest or analysis note.

## Citation and Evidence Rules

Cite every dataset, export, public page, and analysis file using numeric reference-style Markdown citations. Treat derived analysis files as sources when they contain calculations, classifications, or normalized data. Example:

```markdown
Global estimated organic search traffic declined 50.8% across the measured period.[1] [2]

## References

[1]: tables/semrush_top20_countries.csv "Semrush country and rank-history exports, collected YYYY-MM-DD"
[2]: tables/similarweb_total_visits_6m.csv "Similarweb traffic-source exports, collected YYYY-MM-DD"
```

Never cite tool screenshots or browser observations vaguely. Save key findings to notes, CSVs, or Markdown analysis files, then cite those files in References.

## Deliverable Package

Attach the final Markdown report first. Also attach a package containing charts, normalized CSVs, analysis notes, sitemap/robots evidence, and the chart asset manifest. Do not convert to PDF unless the user explicitly requests it.

## Quality Checklist

Before delivery, confirm that:

1. The report uses the standard structure or explains why it was adapted.
2. The report title follows the format "SEO Competitor Report: [domain.com]".
3. The opening narrative states the main trend and competitive implications without fluff.
4. All major claims are backed by citations.
5. Charts were generated by `generate_seo_charts.py` where source data exists.
6. The final report passes `validate_report_assets.py`, or any missing chart categories are explicitly documented.
7. **No recommendations, action plans, roadmaps, or prescriptive advice for the target domain appear anywhere in the report.** Run `validate_report_assets.py` and resolve every prescriptive-language warning before delivery.
8. The report reads as competitive intelligence — explaining what the target is doing, not telling them what to do.
9. Page-type clusters are derived from the target's actual business, not copied from the style example or earlier reports.
