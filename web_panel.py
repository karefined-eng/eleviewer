"""Tabbed web panel with persisted URLs using QtWebEngine."""

try:
    from PySide6.QtCore import Signal, QUrl
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
    from paths import APP_DATA_DIR
    
    # Create a persistent profile for the web engine
    _web_profile = None

    def get_persistent_profile():
        global _web_profile
        if _web_profile is None:
            # We must use a named profile to enable persistence (empty string = off-the-record)
            _web_profile = QWebEngineProfile("eleviewer_web_profile")
            storage_path = str(APP_DATA_DIR / "web_data")
            _web_profile.setPersistentStoragePath(storage_path)
            _web_profile.setCachePath(storage_path)
            _web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        return _web_profile

    class WebViewWrapper(QWebEngineView):
        # We define signals to match the old API so we don't have to rewrite the parent container
        
        def __init__(self, parent=None):
            super().__init__(parent)
            # Assign the persistent profile to this view's page
            page = QWebEnginePage(get_persistent_profile(), self)
            self.setPage(page)
        
        def setUrl(self, qurl):
            super().setUrl(qurl)
            
        def setHtml(self, html):
            super().setHtml(html)
            
        def url(self):
            return super().url()
            
        def back(self):
            super().back()
            
        def forward(self):
            super().forward()

    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

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
        icon_sz = ICON_SIZE_COMPACT
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

        self.btn_add = QToolButton()
        self.btn_add.setIconSize(icon_qsize)
        self.btn_add.setIcon(icon("plus", size=icon_sz))
        self.btn_add.setToolTip("New tab")
        self.btn_add.clicked.connect(self.add_tab)

        for btn in (self.btn_back, self.btn_forward, self.btn_add):
            btn.setStyleSheet(compact_toolbar_stylesheet())
            btn.setAutoRaise(True)

        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_forward)
        nav.addWidget(self.url_bar, stretch=1)
        nav.addWidget(self.btn_add)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addLayout(nav)
        layout.addWidget(self.tabs)

        self.restore_tabs()

    def restore_tabs(self):
        settings = load_settings()
        tabs_data = settings.get("web_tabs") or DEFAULT_WEB_TABS.copy()
        self.tabs.blockSignals(True)
        while self.tabs.count():
            self.tabs.removeTab(0)
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
            return
        view = WebViewWrapper()
        view.setUrl(QUrl(url))
        view.urlChanged.connect(lambda u, v=view: self._on_url_changed(v, u))
        view.titleChanged.connect(lambda t, v=view: self._on_title_changed(v, t))
        index = self.tabs.addTab(view, title)
        self._tabs_data.append({"title": title, "url": url})
        self.tabs.setCurrentIndex(index)

    def add_tab(self):
        if not WEB_AVAILABLE:
            return
        default_url = load_settings().get("web_url", "https://www.google.com")
        self._add_tab_widget(default_url, "New Tab")
        self.persist_tabs()

    def _close_tab(self, index):
        if self.tabs.count() <= 1:
            return
        self.tabs.removeTab(index)
        if index < len(self._tabs_data):
            self._tabs_data.pop(index)
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
