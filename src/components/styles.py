# styles.py
# Contains the dark stylesheet for the application.

DARK_MODE = """
QMainWindow { background-color: #121217; color: #e6eef3; }
QFrame#panel { background-color: #18181b; border-radius: 8px; border: 1px solid #2a2a2f; }
QLabel { color: #e6eef3; background: transparent; }
QLineEdit, QTextEdit, QSpinBox, QComboBox, QListWidget { background: #0f1113; color: #e6eef3; border: 1px solid #2a2a2f; border-radius: 6px; padding: 4px; }
QSpinBox { padding: 2px 4px; }
QMenuBar { background-color: #141416; color: #e6eef3; }
QMenuBar::item:selected { background: #2a2a2f; }
QPushButton { background: #2a2a2f; border-radius: 6px; padding: 6px; }
QPushButton:hover { background: #3a3a3f; }
QListWidget::item { padding: 6px; }
QListWidget::item:selected { background: #33343a; color: #fff; }
QGroupBox { margin-top: 12px; color:#cfd8dd; border: 0px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }

/* Style for the new stat boxes in the left panel */
QFrame#statBox { 
    background: #0f1113; 
    border-radius: 6px; 
    border: 1px solid #2a2a2f; 
}
QLabel#statLabel { 
    font-weight: 700; 
    background: transparent; 
    border: 0px;
    font-size: 11px;
}
QLineEdit#statEdit {
    font-size: 12px;
}

/* Style for the dice roller result box */
QLineEdit#rollResult {
    font-size: 16px; 
    font-weight: 700; 
    color: #d0cddc;
    padding: 8px;
}
QPushButton#modButton {
    min-width: 30px;
    max-width: 30px;
    padding: 6px;
    font-weight: 700;
}
"""