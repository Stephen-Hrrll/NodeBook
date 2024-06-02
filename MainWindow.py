from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from ObjectLibraryDock import ObjectLibraryDock
from ProjectHierarchyDock import ProjectHierarchyDock
from NodeCanvas import NodeCanvas
from FileManager import FileManager

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Programming")
        self.resizable = True
        self.setAcceptDrops(True)
        
        screen_geometry = QtGui.QGuiApplication.primaryScreen().geometry()
        #set the minimum width of the window to half the screen width and height
        self.setMinimumWidth(screen_geometry.width() // 2)
        self.setMinimumHeight(int(screen_geometry.height() // 2))

        central_widget = QtWidgets.QWidget(self)
        central_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(central_layout)
        central_layout.setContentsMargins(0, 0, 0, 0)

        self.object_library_dock = ObjectLibraryDock(self)
        self.project_hierarchy_dock = ProjectHierarchyDock(self)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.object_library_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.project_hierarchy_dock)

        self.node_canvas = NodeCanvas()
        central_layout.addWidget(self.node_canvas)
        central_layout.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(central_widget)
        self.createMenus()

    def createMenus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")
        # Add actions to the file menu
        new_action = QtGui.QAction("New", self)
        open_action = QtGui.QAction("Open", self)
        save_action = QtGui.QAction("Save", self)

        self.file_man = FileManager(canvas=self.node_canvas) 
        # Connect to the FileManager methods
        open_action.triggered.connect(self.file_man.loadProject)
        save_action.triggered.connect(self.file_man.saveProject)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())