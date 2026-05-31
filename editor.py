from PySide6.QtWidgets import QTextEdit


class EditorTab(QTextEdit):

    def __init__(self):
        super().__init__()

        self.file_path = None

        self.is_modified = False

        self.textChanged.connect(self.mark_modified)

        self.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #ffffff;
                font-size: 15px;
                padding: 10px;
                border: none;
            }
        """)

    def mark_modified(self):

        self.is_modified = True

        parent_tabs = self.parentWidget()

        if parent_tabs:

            index = parent_tabs.indexOf(self)

            if index != -1:

                current_name = parent_tabs.tabText(index)

                if not current_name.endswith("*"):
                    parent_tabs.setTabText(
                        index,
                        current_name + "*"
                    )
