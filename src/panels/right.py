# right_panel.py
# Populates the right panel of the MainWindow.

from PyQt6 import QtCore, QtGui, QtWidgets
# UPDATED: We only need InventoryList from our custom widgets
from components.widgets import InventoryList

def populate_right_panel(main_window: QtWidgets.QMainWindow, layout: QtWidgets.QVBoxLayout):
    """
    Fills the right-hand QVBoxLayout with spells, inventory, etc.
    """
    # Spells section
    spells_group = QtWidgets.QGroupBox("Spells slots")
    spells_layout = QtWidgets.QVBoxLayout()
    spells_group.setLayout(spells_layout)

    # Spell slots
    slots_grid = QtWidgets.QGridLayout()
    slots_grid.setSpacing(8)
    slots_grid.setContentsMargins(10, 0, 10, 0) # Add some padding
    main_window.spell_slot_spins = {} 
    
    ordinals = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]

    for lvl in range(1, 10): # Levels 1 to 9
        if lvl <= 5: # Top row: 1-5
            row = 0
            col = lvl - 1
        else: # Bottom row: 6-9
            row = 1
            col = lvl - 6
        
        # This is the vertical cell
        box = QtWidgets.QFrame()
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0) # Tight spacing
        box.setLayout(v_layout)
        box.setStyleSheet("background: transparent; border: 0px;") # No border
        
        # The number (QSpinBox) - on top
        spin = QtWidgets.QSpinBox()
        spin.setRange(0, 20)
        spin.setValue(0)
        spin.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        spin.setFixedWidth(60)
        # Style to look like the image
        spin.setStyleSheet("""
            QSpinBox { 
                font-size: 18px; 
                font-weight: 700; 
                color: #d0cddc;
                background: transparent; 
                border: 0px; 
                padding-bottom: 0px;
                margin-bottom: -2px; /* Pull label up */
            }
        """)
        
        # The label (e.g., "1st") - on bottom
        lbl = QtWidgets.QLabel(ordinals[lvl-1])
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #888a8f; font-size: 11px; background: transparent; border: 0px;")
        
        # Add in new order: number on top, label on bottom
        v_layout.addWidget(spin)
        v_layout.addWidget(lbl)
        
        slots_grid.addWidget(box, row, col, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        main_window.spell_slot_spins[lvl] = spin
        
    # Add an empty widget to col 4, row 1 to push 6-9 to the left
    slots_grid.addWidget(QtWidgets.QWidget(), 1, 4)
    slots_grid.setColumnStretch(4, 1) 
        
    spells_layout.addLayout(slots_grid)
    layout.addWidget(spells_group)

    # --- QToolBox Accordion for Feats, Spells, and Inventory ---
    main_window.accordion = QtWidgets.QToolBox()
    main_window.accordion.setStyleSheet("QToolBox::tab { background: #1a1a1f; padding: 6px; border-radius: 4px; }")

    # Feats page
    main_window.feats_page = QtWidgets.QWidget()
    feats_layout = QtWidgets.QVBoxLayout()
    feats_layout.setContentsMargins(0, 0, 0, 0) # Remove padding
    # UPDATED: Use InventoryList
    main_window.feats_txt = InventoryList()
    
    # --- NEW: Add placeholder to fix layout bug ---
    _feats_placeholder = QtWidgets.QListWidgetItem("No feats added")
    _feats_placeholder.setFlags(QtCore.Qt.ItemFlag.NoItemFlags) # Not selectable, not enabled
    _feats_placeholder.setForeground(QtGui.QColor("#888a8f")) # Gray
    main_window.feats_txt.addItem(_feats_placeholder)
    # --- END NEW ---
    
    feats_layout.addWidget(main_window.feats_txt)
    main_window.feats_page.setLayout(feats_layout)

    # Features page
    main_window.feature_page = QtWidgets.QWidget()
    feature_layout = QtWidgets.QVBoxLayout()
    feature_layout.setContentsMargins(0, 0, 0, 0) # Remove padding
    # UPDATED: Use InventoryList
    main_window.feature_txt = InventoryList()

    # --- NEW: Add placeholder to fix layout bug ---
    _features_placeholder = QtWidgets.QListWidgetItem("No features added")
    _features_placeholder.setFlags(QtCore.Qt.ItemFlag.NoItemFlags) # Not selectable, not enabled
    _features_placeholder.setForeground(QtGui.QColor("#888a8f")) # Gray
    main_window.feature_txt.addItem(_features_placeholder)
    # --- END NEW ---
    
    feature_layout.addWidget(main_window.feature_txt)
    main_window.feature_page.setLayout(feature_layout)

    # Spells page
    main_window.spells_page = QtWidgets.QWidget()
    spells_vbox = QtWidgets.QVBoxLayout()
    spells_vbox.setContentsMargins(0, 0, 0, 0) # Remove padding
    # UPDATED: Use InventoryList
    main_window.spell_info = InventoryList()

    # --- NEW: Add placeholder to fix layout bug ---
    _spells_placeholder = QtWidgets.QListWidgetItem("No spells added")
    _spells_placeholder.setFlags(QtCore.Qt.ItemFlag.NoItemFlags) # Not selectable, not enabled
    _spells_placeholder.setForeground(QtGui.QColor("#888a8f")) # Gray
    main_window.spell_info.addItem(_spells_placeholder)
    # --- END NEW ---

    spells_vbox.addWidget(main_window.spell_info)
    main_window.spells_page.setLayout(spells_vbox)

    # Inventory page
    main_window.inv_page = QtWidgets.QWidget()
    inv_vbox = QtWidgets.QVBoxLayout()
    inv_vbox.setContentsMargins(0, 0, 0, 0) # Remove padding
    main_window.inventory = InventoryList()
    
    _inventory_placeholder = QtWidgets.QListWidgetItem("No inventory items")
    _inventory_placeholder.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
    _inventory_placeholder.setForeground(QtGui.QColor("#888a8f"))
    main_window.inventory.addItem(_inventory_placeholder)

    inv_vbox.addWidget(main_window.inventory)
    main_window.inv_page.setLayout(inv_vbox)

    main_window.accordion.addItem(main_window.feats_page, "Feats")
    main_window.accordion.addItem(main_window.feature_page, "Features")
    main_window.accordion.addItem(main_window.spells_page, "Spells")
    main_window.accordion.addItem(main_window.inv_page, "Inventory")

    layout.addWidget(main_window.accordion)