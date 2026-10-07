# Desktop stack prototype: Tauri vs. Wails

## Recommendation

Explore a small **Tauri + Rust** prototype before considering a rewrite. Compare it with the current PySide6 app and, if time permits, a small **Wails + Go** prototype. Do not replace the current app or promise feature parity until measurements and a feature-risk review support that decision.

The strongest reason to test these stacks is not that Rust or Go automatically makes an app small or fast. On Windows, Tauri and Wails can use the installed **Microsoft Edge WebView2 runtime** instead of packaging a separate Chromium browser. That may substantially reduce the download size. It also changes the assumptions: users need a WebView2 runtime, and installing or bundling one affects offline setup size and behavior.

## Why consider another stack?

The current release is self-contained and predictable, but the Full portable build expands to about **503 MB**. The downloadable portable ZIP is about **196 MB**, and the installer is about **126 MB**. The bundled Qt WebEngine/Chromium runtime is the largest removable part. LTO is already enabled; it optimizes compiled code, not the bundled browser and framework libraries.

Using the Windows WebView2 runtime could avoid duplicating Chromium in every EleViewer download. A native Rust or Go shell may also offer different startup and memory characteristics. Neither benefit should be assumed: measure them on a clean Windows machine.

## Candidate stacks

| Candidate | Potential advantages | Main risks and questions |
|---|---|---|
| **Tauri + Rust** | Windows WebView2 integration; small native application shell; Rust's memory-safety guarantees; broad plugin ecosystem | Rust learning and build complexity; plugin maturity varies; file-format and accessibility coverage must be proven; runtime availability and installer behavior need testing |
| **Wails + Go** | Windows WebView2 integration; straightforward Go backend and distribution; approachable concurrency model | Web frontend becomes a larger part of the application; Go runtime and WebView2 packaging still have a cost; UI parity and native Windows behavior need testing |
| **Keep PySide6** | Existing behavior, modules, and tests; familiar development workflow; portable standalone build | Bundled Qt and Chromium keep the Full release large; optimization headroom needs a separate measured pass |

**Initial preference:** test Tauri first, with Wails as a comparison rather than a predetermined second implementation. If the prototype's only important win is omitting bundled Chromium, first compare it fairly against the current Compact edition, which is already intended to ship without the embedded browser.

## Non-negotiable product requirements

Any prototype must be evaluated against EleViewer's actual promise:

- Windows 10 and 11 desktop app; per-user installation must not require administrator rights.
- Local-first use of files and study data; core document reading and note-taking must work offline.
- Clear behavior when the embedded web panel is unavailable. Do not silently pretend online pages work offline.
- Portable distribution remains a product goal. A WebView2-dependent portable package must explain the runtime requirement and work predictably on a clean machine.
- No account, telemetry, or automatic transmission of document contents.
- Keep existing formats and workflows in scope: PDF, DOCX, PPTX, XLSX, CSV/TSV, Markdown, TXT, HTML, and notes.
- Preserve the high-value workspace features where feasible: vault browsing/search, session restore, bookmarks, quick note (`Alt+E`), text-to-speech, file associations, and reliable saving.

The current app's Office viewers are readers, not full Microsoft Office replacements. The prototype should match existing EleViewer behavior rather than expand that claim into full editing or perfect Office rendering.

## Runtime and offline tradeoffs

WebView2 offers a potentially large package-size reduction only when EleViewer can use a runtime already installed on the user's system. Validate all of these deployment choices:

1. **Use the installed Evergreen Runtime.** This keeps EleViewer's download small when the runtime is present, but the first-run experience needs a clear path for machines without it. Determine whether the supported Windows versions reliably have it; do not assume that Microsoft Edge being installed proves the WebView2 Runtime is installed.
2. **Bootstrapper.** A small installer can obtain the runtime when online. This is not a fully offline installation and may be blocked by school networks or device policy.
3. **Fixed Version Runtime.** Shipping a private runtime improves predictability and offline installation, but adds a large payload and may erase the size advantage. Measure the actual installer and installed footprint before selecting it.
4. **Browser-free edition.** A small core edition can leave web links to the user's default browser and avoid making a browser runtime a requirement. Compare this directly with the current Compact edition.

Keep browser integration behind a clear boundary so document reading and note-taking still work if WebView2 cannot initialize. Test local HTML separately from remote browsing: local previews may have different requirements and security constraints from an online web panel.

## Feature migration risks

| Area | Prototype question |
|---|---|
| PDF | Can a native or WebView2-based reader preserve page navigation, search, bookmarks, zoom, and reliable offline reading? Validate large and image-heavy files. |
| DOCX and PPTX | Can the new renderer preserve the current text, image, notes, and slide behaviors without requiring Office? Check representative complex documents, not only simple samples. |
| XLSX, CSV, and TSV | Verify multiple sheets, large files, delimiters, cell search, and the current read/edit behavior. |
| Markdown and HTML | Check editing, preview fidelity, local asset links, safe HTML handling, and large document responsiveness. |
| Vault search | Compare indexing speed, query responsiveness, Unicode/path handling, cancellation, and index recovery. |
| Session and bookmarks | Define a versioned local data format and test recovery after an interrupted write. Plan migration from the existing `%APPDATA%\\EleViewer` data without losing user state. |
| Quick note and shortcuts | Confirm global `Alt+E` registration, conflict handling, single-instance behavior, and file-open routing on Windows. |
| Text-to-speech | Test Windows voices, selected-text reading, playback controls, and offline behavior. |
| Install and update | Test per-user installation, upgrade, rollback, file associations, uninstall, and preservation of user data. Keep update integrity checks. |
| Accessibility | Check keyboard-only navigation, screen-reader names and announcements, high contrast, and sensible focus order in the native shell and web content. |

## Prototype plan

Create independent prototype branches **from `main`**, not from a feature branch or from one another:

- `prototype-tauri` — Tauri/Rust proof of concept.
- `prototype-wails` — optional Go/Wails comparison, also based directly on `main`.

Keep experiments isolated from the production app. Each branch should record its base commit and avoid changing the current release pipeline. Do not merge prototype work into `main` just to preserve it; retain the branches until the decision is made.

### Stage 1: deployment and size proof

Build the smallest branded Windows window with a WebView2 page, per-user packaging, and a startup diagnostic. Produce:

- A network-accessible install path.
- A portable or offline test path with its exact runtime prerequisites stated.
- Installer download size, extracted application size, and total installed size, with WebView2 counted separately and together.
- A clean-machine test for a system with and without the WebView2 Runtime.

Stop early if the runtime cannot be installed or found reliably on target school machines, or if offline/portable distribution requires a payload close to the current Full build.

### Stage 2: representative feature slice

Only if Stage 1 is promising, add a vertical slice that exercises actual product risks:

- Open and search one PDF, one DOCX, one image-heavy PPTX, and one XLSX, plus Markdown and CSV.
- Edit and save a note using crash-safe writes.
- Open a local study folder and search filenames.
- Restore a small session and one bookmark.
- Open a web panel when the runtime is available and open web links in the default browser when it is not.

Do not implement every settings screen or reproduce every visual detail during this stage.

### Stage 3: decide whether to continue

Write down benchmark results and missing features. Continue toward broader parity only if a prototype is materially better on the chosen product goals and its gaps have credible, maintainable solutions.

## Measurement plan

Compare release builds made with documented, reproducible settings. Use the same representative Windows machine and sample files. Report results as separate measurements; do not call an app “small” based only on the installer download.

| Measure | How to compare |
|---|---|
| Download size | Bytes for each installer and portable archive |
| Installed footprint | App files plus the required WebView2 runtime; report the runtime separately and included in total |
| Cold startup | Time from launch to a usable window, after a reboot or clean process start; report median across repeated runs |
| Warm startup | Time to usable window on a later launch |
| Idle memory | Working set after the window settles, both with and without the web panel |
| Active memory | Working set after opening representative documents and a web page |
| CPU and responsiveness | Time to open/search representative files; check for UI stalls during indexing and rendering |
| Offline behavior | Cold start and open local files with network disabled; test web actions and first install separately |
| Reliability | Repeated launch/close, interrupted save recovery, single-instance file opening, and updater/install tests |
| Feature coverage | Pass/fail list against the requirements above, including accessibility and security behavior |

Keep the current Full and Compact package figures as baselines. Record Windows version, hardware, runtime version, build configuration, number of runs, and test-file sizes beside each result.

## Decision criteria

Proceed beyond prototypes only if the chosen option:

- Has a clearly smaller total download and installed footprint for the intended edition—not just a small installer that downloads a large runtime later.
- Preserves offline reading, local files, per-user installation, and the no-account/no-telemetry promise.
- Can reach an acceptable level of feature coverage without excessive native dependencies or fragile plugins.
- Meets or improves startup, responsiveness, memory, reliability, and accessibility on representative school hardware.
- Has a maintainable update, security-patching, and Windows runtime plan.

If the only size win requires a permanently online browser-runtime download, or offline distribution requires bundling nearly the same runtime again, prefer keeping the existing app and shipping the Compact edition rather than rewriting for size alone.

## Current conclusion

The Tauri/Rust direction is worth testing, not yet worth adopting. The central experiment is whether using the installed WebView2 runtime delivers a real size and performance benefit **without breaking offline and portable use**. A small prototype can answer that at far lower cost than a rewrite.
