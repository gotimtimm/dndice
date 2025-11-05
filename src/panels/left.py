# left_panel.py
# Populates the left panel of the MainWindow.

from PyQt6 import QtCore, QtGui, QtWidgets
from components.widgets import ImageLabel

def _create_stat_box(label_text: str, widget: QtWidgets.QWidget) -> QtWidgets.QFrame:
    """Helper to create a styled stat box (like abilities)."""
    box = QtWidgets.QFrame()
    box.setObjectName("statBox")
    layout = QtWidgets.QVBoxLayout()
    layout.setContentsMargins(4, 4, 4, 4)
    layout.setSpacing(4)
    box.setLayout(layout)

    lbl = QtWidgets.QLabel(label_text)
    lbl.setObjectName("statLabel")
    lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    
    # Center spinboxes, but not lineedits
    if isinstance(widget, QtWidgets.QSpinBox):
        widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
    elif isinstance(widget, QtWidgets.QLineEdit):
        widget.setObjectName("statEdit")

    layout.addWidget(lbl)
    layout.addWidget(widget)
    return box


def populate_left_panel(main_window: QtWidgets.QMainWindow, layout: QtWidgets.QVBoxLayout):
    """
    Fills the left-hand QVBoxLayout with character info, stats, and skills.
    """
    
    # Top Character Card (Image + Info)
    char_card_widget = QtWidgets.QWidget()
    char_card_layout = QtWidgets.QHBoxLayout()
    char_card_layout.setContentsMargins(0, 0, 0, 0)
    char_card_layout.setSpacing(10)
    char_card_widget.setLayout(char_card_layout)

    # Left side: Image
    main_window.char_image = ImageLabel("Image")
    char_card_layout.addWidget(main_window.char_image)
    
    # Right side: Info Fields
    info_layout = QtWidgets.QFormLayout()
    info_layout.setSpacing(8)
    info_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
    info_layout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

    main_window.name_edit = QtWidgets.QLineEdit("Name")
    main_window.class_edit = QtWidgets.QLineEdit("Class")
    main_window.race_edit = QtWidgets.QLineEdit("Race")
    main_window.level_spin = QtWidgets.QSpinBox()
    main_window.level_spin.setRange(1, 30)
    main_window.level_spin.setValue(1)

    info_layout.addRow("Name:", main_window.name_edit)
    info_layout.addRow("Class:", main_window.class_edit)
    info_layout.addRow("Race:", main_window.race_edit)
    info_layout.addRow("Level:", main_window.level_spin)

    char_card_layout.addLayout(info_layout)
    layout.addWidget(char_card_widget)

    # ---------- NEW: Combat Stats ----------
    stats_group = QtWidgets.QGroupBox("Combat Stats")
    stats_grid = QtWidgets.QGridLayout()
    stats_grid.setSpacing(10)
    stats_group.setLayout(stats_grid)

    # Create widgets
    main_window.hp_spin = QtWidgets.QSpinBox()
    main_window.hp_spin.setRange(0, 999)
    main_window.hp_spin.setValue(25)
    
    main_window.ac_spin = QtWidgets.QSpinBox()
    main_window.ac_spin.setRange(0, 99)
    main_window.ac_spin.setValue(15)

    main_window.speed_spin = QtWidgets.QSpinBox()
    main_window.speed_spin.setRange(0, 200)
    main_window.speed_spin.setValue(30)
    
    main_window.init_spin = QtWidgets.QSpinBox()
    main_window.init_spin.setRange(-10, 30)
    main_window.init_spin.setValue(2)

    main_window.perc_spin = QtWidgets.QSpinBox()
    main_window.perc_spin.setRange(0, 50)
    main_window.perc_spin.setValue(10)

    main_window.hd_edit = QtWidgets.QLineEdit()
    main_window.hd_edit.setPlaceholderText("e.g., 1d8")

    # Create boxes
    hp_box = _create_stat_box("HP", main_window.hp_spin)
    ac_box = _create_stat_box("AC", main_window.ac_spin)
    speed_box = _create_stat_box("Speed", main_window.speed_spin)
    init_box = _create_stat_box("Initiative", main_window.init_spin)
    perc_box = _create_stat_box("Passive Perc.", main_window.perc_spin)
    hd_box = _create_stat_box("Hit Dice", main_window.hd_edit)
    
    # Add to grid
    stats_grid.addWidget(hp_box, 0, 0)
    stats_grid.addWidget(ac_box, 0, 1)
    stats_grid.addWidget(speed_box, 0, 2)
    stats_grid.addWidget(init_box, 1, 0)
    stats_grid.addWidget(perc_box, 1, 1)
    stats_grid.addWidget(hd_box, 1, 2)

    layout.addWidget(stats_group)
    # ---------- END: Combat Stats ----------

    # Abilities
    ab_group = QtWidgets.QGroupBox("Ability Scores")
    ab_grid = QtWidgets.QGridLayout()
    ab_grid.setSpacing(10)
    ab_group.setLayout(ab_grid)

    labels = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    main_window.ability_spins = {}

    for i, lab in enumerate(labels):
        row = i // 3
        col = i % 3

        spin = QtWidgets.QSpinBox()
        spin.setRange(1, 30)
        spin.setValue(10)
        
        cell_widget = _create_stat_box(lab, spin)
        
        ab_grid.addWidget(cell_widget, row, col)
        main_window.ability_spins[lab] = spin

    layout.addWidget(ab_group)

    # Skills
    skills_group = QtWidgets.QGroupBox("Skills")
    skills_layout = QtWidgets.QGridLayout()
    skills_layout.setSpacing(8)
    skills_layout.setColumnStretch(1, 1) # Add stretch after names
    skills_layout.setColumnStretch(3, 1) # Add stretch after names
    skills_group.setLayout(skills_layout)
    
    main_window.skill_spins = {}
    skill_names = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", 
        "History", "Insight", "Intimidation", "Investigation", "Medicine", 
        "Nature", "Perception", "Performance", "Persuasion", "Religion", 
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Create 9 rows
    for i in range(9):
        # Left column skill
        skill_left_name = skill_names[i]
        spin_left = QtWidgets.QSpinBox()
        spin_left.setRange(-5, 15)
        spin_left.setValue(0)
        spin_left.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        spin_left.setFixedWidth(40)
        main_window.skill_spins[skill_left_name] = spin_left
        
        skills_layout.addWidget(spin_left, i, 0)
        skills_layout.addWidget(QtWidgets.QLabel(skill_left_name), i, 1)

        # Right column skill
        skill_right_name = skill_names[i + 9]
        spin_right = QtWidgets.QSpinBox()
        spin_right.setRange(-5, 15)
        spin_right.setValue(0)
        spin_right.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        spin_right.setFixedWidth(40)
        main_window.skill_spins[skill_right_name] = spin_right
        
        skills_layout.addWidget(spin_right, i, 2)
        skills_layout.addWidget(QtWidgets.QLabel(skill_right_name), i, 3)

    layout.addWidget(skills_group)

    # HOOK: connect signals to save/update functions as needed
    # e.g. main_window.name_edit.editingFinished.connect(main_window.on_name_change)