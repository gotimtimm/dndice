# widgets.py
# Contains custom widgets for the character sheet.

from PyQt6 import QtCore, QtGui, QtWidgets

# --- (REMOVED) DroppableTextEdit class ---
# We will use the updated InventoryList instead.

# ---------- Drag / Drop: EquipmentSlot ----------
class EquipmentSlot(QtWidgets.QLabel):
    """
    Accepts drops from QListWidget inventory items. Shows item text.
    Double-click to clear.
    """
    def __init__(self, placeholder="Empty", parent=None):
        super().__init__(parent)
        self.setObjectName("equipSlot")
        self.setText(placeholder)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(100, 100)
        self.setStyleSheet("""
            QLabel#equipSlot {
                background: #0f1113;
                border: 2px dashed #2f2f34;
                border-radius: 8px;
                color: #bfc9cf;
            }
        """)
        self.setAcceptDrops(True)
        # store item data
        self.item_text = None

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        text = event.mimeData().text()
        self.set_item(text)
        event.acceptProposedAction()
        # HOOK: emit a signal or call a method to inform your backend that
        # `text` was equipped into this slot.
        # Example: self.item_equipped.emit(self, text)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        # clear slot on double-click
        self.clear_item()
        # HOOK: inform backend that this slot was cleared.

    def set_item(self, text):
        self.item_text = text
        self.setText(text)
        self.setStyleSheet("""
            QLabel#equipSlot {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f1417, stop:1 #15171a);
                border: 2px solid #3fbb7b;
                border-radius: 8px;
                color: #e6f9ee;
            }
        """)

    def clear_item(self):
        self.item_text = None
        self.setText("Empty")
        self.setStyleSheet("""
            QLabel#equipSlot {
                background: #0f1113;
                border: 2px dashed #2f2f34;
                border-radius: 8px;
                color: #bfc9cf;
            }
        """)

# ---------- Inventory List (UPDATED) ----------
class InventoryList(QtWidgets.QListWidget):
    """
    Draggable list widget. Each item has plain text.
    UPDATED: Now also accepts drops to add new items.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        # UPDATED: Set to True to accept drops
        self.setAcceptDrops(True) 
        self.setDefaultDropAction(QtCore.Qt.DropAction.CopyAction)
        self.setSpacing(4)
        self.setMinimumWidth(220)
        self.setMaximumWidth(320)

    # NEW: Handle incoming drops
    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    # NEW: Add dropped item to the list
    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        text = event.mimeData().text()
        if text:
            # Check if item already exists
            if not self.findItems(text, QtCore.Qt.MatchFlag.MatchExactly):
                self.addItem(text)
                event.acceptProposedAction()
        else:
            event.ignore()

    # This function handles dragging *from* this list
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        mime = QtCore.QMimeData()
        mime.setText(item.text())

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime)

        # small pixmap for drag preview
        pix = QtGui.QPixmap(self.viewport().visibleRegion().boundingRect().size())
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pix)
        painter.setPen(QtGui.QPen(QtGui.QColor("#e6eef3")))
        painter.drawText(10, 20, item.text())
        painter.end()
        drag.setHotSpot(QtCore.QPoint(10, 10))
        drag.setPixmap(pix)

        # Use CopyAction by default
        drag.exec(QtCore.Qt.DropAction.CopyAction)

# ---------- Image Label ----------
class ImageLabel(QtWidgets.QLabel):
    """
    A QLabel that accepts clicks to open an image file dialog.
    Displays the selected image.
    """
    def __init__(self, placeholder_text="Image", parent=None):
        super().__init__(parent)
        self.setText(placeholder_text)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(120, 120) # Changed: Made smaller and square
        self.setStyleSheet("""
            ImageLabel {
                background: #0f1113;
                border: 2px dashed #2f2f34;
                border-radius: 8px;
                color: #bfc9cf;
            }
            ImageLabel:hover {
                border: 2px dashed #4f4f54;
                color: #e6eef3;
            }
        """)
        self.image_path = None

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Character Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.set_image(file_path)

    def set_image(self, file_path):
        self.image_path = file_path
        pixmap = QtGui.QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)
        self.setText("") # Clear placeholder text
        self.setStyleSheet("border-radius: 8px;") # Clear dashed border style