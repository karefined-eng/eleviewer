# SEO Competitor Report: example-ai.com

**Prepared by:** Manus AI  
**Date:** 2026-06-09  
**Target domain:** [example-ai.com](https://example-ai.com/)  
**Primary data sources:** Semrush Domain Analytics exports, Semrush keyword exports for the United States, Italy, Brazil, and Indonesia, Similarweb website-analysis exports, public `robots.txt`, extracted sitemap samples, and observable public-site evidence. Third-party metrics are estimates and should be used as directional data, not first-party analytics data.[1] [2] [3] [4] [5]

> **Usage note:** This file is a style example for SKILL.md. It is written about a fictionalized AI-tool site (`example-ai.com`); its page-type clusters, numbers, and URLs apply only to that vertical. When writing a new report, derive clusters from the target's actual business and never reuse any data from this example. The report opens with a direct, data-backed shortlist of the target's strategies worth manually reviewing and replicating, addressed to the reader (the competitor). It never gives the target domain recommendations — all action guidance is for the reader. Every new report must keep this same competitive-intelligence perspective.

---

## Strategies Worth Reviewing & Replicating

**Three of example-ai.com's strategies justify a manual deep-dive, and two of its weaknesses are directly exploitable.** The shortlist below is ranked by expected competitive value; every row traces to the analysis sections that follow.

| Rank | Strategy | Data evidence | Example URLs to review manually | Replication difficulty | Suggested first action |
| --- | --- | --- | --- | --- | --- |
| 1 | Localized model/chat tool-page matrix | The cluster drives 46.7% of sampled organic clicks; `/ar/chatgpt` alone takes 29,814 May clicks.[2] [5] | `example-ai.com/ar/chatgpt`, `example-ai.com/tw/chatgpt`, `example-ai.com/it/chatgpt` | Medium — template is simple, but 15+ language localization requires sustained effort | Manually review the three URLs to extract the page template (H1 pattern, tool embed, FAQ block, internal links), then map which of these localized SERPs are weakest. |
| 2 | BOFU comparison/alternatives blog cluster | `/blog/vs-` and `/blog/alternatives-to-` posts capture 3.7% of clicks with high commercial intent, part of the 49.2% BOFU+tool click shift in Brazil, Indonesia, and Italy.[2] [5] [6] | `example-ai.com/blog/vs-…`, `example-ai.com/blog/alternatives-to-…` | Low — standard editorial format with a clear template | Review 3–5 of their vs-posts to extract the comparison table structure and target-keyword pattern, then build the same cluster for your own product's evaluation queries. |
| 3 | Feature-page-focused link building | Model/chat pages received 4,276 backlink rows and AI writing pages 2,923 — links go to ranking pages, not just the homepage.[6] [8] | `example-ai.com/chatgpt`, `example-ai.com/ai-writer/` | Medium — requires outreach capacity, but the deep-link targeting logic is copyable | Pull their newest referring domains for these two pages and review which link sources are legitimate and reachable for your own feature pages. |

**Two exposures are directly actionable for the reader.** First, the Indonesian translation and detector-bypass demand clusters have already collapsed (`translate arab indonesia` fell from 16,817 to 0), leaving vacated SERP positions that can be claimed.[7] Second, 465 of the sampled anchors look manipulative, so the durability of their link-driven rankings carries a discount — quality link building into the same destinations is a viable displacement path.[8]

---

## Executive Narrative

**What competitors should learn from example-ai.com:** The domain has successfully built a high-leverage SEO footprint by combining a **scalable tool matrix** (deploying model/chat access pages across 15+ languages) with a **targeted comparison blog strategy**. Instead of generic informational content, their blog aggressively targets bottom-of-funnel users with "Product A vs Product B" comparison posts and "Top 10" listicles. Furthermore, their link-building strategy is highly pragmatic, driving links directly into non-branded feature pages rather than just the homepage. **This strategy drove a massive traffic shift between January and April 2026: while their US homepage traffic flatlined, their localized `/chatgpt` tool pages and BOFU `/blog/vs-` comparison pages surged to capture 49.2% of their total organic click share across Brazil, Indonesia, and Italy.**[1] [2] [5] [6]

**Despite these strong structural foundations, example-ai.com's organic visibility is currently declining.** Based on the last six months of data, Similarweb's global desktop organic search estimate fell from **601,535 visits in December 2025 to 296,206 in May 2026**, a **50.8% decline**.[2] Semrush country histories show the same decline across tracked markets: the United States fell **80.0%**, Brazil **56.9%**, Italy **59.0%**, and Indonesia **43.7%** from the first to the last six-month snapshot.[1] The main finding is clear: example-ai.com lost organic visibility because ranking keyword coverage shrank across major country databases, not because of one isolated country issue. Tracked-country keyword counts fell between **66.7% and 88.5%** over the same period.[1]

**The current SEO footprint depends heavily on non-branded utility pages and brand demand.** The biggest current organic traffic drivers are **model/chat access pages** with **95,127 May clicks**, **AI detection/humanizer pages** with **36,697 clicks**, and **homepage/brand pages** with **34,854 clicks** in the Similarweb landing-page sample.[2] Similarweb's top-300 keyword sample has **251 non-branded keywords** and **49 branded keywords**, but branded terms still drive more clicks: **243,404 branded clicks** versus **202,110 non-branded clicks**.[2] The backlink finding is that example-ai.com is using a **high-volume, SEO-led, feature-page-focused** link-building strategy, but many new referring domains are low-authority — a quality weakness worth noting when assessing the durability of its authority moat.[6] [8]

![example-ai.com global estimated organic search traffic trend](charts/global_organic_trend.png)

---

# Part 1: What Is Happening With example-ai.com?

## 1. Business Context and Current SEO Strategy

**example-ai.com's SEO strategy is multilingual, utility-led, and template-driven.** The site builds around AI model access, AI writing, AI detection, AI media, homework help, apps, and localized pages.[3] The public navigation includes Chat, AI Image, AI Video, Discover, Bots, Other Apps, AI Writer, Detector Bypass, AI Essay Writer, AI Article Writer, Browser Extension, Desktop App, and AI Homework Helper.[3] The public `robots.txt` also shows localized sitemap paths for many language folders, including Italian, Portuguese, Indonesian, Spanish, French, German, Japanese, Korean, Russian, Arabic, and Dutch.[4] This shows an international SEO strategy, not a homepage-only strategy.

## 2. Page Type Analysis: Where Organic Demand Lands

**Organic traffic is concentrated in a few page types even though the site has many content types.** Similarweb's May 2026 landing-page sample shows that **model/chat access pages drive 46.7%** of sampled organic clicks, **AI detection/humanizer pages drive 18.0%**, and **homepage/brand pages drive 17.1%**.[2] Other page types exist, but they currently contribute much less traffic.[2] [5]

| Page type | URL pattern | Traffic share | What it means |
| --- | --- | --- | --- |
| Model/chat access pages | `/chatgpt`, `/gemini`, `/claude`, `/c/`, localized variants | 46.7% | This is the main organic traffic engine and the target's most important defensive asset.[2] [5] |
| AI detection / humanizer pages | `bypass.example-ai.com`, detector-bypass variants | 18.0% | A major traffic contributor that also appears in the six-month loss analysis — both a pillar and an exposure.[2] [7] |
| Homepage / brand | `example-ai.com`, localized home roots | 17.1% | Brand demand remains important, but it is not the only traffic source.[2] [5] |
| Other landing pages | Mixed tool, localized, and miscellaneous URLs | 4.7% | The long tail exists, but it currently lacks keyword evidence to back its contribution.[2] |
| BOFU: Comparison / vs. posts | `/blog/vs-` | 2.5% | Captures bottom-of-funnel evaluation intent.[2] [5] |
| BOFU: Alternatives listicles | `/blog/alternatives-to-` | 1.2% | High-conversion intent for users looking to switch tools.[2] [5] |
| TOFU: Informational listicles | `/blog/top-` | 1.0% | Drives broad awareness at the top of the funnel.[2] [5] |
| TOFU: How-to / tutorial guides | `/blog/how-to-` | 0.5% | Educational content, low direct commercial traffic share.[2] [5] |
| Authority: Data / proprietary research | `/research/` | 0.2% | Acts primarily as a link-bait asset to attract backlinks, not direct traffic.[2] [5] [6] |
| AI writing utility pages | `/ai-writer/`, `/ai-article-writer/`, `/translate` | 4.0% | Writing tools are visible but secondary in current sampled traffic.[2] [5] |
| AI media generation pages | `/ai-video`, `/ai-image`, `/text-to-video`, `/image-to-video`, `/video-effects/`, `/photo-effects/` | 2.2% | AI media pages exist at scale, but current measured traffic is small.[2] [5] |
| Commercial / company pages | Pricing, account, product, and company-support pages | 1.9% | These pages support conversion and trust more than acquisition.[2] |
| Homework / education pages | `/ai-homework-helper/`, math and science helpers | 1.2% | Education pages are present but not a leading traffic category.[1] [2] [5] |
| Extension / app pages | Browser extension and app-related URLs | 0.1% | App and extension pages are visible but have minimal sampled organic traffic.[2] |

**Model/chat pages are the most important page group.** The top model/chat page in the Similarweb sample is **`example-ai.com/ar/chatgpt`** with **29,814 May organic clicks**, followed by **`example-ai.com/tw/chatgpt`** with **8,599**, **`example-ai.com/claude`** with **8,386**, **`example-ai.com/it/chatgpt`** with **4,473**, and **`example-ai.com/es/claude`** with **4,419**.[2] This shows that localized ChatGPT and Claude pages are a major part of example-ai.com's current SEO footprint.

**The competitive takeaway is that example-ai.com's traffic lifeline is concentrated in a few proven clusters.** Model/chat pages, AI detection/humanizer pages, and brand/navigation pages form its defensive core, while the remaining page types are widely deployed but capture little traffic — its template expansion has not converted into visibility everywhere.[2] [5]

![Similarweb organic clicks by landing-page type](charts/page_type_traffic_bar.png)

## 3. Typical Page Structure & Content Audit

**The target uses highly templated, interactive modules rather than text-heavy articles to capture tool intent.** We manually audited three of their most successful page templates to extract their structure.

### Template 1: Localized Model/Chat Access Page
* **Audited URL:** `example-ai.com/ar/chatgpt`
* **Module Structure:** H1 (Localized Keyword) -> Interactive Chat Interface (Above the fold) -> "How to use" 3-step graphic -> H2 Comparison Table (ChatGPT vs Claude) -> FAQ Schema Block -> Bottom Sticky CTA.
* **Content Organization:** They place the interactive tool immediately below the H1, pushing all SEO text below the fold. The text itself is heavily structured into tables and lists rather than paragraphs.
* **What to copy:** The immediate time-to-value. Do not force users to read 500 words before seeing the tool. The FAQ block uses valid JSON-LD schema to capture "People Also Ask" rich snippets.

### Template 2: BOFU Comparison Blog Post
* **Audited URL:** `example-ai.com/blog/vs-jasper-ai`
* **Module Structure:** H1 -> Quick Verdict Box -> Feature-by-Feature Comparison Matrix -> Pricing Breakdown -> Pros/Cons Lists -> H2 "Why Choose Us" -> CTA.
* **Content Organization:** The "Quick Verdict" box at the very top answers the search intent instantly. The comparison matrix uses custom CSS icons (checkmarks/crosses) that keep the reader scanning.
* **What to copy:** The "Quick Verdict" module and the highly visual comparison matrix. Their posts rank because they are formatted for scannability, not word count.

### Template 3: AI Detection / Humanizer Tool
* **Audited URL:** `bypass.example-ai.com/`
* **Module Structure:** H1 -> Split-screen Input/Output Box -> "Supported Detectors" Logo Banner -> H2 Use Cases -> User Reviews -> SEO Content Block.
* **Content Organization:** The logo banner of "Supported Detectors" (Turnitin, GPTZero, etc.) acts as massive social proof and captures secondary long-tail keywords simultaneously.
* **What to copy:** The logo banner pattern. It builds trust instantly while naturally injecting the names of competing products they want to rank for.

## 4. Organic Visibility: Where Search Demand Comes From

**In the last six months, the United States drove the highest tracked organic traffic, followed by Indonesia, Brazil, and Italy.** These four Semrush country histories do not represent the full global market, but they show how major tracked markets moved over the same period.[1]

### Top Countries With Highest Organic Traffic

**The six-month trend shows broad country-level decline.** The current top-country snapshot may show a different leading market at one point in time, but the six-month view is better for explaining the decline.[1]

| Rank | Country | Six-month Semrush organic traffic sum | Start traffic | End traffic | Six-month change | Keyword change | Top traffic keywords in available sample | Top landing pages in available sample | Strongest topics | Branded/non-branded mix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | United States | 206,503 | 69,980 | 13,982 | -55,998 (-80.0%) | -88.5% | `example ai`, `example-ai.com`, `claude ai`, `claude` | Homepage, `/claude`, `/chatgpt`, `bypass.example-ai.com/` | AI model/chat access, brand/navigation, AI writing and translation | 38.0% branded and 56.8% non-branded by Semrush top-300 sample traffic.[1] |
| 2 | Indonesia | 185,670 | 82,719 | 46,606 | -36,113 (-43.7%) | -85.6% | `cht gpt`, `gemini`, `chat gpt`, `pemecah soal matematika`, `gpt` | `/id/chatgpt`, `/id/gemini`, `/id/ai-homework-helper/math-ai`, `/id/gpt-4o` | AI model/chat access, other non-branded discovery, AI writing/translation | 1.1% branded and 97.5% non-branded by Semrush top-300 sample traffic.[1] |
| 3 | Brazil | 176,631 | 39,118 | 16,875 | -22,243 (-56.9%) | -66.7% | `gemini`, `bypass example ai`, `example ai` | `/pt/gemini`, `bypass.example-ai.com/pt`, `/pt/chatgpt`, `bypass.example-ai.com/` | Brand/navigation, AI model/chat access, AI detection/bypass | 47.2% branded and 49.2% non-branded by Semrush top-300 sample traffic.[1] |
| 4 | Italy | 125,807 | 33,947 | 13,918 | -20,029 (-59.0%) | -76.4% | `chat gpt`, `chatgpt`, `example ai`, `risolutore matematico` | `/it/chatgpt`, homepage, `/it/ai-homework-helper/math-ai`, `/it` | AI model/chat access, brand/navigation, other discovery | 9.3% branded and 89.1% non-branded by Semrush top-300 sample traffic.[1] |

**The United States is the largest six-month tracked market, and its traffic structure is a mix of branded and non-branded demand.** The US sample contains brand terms such as `example ai`, plus non-branded model terms such as `claude ai` and `claude`.[1] The top US pages include the homepage, `/claude`, `/chatgpt`, and `bypass.example-ai.com/`, which shows that the target's US visibility depends on both brand demand and non-branded model/bypass pages — and both fronts are contracting.[1]

**The US exposure is not desktop-only.** The current Semrush country snapshot shows **16,759** estimated desktop organic visits and **12,352** estimated mobile organic visits, or a directional split of **57.6% desktop** and **42.4% mobile**.[1] This means the target's US visibility loss spans both desktop and mobile SERPs.

| Highest six-month tracked country | Desktop share | Mobile share | Data source | Competitive reading |
| --- | --- | --- | --- | --- |
| United States | 57.6% | 42.4% | Semrush `us` and `mobile-us` current database rows | The target's US exposure covers desktop and mobile alike; there is no single-device moat.[1] |

## 5. Traffic Trend: Is example-ai.com Growing?

**example-ai.com is not growing; estimated global organic search traffic is down 50.8%.** Similarweb shows global desktop organic search falling from **601,535 visits in December 2025** to **296,206 visits in May 2026**, a loss of **305,329 visits**.[2] The largest decline happened from December to February, traffic stabilized in March and April, and May declined again.[2]

| Month | Similarweb global estimated organic search visits | Paid search visits | Month-over-month reading | Evidence-backed diagnosis |
| --- | --- | --- | --- | --- |
| Dec 2025 | 601,535 | 82,753 | Baseline | Organic search was much larger than paid search at the start of the period.[2] |
| Jan 2026 | 477,551 | 15,323 | Down 20.6% | Organic search and paid search both declined.[2] |
| Feb 2026 | 360,284 | 4,629 | Down 24.6% | The early organic decline continued.[2] |
| Mar 2026 | 359,812 | 2,929 | Flat | Organic search stabilized after the early drop.[2] |
| Apr 2026 | 353,447 | 1,068 | Slightly down | Organic traffic stayed close to the March level.[2] |
| May 2026 | 296,206 | 9,683 | Down 16.2% | Organic traffic fell again at the end of the period.[2] |

**The largest page losses point to Indonesian translation pages and detector-bypass pages.** These pages explain a large part of the tracked decline and are the clearest evidence of where the target is losing ground.[7]

| Largest tracked-country page losses | Start estimated traffic | End estimated traffic | Estimated traffic loss | What the loss indicates |
| --- | --- | --- | --- | --- |
| `https://example-ai.com/id/translate/arabic-indonesian` | 23,070 | 0 | 23,070 | Visibility for this page disappeared entirely, indicating a drastic change in indexing, ranking, or page replacement.[7] |
| `https://bypass.example-ai.com/` | 25,881 | 3,799 | 22,082 | The bypass product root lost most of its traffic, indicating intensified SERP competition or shifting trust signals.[7] |
| `https://bypass.example-ai.com/it` | 6,385 | 198 | 6,188 | The Italian localized bypass page collapsed to near zero, exposing the fragility of its localized templates.[7] |

**The largest keyword losses also point to Indonesian translation demand and detector-bypass demand.** These clusters carry the heaviest weight in the target's decline.[7]

| Largest tracked-country keyword losses | Start estimated traffic | End estimated traffic | Estimated traffic loss | What the loss indicates |
| --- | --- | --- | --- | --- |
| `translate arab indonesia` | 16,817 | 0 | 16,817 | Indonesian translation visibility was wiped out, likely displaced by competitors or SERP changes.[7] |
| `example bypass` | 13,150 | 537 | 12,613 | Even the brand-flavored bypass query fell sharply, indicating that demand or visibility for this product line itself is contracting.[7] |
| `bahasa indonesia ke bahasa inggris` | 4,045 | 0 | 4,045 | Indonesian translation terms form a distinct demand cluster the target has already lost.[7] |

**The decline is market-wide across the tracked countries.** Semrush shows lower traffic and fewer ranking keywords at the end of the six-month window in the United States, Indonesia, Brazil, and Italy.[1] The largest absolute traffic decline came from the United States (**-55,998**), followed by Indonesia (**-36,113**), Brazil (**-22,243**), and Italy (**-20,029**).[1]

**The likely issue is visibility loss, not one confirmed algorithm or technical cause.** The data does not prove a single cause such as an algorithm update, technical problem, or demand shift. It does show that example-ai.com lost organic visibility while ranking keyword footprints shrank sharply, with the largest measured losses concentrated in Indonesian translation pages and detector-bypass pages.[1] [7]

![Semrush organic traffic by country trend](charts/country_trend.png)

---

## 6. Branded vs Non-Branded Search

**example-ai.com has more non-branded keywords, but branded keywords drive more clicks.** In Similarweb's March–May 2026 top-300 organic keyword export, **251 keywords are non-branded** and **49 are branded**.[2] By summed Similarweb clicks, branded keywords drive **243,404 clicks**, while non-branded keywords drive **202,110 clicks**.[2] This means example-ai.com has broad non-branded SEO coverage, but brand/navigation demand is still stronger by click volume.

**The question is not whether example-ai.com targets non-branded demand; it already does.** The question is whether its non-branded traffic is durable and high-quality. Italy is **89.1% non-branded**, Indonesia is **97.5% non-branded**, the United States is **56.8% non-branded**, and Brazil is nearly balanced at **49.2% non-branded versus 47.2% branded** in the Semrush top-300 sample.[1] For a competitor, the key reading is that example-ai.com's non-branded keyword breadth has not yet converted into proportional non-branded click strength — that gap is the contested space across its model/chat, bypass, writing, homework, and AI media clusters.[1] [2] [5]

---

# Part 2: Backlink Strategy Evidence

## 7. Backlinks: Is example-ai.com Building Links for SEO Growth?

**Yes. example-ai.com is actively building backlinks, and the pattern looks SEO-team-led rather than PR-led.** Links point into the pages the target wants to rank, not only to the homepage or brand pages. The newest page-level sample shows **184 non-branded/descriptive anchors** versus **169 branded anchors**, plus **75 generic/CTA anchors**, **107 empty or unknown anchors**, and **465 manipulative or spam-like anchors**.[8] Destination pages also show SEO targeting: model/chat access pages received **4,276 backlink rows**, AI writing pages received **2,923**, AI media pages received **2,157**, AI detection/humanizer pages received **708**, and the homepage received **2,634**.[8] Some high-authority PR links exist, but the main pattern is deep linking into tool and feature pages.[6] [8]

**The weakness of this backlink profile is quality, not volume.** The profile helps when relevant, credible sources support its priority tool, model, writing, media, and detection pages, and it is diluted when low-quality, manipulative, or irrelevant links inflate volume without improving trust. The 465 manipulative-looking anchors show that example-ai.com's authority growth carries meaningful quality exposure — a signal competitors can weigh when assessing the durability of its rankings.[6] [8]

---

# Part 3: Strategic Assessment

## 8. Key Dependencies and Vulnerabilities

**example-ai.com's core dependency is a small set of page clusters plus a wide multilingual template footprint, and its core vulnerability is a broad visibility contraction.** Global estimated organic search traffic declined, tracked-country keyword footprints contracted, and the largest measured losses sit in Indonesian translation pages and detector-bypass pages.[1] [2] [7]

### The Scale of Investment
This is not a massive editorial operation; it is a **lean, programmatic, engineering-led SEO team**. They are not spending millions on writers to produce thousands of blog posts. Instead, their investment goes into building robust, interactive web-app templates (the Chat interface, the Humanizer tool) and deploying them across 15+ languages via a programmatic routing matrix. Their content cost is low, but their technical SEO and template engineering investment is very high.

### The Defensibility of the Moat
* **Defensible Pillars:** Their localized model/chat matrix is highly defensible. They have secured top positions in markets like Brazil and Italy because the actual tool works in those languages, not just because the page is translated. This requires real product integration.
* **Fragile Pillars:** Their bypass/humanizer cluster is highly fragile. The data shows this cluster is already bleeding traffic heavily (`bypass.example-ai.com/it` fell from 6K to near zero).[7] This indicates that search engines are either penalizing these specific thin-content tools or competitors are easily outranking them. Furthermore, their link profile contains significant noise (465 manipulative anchors), meaning their domain authority is partly built on a house of cards.[8]

### The Displacement Path
If a competitor wants to beat example-ai.com, the data dictates this exact sequence of attacks:
1. **Attack the Bypass/Humanizer cluster first.** This is their second-largest traffic pillar but it is actively retreating and highly fragile. Build a better, faster Humanizer tool, copy their "Supported Detectors" logo banner template, and hit it with higher-quality PR backlinks. You are pushing against an open door here.
2. **Steal the BOFU comparison traffic.** They only have a few `/blog/vs-` posts, but these drive high-intent clicks. This is the easiest content to replicate manually. Write 10 comparison posts using their "Quick Verdict" module structure and capture the evaluation traffic they haven't targeted yet.
3. **Flank the localized Chat matrix.** Do not attack their US homepage. Instead, identify the specific non-English markets where their traffic is declining (e.g., Indonesia) and launch localized, culturally adapted tool pages to fill the vacuum they are leaving behind.

---

## References

[1]: tables/semrush_top20_countries.csv "Semrush Domain Analytics country, keyword, and rank-history exports for example-ai.com, collected and normalized 2026-06-09"

[2]: tables/similarweb_total_visits_6m.csv "Similarweb website-analysis exports for example-ai.com, including total visits, traffic sources, countries, keywords, and landing pages, collected and normalized 2026-06-09"

[3]: https://example-ai.com/ "example-ai.com homepage public navigation, extracted 2026-06-09"

[4]: https://example-ai.com/robots.txt "example-ai.com robots.txt and sitemap declarations, extracted 2026-06-09"

[5]: tables/sitemap_extracted_urls_classified.csv "Extracted example-ai.com sitemap sample classified by page type and language prefix, collected 2026-06-09"

[6]: recent_backlinks/section_6_recent_backlink_summary.md "Semrush Backlinks API overview, backlinks, referring-domain, and anchor exports for example-ai.com; recent referring-domain export collected 2026-06-09 and analyzed for the last-six-month first-seen window"

[7]: traffic_loss_analysis/six_month_page_keyword_loss_digest.md "Semrush historical movement analysis for example-ai.com tracked-country page and keyword losses, generated 2026-06-09"

[8]: latest_user_revision_analysis.md "Semrush page-level backlink sample analysis for example-ai.com anchor mix, destination page type, country focus, and May 2026 target-page growth, generated 2026-06-09"
