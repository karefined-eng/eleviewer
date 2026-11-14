# Learning Proposal

**Date:** 2025-10-27

## Summary

This proposal captures three environment constraints learned during research and data viz analysis work, plus a conceptual framework the user requested incorporated.

---

## Candidate Learning 1: WebFetch Source Reliability Pattern

| Field | Value |
|---|---|
| **Trigger** | Research tasks requiring data from external websites via WebFetch |
| **Invariant** | Never assume a given URL will return usable content; always have fallback sources ready |
| **Evidence** | Session research for "data viz tool usage" yielded 404/403 from: Stack Overflow Survey (2024 subpages), JetBrains Survey, Tableau blog, DataWrapper docs, Observable docs sub-pages, KDnuggets survey |

### Classification
**Rule** — Can be satisfied with "Always validate WebFetch results and prepare fallback sources"

### Scope
**Workspace** — Specific to this repository's research workflow

### Proposed addition to AGENTS.md

```
## WebFetch Source Reliability Pattern

**Environment Trap:** WebFetch returns variable reliability across sources:
- Sub-pages of surveys often return 404 (URL structure changes)
- Enterprise marketing sites block automated access (403)
- Academic/blog sites may require authentication or be ephemeral

**Workflow guardrail:** When primary source fails:
1. Identify alternative authoritative source (Wikipedia, official docs, GitHub README)
2. If no alternative exists, state clearly: "Source unavailable due to [404/403/auth]"
3. Do not attempt to synthesize statistics from partial data without explicit user request
```

---

## Candidate Learning 2: Google Trends Endpoint Rate Limiting

| Field | Value |
|---|---|
| **Trigger** | Direct API/URL fetch of Google Trends data via WebFetch |
| **Invariant** | Google Trends endpoints return HTTP 429 after limited requests; plan for this |
| **Evidence** | Session: `trends.google.com/trends/explore?date=today%205-y&q=information%20is%20beautiful,...` returned HTTP 429 |

### Classification
**Rule** — "If Google Trends data is explicitly requested, use browser-based verification instead of API"

### Scope
**Workspace** — Affects any research involving trend analysis

### Proposed addition to AGENTS.md

```
## Google Trends Access

**Environment Fact:** Google Trends API endpoints rate-limit heavily. WebFetch to Google Trends URLs returns HTTP 429 "Too Many Requests" almost immediately.

**Alternative workflow:**
- Direct user verification: Google Trends website in browser
- Indirect via search console/analytics if available to user
- Document this limitation when findings cannot be fetched
```

---

## Candidate Learning 3: Research Transparency When Data Sources Fail

| Field | Value |
|---|---|
| **Trigger** | Research task where direct data is unavailable |
| **Invariant** | Be explicit about what data could not be fetched and why, rather than fabricating |
| **Evidence** | Session: Provided analytical answer about data viz trends without Google Trends numbers, flagged "Google Trends API rate-limited", did not fabricate search volume data |

### Classification
**Rule** — "When data sources fail, document limitations; do not fabricate"

### Scope
**Workspace** — Research methodology

### Proposed addition to AGENTS.md

```
## Research Transparency Policy

When requested data is unavailable:
1. Attempt fetch via available tools (WebFetch, WebSearch if enabled)
2. If unavailable due to rate limits or 404/403, state the specific error
3. Provide analytical answer based on available sources, marked as "[Analytical based on available sources]"
4. Never fabricate numerical data; use phrases like "cannot fetch exact numbers" or "data unavailable via available channels"
```

---

## Candidate Learning 4: Anti-Stterility Law / Metaphorical Translation Framework

| Field | Value |
|---|---|
| **Trigger** | User requests for creative data visualization approaches beyond standard charts |
| **Invariant** | Data visualizations should map to physical metaphors, not generic shapes |
| **Evidence** | User attachment describing "THE METAPHORICAL TRANSLATION ENGINE Anti-Sterility Law" with rules for physical avatars (Carbon→organic blobs, Time→branching structures, Network→gravity wells) |

### Classification
**Skill** — Multi-step creative decision framework requiring ordered steps

### Proposed location
`skills/metaphorical-translation/SKILL.md`

### Proposed skill description (draft text)

```markdown
# Metaphorical Translation Engine — Anti-Stterility Law

> Data is physical; context has weight. Map primitive shapes to dataset metaphors.

## The Anti-Stterility Law
You are forbidden from generating generic rectangles, uniform circles, or isolated coordinate nodes unless explicitly ordered. Data visualizations must use the physical avatar of the data.

## Physical Avatars

| Data Phenomenon | Physical Avatar |
|---|---|
| Carbon / Pollution / Debt | Heavy, pooling, sinking shapes (gravity-weighted blobs) |
| Time / Growth | Continuous, splitting, branching organic structures (river topography) |
| Network / Community | Gravity wells, planetary orbits |

## The 3 Laws of Semantic Layout
1. Form Follows Concept — Typography becomes structure for text data
2. Contextual Framing — Custom paths frame narrative
3. Proportional Weighting — Overlapping translucent forms show scale

## Execution
Generate bespoke nodes that respect the avatar mapping, not library defaults.
```

---

## Proposed Actions

1. **Update AGENTS.md** with WebFetch reliability, Google Trends, and research transparency rules
2. **Create new skill** `skills/metaphorical-translation/SKILL.md` for the Anti-Stterility Law framework

---

## Awaiting Approval

Please approve:
- [x] Add the three environment rules to AGENTS.md
- [x] Create the new Metaphorical Translation Engine skill
- [x] Combination of both

---

## Outome Applied ✅

### Changes Applied

1. **AGENTS.md** — Added three new sections:
   - Updated table with three new environment traps (WebFetch unreliability, Google Trends 429, Research transparency)
   - New "WebFetch Source Reliability Pattern" subsection with workflow guardrails
   - New "Google Trends Access" subsection with alternative workflow
   - New "Research Transparency Policy" subsection

2. **Created `skills/metaphorical-translation/SKILL.md`** — New skill implementing:
   - Anti-Stterility Law framework
   - Physical Avatars table (7 data phenomena → visual forms)
   - 3 Laws of Semantic Layout
   - Execution framework with step-by-step guidance
   - Creativity score scaling
   - Success/Failure mode documentation

### Verification

- AGENTS.md: New content appears at lines 56–87
- Skill file: Created at `/skills/metaphorical-translation/SKILL.md` with valid frontmatter and 189 lines