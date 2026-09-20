from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

from resources.icons import Icons
from styles import TEXT_PRIMARY, TEXT_SECONDARY

LOG_FILE = Path("TriggerPulse.log")

class LogPanel(QWidget):
    """
    A compact panel that displays the last two lines from TriggerPulse.log
    with icons and text.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        title = QLabel("Recent Events")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
        self.layout.addWidget(title)

        # List widget for last 2 log entries
        self.log_list = QListWidget()
        self.log_list.setFixedHeight(60)  # enough for two entries without huge space
        self.log_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.log_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.log_list.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent; border: none;")
        self.layout.addWidget(self.log_list)

        # Initial populate
        self.refresh()

    def _get_last_two_lines(self):
        """
        Read the log file and return the last two meaningful lines.
        """
        if not LOG_FILE.exists():
            return []

        lines = LOG_FILE.read_text().splitlines()
        # Only non-empty lines
        lines = [l for l in lines if l.strip()]
        return lines[-2:] if len(lines) >= 2 else lines

    def refresh(self):
        """
        Refresh the display to show the last two log events.
        """
        self.log_list.clear()
        last_lines = self._get_last_two_lines()

        for entry in last_lines:
            item = QListWidgetItem(self._format_entry(entry))
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            self.log_list.addItem(item)

    def _format_entry(self, raw_line: str) -> str:
        """
        Convert a raw log line into an icon + label string.

        Example:
            "2026-02-02 13:45:12 — MATCH — Continue [1].png — SUCCESS"
            becomes:
            "✔ SUCCESS — Continue [1].png"
        """
        # Attempt to parse common log formats
        text = raw_line.strip()

        # ICON + label mapping
        if "SUCCESS" in text:
            icon = Icons.SUCCESS
        elif "FAILURE" in text:
            icon = Icons.WARNING
        elif "STOPPED" in text:
            # Treat stop as a warning style (not error)
            icon = Icons.WARNING
        else:
            icon = Icons.WARNING

        # Remove timestamp if present
        if "—" in text:
            parts = text.split("—")
            # last part should hold the event text
            summary = parts[-1].strip()
        else:
            summary = text

        return f"{icon} {summary}"
