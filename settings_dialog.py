from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QSpinBox, QPushButton, QFormLayout, QTabWidget,
    QComboBox, QWidget, QListWidget, QFileDialog
)
from PySide6.QtCore import Qt

from settings import load_settings, save_settings, DEFAULT_SETTINGS, DEFAULT_WEB_TABS
from theme import (
    MARKDOWN_ICON_SIZE_MIN, MARKDOWN_ICON_SIZE_MAX,
    resolve_markdown_icon_size,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(580, 500)
        self.settings = load_settings()
        # FIX: WA_DeleteOnClose=True ensures dialog is freed on close
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), "Startup & Defaults")
        tabs.addTab(self._build_editor_tab(), "Text Editing")
        tabs.addTab(self._build_pdf_tab(), "PDF Reading")
        tabs.addTab(self._build_web_tab(), "Web Browser Panel")
        tabs.addTab(self._build_audio_tab(), "Audio & Read Aloud")
        tabs.addTab(self._build_vault_tab(), "Folders & Organization")
        layout.addWidget(tabs)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

    def _build_general_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        self.launch_combo = QComboBox()
        self.launch_combo.addItem("Use my last window size", "remembered")
        self.launch_combo.addItem("Always open maximized", "maximized")
        self.launch_combo.addItem("Use the default window size", "default")
        launch_value = self.settings.get("launch_behavior", "remembered")
        self.launch_combo.setCurrentIndex(max(0, self.launch_combo.findData(launch_value)))
        form.addRow("When EleViewer opens:", self.launch_combo)

        self.theme_mode_combo = QComboBox()
        self.theme_mode_combo.addItem("Dark", "dark")
        self.theme_mode_combo.addItem("Light", "light")
        self.theme_mode_combo.addItem("Match Windows", "system")
        theme_mode = self.settings.get("theme_mode", "dark")
        self.theme_mode_combo.setCurrentIndex(max(0, self.theme_mode_combo.findData(theme_mode)))
        form.addRow("Appearance:", self.theme_mode_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["grey", "blue"])
        current_accent = self.settings.get("theme_accent", "grey")
        self.theme_combo.setCurrentText(current_accent if current_accent in ["grey", "blue"] else "grey")
        form.addRow("Theme accent color:", self.theme_combo)

        self.toolbar_style_combo = QComboBox()
        self.toolbar_style_combo.addItem("Icons with text labels (Default)", "text_under_icon")
        self.toolbar_style_combo.addItem("Icons only (Compact)", "icon_only")
        self.toolbar_style_combo.addItem("Icons beside text labels", "text_beside_icon")
        current_tb_style = self.settings.get("toolbar_button_style", "text_under_icon")
        self.toolbar_style_combo.setCurrentIndex(max(0, self.toolbar_style_combo.findData(current_tb_style)))
        form.addRow("Toolbar layout style:", self.toolbar_style_combo)

        self.show_toolbar_check = QCheckBox("Show main toolbar")
        self.show_toolbar_check.setChecked(self.settings.get("show_toolbar", True))
        form.addRow(self.show_toolbar_check)

        self.fresh_session_combo = QComboBox()
        self.fresh_session_combo.addItem("Show the welcome screen", "welcome")
        self.fresh_session_combo.addItem("Open a blank note", "blank_tab")
        self.fresh_session_combo.addItem("Open an empty workspace", "empty")
        fresh_session = self.settings.get("fresh_session_behavior", "welcome")
        self.fresh_session_combo.setCurrentIndex(max(0, self.fresh_session_combo.findData(fresh_session)))
        form.addRow("When no session is saved:", self.fresh_session_combo)

        self.restore_session_check = QCheckBox("Restore open documents and tabs on launch")
        self.restore_session_check.setChecked(self.settings.get("restore_session", True))
        form.addRow(self.restore_session_check)

        self.autosave_check = QCheckBox("Enable background auto-save to file")
        self.autosave_check.setChecked(self.settings.get("autosave_enabled", True))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(2, 300)
        self.interval_spin.setSuffix(" sec")
        self.interval_spin.setValue(self.settings.get("autosave_interval_seconds", 5))
        form.addRow(self.autosave_check)
        form.addRow("Auto-save interval:", self.interval_spin)

        self.draft_autosave_check = QCheckBox("Enable draft recovery buffer (power-loss safety net)")
        self.draft_autosave_check.setChecked(self.settings.get("draft_autosave_enabled", True))
        form.addRow(self.draft_autosave_check)

        self.minimize_to_tray_check = QCheckBox("Minimize to system tray on window close")
        self.minimize_to_tray_check.setChecked(self.settings.get("minimize_to_tray", False))
        form.addRow(self.minimize_to_tray_check)

        return w

    def _build_editor_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        self.md_mode_combo = QComboBox()
        self.md_mode_combo.addItems(["view", "simple", "syntax"])
        current = self.settings.get("markdown_default_mode", "view")
        self.md_mode_combo.setCurrentText(current)
        form.addRow("Default markdown mode:", self.md_mode_combo)

        self.md_icon_spin = QSpinBox()
        self.md_icon_spin.setRange(MARKDOWN_ICON_SIZE_MIN, MARKDOWN_ICON_SIZE_MAX)
        self.md_icon_spin.setValue(resolve_markdown_icon_size(self.settings.get("markdown_icon_size")))
        form.addRow("Mode icon size (px):", self.md_icon_spin)

        self.editor_font_spin = QSpinBox()
        self.editor_font_spin.setRange(10, 28)
        self.editor_font_spin.setSuffix(" px")
        self.editor_font_spin.setValue(int(self.settings.get("editor_font_size", 14)))
        form.addRow("Editor font size:", self.editor_font_spin)

        self.editor_font_combo = QComboBox()
        self.editor_font_combo.addItems(["Segoe UI", "Consolas", "Cascadia Code", "Courier New", "Arial"])
        current_font = self.settings.get("editor_font_family", "Segoe UI")
        if current_font in ["Segoe UI", "Consolas", "Cascadia Code", "Courier New", "Arial"]:
            self.editor_font_combo.setCurrentText(current_font)
        form.addRow("Editor font family:", self.editor_font_combo)

        self.editor_word_wrap_check = QCheckBox("Enable soft line wrapping in editor")
        self.editor_word_wrap_check.setChecked(self.settings.get("editor_word_wrap", True))
        form.addRow(self.editor_word_wrap_check)

        self.editor_line_numbers_check = QCheckBox("Show line numbers in code/plain text mode")
        self.editor_line_numbers_check.setChecked(self.settings.get("editor_line_numbers", True))
        form.addRow(self.editor_line_numbers_check)

        return w

    def _build_pdf_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        self.pdf_fit_combo = QComboBox()
        self.pdf_fit_combo.addItems(["width", "page"])
        self.pdf_fit_combo.setCurrentText(self.settings.get("pdf_fit_mode", "width"))
        form.addRow("Default fit mode:", self.pdf_fit_combo)

        self.pdf_quality_combo = QComboBox()
        self.pdf_quality_combo.addItems(["high", "normal"])
        self.pdf_quality_combo.setCurrentText(self.settings.get("pdf_render_quality", "high"))
        form.addRow("Render quality:", self.pdf_quality_combo)

        self.pdf_default_zoom_combo = QComboBox()
        self.pdf_default_zoom_combo.addItems(["Fit to Width", "Fit to Page", "100%", "125%", "150%"])
        self.pdf_default_zoom_combo.setCurrentText(self.settings.get("pdf_default_zoom", "Fit to Width"))
        form.addRow("Default zoom level:", self.pdf_default_zoom_combo)

        self.pdf_continuous_check = QCheckBox("Enable smooth continuous page scrolling")
        self.pdf_continuous_check.setChecked(self.settings.get("pdf_continuous_scroll", True))
        form.addRow(self.pdf_continuous_check)

        return w

    def _build_web_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        self.web_url_input = QLineEdit()
        self.web_url_input.setPlaceholderText("https://example.com")
        self.web_url_input.setText(self.settings.get("web_url", DEFAULT_SETTINGS["web_url"]))
        form.addRow("Default URL for new tabs:", self.web_url_input)

        self.web_default_zoom_combo = QComboBox()
        self.web_default_zoom_combo.addItem("50%", 50)
        self.web_default_zoom_combo.addItem("75%", 75)
        self.web_default_zoom_combo.addItem("100% (Default)", 100)
        self.web_default_zoom_combo.addItem("125%", 125)
        self.web_default_zoom_combo.addItem("150%", 150)
        self.web_default_zoom_combo.addItem("175%", 175)
        self.web_default_zoom_combo.addItem("200%", 200)
        current_zoom = int(self.settings.get("web_default_zoom", 100))
        idx = self.web_default_zoom_combo.findData(current_zoom)
        self.web_default_zoom_combo.setCurrentIndex(max(0, idx))
        form.addRow("Default page zoom:", self.web_default_zoom_combo)

        dl_layout = QHBoxLayout()
        self.download_folder_input = QLineEdit()
        self.download_folder_input.setText(self.settings.get("default_download_folder", ""))
        self.download_folder_input.setPlaceholderText("(System Downloads folder)")
        dl_browse_btn = QPushButton("Browse...")

        def _browse_dl():
            folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
            if folder:
                self.download_folder_input.setText(folder)

        dl_browse_btn.clicked.connect(_browse_dl)
        dl_layout.addWidget(self.download_folder_input)
        dl_layout.addWidget(dl_browse_btn)
        form.addRow("Downloads destination:", dl_layout)

        self.web_intercept_check = QCheckBox("Open links clicked in documents in split-screen Web Panel")
        self.web_intercept_check.setChecked(self.settings.get("web_intercept_links", True))
        form.addRow(self.web_intercept_check)

        self.web_restore_tabs_check = QCheckBox("Restore open web tabs across application restarts")
        self.web_restore_tabs_check.setChecked(self.settings.get("web_restore_tabs", True))
        form.addRow(self.web_restore_tabs_check)

        tab_count = len(self.settings.get("web_tabs", DEFAULT_WEB_TABS))
        form.addRow("Currently saved web tabs:", QLabel(str(tab_count)))
        return w

    def _build_audio_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        self.tts_engine_combo = QComboBox()
        self.tts_engine_combo.addItem("Microsoft Neural (Online / High Quality)", "neural")
        self.tts_engine_combo.addItem("Local Windows SAPI (Offline)", "local")
        current_engine = self.settings.get("tts_engine", "neural")
        self.tts_engine_combo.setCurrentIndex(max(0, self.tts_engine_combo.findData(current_engine)))
        form.addRow("Speech engine:", self.tts_engine_combo)

        self.tts_speed_combo = QComboBox()
        self.tts_speed_combo.addItem("0.75x (Slower)", "0.75x")
        self.tts_speed_combo.addItem("1.0x (Normal)", "1.0x")
        self.tts_speed_combo.addItem("1.25x (Fast)", "1.25x")
        self.tts_speed_combo.addItem("1.5x (Faster)", "1.5x")
        self.tts_speed_combo.addItem("2.0x (Double Speed)", "2.0x")
        current_speed = self.settings.get("tts_speed", "1.0x")
        self.tts_speed_combo.setCurrentIndex(max(0, self.tts_speed_combo.findData(current_speed)))
        form.addRow("Reading speed:", self.tts_speed_combo)

        self.tts_mode_combo = QComboBox()
        self.tts_mode_combo.addItem("Selected text (or current page)", "page")
        self.tts_mode_combo.addItem("Continuous document reading", "continuous")
        current_mode = self.settings.get("tts_read_mode", "page")
        self.tts_mode_combo.setCurrentIndex(max(0, self.tts_mode_combo.findData(current_mode)))
        form.addRow("Default reading scope:", self.tts_mode_combo)

        self.tts_clean_citations_check = QCheckBox("Clean footnotes, brackets [1], and URL citations before speaking")
        self.tts_clean_citations_check.setChecked(self.settings.get("tts_clean_citations", True))
        form.addRow(self.tts_clean_citations_check)

        return w

    def _build_vault_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        self.vault_show_all = QCheckBox("Show all files in vault (not just supported documents)")
        self.vault_show_all.setChecked(self.settings.get("vault_show_all_files", False))
        form.addRow(self.vault_show_all)

        self.vault_exclude_hidden_check = QCheckBox("Filter out system and hidden files (desktop.ini, .git)")
        self.vault_exclude_hidden_check.setChecked(self.settings.get("vault_exclude_hidden", True))
        form.addRow(self.vault_exclude_hidden_check)

        self.vault_search_scope_combo = QComboBox()
        self.vault_search_scope_combo.addItem("Active course folder only", "active_vault")
        self.vault_search_scope_combo.addItem("All connected course folders", "all_vaults")
        current_scope = self.settings.get("file_search_scope", "active_vault")
        self.vault_search_scope_combo.setCurrentIndex(max(0, self.vault_search_scope_combo.findData(current_scope)))
        form.addRow("File search scope:", self.vault_search_scope_combo)

        folder_layout = QHBoxLayout()
        self.save_folder_input = QLineEdit()
        self.save_folder_input.setText(self.settings.get("default_save_folder", ""))
        self.save_folder_input.setPlaceholderText("(Use the current folder)")
        browse_btn = QPushButton("Browse...")

        def _browse():
            folder = QFileDialog.getExistingDirectory(self, "Select Default Save Folder")
            if folder:
                self.save_folder_input.setText(folder)

        browse_btn.clicked.connect(_browse)
        folder_layout.addWidget(self.save_folder_input)
        folder_layout.addWidget(browse_btn)
        form.addRow("Default folder for new notes:", folder_layout)

        self.vault_list = QListWidget()
        paths = self.settings.get("vault_paths", [])
        self.vault_list.addItems(paths)

        vault_controls = QVBoxLayout()
        btn_add = QPushButton("Add...")
        btn_edit = QPushButton("Edit...")
        btn_remove = QPushButton("Remove")

        def _add_vault():
            folder = QFileDialog.getExistingDirectory(self, "Select Vault Folder")
            if folder:
                self.vault_list.addItem(folder)

        def _edit_vault():
            current = self.vault_list.currentItem()
            if current:
                folder = QFileDialog.getExistingDirectory(self, "Select Vault Folder", current.text())
                if folder:
                    current.setText(folder)

        def _remove_vault():
            row = self.vault_list.currentRow()
            if row >= 0:
                self.vault_list.takeItem(row)

        btn_add.clicked.connect(_add_vault)
        btn_edit.clicked.connect(_edit_vault)
        btn_remove.clicked.connect(_remove_vault)

        vault_controls.addWidget(btn_add)
        vault_controls.addWidget(btn_edit)
        vault_controls.addWidget(btn_remove)
        vault_controls.addStretch()

        vault_layout = QHBoxLayout()
        vault_layout.addWidget(self.vault_list)
        vault_layout.addLayout(vault_controls)

        form.addRow("Course folders:", vault_layout)
        return w

    def _save(self):
        self.settings = load_settings()
        vaults = []
        for i in range(self.vault_list.count()):
            vaults.append(self.vault_list.item(i).text())

        self.settings.update({
            "launch_behavior": self.launch_combo.currentData(),
            "theme_mode": self.theme_mode_combo.currentData(),
            "theme_accent": self.theme_combo.currentText(),
            "toolbar_button_style": self.toolbar_style_combo.currentData(),
            "show_toolbar": self.show_toolbar_check.isChecked(),
            "fresh_session_behavior": self.fresh_session_combo.currentData(),
            "restore_session": self.restore_session_check.isChecked(),
            "autosave_enabled": self.autosave_check.isChecked(),
            "autosave_interval_seconds": self.interval_spin.value(),
            "draft_autosave_enabled": self.draft_autosave_check.isChecked(),
            "minimize_to_tray": self.minimize_to_tray_check.isChecked(),
            "markdown_default_mode": self.md_mode_combo.currentText(),
            "markdown_icon_size": self.md_icon_spin.value(),
            "editor_font_size": self.editor_font_spin.value(),
            "editor_font_family": self.editor_font_combo.currentText(),
            "editor_word_wrap": self.editor_word_wrap_check.isChecked(),
            "editor_line_numbers": self.editor_line_numbers_check.isChecked(),
            "pdf_fit_mode": self.pdf_fit_combo.currentText(),
            "pdf_render_quality": self.pdf_quality_combo.currentText(),
            "pdf_default_zoom": self.pdf_default_zoom_combo.currentText(),
            "pdf_continuous_scroll": self.pdf_continuous_check.isChecked(),
            "web_url": self.web_url_input.text().strip() or DEFAULT_SETTINGS["web_url"],
            "web_default_zoom": self.web_default_zoom_combo.currentData(),
            "default_download_folder": self.download_folder_input.text().strip(),
            "web_intercept_links": self.web_intercept_check.isChecked(),
            "web_restore_tabs": self.web_restore_tabs_check.isChecked(),
            "tts_engine": self.tts_engine_combo.currentData(),
            "tts_speed": self.tts_speed_combo.currentData(),
            "tts_read_mode": self.tts_mode_combo.currentData(),
            "tts_clean_citations": self.tts_clean_citations_check.isChecked(),
            "vault_show_all_files": self.vault_show_all.isChecked(),
            "vault_exclude_hidden": self.vault_exclude_hidden_check.isChecked(),
            "file_search_scope": self.vault_search_scope_combo.currentData(),
            "default_save_folder": self.save_folder_input.text().strip(),
            "vault_paths": vaults,
        })
        save_settings(self.settings)
        self.accept()

    def get_settings(self):
        return self.settings
