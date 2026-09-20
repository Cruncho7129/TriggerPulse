from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QComboBox, QPushButton
import serial.tools.list_ports
import mss

from styles import ACCENT_COLOR, TEXT_PRIMARY

class ControlsPanel(QWidget):
    """
    Panel with serial port and monitor selection
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Serial Port
        self.layout.addWidget(QLabel("Serial Port:"))

        self.serial_combo = QComboBox()
        self._populate_serial_ports()
        self.layout.addWidget(self.serial_combo)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh Ports")
        self.refresh_btn.clicked.connect(self._populate_serial_ports)
        self.layout.addWidget(self.refresh_btn)

        # Monitor Selector
        self.layout.addWidget(QLabel("Monitor:"))

        self.monitor_combo = QComboBox()
        self._populate_monitors()
        self.layout.addWidget(self.monitor_combo)

        # Apply styles
        self._apply_styles()

    def _apply_styles(self):
        """
        Apply consistent styles for controls.
        """
        self.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-weight: bold;
            }}
            QComboBox {{
                background: #2A2A2A;
                color: {TEXT_PRIMARY};
            }}
            QPushButton {{
                background: {ACCENT_COLOR};
                color: #000;
                padding: 4px 10px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: #7E86FF;
            }}
        """)

    def _populate_serial_ports(self):
        """
        Populate only active serial COM ports
        """
        self.serial_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.serial_combo.addItem(p.device)

    def _populate_monitors(self):
        """
        Populate monitor dropdown with *only active* monitors
        """
        self.monitor_combo.clear()

        with mss.mss() as sct:
            count = len(sct.monitors) - 1  # sct.monitors[0] is the virtual full
            for idx in range(1, count + 1):
                self.monitor_combo.addItem(str(idx))

    def current_serial(self) -> str:
        """
        Return currently selected serial port.
        """
        return self.serial_combo.currentText()

    def current_monitor(self) -> int:
        """
        Return currently selected monitor index.
        """
        try:
            return int(self.monitor_combo.currentText())
        except ValueError:
            return 1
