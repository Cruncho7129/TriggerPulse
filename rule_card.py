from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QSlider, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QInputDialog
)

from styles import CARD_BACKGROUND, TEXT_PRIMARY, apply_shadow
from resources.icons import Icons
from key_capture import KeyCaptureDialog

SCREENSHOT_FOLDER = Path("screenshots")


class RuleCard(QWidget):
    """
    A modern card representation of a trigger rule,
    ensuring defaults for missing config fields.
    """

    def __init__(self, rule_data):
        super().__init__()
        self.data = rule_data

        # Ensure all expected fields exist
        self._ensure_defaults()

        # Root layout
        self.root_layout = QVBoxLayout()
        self.setLayout(self.root_layout)
        self.setStyleSheet(f"background: {CARD_BACKGROUND}; border-radius: 8px;")

        # Shadow effect
        apply_shadow(self)

        # Build sections
        self._build_header()
        self._build_inputs()
        self._build_action_list()
        self._build_failure()

    def _ensure_defaults(self):
        self.data.setdefault("threshold", 0.9)
        self.data.setdefault("detect_time", 0)
        self.data.setdefault("cooldown", 0)
        self.data.setdefault("actions", [])

        if "failure" not in self.data or not isinstance(self.data["failure"], dict):
            self.data["failure"] = {"max_retries": 0, "retry_delay_ms": 0, "skip_actions": []}
        else:
            self.data["failure"].setdefault("max_retries", 0)
            self.data["failure"].setdefault("retry_delay_ms", 0)
            self.data["failure"].setdefault("skip_actions", [])

    def _build_header(self):
        header_layout = QHBoxLayout()
        title = QLabel(f"{Icons.RULE} {self.data['filename']}")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13pt; font-weight: bold;")
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        screenshot_path = SCREENSHOT_FOLDER / self.data["filename"]
        if screenshot_path.exists():
            pix = QPixmap(str(screenshot_path)).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio)
            preview = QLabel()
            preview.setPixmap(pix)
            header_layout.addWidget(preview, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            title.setStyleSheet("color: gray;")

        self.root_layout.addLayout(header_layout)

    def _build_inputs(self):
        self._labeled_slider("Threshold (%):", "threshold", 0, 100, 1)
        self._labeled_slider("Detect Time (ms):", "detect_time", 0, 2000, 25)
        self._labeled_slider("Cooldown (ms):", "cooldown", 0, 5000, 50)

    def _labeled_slider(self, label_text, key, minimum, maximum, step):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setSingleStep(step)

        # Initial value
        current_val = int(self.data.get(key, 0))
        slider.setValue(current_val)

        line = QLineEdit(str(current_val))
        line.setFixedWidth(60)

        # Sync slider → line edit → data
        def on_slider_change(val):
            self.data[key] = val
            line.setText(str(val))

        slider.valueChanged.connect(on_slider_change)

        # Sync line edit → slider → data
        def on_line_edit():
            try:
                val = int(line.text())
                val = max(min(val, maximum), minimum)
                slider.setValue(val)
                self.data[key] = val
            except ValueError:
                pass

        line.editingFinished.connect(on_line_edit)

        layout.addWidget(slider)
        layout.addWidget(line)
        self.root_layout.addLayout(layout)

    def _build_action_list(self):
        self.root_layout.addWidget(QLabel("Actions:"))

        self.action_list = QListWidget()
        self.root_layout.addWidget(self.action_list)
        self._refresh_actions()

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._button("Press", self._add_press))
        btn_layout.addWidget(self._button("Hold", self._add_hold))
        btn_layout.addWidget(self._button("Wait", self._add_wait))
        self.root_layout.addLayout(btn_layout)

    def _refresh_actions(self):
        self.action_list.clear()
        for act in self.data.get("actions", []):
            item = QListWidgetItem(self._format_action(act))
            self.action_list.addItem(item)

    def _format_action(self, act):
        if act["type"] == "press":
            return f"{Icons.PRESS} PRESS {act['key']}"
        elif act["type"] == "hold":
            return f"{Icons.HOLD} HOLD {act['key']} ({act['duration_ms']} ms)"
        elif act["type"] == "wait":
            return f"{Icons.WAIT} WAIT {act['duration_ms']} ms"
        return ""

    def _add_press(self):
        dlg = KeyCaptureDialog("Press Key")
        if dlg.exec():
            self.data["actions"].append({"type": "press", "key": dlg.captured})
            self._refresh_actions()

    def _add_hold(self):
        dlg = KeyCaptureDialog("Hold Key")
        if dlg.exec():
            key = dlg.captured
            dur, ok = QInputDialog.getInt(self, "Hold Duration", "Hold ms (0=until next):", 500, 0)
            if ok:
                self.data["actions"].append({"type": "hold", "key": key, "duration_ms": dur})
                self._refresh_actions()

    def _add_wait(self):
        dur, ok = QInputDialog.getInt(self, "Wait Duration", "Wait ms:", 200, 0)
        if ok:
            self.data["actions"].append({"type": "wait", "duration_ms": dur})
            self._refresh_actions()

    def _build_failure(self):
        self.root_layout.addWidget(QLabel("Failure / Retry Settings"))

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Max retries:"))

        maxr = QLineEdit(str(self.data["failure"]["max_retries"]))
        maxr.setFixedWidth(60)

        def on_maxr():
            try:
                v = int(maxr.text())
                self.data["failure"]["max_retries"] = v
            except:
                pass

        maxr.editingFinished.connect(on_maxr)

        layout.addWidget(maxr)

        layout.addWidget(QLabel("Retry delay (ms):"))
        rdelay = QLineEdit(str(self.data["failure"]["retry_delay_ms"]))
        rdelay.setFixedWidth(60)

        def on_rdelay():
            try:
                v = int(rdelay.text())
                self.data["failure"]["retry_delay_ms"] = v
            except:
                pass

        rdelay.editingFinished.connect(on_rdelay)
        layout.addWidget(rdelay)
        self.root_layout.addLayout(layout)

        self.root_layout.addWidget(QLabel("Skip Actions:"))
        self.skip_list = QListWidget()
        self.root_layout.addWidget(self.skip_list)
        self._refresh_skip_list()

        btn = self._button("Add Skip Action", self._add_skip_action)
        self.root_layout.addWidget(btn)

    def _refresh_skip_list(self):
        self.skip_list.clear()
        for act in self.data["failure"]["skip_actions"]:
            self.skip_list.addItem(f"{Icons.SKIP} {act['type'].upper()}")

    def _add_skip_action(self):
        dlg = KeyCaptureDialog("Skip Action Key")
        if dlg.exec():
            self.data["failure"]["skip_actions"].append({"type": "press", "key": dlg.captured})
            self._refresh_skip_list()

    def _button(self, text, fn):
        btn = QPushButton(text)
        btn.clicked.connect(fn)
        return btn
