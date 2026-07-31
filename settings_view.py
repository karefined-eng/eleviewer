from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QSpinBox, QPushButton, QComboBox, QListWidget, 
    QStackedWidget, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from settings import load_settings, save_settings, DEFAULT_SETTINGS, DEFAULT_WEB_TABS
from theme import (
    MARKDOWN_ICON_SIZE_MIN, MARKDOWN_ICON_SIZE_MAX,
    resolve_markdown_icon_size, get_active_palette
)


class SettingCard(QFrame):
    """A modern card for a single setting toggle/input."""
    def __init__(self, title_text, desc_text, control_widget, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.title = QLabel(title_text)
        font = self.title.font()
        font.setBold(True)
        self.title.setFont(font)
        
        self.desc = QLabel(desc_text)
        self.desc.setWordWrap(True)
        
        text_layout.addWidget(self.title)
        text_layout.addWidget(self.desc)
        
        layout.addLayout(text_layout, 1)
        
        control_widget.setMinimumWidth(150)
        layout.addWidget(control_widget, 0, Qt.AlignVCenter | Qt.AlignRight)
        self.reload_theme()

    def reload_theme(self):
        p = get_active_palette()
        self.setStyleSheet(f"""
            #SettingCard {{
                background: {p['BRAND_PANEL']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 8px;
            }}
        """)
        self.title.setStyleSheet(f"color: {p['BRAND_PRIMARY']};")
        self.desc.setStyleSheet(f"color: {p['BRAND_MUTED_FG']};")


class SettingsCategory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        
    def add_card(self, title, desc, widget):
        card = SettingCard(title, desc, widget)
        self.layout.addWidget(card)
        return widget
        
    def add_stretch(self):
        self.layout.addStretch()


class SettingsView(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.settings = load_settings()
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        self.sidebar.setSpacing(4)
        
        # Main content area
        self.stack = QStackedWidget()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        
        self._build_ui()
        
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        if self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)
        self.reload_theme()

    def reload_theme(self):
        p = get_active_palette()
        from theme import get_brand_accent
        accent = get_brand_accent()
        self.setStyleSheet(f"background-color: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']};")
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background: {p['BRAND_BACKGROUND']};
                border-right: 1px solid {p['BRAND_BORDER']};
                border-top: none; border-bottom: none; border-left: none;
                color: {p['BRAND_PRIMARY']};
                font-size: 13px;
            }}
            QListWidget::item {{ padding: 8px 12px; border-radius: 4px; margin: 2px 4px; }}
            QListWidget::item:selected {{ background: {accent}; color: {p['BRAND_PRIMARY_FG']}; font-weight: bold; }}
            QListWidget::item:hover:!selected {{ background: {p['BRAND_PANEL_2']}; }}
        """)
        self.stack.setStyleSheet(f"background: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']};")
        # Reload theme on all SettingCards inside stacked pages
        for i in range(self.stack.count()):
            scroll = self.stack.widget(i)
            if hasattr(scroll, 'widget') and scroll.widget():
                cat = scroll.widget()
                for child in cat.findChildren(SettingCard):
                    child.reload_theme()

    def _build_ui(self):
        self._add_category("Startup & Defaults", self._build_general_tab())
        self._add_category("Text Editing", self._build_editor_tab())
        self._add_category("PDF Reading", self._build_pdf_tab())
        self._add_category("Vault & Files", self._build_vault_tab())
        self._add_category("Web Browser", self._build_web_tab())
        self._add_category("Read Aloud (TTS)", self._build_tts_tab())

    def _add_category(self, name, widget):
        self.sidebar.addItem(name)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(widget)
        self.stack.addWidget(scroll)

    def _save_setting(self, key, value):
        self.settings[key] = value
        save_settings(self.settings)
        
        # Immediate application hooks
        if key in ("theme_mode", "theme_accent"):
            if hasattr(self.main_window, "apply_theme"):
                self.main_window.apply_theme()
            elif hasattr(self.main_window, "reload_theme"):
                self.main_window.reload_theme()
        elif key == "vault_show_all_files":
            if hasattr(self.main_window, "vault_panel") and hasattr(self.main_window.vault_panel, "set_show_all_files"):
                self.main_window.vault_panel.set_show_all_files(value)
            if hasattr(self.main_window, "vault_panel") and hasattr(self.main_window.vault_panel, 'restore_from_settings'):
                self.main_window.vault_panel.restore_from_settings()
        elif key in ("autosave_enabled", "autosave_interval_seconds"):
            if hasattr(self.main_window, 'autosaver'):
                self.main_window.autosaver.apply_settings()

    # --- UI Builders ---

    def _build_general_tab(self):
        cat = SettingsCategory()
        
        combo_launch = QComboBox()
        combo_launch.addItems(["remembered", "maximized", "default"])
        combo_launch.setCurrentText(self.settings.get("launch_behavior", "remembered"))
        combo_launch.currentTextChanged.connect(lambda v: self._save_setting("launch_behavior", v))
        cat.add_card("Launch Window Size", "How should the window size behave when you open the app?", combo_launch)
        
        combo_theme = QComboBox()
        combo_theme.addItems(["dark", "light", "system"])
        combo_theme.setCurrentText(self.settings.get("theme_mode", "dark"))
        combo_theme.currentTextChanged.connect(lambda v: self._save_setting("theme_mode", v))
        cat.add_card("Theme Mode", "Switch between Dark and Light mode, or follow your OS setting.", combo_theme)
        
        combo_accent = QComboBox()
        combo_accent.addItems(["blue", "grey"])
        combo_accent.setCurrentText(self.settings.get("theme_accent", "blue"))
        combo_accent.currentTextChanged.connect(lambda v: self._save_setting("theme_accent", v))
        cat.add_card("Accent Color", "The primary color used for highlights and active UI elements.", combo_accent)
        
        combo_fresh = QComboBox()
        combo_fresh.addItems(["welcome", "blank_tab", "empty"])
        combo_fresh.setCurrentText(self.settings.get("fresh_session_behavior", "welcome"))
        combo_fresh.currentTextChanged.connect(lambda v: self._save_setting("fresh_session_behavior", v))
        cat.add_card("Fresh Session Behavior", "What opens when you start a completely new session?", combo_fresh)
        
        check_restore = QCheckBox()
        check_restore.setChecked(self.settings.get("restore_session_tabs", True))
        check_restore.toggled.connect(lambda v: self._save_setting("restore_session_tabs", v))
        cat.add_card("Restore Session Tabs", "Automatically reopen the files you were working on last time.", check_restore)

        check_hw = QCheckBox()
        check_hw.setChecked(self.settings.get("hardware_acceleration_enabled", True))
        check_hw.toggled.connect(lambda v: self._save_setting("hardware_acceleration_enabled", v))
        cat.add_card("Hardware Acceleration (GPU)", "Disable this if you experience screen tearing or crashes in Web or PDF views. Requires restart.", check_hw)

        check_autosave = QCheckBox()
        check_autosave.setChecked(self.settings.get("autosave_enabled", True))
        check_autosave.toggled.connect(lambda v: self._save_setting("autosave_enabled", v))
        cat.add_card("Background Auto-save", "Automatically save changes to your files.", check_autosave)
        
        spin_interval = QSpinBox()
        spin_interval.setRange(2, 300)
        spin_interval.setSuffix(" sec")
        spin_interval.setValue(self.settings.get("autosave_interval_seconds", 5))
        spin_interval.valueChanged.connect(lambda v: self._save_setting("autosave_interval_seconds", v))
        cat.add_card("Auto-save Interval", "How often should files be saved in the background?", spin_interval)

        cat.add_stretch()
        return cat

    def _build_editor_tab(self):
        cat = SettingsCategory()
        
        combo_md = QComboBox()
        combo_md.addItems(["view", "simple", "syntax"])
        combo_md.setCurrentText(self.settings.get("markdown_default_mode", "view"))
        combo_md.currentTextChanged.connect(lambda v: self._save_setting("markdown_default_mode", v))
        cat.add_card("Default Markdown Mode", "Which editor view to use when opening a new Markdown file.", combo_md)
        
        spin_icon = QSpinBox()
        spin_icon.setRange(MARKDOWN_ICON_SIZE_MIN, MARKDOWN_ICON_SIZE_MAX)
        spin_icon.setValue(resolve_markdown_icon_size(self.settings.get("markdown_icon_size")))
        spin_icon.valueChanged.connect(lambda v: self._save_setting("markdown_icon_size", v))
        cat.add_card("Markdown Icon Size", "Adjust the size of the editor toolbar icons (in pixels).", spin_icon)
        
        cat.add_stretch()
        return cat

    def _build_pdf_tab(self):
        cat = SettingsCategory()
        
        combo_fit = QComboBox()
        combo_fit.addItems(["page", "width"])
        combo_fit.setCurrentText(self.settings.get("pdf_fit_mode", "width"))
        combo_fit.currentTextChanged.connect(lambda v: self._save_setting("pdf_fit_mode", v))
        cat.add_card("Default PDF Zoom", "Should PDFs fit the page entirely or fit the window width?", combo_fit)
        
        combo_quality = QComboBox()
        combo_quality.addItems(["normal", "high"])
        combo_quality.setCurrentText(self.settings.get("pdf_render_quality", "high"))
        combo_quality.currentTextChanged.connect(lambda v: self._save_setting("pdf_render_quality", v))
        cat.add_card("Render Quality", "High quality uses slightly more memory for crisper text.", combo_quality)
        
        cat.add_stretch()
        return cat

    def _build_vault_tab(self):
        cat = SettingsCategory()
        
        check_all = QCheckBox()
        check_all.setChecked(self.settings.get("vault_show_all_files", False))
        check_all.toggled.connect(lambda v: self._save_setting("vault_show_all_files", v))
        cat.add_card("Show All Files", "Display non-document files (images, assets) in the Vault sidebar.", check_all)
        
        check_index = QCheckBox()
        check_index.setChecked(self.settings.get("vault_auto_index", True))
        check_index.toggled.connect(lambda v: self._save_setting("vault_auto_index", v))
        cat.add_card("Background Fast Indexing", "Automatically parse text for blazing fast full-vault search (FTS5). Disable to save battery.", check_index)
        
        cat.add_stretch()
        return cat

    def _build_web_tab(self):
        cat = SettingsCategory()
        
        inp_url = QLineEdit()
        inp_url.setText(self.settings.get("web_url", DEFAULT_SETTINGS["web_url"]))
        inp_url.editingFinished.connect(lambda: self._save_setting("web_url", inp_url.text().strip()))
        cat.add_card("Default New Tab URL", "The webpage that opens when you create a new browser tab.", inp_url)
        
        check_js = QCheckBox()
        check_js.setChecked(self.settings.get("web_enable_javascript", True))
        check_js.toggled.connect(lambda v: self._save_setting("web_enable_javascript", v))
        cat.add_card("Enable JavaScript", "Allow websites to run JS. Disable for a distraction-free reading experience.", check_js)
        
        check_ad = QCheckBox()
        check_ad.setChecked(self.settings.get("web_enable_adblock", True))
        check_ad.toggled.connect(lambda v: self._save_setting("web_enable_adblock", v))
        cat.add_card("Enable Adblock", "Block annoying ads and trackers at the network level.", check_ad)
        
        cat.add_stretch()
        return cat

    def _build_tts_tab(self):
        cat = SettingsCategory()
        
        combo_mode = QComboBox()
        combo_mode.addItems(["page", "continuous"])
        combo_mode.setCurrentText(self.settings.get("tts_read_mode", "page"))
        combo_mode.currentTextChanged.connect(lambda v: self._save_setting("tts_read_mode", v))
        cat.add_card("Read Mode", "Stop at the end of the page or continue reading automatically?", combo_mode)
        
        spin_rate = QSpinBox()
        spin_rate.setRange(50, 400)
        spin_rate.setSingleStep(10)
        spin_rate.setSuffix(" wpm")
        spin_rate.setValue(self.settings.get("tts_rate", 200))
        spin_rate.valueChanged.connect(lambda v: self._save_setting("tts_rate", v))
        cat.add_card("Speech Rate", "How fast the Universal TTS engine should read your documents.", spin_rate)
        
        cat.add_stretch()
        return cat
