from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction


class ContextMenu(QMenu):
    """This class creates the base context menu for nodes, edges and the canvas(those classes are below). 
    The menu options will be the same for both nodes and the canvas, but only
    the appropriate options will be enabled based on the context of the right-click.
    For example, you shouldnt be able to paste a copied node on to another node."""
    def __init__(self, canvas=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.setupActions()
    

    def setupActions(self):
        self.cut_action = QAction("Cut")
        self.copy_action = QAction("Copy")
        self.paste_action = QAction("Paste")
        self.delete_action = QAction("Delete")
        self.select_all_action = QAction("Select All")
        self.undo_action = QAction("Undo")
        self.redo_action = QAction("Redo")

        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addAction(self.delete_action)
        self.addAction(self.select_all_action)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)

    
    def setActionsEnabled(self, delete_enabled=False, copy_enabled=False, 
                            paste_enabled=False, cut_enabled=False, select_all_enabled=False,
                            undo_enabled=False, redo_enabled=False):
        # set the enabled state of the actions based on the context of the right-click,
        # for example, if the user right-clicks on a node, the delete action should be enabled
        # if the user right-clicks on a blank space, the delete action should be disabled
        self.delete_action.setEnabled(delete_enabled)
        self.copy_action.setEnabled(copy_enabled)
        self.paste_action.setEnabled(paste_enabled)
        self.cut_action.setEnabled(cut_enabled)
        self.select_all_action.setEnabled(select_all_enabled)
        self.undo_action.setEnabled(undo_enabled)
        self.redo_action.setEnabled(redo_enabled)
    
    def connectActionsToMethods():
        # connect the actions to the appropriate methods, to be implemented
        #by NodeContextMenu or CanvasContextMenu, or EdgeContextMenu, or any
        # other class that needs this menu
        pass


class NodeContextMenu(ContextMenu):
    def __init__(self, canvas=None, node=None):
        super().__init__(canvas)
        self.node = node
        self.canvas = canvas
        self.setActionsEnabled(delete_enabled=True, copy_enabled=True)
        self.connectActionsToMethods()

    def connectActionsToMethods(self):
        # print("NodeContextMenu.connect_actions_to_methods canvas", self.canvas) 
        # connect the actions to the appropriate methods in Node.py
        self.delete_action.triggered.connect(lambda: self.canvas.deleteNodeAndEdges(self.node))
        # self.copy_action.triggered.connect(self.canvas.copy_node)


class EdgeContextMenu(ContextMenu):
    def __init__(self, canvas=None, edge=None):
        super().__init__(canvas)
        self.edge = edge
        self.canvas = canvas
        self.setActionsEnabled(delete_enabled=True)
        self.connectActionsToMethods()

    def connectActionsToMethods(self):
        # connect the actions to the appropriate methods in Edge.py
        self.delete_action.triggered.connect(lambda: self.canvas.deleteEdge(self.edge))
    