from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class KeyCaptureDialog(QDialog):
    def __init__(self, title="Press a Key"):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(300, 100)

        self.label = QLabel("Press the key you want now...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.captured = None

    def keyPressEvent(self, event):
        key = event.key()

        # Special key mapping
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.captured = "enter"
        elif key == Qt.Key.Key_Space:
            self.captured = "space"
        elif key == Qt.Key.Key_Escape:
            self.captured = "escape"
        else:
            # Get the text the key represents (lowercase)
            text = event.text()
            if text:
                self.captured = text.lower()
            else:
                # Fallback for other keys
                self.captured = event.key().name.lower()

        self.accept()
