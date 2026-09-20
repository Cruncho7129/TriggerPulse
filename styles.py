# styles.py
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

# =============================
# COLOR PALETTE
# =============================

# Base background
BACKGROUND_DARK_CHARCOAL = "#121212"
CARD_BACKGROUND = "#1E1E1E"
TEXT_PRIMARY = "#D3D3FF"
TEXT_SECONDARY = "#B0B4FF"
ACCENT_COLOR = "#6E76FF"
BORDER_LIGHT = "#2C2C2C"

# Status colors
STATUS_SUCCESS = "#4CAF50"
STATUS_FAILURE = "#E53935"
STATUS_WARNING = "#FFC107"

# =============================
# QSS STYLES (GLOBAL)
# =============================

MAIN_WINDOW_QSS = f"""
QWidget {{
    background-color: {BACKGROUND_DARK_CHARCOAL};
    color: {TEXT_PRIMARY};
    font-size: 11pt;
}}

QLabel {{
    color: {TEXT_PRIMARY};
}}

QComboBox {{
    background-color: {CARD_BACKGROUND};
    border: 1px solid {BORDER_LIGHT};
    padding: 5px;
    border-radius: 4px;
}}

QComboBox:hover {{
    border: 1px solid {ACCENT_COLOR};
}}

QPushButton {{
    background-color: {CARD_BACKGROUND};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 6px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
}}

QPushButton:hover {{
    background-color: {ACCENT_COLOR};
}}

QPushButton:pressed {{
    background-color: {BORDER_LIGHT};
}}

QLineEdit, QSpinBox {{
    background-color: {CARD_BACKGROUND};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 4px;
    padding: 4px;
}}

QListWidget {{
    background-color: {CARD_BACKGROUND};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 4px;
    color: {TEXT_PRIMARY};
}}

QScrollArea {{
    background-color: {BACKGROUND_DARK_CHARCOAL};
    border: none;
}}
"""

# =============================
# SHADOW EFFECT HELPERS
# =============================

def apply_shadow(widget, blur_radius=18, x_offset=0, y_offset=4, color=QColor(0, 0, 0, 160)):
    """
    Apply a drop shadow effect to a widget.
    Usage:
        from styles import apply_shadow
        apply_shadow(my_widget)
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setOffset(x_offset, y_offset)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)
