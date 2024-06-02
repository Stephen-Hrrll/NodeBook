from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import Qt, QLineF, QPointF, QSizeF, QRectF
from PySide6.QtGui import QPolygonF
from ContextMenu import EdgeContextMenu
# from Node import Node
import math

class Edge(QGraphicsItem):
    # The Type attribute is used to distinguish between different types of items in the scene.
    Type = QGraphicsItem.UserType + 2

    def __init__(self, sourcePin, destPin, canvas):
        super().__init__()

        self.canvas = canvas       
        self.source = sourcePin
        self.dest = destPin
        
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()

    def sourceNode(self):
        return self.source

    def destNode(self):
        return self.dest

    def adjust(self):
        if not self.source or not self.dest:
            return
        
        line = QLineF(self.mapFromItem(self.source, 0, 0), self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        # tell Qt that the item is about to change, and that it should be redrawn.
        self.prepareGeometryChange()
        
        #make the tip of the edge touch the border of the node, not from center of the node to center
        if length > 20:
            edgeOffset = QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)
            self.sourcePoint = line.p1() + edgeOffset
            self.destPoint = line.p2() - edgeOffset
        else:
            self.sourcePoint = self.destPoint = line.p1()


    #override
    def type(self):
        return Edge.Type
    
    def boundingRect(self):
        if not self.source or not self.dest:
            return QRectF()

        penWidth = 1
        arrowSize = 20
        extra = (penWidth + arrowSize) / 2.0

        return QRectF(
            self.sourcePoint, 
            QSizeF(
                self.destPoint.x() - self.sourcePoint.x(), 
                self.destPoint.y() - self.sourcePoint.y()
                )).normalized().adjusted(-extra, -extra, extra, extra)
    
    #override
    def paint(self, painter, option, widget):

        if not self.source or not self.dest:
            return
        line = QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        # Draw the line itself
        painter.setPen(Qt.PenStyle.SolidLine)
        painter.setBrush(Qt.GlobalColor.black)
        painter.drawLine(line)

        # Draw the arrows
        arrowSize = 20
        angle = math.atan2(-line.dy(), line.dx())
        
        sourceArrowP1 = self.sourcePoint + QPointF(
            math.sin(angle + math.pi / 3) * arrowSize,
            math.cos(angle + math.pi / 3) * arrowSize
        )

        sourceArrowP2 = self.sourcePoint + QPointF(
            math.sin(angle + math.pi - math.pi / 3) * arrowSize,
            math.cos(angle + math.pi - math.pi / 3) * arrowSize
        )

        destArrowP1 = self.destPoint + QPointF(
            math.sin(angle - math.pi / 3) * arrowSize,
            math.cos(angle - math.pi / 3) * arrowSize
        )

        destArrowP2 = self.destPoint + QPointF(
            math.sin(angle - math.pi + math.pi / 3) * arrowSize,
            math.cos(angle - math.pi + math.pi / 3) * arrowSize
        )

        painter.setBrush(Qt.GlobalColor.black)
        painter.drawPolygon(QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
        painter.drawPolygon(QPolygonF([line.p2(), destArrowP1, destArrowP2]))

    def mousePressEvent(self, event):
        print("NodeGraphic.mousePressEvent")
        if event.button() == Qt.RightButton:
            print("Right click on edge")
            context_menu = EdgeContextMenu(canvas = self.canvas, edge = self)
            context_menu.exec(event.screenPos())
        else:
            super().mousePressEvent(event)

    def toDict(self):
        # print(f"Edge.to_dict: source: {self.source.parent.id}, dest: {self.dest.parent.id}")
        return {
            "source_node_id": self.source.parent.id,
            "dest_node_id": self.dest.parent.id
        }