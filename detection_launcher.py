import time
import json
import datetime
from pathlib import Path

import cv2
import numpy as np
import mss
import serial

from PyQt6.QtCore import QThread, pyqtSignal

CONFIG_FILE = Path("config.json")
SCREENSHOT_FOLDER = Path("screenshots")
LOG_FILE = Path("TriggerPulse.log")


class DetectionWorker(QThread):
    log_event = pyqtSignal(str)
    status_update = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False

    def stop(self):
        self._running = False

    def _log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        self.log_event.emit(line)

    def run(self):
        self._running = True
        self.status_update.emit("running")

        if not CONFIG_FILE.exists():
            self._log("ERROR: config.json not found")
            self._shutdown()
            return

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            self._log(f"ERROR: Failed to load config.json: {e}")
            self._shutdown()
            return

        serial_port = cfg.get("serial_port")
        rules = cfg.get("rules", [])
        monitor_index = cfg.get("monitor_index", 1)

        if not serial_port:
            self._log("ERROR: No serial port selected")
            self._shutdown()
            return

        try:
            ser = serial.Serial(serial_port, 115200, timeout=1)
        except Exception as e:
            self._log(f"ERROR: Failed to open serial port: {e}")
            self._shutdown()
            return

        templates = {}
        for rule in rules:
            path = SCREENSHOT_FOLDER / rule["filename"]
            if path.exists():
                img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    templates[rule["filename"]] = img
                else:
                    self._log(f"WARNING: Failed to load {rule['filename']}")
            else:
                self._log(f"WARNING: Missing template {rule['filename']}")

        sct = mss.mss()
        try:
            monitor = sct.monitors[monitor_index]
        except Exception:
            self._log(f"ERROR: Invalid monitor index {monitor_index}")
            self._shutdown()
            return

        self._log("Detection started")

        last_trigger = {}

        while self._running:
            frame = np.array(sct.grab(monitor))[:, :, :3]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            now = time.time()

            for rule in rules:
                name = rule["filename"]
                tmpl = templates.get(name)
                if tmpl is None:
                    continue

                res = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)

                # 🔥 FIX: normalize threshold from percent to 0–1
                threshold = rule.get("threshold", 90) / 100.0
                cooldown = rule.get("cooldown", 0)

                last = last_trigger.get(name, 0)

                if max_val >= threshold and (now - last) >= cooldown:
                    self._log(f"MATCH: {name} ({max_val:.3f})")

                    for action in rule.get("actions", []):
                        ser.write((json.dumps(action) + "\n").encode())

                    ser.write(b'{"type":"increment_cycle"}\n')

                    last_trigger[name] = now

            time.sleep(0.1)

        ser.close()
        self._shutdown()

    def _shutdown(self):
        self.status_update.emit("stopped")
        self.stopped.emit()
