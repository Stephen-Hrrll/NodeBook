from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from PySide6.QtGui import QBrush
from Edge import Edge

class PinGraphic(QGraphicsEllipseItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, scene,pin_type, graphWidget=None, parent=None):
        super().__init__(-5, -5, 15, 15, parent=parent)
        self.pin_type = pin_type
        self.edgeList = []
        self.newPos = QPointF()
        self.graph = graphWidget
        # print(f"PinGraphic: {self.pin_type} pin created")
        # print(f"PinGraphic: graphWidget: {graphWidget}")
        # print(f"PinGraphic: parent: {parent}")
        self.parent = parent
        self.scene = scene
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # enable itemChange() notifications for position and transformation changes
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        #  speed up rendering performance.
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setZValue(1)
        self.setBrush(QBrush(Qt.GlobalColor.red))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
       
    def mousePressEvent(self, event):
        """Clicking a pin will start a connection or finish making a connection if one is already started."""
        print(f"{self.pin_type} pin was clicked")
        start = self.graph.connection["start"]
        end = self.graph.connection["end"]
        if start is None:#I want to start a connection
            # print("Starting a connection")
            self.graph.connection["start"] = self
        elif end is None and start != self:#a connection is already started and I want to finish the connection
            # print("Finishing a connection")
            end = self
            # The Edge init function adds the edge to the source and destination pin
            # check the source and end pin to see if the edge already exists before 
            # making the Edge
            found = False
            for pin in [start, end]:
                for edge in pin.edgeList:
                    if (edge.sourceNode() == start and edge.destNode() == end) or \
                        (edge.sourceNode() == end and edge.destNode() == start):
                        print("Edge already exists")
                        found = True

            if not found:
                #if a user starts a connection on an input put, and then ends with a 
                #connection on an output pin, swap the direction of the connection. The 
                #wants to start a connection between these two nodes, but we need to ensure that it 
                #goes in the correct direction.
                if start.pin_type == "input" and end.pin_type == "output":
                    start, end = end, start
                elif (start.pin_type == "output" and end.pin_type == "output") or \
                    (start.pin_type == "input" and end.pin_type == "input"):
                    raise ValueError("Cannot connect two pins of the same type")
                
                edge = Edge(start, end, self.graph)
                self.scene.addItem(edge)
                # print("pin scene:", self.scene)
                self.graph.addEdge(edge)
            self.graph.connection = {"start": None, "end": None}

        super().mousePressEvent(event)    

    
    def addEdge(self, edge):
        for otr_edge in self.edgeList:
            # two edges are equal if they connect the same pins, regardless of the dircetion
            if (otr_edge.sourceNode() == edge.sourceNode() and otr_edge.destNode() == edge.destNode()) or \
                (otr_edge.sourceNode() == edge.destNode() and otr_edge.destNode() == edge.sourceNode()):
                print("Pin.addEdge: Edge already exists")
                return
            

        self.edgeList.append(edge)

    def edges(self):
        return self.edgeList

    def type(self):
        return PinGraphic.Type
    
    def advancePosition(self):
        # if the nodes postion changes, return True, else return False
        if self.newPos == self.pos():
            return False
        self.setPos(self.newPos)
        return True
    
    def adjust(self):
        # print(f"PinGraphic: Adjusting pin position for {self.pin_type} pin")
        for edge in self.edgeList:
            edge.adjust()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for edge in self.edgeList:
                edge.adjust()
        return super().itemChange(change, value)
    
    def removeEdge(self, edge):
        self.edgeList.remove(edge)
        

    
    