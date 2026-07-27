---
name: seo-audit
description: Create plain-language, evidence-led SEO audit reports using the structure developed with the user. Use when asked to create, revise, or standardize an SEO audit report, SEO audit mockup, organic search audit, backlink-focused SEO audit, business-style report, or sample-modeled audit where the output must rely strictly on report data, avoid hallucinations, use a 150–200 word one-paragraph executive summary, explain organic traffic and market drivers, exclude standalone Content Quality Audit and On-Page SEO sections by default, end with a concise ordered problem/fix prioritization list instead of a roadmap, and use direct insight-and-action language.
---

# SEO Audit

## Purpose

Use this skill to produce a business-style SEO audit report that explains **what the data shows, why it matters, and what action to take**. The report must read like an insight-led executive/practitioner report, not a generic SEO checklist or metric dump. Future reports should consistently follow the same structure, reasoning flow, and evidence-led quality standard as the approved `manus.im` report: verdict first, evidence second, business/SEO meaning third, and specific fix last.

The report must rely only on available evidence from audit data, user-provided exports, existing report tables, crawl data, GSC/GA data, Ahrefs/Semrush data, Similarweb data, Lighthouse/PageSpeed data, or clearly labeled mock data. Do not force a fixed source hierarchy because available datasets vary by user. Before writing, identify which datasets exist, which important datasets are missing, and what additional exports would be needed for a full analysis. State missing-data limits in the report’s data note or the relevant section; ask the user for missing data only when the requested analysis cannot be completed without it. Do not infer team intent, Google penalties, spam risk, strategy, or technical priority unless the report evidence supports it.

## Core workflow

1. Confirm the data basis internally. Identify available datasets and missing datasets before writing. State data limitations only where needed; do not include a standalone **Scope and Data Used** section unless the user asks for it.
2. If important datasets are missing, tell the user in the report’s data note or affected section what is lacking and what data would be needed for a fuller analysis, such as GSC/GA traffic exports, keyword/top-page exports, crawl exports, backlink exports, internal-link exports, sitemap data, or Lighthouse/Core Web Vitals data.
3. Build evidence tables and charts before writing. Extract the numerical facts needed for organic traffic trend, country drivers, top pages, branded versus non-branded terms, keyword concentration, content clusters, multilingual pages, backlinks, technical issues, site architecture, and page experience. When any supported chart data exists, normalize it into `chart_data/*.csv` inputs and run `scripts/generate_seo_audit_charts.py` so charts use the fixed report style and filenames.
4. Write findings only after the evidence exists. Each finding must connect to a number, table, chart, observed page issue, or explicitly stated data limitation.
5. Prioritize insight over raw metrics. Do not list platform overview numbers unless they explain growth, decline, concentration risk, market fit, content strategy, or a concrete action.
6. Separate brand demand from SEO discovery. Do not call total organic growth a success if branded growth hides weak non-branded discovery.
7. Diagnose the current SEO pattern from evidence only. Decide whether performance is driven by branded demand, utility/tool pages, content expansion, localized pages, commercial landing pages, backlink growth, technical cleanup, or site architecture based on the data.
8. Prioritize actions by business impact and execution order.

## Required report structure

Use this structure unless the user provides a different one:

1. Executive Summary
2. Organic Traffic Trend
   - Include a graph for total global organic traffic for the last six months when data exists.
   - Include Top Organic Countries with market/page/keyword insight.
3. Page Type Analysis
4. Branded vs Non-Branded Search Terms
5. Keyword Portfolio
6. SEO Content Analysis
   - Content Cluster Matrix with cluster-click chart.
   - Multilingual/locale page analysis with locale traffic-share chart when data exists.
7. Site Architecture
   - Verdict-led architecture assessment covering click depth, orphan pages, URL hierarchy, internal link equity, crawl budget, indexation logic, and navigation/breadcrumbs.
8. Backlink Analysis (must follow this exact flow in order):
   - Headline: State the backlink profile strength and why it is strong, weak, or spammy.
   - Domain Quality: Analyze if the domain acquires low quality spammy or high quality referring domains.
   - Anchor Text Analysis: Branded vs non-branded split, healthy mix assessment, determine if PR-driven or SEO team.
   - Distribution of Backlinks: Homepage = PR/natural, feature pages = SEO team efforts.
   - Verdict: Final conclusion on the domain's backlink profile.
9. Technical SEO
10. Core Web Vitals and Page Experience
11. Final Prioritization
12. References

Do not include standalone sections titled **Scope and Data Used**, **Content Quality Audit**, **On-Page SEO**, **Robots, Indexation, and Canonical Control**, **Structured Data**, **30/60/90-Day Roadmap**, **7-Day Roadmap**, or **90-Day Roadmap** unless the user explicitly asks for them. If robots, indexation, canonical, schema, structured-data, content-quality, title-tag, meta-description, heading, or internal-page relevance issues matter, fold them into **SEO Content Analysis**, **Site Architecture**, **Technical SEO**, or the most relevant existing section rather than creating standalone sections.

## Standard chart-generation workflow

Use the bundled chart generator for every future report that has chartable data. Create a working `chart_data/` directory for the report, add the supported normalized CSV files listed below, and run:

```bash
python /home/ubuntu/skills/seo-audit/scripts/generate_seo_audit_charts.py \
  --data-dir /path/to/chart_data \
  --output-dir /path/to/report/output/assets \
  --manifest /path/to/report/output/chart_manifest.md
```

The script generates every supported chart for which a matching CSV exists and writes a manifest showing which charts were generated or skipped. It must not fabricate data. If a chart is skipped because the needed data was not provided, state the limitation in the relevant section rather than creating a fake chart.

Supported standard chart inputs and fixed output files are:

| Input CSV | Required Minimum Columns | Output Chart |
|---|---|---|
| `organic_traffic_trend.csv` | `period`, `organic_clicks_or_visits` | `assets/organic_traffic_trend.png` |
| `top_organic_countries.csv` | `country`, `traffic_share_pct` | `assets/top_organic_countries.png` |
| `page_type_analysis.csv` | `page_type`, `traffic_share_pct` | `assets/page_type_traffic_share.png` |
| `branded_nonbranded.csv` | `search_type`, `traffic_share_pct` | `assets/branded_nonbranded_mix.png` |
| `keyword_portfolio.csv` | `keyword`, `clicks_or_traffic`, `brand_type` | `assets/keyword_portfolio_brand_mix.png` |
| `content_clusters.csv` | `landing_page_cluster`, `clicks` | `assets/content_cluster_clicks.png` |
| `locale_analysis.csv` | `locale`, `traffic_share_pct` | `assets/locale_traffic_share.png` |
| `site_architecture_depth.csv` | `click_depth`, `pages` | `assets/site_architecture_click_depth.png` |
| `backlink_referring_domains.csv` | `period`, `referring_domains` | `assets/backlink_referring_domains.png` |
| `backlink_quality.csv` | `quality_bucket`, `referring_domains` | `assets/backlink_quality_distribution.png` |
| `core_web_vitals.csv` | `metric`, `value` | `assets/core_web_vitals_snapshot.png` |

Do not hand-build alternative versions of these standard charts unless the user explicitly asks for a different style. Custom charts are allowed only when the required analysis is not covered by the standard generator; they must still follow the same clean, report-safe style and be referenced in the report body only when they support a finding.

## Executive summary rules

The executive summary is strict.

It must be **one condensed paragraph of 150–200 words**, unless the user requests another format. Start the paragraph with a bold headline that summarizes the main audit finding in one sentence. The paragraph must distill every main finding without becoming a metric dump: organic traffic trend, which pages or page types capture the largest traffic, keyword mix and whether traffic is branded or non-branded dependent, keyword concentration risk, the most important technical SEO finding, and the backlink-profile finding.

The backlink sentence in the summary must answer whether the last six months show active link building, whether the backlink profile is spammy or high quality, and whether authority reaches commercial pages. Use anchor text, referring-domain quality, target-page mix, link velocity, and country relevance when the data exists.

Do not add unsupported claims such as “Google penalty,” “the SEO team focused on X,” or “active outreach campaign” unless the report data directly supports that reading. Prefer direct evidence statements such as “traffic growth came from,” “the backlink data shows,” or “the largest page type is.”

## Section-specific standards

Every section must answer its strategic question before showing detail. Do not merely describe metrics. Use this logic flow unless the user provides a different structure: **verdict or headline insight → evidence → why it matters → what should change**. Keep insights simple and avoid unnecessary data.

### Organic Traffic Trend

Start with a simple answer to whether organic traffic has grown, stayed flat, or dropped over the last six months. Then identify the landing page, folder, country, or page type causing the growth or decline, and name the organic keywords that increased or dropped when keyword history exists. If the timing overlaps a documented Google core update, mention it only as a possible coinciding factor, not as a proven cause unless the evidence supports it. Do not mention penalties unless manual-action or penalty evidence exists.

Include a last-six-month global organic traffic graph when date-level data exists. The section should answer: **what changed, which landing pages caused the change, which keywords contributed, and whether an external algorithm event coincided with the movement**.

### Top Organic Countries

For the country with the highest organic traffic, you must identify which specific pages from that country are driving the growth. List out the top 3 pages, their category, their page type, and the top keyword driving the organic growth for those pages. You must also mention the device split (desktop vs. mobile) from this top country. This is the required logic flow for this section.

The Top Organic Countries table should focus on **which market it caters to**, **which pages or content types win in that market**, and **why those pages work**. Remove action columns from this table. The analysis must answer why the top country gets the highest organic traffic, not just list country shares.

### Page Type Analysis

Begin with the page type that captures the highest global organic traffic and its traffic percentage. Explain what the page type is, such as homepage, landing page, utility page, tool, blog, docs, comparison page, or localized page. Then give the strategic reading: whether the site is winning because utility pages target high-volume keywords, because brand navigation dominates, because blog discovery is working, because commercial pages are visible, or because localized templates match market demand.

### Branded vs Non-Branded Search Terms

Start with a headline in this style: **“Branded search dominates organic search, with branded terms capturing X% of traffic and non-branded terms capturing Y%.”** Reverse the wording when non-branded dominates. Then mention only the top keywords that drive the highest organic traffic and explain what those terms reveal about demand quality, brand dependency, discovery, and fragility. Keep the finding simple; do not add unnecessary keyword rows or secondary metrics.

### Keyword Portfolio

Analyze whether the keyword portfolio is branded-heavy or non-branded-heavy and whether traffic depends on a handful of keywords or is spread across many. Include the top 10 keywords and a pie chart for branded versus non-branded keyword-click mix when data exists. The point of the analysis is to tell readers whether traffic is fragile because it depends on a few terms, resilient because it is spread across many terms, and whether keyword coverage is broad enough for sustainable growth.

### SEO Content Analysis

Identify a small set of the strongest landing-page/content clusters that have been built. Include a bar chart showing clicks by landing-page content cluster when data exists. The content-cluster table must use these columns: **Landing Page Cluster**, **Number of Pages**, **Clicks**, **Keywords Ranked**, and **Traffic Share %**.

Include a multilingual or locale-page analysis when locale pages exist. Start with a headline insight stating how much organic search traffic locale pages receive and which locales lead. Use a bar chart to show traffic share by locale and explain what content types or intents perform best in those locales.

### Site Architecture

Include a standalone section titled **Site Architecture** immediately after **SEO Content Analysis** and before **Backlink Analysis**. Lead with a verdict in business terms: state whether the architecture is helping or hurting organic growth, and connect the structural issue to ranking, crawling, indexation, or conversion impact. Do not describe the site structure back to the reader unless the description explains a traffic or ranking consequence.

Write this section as narrative findings, not a checklist. Each finding cluster must stay short: **3–4 lines maximum** in the final report body, ideally one compact paragraph of roughly 45–70 words. Each finding must include the **observation**, the **SEO or business impact**, and the **fix** without expanding into long explanation. The findings must answer these seven structural questions when data exists: click depth, orphan pages, hierarchy and URL structure, internal link equity, crawl budget waste, indexation logic, and navigation/breadcrumbs. Use crawl exports, internal-link exports, sitemap data, GSC landing-page data, and Ahrefs/Semrush top-page data as evidence. If a required data point is not available, state that the data was not provided rather than guessing.

Use a simple click-depth chart, link-flow diagram, or architecture diagram only when it communicates the issue faster than prose. Keep raw URL lists, full orphan-page inventories, long broken-link tables, and crawl-detail exports in an appendix or supporting workbook, not in the report body. The report body should contain only the sized finding, business impact, and recommended fix.

### Backlink Analysis

The backlink analysis section MUST follow this exact flow in order. Do not rearrange, skip, or merge steps. Each step flows into the next as a narrative:

1. **Headline:** State the backlink profile strength and why it is strong, weak, or spammy.
2. **Domain Quality:** Analyze if the domain acquires low quality spammy or high quality referring domains.
3. **Anchor Text Analysis:** Branded vs non-branded split, healthy mix assessment, determine if PR-driven or SEO team.
4. **Distribution of Backlinks:** Homepage = PR/natural, feature pages = SEO team efforts.
5. **Verdict:** Final conclusion on the domain's backlink profile.

Keep the finding simple; do not add unnecessary keyword rows or secondary metrics. Do not recommend mass disavow work unless the evidence shows clear harmful links at meaningful scale.

### Final Prioritization

End the report with a concise section titled **Final Prioritization**. Do not create a separate **Priority Matrix** or **7-day**, **30-day**, **60-day**, **90-day**, or **30/60/90-Day Roadmap** section unless the user explicitly asks for one.

Write final priorities as an ordered list, usually **1, 2, 3, 4**, in execution order. Each numbered item must contain only two parts: **Problem:** one direct sentence stating what is broken or missing, and **Fix:** one direct sentence stating what should be changed. Do not add impact/effort/confidence columns, timeline rows, success metrics, or explanatory paragraphs in this final section.

## Writing style

Write in plain business language. Use short paragraphs. Avoid fluff. Every section should include a direct finding, the evidence behind it, the business impact, and the action, expressed in the narrative rather than in table columns. Only the Technical SEO table may carry an `Action` column; all other tables must not. Route all other actions to the narrative finding or to **Final Prioritization**.

Use phrases like these:

- “Traffic increased, but the growth came from branded searches.”
- “The issue is not content volume. The issue is weak commercial coverage.”
- “The backlink profile is high quality and brand-heavy, not spam-led.”
- “Fix duplicate URLs before launching new pages at scale.”
- “Use non-branded commercial clicks as the main SEO KPI.”

Avoid phrases like these:

- “It is worth noting that…”
- “This may suggest…”
- “In today’s competitive landscape…”
- “A robust SEO strategy should…”
- “Overall, the website has opportunities…”

## Evidence standards

Every claim about strategy, cause, quality, or priority must be backed by a data point already in the report. If evidence is missing, write “Data not provided” or identify the needed export. Do not pretend a full analysis is possible when key data is absent; tell the user which datasets are lacking and what additional data would be needed for a fuller report.

Use numerical reasoning. Compare changes across time, split branded versus non-branded, identify concentration risk, identify top page and country drivers, distinguish high-volume low-intent pages from commercial pages, and separate localized page performance from global performance. Do not guess causes that are not visible in the data.

For mock reports, synthetic data may be used only when the output is clearly labeled as a mockup. The mockup should still be internally consistent.

## Backlink analysis standards

The backlink analysis section MUST follow this exact flow in order. Do not rearrange, skip, or merge steps. Each step flows into the next as a narrative:

1. **Headline:** State the backlink profile strength and why it is strong, weak, or spammy.
2. **Domain Quality:** Analyze if the domain acquires low quality spammy or high quality referring domains.
3. **Anchor Text Analysis:** Branded vs non-branded split, healthy mix assessment, determine if PR-driven or SEO team.
4. **Distribution of Backlinks:** Homepage = PR/natural, feature pages = SEO team efforts.
5. **Verdict:** Final conclusion on the domain's backlink profile.

Keep the finding simple; do not add unnecessary keyword rows or secondary metrics. Do not recommend mass disavow work unless the evidence shows clear harmful links at meaningful scale.

## Quality checks before delivery

Before delivering, verify that:

1. The executive summary has exactly one paragraph unless the user requested another format.
2. The executive summary is 150–200 words by default and still includes every main finding.
3. The summary headline states the main audit finding in one concise sentence.
4. No unsupported claims remain.
5. No standalone **Scope and Data Used**, **Content Quality Audit**, **On-Page SEO**, **Structured Data**, or **Robots, Indexation, and Canonical Control** sections remain unless explicitly requested.
6. Organic Traffic Trend includes a six-month global organic traffic chart when date-level data exists.
7. Top Organic Countries explains the leading country by page and keyword drivers when data exists.
8. Page Type Analysis starts with the largest page type and its traffic percentage.
9. Branded vs Non-Branded starts with a dominance headline and includes percentages.
10. Keyword Portfolio includes the top 10 keywords and a branded/non-branded pie chart when data exists.
11. SEO Content Analysis includes cluster and locale charts when data exists.
12. The report includes a standalone **Site Architecture** section after SEO Content Analysis, led by a business verdict and supported by concise 3–4 line narrative finding clusters that cover click depth, orphan pages, URL hierarchy, internal link equity, crawl budget, indexation logic, and navigation/breadcrumbs when data exists.
13. The report ends with **Final Prioritization**, written as an ordered list where each item includes only **Problem** and **Fix**.
14. No **7-day**, **30-day**, **60-day**, **90-day**, or **30/60/90-Day Roadmap** section appears unless the user explicitly requested one.
15. `scripts/generate_seo_audit_charts.py` was run when supported chart data existed, `chart_manifest.md` was produced, and every chart referenced in the report exists under `assets/` with the fixed filename from the standard chart table.
16. Any missing chart is explained by unavailable data in the relevant section or manifest; no placeholder chart references remain in the final report.
17. No table outside Technical SEO carries an `Action` column; actions appear in narrative findings and in **Final Prioritization**.

Use `scripts/validate_exec_summary.py` when a Markdown report file is available. Use `scripts/generate_seo_audit_charts.py` whenever supported chart data is available.

## Bundled resources

- `scripts/validate_exec_summary.py`: Validates that the Executive Summary has the expected paragraph count, optional word target, and bold opening headline. Supports English and Chinese headings and counting via `--lang auto/zh/en`.
- `scripts/generate_seo_audit_charts.py`: Generates fixed-format SEO audit charts from normalized CSV inputs and writes a chart manifest showing generated and skipped visuals.
- `templates/report_structure.md`: Reusable Markdown skeleton for the updated report structure.
