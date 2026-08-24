import os
import re

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix paintEvent
old_paint_event = '''    def paintEvent(self, event):
        super().paintEvent(event)
        if self._drop_indicator_x < 0:
            return
        from PySide6.QtGui import QPainter, QPen, QColor
        from theme import get_active_accent
        painter = QPainter(self)
        pen = QPen(QColor(get_active_accent()["accent"]), 2)
        painter.setPen(pen)
        painter.drawLine(self._drop_indicator_x, 4, self._drop_indicator_x, self.height() - 4)
        painter.end()'''

new_paint_event = '''    def paintEvent(self, event):
        super().paintEvent(event)
        if self._drop_indicator_x < 0:
            return
        from PySide6.QtGui import QPainter, QPen, QColor
        from theme import get_active_accent
        painter = QPainter(self)
        try:
            pen = QPen(QColor(get_active_accent()["accent"]), 2)
            painter.setPen(pen)
            painter.drawLine(self._drop_indicator_x, 4, self._drop_indicator_x, self.height() - 4)
        finally:
            painter.end()'''

content = content.replace(old_paint_event, new_paint_event)

# 2. Overhaul _create_welcome_widget
match = re.search(r'    def _create_welcome_widget\(self\):.*?    def _replace_welcome_if_present\(self\):', content, flags=re.DOTALL)
if match:
    old_welcome = match.group(0)[:-len('    def _replace_welcome_if_present(self):')]
    
    new_welcome = '''    def _create_welcome_widget(self):
        w = QWidget()
        w.is_welcome_tab = True
        outer_layout = QGridLayout(w)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        content_w = QWidget()
        content_w.setMaximumWidth(800)
        main_layout = QVBoxLayout(content_w)
        main_layout.setContentsMargins(40, 60, 40, 60)
        main_layout.setSpacing(32)
        
        p = get_palette()
        
        # 1. Hero Section
        hero = QWidget()
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(0, 0, 0, 0)
        hero_layout.setSpacing(8)
        
        title = QLabel("EleViewer")
        title.setStyleSheet(f"""
            font-size: 42px; 
            font-weight: 800; 
            color: {p['BRAND_PRIMARY']};
            letter-spacing: -1px;
        """)
        
        subtitle = QLabel("Your local, zero-telemetry document workstation.")
        subtitle.setStyleSheet(f"""
            font-size: 16px; 
            color: {p['BRAND_MUTED_FG']};
        """)
        
        hero_layout.addWidget(title, 0, Qt.AlignLeft)
        hero_layout.addWidget(subtitle, 0, Qt.AlignLeft)
        main_layout.addWidget(hero)
        
        # 2. Omnibar Search
        omni_wrapper = QWidget()
        omni_wrapper.setObjectName("OmniWrapper")
        omni_wrapper.setStyleSheet(f"""
            QWidget#OmniWrapper {{
                background: {p['BRAND_PANEL']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 12px;
            }}
        """)
        omni_wrapper_layout = QVBoxLayout(omni_wrapper)
        omni_wrapper_layout.setContentsMargins(8, 8, 8, 8)
        omni_wrapper_layout.setSpacing(0)
        
        omni_bar_row = QWidget()
        omni_bar_layout = QHBoxLayout(omni_bar_row)
        omni_bar_layout.setContentsMargins(8, 0, 8, 0)
        omni_bar_layout.setSpacing(12)
        
        search_ico = QLabel()
        search_ico.setPixmap(icon("search", size=18).pixmap(18, 18))
        
        self.welcome_search = QLineEdit()
        self.welcome_search.setPlaceholderText("Search vault files or enter URL to browse...")
        self.welcome_search.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {p['BRAND_PRIMARY']};
                font-size: 15px;
                padding: 12px 0;
            }}
        """)
        
        omni_bar_layout.addWidget(search_ico)
        omni_bar_layout.addWidget(self.welcome_search)
        omni_wrapper_layout.addWidget(omni_bar_row)
        
        # 3. Hidden Search Results Dropdown
        self.omni_results = QListWidget()
        self.omni_results.hide()
        
        # Convert accent hex to rgba for the selected state
        accent_hex = p.get('BRAND_ACCENT', '#000000').lstrip('#')
        try:
            r, g, b = tuple(int(accent_hex[i:i+2], 16) for i in (0, 2, 4))
            accent_rgba = f"rgba({r}, {g}, {b}, 0.15)"
        except:
            accent_rgba = p.get('BRAND_PANEL_2', '#333333')

        self.omni_results.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                border-top: 1px solid {p['BRAND_BORDER']};
                outline: none;
                margin-top: 8px;
            }}
            QListWidget::item {{
                color: {p['BRAND_PRIMARY']};
                padding: 12px;
                border-radius: 6px;
            }}
            QListWidget::item:selected {{
                background: {accent_rgba};
                color: {p['BRAND_ACCENT']};
            }}
        """)
        self.omni_results.setMaximumHeight(220)
        omni_wrapper_layout.addWidget(self.omni_results)
        
        main_layout.addWidget(omni_wrapper)
        
        # Search logic
        def _do_search(text):
            text = text.strip()
            if not text:
                self.omni_results.hide()
                return
            
            if hasattr(self, 'vault_panel') and self.vault_panel.vault_selector.currentData():
                vault_path = self.vault_panel.vault_selector.currentData()
            else:
                settings = load_settings()
                vaults = settings.get("vault_paths", [])
                vault_path = vaults[0] if vaults else None
                
            if not vault_path:
                return
                
            results = []
            text_lower = text.lower()
            import os as _os
            for root, _, files in _os.walk(vault_path):
                if ".git" in root or "__pycache__" in root: continue
                for f in files:
                    if text_lower in f.lower():
                        results.append(_os.path.join(root, f))
                        if len(results) >= 8: break
                if len(results) >= 8: break
            
            self.omni_results.clear()
            if results:
                for r in results:
                    rel = _os.path.relpath(r, vault_path)
                    it = QListWidgetItem(rel)
                    it.setData(Qt.UserRole, r)
                    self.omni_results.addItem(it)
                self.omni_results.show()
            else:
                self.omni_results.hide()

        def _open_omni_result():
            if self.omni_results.isVisible() and self.omni_results.currentItem():
                path = self.omni_results.currentItem().data(Qt.UserRole)
                if path:
                    self._open_vault_file(path)
            else:
                # Check if it's a URL
                txt = self.welcome_search.text().strip()
                if txt.startswith("http://") or txt.startswith("https://") or ("." in txt and " " not in txt):
                    if not txt.startswith("http"):
                        txt = "https://" + txt
                    try:
                        from web_panel import WebBrowserPanel
                        browser = WebBrowserPanel(self)
                        self._add_editor_tab(browser, txt)
                        browser.load_url(txt)
                    except ImportError:
                        pass

        self.welcome_search.textChanged.connect(_do_search)
        self.welcome_search.returnPressed.connect(_open_omni_result)
        self.omni_results.itemClicked.connect(lambda: _open_omni_result())
        
        # 4. Action Buttons (Horizontal layout now)
        action_bar = QWidget()
        action_bar_layout = QHBoxLayout(action_bar)
        action_bar_layout.setContentsMargins(0, 0, 0, 0)
        action_bar_layout.setSpacing(12)
        
        actions = [
            ("Open File", "folder", self.open_file),
            ("New Blank", "file", self.new_tab),
            ("Settings", "settings", self.show_settings)
        ]
        
        for label, ico, slot in actions:
            btn = QToolButton()
            btn.setText(label)
            btn.setIcon(icon(ico))
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            btn.setStyleSheet(f"""
                QToolButton {{
                    background: {p['BRAND_PANEL']};
                    border: 1px solid {p['BRAND_BORDER']};
                    border-radius: 8px;
                    color: {p['BRAND_PRIMARY']};
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QToolButton:hover {{
                    background: {p['BRAND_PANEL_2']};
                    border-color: {p['BRAND_ACCENT']};
                    color: {p['BRAND_ACCENT']};
                }}
            """)
            action_bar_layout.addWidget(btn)
        
        action_bar_layout.addStretch()
        main_layout.addWidget(action_bar)
        
        # 5. Two Columns: Recent Files & Bookmarks
        columns = QWidget()
        cols_layout = QHBoxLayout(columns)
        cols_layout.setSpacing(40)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setAlignment(Qt.AlignTop)
        
        def _create_section(title, icon_name, items, click_handler, empty_text):
            col = QWidget()
            layout = QVBoxLayout(col)
            layout.setSpacing(12)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Header
            header = QWidget()
            h_layout = QHBoxLayout(header)
            h_layout.setContentsMargins(0, 0, 0, 0)
            ico_lbl = QLabel()
            ico_lbl.setPixmap(icon(icon_name, size=14).pixmap(14, 14))
            title_lbl = QLabel(title.upper())
            title_lbl.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
            h_layout.addWidget(ico_lbl)
            h_layout.addWidget(title_lbl)
            h_layout.addStretch()
            layout.addWidget(header)
            
            # List
            lst = QListWidget()
            lst.setStyleSheet(f"""
                QListWidget {{
                    background: transparent; 
                    border: none; 
                    outline: none; 
                }}
                QListWidget::item {{
                    color: {p['BRAND_PRIMARY']}; 
                    padding: 8px 12px; 
                    border-radius: 6px; 
                    margin-bottom: 2px;
                }}
                QListWidget::item:hover {{
                    background: {p['BRAND_PANEL_2']}; 
                    color: {p['BRAND_ACCENT']};
                }}
            """)
            if not items:
                i = QListWidgetItem(empty_text)
                i.setFlags(Qt.NoItemFlags)
                i.setForeground(QColor(p["BRAND_MUTED_FG"]))
                lst.addItem(i)
            else:
                for label, path, data in items:
                    i = QListWidgetItem(f"{label} \\n{path}")
                    i.setData(Qt.UserRole, data)
                    i.setToolTip(path)
                    lst.addItem(i)
                    
            lst.setFixedHeight(max(40, len(items or [1]) * 46))
            lst.itemClicked.connect(click_handler)
            layout.addWidget(lst)
            return col

        # Load lists
        import os as _os
        recent_files = load_recent_files(validate=True)[:6]
        recent_items = [(_os.path.basename(path), path, path) for path in recent_files]
        
        bms = load_settings().get("bookmarks", [])[:6]
        bm_items = [(b.get("label", "Bookmark"), b["file_path"], b) for b in bms]
        
        def _handle_recent(it):
            path = it.data(Qt.UserRole)
            if path: self._open_vault_file(path)
            
        def _handle_bm(it):
            b = it.data(Qt.UserRole)
            if b:
                self._open_vault_file(b["file_path"])
                w = self.tabs.currentWidget()
                if hasattr(w, "go_to_bookmark"): w.go_to_bookmark(b.get("page_number", 0), b.get("scroll_position_y", 0.0))

        cols_layout.addWidget(_create_section("Recent Files", "clock", recent_items, _handle_recent, "No recent files"))
        cols_layout.addWidget(_create_section("Bookmarks", "bookmark", bm_items, _handle_bm, "No bookmarks"))
        
        main_layout.addWidget(columns)
        main_layout.addStretch()
        
        outer_layout.addWidget(content_w, 0, Qt.AlignHCenter)
        return w
'''
    content = content.replace(old_welcome, new_welcome)
    with open('ui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced!")
else:
    print("Match not found!")
