# EleViewer Agent Guide

## Purpose
This repository is a Python + PySide6 desktop app for browsing and studying local documents. Keep changes small, local, and consistent with the current implementation.

## Short-form operating rules
- Read `docs/origin.md` before major product or UI changes; do not drift from documented intent.
- Treat `docs/AGENTS.md` and `.agents/AGENTS.md` as the repo's living operating manual; read them before acting.
- Keep durable work notes in `docs/handoff/` and UX rationale in `docs/research/`.
- API reference for core modules lives in `docs/api/`; user-facing feature guides live in `docs/features/`; friction logs live in `docs/friction-log.md`.
- Do not leave a tool trap or environment quirk unexplained; log it under `Tool Quirks` / `Environment Traps` before ending the session.
- Be proactive: challenge weak assumptions, explain tradeoffs, and keep decisions anchored in user value and product psychology.
- Prefer legal/safe, authorized workflows; do not help with unauthorized scraping or private-data collection.
- If a release, distribution, or package-manager step fails, separate product issues from external upstream blockers and document the exact cause.

## Working assumptions
- The app entry point is [main.py](../main.py).
- The main UI shell is [ui.py](../ui.py).
- File routing happens in [file_handler.py](../file_handler.py).
- Viewer-specific logic lives in [markdown_renderer.py](../markdown_renderer.py), [docx_viewer.py](../docx_viewer.py), [pptx_viewer.py](../pptx_viewer.py), [pdf_viewer.py](../pdf_viewer.py), [xlsx_viewer.py](../xlsx_viewer.py), and [csv_viewer.py](../csv_viewer.py).
- Interactive tutorials and onboarding live in [tutorials.py](../tutorials.py) and [onboarding.py](../onboarding.py).
- Web browsing panel lives in [web_panel.py](../web_panel.py).
- Versioning single source of truth is [version.py](../version.py).
- The app is intentionally lightweight. Prefer native Python/Qt rendering and small caching or debouncing changes over introducing new runtime dependencies.
- There is no Rust-based viewer implementation in the current repository; do not add Rust or PyO3 work unless the user explicitly asks for it.

## Before editing
- Read this guide before acting. It is the canonical agent guide for this repository; do not create competing copies at the root or under `docs/`.
- Before major architecture changes, UI redesigns, or feature-scope decisions, read `docs/origin.md` if it exists. If the project vision is not documented there, use the README and developer onboarding guide and avoid making unapproved product-direction changes.
- Read `README.md` and `DEVELOPER_ONBOARDING.md` before making architecture or implementation changes.
- Read the relevant module and nearby callers before changing behavior.
- Check whether the change should be covered by an existing test in the repository root (for example [test_markdown_renderer.py](../test_markdown_renderer.py)). Use `pytest -s <test_file>.py` to validate changes.
- If a change affects public module APIs, search for imports before editing.
- Website-specific UI/CSS changes belong in the `eleviewer-site` repository unless the user explicitly asks for desktop app changes.

## Git identity and commits
- When creating commits, use the repository's configured Karefined Git identity (`git config user.name` and `git config user.email`); do not substitute another account.
- Never store, request, expose, or commit passwords, access tokens, private keys, or other credentials. Authentication must come from the user's configured Git/GitHub credential helper.
- Never commit or push unless the user explicitly requests it. Never add a `Co-authored-by` trailer in this repository.

## Documentation, product intent, and handoffs
- Keep this guide as the repository's operational manual for architecture, contribution rules, validation, and known environment traps.
- Before a substantial feature or phase is complete, add a concise permanent walkthrough under `docs/handoff/` covering the implementation, important decisions, and validation. Do not create handoff notes for trivial edits.
- For UI or core-workflow design, record relevant user needs and evidence-based UX reasoning under `docs/research/`; avoid generic aesthetic rationales.
- When evaluating a major product or technical direction, offer candid tradeoffs and practical alternatives. Do not present an unmeasured hypothesis as a proven benefit or silently expand the approved scope.
- For scraping or data-collection requests, assess the target, data sensitivity, and applicable access rules first. Explain privacy and terms-of-service risks when relevant; do not help collect private data or bypass access restrictions. Offer a safer, authorized alternative when needed.

## Implementation rules
- Keep UI responsiveness in mind for preview-heavy paths. Debouncing, caching, and skipping redundant renders are preferred when the user is typing or revisiting the same content.
- Preserve existing keyboard shortcuts and document navigation behavior unless the task explicitly changes them.
- **Tutorial & Dialog Geometry Invariants:** Spotlight overlays in `tutorials.py` must clamp card coordinates strictly within visible window bounds (`max(margin, min(win_w - card_w - margin, card_x))`) to prevent dialogs from rendering off-screen.
- **Version Alignment:** When bumping versions, update [version.py](../version.py), [setup.iss](../setup.iss), [version_sync.py](../version_sync.py), and the Winget manifests in `winget/`.

## Copywriting & Documentation
- **No Developer Jargon in User Copy:** User-facing files (Welcome guide, marketing sites, README intros, release notes) MUST strictly avoid developer jargon (e.g., SQLite, QThread, bleach, chardet, pyttsx3). Translate these into plain English (e.g., "background search engine", "security sanitization"). Keep readability at a 6th-to-8th grade level (Flesch-Kincaid). Developer docs (`DEVELOPER_ONBOARDING.md`, code comments) should remain technical.
- **Lead with Killer Features:** Do not bury the lede. Always highlight EleViewer's unique unified workspace features first: Split-Screen Web Panel, Vaults & Live Search, Session Restore, Persistent Bookmarks, and the Global Quick Note (Alt+E). Generic features (like "opens DOCX") should be listed last.
- Avoid adding new packages unless the task truly requires them.
- **Release Notes vs. Changelog:** Always maintain a dual-format structure for releases. 
  - `CHANGELOG.md` must be written for developers using the strict **"Keep a Changelog"** standard, utilizing semantic headings (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`) in reverse chronological order.
  - `release_notes.md` (and public announcements) must be written for users. It must strictly follow the "No Developer Jargon" and "Lead with Killer Features" rules, grouping changes logically by functional area (e.g., Workspace, Web Panel) and utilizing visuals where applicable.

## Release & Distribution
- The production CI/CD pipeline is defined in `.github/workflows/build.yml`. It triggers on tags matching `v[0-9]+.[0-9]+.[0-9]+`.
- The pipeline compiles with Nuitka C++ (LTO enabled), builds the Inno Setup installer, packages the portable zip, generates the Winget installer manifest with dynamic SHA256 hashes, creates the GitHub Release, and submits to the Windows Package Manager.
- Windows Package Manager manifests reside in `winget/karefined-eng.EleViewer*.yaml`.

## Validation
- Run the full root-level test suite with `python -m pytest`.
- If the change touches a viewer, do a quick manual smoke check by launching the app with `python main.py`.

## Tool Quirks and Environment Traps

- Windows PowerShell `Select-String` does not support a `-Recurse` parameter. Use `rg` or pipe `Get-ChildItem -Recurse` results into `Select-String` instead.
- Windows PowerShell `Select-String` also does not support `-First`; pipe its output to `Select-Object -First N`.
- `gh run view --log` returns exit code 1 with “logs will be available when it is complete” while a workflow is still running; use the run JSON status until completion.
- Generated release files under `dist/` are not tracked in the tag source tree; retrieve `winget-installer.yaml` and checksums from the GitHub Release assets instead of the repository contents API.
- Large GitHub release downloads can emit a `wsarecv` connection error in PowerShell while leaving a partial file behind. Check the downloaded file size and hash before treating the command as successful; retry with a resumable/direct download if they do not match the release metadata.
- In PowerShell, quote `gh --jq` expressions containing version-like strings; otherwise the shell can strip JSON string quotes and jq reports an invalid token. When possible, use `gh ... --json` and parse the returned object in PowerShell.
- `gh api --input` rejects JSON files written with Windows PowerShell's UTF-8 BOM. Write API payloads with Python or .NET UTF-8 without a BOM before submitting GitHub Git-object requests.

- Git ignore patterns do not treat an inline `#` as a comment when it appears after a pattern. Keep explanatory comments on their own line; otherwise a pattern such as `EleViewer_Setup_*.exe  # ...` will not ignore matching installers.
- The worktree directory name may not change when the session branch is renamed. Searching under `C:\Users\asamoah\copilot-worktrees\eleviewer\elevonprospera-eng-commit-onboarding-update` failed with `Search paths do not exist` even though that was the branch name. Use the actual workspace path (`C:\Users\asamoah\copilot-worktrees\eleviewer\elevonprospera-eng-fantastic-garbanzo`) or omit the path to search from the current repository root.
- `docs/AGENTS.md` points to this file for operational guidance. `docs/origin.md` records only documented product purpose, not an inferred historical origin story.
- **Pytest unavailable / dependency installation blocked:** `python -m pytest` failed with `No module named pytest`. Installing project requirements and pytest failed because the environment could not resolve `files.pythonhosted.org` (`getaddrinfo failed`). Do not treat the suite as passing; report the blocker and use available syntax/static checks until dependencies can be installed.
- **Windows PowerShell command chaining:** This environment's PowerShell does not support `&&` or `||`. Chain commands with `;` and check `$LASTEXITCODE` or `$?` explicitly before dependent steps.
- **Mixed staged and unstaged documentation edits:** Interactive `git add -p` piped through PowerShell can stage unexpected hunks or leave prompts ambiguous. Inspect the index and working-tree diffs separately; use a narrowly scoped patch or index-only update, then verify `git diff --cached` before committing.
- `git merge origin/main` can fail with `Your local changes to the following files would be overwritten by merge` when an uncommitted edit overlaps an incoming change. After approval, `git merge --autostash origin/main` may create the merge commit but fail to reapply the autostash with `Applying autostash resulted in conflicts.` Git keeps the backup in `git stash list`. Resolve overlapping edits by combining both sides, verify each stashed change is represented in the merged tree or worktree, and only then drop the autostash.
- **Offscreen Qt capture caveat:** Capturing this PySide6 UI with `QT_QPA_PLATFORM=offscreen` rendered text as square missing-glyph boxes. The requested `QMainWindow.resize(800, 600)` also yielded a captured size of `804x844` because the non-scrollable welcome content imposed a taller minimum. Treat offscreen text pixels as unreliable; use Qt widget dimensions/accessibility or a real Windows display capture for visual-copy verification, and check the captured image dimensions rather than assuming a resize request took effect.
- **Qt debounce test timing:** A test that waited just longer than a `QTimer` interval intermittently asserted against stale UI state under the full suite. Stop the timer and emit its `timeout` signal directly when testing the debounced callback's resulting state; reserve real-time delay tests for the timer behavior itself.
- **Stale publishing-documentation URLs:** `web_fetch` returned 404 for the older Microsoft Learn paths `.../windows/apps/publish/publish-your-app/msix/upload-your-app-to-the-store` and `.../packaging-uwp-apps`, the Chocolatey path `.../create/create-packages/automatic-packages/`, and guessed Npackd/PortableApps submission paths. The Scoop wiki pages for app manifests/main-bucket criteria returned “You can’t perform that action at this time.” Use the current Learn signing overview (`https://learn.microsoft.com/en-us/windows/msix/package/signing-package-overview`) and developer-account page (`https://learn.microsoft.com/en-us/windows/apps/publish/partner-center/open-a-developer-account`); for Scoop requirements, use the working `https://raw.githubusercontent.com/ScoopInstaller/.github/main/.github/CONTRIBUTING.md`, Scoop Extras repository README, and raw Scoop README. For Chocolatey, use the current package-creation and moderation docs at `https://docs.chocolatey.org/en-us/create/create-packages/` and `https://docs.chocolatey.org/en-us/community-repository/moderation/`. Verify canonical URLs before relying on older publishing links.
- **Patch context for cross-file edits:** A patch that targeted `web_panel.py` with `ui.py` context failed because the WebPanel construction handler lives in `ui.py`. Apply module-specific hunks separately and verify the target file before retrying.
- **Patch context for test edits:** A multi-file patch partially applied before failing when a test's expected assertion context differed. Inspect each changed file after a partial patch and retry only the failed hunk.
- **Qt test shutdown:** A focused pytest run containing full `MainWindow` UI tests emitted its complete result but did not exit promptly after completion. Read the result before stopping the process; use non-UI targeted tests for fast iteration and treat the reported result as valid only after the process is stopped explicitly.
- **Repository-wide compileall:** `python -m compileall -q .` reaches `src/scratch/test_script.py`, which contains null bytes and fails compilation. Compile changed production modules explicitly; do not treat this scratch-file failure as a regression in the application code.
- **Viewer test names:** There is no `test_xlsx_viewer.py`; XLSX coverage is included in `test_all_ui_actions.py`. Use the existing `test_pptx_viewer.py`, `test_csv_viewer.py`, `test_tsv_viewer.py`, and targeted UI tests instead of assuming one test file per viewer.
- **Full-suite Qt/TTS crash:** A repository-wide pytest run terminated with Windows fatal exception `0x80000003` while background `tts_engine.py` threads were active during `test_link_interception.py`. The focused changed-module, viewer, security, UI, settings, and shortcut suites pass; investigate TTS test isolation separately before treating the full suite as reliable.
- **Selective staging of mixed hunks:** Building a cached patch by splitting on `@@ ` can drop the first hunk header and produce `patch with only garbage`. Preserve each complete hunk delimiter (for example with a regex matching `^@@ .*`) before passing the patch to `git apply --cached`.
- **GitHub large-file rejection:** Pushing a generated `EleViewer_Setup_v1.3.6.exe` failed because GitHub rejects files over 100 MB; the 125.75 MB installer must remain a release artifact rather than a repository file.
- **PowerShell URL query parsing:** An unquoted `gh api repos/.../issues?state=all&per_page=100` command fails because PowerShell treats `&` as an operator. Quote the endpoint (`"repos/.../issues?state=all&per_page=100"`) before passing it to `gh api`.
- **QtWebEngine test cache warnings:** Web Panel tests can pass while Chromium logs cache errors such as `Unable to move the cache: Access is denied` and `Unable to create cache` when a prior QtWebEngine process still holds the profile cache. Treat these as test-environment cleanup warnings unless the test itself fails; rerun after the process exits if cache behavior is under investigation.
- **Unavailable security-review skill name:** The requested `security-review` skill name was not registered; the available equivalent is `review-security`, which must be loaded before invoking the security-review agent.
- **pip-audit unavailable:** `python -m pip_audit` failed with `No module named pip_audit`. Use the installed package list and static dependency review unless the audit tool is explicitly added or can be installed.
- **Patch context after creating handoff files:** A later multi-file patch can fail when the newly created file is not represented in the current Git diff context. Read the file and apply its replacement hunk separately.
- **pip-compile hash resolution:** `pip-compile --generate-hashes --output-file=requirements.lock.txt requirements.txt` produced no output and remained running for several minutes in this environment. Stop it rather than leaving a resolver process active; use exact pins and CI `pip-audit` until a clean release environment can generate platform-specific hashes.
- **pip-audit network resolution:** `pip-audit -r requirements.lock.txt --strict` also remained silent beyond two minutes locally. Stop it and rely on the CI audit job, where the package advisory service has normal network access.
- **Qt deleted C++ object RuntimeError guard:** PySide6 widgets whose C++ object has been destroyed (e.g., when a parent tab is closed) raise `RuntimeError: Internal C++ object already deleted` on any method call. `hasattr()` only checks the Python wrapper, not whether the C++ object is still alive. When accessing a Qt widget whose parent tab or dialog may have been destroyed while signal-slot connections remain live, wrap the access in `try/except RuntimeError`:
```python
try:
    self.welcome_search_guidance.setText(...)
except RuntimeError:
    # C++ QObject was deleted; signal connection is stale. Guard against crash.
    pass
```
- **PowerShell head/tail unavailable:** Windows PowerShell 5.1 does not provide `head` or `tail` cmdlets. Use `Select-Object -First N` for the first N lines and `Select-Object -Last N` for the last N lines:
```powershell
command | Select-Object -First 10   # instead of command | head -10
command | Select-Object -Last 20    # instead of command | tail -20
```
- **PowerShell mkdir -p unavailable:** Windows PowerShell 5.1's `mkdir` does not support the Unix `-p` recursive flag. Create directories recursively with:
```powershell
New-Item -ItemType Directory -Force -Path docs/api, docs/features
```
