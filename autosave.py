from PySide6.QtCore import QTimer


class AutoSaver:

    def __init__(self, main_window):

        self.main_window = main_window

        self.timer = QTimer()

        # Autosave every 5 seconds
        self.timer.setInterval(5000)

        self.timer.timeout.connect(self.autosave)

        self.timer.start()

    def autosave(self):

        tabs = self.main_window.tabs

        for i in range(tabs.count()):

            editor = tabs.widget(i)

            if (
                editor
                and editor.is_modified
                and editor.file_path
            ):

                try:
                    with open(
                        editor.file_path,
                        "w",
                        encoding="utf-8"
                    ) as file:

                        file.write(editor.toPlainText())

                    editor.is_modified = False

                    name = editor.file_path.split("/")[-1]

                    tabs.setTabText(i, name)

                except Exception as e:
                    print("Autosave failed:", e)
