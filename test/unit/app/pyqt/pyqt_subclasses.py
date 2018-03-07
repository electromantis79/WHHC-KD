#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 100%  Sphinx Approved = **True**

.. topic:: Overview

    This module holds any PyQt customized sub-class.

    :Created Date: 3/13/2015
    :Modified Date: 8/31/2016
    :Author: **Craig Gunter**

"""

from PyQt4.QtSvg import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class GraphicsScene(QGraphicsScene):
	def __init__(self, parent=None):
		super(GraphicsScene, self).__init__(parent)

class GraphicsView (QGraphicsView):
	def __init__ (self, parent = None):
		super (GraphicsView, self).__init__ (parent)

	def wheelEvent (self, event):
		'''Makes mouse wheel zoom in and out.'''
		#super (GraphicsView, self).wheelEvent(event)
		factor = 1.2

		if event.delta() < 0 :
			factor = 1.0 / factor
			self.scale(factor, factor)
		else:
			self.scale(factor, factor)


class GraphicsItemGroup (QGraphicsItemGroup):
	def __init__ (self, parent = None, scene=None):
		super (GraphicsItemGroup, self).__init__ (parent, scene)

	def wheelEvent (self, event):
		'''Makes mouse wheel zoom in and out.'''
		super (GraphicsItemGroup, self).wheelEvent(event)
		factor = 1.2
		if event.delta() < 0 :
				factor = 1.0 / factor
