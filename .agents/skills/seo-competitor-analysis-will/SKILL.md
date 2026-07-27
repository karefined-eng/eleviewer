---
name: seo-competitor-analysis-will
description: Create simplified, target-first SEO organic competitor reports modeled on the approved example report style. Use for `/seo-competitor-analysis-will`, simplified SEO reports, organic visibility diagnosis, country traffic trend reports, Ahrefs/Semrush/Similarweb organic data analysis, page-type SEO analysis, branded versus non-branded keyword review, and backlink strategy analysis. Always generate supporting charts from normalized data before writing the report. This report is written from the perspective of someone competing against the target domain — it dissects the domain's strategy AND opens with a direct, data-backed list of the target's SEO strategies worth manually reviewing and replicating.
---

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
