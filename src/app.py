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

# --- Import modularized components ---
from components.styles import DARK_MODE
# Import panel builders
from panels.left import populate_left_panel
from panels.center import populate_center_panel
from panels.right import populate_right_panel

# ---------- Main Window ----------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Sheet — Draft")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_MODE)

        # ---------- NEW: Dice queue state ----------
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
        help_menu.addAction("About")  # HOOK: show about

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