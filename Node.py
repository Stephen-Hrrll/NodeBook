# from Pin import PinGraphic        
import ast, time, random, astor
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsProxyWidget, 
    QVBoxLayout, QPlainTextEdit, QWidget,
    QGraphicsSceneContextMenuEvent)

from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtCore import QRectF, Qt
from Pin import PinGraphic
from PygmentsHighlighter import PygmentsHighlighter
from ContextMenu import NodeContextMenu




# What is a node in the context of my program?
# A node is a container of other nodes

# Each node can parse the code it contains, and build the visual representation of the 
# code contained in the node

# each node will have a code editor and a run button

# each node will be able to switch between text and visual representation of the code

#different node types will be subclasses of the node class
# to start there will be a variable node, a function node, a class node

# each node will have a list of nodes that it contains

# each node will have a reference to the previous node and the next node, if they exist
#
class Node:
    """Base Node class. """
    def __init__(self, text="", code="", canvas=None, node_number=0):
        self.previous_node = None
        self.next_node = None 
        # TODO: self.nodes_within = []
        self.syntax_tree = None
        self.code = code
        self.canvas = canvas
        self.id = node_number
        self.text = text

    def setCode(self, code):
        self.code = code
    
    def getCode(self):
        return self.code
    
    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id
    
    def setPreviousNode(self, node):
        self.previous_node = node
    
    def getPreviousNode(self):
        return self.previous_node
    
    def setNextNode(self, node):
        self.next_node = node

    def getNextNode(self):
        return self.next_node
    
    def addNodeWithin(self, node):
        self.nodes.append(node)
    
    def removeNodeWithin(self, node):
        self.nodes.remove(node)

    def getNodesWithin(self):
        return self.nodes_within
    
    # def parseCode(self):
    #     self.syntax_tree = ast.parse(self.code)
    #     # make a node for variable, function, class, and add it to the nodes_within list
    #     for node in self.syntax_tree.body:
    #         print("node:", node)
    #         str_rep = astor.to_source(node).strip()
    #         self.nodes_within.append(Node(code=str_rep))


    def toDict(self):
        return {
            "id": self.id,
            "text": self.text,
            "code": self.code_editor.toPlainText(),
            "class_name": self.__class__.__name__,
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
        }
        # TODO:"nodes_within": [node.to_dict() for node in self.nodes_within],
    

class NodeGraphic(QGraphicsItem, Node):
    """Graphic representation of a node. """
    # # The Type attribute is used to distinguish between different types of items in the scene.
    Type = QGraphicsItem.UserType + 1
    def __init__(self, scene, text="", canvas=None):
        super().__init__()
        self.text = text
        self.canvas = canvas
        self.id = self.randomId()
        self.scene = scene
        print("NodeGraphic.__init__ node made")
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Create a container widget for the node
        self.container = QWidget()
  
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(0)

        # Add a code editor to the node
        self.code_editor = QPlainTextEdit()#TODO: make custom node for Syntax highlighting
        self.code_editor.setPlainText(self.text)
        self.code_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        # print("reading code from file")
        # # Load syntax.py into the editor for demo purposes
        # infile = open('D:\\Programming Projects\\node_programming\\syntax_experiments\\Syntax.py', 'r')
        # file_content = infile.read()
        # self.code_editor.setPlainText(file_content)
        # print("code read from file")
      
        self.layout.addWidget(self.code_editor)
        # Create a proxy widget to embed the container into the scene
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.container)
        # Add pins
        self._input_pin = self.createPin("input")
        self._output_pin = self.createPin("output")
        self.setPinPositions()
        # self.code_editor.show()
        # print("highlighting code")
        self.highlighter = PygmentsHighlighter(self.code_editor.document())
        # print("code highlighted")

    def randomId(self):
        """Generate a time based random id for the node"""
        return int(time.time() * 1000) + random.randint(1, 1000)

        
    def type(self):
        return NodeGraphic.Type
    
    def createPin(self, pin_type):
        pin = PinGraphic(self.scene, pin_type, graphWidget=self.canvas, parent=self)
        return pin

    def setPinPositions(self):
        # Vertically center the pins relative to the node
        node_height = self.proxy.boundingRect().height()
        input_pin_y = node_height / 2
        output_pin_y = node_height / 2

        # Set pin positions
        self._input_pin.setPos(-10, input_pin_y - 5)  # Left edge, vertically centered
        self._output_pin.setPos(self.proxy.boundingRect().width(), output_pin_y - 5)  # Right edge, vertically centered

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for pin in [self._input_pin, self._output_pin]:
                pin.adjust()
        return super().itemChange(change, value)

    def boundingRect(self):
        # Adjust the bounding rectangle to fit the contents including padding
        return QRectF(0, 0, self.proxy.boundingRect().width(), self.proxy.boundingRect().height())
    
    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawRect(self.boundingRect())

    def getInputPinPosition(self):
        return self.mapToScene(self._input_pin.pos())

    def getOutputPinPosition(self):
        return self.mapToScene(self._output_pin.pos())
    
    def inputPin(self):
        return self._input_pin
    
    def outputPin(self):
        return self._output_pin
        

    def mousePressEvent(self, event):
        print("NodeGraphic.mousePressEvent")
        if event.button() == Qt.RightButton:
            print("Right click on node")
            context_menu = NodeContextMenu(canvas = self.canvas, node = self)
            context_menu.exec(event.screenPos())
        else:
            super().mousePressEvent(event)
    

class DiffNode(NodeGraphic):
    """for testing purposes only."""
    def __init__(self, text="", canvas=None, node_number=0):
        super().__init__(text, canvas=canvas)
      

