# app.py
# PyQt6 app scaffold for a DnD-style character sheet UI (dark mode).
#
# This file contains the MainWindow, application entry point,
# and signal handlers.
#
# UI components are modularized into:
# - ui_styles.py:       Contains the DARK_MODE string
# - ui_widgets.py:      Custom QWidget classes (EquipmentSlot, etc.)
# - ui_panels_left.py:  Function to populate the left panel
# - ui_panels_center.py:Function to populate the center panel
# - ui_panels_right.py: Function to populate the right panel

from PyQt6 import QtCore, QtGui, QtWidgets
import sys
import random
import os
import sqlite3
import json

# --- Import modularized components ---
from components.styles import DARK_MODE
# Import InventoryList to use as the right-hand panel
from components.widgets import InventoryList 
# Import panel builders
from panels.left import populate_left_panel
from panels.center import populate_center_panel
from panels.right import populate_right_panel

# --- (REMOVED) DraggableTreeWidget class ---


# ---------- REVISED: Database Viewer Window (Tree/List View) ----------
class DbViewerWindow(QtWidgets.QWidget):
    """
    A new window for displaying database query results.
    Left panel: QTreeWidget for navigation.
    Right panel: Draggable InventoryList for items.
    """
    def __init__(self, title, data, data_type, parent_list, parent_main):
        super().__init__()
        self.parent_list = parent_list
        self.parent_list.append(self)
        self.parent_main = parent_main # Reference to MainWindow for DB calls
        self.data_type = data_type
        
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.setStyleSheet(DARK_MODE) 

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Splitter for list and details
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.setObjectName("viewerSplitter")
        
        # Left: Tree widget for grouped items (Navigation)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setObjectName("viewerTree")
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(False) # Left panel is NOT draggable
        self.tree.itemClicked.connect(self.on_item_clicked)
        
        # Right: List widget for draggable items
        self.list = InventoryList() # Use the draggable list widget
        self.list.setObjectName("viewerList")
        self.list.setDragEnabled(True) # Right panel IS draggable
        
        # Populate tree and, if necessary, the initial list
        self._populate_tree_and_list(data)
        
        splitter.addWidget(self.tree)
        splitter.addWidget(self.list)
        splitter.setSizes([250, 550]) # Initial size split
        
        layout.addWidget(splitter)
        self.setLayout(layout)

    def _populate_tree_and_list(self, data_dicts):
        """Fills the QTreeWidget and, for flat lists, the QListWidget."""
        self.tree.clear()
        self.list.clear()
        
        if self.data_type == 'spells':
            groups = {}
            for spell in data_dicts:
                groups.setdefault(spell['level'], []).append(spell)
            
            for level in sorted(groups.keys()):
                level_str = "Cantrips" if level == 0 else f"{level}-Level Spells"
                level_item = QtWidgets.QTreeWidgetItem(self.tree, [level_str])
                
                for spell in groups[level]:
                    spell_item = QtWidgets.QTreeWidgetItem(level_item, [spell['name']])
        
        elif self.data_type == 'equipment':
            groups = {}
            for item in data_dicts:
                cat = item['equipment_category_index']
                if not cat: cat = "other"
                groups.setdefault(cat, []).append(item)
            
            for cat in sorted(groups.keys()):
                cat_item = QtWidgets.QTreeWidgetItem(self.tree, [cat.replace('-', ' ').title()])

                for item in groups[cat]:
                    item_widget = QtWidgets.QTreeWidgetItem(cat_item, [item['name']])

        elif self.data_type == 'races':
            current_race_item = None
            for row in data_dicts:
                if current_race_item is None or current_race_item.text(0) != row['name']:
                    current_race_item = QtWidgets.QTreeWidgetItem(self.tree, [row['name']])
                
                if row['subrace_name']:
                    subrace_item = QtWidgets.QTreeWidgetItem(current_race_item, [row['subrace_name']])
            self.tree.expandAll()
            
        elif self.data_type in ['features', 'feats', 'classes']:
            # Flat list: populate BOTH tree and list
            for item in data_dicts:
                tree_item = QtWidgets.QTreeWidgetItem(self.tree, [item['name']])
                self.list.addItem(item['name']) # Add to list on the right
    
    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def on_item_clicked(self, item, column):
        """
        When a category is clicked, populate the right list with its children.
        If a child is clicked, do nothing.
        """
        
        # --- START FIX ---
        # Only repopulate the list if a CATEGORY (an item with children) is clicked.
        if item.childCount() > 0:
            self.list.clear() # Clear the list on the right
            
            # For Races, add the base race itself as the first draggable item
            if self.data_type == 'races' and not item.parent():
                self.list.addItem(item.text(0))
            
            # Add all children (e.g., all cantrips, all subraces)
            for i in range(item.childCount()):
                self.list.addItem(item.child(i).text(0))
        
        # If a child item is clicked (e.g., "Fire Bolt"), do nothing.
        # This allows the drag operation to start without interference.
        elif item.parent():
            pass 
        
        # If a flat-list item is clicked (e.g., "Feats"), do nothing.
        # The list is already populated.
        elif not item.parent() and not item.childCount():
            pass
        # --- END FIX ---
    
    # --- (REMOVED) _build_html_display method ---


# ---------- Main Window ----------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Sheet — Draft")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_MODE)

        # ---------- NEW: Database state ----------
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dnd_srd.db')
        self.open_viewers = [] # Holds references to open DB windows
        
        # ---------- Dice queue state ----------
        self.dice_queue = {} # e.g., {6: 2, 20: 1} for 2d6 + 1d20

        # Menu
        self._create_menu()

        # Central layout
        central = QtWidgets.QWidget()
        central_layout = QtWidgets.QHBoxLayout()
        central_layout.setContentsMargins(12, 12, 12, 12)
        central_layout.setSpacing(12)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        # Left panel (Character info)
        left_panel = QtWidgets.QFrame()
        left_panel.setObjectName("panel")
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(360)

        # Populate using imported function
        populate_left_panel(self, left_layout)

        # Center panel (presentation + equip slots + HP/AC)
        center_panel = QtWidgets.QFrame()
        center_panel.setObjectName("panel")
        center_layout = QtWidgets.QVBoxLayout()
        center_layout.setContentsMargins(12, 12, 12, 12)
        center_layout.setSpacing(12)
        center_panel.setLayout(center_layout)

        # Populate using imported function
        populate_center_panel(self, center_layout)

        # Right panel (spells, inventory, dice)
        right_panel = QtWidgets.QFrame()
        right_panel.setObjectName("panel")
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(10)
        right_panel.setLayout(right_layout)
        right_panel.setFixedWidth(400)

        # Populate using imported function
        populate_right_panel(self, right_layout)

        # Add panels to main layout
        central_layout.addWidget(left_panel)
        central_layout.addWidget(center_panel, stretch=1)
        central_layout.addWidget(right_panel)

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")

        # placeholders
        file_menu.addAction("New")
        file_menu.addAction("Open")
        file_menu.addAction("Save")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        view_menu.addAction("Toggle Dark Mode")  # HOOK: connect
        
        # ---------- DB Viewer Actions (Separated) ----------
        view_menu.addSeparator()
        view_menu.addAction("View Classes", self.on_view_classes)
        view_menu.addAction("View Spells", self.on_view_spells)
        view_menu.addAction("View Equipment", self.on_view_equipment)
        view_menu.addAction("View Features", self.on_view_features)
        view_menu.addAction("View Feats", self.on_view_feats)
        view_menu.addAction("View Races", self.on_view_races)
        
        help_menu.addAction("About")  # HOOK: show about

    # ---------- NEW: Database Helper Function ----------

    def _get_db_data(self, query: str):
        """
        Connects to the DB, runs a query, and returns headers, data, or an error.
        Returns: (headers, data_as_dicts, error_message)
        """
        abs_db_path = os.path.abspath(self.db_path)
        if not os.path.exists(abs_db_path):
            return None, None, f"Database file not found. Looked for:\n{abs_db_path}"

        conn = None
        try:
            conn = sqlite3.connect(f"file:{abs_db_path}?mode=ro", uri=True) # Read-only
            # Use sqlite3.Row to get results as dictionaries
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                return [], [], None # No results, but not an error
                
            headers = [desc[0] for desc in cursor.description]
            # Convert sqlite3.Row objects to standard dicts
            data_as_dicts = [dict(row) for row in rows] 
            
            return headers, data_as_dicts, None
                    
        except sqlite3.Error as e:
            return None, None, f"Database error: {e}"
        finally:
            if conn:
                conn.close()

    # ---------- NEW: Database Viewer Slots ----------

    def _show_db_viewer(self, title: str, query: str, data_type: str):
        """Helper to query DB and show results in a new window."""
        headers, data_dicts, error = self._get_db_data(query)
        
        if error:
            QtWidgets.QMessageBox.critical(self, "Database Error", error)
            return
        
        if not headers and not data_dicts:
            QtWidgets.QMessageBox.information(self, "Query Result", "No results found for this query.")
            return

        # Create and show the new window, passing in the data type and a
        # reference to this main window
        viewer = DbViewerWindow(title, data_dicts, data_type, self.open_viewers, self)
        viewer.show()

    @QtCore.pyqtSlot()
    def on_view_classes(self):
        self._show_db_viewer(
            "SRD Classes",
            "SELECT * FROM Class ORDER BY name",
            data_type='classes'
        )

    @QtCore.pyqtSlot()
    def on_view_spells(self):
        # Gets all spell data for the detailed view
        self._show_db_viewer(
            "SRD Spells",
            """
            SELECT * FROM Spell
            ORDER BY level, name
            """,
            data_type='spells'
        )

    @QtCore.pyqtSlot()
    def on_view_equipment(self):
        # Gets all equipment data for the detailed view
        self._show_db_viewer(
            "SRD Equipment",
            """
            SELECT * FROM Equipment
            ORDER BY equipment_category_index, name
            """,
            data_type='equipment'
        )

    @QtCore.pyqtSlot()
    def on_view_features(self):
        """Views class/subclass features, which are in the Feature table."""
        self._show_db_viewer(
            "SRD Features",
            "SELECT * FROM Feature ORDER BY name",
            data_type='features'
        )

    @QtCore.pyqtSlot()
    def on_view_feats(self):
        """Views Feats from the Feat table."""
        self._show_db_viewer(
            "SRD Feats",
            "SELECT * FROM Feat ORDER BY name",
            data_type='feats'
        )

    @QtCore.pyqtSlot()
    def on_view_races(self):
        # Joins Race and Subrace to build the tree structure
        self._show_db_viewer(
            "SRD Races and Subraces",
            """
            SELECT
                R.*,
                S.name as subrace_name,
                S."index" as subrace_index,
                S.description as subrace_desc
            FROM Race AS R
            LEFT JOIN Subrace AS S ON R."index" = S.race_index
            ORDER BY R.name, S.name
            """,
            data_type='races'
        )
        
    # ---------- Dice Roller Slots ----------

    @QtCore.pyqtSlot()
    def on_mod_down(self):
        """Decrements the (hidden) modifier spinbox."""
        if hasattr(self, 'mod_spin'):
            self.mod_spin.setValue(self.mod_spin.value() - 1)
            self.update_roll_display() # Update display

    @QtCore.pyqtSlot()
    def on_mod_up(self):
        """Increments the (hidden) modifier spinbox."""
        if hasattr(self, 'mod_spin'):
            self.mod_spin.setValue(self.mod_spin.value() + 1)
            self.update_roll_display() # Update display

    @QtCore.pyqtSlot()
    def on_roll_clear(self):
        """Clears the dice queue and updates the display."""
        self.dice_queue = {}
        self.update_roll_display()

    @QtCore.pyqtSlot(int)
    def update_roll_display(self, value: int = None):
        """
        Updates the result box text to show the current formula.
        """
        if not hasattr(self, 'roll_result'): return
        
        mod = self.mod_spin.value()
        mod_str = f" + {mod}" if mod > 0 else f" - {abs(mod)}" if mod < 0 else ""

        formula_parts = []
        # Sort by die type (d4, d6, etc.)
        for sides, count in sorted(self.dice_queue.items()):
            formula_parts.append(f"{count}d{sides}")
        
        formula_str = " + ".join(formula_parts)

        if not formula_str and mod == 0:
            self.roll_result.setPlaceholderText("Build your roll...")
            self.roll_result.setText("")
        elif not formula_str and mod != 0:
            self.roll_result.setText(f"{mod}") # Just show modifier
        else:
            self.roll_result.setText(f"{formula_str}{mod_str}")

    @QtCore.pyqtSlot(int)
    def on_dice_added(self, sides: int):
        """
        Adds a die to the queue and updates the display.
        """
        self.dice_queue[sides] = self.dice_queue.get(sides, 0) + 1
        self.update_roll_display()

    @QtCore.pyqtSlot()
    def on_roll_execute(self):
        """
        Rolls all dice in the queue, displays the result, and clears
        the queue.
        """
        if not self.dice_queue:
             # If no dice, just "roll" the modifier
             mod = self.mod_spin.value()
             self.roll_result.setText(f"Result: {mod} [Mod: {mod}]")
             return

        total_roll = 0
        roll_details = []

        for sides, count in sorted(self.dice_queue.items()):
            rolls_for_this_type = []
            for _ in range(count):
                roll = random.randint(1, sides)
                total_roll += roll
                rolls_for_this_type.append(str(roll))
            
            roll_details.append(f"{count}d{sides} ({', '.join(rolls_for_this_type)})")

        mod = self.mod_spin.value()
        final_total = total_roll + mod
        
        mod_str = f" + {mod}" if mod > 0 else f" - {abs(mod)}" if mod < 0 else ""
        details_str = " | ".join(roll_details)

        self.roll_result.setText(f"Result: {final_total} [{details_str}{mod_str}]")
        
        # Clear the queue for the next roll
        self.dice_queue = {}


# ---------- Main ----------
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()