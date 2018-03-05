#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 100%  Sphinx Approved = **True**

.. topic:: Overview

    This module creates a scrolling list from a given list of labels.

    :Date: 3/13/2015
    :Author: **Craig Gunter**

"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ListLayoutWidget(QWidget):
	#constructor
	def __init__(self, label, List, currentItem):
		super(ListLayoutWidget, self).__init__()
		FontBig=QFont('Ariel',15)
		FontSmall=QFont('Ariel',12)

		#create widget
		self.listWidget = ListWidget(List, currentItem)
		self.titleLabel = QLabel(label)
		self.titleLabel.setFont(FontBig)

		#create a layout for whole widget
		self.list_layout = QVBoxLayout()
		self.list_layout.addWidget(self.titleLabel)
		self.list_layout.addWidget(self.listWidget)

		#set layout for this widget
		self.setLayout(self.list_layout)

class ListWidget(QListWidget):
	'''This class creates a scrolling list from a given list of labels.'''

	#constructor
	def __init__(self, List, currentItem):
		super(ListWidget, self).__init__()
		#self.itemClicked.connect(self.item_click)

		for item_text in List:
			item = QListWidgetItem(item_text)
			self.addItem(item)
			if str(item.text())==currentItem:
				defaultItem=item
		self.setCurrentItem(defaultItem)


