#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 100%  Sphinx Approved = **True**

.. topic:: Overview

    This module creates the layout of the keypad.

    :Created Date: 3/16/2015
    :Modified Date: 10/12/2016
    :Author: **Craig Gunter**

"""

from functions import *
from pyqt_subclasses import * #Holds PyQt4 imports

class Keypad_Layout(object):
	'''This class creates the layout of the keypad.'''

	def __init__(self, board, model):
		self.scoreboard=board.scoreboard
		self.board=board
		self.keyMap=self.scoreboard.keyMap
		self.lcd=self.scoreboard.lcd
		self.genericKeys=self.keyMap.Keypad_Keys.keys()
		self.keyNames=self.keyMap.Keypad_Keys.values()
		self.buttonNamesDict = readMP_Keypad_Button_Names()
		self.height=87
		self.width=87

		#second layout
		self.lcdRow1_line_edit = QLineEdit()
		self.lcdRow2_line_edit = QLineEdit()

		self.lcdFont=QFont('LCDPHONE',20)
		self.lcdFont.setFixedPitch(True)

		self.modelFont=QFont('Arial',40)
		self.modelFont.setFixedPitch(True)

		self.buttonFont=QFont('Arial',11,QFont.Bold)
		self.buttonFont.setFixedPitch(True)

		self.outlineBlueColor='#3A54A4'
		self.standardRedColor='#8E191C'
		self.possRedColor='#BF202F'
		self.clockRedColor='#ED2024'
		self.standardGreenColor='#3CB64B'
		self.standardBlackColor='#050708'
		self.backgroundGrayColor='#E7E7E8'

		self.os='outline-style: solid;'
		self.ow='outline-width:4px;'
		self.oc='outline-color: '+self.outlineBlueColor+';'
		self.bs='border-style: solid;'
		self.bw='border-width:4px;'
		self.bc='border-color: '+self.outlineBlueColor+';'
		self.c='color: '+self.outlineBlueColor+';'
		self.bgc='background-color:'+self.backgroundGrayColor+''

		self.lcdRow1_line_edit.setFont(self.lcdFont)
		self.lcdRow2_line_edit.setFont(self.lcdFont)

		self.lcdRow1_line_edit.setFixedWidth(265)
		self.lcdRow2_line_edit.setFixedWidth(265)

		self.lcdRow1_line_edit.setLayoutDirection(Qt.RightToLeft)
		self.lcdRow2_line_edit.setLayoutDirection(Qt.RightToLeft)

		self.keypad_grid = QGridLayout()
		self.console_grid = QVBoxLayout()
		self.modelLabel=QLabel(model)
		self.modelLabel.setFont(self.modelFont)

		for x, key in enumerate(self.keyMap.Keypad_Keys):
			function=self.keyMap.Keypad_Keys[key]
			buttonText=self.buttonNamesDict[function]
			lines=buttonText.split('%')
			buttonTextFormated=QString()
			for y in range(len(lines)):
				if len(lines):
					buttonTextFormated.append(lines[y]+'\n')
			buttonTextFormated.chop(1)
			vars(self)[self.genericKeys[x]+'_button']=QPushButton(buttonTextFormated)
			if function=='periodClockOnOff':
				vars(self)[self.genericKeys[x]+'_button'].setStyleSheet(self.bs+self.bw+'border-color: '+self.clockRedColor+';'+'color:'+self.clockRedColor+';'+self.bgc)
			elif function[:8]=='handheld' or function=='None':
				vars(self)[self.genericKeys[x]+'_button'].setStyleSheet(self.bs+self.bw+'border-color: '+self.backgroundGrayColor+';'+'color:'+self.clockRedColor+';'+self.bgc)
			else:
				vars(self)[self.genericKeys[x]+'_button'].setStyleSheet(self.bs+self.bw+self.bc+self.c+self.bgc)
			vars(self)[self.genericKeys[x]+'_button'].setFixedHeight(self.height)
			vars(self)[self.genericKeys[x]+'_button'].setFixedWidth(self.width)
			vars(self)[self.genericKeys[x]+'_button'].setFont(self.buttonFont)

		self.letters=['B', 'C', 'D', 'E', 'F']
		self.numbers=['8', '7', '6', '5', '4', '3', '2', '1']
		for i in range(8):
			for j in range(5):
				self.keypad_grid.addWidget(vars(self)[self.letters[j]+self.numbers[i]+'_button'], j, i)

		if self.scoreboard.partsDict[model]['qtyOfCabinets']==2 and not(self.scoreboard.model=='LX2055' \
		or self.scoreboard.model=='LX2056'):
			self.sizeLabel=QLabel('     Width = '+str(self.scoreboard.boardWidth/12)+' Feet, Height = '+\
			str((self.board.face1Rect.size().height()+self.board.face2Rect.size().height())/12)+' Feet')
		elif self.scoreboard.model=='LX2555':
			self.sizeLabel=QLabel('     Width = 17.0 Feet, Height = 5.0 Feet')
		elif self.scoreboard.model=='LX2556':
			self.sizeLabel=QLabel('     Width = 18.0 Feet, Height = 6.0 Feet')
		elif self.scoreboard.model=='LX2575':
			self.sizeLabel=QLabel('     Width = 22.0 Feet, Height = 5.0 Feet')
		elif self.scoreboard.model=='LX2576':
			self.sizeLabel=QLabel('     Width = 23.0 Feet, Height = 6.0 Feet')
		else:
			self.sizeLabel=QLabel('     Width = '+str(self.scoreboard.boardWidth/12)+' Feet, Height = '+str(self.scoreboard.boardHeight/12)+' Feet')
		self.sizeLabel.setFont(self.buttonFont)

		self.console_grid.addWidget(self.modelLabel)
		self.console_grid.addWidget(self.sizeLabel)
		self.console_grid.addWidget(self.lcdRow1_line_edit, 0, Qt.AlignBottom)
		self.console_grid.addWidget(self.lcdRow2_line_edit)

		self.lcdRow1_line_edit.setText(self.lcd.row1)
		self.lcdRow2_line_edit.setText(self.lcd.row2)

		#add keypad to lcd
		self.console_grid.addLayout(self.keypad_grid)

	def updateNames(self, keyMap):
		'''
		PUBLIC METHOD

		Changes the text on all buttons to another keymap.
		'''
		for x, key in enumerate(keyMap):
			function=keyMap[key]
			buttonText=self.buttonNamesDict[function]
			lines=buttonText.split('%')
			buttonTextFormated=QString()
			for y in range(len(lines)):
				if len(lines):
					buttonTextFormated.append(lines[y]+'\n')
			buttonTextFormated.chop(1)
			vars(self)[self.genericKeys[x]+'_button'].setText(buttonTextFormated)
			if function=='periodClockOnOff':
				vars(self)[self.genericKeys[x]+'_button'].setStyleSheet(self.bs+self.bw+'border-color: '+self.clockRedColor+';'+'color:'+self.clockRedColor+';'+self.bgc)
			elif function[:8]=='handheld' or function=='None':
				vars(self)[self.genericKeys[x]+'_button'].setStyleSheet(self.bs+self.bw+'border-color: '+self.backgroundGrayColor+';'+'color:'+self.clockRedColor+';'+self.bgc)
			else:
				vars(self)[self.genericKeys[x]+'_button'].setStyleSheet(self.bs+self.bw+self.bc+self.c+self.bgc)
			vars(self)[self.genericKeys[x]+'_button'].setFixedHeight(self.height)
			vars(self)[self.genericKeys[x]+'_button'].setFixedWidth(self.width)
			vars(self)[self.genericKeys[x]+'_button'].setFont(self.buttonFont)
