---
name: keyword-research
description: Conduct keyword research and generate a strictly formatted three-tab Excel workbook containing a Topic Cluster Summary, 300 priority keywords, and a competitor gap analysis. Use when the user asks to "conduct keyword research for [keyword]", "create a keyword research excel", or provides a keyword and needs a structured priority list and competitor gaps.
---

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
