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

/* ---------- NEW: Styles for the DB Viewer Window ---------- */

/* The Tree Widget (Left Panel) */
QTreeWidget#viewerTree {
    background-color: #18181b; /* Darker than the list */
    border: 1px solid #2a2a2f;
    border-radius: 6px;
    color: #e6eef3;
    padding: 4px;
}
/* Top-level items (e.g., "Cantrips") */
QTreeWidget::item:!selected {
    color: #cfd8dd;
    font-weight: 700;
    padding-top: 5px;
    padding-bottom: 5px;
}
/* Child items (e.g., "Fire Bolt") */
QTreeWidget::item:!selected:!parent {
    color: #e6eef3;
    font-weight: 400;
    padding: 0px;
}
QTreeWidget::item:selected {
    background: #3fbb7b; /* Accent green */
    color: #0f1113;
    font-weight: 700;
}
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    image: url(icons:light/rightarrow.png); /* Use built-in icons */
}
QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {
    image: url(icons:light/downarrow.png); /* Use built-in icons */
}

/* (REMOVED) QTextEdit#viewerDetails styles */

/* NEW: The List Widget in the viewer (Right Panel) */
QListWidget#viewerList {
    background: #0f1113;
    border: 1px solid #2a2a2f;
    border-radius: 6px;
    padding: 4px;
}
QListWidget#viewerList::item {
    padding: 7px;
    color: #e6eef3;
}
QListWidget#viewerList::item:selected {
    background: #33343a;
    color: #fff;
    border-radius: 4px;
}
QListWidget#viewerList::item:hover:!selected {
    background: #18181b;
    border-radius: 4px;
}


/* Splitter handle */
QSplitter::handle {
    background: #121217;
}
QSplitter::handle:horizontal {
    width: 8px;
}
QSplitter::handle:vertical {
    height: 8px;
}
QSplitter::handle:hover {
    background: #2a2a2f;
}

/* Scrollbar styles */
QScrollBar:vertical {
    background: #18181b;
    width: 12px;
    margin: 0px;
    border: 0px;
}
QScrollBar::handle:vertical {
    background: #3a3a3f;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #4a4a4f;
}
QScrollBar:horizontal {
    background: #18181b;
    height: 12px;
    margin: 0px;
    border: 0px;
}
QScrollBar::handle:horizontal {
    background: #3a3a3f;
    min-width: 20px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
    background: #4a4a4f;
}
QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
    background: none;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}
"""