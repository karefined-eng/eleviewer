"""Web panel using QtWebEngineWidgets (bundled Chromium) with ad-blocking and security hardening."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton
)
import sys
import os
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor, QWebEnginePage
)

from theme import get_active_palette, get_brand_accent
from settings import load_settings, save_settings

WEB_AVAILABLE = True

# ── Persistent profile (shared across all views) ─────────────────────────────
_web_profile: QWebEngineProfile | None = None
_interceptor = None  # module-level ref keeps AdBlockInterceptor alive (prevents GC dangling-pointer crash)

def get_persistent_profile() -> QWebEngineProfile:
    global _web_profile
    if _web_profile is not None:
        return _web_profile

    settings_dict = load_settings()

    _web_profile = QWebEngineProfile("EleViewerWebProfile")
    _web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)

    # Persistent disk cache — avoids re-downloading assets on every session
    from paths import APP_DATA_DIR
    cache_dir = str(APP_DATA_DIR / "web_cache")
    storage_dir = str(APP_DATA_DIR / "web_storage")
    _web_profile.setCachePath(cache_dir)
    _web_profile.setPersistentStoragePath(storage_dir)

    # ── Ad / tracker blocker ──────────────────────────────────────────────────
    class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
        AD_KEYWORDS = (
            "doubleclick.net", "googlesyndication.com", "adservice.google.com",
            "youtube.com/pagead", "googleadservices.com", "/pagead/", "/adserver/",
            "adnxs.com", "amazon-adsystem.com",
        )
        def interceptRequest(self, info):
            url = info.requestUrl().toString()
            if any(kw in url for kw in self.AD_KEYWORDS):
                info.block(True)

    if settings_dict.get("web_enable_adblock", True):
        global _interceptor
        _interceptor = AdBlockInterceptor(_web_profile)
        _web_profile.setUrlRequestInterceptor(_interceptor)

    # ── Hardened WebEngine settings ───────────────────────────────────────────
    s = _web_profile.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, True)
    s.setAttribute(
        QWebEngineSettings.WebAttribute.JavascriptEnabled,
        settings_dict.get("web_enable_javascript", True)
    )

    return _web_profile


# ── Hardened WebView wrapper ──────────────────────────────────────────────────
class _SecureWebView(QWebEngineView):
    """QWebEngineView with permission denial, ad-skip JS, and popup intercept."""

    def __init__(self, parent=None):
        super().__init__(parent)
        page = QWebEnginePage(get_persistent_profile(), self)
        self.setPage(page)
        page.featurePermissionRequested.connect(self._auto_deny_permissions)
        if load_settings().get("web_enable_adblock", True):
            page.loadFinished.connect(self._inject_ad_blocker)

    def _auto_deny_permissions(self, security_origin, feature):
        """Block all permission requests (camera, mic, geo, notifications)."""
        self.page().setFeaturePermission(
            security_origin, feature,
            QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
        )

    def _inject_ad_blocker(self, ok):
        """Inject YouTube ad-skip + DOM ad-removal JS after every page load."""
        if not ok:
            return
        js = """
            (function() {
                if (window._eleAdBlock) return;
                window._eleAdBlock = true;
                setInterval(function() {
                    // Skip button
                    var btn = document.querySelector(
                        '.ytp-ad-skip-button, .ytp-skip-ad-button, .ytp-ad-skip-button-modern'
                    );
                    if (btn) btn.click();
                    // Hide overlay ad containers
                    var ads = document.querySelectorAll(
                        '.video-ads, .ytp-ad-module, .ytp-ad-overlay-container, #player-ads'
                    );
                    ads.forEach(function(a) { a.style.display = 'none'; });
                }, 1000);
            })();
        """
        self.page().runJavaScript(js)

    def createWindow(self, type):
        """Intercept target=_blank / window.open — open inside EleViewer, not a new OS window."""
        parent_w = self.parent()
        while parent_w and not hasattr(parent_w, "add_tab"):
            parent_w = parent_w.parent()
        if parent_w and hasattr(parent_w, "add_tab"):
            new_view = parent_w.add_tab(url="about:blank", title="Loading...")
            return new_view if isinstance(new_view, QWebEngineView) else self
        return self


# ── WebPanel widget ───────────────────────────────────────────────────────────
class WebPanel(QWidget):
    tabs_changed = Signal()
    expand_requested = Signal()
    url_changed = Signal(str)
    title_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        p = get_active_palette()
        accent = get_brand_accent()

        # Header / URL bar
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header.setStyleSheet(
            f"background: {p['BRAND_PANEL_2']}; border-bottom: 1px solid {p['BRAND_BORDER']}; color: {p['BRAND_PRIMARY']};"
        )

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Search or enter web address...")
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 18px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {accent};
                background: {p['BRAND_BACKGROUND']};
            }}
        """)
        self.url_input.returnPressed.connect(self._on_url_entered)

        btn_go = QPushButton("Go")
        btn_go.setCursor(Qt.PointingHandCursor)
        btn_go.setStyleSheet(f"""
            QPushButton {{
                background: {accent};
                color: white;
                border: none;
                border-radius: 18px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {p.get('BRAND_ACCENT_HOVER', accent)};
            }}
        """)
        btn_go.clicked.connect(self._on_url_entered)

        header_layout.addWidget(self.url_input, 1)
        header_layout.addWidget(btn_go)

        # Hardened WebView
        self.webview = _SecureWebView(self)
        self.webview.urlChanged.connect(self._on_url_changed)
        self.webview.titleChanged.connect(self._on_title_changed)
        self.webview.setStyleSheet(f"background: {p['BRAND_PANEL']};")

        layout.addWidget(header)
        layout.addWidget(self.webview, 1)

        self._status_callback = None
        # Dummy attribute so ui.py callers don't crash on .tabs.count()
        self.tabs = _DummyTabs()

    def _on_url_entered(self):
        url = self.url_input.text().strip()
        if not url:
            return
        self.open_url_in_new_tab(url)

    def _on_url_changed(self, url: QUrl):
        url_str = url.toString()
        self.url_input.setText(url_str)
        self.url_changed.emit(url_str)
        # Record in browsing history (fire-and-forget; title filled in later by titleChanged)
        try:
            from web_history import add_to_history
            add_to_history(url_str, "")
        except Exception:
            pass

    def _on_title_changed(self, title: str):
        self.title_changed.emit(title)
        # Back-fill the title for the most recent history entry
        try:
            from web_history import add_to_history
            current_url = self.webview.url().toString()
            if current_url and current_url != "about:blank":
                add_to_history(current_url, title)
        except Exception:
            pass

    def open_url_in_new_tab(self, url_str, title="Web"):
        if not url_str.startswith(("http://", "https://", "file://")):
            if "." in url_str and " " not in url_str:
                url_str = "https://" + url_str
            else:
                import urllib.parse
                url_str = "https://duckduckgo.com/?q=" + urllib.parse.quote(url_str)
        self.url_input.setText(url_str)
        self.webview.load(QUrl(url_str))

    def add_tab(self, url=None, title="New Tab"):
        if url:
            self.open_url_in_new_tab(url, title)
        else:
            self.url_input.setFocus()
        return self.webview  # single-view panel; return the view for createWindow

    def reload_url(self, url_str):
        self.webview.load(QUrl(url_str))

    def _close_tab(self, index):
        """For the single-view panel, closing navigates back to blank."""
        self.webview.load(QUrl("about:blank"))
        self.url_input.clear()

    def persist_tabs(self):
        """Return the current URL for session persistence."""
        url = self.webview.url().toString()
        return url if url and url != "about:blank" else None

    def _bookmark_current(self):
        """Bookmark the currently loaded web URL."""
        url = self.webview.url().toString()
        title = self.webview.title() or url
        if url and url not in ("about:blank", ""):
            try:
                from bookmark_manager import add_bookmark
                add_bookmark(url, label=title, page_number=0, scroll_position_y=0.0)
            except Exception:
                pass


class _DummyTabs:
    def count(self): return 0
    def currentIndex(self): return 0
