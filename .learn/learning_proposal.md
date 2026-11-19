# Learning Proposal

**Date:** 2026-11-18

## Summary

This proposal captures three environment constraints and coding standards learned during the EleViewer gap-analysis implementation session: (1) a Qt deleted-C++-object RuntimeError guard pattern for PySide6 widgets, (2) PowerShell 5.1 `head`/`tail` replacement with `Select-Object`, and (3) PowerShell 5.1 `mkdir -p` replacement with `New-Item`. All three are new and not currently covered in `AGENTS.md`.

---

## Candidate Learning 1: Qt Deleted C++ Object RuntimeError Guard

| Field | Value |
|---|---|
| **Trigger** | Accessing a Qt widget (e.g., QLabel, QPushButton) whose parent tab/dialog has been destroyed, while a signal-slot connection is still live |
| **Invariant** | Wrap Qt widget method calls in `try/except RuntimeError` when the widget's lifetime is tied to a tab or dialog that may be destroyed independently of the signal connection |
| **Evidence** | `ui.py:1296` fix (commit `6ae012c`): `RuntimeError: libshiboken: Internal C++ object (PySide6.QtWidgets.QLabel) already deleted` in `_refresh_welcome_search_guidance`, connected to `vaults_changed` signal |

### Classification
**Rule** — Can be satisfied with "Guard Qt widget access with try/except RuntimeError when widget lifetime is tied to a destroyable tab/dialog"

### Scope
**Workspace** — Specific to this repository's PySide6 codebase

### Proposed addition to AGENTS.md

```
## Qt Deleted C++ Object Guard

**Environment Trap:** PySide6 widgets whose C++ object has been destroyed (e.g., when a parent tab is closed) raise `RuntimeError: Internal C++ object already deleted` on any method call. `hasattr()` only checks the Python wrapper, not whether the C++ object is still alive.

**Workflow guardrail:** When accessing a Qt widget whose parent tab or dialog may have been destroyed while signal-slot connections remain live, wrap the access in `try/except RuntimeError`:

```python
try:
    self.welcome_search_guidance.setText(...)
except RuntimeError:
    # C++ QObject was deleted; signal connection is stale. Guard against crash.
    pass
```

**Files affected:** `ui.py` (commit `6ae012c`), any file connecting signals to widgets with independent lifetimes.
```

---

## Candidate Learning 2: PowerShell head/tail → Select-Object

| Field | Value |
|---|---|
| **Trigger** | Viewing the first or last N lines of command output in Windows PowerShell 5.1 |
| **Invariant** | Use `Select-Object -First N` or `Select-Object -Last N` instead of `head`/`tail`, which are not recognized cmdlets |
| **Evidence** | Failed commands: `tasklist ... | head -10`, `pytest ... 2>&1 | tail -20` — both returned "The term 'head'/'tail' is not recognized" |

### Classification
**Rule** — "Use Select-Object -First/-Last instead of head/tail in PowerShell"

### Scope
**Workspace** — This machine's PowerShell 5.1 environment used for EleViewer development

### Proposed addition to AGENTS.md

```
## PowerShell head/tail Unavailable

**Environment Trap:** Windows PowerShell 5.1 does not provide `head` or `tail` cmdlets. Piping to them returns "The term 'head'/'tail' is not recognized".

**Workflow guardrail:** Use `Select-Object -First N` for the first N lines and `Select-Object -Last N` for the last N lines:

```powershell
# Instead of: command | head -10
command | Select-Object -First 10

# Instead of: command | tail -20
command | Select-Object -Last 20
```

**Related:** Existing AGENTS.md rules already cover PowerShell `Select-String` limitations (no `-Recurse`/`-First`) and `&&`/`||` chaining limitations (lines 72-73, 84).
```

---

## Candidate Learning 3: PowerShell mkdir -p → New-Item

| Field | Value |
|---|---|
| **Trigger** | Creating directories recursively in Windows PowerShell 5.1 |
| **Invariant** | Use `New-Item -ItemType Directory -Force -Path <path>` instead of `mkdir -p`, which is not valid PowerShell syntax |
| **Evidence** | Failed command: `mkdir -p docs/api docs/features` — returned "A positional parameter cannot be found that accepts argument 'docs/features'" |

### Classification
**Rule** — "Use New-Item -ItemType Directory -Force instead of mkdir -p in PowerShell"

### Scope
**Workspace** — This machine's PowerShell 5.1 environment used for EleViewer development

### Proposed addition to AGENTS.md

```
## PowerShell mkdir -p Unavailable

**Environment Trap:** Windows PowerShell 5.1's `mkdir` (alias for `mkdir`/`md`) does not support the `-p` recursive flag from Unix. Use `New-Item` instead.

**Workflow guardrail:** Create directories recursively with:

```powershell
New-Item -ItemType Directory -Force -Path docs/api, docs/features
```

**Related:** Existing AGENTS.md rules already cover PowerShell `Select-String` limitations (no `-Recurse`/`-First`) and `&&`/`||` chaining limitations (lines 72-73, 84).
```

---

## Proposed Actions

1. **Update `AGENTS.md`** ("Tool Quirks and Environment Traps" section, lines 70-104) with the three rules above
2. No new skill files needed — all three are single-sentence do/don't constraints

---

## Awaiting Approval

Please approve:
- [ ] Add the Qt Deleted C++ Object Guard rule to AGENTS.md
- [ ] Add the PowerShell head/tail → Select-Object rule to AGENTS.md
- [ ] Add the PowerShell mkdir -p → New-Item rule to AGENTS.md
- [ ] All three together

---

## Notes

- The existing `.learn/learning_proposal.md` (dated 2025-10-27) was already completed ("Outcome Applied ✅") and will be replaced by this new proposal on approval.
- All three learnings trace to actual failed commands or fixes from this session — none are invented.

---

## Outcome Applied ✅

### Changes Applied

1. **AGENTS.md** — Added three new entries to "Tool Quirks and Environment Traps" (lines 106–122):
   - Qt deleted C++ object RuntimeError guard (`try/except RuntimeError` around Qt widget access)
   - PowerShell `head`/`tail` → `Select-Object -First`/`-Last`
   - PowerShell `mkdir -p` → `New-Item -ItemType Directory -Force`

### Verification

- Re-read `.agents/AGENTS.md` lines 106–122 and confirmed the exact text is present.
- Verified `ui.py` compiles after earlier Qt guard fix (commit `6ae012c`).

