# ui_panels_center.py
# Populates the center panel of the MainWindow.

from PyQt6 import QtCore, QtGui, QtWidgets
from components.widgets import EquipmentSlot
import random # Keep random here for the dice roller logic

def _create_dice_roller(main_window: QtWidgets.QMainWindow) -> QtWidgets.QGroupBox:
    """Creates and returns the Dice Roller group box."""
    dice_group = QtWidgets.QGroupBox("Dice Roller")
    dice_layout = QtWidgets.QVBoxLayout()
    dice_group.setLayout(dice_layout)
    dice_group.setFlat(True)

    # Modifier spinbox (hidden, but controls the value)
    main_window.mod_spin = QtWidgets.QSpinBox()
    main_window.mod_spin.setRange(-30, 30)
    main_window.mod_spin.setValue(0)
    main_window.mod_spin.hide() # Hide this
    dice_layout.addWidget(main_window.mod_spin) # Add to layout so it has a parent

    # ---------- REVISED: Result box with overlaid buttons ----------
    
    # This QWidget will contain the grid layout
    result_screen_widget = QtWidgets.QWidget()
    result_screen_layout = QtWidgets.QGridLayout()
    result_screen_layout.setContentsMargins(0, 0, 0, 0)
    result_screen_layout.setSpacing(0)
    result_screen_widget.setLayout(result_screen_layout)

    # Main Result Display (QTextEdit) - This is the background
    main_window.roll_result = QtWidgets.QTextEdit() 
    main_window.roll_result.setReadOnly(True)
    main_window.roll_result.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    main_window.roll_result.setObjectName("rollResult")
    main_window.roll_result.setMinimumHeight(60) # Taller
    main_window.roll_result.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Expanding
    )
    main_window.roll_result.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
    main_window.roll_result.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    main_window.roll_result.setStyleSheet("""
        QTextEdit#rollResult { 
            font-size: 16px; 
            font-weight: 700; 
            color: #d0cddc;
            /* Add padding so text doesn't go under buttons */
            padding-top: 8px;
            padding-bottom: 8px;
            padding-left: 42px; 
            padding-right: 42px;
            background: #0f1113; 
            border: 1px solid #2a2a2f;
            border-radius: 6px; 
        }
    """)
    # Add the text edit to the grid, spanning all 3 columns
    result_screen_layout.addWidget(main_window.roll_result, 0, 0, 1, 3)

    # Left Modifier Button (-) - Overlaid
    mod_down_btn = QtWidgets.QPushButton("-")
    mod_down_btn.setObjectName("modButtonOverlay")
    mod_down_btn.setFixedSize(40, 60) # Match text box height
    mod_down_btn.setStyleSheet("""
        QPushButton#modButtonOverlay {
            background: transparent;
            border: none;
            color: #d0cddc;
            font-size: 18px;
            font-weight: 700;
        }
        QPushButton#modButtonOverlay:hover {
            color: #ffffff;
        }
    """)
    mod_down_btn.clicked.connect(main_window.on_mod_down)
    # Add to grid cell (0, 0)
    result_screen_layout.addWidget(mod_down_btn, 0, 0, 
                                   alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

    # Right Modifier Button (+) - Overlaid
    mod_up_btn = QtWidgets.QPushButton("+")
    mod_up_btn.setObjectName("modButtonOverlay")
    mod_up_btn.setFixedSize(40, 60) # Match text box height
    mod_up_btn.setStyleSheet("""
        QPushButton#modButtonOverlay {
            background: transparent;
            border: none;
            color: #d0cddc;
            font-size: 18px;
            font-weight: 700;
        }
        QPushButton#modButtonOverlay:hover {
            color: #ffffff;
        }
    """)
    mod_up_btn.clicked.connect(main_window.on_mod_up)
    # Add to grid cell (0, 2)
    result_screen_layout.addWidget(mod_up_btn, 0, 2, 
                                   alignment=QtCore.Qt.AlignmentFlag.AlignRight)

    # Make the middle column (where the text is) stretch
    result_screen_layout.setColumnStretch(1, 1)
    
    dice_layout.addWidget(result_screen_widget)
    
    main_window.mod_spin.valueChanged.connect(main_window.update_roll_display)
    main_window.update_roll_display()
    # ---------- END: Revised Result Box ----------

    # Dice buttons (from previous expanding layout)
    dice_buttons_grid = QtWidgets.QGridLayout()
    dice_buttons_grid.setSpacing(8) 
    dice_layout.addLayout(dice_buttons_grid)

    dice_types = [("d4", 4), ("d6", 6), ("d8", 8), ("d10", 10), ("d12", 12), ("d20", 20)]
    
    button_height = 45 # Taller buttons
    
    row = 0
    col = 0
    for name, sides in dice_types:
        btn = QtWidgets.QPushButton(name)
        btn.setMinimumHeight(button_height) 
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, 
            QtWidgets.QSizePolicy.Policy.Fixed
        )
        btn.clicked.connect(lambda checked, s=sides: main_window.on_dice_added(s))
        dice_buttons_grid.addWidget(btn, row, col)
        col += 1
        if col > 2: 
            col = 0
            row += 1
            
    # "C" (Clear) Button
    clear_btn = QtWidgets.QPushButton("C")
    clear_btn.setMinimumHeight((button_height * 2) + 8)
    clear_btn.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding, 
        QtWidgets.QSizePolicy.Policy.Fixed
    )
    clear_btn.clicked.connect(main_window.on_roll_clear) 
    clear_btn.setStyleSheet("""
        QPushButton {
            font-size: 16px;
            font-weight: 700;
            color: #d0cddc;
            background: #5a3a3a; /* Dark red */
            border-radius: 6px;
        }
        QPushButton:hover {
            background: #7a4a4a; /* Lighter red */
        }
    """)
    dice_buttons_grid.addWidget(clear_btn, 0, 3, 2, 1) 
            
    # "ROLL" Button
    roll_btn = QtWidgets.QPushButton("ROLL")
    roll_btn.setMinimumHeight(50) # Taller
    roll_btn.clicked.connect(main_window.on_roll_execute)
    roll_btn.setStyleSheet("""
        QPushButton {
            font-size: 16px; 
            font-weight: 700; 
            background: #3fbb7b; 
            color: #0f1113;
            border-radius: 6px;
        }
        QPushButton:hover {
            background: #50c88c;
        }
    """)
    roll_btn_layout = QtWidgets.QHBoxLayout()
    roll_btn_layout.setContentsMargins(0, 8, 0, 0) 
    roll_btn_layout.addWidget(roll_btn) # Button will now expand
    
    dice_layout.addLayout(roll_btn_layout)
    dice_layout.addStretch() 

    return dice_group

def populate_center_panel(main_window: QtWidgets.QMainWindow, layout: QtWidgets.QVBoxLayout):
    """
    Fills the center QVBoxLayout with equipment and dice,
    with the dice roller at the bottom.
    """
    # presentation area title
    title = QtWidgets.QLabel("Equipment")
    title.setStyleSheet("font-weight: 700; font-size: 16px;")
    layout.addWidget(title)

    # Equipment slots "person" layout
    slots_widget = QtWidgets.QWidget()
    slots_layout = QtWidgets.QGridLayout()
    slots_layout.setSpacing(14)
    slots_widget.setLayout(slots_layout)
    slots_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop) 

    slot_definitions = {
        "Helmet": (0, 1),
        "Left Hand": (1, 0),
        "Armor": (1, 1),
        "Right Hand": (1, 2),
        "Accessory": (2, 0),
        "Boots": (2, 1)
    }
    
    main_window.equip_slots = {} 

    for name, (r, c) in slot_definitions.items():
        container = QtWidgets.QWidget()
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(4)
        container.setLayout(v_layout)

        lbl = QtWidgets.QLabel(name)
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #888a8f; font-size: 10px;")

        slot = EquipmentSlot("Empty")
        
        v_layout.addWidget(lbl)
        v_layout.addWidget(slot)
        
        slots_layout.addWidget(container, r, c, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        main_window.equip_slots[name] = slot

    layout.addWidget(slots_widget, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

    layout.addStretch() # Push equipment to top, dice roller to bottom

    # Dice Roller (now at the bottom)
    dice_roller_group = _create_dice_roller(main_window)
    
    # Allow the groupbox to expand horizontally
    layout.addWidget(dice_roller_group, alignment=QtCore.Qt.AlignmentFlag.AlignBottom)
