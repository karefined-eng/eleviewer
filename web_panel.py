"""Tabbed web panel with persisted URLs using QtWebEngine."""

from PySide6.QtCore import Signal, QUrl, QTimer
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
                from settings import load_settings
                if not load_settings().get("web_ad_blocker", True):
                    return
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
        _web_profile.setHttpCacheMaximumSize(50 * 1024 * 1024)  # Cap HTTP cache at 50 MB
        _web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        
        settings = _web_profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        from settings import load_settings
        webgl_enabled = load_settings().get("web_webgl", False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, webgl_enabled)
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
                page.fullScreenRequested.connect(self._handle_fullscreen)

            def _handle_fullscreen(self, request):
                request.accept()
                if request.toggleOn():
                    if getattr(self, '_fs_window', None):
                        return
                    
                    panel = self.parent()
                    while panel and not hasattr(panel, 'tabs'):
                        panel = panel.parent()
                    
                    if not panel:
                        self.setWindowFlag(Qt.Window, True)
                        self.setWindowFlag(Qt.FramelessWindowHint, True)
                        self.showFullScreen()
                        return
                        
                    self._fs_panel = panel
                    self._saved_tab_index = panel.tabs.indexOf(self)
                    self._saved_tab_text = panel.tabs.tabText(self._saved_tab_index)
                    
                    from PySide6.QtWidgets import QWidget, QVBoxLayout
                    self._fs_window = QWidget(panel.window())
                    self._fs_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
                    layout = QVBoxLayout(self._fs_window)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(self)
                    self._fs_window.showFullScreen()
                else:
                    if getattr(self, '_fs_window', None):
                        self._fs_window.hide()
                        self._fs_panel.tabs.insertTab(self._saved_tab_index, self, self._saved_tab_text)
                        self._fs_panel.tabs.setCurrentWidget(self)
                        self._fs_window.deleteLater()
                        del self._fs_window
                    else:
                        self.setWindowFlag(Qt.Window, False)
                        self.setWindowFlag(Qt.FramelessWindowHint, False)
                        self.show()
                
            def _auto_deny_permissions(self, security_origin, feature):
                self.page().setFeaturePermission(security_origin, feature, QWebEnginePage.PermissionPolicy.PermissionDeniedByUser)

            def _inject_ad_blocker(self, ok):
                from settings import load_settings
                if ok and load_settings().get("web_ad_blocker", True):
                    js = """
                    (function() {
                        if (window._eleAdBlock) return;
                        window._eleAdBlock = true;
                        setInterval(function() {
                            var btn = document.querySelector('.ytp-ad-skip-button, .ytp-skip-ad-button, .ytp-ad-skip-button-modern');
                            if (btn) {
                                btn.click();
                                btn.click();
                            }
                            var ads = document.querySelectorAll('.video-ads, .ytp-ad-module, .ytp-ad-overlay-container, #player-ads');
                            ads.forEach(function(a) { a.style.display = 'none'; });
                            
                            var adShowing = document.querySelector('.ad-showing');
                            if (adShowing) {
                                var video = document.querySelector('video');
                                if (video && video.duration) video.currentTime = video.duration;
                            }
                        }, 500);
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
                # Keys forwarded to the main application window unchanged.
                # NOTE: Ctrl+F is intentionally absent — it opens the
                # in-panel find bar via the explicit handler below.
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
                    (Qt.ControlModifier, Qt.Key_H),
                    (Qt.ControlModifier | Qt.ShiftModifier, Qt.Key_T),
                    (Qt.ControlModifier | Qt.ShiftModifier, Qt.Key_F),
                    (Qt.ControlModifier | Qt.ShiftModifier, Qt.Key_S),
                    (Qt.NoModifier, Qt.Key_F9),
                }
                # Ctrl+F → route to the parent WebPanel's in-page find bar.
                # We traverse up because QWebEngineView sits inside containers.
                if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F:
                    panel = self.parent()
                    while panel and not hasattr(panel, "_toggle_find_bar"):
                        panel = panel.parent()
                    if panel:
                        panel._toggle_find_bar()
                        event.accept()
                        return
                key_combo = (event.modifiers(), event.key())
                if key_combo in _APP_SHORTCUT_KEYS:
                    from PySide6.QtCore import QCoreApplication
                    QCoreApplication.sendEvent(self.window(), event)
                    event.accept()
                    return
                super().keyPressEvent(event)

            def wheelEvent(self, event):
                """Ctrl+ScrollWheel zooms the web page."""
                if event.modifiers() == Qt.ControlModifier:
                    panel = self.parent()
                    while panel and not hasattr(panel, "_zoom_in"):
                        panel = panel.parent()
                    if panel:
                        delta = event.angleDelta().y()
                        if delta > 0:
                            panel._zoom_in()
                        elif delta < 0:
                            panel._zoom_out()
                        event.accept()
                        return
                super().wheelEvent(event)

            def contextMenuEvent(self, event):
                """Custom right-click menu with app-relevant actions."""
                from settings import load_settings
                if not load_settings().get("web_context_menus", False):
                    event.accept()
                    return
                try:
                    from PySide6.QtWidgets import QMenu, QApplication
                    from icons import icon as _icon
                    menu = QMenu(self)
                    page = self.page()
                    hit = page.contextMenuData()

                    # Navigation
                    back_act = menu.addAction(_icon("chevron-left", size=16), "Back")
                    back_act.setEnabled(self.history().canGoBack())
                    back_act.triggered.connect(self.back)

                    fwd_act = menu.addAction(_icon("chevron-right", size=16), "Forward")
                    fwd_act.setEnabled(self.history().canGoForward())
                    fwd_act.triggered.connect(self.forward)

                    reload_act = menu.addAction(_icon("refresh-cw", size=16), "Reload")
                    reload_act.triggered.connect(self.reload)

                    menu.addSeparator()

                    # Link actions (when right-clicking a link)
                    link_url = hit.linkUrl() if hit else QUrl()
                    if link_url.isValid() and not link_url.isEmpty():
                        open_tab_act = menu.addAction("Open Link in New Tab")
                        open_tab_act.triggered.connect(
                            lambda: self._open_link_in_new_tab(link_url))

                        copy_link_act = menu.addAction("Copy Link Address")
                        copy_link_act.triggered.connect(
                            lambda: QApplication.clipboard().setText(link_url.toString()))
                        menu.addSeparator()

                    # Selection actions
                    if hit and hit.selectedText():
                        copy_act = menu.addAction("Copy")
                        copy_act.triggered.connect(lambda: page.triggerAction(
                            page.WebAction.Copy))
                        menu.addSeparator()

                    # Bookmark & Zoom
                    panel = self.parent()
                    while panel and not hasattr(panel, "_bookmark_current"):
                        panel = panel.parent()
                    if panel:
                        bm_act = menu.addAction(_icon("bookmark", size=16), "Bookmark This Page")
                        bm_act.triggered.connect(panel._bookmark_current)
                        menu.addSeparator()

                        zi_act = menu.addAction(_icon("zoom-in", size=16), "Zoom In")
                        zi_act.triggered.connect(panel._zoom_in)
                        zo_act = menu.addAction(_icon("zoom-out", size=16), "Zoom Out")
                        zo_act.triggered.connect(panel._zoom_out)
                        zr_act = menu.addAction("Reset Zoom")
                        zr_act.triggered.connect(panel._zoom_reset)

                    menu.exec(event.globalPos())
                except Exception:
                    import logging
                    logging.getLogger("eleviewer").exception("contextMenuEvent failed")
                    super().contextMenuEvent(event)

            def _open_link_in_new_tab(self, url):
                parent_w = self.parent()
                while parent_w and not hasattr(parent_w, "add_tab"):
                    parent_w = parent_w.parent()
                if parent_w:
                    parent_w.add_tab(url=url.toString(), title="Loading...")

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
    QToolButton, QTabBar, QProgressBar, QFrame, QLabel,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QKeySequence, QShortcut

from icons import icon
from settings import load_settings, save_settings, DEFAULT_WEB_TABS
from theme import compact_toolbar_stylesheet, ICON_SIZE_COMPACT


class WebPanel(QWidget):
    tabs_changed = Signal()

    _NAV_ICON_SZ = 16
    _FIND_ICON_SZ = 16
    _SEC_ICON_SZ = 14

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs_data = []
        self._is_loading = False  # tracks load state of the currently visible tab

        # Debounce timer: collapses rapid urlChanged / titleChanged /
        # currentChanged events into a single disk write after 800 ms of silence.
        self._persist_timer = QTimer(self)
        self._persist_timer.setSingleShot(True)
        self._persist_timer.setInterval(800)
        self._persist_timer.timeout.connect(self._do_persist_tabs)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Navigation row ────────────────────────────────────────────────
        nav = QHBoxLayout()
        nav.setContentsMargins(2, 2, 2, 0)
        self.nav_layout = nav  # exposed so the dock can merge its controls
        icon_sz = self._NAV_ICON_SZ
        icon_qsize = QSize(icon_sz, icon_sz)

        self.btn_back = QToolButton()
        self.btn_back.setIconSize(icon_qsize)
        self.btn_back.setIcon(icon("chevron-left", size=icon_sz))
        self.btn_back.setToolTip("Back")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._go_back)

        self.btn_forward = QToolButton()
        self.btn_forward.setIconSize(icon_qsize)
        self.btn_forward.setIcon(icon("chevron-right", size=icon_sz))
        self.btn_forward.setToolTip("Forward")
        self.btn_forward.setEnabled(False)
        self.btn_forward.clicked.connect(self._go_forward)

        # Refresh / Stop — icon swaps while page is loading
        self.btn_refresh = QToolButton()
        self.btn_refresh.setIconSize(icon_qsize)
        self.btn_refresh.setIcon(icon("refresh-cw", size=icon_sz))
        self.btn_refresh.setToolTip("Reload page (Ctrl+R / F5)")
        self.btn_refresh.clicked.connect(self._refresh_or_stop)

        # URL bar with a leading connection-security icon
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address\u2026")
        self.url_bar.returnPressed.connect(self._navigate_current)
        self._security_action = self.url_bar.addAction(
            icon("globe", size=self._SEC_ICON_SZ),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self._security_action.setVisible(False)

        self.btn_bookmark = QToolButton()
        self.btn_bookmark.setIconSize(icon_qsize)
        self.btn_bookmark.setIcon(icon("bookmark", size=icon_sz))
        self.btn_bookmark.setToolTip("Bookmark this web page (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self._bookmark_current)

        # Zoom % indicator (hidden when at 100%)
        self._zoom_label = QLabel()
        self._zoom_label.setStyleSheet(
            "font-size: 11px; color: #9b9b96; padding: 0 4px; min-width: 32px;"
        )
        self._zoom_label.setAlignment(Qt.AlignCenter)
        self._zoom_label.hide()

        self.btn_add = QToolButton()
        self.btn_add.setIconSize(icon_qsize)
        self.btn_add.setIcon(icon("plus", size=icon_sz))
        self.btn_add.setToolTip("New tab (Ctrl+T)")
        self.btn_add.clicked.connect(self.add_tab)

        self.btn_menu = QToolButton()
        self.btn_menu.setIconSize(icon_qsize)
        self.btn_menu.setIcon(icon("more-vertical", size=icon_sz))
        self.btn_menu.setToolTip("Menu")
        self.btn_menu.setPopupMode(QToolButton.InstantPopup)
        self.btn_menu.setMenu(self._build_nav_menu())

        for btn in (self.btn_back, self.btn_forward, self.btn_refresh,
                    self.btn_bookmark, self.btn_add, self.btn_menu):
            btn.setStyleSheet(compact_toolbar_stylesheet())
            btn.setFixedSize(28, 28)
            btn.setAutoRaise(True)

        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_forward)
        nav.addWidget(self.btn_refresh)
        nav.addWidget(self.url_bar, stretch=1)
        nav.addWidget(self._zoom_label)
        nav.addWidget(self.btn_bookmark)
        nav.addWidget(self.btn_add)
        nav.addWidget(self.btn_menu)

        # ── Tab widget ────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("QTabWidget::pane { border: none; }")
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # ── Loading progress bar (3 px strip below nav, hidden when idle) ─
        self._progress_bar = QProgressBar()
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(3)
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.hide()
        self._progress_bar.setStyleSheet(
            "QProgressBar { background: transparent; border: none; margin: 0; }"
            "QProgressBar::chunk { background: #4a9eff; border-radius: 1px; }"
        )

        # ── In-page find bar (hidden by default, opened by Ctrl+F) ────────
        self._find_bar = self._build_find_bar()

        # ── Download status bar (hidden by default) ───────────────────────
        self._download_bar = self._build_download_bar()

        layout.addLayout(nav)
        layout.addWidget(self._progress_bar)
        layout.addWidget(self.tabs)
        layout.addWidget(self._find_bar)
        layout.addWidget(self._download_bar)

        # ── Connect download handling on the shared profile ───────────────
        get_persistent_profile().downloadRequested.connect(self._on_download_requested)

        # ── Keyboard shortcuts ────────────────────────────────────────────
        QShortcut(QKeySequence("Ctrl+R"), self, self._refresh_or_stop)
        QShortcut(QKeySequence("F5"), self, self._refresh_or_stop)
        QShortcut(QKeySequence("F12"), self, self._toggle_devtools)

        # Ctrl+L: focus & select-all the URL bar
        sc_url = QShortcut(QKeySequence("Ctrl+L"), self)
        sc_url.setContext(Qt.WidgetWithChildrenShortcut)
        sc_url.activated.connect(self._focus_url_bar)

        # Ctrl+F: in-panel find bar (also routed here from the web view's
        # keyPressEvent override so Chromium doesn't swallow it).
        sc_find = QShortcut(QKeySequence("Ctrl+F"), self)
        sc_find.setContext(Qt.WidgetWithChildrenShortcut)
        sc_find.activated.connect(self._toggle_find_bar)

        # Zoom shortcuts
        for key in ("Ctrl+=", "Ctrl+Plus"):
            sc = QShortcut(QKeySequence(key), self)
            sc.setContext(Qt.WidgetWithChildrenShortcut)
            sc.activated.connect(self._zoom_in)
        sc_zout = QShortcut(QKeySequence("Ctrl+-"), self)
        sc_zout.setContext(Qt.WidgetWithChildrenShortcut)
        sc_zout.activated.connect(self._zoom_out)
        sc_zreset = QShortcut(QKeySequence("Ctrl+0"), self)
        sc_zreset.setContext(Qt.WidgetWithChildrenShortcut)
        sc_zreset.activated.connect(self._zoom_reset)

        # History and Downloads Shortcuts
        sc_hist = QShortcut(QKeySequence("Ctrl+Shift+H"), self)
        sc_hist.setContext(Qt.WidgetWithChildrenShortcut)
        sc_hist.activated.connect(self._show_history_dialog)

        sc_dl = QShortcut(QKeySequence("Ctrl+J"), self)
        sc_dl.setContext(Qt.WidgetWithChildrenShortcut)
        sc_dl.activated.connect(self._show_downloads_dialog)

        self.restore_tabs()

    def _import_cookies(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        path, _ = QFileDialog.getOpenFileName(self, "Import Cookies", "", "JSON Files (*.json)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cookies_data = json.load(f)
            store = get_persistent_profile().cookieStore()
            from PySide6.QtNetwork import QNetworkCookie
            from PySide6.QtCore import QDateTime, QUrl
            for c_data in cookies_data:
                c = QNetworkCookie(c_data["name"].encode('utf-8', 'ignore'), c_data["value"].encode('utf-8', 'ignore'))
                c.setDomain(c_data["domain"])
                c.setPath(c_data["path"])
                c.setSecure(c_data.get("secure", False))
                c.setHttpOnly(c_data.get("httpOnly", False))
                if "expirationDate" in c_data:
                    c.setExpirationDate(QDateTime.fromSecsSinceEpoch(int(c_data["expirationDate"])))
                domain = c_data["domain"]
                url_str = "https://" + (domain[1:] if domain.startswith(".") else domain) + c_data["path"]
                store.setCookie(c, QUrl(url_str))
            QMessageBox.information(self, "Import Successful", f"Successfully imported {len(cookies_data)} cookies.")
        except Exception as e:
            QMessageBox.warning(self, "Import Failed", f"Failed to import cookies:\n{str(e)}")

    def _export_cookies(self):
        self._exported_cookies = []
        store = get_persistent_profile().cookieStore()
        
        def on_cookie(c):
            self._exported_cookies.append(c)
            
        store.cookieAdded.connect(on_cookie)
        store.loadAllCookies()
        
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self._do_export_cookies(store, on_cookie))
        
    def _do_export_cookies(self, store, on_cookie_slot):
        try:
            store.cookieAdded.disconnect(on_cookie_slot)
        except Exception:
            pass
            
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        path, _ = QFileDialog.getSaveFileName(self, "Export Cookies", "", "JSON Files (*.json)")
        if not path: return
        try:
            out = []
            for c in self._exported_cookies:
                d = {
                    "name": c.name().data().decode('utf-8', 'ignore'),
                    "value": c.value().data().decode('utf-8', 'ignore'),
                    "domain": c.domain(),
                    "path": c.path(),
                    "secure": c.isSecure(),
                    "httpOnly": c.isHttpOnly(),
                }
                if not c.isSessionCookie():
                    d["expirationDate"] = c.expirationDate().toSecsSinceEpoch()
                out.append(d)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=4)
            QMessageBox.information(self, "Export Successful", f"Successfully exported {len(out)} cookies.")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"Failed to export cookies:\n{str(e)}")

    def _build_nav_menu(self):
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        
        act_hist = menu.addAction(icon("clock", size=14), "History")
        act_hist.setShortcut("Ctrl+Shift+H")
        act_hist.triggered.connect(self._show_history_dialog)
        
        act_dl = menu.addAction(icon("download", size=14), "Downloads")
        act_dl.setShortcut("Ctrl+J")
        act_dl.triggered.connect(self._show_downloads_dialog)
        
        menu.addSeparator()
        
        act_imp_cookie = menu.addAction(icon("upload", size=14), "Import Cookies...")
        act_imp_cookie.triggered.connect(self._import_cookies)
        
        act_exp_cookie = menu.addAction(icon("download", size=14), "Export Cookies...")
        act_exp_cookie.triggered.connect(self._export_cookies)

        menu.addSeparator()
        
        act_set = menu.addAction(icon("settings", size=14), "Settings")
        act_set.setShortcut("Alt+S")
        act_set.triggered.connect(self._open_settings)
        
        return menu

    def _show_history_dialog(self):
        from web_history import HistoryDialog
        dlg = HistoryDialog(self.window())
        dlg.url_requested.connect(self.open_url_in_new_tab)
        dlg.exec()

    def _show_downloads_dialog(self):
        from web_downloads import DownloadsDialog
        dlg = DownloadsDialog(self.window())
        dlg.exec()

    def _open_settings(self):
        window = self.window()
        if hasattr(window, "open_settings"):
            window.open_settings()

    # ─────────────────────────────────────────────────────────────────────
    # Find bar
    # ─────────────────────────────────────────────────────────────────────

    def _build_find_bar(self):
        bar = QFrame()
        bar.setObjectName("webFindBar")
        bar.hide()
        h = QHBoxLayout(bar)
        h.setContentsMargins(8, 3, 8, 3)
        h.setSpacing(4)

        lbl = QLabel("Find:")
        lbl.setStyleSheet("font-size: 12px;")

        self._find_input = QLineEdit()
        self._find_input.setPlaceholderText("Search in page\u2026")
        self._find_input.setMaximumWidth(240)
        self._find_input.returnPressed.connect(self._find_next)
        self._find_input.textChanged.connect(self._find_text_changed)

        self._find_result_lbl = QLabel()
        self._find_result_lbl.setStyleSheet(
            "color: #9b9b96; font-size: 11px; min-width: 60px;"
        )

        sz = self._FIND_ICON_SZ
        qsz = QSize(sz, sz)

        btn_prev = QToolButton()
        btn_prev.setIcon(icon("arrow-up", size=sz))
        btn_prev.setIconSize(qsz)
        btn_prev.setToolTip("Previous match (Shift+Enter)")
        btn_prev.setAutoRaise(True)
        btn_prev.clicked.connect(self._find_prev)

        btn_next = QToolButton()
        btn_next.setIcon(icon("arrow-down", size=sz))
        btn_next.setIconSize(qsz)
        btn_next.setToolTip("Next match (Enter)")
        btn_next.setAutoRaise(True)
        btn_next.clicked.connect(self._find_next)

        btn_close_find = QToolButton()
        btn_close_find.setIcon(icon("x", size=sz))
        btn_close_find.setIconSize(qsz)
        btn_close_find.setToolTip("Close find bar (Esc)")
        btn_close_find.setAutoRaise(True)
        btn_close_find.clicked.connect(self._close_find_bar)

        h.addWidget(lbl)
        h.addWidget(self._find_input)
        h.addWidget(btn_prev)
        h.addWidget(btn_next)
        h.addWidget(self._find_result_lbl)
        h.addStretch()
        h.addWidget(btn_close_find)

        bar.setStyleSheet(
            "#webFindBar {"
            "  background: #1c1c1c;"
            "  border-top: 1px solid #2c2c2c;"
            "}"
        )

        sc_esc = QShortcut(QKeySequence("Escape"), bar)
        sc_esc.setContext(Qt.WidgetWithChildrenShortcut)
        sc_esc.activated.connect(self._close_find_bar)

        return bar

    def _toggle_find_bar(self):
        if self._find_bar.isHidden():
            self._find_bar.show()
            self._find_input.setFocus()
            self._find_input.selectAll()
        else:
            self._close_find_bar()

    def _close_find_bar(self):
        self._find_bar.hide()
        view = self._current_view()
        if view:
            view.page().findText("")  # clear highlights
        self._find_input.clear()
        self._find_result_lbl.setText("")

    def _find_text_changed(self, text):
        view = self._current_view()
        if view:
            view.page().findText(text, resultCallback=self._on_find_result)

    def _find_next(self):
        view = self._current_view()
        if view:
            view.page().findText(
                self._find_input.text(),
                resultCallback=self._on_find_result,
            )

    def _find_prev(self):
        view = self._current_view()
        if view:
            from PySide6.QtWebEngineCore import QWebEnginePage
            view.page().findText(
                self._find_input.text(),
                QWebEnginePage.FindFlag.FindBackward,
                resultCallback=self._on_find_result,
            )

    def _on_find_result(self, result):
        """Update the match counter label from the findText callback."""
        try:
            n = result.numberOfMatches()
            idx = result.activeMatch()
            if n == 0 and self._find_input.text():
                self._find_result_lbl.setText("No matches")
                self._find_result_lbl.setStyleSheet(
                    "color: #f87171; font-size: 11px; min-width: 60px;"
                )
            else:
                self._find_result_lbl.setText(f"{idx}/{n}" if n else "")
                self._find_result_lbl.setStyleSheet(
                    "color: #9b9b96; font-size: 11px; min-width: 60px;"
                )
        except Exception:
            self._find_result_lbl.setText("")

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

    # ─────────────────────────────────────────────────────────────────────
    # Zoom controls
    # ─────────────────────────────────────────────────────────────────────

    _ZOOM_STEP = 0.10
    _ZOOM_MIN = 0.25
    _ZOOM_MAX = 5.0

    def _zoom_in(self):
        view = self._current_view()
        if view:
            factor = min(view.zoomFactor() + self._ZOOM_STEP, self._ZOOM_MAX)
            view.setZoomFactor(factor)
            self._update_zoom_label(factor)

    def _zoom_out(self):
        view = self._current_view()
        if view:
            factor = max(view.zoomFactor() - self._ZOOM_STEP, self._ZOOM_MIN)
            view.setZoomFactor(factor)
            self._update_zoom_label(factor)

    def _zoom_reset(self):
        view = self._current_view()
        if view:
            view.setZoomFactor(1.0)
            self._update_zoom_label(1.0)

    def _update_zoom_label(self, factor=None):
        if factor is None:
            view = self._current_view()
            factor = view.zoomFactor() if view else 1.0
        pct = round(factor * 100)
        if pct == 100:
            self._zoom_label.hide()
        else:
            self._zoom_label.setText(f"{pct}%")
            self._zoom_label.show()

    # ─────────────────────────────────────────────────────────────────────
    # Download handling
    # ─────────────────────────────────────────────────────────────────────

    def _build_download_bar(self):
        bar = QFrame()
        bar.setObjectName("webDownloadBar")
        bar.hide()
        h = QHBoxLayout(bar)
        h.setContentsMargins(8, 4, 8, 4)
        h.setSpacing(6)

        self._dl_filename = QLabel()
        self._dl_filename.setStyleSheet("font-size: 12px;")

        self._dl_progress = QProgressBar()
        self._dl_progress.setTextVisible(True)
        self._dl_progress.setFixedHeight(16)
        self._dl_progress.setFixedWidth(180)
        self._dl_progress.setRange(0, 100)

        self._dl_open_btn = QToolButton()
        self._dl_open_btn.setText("Open folder")
        self._dl_open_btn.setStyleSheet(
            "font-size: 11px; padding: 2px 8px; border: 1px solid #2c2c2c; border-radius: 4px;"
        )
        self._dl_open_btn.hide()
        self._dl_open_btn.clicked.connect(self._open_download_folder)

        btn_close_dl = QToolButton()
        btn_close_dl.setIcon(icon("x", size=14))
        btn_close_dl.setAutoRaise(True)
        btn_close_dl.setToolTip("Dismiss")
        btn_close_dl.clicked.connect(lambda: bar.hide())

        h.addWidget(self._dl_filename)
        h.addWidget(self._dl_progress)
        h.addWidget(self._dl_open_btn)
        h.addStretch()
        h.addWidget(btn_close_dl)

        bar.setStyleSheet(
            "#webDownloadBar {"
            "  background: #1c1c1c;"
            "  border-top: 1px solid #2c2c2c;"
            "}"
        )
        return bar

    def _on_download_requested(self, download):
        import os
        from pathlib import Path
        from settings import load_settings
        settings = load_settings()
        custom_dl = settings.get("default_download_folder", "").strip()
        if custom_dl and os.path.isdir(custom_dl):
            dl_dir = custom_dl
        else:
            dl_dir = str(Path.home() / "Downloads")
        download.setDownloadDirectory(dl_dir)
        filename = download.downloadFileName()

        self._dl_filename.setText(f"Downloading: {filename}")
        self._dl_progress.setValue(0)
        self._dl_open_btn.hide()
        self._download_bar.show()
        self._current_dl_path = os.path.join(dl_dir, filename)

        from web_downloads import track_download
        track_download(filename, self._current_dl_path, download.url().toString(), "Downloading")

        download.receivedBytesChanged.connect(
            lambda: self._on_dl_progress(download))
        download.isFinishedChanged.connect(
            lambda: self._on_dl_finished(download, filename))

        download.accept()

    def _on_dl_progress(self, download):
        total = download.totalBytes()
        received = download.receivedBytes()
        if total > 0:
            self._dl_progress.setValue(int(received * 100 / total))
        else:
            self._dl_progress.setRange(0, 0)  # indeterminate

    def _on_dl_finished(self, download, filename):
        self._dl_progress.setRange(0, 100)
        self._dl_progress.setValue(100)
        self._dl_filename.setText(f"Downloaded: {filename}")
        self._dl_open_btn.show()
        
        # Determine status
        from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
        status = "Completed" if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted else "Failed"
        from web_downloads import track_download
        track_download(filename, getattr(self, "_current_dl_path", ""), download.url().toString(), status)

    def _open_download_folder(self):
        import os, subprocess
        path = getattr(self, "_current_dl_path", "")
        folder = os.path.dirname(path) if path else str(__import__("pathlib").Path.home() / "Downloads")
        if os.path.isdir(folder):
            subprocess.Popen(["explorer", folder])

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
        try:
            from settings import load_settings
            def_zoom = int(load_settings().get("web_default_zoom", 100))
            if def_zoom != 100:
                view.setZoomFactor(max(0.25, min(5.0, def_zoom / 100.0)))
        except Exception:
            pass
        view.setUrl(QUrl(url))
        view.urlChanged.connect(lambda u, v=view: self._on_url_changed(v, u))
        view.titleChanged.connect(lambda t, v=view: self._on_title_changed(v, t))
        view.iconChanged.connect(lambda ico, v=view: self._on_icon_changed(v, ico))
        view.loadStarted.connect(lambda v=view: self._on_load_started(v))
        view.loadProgress.connect(lambda p, v=view: self._on_load_progress(v, p))
        view.loadFinished.connect(lambda ok, v=view: self._on_load_finished(v, ok))
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

    # ─────────────────────────────────────────────────────────────────────
    # Load lifecycle — progress bar + Stop/Refresh toggle
    # ─────────────────────────────────────────────────────────────────────

    def _on_load_started(self, view):
        if self.tabs.currentWidget() is not view:
            return
        self._is_loading = True
        self._progress_bar.setValue(0)
        self._progress_bar.show()
        self.btn_refresh.setIcon(icon("x", size=self._NAV_ICON_SZ))
        self.btn_refresh.setToolTip("Stop loading")

    def _on_load_progress(self, view, progress):
        if self.tabs.currentWidget() is not view:
            return
        self._progress_bar.setValue(progress)

    def _on_load_finished(self, view, ok):
        if self.tabs.currentWidget() is not view:
            return
        self._is_loading = False
        self._progress_bar.hide()
        self._progress_bar.setValue(0)
        self.btn_refresh.setIcon(icon("refresh-cw", size=self._NAV_ICON_SZ))
        self.btn_refresh.setToolTip("Reload page (Ctrl+R / F5)")
        self._update_nav_state()

    def _refresh_or_stop(self):
        """Reload when idle; stop when a page is loading."""
        view = self._current_view()
        if not view:
            return
        if self._is_loading:
            view.stop()
            self._is_loading = False
            self._progress_bar.hide()
            self._progress_bar.setValue(0)
            self.btn_refresh.setIcon(icon("refresh-cw", size=self._NAV_ICON_SZ))
            self.btn_refresh.setToolTip("Reload page (Ctrl+R / F5)")
        else:
            view.reload()

    # ─────────────────────────────────────────────────────────────────────
    # Navigation helpers
    # ─────────────────────────────────────────────────────────────────────

    def _update_nav_state(self):
        """Enable/disable back & forward buttons to reflect history."""
        view = self._current_view()
        if view:
            self.btn_back.setEnabled(view.history().canGoBack())
            self.btn_forward.setEnabled(view.history().canGoForward())
        else:
            self.btn_back.setEnabled(False)
            self.btn_forward.setEnabled(False)

    def _update_security_indicator(self, url):
        """Color-code the leading globe icon to reflect connection security."""
        scheme = url.scheme().lower() if hasattr(url, "scheme") else ""
        if scheme == "https":
            ico = icon("globe", size=self._SEC_ICON_SZ, color="#4ade80")
            tip = "Secure connection (HTTPS)"
        elif scheme == "http":
            ico = icon("globe", size=self._SEC_ICON_SZ, color="#f59e0b")
            tip = "Not secure (HTTP)"
        elif scheme == "file":
            ico = icon("folder-open", size=self._SEC_ICON_SZ)
            tip = "Local file"
        else:
            self._security_action.setVisible(False)
            return
        self._security_action.setIcon(ico)
        self._security_action.setToolTip(tip)
        self._security_action.setVisible(True)

    def _focus_url_bar(self):
        """Focus and select-all the URL bar (Ctrl+L)."""
        self.url_bar.setFocus()
        self.url_bar.selectAll()

    def _on_tab_changed(self, index):
        # Reset loading visuals so they match the newly focused tab
        self._is_loading = False
        self._progress_bar.hide()
        self._progress_bar.setValue(0)
        self.btn_refresh.setIcon(icon("refresh-cw", size=self._NAV_ICON_SZ))
        self.btn_refresh.setToolTip("Reload page (Ctrl+R / F5)")
        view = self._current_view()
        if view:
            url = view.url()
            self.url_bar.setText(url.toString())
            self._update_security_indicator(url)
        self._update_nav_state()
        self._update_zoom_label()
        self._schedule_persist()

    def _on_url_changed(self, view, url):
        if self.tabs.currentWidget() is view:
            self.url_bar.setText(url.toString())
            self._update_security_indicator(url)
        idx = self.tabs.indexOf(view)
        if 0 <= idx < len(self._tabs_data):
            self._tabs_data[idx]["url"] = url.toString()
            # Update tooltip with current title + URL
            title = self._tabs_data[idx].get("title", "")
            self.tabs.setTabToolTip(idx, f"{title}\n{url.toString()}")
        
        # Track history
        try:
            from web_history import track_visit
            track_visit(url.toString(), view.title() if view else url.toString())
        except Exception:
            pass
            
        self._schedule_persist()

    def _on_title_changed(self, view, title):
        idx = self.tabs.indexOf(view)
        if idx >= 0 and title:
            short = title[:20] + ("\u2026" if len(title) > 20 else "")
            self.tabs.setTabText(idx, short)
            if idx < len(self._tabs_data):
                self._tabs_data[idx]["title"] = title
            # Update tooltip with full title + URL
            url_str = view.url().toString() if view else ""
            self.tabs.setTabToolTip(idx, f"{title}\n{url_str}")
        
        # Track history update
        try:
            from web_history import track_visit
            if view and view.url().isValid():
                track_visit(view.url().toString(), title)
        except Exception:
            pass
            
        self._schedule_persist()

    def _on_icon_changed(self, view, web_icon):
        """Show the site favicon on the tab strip."""
        idx = self.tabs.indexOf(view)
        if idx >= 0 and not web_icon.isNull():
            self.tabs.setTabIcon(idx, web_icon)

    def _navigate_current(self):
        """Navigate the current tab, or fall back to a Google search."""
        view = self._current_view()
        if not view:
            return
        text = self.url_bar.text().strip()
        if not text:
            return
        if text.startswith(("http://", "https://", "file://", "ftp://")):
            url = text
        elif "." in text and " " not in text:
            # Bare domain like "example.com" or "github.com/user/repo"
            url = "https://" + text
        else:
            # Free-text search query
            from urllib.parse import quote_plus
            from settings import load_settings
            engine = load_settings().get("web_search_engine", "google")
            if engine == "duckduckgo":
                url = "https://duckduckgo.com/?q=" + quote_plus(text)
            elif engine == "bing":
                url = "https://www.bing.com/search?q=" + quote_plus(text)
            else:
                url = "https://www.google.com/search?q=" + quote_plus(text)
        view.setUrl(QUrl(url))

    def _go_back(self):
        view = self._current_view()
        if view:
            view.back()

    def _go_forward(self):
        view = self._current_view()
        if view:
            view.forward()


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

    def _schedule_persist(self):
        """Debounced persist: restarts the 800 ms timer on every rapid call."""
        self._persist_timer.start()

    def _do_persist_tabs(self):
        """Write tab state to disk (called by the debounce timer)."""
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

    def persist_tabs(self):
        """Immediate (synchronous) persist — used by add_tab and _close_tab."""
        self._persist_timer.stop()
        self._do_persist_tabs()
