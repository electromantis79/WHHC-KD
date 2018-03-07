#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 100%  Sphinx Approved = **True**

.. topic:: Overview

    This module creates a group of radio buttons from a given list of labels.

    :Created Date: 3/13/2015
    :Modified Date: 8/31/2016
    :Author: **Craig Gunter**

"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class RadioButtonWidget(QWidget):
	'''This class creates a group of radio buttons from a given list of labels.'''

	#constructor
	def __init__(self, label, instruction, buttonList, defaultChecked=0):
		super(RadioButtonWidget, self).__init__()
		radioFontBig=QFont('Ariel',15)
		radioFontSmall=QFont('Ariel',12)
		buttonListLength=len(buttonList)

		#create widget
		self.titleLabel = QLabel(label)
		self.titleLabel.setFont(radioFontBig)
		self.radioGroupBox = QGroupBox(instruction)
		self.radioGroupBox.setFont(radioFontSmall)
		self.radioButtonGroup = QButtonGroup()

		#create the radio buttons
		self.radioButtonList = []
		for each in buttonList:
			self.radioButtonList.append(QRadioButton(each))

		#set the default checked item
		self.radioButtonList[defaultChecked].setChecked(True)

		#create layout for radio buttons and add them
		self.radio_button_layout = QVBoxLayout()

		#add buttons to the layout and button group
		for counter, each in enumerate(self.radioButtonList):
			self.radio_button_layout.addWidget(each, 0, Qt.AlignTop)
			self.radioButtonGroup.addButton(each)
			self.radioButtonGroup.setId(each, counter)

		#add radio buttons to the group box
		self.radioGroupBox.setLayout(self.radio_button_layout)

		#create a layout for whole widget
		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(self.titleLabel)
		self.main_layout.addWidget(self.radioGroupBox)

		#set layout for this widget
		self.setLayout(self.main_layout)

	def selected_button(self):
		'''Method to find out the selected button's ID.'''
		return self.radioButtonGroup.checkedId()
