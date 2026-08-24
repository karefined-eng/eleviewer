"""Tabbed web panel with persisted URLs using QtWebEngine."""

from PySide6.QtCore import Signal, QUrl
from paths import APP_DATA_DIR

WEB_AVAILABLE = True
_web_profile = None
_WebViewWrapperClass = None

def get_persistent_profile():
    global _web_profile
    if _web_profile is None:
        from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
        
        class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
            AD_KEYWORDS = (
                "doubleclick.net", "googlesyndication.com", "adservice.google.com",
                "youtube.com/pagead", "googleadservices.com", "/pagead/", "/adserver/",
                "adnxs.com", "amazon-adsystem.com"
            )
            def interceptRequest(self, info):
                url_str = info.requestUrl().toString()
                if any(kw in url_str for kw in self.AD_KEYWORDS):
                    info.block(True)

        from PySide6.QtCore import QCoreApplication
        _web_profile = QWebEngineProfile("eleviewer_web_profile", QCoreApplication.instance())
        _interceptor = AdBlockInterceptor(_web_profile)
        _web_profile.setUrlRequestInterceptor(_interceptor)
        storage_path = str(APP_DATA_DIR / "web_data")
        _web_profile.setPersistentStoragePath(storage_path)
        _web_profile.setCachePath(storage_path)
        _web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        
        settings = _web_profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, False)
    return _web_profile

def get_web_view_class():
    global _WebViewWrapperClass
    if _WebViewWrapperClass is None:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWebEngineCore import QWebEnginePage

        class _WebViewWrapperImpl(QWebEngineView):
            def __init__(self, parent=None):
                super().__init__(parent)
                page = QWebEnginePage(get_persistent_profile(), self)
                self.setPage(page)
                page.featurePermissionRequested.connect(self._auto_deny_permissions)
                page.loadFinished.connect(self._inject_ad_blocker)
                
            def _auto_deny_permissions(self, security_origin, feature):
                self.page().setFeaturePermission(security_origin, feature, QWebEnginePage.PermissionPolicy.PermissionDeniedByUser)

            def _inject_ad_blocker(self, ok):
                if ok:
                    js = """
                    (function() {
                        if (window._eleAdBlock) return;
                        window._eleAdBlock = true;
                        setInterval(function() {
                            var btn = document.querySelector('.ytp-ad-skip-button, .ytp-skip-ad-button, .ytp-ad-skip-button-modern');
                            if (btn) btn.click();
                            var ads = document.querySelectorAll('.video-ads, .ytp-ad-module, .ytp-ad-overlay-container, #player-ads');
                            ads.forEach(function(a) { a.style.display = 'none'; });
                        }, 1000);
                    })();
                    """
                    self.page().runJavaScript(js)

            def createWindow(self, type):
                parent_w = self.parent()
                while parent_w and not hasattr(parent_w, "add_tab"):
                    parent_w = parent_w.parent()
                if parent_w and hasattr(parent_w, "add_tab"):
                    new_view = parent_w.add_tab(url="about:blank", title="Loading...")
                    if new_view:
                        if hasattr(parent_w, "tabs"):
                            parent_w.tabs.setCurrentWidget(new_view)
                        return new_view
                return self
            
            def setUrl(self, qurl):
                super().setUrl(qurl)
                
            def setHtml(self, html, baseUrl=None):
                if baseUrl is not None:
                    super().setHtml(html, baseUrl)
                else:
                    super().setHtml(html)
                
            def url(self):
                return super().url()
                
            def back(self):
                super().back()
                
            def forward(self):
                super().forward()

            def keyPressEvent(self, event):
                _APP_SHORTCUT_KEYS = {
                    (Qt.NoModifier, Qt.Key_Escape),
                    (Qt.AltModifier, Qt.Key_V),
                    (Qt.AltModifier, Qt.Key_E),
                    (Qt.AltModifier, Qt.Key_S),
                    (Qt.ControlModifier, Qt.Key_Q),
                    (Qt.ControlModifier, Qt.Key_T),
                    (Qt.ControlModifier, Qt.Key_W),
                    (Qt.ControlModifier, Qt.Key_N),
                    (Qt.ControlModifier, Qt.Key_O),
                    (Qt.ControlModifier, Qt.Key_S),
                    (Qt.ControlModifier, Qt.Key_F),
                    (Qt.ControlModifier, Qt.Key_H),
                    (Qt.ControlModifier | Qt.ShiftModifier, Qt.Key_T),
                    (Qt.ControlModifier | Qt.ShiftModifier, Qt.Key_F),
                    (Qt.ControlModifier | Qt.ShiftModifier, Qt.Key_S),
                    (Qt.NoModifier, Qt.Key_F9),
                }
                key_combo = (event.modifiers(), event.key())
                if key_combo in _APP_SHORTCUT_KEYS:
                    from PySide6.QtCore import QCoreApplication
                    QCoreApplication.sendEvent(self.window(), event)
                    event.accept()
                    return
                super().keyPressEvent(event)

        _WebViewWrapperClass = _WebViewWrapperImpl
    return _WebViewWrapperClass

class _LazyWebViewMeta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, get_web_view_class())

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, get_web_view_class())

    def __call__(cls, *args, **kwargs):
        return get_web_view_class()(*args, **kwargs)

class WebViewWrapper(metaclass=_LazyWebViewMeta):
    pass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLineEdit,
    QToolButton, QTabBar,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QKeySequence, QShortcut

from icons import icon
from settings import load_settings, save_settings, DEFAULT_WEB_TABS
from theme import compact_toolbar_stylesheet, ICON_SIZE_COMPACT


class WebPanel(QWidget):
    tabs_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs_data = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav = QHBoxLayout()
        nav.setContentsMargins(4, 4, 4, 0)
        icon_sz = 24  # Larger icons for web panel
        icon_qsize = QSize(icon_sz, icon_sz)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("https://...")
        self.url_bar.returnPressed.connect(self._navigate_current)

        self.btn_back = QToolButton()
        self.btn_back.setIconSize(icon_qsize)
        self.btn_back.setIcon(icon("chevron-left", size=icon_sz))
        self.btn_back.setToolTip("Back")
        self.btn_back.clicked.connect(self._go_back)

        self.btn_forward = QToolButton()
        self.btn_forward.setIconSize(icon_qsize)
        self.btn_forward.setIcon(icon("chevron-right", size=icon_sz))
        self.btn_forward.setToolTip("Forward")
        self.btn_forward.clicked.connect(self._go_forward)

        self.btn_refresh = QToolButton()
        self.btn_refresh.setIconSize(icon_qsize)
        self.btn_refresh.setIcon(icon("refresh-cw", size=icon_sz))
        self.btn_refresh.setToolTip("Reload page (Ctrl+R / F5)")
        self.btn_refresh.clicked.connect(self._reload_current)

        self.btn_bookmark = QToolButton()
        self.btn_bookmark.setIconSize(icon_qsize)
        self.btn_bookmark.setIcon(icon("bookmark", size=icon_sz))
        self.btn_bookmark.setToolTip("Bookmark this web page (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self._bookmark_current)

        self.btn_add = QToolButton()
        self.btn_add.setIconSize(icon_qsize)
        self.btn_add.setIcon(icon("plus", size=icon_sz))
        self.btn_add.setToolTip("New tab")
        self.btn_add.clicked.connect(self.add_tab)

        for btn in (self.btn_back, self.btn_forward, self.btn_refresh, self.btn_bookmark, self.btn_add):
            btn.setStyleSheet(compact_toolbar_stylesheet())
            btn.setAutoRaise(True)

        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_forward)
        nav.addWidget(self.btn_refresh)
        nav.addWidget(self.url_bar, stretch=1)
        nav.addWidget(self.btn_bookmark)
        nav.addWidget(self.btn_add)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("QTabWidget::pane { border: none; }")
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addLayout(nav)
        layout.addWidget(self.tabs)

        QShortcut(QKeySequence("Ctrl+R"), self, self._reload_current)
        QShortcut(QKeySequence("F5"), self, self._reload_current)
        QShortcut(QKeySequence("F12"), self, self._toggle_devtools)

        self.restore_tabs()

    def _toggle_devtools(self):
        view = self._current_view()
        if not view:
            return
        if hasattr(self, "_devtools_window") and self._devtools_window:
            self._devtools_window.close()
            self._devtools_window = None
            return

        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        
        self._devtools_window = QDialog(self.window())
        self._devtools_window.setWindowTitle("Developer Tools")
        self._devtools_window.resize(800, 600)
        layout = QVBoxLayout(self._devtools_window)
        layout.setContentsMargins(0, 0, 0, 0)
        
        inspector_view = QWebEngineView(self._devtools_window)
        view.page().setDevToolsPage(inspector_view.page())
        layout.addWidget(inspector_view)
        
        self._devtools_window.finished.connect(lambda *args: setattr(self, "_devtools_window", None))
        self._devtools_window.show()

    def restore_tabs(self):
        settings = load_settings()
        tabs_data = settings.get("web_tabs") or DEFAULT_WEB_TABS.copy()
        self.tabs.blockSignals(True)
        while self.tabs.count():
            w = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if w:
                if hasattr(w, "page"):
                    w.page().deleteLater()
                w.deleteLater()
        self._tabs_data = []
        for tab in tabs_data:
            url = tab.get("url", "https://www.google.com")
            title = tab.get("title", "Web")
            self._add_tab_widget(url, title)
        if self.tabs.count() == 0:
            self.add_tab()
        self.tabs.blockSignals(False)
        self._on_tab_changed(self.tabs.currentIndex())

    def _add_tab_widget(self, url, title="Web"):
        if not WEB_AVAILABLE:
            return None
        view = WebViewWrapper()
        view.setUrl(QUrl(url))
        view.urlChanged.connect(lambda u, v=view: self._on_url_changed(v, u))
        view.titleChanged.connect(lambda t, v=view: self._on_title_changed(v, t))
        index = self.tabs.addTab(view, title)
        self._tabs_data.append({"title": title, "url": url})
        self.tabs.setCurrentIndex(index)
        return view

    def add_tab(self, url=None, title="New Tab"):
        if not WEB_AVAILABLE:
            return None
        if url is None or not isinstance(url, str) or not url:
            url = load_settings().get("web_url", "https://www.google.com")
        if not isinstance(title, str) or not title:
            title = "New Tab"
        view = self._add_tab_widget(url, title)
        self.persist_tabs()
        return view

    def open_url_in_new_tab(self, url_str, title="Live Feed"):
        if not WEB_AVAILABLE:
            return None
        target_local = QUrl(url_str).toLocalFile().lower() if url_str.lower().startswith("file:") else ""
        for i in range(self.tabs.count()):
            view = self.tabs.widget(i)
            if view and WEB_AVAILABLE:
                curr_str = view.url().toString()
                curr_local = view.url().toLocalFile().lower() if curr_str.lower().startswith("file:") else ""
                if curr_str == url_str or (target_local and curr_local == target_local):
                    self.tabs.setCurrentIndex(i)
                    view.reload()
                    return view
        view = self._add_tab_widget(url_str, title)
        self.persist_tabs()
        return view

    def reload_url(self, url_str):
        if not WEB_AVAILABLE:
            return False
        reloaded = False
        target_local = QUrl(url_str).toLocalFile().lower() if url_str.lower().startswith("file:") else ""
        for i in range(self.tabs.count()):
            view = self.tabs.widget(i)
            if view and WEB_AVAILABLE:
                curr_str = view.url().toString()
                curr_local = view.url().toLocalFile().lower() if curr_str.lower().startswith("file:") else ""
                if curr_str == url_str or (target_local and curr_local == target_local):
                    view.reload()
                    reloaded = True
        return reloaded

    def _close_tab(self, index):
        if self.tabs.count() <= 1:
            return
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if index < len(self._tabs_data):
            self._tabs_data.pop(index)
        if widget:
            if hasattr(widget, "page"):
                widget.page().deleteLater()
            widget.deleteLater()
        self.persist_tabs()


    def _current_view(self):
        w = self.tabs.currentWidget()
        return w if WEB_AVAILABLE else None

    def _on_tab_changed(self, index):
        view = self._current_view()
        if view:
            self.url_bar.setText(view.url().toString())
        self.persist_tabs()

    def _on_url_changed(self, view, url):
        if self.tabs.currentWidget() is view:
            self.url_bar.setText(url.toString())
        idx = self.tabs.indexOf(view)
        if 0 <= idx < len(self._tabs_data):
            self._tabs_data[idx]["url"] = url.toString()
        self.persist_tabs()

    def _on_title_changed(self, view, title):
        idx = self.tabs.indexOf(view)
        if idx >= 0 and title:
            short = title[:20] + ("…" if len(title) > 20 else "")
            self.tabs.setTabText(idx, short)
            if idx < len(self._tabs_data):
                self._tabs_data[idx]["title"] = title
        self.persist_tabs()

    def _navigate_current(self):
        view = self._current_view()
        if not view:
            return
        url = self.url_bar.text().strip()
        if url and not url.startswith("http"):
            url = "https://" + url
        view.setUrl(QUrl(url))

    def _go_back(self):
        view = self._current_view()
        if view:
            view.back()

    def _go_forward(self):
        view = self._current_view()
        if view:
            view.forward()

    def _reload_current(self):
        view = self._current_view()
        if view:
            view.reload()

    def _bookmark_current(self):
        view = self._current_view()
        if not view:
            return
        url_str = view.url().toString()
        title = view.title() or url_str
        try:
            from bookmark_manager import add_bookmark
            add_bookmark(label=title, file_path=url_str, page_number=0, scroll_position_y=0.0)
            window = self.window()
            if hasattr(window, "bookmarks_panel") and window.bookmarks_panel:
                window.bookmarks_panel.refresh()
            if hasattr(window, "update_bookmarks_menu"):
                window.update_bookmarks_menu()
            if hasattr(window, "show_status_message"):
                window.show_status_message(f"Bookmarked: {title}", 2500)
        except Exception as e:
            print(f"[WebPanel] Bookmark error: {e}")

    def persist_tabs(self):
        settings = load_settings()
        data = []
        for i in range(self.tabs.count()):
            view = self.tabs.widget(i)
            if view and WEB_AVAILABLE:
                data.append({
                    "title": self.tabs.tabText(i),
                    "url": view.url().toString(),
                })
        if data:
            settings["web_tabs"] = data
            save_settings(settings)
        self.tabs_changed.emit()
