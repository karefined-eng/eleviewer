# EleViewer Python Application Rules & Directives

## Mandatory Context & Architecture Enforcement
Before creating or modifying any module in `eleviewer`, you MUST read and strictly adhere to `PROJECT_LOG.md` and `DEVELOPER_ONBOARDING.md`.

### Key Constraints:
1. **Zero Telemetry & PII Protection:** No analytics, no tracking, and no phone-home mechanisms. Unhandled exceptions and student feedback submitted via `feedback_dialog.py` MUST strip all user PII (such as Windows home directory paths via `os.path.expanduser("~")` -> `~`) before network transmission.
2. **UI & Theme Variable Consistency:** Do NOT hardcode hex color values (e.g., `#1c1c1c`, `#6cb6ff`) in PySide6 UI modules. Always import and reuse centralized theme constants (`BRAND_PRIMARY`, `BRAND_PANEL`, `BRAND_PANEL_2`, `BRAND_ACCENT`, `BRAND_BORDER`, `BRAND_BACKGROUND`) defined in `theme.py`, which mirror `eleviewer-site`'s CSS variables.
3. **Off-Thread Concurrency:** All network requests, file indexing, and auto-save operations MUST be executed on background `QThread` workers (e.g., `DraftWorker`, `VaultSearchWorker`, `FeedbackSubmitWorker`) to prevent UI freezes.
4. **Cognitive Load & Simplicity:** Preserve the lightweight, distraction-free "Sovereignty Workstation" philosophy. Avoid bloated toolbars or unnecessary configuration wizards. Maintain seamless support for the 4 Reflex keys (`Ctrl+Q`, `Alt+V`, `Ctrl+T`, `Ctrl+Shift+T`) and Universal TTS (`F9`).
5. **Atomic File Operations:** All settings and session saves MUST use atomic write patterns (`atomic_write`) to prevent 0-byte file corruption during sudden system shutdowns.
