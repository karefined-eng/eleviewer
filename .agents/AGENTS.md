# EleViewer Agent Guide

## Purpose
This repository is a Python + PySide6 desktop app for browsing and studying local documents. Keep changes small, local, and consistent with the current implementation.

## Working assumptions
- The app entry point is [main.py](../main.py).
- The main UI shell is [ui.py](../ui.py).
- File routing happens in [file_handler.py](../file_handler.py).
- Viewer-specific logic lives in [markdown_renderer.py](../markdown_renderer.py), [docx_viewer.py](../docx_viewer.py), [pptx_viewer.py](../pptx_viewer.py), [pdf_viewer.py](../pdf_viewer.py), [xlsx_viewer.py](../xlsx_viewer.py), and [csv_viewer.py](../csv_viewer.py).
- The app is intentionally lightweight. Prefer native Python/Qt rendering and small caching or debouncing changes over introducing new runtime dependencies.
- There is no Rust-based viewer implementation in the current repository; do not add Rust or PyO3 work unless the user explicitly asks for it.

## Before editing
- Read `README.md` and `DEVELOPER_ONBOARDING.md` before making architecture or implementation changes.
- Read the relevant module and nearby callers before changing behavior.
- Check whether the change should be covered by an existing test in the repository root (for example [test_markdown_renderer.py](../test_markdown_renderer.py)). Use `pytest -s <test_file>.py` to validate changes.
- If a change affects public module APIs, search for imports before editing.
- Website-specific UI/CSS changes belong in the `eleviewer-site` repository unless the user explicitly asks for desktop app changes.

## Implementation rules
- Keep UI responsiveness in mind for preview-heavy paths. Debouncing, caching, and skipping redundant renders are preferred when the user is typing or revisiting the same content.
- Preserve existing keyboard shortcuts and document navigation behavior unless the task explicitly changes them.
- Keep user-facing copy simple and direct.
- Avoid adding new packages unless the task truly requires them.

## Validation
- Run the relevant root-level tests with `pytest -s <test_file>.py`.
- If the change touches a viewer, do a quick manual smoke check by launching the app with `python main.py`.

