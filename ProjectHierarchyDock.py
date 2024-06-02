from PySide6 import QtWidgets
from PySide6.QtCore import Qt

class ProjectHierarchyDock(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Project Hierarchy", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        # You can add a widget here, like a QTreeWidget, to display the project hierarchy
