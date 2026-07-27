---
name: eleviewer-seo-geo
description: Guidelines for Search Engine Optimization (SEO) and Generative Engine Optimization (GEO) for EleViewer and eleviewer-site. Use this when updating website metadata, landing pages, or distribution channels.
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
