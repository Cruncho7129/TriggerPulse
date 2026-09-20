from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QLabel,
    QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt

from styles import MAIN_WINDOW_QSS
from controls import ControlsPanel
from rule_card import RuleCard
from config_handlers import load_config, save_config
from detection_launcher import DetectionWorker


SCREENSHOT_FOLDER = Path("screenshots")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TriggerPulse")
        self.setStyleSheet(MAIN_WINDOW_QSS)

        # Detection worker (thread-based)
        self.worker: DetectionWorker | None = None

        # Layout
        self.main_layout = QVBoxLayout(self)

        # Controls (serial + monitor)
        self.controls = ControlsPanel(self)
        self.main_layout.addWidget(self.controls)

        # Rules area
        self.rules_area = QScrollArea()
        self.rules_area.setWidgetResizable(True)
        self.rules_container = QWidget()
        self.rules_layout = QVBoxLayout(self.rules_container)
        self.rules_area.setWidget(self.rules_container)
        self.rules_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.main_layout.addWidget(self.rules_area, stretch=3)

        # Status indicator
        self.status_label = QLabel("Status: 🟥 Stopped")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.status_label)

        # Recent events
        self.recent_events = QListWidget()
        self.recent_events.setFixedHeight(180)
        self.main_layout.addWidget(self.recent_events)

        # Buttons
        self._add_buttons()

        # Load config and rules
        self._load_config()

    # --------------------------------------------------
    # UI setup
    # --------------------------------------------------

    def _add_buttons(self):
        self.btn_save = QPushButton("Save Config")
        self.btn_save.clicked.connect(self._on_save)
        self.main_layout.addWidget(self.btn_save)

        self.btn_run = QPushButton("Run Detection")
        self.btn_run.clicked.connect(self._on_run)
        self.main_layout.addWidget(self.btn_run)

        self.btn_stop = QPushButton("End Session")
        self.btn_stop.clicked.connect(self._on_stop)
        self.main_layout.addWidget(self.btn_stop)

    # --------------------------------------------------
    # Button handlers
    # --------------------------------------------------

    def _on_save(self):
        save_config(self._collect_config())
        QMessageBox.information(self, "TriggerPulse", "Configuration saved.")

    def _on_run(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "TriggerPulse", "Detection is already running.")
            return

        # Save current config before starting
        save_config(self._collect_config())

        # Clear UI state
        self.recent_events.clear()
        self.status_label.setText("Status: 🟢 Running")

        # Create worker
        self.worker = DetectionWorker()

        # Connect signals
        self.worker.log_event.connect(self._on_log_event)
        self.worker.status_update.connect(self._on_status_update)
        self.worker.stopped.connect(self._on_worker_stopped)

        # Start detection thread
        self.worker.start()

    def _on_stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

    # --------------------------------------------------
    # Worker signal handlers
    # --------------------------------------------------

    def _on_log_event(self, message: str):
        self.recent_events.addItem(QListWidgetItem(message))
        self.recent_events.scrollToBottom()

    def _on_status_update(self, status: str):
        if status == "running":
            self.status_label.setText("Status: 🟢 Running")
        elif status == "stopped":
            self.status_label.setText("Status: 🟥 Stopped")

    def _on_worker_stopped(self):
        self.status_label.setText("Status: 🟥 Stopped")

    # --------------------------------------------------
    # Config handling
    # --------------------------------------------------

    def _load_config(self):
        cfg = load_config()

        self.controls.serial_combo.setCurrentText(cfg.get("serial_port", ""))
        self.controls.monitor_combo.setCurrentText(str(cfg.get("monitor_index", 1)))

        # Load rules from config
        for rule in cfg.get("rules", []):
            card = RuleCard(rule)
            if not (SCREENSHOT_FOLDER / rule["filename"]).exists():
                card.setStyleSheet("opacity:0.4;")
            self.rules_layout.addWidget(card)

        # Add any screenshots not yet in config
        seen = {r["filename"] for r in cfg.get("rules", [])}
        for f in SCREENSHOT_FOLDER.glob("*.png"):
            if f.name not in seen:
                self.rules_layout.addWidget(RuleCard({"filename": f.name}))

    def _collect_config(self):
        cfg = {
            "serial_port": self.controls.current_serial(),
            "monitor_index": self.controls.current_monitor(),
            "rules": []
        }

        for i in range(self.rules_layout.count()):
            w = self.rules_layout.itemAt(i).widget()
            if isinstance(w, RuleCard):
                cfg["rules"].append(w.data)

        return cfg
