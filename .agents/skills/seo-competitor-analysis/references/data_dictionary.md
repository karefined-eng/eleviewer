# SEO Competitor V3 Normalized Data Dictionary

Use this reference when preparing data for `scripts/generate_seo_charts.py`. The script is tolerant of alternate column names, but future reports are most consistent when these exact filenames and columns are used.

## Required or Strongly Preferred Files

| File | Purpose | Recommended columns |
|---|---|---|
| `traffic_trend.csv` | Global organic search trend chart immediately after the Executive Narrative. | `month`, `organic_visits`, optional `paid_visits` |
| `country_traffic.csv` | Top country bar chart and country visibility table. | `country`, `organic_traffic`, optional `share`, `start_traffic`, `end_traffic`, `keyword_change` |
| `country_trend.csv` | Multi-country trend chart when country-level history exists. | `month`, `country`, `organic_traffic`, optional `organic_keywords` |
| `page_type_summary.csv` | Page Type Analysis chart and table. | `page_type`, `clicks` or `organic_traffic`, optional `keywords`, `share` |
| `top_pages.csv` | Top landing-page evidence chart and content-matrix table. | `landing_page`, `page_type`, `clicks` or `organic_traffic`, optional `keywords`, `top_keyword` |
| `branded_nonbranded.csv` | Branded vs non-branded comparison chart. | `segment`, `keywords`, `clicks` or `organic_traffic` |

## Optional but Recommended Files

| File | Purpose | Recommended columns |
|---|---|---|
| `keyword_sample.csv` | Builds branded/non-branded summary if `branded_nonbranded.csv` is unavailable. | `keyword`, `brand_type`, `clicks` or `traffic`, optional `country`, `landing_page`, `position` |
| `page_losses.csv` | Largest page-loss chart for decline reports. | `landing_page`, `start_traffic`, `end_traffic`, optional `traffic_loss` |
| `keyword_losses.csv` | Largest keyword-loss chart for decline reports. | `keyword`, `start_traffic`, `end_traffic`, optional `traffic_loss`, `landing_page` |
| `backlink_anchor_mix.csv` | Backlink anchor-type chart. | `anchor_type`, `count` |
| `backlink_destination_mix.csv` | Backlink destination page-type chart. | `page_type`, `count` or `rows` |

## Normalization Rules

Use the last six months by default unless the user specifies another date range. Preserve the tool source in filenames or reference notes where possible. Do not merge Semrush, Ahrefs, Similarweb, GSC, and GA4 metrics into one number unless the report clearly labels the result as directional and explains how it was calculated.

Every row used for a chart should also support a report statement. If a chart cannot be generated because the CSV is missing or lacks required columns, write a limitation in the report rather than inventing a metric.
