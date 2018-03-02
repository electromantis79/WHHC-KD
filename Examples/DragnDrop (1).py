#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

In this program, we can press on a button 
with a left mouse click or drag and drop the 
button with  the right mouse click. 

author: Jan Bodnar
website: zetcode.com
last edited: October 2013
"""

import sys
from PyQt4 import QtCore, QtGui
from Game import *
from Config import *
from GameDefaultSettings import *

class Button(QtGui.QPushButton):
  
    def __init__(self, title, parent, game):
        super(Button, self).__init__(title, parent)
        self.game=game

    def mouseMoveEvent(self, e):

        if e.buttons() != QtCore.Qt.RightButton:
            return

        mimeData = QtCore.QMimeData()

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        dropAction = drag.start(QtCore.Qt.MoveAction)

    def mousePressEvent(self, e):
      
        super(Button, self).mousePressEvent(e)
        
        if e.button() == QtCore.Qt.LeftButton:
            gameDict=self.game.__dict__
            printDict(gameDict)


class Example(QtGui.QWidget):
  
    def __init__(self, game):
        super(Example, self).__init__()
        self.game=game
        self.initUI()
        
    def initUI(self):

        self.setAcceptDrops(True)

        self.button = Button('Button', self, self.game)
        self.button.move(100, 65)

        self.setWindowTitle('Click or Move')
        self.setGeometry(300, 300, 280, 150)
        self.show()

    def dragEnterEvent(self, e):
      
        e.accept()

    def dropEvent(self, e):

        position = e.pos()     
        self.button.move(position)

        e.setDropAction(QtCore.Qt.MoveAction)
        e.accept()
        

def main():
    print "ON"
    c=Config(1)
    sport=c.config['sport']
    storedSportName=c.config['storedSportName']
    game = selectSportInstance(sport, storedSportName)
    app = QtGui.QApplication([])
    ex = Example(game)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
