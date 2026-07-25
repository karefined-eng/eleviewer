# EleViewer Architecture, Design System, and Distribution Synthesis
**Session Date:** July 25, 2026  
**Target Ingestion Engine:** NotebookLM / Future AI Agent Context  
**Repositories Covered:** `eleviewer` (Python/PySide6 Desktop App) & `eleviewer-site` (Next.js/Tailwind Web Platform)

---

## 1. Executive Summary & Sovereignty Workstation Philosophy
EleViewer is an offline-first, lightweight study and document workspace built for Windows 10/11 undergraduates and academic power users. It adheres to the **"Sovereignty Workstation"** philosophy:
* **Zero Telemetry:** No tracking, analytics, or phone-home pings. User data lives locally.
* **Speed Over Features:** Uncompromising execution speed, single-file `.exe` portability (~220MB standalone), and zero administrative friction.
* **4 Reflex Keys:** `Ctrl+Q` (Quit/Lock), `Alt+V` (Toggle Vault Sidebar), `Ctrl+T` (New Web Tab), `Ctrl+Shift+T` (Restore Tab).
* **Universal Accessibility:** Built-in Text-to-Speech (TTS) bound to `F9` across all supported document types (PDF, Word DOCX, Excel XLSX, PowerPoint PPTX, Markdown MD, and TXT).

---

## 2. Canonical UI Design System (Vercel Geist & Google Stitch Contract)
To eradicate visual fragmentation between the desktop application and the web marketing platform, a canonical design system contract was codified in `eleviewer-site/DESIGN.md` and enforced via `.agents/AGENTS.md` in both repositories.

### Key Visual & Architectural Constraints:
1. **Monochromatic Ink-on-Canvas Aesthetic:** Inspired by Vercel (Geist) and Linear, the interface relies on near-white canvases (`#ffffff` / `#131313`) and near-black ink (`#0c0c0c` / `#f2f2f0`) with 1px hairline borders (`border-border`).
2. **Absolute Ban on Ad-Hoc Alert Colors:** No Tailwind utility classes like `amber-500`, `rose-500`, `emerald-500`, `red-500`, `purple-500`, or `green-500` may be used for badges, icon containers, or alert banners. 
3. **Canonical Component Vocabulary:**
   * **Notices & SmartScreen Warnings (`notice-box`):** Must use `rounded-lg border border-border bg-panel text-muted-foreground font-mono text-xs p-4`.
   * **Primary Action CTAs (`button-primary`):** Must use `h-11 px-6 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90`.
   * **Secondary CTAs (`button-secondary`):** Must use `h-11 px-6 border border-border bg-transparent text-foreground hover:bg-panel`.
   * **Eyebrows & Tags (`status-pill`):** Must use `rounded-full border border-border bg-panel px-3 py-1 font-mono text-xs uppercase tracking-wider text-muted-foreground`.
4. **Desktop App Theme Parity:** Custom PySide6 UI widgets (`ui.py`, `xlsx_viewer.py`, `vault_explorer.py`) must never hardcode hex colors; they must import constants (`BRAND_PRIMARY`, `BRAND_PANEL`, `BRAND_ACCENT`) from `theme.py`.

---

## 3. Frictionless Feedback Hub & Copywriting Readability (Flesch-Kincaid Rule)
To maximize user bug reporting and feature intake without corporate friction, the web review page (`app/review/page.tsx`) was rebuilt into a unified, zero-emoji **Feedback and Bug Reporting Hub**.

### Copywriting & Readability Foundations:
* **The 8th-Grade / Middle School Readability Rule:** Drawing from classical advertising (David Ogilvy), usability research (Jakob Nielsen / Nielsen Norman Group), and startup copywriting (Paul Graham's *"Write Like You Talk"* / Rudolf Flesch's Flesch-Kincaid test), public-facing developer copy must aim for a Grade 6 to 8 reading level (ages 11–13). This minimizes cognitive load for undergraduates skimming on lab PCs.
* **The PMF Outcome Opening:** Instead of asking *"What feature do you want?"*, the hub asks: **"Is there something you wish EleViewer could do?"** This uncovers unmet desired outcomes and workflow gaps.
* **Guarding Against Roadmap Debt:** To avoid promising unconditional implementation (which causes bloat and feature traps), the subheadline guarantees review rather than execution: *"Share your idea directly with the developer — every submission is reviewed for our upcoming builds."*
* **Zero-Authentication Web Bridge:** The form POSTs directly to a Vercel serverless endpoint (`/api/feedback`), which uses an encrypted Vercel environment variable (`GITHUB_PAT`) to convert anonymous student submissions into cleanly formatted markdown issues in the `karefined-eng/eleviewer` GitHub repo. No GitHub account or email is required from the student.

---

## 4. PowerPoint (.pptx) & Distribution Manifest Verification
* **Native PPTX Integration:** Verified across desktop (`pptx_viewer.py`, slide text extraction via `python-pptx`, F9 TTS slide reading, and fallback `win32com` silent conversion) and web (`hero.tsx`, `faq.tsx`, JSON-LD schema).
* **Winget & Inno Setup Manifests:** Verified that `setup.iss` registers default Windows file associations (`HKCR\.pptx`, `.docx`, etc.) and that `karefined-eng.EleViewer.locale.en-US.yaml` routes downloads directly to GitHub Releases under GNU GPLv3 licensing.

---

## 5. Autonomous AI GUI Testing Ecosystem (How AI Tests Like Humans)
In evaluating how AI agents test graphical interfaces like human quality assurance engineers, the following cutting-edge benchmarks and frameworks were documented:
1. **OSWorld & OSWorld-Human (Desktop Applications):** A benchmark testing AI agents inside real operating systems (Windows, Ubuntu, macOS). Agents look at raw screenshots and operate virtual mice/keyboards to complete multi-step tasks in desktop apps (Office suites, PDF readers, file explorers).
2. **WebArena & VisualWebArena (Web Applications):** Evaluates autonomous web agents navigating live websites (clicking links, filling out forms, submitting feedback) using visual DOM observation.
3. **AppAgent (Tencent / USC):** A multimodal agent framework that learns to operate software through autonomous visual exploration (clicking around to observe state transitions) or by watching human tutorial video recordings.
4. **Live Verification:** Demonstrated this paradigm in real time by launching an autonomous browser subagent (`localhost:3000/review`) to visually inspect EleViewer's new monochromatic UI and test typing into the Flesch-Kincaid feedback form.
