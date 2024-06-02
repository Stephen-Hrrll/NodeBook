from Node import DiffNode, NodeGraphic
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QMouseEvent, QPainter
from PySide6.QtCore import QDataStream, QIODevice, Qt, QEvent

from Edge import Edge
from Pin import PinGraphic


class Graph:
    """This class manages the graph of nodes and edges."""
    def __init__(self):
        self.edges = []
        self.nodes = []
        #used in doubleClickEvent here and in PinGraph to track an unfinished connection
        self.connection = {"start": None, "end": None}

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def createNode(self, dict):
        """create a node from a dictionary, (used to load a saved project)"""
        node = self.chooseClass(dict["class_name"])
        node.setPos(dict["x"], dict["y"])
        
        node.id = dict["id"]
        node.code_editor.setPlainText(dict["code"])
        node.text = dict["text"]
        # TODO:node.nodes_within = self.create_nodes_within(dict["nodes_within"], node)
        return node
    
    def chooseClass(self, class_name):
        """Instantiate a node based on the class name"""
        if class_name == "NodeGraphic":
            return NodeGraphic(self.scene, canvas=self)
        elif class_name == "DiffNode":
            return DiffNode(self.scene, canvas=self)
    
    def deleteNodeAndEdges(self, node):
        """used by right click context menu to delete the node and all edges connected to it
        When a node is deleted, we need to visit the input and output pins of the node
        to remove all of the edges connected to them"""
        inpin = node.inputPin()
        outpin = node.outputPin()
        for edge in inpin.edges() + outpin.edges():
            #we also need to visit the other node connected to the edge to remove the 
            # edge from its list of edges too
            edge_source = edge.sourceNode()
            self.removeEdgeFrom(edge_source, edge)
            
            edge_dest = edge.destNode()
            self.removeEdgeFrom(edge_dest, edge)

        self.removeNode(node)
        self.scene.removeItem(node)

    def deleteEdge(self, edge):
        """used by right click context menu to delete an edge"""
        source_node = edge.sourceNode()
        dest_node = edge.destNode()
        self.removeEdgeFrom(source_node, edge)
        self.removeEdgeFrom(dest_node, edge)
        self.scene.removeItem(edge)

    def removeEdgeFrom(self, node, edge):
        """removes the edge from input pin and output pin of the node"""
        node_edges = node.edges()#get the edges of the source node
        for pin_edge in node_edges:
            if pin_edge == edge:
                self.scene.removeItem(pin_edge)
                node.removeEdge(pin_edge)
                self.removeEdge(pin_edge)

    
    def copyNode(self, node):
        #TODO: implement copy node action
        #used by right click context menu to copy the node
        pass

    def clear(self):
        self.edges = []
        self.nodes = []

    def getNodeById(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        return None
    
class NodeCanvas(QGraphicsView, Graph):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setAcceptDrops(True)

        #the canvas has a context menu that allows the user to save the project
        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        #used in doubleClickEvent here and in PinGraph to track an unfinished 
        # self.connection = {"start": None, "end": None}
        # connection between two pins (one end of the edge is connected to a 
        # pin, but the other end is not)

        # node1 = NodeGraphic(canvas=self, node_number=1)
        # node1.setPos(0, 0)
        # self.scene.addItem(node1)
        # self.nodes.append(node1)

        # node2 = NodeGraphic(canvas=self, node_number=2)
        # node2.setPos(400, 0)
        # self.scene.addItem(node2)
        # self.nodes.append(node2)


    #override
    def dragEnterEvent(self, event):
        if event.mimeData().hasText:
            event.acceptProposedAction()
        else:
            event.ignore()

    #override
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    
    #override
    def dropEvent(self, event):
        print("NodeCanvas.dropEvent")
        if event.mimeData().hasText():
            node_class_name = event.mimeData().text()
            print("node_class_name:", node_class_name)

            if node_class_name == 'NodeGraphic':
                new_node = NodeGraphic(self.scene, canvas=self)
            
            elif node_class_name == 'DiffNode':
                new_node = DiffNode(self.scene, canvas=self)

            scene_pos = self.mapToScene(event.position().toPoint())
            new_node.setPos(scene_pos)
            print("graph scene", self.scene)
            self.scene.addItem(new_node)
            self.nodes.append(new_node)
            event.acceptProposedAction()
    
    #override
    def wheelEvent(self, event):
        zoom_factor = 1.25
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)
    
    #override
    def mouseDoubleClickEvent(self, event):
        #double click the canvas to cancel a connection
        if event.button() == Qt.MouseButton.LeftButton:
            if self.connection["start"] is not None and self.connection["end"] is None:
                print("NodeCanvas.mouseDoubleClickEvent: Dropping a connection")
                self.connection["start"] = None
        super().mousePressEvent(event)