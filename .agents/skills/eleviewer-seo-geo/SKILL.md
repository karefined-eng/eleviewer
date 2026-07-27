---
name: eleviewer-seo-geo
description: >
  Unified SEO, GEO, keyword research, SEO audit, and SEO competitor analysis skill
  for EleViewer and eleviewer-site. Use this when updating website metadata, landing
  pages, distribution channels, conducting keyword research, creating SEO audit
  reports, or performing SEO competitor analysis. Covers: intent-first keyword
  strategy, technical SEO infrastructure, GEO/AI visibility, trust and conversion UX,
  keyword research Excel workbooks, evidence-led SEO audit reports, simplified
  target-first SEO organic competitor reports, and competitor strategy replication
  reports with data-backed replication guidance.
---

# EleViewer SEO & GEO Alignment Strategy

This skill outlines the blueprint for transitioning EleViewer from an "invisible" repository to a highly discoverable **Sovereignty Workstation** optimized for both search engines and AI agents (ChatGPT, Perplexity, Claude).

## 1. Intent-First Keyword Strategy
Target distinct "intent buckets" across all marketing copy, `eleviewer-site` landing pages, and FAQs:
*   **The Frustrated Student:** Target high-volume queries like *"open docx without Word,"* *"free alternative to Adobe Acrobat for students,"* and *"student document viewer"*.
*   **The Accessibility Seeker:** Focus on high-conversion terms such as *"read PDF aloud offline,"* *"free pdf reader with text to speech windows,"* and *"listen to lecture slides for free"*.
*   **The Privacy Minimalist:** Capture niche searches for *"open source pdf reader no telemetry,"* *"portable docx editor,"* and *"local-first document viewer"*.
*(Note: Per AGENTS.md Rule 12, localized "Trojan Horse" keywords like "UG course material viewer" are strictly deprecated).*

## 2. Technical SEO & Infrastructure (`eleviewer-site`)
*   **SoftwareApplication Schema:** The Vercel site header MUST include JSON-LD structured data declaring the **220MB file size**, **$0 price**, and **Windows 10/11 platform** to earn Google "rich snippets".
*   **Sitemap & Canonical Routing:** All CTAs must route through `/download` to prevent duplicate content penalties. The `sitemap.ts` must make pages like `/download`, `/demo`, and `/review` indexable.
*   **Absolute Navigation:** Use absolute anchor paths (e.g., `href="/#features"`) to ensure SEO-friendly routing from subpages.

## 3. GEO & AI Visibility (The "Citation Moat")
*   **Passive Discovery Streams:** Maintain EleViewer's presence on directories like **AlternativeTo.net**, **Chocolatey**, and **Scoop**. AI models heavily weigh these directories for software recommendations.
*   **Semantic Markup:** Use exact technical terminology (e.g., *"GPLv3 licensed portable .exe"*, *"PySide6 factory pattern"*) so LLM crawlers can accurately categorize the workstation.
*   **GitHub Repository SEO:** Keep repository topics/tags updated (`#pyside6`, `#pdf-reader`, `#text-to-speech`) to rank in GitHub's discovery feed (a major AI training data source).

## 4. Trust & Conversion UX
*   **Bypassing the "Blue Wall":** The long-term goal includes **Azure Trusted Signing** to establish "Verified Publisher" status, eliminating SmartScreen bounce rates.
*   **Mobile-to-Desktop Funnel:** Ensure `<MobileReminder>` components leverage the Web Share API to capture mobile search traffic (where 50% of discovery happens) and push the intent to desktop for download.


================================================================================

<!-- MERGED FROM: keyword-research -->
<!-- Original Skill Metadata:
name: keyword-research
description: Conduct keyword research and generate a strictly formatted three-tab Excel workbook containing a Topic Cluster Summary, 300 priority keywords, and a competitor gap analysis. Use when the user asks to "conduct keyword research for [keyword]", "create a keyword research excel", or provides a keyword and needs a structured priority list and competitor gaps.
-->

# Keyword Research

This skill provides a locked-in workflow for generating a comprehensive, three-tab Excel workbook for keyword research. It is designed to enforce a strict output structure that never deviates, providing a cluster-level summary, 300 prioritized keywords, and actionable competitor gaps.

Use this skill whenever the user provides a seed keyword and requests keyword research, especially when they mention an Excel sheet, priority targets, or competitor gaps.

## The Keyword Research Workflow

When triggered, you must execute the following workflow to gather data and generate the exact Excel deliverable. Do not deviate from this structure.

### Step 0: Confirm Target Country & Data Source (Ask First)

Before doing anything else, you MUST ask the user two things and wait for their response. Do not proceed to data gathering until they answer.

**0a. Target Country (mandatory first question):**
Ask the user which country or countries they are targeting for this keyword research. This determines which search volume data to pull. Handle their answer as follows:

- **A specific country (e.g., United States, United Kingdom, Germany, India):** Pull and report search volume **for that country only**. The volume columns must reflect that country (e.g., "Monthly Volume (US)" becomes "Monthly Volume (UK)").
- **Multiple specific countries:** Pull volume for each named country and report a per-country volume column for each.
- **Worldwide / global:** Pull the **global (worldwide) volume**.
- **No global/worldwide data available:** If the user wants worldwide data but the chosen data source does not provide a true global/worldwide volume figure, clearly tell the user that global/worldwide volume is not available from that source, and ask whether they want to (a) proceed with a specific country instead, or (b) approximate by summing major country volumes (clearly labeled as an estimate). Do not silently substitute one for the other.

Use the user's country choice consistently across all three tabs and all volume columns.

**0b. Data Source:**
Ask the user which data source they want to use.

- If they want **Ahrefs, Semrush, DataForSEO, or Similarweb**, tell them they can connect their accounts to Manus via MCP, and use that connected data source for the report.
- If the tool they want does **not** have an MCP integration, ask them to check whether it can be connected via API instead.
- If no data source can be connected, clearly tell the user that Manus will use **public data** (knowledge and available public search tools) to build the report, and note this clearly in the deliverable.

### Step 1: Data Gathering & Analysis
1. **Understand the Seed:** Analyze the user's input keyword to determine the core topic, target audience, and primary search intent.
2. **Keyword Expansion (300 Keywords):** Use your knowledge and available search tools to generate exactly 300 relevant keywords.
   - Categorize them into exactly 5 logical Topic Clusters.
   - Determine Search Intent (Informational, Navigational, Commercial, Transactional).
   - Pull **Monthly Volume for the target country/countries chosen in Step 0a**, OR **Global Volume** if the user chose worldwide. Only report the volume scope the user selected; do not fabricate a country breakdown the source cannot support.
   - Estimate Keyword Difficulty (KD) and assign a KD Level (e.g., Easy, Medium, Hard).
   - Estimate CPC.
   - Identify the Parent Topic.
   - Recommend a Content Type (e.g., Blog Post, Product Page, Comparison Guide).
   - Assign a Priority rating (High, Medium, Low).
3. **Competitor Analysis:** Identify the top 20 organic competitors for this topic.
   - Estimate their Traffic Share %, Traffic Value, and Domain Rating (DR).
   - Write a brief observation for each.
   - Identify 20 high-value keyword gaps (keywords competitors rank for but represent an opportunity) and recommend actions.
   - Synthesize 5 key findings and 5 prioritized recommendations, highlighting the Total Addressable Market and Best Immediate Opportunities.

### Step 2: Excel Generation
You must use the bundled Python script to generate the Excel workbook. This script enforces the locked-in structure, including specific tabs, columns, and color-coding.

**Run the generation script:**
```bash
python /home/ubuntu/skills/keyword-research/scripts/generate_keyword_excel.py <input_json_path> /home/ubuntu/keyword_research.xlsx
```
*(Note: You must first prepare the data in JSON format to pass to the script. The script expects a JSON file containing the 300 keywords and the competitor data. See `scripts/generate_keyword_excel.py` and `references/data_schema_example.json` for the required JSON schema).*

**Volume column naming:** Populate the volume field(s) for each keyword to match the Step 0a choice. For a specific country, label the column for that country (e.g., `Monthly Volume (UK)`). For worldwide, use `Global Volume`. Keep the chosen label consistent across the JSON, the keyword tab, and the cluster summary tab.

### Step 3: Deliverable Review
1. Ensure the output file is an `.xlsx` workbook.
2. Verify the volume columns reflect the country/worldwide scope the user selected in Step 0a, and that the deliverable notes the volume scope clearly.
3. Verify Tab 1 (Topic Cluster Summary) aggregates all 5 clusters with correct totals.
4. Verify Tab 2 contains exactly 300 rows (plus header) and the required columns.
5. Verify Tab 3 contains the three required sections.
6. Deliver the `.xlsx` file to the user, stating which country/worldwide volume scope was used.

## Locked-In Deliverable Structure

The output MUST be an Excel workbook with exactly three tabs formatted as follows. The volume columns below show the default labels; rename the volume column(s) to reflect the target country/countries or worldwide scope chosen in Step 0a.

### Tab 1: Topic Cluster Summary (Auto-Generated)
This tab is automatically generated by the script from the keyword data. It provides a high-level overview of search volume distribution across clusters.

**Columns:**
1. Topic Cluster
2. Keywords (count)
3. Monthly Volume (target country) (aggregated)
4. Global Volume (aggregated)
5. Avg KD
6. Avg CPC ($)
7. High Priority (count)
8. Medium Priority (count)
9. Low Priority (count)

**Includes:**
- A TOTAL row summing all clusters.
- A Volume Share % note showing each cluster's proportion of total volume.

### Tab 2: Priority Keyword Targets (300 Keywords)
This tab must contain exactly 300 keyword rows, organized across 5 topic clusters.

**Required Columns:**
1. Keyword
2. Topic Cluster (Must be one of 5 defined clusters)
3. Search Intent
4. Monthly Volume (target country)
5. Global Volume
6. Keyword Difficulty (KD)
7. KD Level
8. CPC
9. Parent Topic
10. Recommended Content Type
11. Priority

**Formatting Rules:**
- The `Priority` column MUST be color-coded (Green = High, Yellow = Medium, Red = Low).
- The `KD Level` column MUST be clearly formatted for quick scanning.

### Tab 3: Competitor Keyword Gaps & Landscape
This tab must contain exactly three sections.

**Section 1: Traffic Share by Domain**
Top 20 competitors with traffic.
Columns: Domain, Traffic Share %, Traffic Value, DR, Observations.

**Section 2: Keyword Gap Opportunities**
20 high-value gaps.
Columns: Competitor Domain, Keyword Gap, Search Volume, Recommended Action.

**Section 3: Strategic Insights & Recommendations**
- **Key Highlights:** Total addressable market, Best immediate opportunities.
- **5 Key Findings:** Bulleted list.
- **5 Prioritized Recommendations:** Numbered list.


================================================================================

<!-- MERGED FROM: seo-audit -->
<!-- Original Skill Metadata:
name: seo-audit
description: Create plain-language, evidence-led SEO audit reports using the structure developed with the user. Use when asked to create, revise, or standardize an SEO audit report, SEO audit mockup, organic search audit, backlink-focused SEO audit, business-style report, or sample-modeled audit where the output must rely strictly on report data, avoid hallucinations, use a 150–200 word one-paragraph executive summary, explain organic traffic and market drivers, exclude standalone Content Quality Audit and On-Page SEO sections by default, end with a concise ordered problem/fix prioritization list instead of a roadmap, and use direct insight-and-action language.
-->

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


================================================================================

<!-- MERGED FROM: seo-competitor-analysis -->
<!-- Original Skill Metadata:
name: seo-competitor-analysis
description: Create simplified, target-first SEO organic competitor reports modeled on the approved example report style. Use for `/seo-competitor-analysis`, simplified SEO reports, organic visibility diagnosis, country traffic trend reports, Ahrefs/Semrush/Similarweb/GSC organic data analysis, page-type SEO analysis, branded versus non-branded keyword review, and backlink strategy analysis. Always generate supporting charts from normalized data before writing the report. This report is written from the perspective of someone competing against the target domain — it explains the domain's strategy, not how to improve it.
-->

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


================================================================================

<!-- MERGED FROM: seo-competitor-analysis-will -->
<!-- Original Skill Metadata:
name: seo-competitor-analysis-will
description: Create simplified, target-first SEO organic competitor reports modeled on the approved example report style. Use for `/seo-competitor-analysis-will`, simplified SEO reports, organic visibility diagnosis, country traffic trend reports, Ahrefs/Semrush/Similarweb organic data analysis, page-type SEO analysis, branded versus non-branded keyword review, and backlink strategy analysis. Always generate supporting charts from normalized data before writing the report. This report is written from the perspective of someone competing against the target domain — it dissects the domain's strategy AND opens with a direct, data-backed list of the target's SEO strategies worth manually reviewing and replicating.
-->

# SEO Competitor Analysis

Create **simplified, evidence-led SEO competitor reports** that read like the approved style example: direct, target-first, concise, and analytical. The goal is to help the reader — who is a **competitor** of the target domain — understand the target's SEO strategy, strengths, weaknesses, and dependencies, and act on them. The report does NOT advise the target domain on what to do; it dissects what the target is doing and gives the reader direct, data-backed guidance on which of the target's strategies are worth manually reviewing and replicating.

If more style guidance is needed, read `references/style_example.md` (a fictionalized AI-tool site; its clusters and numbers apply only to that vertical and must never be reused). If normalizing chart input files, read `references/data_dictionary.md`.

## Core Output Standard

Write the final deliverable as a polished Markdown report unless the user asks for another format. Use complete paragraphs, clear tables, and chart images embedded with Markdown image syntax. Use numeric reference-style citations for all tool exports, public pages, and derived analysis files.

Do not make unsupported causal claims. Use phrasing such as **"the data shows," "the available data cannot confirm," "this suggests,"** and **"this should be validated with additional data."** Avoid saying a change happened "because" of an algorithm update, content issue, or link activity unless the data directly proves it.

**Critical rule: Every action recommendation is addressed to the READER (the competitor), never to the target domain.** Do not advise the target domain on how to fix or improve its own SEO. Instead, actively give the reader direct guidance: which of the target's strategies to review manually, which to replicate, and which of the target's weaknesses to exploit. Every such recommendation MUST be derived from the data in the report and cite its evidence — no generic SEO advice that could apply to any site.

**Channel-mix gating rule: Keep the report strictly SEO-focused.** Non-organic channel data (paid search, direct, referral, social from Similarweb) serves exactly ONE purpose: to establish whether organic search is a primary traffic driver for the target domain. State the organic share of total traffic once, early in the report, then move on. Do NOT narrate paid/direct/referral trends for their own sake or let them take over sections.
- If organic search is a major traffic driver (e.g., a leading or top-two channel), confirm this in one or two sentences and proceed with the full SEO analysis.
- If the organic share of total traffic is very low (e.g., clearly a minor channel behind direct/paid), state this explicitly in the Executive Narrative as the single most important finding: studying this domain's SEO should NOT be the primary competitive action, because SEO is not what drives their growth. Then either keep the remaining SEO analysis brief or note which channel actually drives the site, without expanding into a full non-SEO channel analysis.

## Mandatory Workflow

1. **Collect source data.** This is a competitor analysis: the target's first-party data (GSC, GA4) is never available and MUST NOT be listed as a data source. Use exactly two mandatory source layers plus one supporting layer:
   - **Similarweb (mandatory, channel qualifier):** the ONLY source for channel mix (organic vs paid/direct/referral share of total traffic). Pull it FIRST to qualify whether SEO is a primary driver for this domain, per the channel-mix gating rule. Also use it for global traffic trend, country distribution, top landing pages, and top keywords.
   - **Ahrefs and/or Semrush (at least one mandatory, strategy detail):** the source for dissecting the target's detailed SEO strategy — organic keywords, page/folder traffic, country histories, branded vs non-branded, and backlinks (referring domains, anchors, destination pages). If the user specifically asks to use Ahrefs, prioritize Ahrefs and state where Semrush data is unavailable or only directional. If neither Ahrefs nor Semrush is accessible, stop and tell the user the strategy-level analysis cannot be produced.
   - **Public crawl (supporting evidence):** the target's sitemap/robots.txt and public pages, used for site architecture, language footprint, and page-template evidence — never as a traffic metric source.
2. **Normalize analysis tables.** Save CSV files in the project directory using the names in `references/data_dictionary.md` whenever possible.
3. **Generate charts before writing.** Charts MUST be produced with Manus's data visualization capability (Python plotting from normalized data files) — never hand-drawn, AI-image-generated, or copied as screenshots from third-party tools. Use the bundled script as the default renderer:

```bash
python /home/ubuntu/skills/seo-competitor-analysis-will/scripts/generate_seo_charts.py \
  --project-dir /path/to/project \
  --output-dir /path/to/project/charts \
  --title "target.com"
```

4. **Use the chart manifest.** Review `/path/to/project/charts/asset_manifest.md` and embed relevant chart snippets in the final report. If a critical chart cannot be generated, add an explicit data limitation instead of inventing values.
5. **Write the report.** Follow the report structure below. Preserve the style example's direct narrative style. Open with the "Strategies Worth Reviewing & Replicating" section, then support it with the full analysis.
6. **Validate assets before delivery.** Run:

```bash
python /home/ubuntu/skills/seo-competitor-analysis-will/scripts/validate_report_assets.py \
  --report /path/to/project/final_report.md \
  --charts-dir /path/to/project/charts
```

Use `--allow-missing-critical` only when missing critical charts are explicitly explained in the report.

## Standard Report Structure

Use this structure by default. Rename sections only when the user's request clearly requires it.

```markdown
# SEO Competitor Report: [target.com]

**Prepared by:** Manus AI  
**Date:** [Month Day, Year]  
**Primary data sources:** [Similarweb (channel mix + traffic) / Ahrefs and/or Semrush (keywords, pages, backlinks) / public crawl + sitemap]

## Strategies Worth Reviewing & Replicating

[This section MUST come first, before the Executive Narrative. Present a ranked table of the target's SEO strategies that are worth the reader's manual deep-dive and replication. Each row MUST include: the strategy (e.g., localized tool-page matrix, BOFU vs-post cluster, feature-page link building), the data evidence proving it works (traffic share, growth, clicks — with citations), 2–3 example URLs to review manually, replication difficulty (Low/Medium/High with one-line reason), and the suggested first action for the reader. Order rows by expected competitive value. Follow the table with a short paragraph flagging which target weaknesses (declining clusters, vacated demand, low-quality links) the reader can exploit, each backed by cited data. If the data shows the target's SEO is NOT worth replicating (e.g., organic is a minor channel or in broad decline), say so plainly here and state what the data suggests studying instead.]

## Executive Narrative

[Paragraph 1: **Competitor strategy teardown & traffic shift.** Directly state what the target domain is doing well and what SEO strategies are worth learning from (e.g., specific blog content types, tool matrices, backlink strategies, regional focus). **Crucially, immediately connect these strategies to the resulting traffic shift, including specific timeframes, key regions, and the exact page clusters driving the change.** This sets the stage for what the reader should take away.]

[Paragraph 2: State the main organic trend (growth or decline) and the most important strategic implication for competitors. Keep it concise, numeric, and direct. Include one sentence qualifying whether organic search is a primary traffic driver for this domain (organic share of total traffic); if organic share is very low, say plainly that this domain's growth is not SEO-driven and SEO study should not be the primary competitive action.]

[Paragraph 3: State what the target site depends on, what changed, and what this means for the competitive landscape.]

![Global organic trend](charts/global_organic_trend.png)

---

# Part 1: Organic Search Performance

## 1. Business Context and SEO Footprint
## 2. Page Type Analysis: Where Organic Demand Lands
## 3. Typical Page Structure & Content Audit
## 4. Organic Visibility by Country
## 5. Traffic Trend: Is Organic Search Growing or Declining?
## 6. Branded vs Non-Branded Search

---

# Part 2: Backlink Strategy Evidence

## 7. Backlinks: How Is [target] Building Links?

---

# Part 3: Strategic Assessment

## 8. Key Dependencies and Vulnerabilities

---

## References
```

## Section Writing Rules

Open most sections with a **bold finding sentence** that answers the section title. Follow with one or two evidence paragraphs. Keep each section focused on interpretation rather than metric listing.

For Strategies Worth Reviewing & Replicating (always the FIRST section of the report), write it only after completing the full analysis, then place it at the top. Every strategy row must trace back to a section of the report and its cited data; never list a strategy the analysis did not evidence. Keep it to the 3–7 highest-value strategies — this is a shortlist for manual deep-dive, not an inventory. Suggested first actions must be concrete and specific to the target's footprint (e.g., "manually review the target's `/id/chatgpt` and `/tw/chatgpt` templates to extract their localized page structure"), never generic advice.

For the Executive Narrative, write three compact paragraphs. The first paragraph MUST directly state what SEO strategies the target domain is executing successfully that are worth learning from (e.g., content strategy, tool matrix, link building, localization) **AND explicitly show the traffic shift these strategies caused, naming the specific timeframe, region, and most important pages**. The second paragraph should name the main organic trend and size it. The third should explain what the site currently depends on and what this means for competitors observing this domain.

For Page Type Analysis, classify landing pages by meaningful SEO intent, not just URL folder. Derive clusters from the target's actual business rather than copying clusters from the style example or past reports. **Crucially, break down content/blog pages into finer taxonomies based on search intent and funnel stage, using industry best practices:**
- **Bottom-of-Funnel (BOFU) / Commercial Intent:**
  - Comparison / vs. posts (e.g., "Product A vs Product B")
  - Alternatives posts (e.g., "Top 10 X Alternatives")
  - Review posts (e.g., "Product A Review 2026")
  - Best-of / Roundup listicles (e.g., "Best X for Y in 2026")
- **Top/Middle-of-Funnel (TOFU/MOFU) / Informational Intent:**
  - How-to / tutorial guides (e.g., "How to write a prompt")
  - Informational listicles (e.g., "10 ways to boost productivity")
  - Definitional / What-is posts (e.g., "What is generative AI")
  - Ultimate guides / pillar pages
- **Authority / Brand Building:**
  - Data / proprietary research (link-bait assets)
  - News / industry analysis / predictive trends
  - Case studies / customer stories

Other common non-blog patterns include product/tool matrices, core feature or category pages, localized pages, homepage/brand, pricing, apps/extensions, and support. **Always include Traffic Share or Click Share in the analysis table** to show which page types actually drive demand, not just which ones exist.

For Typical Page Structure & Content Audit, you MUST perform a deep-dive structural audit of **3 to 5 of the most successful page templates** (e.g., their top BOFU comparison template, their highest-traffic tool template, their pillar guide template). Do not just list metadata; you must manually browse or extract these pages and **break down their exact module structure**. For each template, provide a dedicated subsection that details:
1. The exact URL audited as the template example.
2. The structural modules from top to bottom (e.g., "H1 + Hero Tool Embed -> How-to Steps -> Comparison Table -> FAQ schema block -> CTA").
3. How they organize the content (e.g., "They place the interactive tool above the fold, pushing all SEO text below to prioritize user engagement").
4. Why this template works and what the reader should copy from it.

For Backlinks, answer whether the pattern looks homepage/brand-led, PR-led, SEO-page-led, or low-quality/manipulative. Separate link quantity from link quality. Use anchor mix and destination page type charts whenever data exists. **If detailed backlink data (like anchor text or destination pages) is unavailable due to tool limits, you MUST explicitly state this as a Data Limitation in the report.**

For Country Visibility, compare country-level traffic and keyword footprint where possible. If only a current snapshot exists, do not imply trend. If trend data exists, state whether each priority market ended higher or lower than it started.

For Branded vs Non-Branded Search, report both keyword count and click/traffic weight. The key question is whether non-branded breadth has become non-branded click strength.

For Key Dependencies and Vulnerabilities (Strategic Assessment), do not just list bullet points of vulnerabilities. This is the culminating section of the report. Write a deep, cohesive strategic evaluation of their entire SEO moat. Address:
1. **The Scale of Investment:** Infer the SEO team and resource investment required to maintain their footprint (e.g., is this a massive editorial operation with high content costs, or a lean programmatic/tool-led approach?).
2. **The Defensibility of the Moat:** Which of their traffic pillars are truly defensible (e.g., proprietary data, massive brand PR) versus highly fragile (e.g., thin programmatic pages, low-quality link building)?
3. **The Displacement Path:** Synthesize the vulnerabilities into a clear displacement strategy. If the reader wants to beat them, what is the exact sequence of attacks (e.g., "Attack their unbranded BOFU blog cluster first because it has high intent but low link defense, then build a better localized tool matrix").
Frame this as high-level strategic intelligence for the competitor's leadership. Recommendations here are addressed to the reader only, never to the target domain.

## Mandatory Charts and Graphs

Generate and embed every chart supported by the available data. The report should normally include at least three charts, and stronger reports include five or more.

**All charts MUST be generated with Manus's data visualization capability**: render them programmatically (the bundled `generate_seo_charts.py`, or matplotlib/plotly for custom charts) from the normalized CSVs, and save them as image files before embedding. Do NOT use AI image generation for charts, and do NOT paste screenshots from Similarweb/Semrush/Ahrefs dashboards as substitutes — every number shown in a chart must trace back to a normalized data file in the project directory.

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
3a. The report qualifies whether organic search is a primary traffic driver, and non-organic channel data (paid/direct/referral) appears only for this qualification purpose — never as standalone narrative.
4. All major claims are backed by citations.
5. Charts were generated with Manus's data visualization capability (`generate_seo_charts.py` or programmatic matplotlib/plotly rendering from normalized CSVs) where source data exists; no tool screenshots or AI-generated chart images are used.
6. The final report passes `validate_report_assets.py`, or any missing chart categories are explicitly documented.
7. **The report opens with the "Strategies Worth Reviewing & Replicating" section**, placed before the Executive Narrative, with every strategy row backed by cited data, example URLs, replication difficulty, and a suggested first action for the reader.
8. All action guidance is addressed to the reader (the competitor) and derived from report data; no advice is directed at the target domain, and no generic uncited SEO advice appears.
9. Page-type clusters are derived from the target's actual business, not copied from the style example or earlier reports.