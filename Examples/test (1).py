"""
import sys
from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

html = \
<html>
<head>
<title>Python Web Plugin Test</title>
</head>

<body>
<h1>Python Web Plugin Test</h1>
<object type="x-pyqt/widget" width="200" height="200"></object>
<p>This is a Web plugin written in Python.</p>
</body>
</html>
"""
'''
class WebWidget(QWidget):

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(Qt.white)
        painter.setPen(Qt.black)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.width()/4, self.height()/4,
                         self.width()/2, self.height()/2)
        painter.end()

    def sizeHint(self):
        return QSize(100, 100)

class WebPluginFactory(QWebPluginFactory):

    def __init__(self, parent = None):
        QWebPluginFactory.__init__(self, parent)

    def create(self, mimeType, url, names, values):
        if mimeType == "x-pyqt/widget":
            return WebWidget()

    def plugins(self):
        plugin = QWebPluginFactory.Plugin()
        plugin.name = "PyQt Widget"
        plugin.description = "An example Web plugin written with PyQt."
        mimeType = QWebPluginFactory.MimeType()
        mimeType.name = "x-pyqt/widget"
        mimeType.description = "PyQt widget"
        mimeType.fileExtensions = []
        plugin.mimeTypes = [mimeType]
        print "plugins"
        return [plugin]

if __name__ == "__main__":

    app = QApplication(sys.argv)
    QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
    view = QWebView()
    factory = WebPluginFactory()
    view.page().setPluginFactory(factory)
    view.setHtml(html)
    view.show()
    sys.exit(app.exec_())
'''
import sys
from PyQt4 import QtGui

class Node(QtGui.QGraphicsItem):
    def __init__(self, parent = None):
        QtGui.QGraphicsItem.__init__(self,parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

app = QtGui.QApplication(sys.argv)

scene = QtGui.QGraphicsScene()
scene.addText("test")

scene.addItem(Node())

view = QtGui.QGraphicsView(scene)
view.show()

sys.exit(app.exec_())
'''
import math

from PyQt4 import QtCore, QtGui

class Mouse(QtGui.QGraphicsItem):
    Pi = math.pi
    TwoPi = 2.0 * Pi

    # Create the bounding rectangle once.
    adjust = 0.5
    BoundingRect = QtCore.QRectF(-20 - adjust, -22 - adjust, 40 + adjust,
            83 + adjust)

    def __init__(self):
        super(Mouse, self).__init__()

        self.angle = 0.0
        self.speed = 0.0
        self.mouseEyeDirection = 0.0
        self.color = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,
                QtCore.qrand() % 256)

        self.rotate(QtCore.qrand() % (360 * 16))

        # In the C++ version of this example, this class is also derived from
        # QObject in order to receive timer events.  PyQt does not support
        # deriving from more than one wrapped class so we just create an
        # explicit timer instead.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(1000 / 33)

    @staticmethod
    def normalizeAngle(angle):
        while angle < 0:
            angle += Mouse.TwoPi
        while angle > Mouse.TwoPi:
            angle -= Mouse.TwoPi
        return angle

    def boundingRect(self):
        return Mouse.BoundingRect

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(-10, -20, 20, 40)
        return path;

    def paint(self, painter, option, widget):
        # Body.
        painter.setBrush(self.color)
        painter.drawEllipse(-10, -20, 20, 40)

        # Eyes.
        painter.setBrush(QtCore.Qt.white)
        painter.drawEllipse(-10, -17, 8, 8)
        painter.drawEllipse(2, -17, 8, 8)

        # Nose.
        painter.setBrush(QtCore.Qt.black)
        painter.drawEllipse(QtCore.QRectF(-2, -22, 4, 4))

        # Pupils.
        painter.drawEllipse(QtCore.QRectF(-8.0 + self.mouseEyeDirection, -17, 4, 4))
        painter.drawEllipse(QtCore.QRectF(4.0 + self.mouseEyeDirection, -17, 4, 4))

        # Ears.
        if self.scene().collidingItems(self):
            painter.setBrush(QtCore.Qt.red)
        else:
            painter.setBrush(QtCore.Qt.darkYellow)

        painter.drawEllipse(-17, -12, 16, 16)
        painter.drawEllipse(1, -12, 16, 16)

        # Tail.
        path = QtGui.QPainterPath(QtCore.QPointF(0, 20))
        path.cubicTo(-5, 22, -5, 22, 0, 25)
        path.cubicTo(5, 27, 5, 32, 0, 30)
        path.cubicTo(-5, 32, -5, 42, 0, 35)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(path)

    def timerEvent(self):
        # Don't move too far away.
        lineToCenter = QtCore.QLineF(QtCore.QPointF(0, 0), self.mapFromScene(0, 0))
        if lineToCenter.length() > 150:
            angleToCenter = math.acos(lineToCenter.dx() / lineToCenter.length())
            if lineToCenter.dy() < 0:
                angleToCenter = Mouse.TwoPi - angleToCenter;
            angleToCenter = Mouse.normalizeAngle((Mouse.Pi - angleToCenter) + Mouse.Pi / 2)

            if angleToCenter < Mouse.Pi and angleToCenter > Mouse.Pi / 4:
                # Rotate left.
                self.angle += [-0.25, 0.25][self.angle < -Mouse.Pi / 2]
            elif angleToCenter >= Mouse.Pi and angleToCenter < (Mouse.Pi + Mouse.Pi / 2 + Mouse.Pi / 4):
                # Rotate right.
                self.angle += [-0.25, 0.25][self.angle < Mouse.Pi / 2]
        elif math.sin(self.angle) < 0:
            self.angle += 0.25
        elif math.sin(self.angle) > 0:
            self.angle -= 0.25

        # Try not to crash with any other mice.
        dangerMice = self.scene().items(QtGui.QPolygonF([self.mapToScene(0, 0),
                                                         self.mapToScene(-30, -50),
                                                         self.mapToScene(30, -50)]))

        for item in dangerMice:
            if item is self:
                continue

            lineToMouse = QtCore.QLineF(QtCore.QPointF(0, 0), self.mapFromItem(item, 0, 0))
            angleToMouse = math.acos(lineToMouse.dx() / lineToMouse.length())
            if lineToMouse.dy() < 0:
                angleToMouse = Mouse.TwoPi - angleToMouse
            angleToMouse = Mouse.normalizeAngle((Mouse.Pi - angleToMouse) + Mouse.Pi / 2)

            if angleToMouse >= 0 and angleToMouse < Mouse.Pi / 2:
                # Rotate right.
                self.angle += 0.5
            elif angleToMouse <= Mouse.TwoPi and angleToMouse > (Mouse.TwoPi - Mouse.Pi / 2):
                # Rotate left.
                self.angle -= 0.5

        # Add some random movement.
        if len(dangerMice) > 1 and (QtCore.qrand() % 10) == 0:
            if QtCore.qrand() % 1:
                self.angle += (QtCore.qrand() % 100) / 500.0
            else:
                self.angle -= (QtCore.qrand() % 100) / 500.0

        self.speed += (-50 + QtCore.qrand() % 100) / 100.0

        dx = math.sin(self.angle) * 10
        self.mouseEyeDirection = [dx / 5, 0.0][QtCore.qAbs(dx / 5) < 1]

        self.rotate(dx)
        self.setPos(self.mapToParent(0, -(3 + math.sin(self.speed) * 3)))


if __name__ == '__main__':

    import sys

    MouseCount = 1

    app = QtGui.QApplication(sys.argv)
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))

    scene = QtGui.QGraphicsScene()
    scene.setSceneRect(-300, -300, 600, 600)
    scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

    for i in range(MouseCount):
        mouse = Mouse()
        mouse.scale(8,8)
        #mouse.setPos(math.sin((i * 6.28) / MouseCount) * 200,
                     #math.cos((i * 6.28) / MouseCount) * 200)
        scene.addItem(mouse)

    view = QtGui.QGraphicsView(scene)
    view.setRenderHint(QtGui.QPainter.Antialiasing)
    view.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap('Graphics/cheese.jpg')))
    view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
    view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
    view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
    #view.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
    #view.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
    view.setWindowTitle("Colliding Mice")
    #view.resize(400, 300)
    view.show()

    sys.exit(app.exec_())
'''
'''
import sys
import svgwrite
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class ImageLabel(QLabel):
    def __init__(self, image, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.setPixmap(image)

    def mousePressEvent(self, event):
        print 'I was pressed'


class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.create_main_frame()

    def create_main_frame(self):
        name_label = QLabel("Here's a clickable image:")
        img_label = ImageLabel(QPixmap('button.png'))

        vbox = QVBoxLayout()
        vbox.addWidget(name_label)
        vbox.addWidget(img_label)

        main_frame = QWidget()
        main_frame.setLayout(vbox)
        self.setCentralWidget(main_frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
'''
