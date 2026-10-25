# PPTX Viewer — P1 Fixes — 2026-10-25

Three verified-P1 defects in `pptx_viewer.py` were fixed, each with a
regression test. Suite result: 6/6 in `test_pptx_viewer.py`, plus
`test_all_ui_actions.py` + `test_user_journey.py` (9 passed, which also
exercised the new WebEngine/QWebChannel setup under real Chromium).

## 1. Title rendered twice on every standard slide

`load_from_path` copied the title-placeholder paragraph into the slide title
but left it in `elements` too — the h1 was immediately repeated as the first
body line on any deck with a real title placeholder. Same duplication existed
in `_fallback_zip_parse` (title repeated in body *and* TTS content).

**Fix:** per-shape placeholder check; first title-placeholder paragraph is
consumed as the title and skipped in the body. Fallback path now builds body
from `texts[1:]`. TTS `content` no longer contains the title string.

## 2. Search "no match" crashed QTextBrowser mode

`self.viewer.moveCursor(self.viewer.textCursor().Start)` — verified live:
PySide6 `QTextCursor` instances have no `.Start` attribute (scoped enums).
Any failed find in fallback mode raised `AttributeError`.

**Fix:** `self.viewer.moveCursor(QTextCursor.MoveOperation.Start)`. Dead
`QWebEngineView` import removed from `_perform_search`.

## 3. No scroll→slide sync in WebEngine mode (primary path)

The document is one continuous scroll, but `current_slide` only updated in
QTextBrowser mode. In the default WebEngine path, manual scrolling left the
counter/list stuck — bookmarks and TTS then targeted the wrong slide.

**Fix:** QWebChannel bridge (`_SlideScrollBridge`). Setup in `_setup_web_scroll_sync()`
(registered on the page in `__init__`); rendered HTML now embeds a scroll
listener (`qrc:///qtwebchannel/qwebchannel.js`) that debounces (120ms), finds
the `.slide-card` at ~35% viewport height, and reports it back. `go_to_slide`
switched from smooth to instant `scrollIntoView` so jump echoes resolve to the
target and no-op against the bridge's `index == current_slide` guard; the
`_is_jumping` gate still covers programmatic jumps. If QtWebChannel is
missing, setup is skipped and behavior is exactly as before.

## Not yet done (known P2/P3 backlog)

- Arrow Left/Right shortcuts (`WidgetWithChildrenShortcut`) hijack caret
  movement inside the search field.
- Monolithic synchronous render: all slides + base64 images in one HTML string
  on the GUI thread — memory ceiling on image-heavy decks, no progress UI.
- Parse failures only `print()`; `_status_callback` stored but never called.
- SmartArt/chart text and hyperlinks are not extracted; fallback loses
  text/image order.
