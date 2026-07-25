# EleViewer Website — Gemini 3.6 AntiGravity IDE Prompt Pack
# @antigravity execute-all target=website module=gemini3.6-high
> Source: eleviewer.vercel.app audit — July 25, 2026
> Stack: Next.js · Vercel · Tailwind (inferred) · HTML/JSX
> Execute each prompt block in sequence inside the website project folder

---

## PROMPT W1 — CRITICAL: Qualify TTS as Windows-Only
# @antigravity prompt module=gemini3.6-high target=website

```
You are a web copywriter and Next.js engineer making a targeted content correction.

PROJECT: EleViewer marketing website (Next.js, hosted on Vercel).
FOLDER: /website or root Next.js project directory.

PROBLEM: The site advertises "PDF text-to-speech" as a universal feature in the
hero section, features section, and FAQ — with no platform caveat. The TTS engine
(tts_engine.py) uses pyttsx3/SAPI5 and is Windows-only. On macOS/Linux it crashes.
This creates false advertising risk and bad reviews from non-Windows users.

FIX REQUIRED — find and update every instance of the TTS claim:

1. HERO SUBTITLE:
   BEFORE: "with PDF text-to-speech, built-in web browser, find & replace, autosave"
   AFTER:  "with PDF text-to-speech (Windows), built-in web browser, find & replace, autosave"

2. FEATURES SECTION — "PDFs that read to you":
   BEFORE: "Native text-to-speech turns any lecture slide or reading into audio."
   AFTER:  "Native Windows text-to-speech turns any lecture slide or reading into audio. (Windows 10/11 only)"

3. META DESCRIPTION:
   BEFORE: "...with PDF text-to-speech, built-in web browser..."
   AFTER:  "...with PDF text-to-speech for Windows, built-in web browser..."

4. OG DESCRIPTION — apply same edit as meta description.

5. FAQ — "Does EleViewer support PDF text-to-speech?":
   BEFORE: "Yes. The built-in PDF reader can read documents aloud so you can study hands-free."
   AFTER:  "Yes, on Windows 10 and 11. The built-in PDF reader uses the Windows speech engine
            to read documents aloud so you can study hands-free. macOS and Linux support is
            planned for a future release."

CONSTRAINTS:
- Do not change any other copy, layout, or component structure.
- Preserve all className, styling, and JSX attributes.
- If content is in a separate data/content file (e.g. content.js, data.ts, or a JSON),
  make the edit there rather than in the JSX directly.

Return each corrected file as a labeled code block with its relative file path.
```

---

## PROMPT W2 — CRITICAL: Qualify Session Restore Claim
# @antigravity prompt module=gemini3.6-high target=website

```
You are a web copywriter and Next.js engineer making a targeted content correction.

PROJECT: EleViewer marketing website (Next.js, hosted on Vercel).

PROBLEM: The site claims "Close your laptop mid-study session. Reopen EleViewer and
every tab comes back exactly where you left it." The codebase audit confirmed that
session_manager.py restores open file paths but does NOT restore scroll positions
or PDF zoom levels. The phrase "exactly where you left it" is inaccurate.

FIX REQUIRED:

1. FEATURES SECTION — "Session restore" card:
   BEFORE: "Close your laptop mid-study session. Reopen EleViewer and every tab
            comes back exactly where you left it."
   AFTER:  "Close your laptop mid-study session. Reopen EleViewer and every tab
            comes back — files, order, and active tab restored automatically."

2. Any other instance of "exactly where you left it" on the page — apply the same
   correction, removing the word "exactly" and replacing with the above phrasing.

CONSTRAINTS:
- Do not change any other copy, layout, or component structure.
- Preserve all className, styling, and JSX attributes.

Return each corrected file as a labeled code block with its relative file path.
```

---

## PROMPT W3 — CRITICAL: Add SmartScreen Warning to Download Flow
# @antigravity prompt module=gemini3.6-high target=website

```
You are a Next.js engineer adding a SmartScreen disclaimer to a download CTA.

PROJECT: EleViewer marketing website (Next.js, hosted on Vercel).

PROBLEM: The .exe download links directly to GitHub releases. PyInstaller onefile
builds without Azure Code Signing trigger Windows SmartScreen "Unknown Publisher"
warnings. Users unfamiliar with this may abandon the download thinking it is malware.

FIX REQUIRED — add a small dismissal note beneath EVERY download button/CTA:

    <p className="text-xs text-neutral-500 mt-2">
      Windows may show a SmartScreen warning — click <strong>"More info"</strong> then{" "}
      <strong>"Run anyway"</strong>. EleViewer is open source and MIT licensed.{" "}
      <a
        href="https://github.com/karefined-eng/eleviewer"
        className="underline hover:text-neutral-300"
        target="_blank"
        rel="noopener noreferrer"
      >
        Verify the source code.
      </a>
    </p>

Apply this note below:
- The hero "Download for Windows" button
- The bottom CTA "Download EleViewer for Windows" button

CONSTRAINTS:
- Do not change the download button itself or its href.
- Match the existing text sizing and color conventions of the site (neutral-500 or equivalent).
- If the site uses a different CSS system than Tailwind, adapt the className values accordingly.

Return each corrected component/section file as a labeled code block.
```

---

## PROMPT W4 — CRITICAL: Add SoftwareApplication JSON-LD Schema
# @antigravity prompt module=gemini3.6-high target=website

```
You are a Next.js SEO engineer adding structured data to a software landing page.

PROJECT: EleViewer marketing website (Next.js, hosted on Vercel).
FILE: app/layout.tsx or pages/_document.tsx or the root layout file.

PROBLEM: No JSON-LD structured data exists on the page. Google cannot generate
a rich result (download button, OS badge, star rating) for EleViewer in search results.

FIX REQUIRED — add SoftwareApplication + FAQPage JSON-LD to the <head>:

    // In your root layout or _document, add inside <head>:
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          "name": "EleViewer",
          "description": "Free portable Windows document viewer and study workspace. Opens DOCX, XLSX, PDF, Markdown, CSV, HTML, and TXT with text-to-speech, file vault, and session restore.",
          "operatingSystem": "Windows 10, Windows 11",
          "applicationCategory": "UtilitiesApplication",
          "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
          },
          "downloadUrl": "https://github.com/karefined-eng/eleviewer/releases/latest/download/EleViewer.exe",
          "softwareVersion": "1.3.0",
          "license": "https://github.com/karefined-eng/eleviewer/blob/main/LICENSE",
          "url": "https://eleviewer.vercel.app",
          "author": {
            "@type": "Person",
            "name": "karefined-eng",
            "url": "https://github.com/karefined-eng"
          },
          "publisher": {
            "@type": "Organization",
            "name": "Karefined"
          }
        })
      }}
    />

Also add FAQPage schema for the FAQ section:

    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": [
            {
              "@type": "Question",
              "name": "Can I browse the web inside EleViewer?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes. Press Ctrl+T to open the built-in web browser panel and browse side-by-side with your documents."
              }
            },
            {
              "@type": "Question",
              "name": "Is EleViewer truly free and open source?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes. EleViewer is free, MIT licensed, portable, and requires no account or installation."
              }
            },
            {
              "@type": "Question",
              "name": "What file types can EleViewer open?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "EleViewer opens DOCX, XLSX, PDF, Markdown, CSV, HTML, and TXT files."
              }
            },
            {
              "@type": "Question",
              "name": "Does EleViewer support PDF text-to-speech?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes, on Windows 10 and 11. The built-in PDF reader uses the Windows speech engine to read documents aloud. macOS and Linux support is planned."
              }
            },
            {
              "@type": "Question",
              "name": "Can I use EleViewer offline?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes. EleViewer runs fully locally on Windows 10 and 11 without an internet connection."
              }
            }
          ]
        })
      }}
    />

CONSTRAINTS:
- Place both scripts inside <head> without disrupting existing meta tags.
- If using Next.js App Router, use the metadata API where possible but dangerouslySetInnerHTML
  is acceptable for JSON-LD.
- Do not duplicate any existing meta tags.

Return the corrected layout/document file in full.
```

---

## PROMPT W5 — SEO: Fix H1 to Match Title Tag Keyword Target
# @antigravity prompt module=gemini3.6-high target=website

```
You are an SEO engineer fixing a heading hierarchy mismatch on a landing page.

PROJECT: EleViewer marketing website (Next.js, hosted on Vercel).
FILE: Main page component (app/page.tsx or pages/index.tsx or equivalent).

PROBLEM: The page <title> targets "Free Windows Document Viewer & Study Workspace"
but the visible <h1> reads "The Lightweight Open Source Study Workspace for Windows".
Google uses H1 as a primary ranking signal. The keyword "document viewer" — which
has the highest search volume — is absent from the H1.

FIX REQUIRED:

1. Change the <h1> to:
   "EleViewer — Free Windows Document Viewer & Study Workspace"

2. Demote the current H1 text to an <h2> styled as a subheading directly below:
   "The open source study workspace for every file your professor throws at you."
   (Rewrite the existing H1 text slightly to work as a supporting subhead.)

3. The existing H2 "Every file your professor throws at you. One free app." can be
   removed or folded into the new H2 above to avoid redundancy.

CONSTRAINTS:
- Preserve all existing className and styling on the heading elements.
- The visual hierarchy (large hero heading → smaller subheading) must be maintained.
- Do not change the hero CTA buttons or any content below the headings.

Return the corrected hero section JSX.
```

---

## PROMPT W6 — SEO: Replace "Lightweight" with Accurate Positioning
# @antigravity prompt module=gemini3.6-high target=website

```
You are a web copywriter making brand-accurate copy corrections across a landing page.

PROJECT: EleViewer marketing website (Next.js, hosted on Vercel).

PROBLEM: The word "lightweight" appears multiple times on the page but the executable
is ~220MB due to the bundled Chromium (QWebEngineView) component. This contradicts
the "lightning fast / lightweight" claims and will generate negative reviews from
users who notice the file size. The stronger and accurate differentiator is
"portable" (no install, runs from USB) and "no Electron overhead."

FIX REQUIRED — find and replace all instances:

1. Section heading: "A study workspace, not another bloated suite"
   (Keep this — it's accurate and strong. No change.)

2. Meta description: "...one lightweight study workspace..."
   CHANGE TO: "...one portable study workspace..."

3. OG description: apply the same edit.

4. Feature card copy — wherever "lightweight" appears describing the app:
   CHANGE TO: "portable" or "self-contained"

5. "Lightning Fast — Native PySide6 engine" badge:
   CHANGE TO: "Native PySide6 — No Electron overhead"
   (This is accurate, still a strong differentiator vs. Electron apps like VS Code.)

6. Hero body: "one lightweight study workspace"
   CHANGE TO: "one portable study workspace"

CONSTRAINTS:
- Do NOT change "lightweight" if it refers to the interface/UX feel rather than file size
  (e.g. "lightweight workflow" is fine).
- Preserve all className, JSX structure, and styling.
- Return each changed file as a labeled code block.
```

---

## PROMPT W7 — UX: Route Download Through /download Page
# @antigravity prompt module=gemini3.6-high target=website

```
You are a Next.js engineer creating a download landing page.

PROJECT: EleViewer marketing website (Next.js, Vercel).

PROBLEM: All download CTAs link directly to the GitHub releases .exe. This:
- Loses download conversion analytics
- Gives users no context before the download starts
- Triggers browser "dangerous file" warnings with no reassurance

FIX REQUIRED — create app/download/page.tsx (or pages/download.tsx):

The /download page should:

1. Display the app name, version, and a prominent "Download EleViewer.exe" button
   that links to: https://github.com/karefined-eng/eleviewer/releases/latest/download/EleViewer.exe

2. Show the SHA-256 hash placeholder (to be filled by CI):
   <p>SHA-256: <code>{SHA256_HASH}</code></p>
   Use an environment variable: process.env.NEXT_PUBLIC_SHA256 ?? 'See GitHub Releases'

3. List system requirements:
   - Windows 10 or 11 (64-bit)
   - ~220MB free disk space
   - No installation required

4. Show the SmartScreen note (same as Prompt W3).

5. Show the winget CLI alternative:
   <code>winget install karefined-eng.EleViewer</code>
   with a copy-to-clipboard button.

6. Update ALL existing download button hrefs across the site from:
   https://github.com/karefined-eng/eleviewer/releases/latest/download/EleViewer.exe
   TO:
   /download

CONSTRAINTS:
- Match the existing site design system (dark background, accent colors, typography).
- The /download page must be statically renderable (no server-side data fetching required).
- Add a <title> tag: "Download EleViewer — Free Windows Document Viewer"

Return:
[1] The full app/download/page.tsx (or pages/download.tsx) file
[2] The diff/changes to update all existing download button hrefs
```

---

## PROMPT W8 — UX: Demote GitHub CTA to Ghost Button in Hero
# @antigravity prompt module=gemini3.6-high target=website

```
You are a Next.js UI engineer improving hero CTA conversion hierarchy.

PROJECT: EleViewer marketing website (Next.js, Vercel).
FILE: Main page component hero section.

PROBLEM: "Download for Windows" and "View on GitHub" buttons have equal visual
weight in the hero. GitHub is a secondary action. Equal weighting splits user
attention and reduces download conversion rate.

FIX REQUIRED:

1. Keep "Download for Windows" as the primary filled/solid button (no change to styling).

2. Change "View on GitHub" to a ghost/outline button:
   - Remove solid background fill
   - Add border: 1px solid currentColor (or equivalent in your CSS system)
   - Reduce font weight slightly if currently bold
   - The text and icon remain the same

   Example Tailwind classes (adapt to match your existing design system):
   BEFORE: className="bg-white text-black px-6 py-3 rounded-md font-semibold ..."
   AFTER:  className="border border-neutral-500 text-neutral-300 px-6 py-3 rounded-md
                      font-medium hover:border-neutral-300 hover:text-white transition ..."

CONSTRAINTS:
- Do not change the href, icon, or text of either button.
- Do not change the primary download button styling at all.
- Preserve responsive layout (buttons should still stack correctly on mobile).

Return the corrected hero CTA section JSX.
```

---

## PROMPT W9 — UX: Route WhatsApp Link Through /community
# @antigravity prompt module=gemini3.6-high target=website

```
You are a Next.js engineer making a community link resilient to future changes.

PROJECT: EleViewer marketing website (Next.js, Vercel).

PROBLEM: The WhatsApp Nightly Insiders link is hardcoded as:
https://chat.whatsapp.com/FeofuieK0Ae51KdUZEvwTQ
If this group reaches capacity or is replaced, the link breaks silently across
every user who has bookmarked or shared the site. Updating requires a full redeploy.

FIX REQUIRED:

1. Create app/community/page.tsx that immediately redirects to the WhatsApp URL:

    import { redirect } from 'next/navigation'
    export default function CommunityPage() {
      redirect('https://chat.whatsapp.com/FeofuieK0Ae51KdUZEvwTQ')
    }

   Future WhatsApp group changes = update one line, no site-wide find/replace needed.

2. Update the "Join Nightly Insiders on WhatsApp" button href from:
   https://chat.whatsapp.com/FeofuieK0Ae51KdUZEvwTQ
   TO:
   /community

3. Remove rel="noopener noreferrer" from the /community link since it's now internal.
   Keep it on any remaining direct external WhatsApp links.

CONSTRAINTS:
- The redirect must be instant (use Next.js redirect(), not a client-side useRouter push).
- Do not change the button text, styling, or surrounding copy.

Return:
[1] app/community/page.tsx
[2] The updated link href in the main page component
```

---

## PROMPT W10 — UX: Add Winget CLI Command Next to Badge
# @antigravity prompt module=gemini3.6-high target=website

```
You are a Next.js UI engineer adding a developer-friendly install command to a landing page.

PROJECT: EleViewer marketing website (Next.js, Vercel).
FILE: Main page component — wherever the "Winget Verified" badge appears.

PROBLEM: The "Winget Verified — Official Windows package" badge exists but gives
power users no actionable command to copy. Users who prefer winget have to
Google the package ID.

FIX REQUIRED — add a copyable winget command block beneath or beside the badge:

    <div className="flex items-center gap-3 mt-3">
      <code className="bg-neutral-900 border border-neutral-700 text-neutral-300
                       text-sm px-4 py-2 rounded-md font-mono select-all">
        winget install karefined-eng.EleViewer
      </code>
      <button
        onClick={() => navigator.clipboard.writeText('winget install karefined-eng.EleViewer')}
        className="text-xs text-neutral-500 hover:text-neutral-300 transition"
        aria-label="Copy winget command"
      >
        Copy
      </button>
    </div>

Add a small label above: <p className="text-xs text-neutral-500">Or install via Winget:</p>

CONSTRAINTS:
- Use 'use client' directive on this component if not already a client component
  (navigator.clipboard requires browser context).
- Adapt className values to match the existing design system if not using Tailwind.
- Do not change the badge text or icon.

Return the corrected badge + command section JSX.
```

---

## PROMPT W11 — SEO: Add Extended FAQ Items for Long-Tail Keywords
# @antigravity prompt module=gemini3.6-high target=website

```
You are an SEO copywriter expanding a FAQ section to capture long-tail search traffic.

PROJECT: EleViewer marketing website (Next.js, Vercel).
FILE: FAQ section component or data file.

PROBLEM: The FAQ has only 5 items. Competitors rank for 15–20 long-tail queries
that EleViewer directly answers. Adding targeted FAQ items captures organic search
traffic from students searching for these exact problems.

FIX REQUIRED — add these 8 new FAQ items to the existing FAQ list:

Q: How do I open a DOCX file without Microsoft Word?
A: Download EleViewer — it opens Word documents (.docx) for free with no Microsoft
   Office required. Just drag the file onto EleViewer or use Ctrl+O to open it.

Q: Is there a free portable PDF reader for Windows with no install?
A: Yes — EleViewer is a portable .exe that opens PDFs, DOCX, XLSX, Markdown, and
   more with no installation. Run it directly from a USB drive or a shared lab computer.

Q: Can EleViewer run on a school or university computer without admin rights?
A: Yes. EleViewer is a single portable .exe that requires no installation and no
   admin privileges. Just download and double-click.

Q: Does EleViewer work without an internet connection?
A: Fully. EleViewer runs 100% locally on Windows 10 and 11. No internet connection
   is needed to open, edit, or read documents.

Q: What is the keyboard shortcut to search inside a file in EleViewer?
A: Press Ctrl+F to open Find in any open document. Press Ctrl+H to open Find & Replace.

Q: How do I open my course folder in EleViewer?
A: Press Alt+V to toggle the Vault sidebar, then point it at your course folder in
   settings. Every file in the folder becomes one click away.

Q: Does EleViewer save my files automatically?
A: Yes. EleViewer has a built-in autosave that runs in the background at a
   configurable interval. You can adjust the autosave frequency in Settings (Alt+S).

Q: Is EleViewer safe to download? Will it trigger antivirus warnings?
A: EleViewer is fully open source (MIT licensed) — you can read every line of code
   on GitHub. Windows may show a SmartScreen warning because the app is not yet
   code-signed. Click "More info" then "Run anyway" to proceed. The source code is
   publicly auditable at github.com/karefined-eng/eleviewer.

CONSTRAINTS:
- Match the existing FAQ item component structure exactly (same JSX pattern as current items).
- Append new items after the existing 5, in the order listed above.
- Also add these 8 questions to the FAQPage JSON-LD schema (from Prompt W4).

Return the updated FAQ section/data file with all 13 items.
```

---

## PROMPT W12 — CONTENT: Add Minimal Privacy Policy Page
# @antigravity prompt module=gemini3.6-high target=website

```
You are a Next.js engineer creating a minimal privacy policy page for a local-first app.

PROJECT: EleViewer marketing website (Next.js, Vercel).

PROBLEM: No privacy policy page exists. School IT departments and institutional users
check for a privacy policy before allowing students to use software. Its absence
can block adoption in educational institutions.

FIX REQUIRED — create app/privacy/page.tsx:

Content to include:

    # EleViewer Privacy Policy

    **Last updated: [AUTO-DATE]**

    ## What data EleViewer collects
    EleViewer collects no personal data. The application runs entirely on your
    local machine. No usage data, file contents, or identifiers are transmitted
    to any server.

    ## The feedback feature
    If you choose to submit feedback using the in-app feedback dialog, the text
    you type is sent to eleviewer.vercel.app/api/feedback. No account, name,
    or email is required or collected. This is entirely opt-in.

    ## This website
    This website (eleviewer.vercel.app) is hosted on Vercel, which may collect
    standard server access logs (IP address, browser, referring URL) as part of
    its hosting infrastructure. EleViewer does not access or use these logs.
    See Vercel's privacy policy for details.

    ## Open source
    EleViewer's source code is publicly available at
    github.com/karefined-eng/eleviewer under the MIT license.
    You can verify exactly what the application does.

    ## Contact
    Questions? Open an issue at github.com/karefined-eng/eleviewer/issues.

Also add a "Privacy" link to the site footer alongside the existing
GitHub, Releases, Report a bug, and MIT License links.

CONSTRAINTS:
- Match the existing site design system for the page layout.
- Use the current date dynamically or hardcode the audit date: July 25, 2026.
- Keep the page under 400 words — this is a software privacy policy, not a legal document.

Return:
[1] app/privacy/page.tsx
[2] The updated footer component with the Privacy link added
```

---

## EXECUTION ORDER FOR ANTIGRAVITY IDE
# @antigravity config

Priority   | Prompt | File(s) Affected                          | Risk if Skipped
-----------|--------|-------------------------------------------|------------------
🔴 CRITICAL | W1    | Page copy + meta tags                     | False advertising (TTS)
🔴 CRITICAL | W2    | Page copy                                 | User disappointment
🔴 CRITICAL | W3    | Hero + CTA components                     | Download abandonment
🔴 CRITICAL | W4    | layout.tsx / _document.tsx                | Missing Google rich results
🟠 SEO      | W5    | page.tsx hero section                     | Keyword ranking loss
🟠 SEO      | W6    | Page copy + meta                          | Brand contradiction
🟠 SEO      | W11   | FAQ section/data file                     | Missed long-tail traffic
🟡 UX       | W7    | New /download page + all CTA hrefs        | No analytics on downloads
🟡 UX       | W8    | Hero CTA buttons                          | Split conversion attention
🟡 UX       | W9    | New /community redirect + link            | Broken WhatsApp if group changes
🟡 UX       | W10   | Winget badge section                      | Power user friction
🟢 TRUST    | W12   | New /privacy page + footer                | Blocked by school IT