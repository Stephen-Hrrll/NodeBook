
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import Qt,  QMimeData, QByteArray, QDataStream, QIODevice
from PySide6.QtGui import QDrag, QPixmap
from Node import NodeGraphic, DiffNode

from PySide6.QtCore import Signal




class ObjectLibrary:
    """This class stores information about the types of nodes that can be created."""
    def __init__(self):
        self.node_types = [
            {"name": "NodeWidget", "icon": "icon1.png", "node_class": 'NodeGraphic'},
            {"name": "DiffNode", "icon": "icon2.png", "node_class": 'DiffNode'},
            # Add more node types as needed
        ]

class DragItem(QLabel):
    """This is an item that can be dragged and dropped."""
    def __init__(self, node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(25, 5, 25, 5)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        # Store data separately from display label, but use label for default.
        print("DragItem.__init__ node:", type(node))
        self.node = node

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
        
            drag = QDrag(self)
            mime = QMimeData()
            
            # Use QDataStream to serialize the node object
            # data = QByteArray()
            # stream = QDataStream(data, QIODevice.OpenModeFlag.WriteOnly)
            # print("DragItem.mouseMoveEvent self.node:", self.node)
            # stream.writeQString(self.node)  # Store the class name or other identifier
            
            mime.setText(self.node)
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)

class DragWidget(QWidget):
    """
    Generic list sorting handler.
    This class is a widgete where things can be dragged around and ordered in.
    """

    orderChanged = Signal(list)

    def __init__(self, *args, orientation=Qt.Orientation.Vertical, **kwargs):
        super().__init__()
        self.setAcceptDrops(True)

        # Store the orientation for drag checks later.
        self.orientation = orientation

        if self.orientation == Qt.Orientation.Vertical:
            self.blayout = QVBoxLayout()
        else:
            self.blayout = QHBoxLayout()

        self.setLayout(self.blayout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()
        self.blayout.removeWidget(widget)

        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            if self.orientation == Qt.Orientation.Vertical:
                # Drag drop vertically.
                drop_here = pos.y() < w.y() + w.size().height() // 2
            else:
                # Drag drop horizontally.
                drop_here = pos.x() < w.x() + w.size().width() // 2

            if drop_here:
                break

        else:
            # We aren't on the left hand/upper side of any widget,
            # so we're at the end. Increment 1 to insert after.
            n += 1

        self.blayout.insertWidget(n, widget)
        self.orderChanged.emit(self.get_item_data())

        e.accept()

    def addItem(self, item):
        self.blayout.addWidget(item)

    def getItemData(self):
        data = []
        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            data.append(w.data)
        return data



class ObjectLibraryDock(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Object Library", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        # You can add a widget here, like a QListWidget or QTreeWidget, to display objects
        self.drag = DragWidget(orientation=Qt.Orientation.Vertical)
        
        self.object_library = ObjectLibrary()

        # Add some example items
        for idx, item_info in enumerate(self.object_library.node_types):
            node_type = item_info["node_class"]
            item = DragItem(node_type, item_info["name"])
            self.drag.addItem(item)

        # self.drag.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.drag.orderChanged.connect(print)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.drag)
        layout.addStretch(1)
        container.setLayout(layout)

        self.setWidget(container)

