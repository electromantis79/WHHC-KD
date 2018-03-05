#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 99%  Sphinx Approved = **True**

.. topic:: Overview

    This module draws a scoreboard and all of it's components with PyQt.

    :Created Date: 3/16/2015
    :Modified Date: 10/14/2016
    :Author: **Craig Gunter**

"""

import time

from functions import *
from pyqt_subclasses import * #Holds PyQt4 imports
import xml.etree.ElementTree as ET

class LED(QGraphicsItem):
	'''Graphical representation of an LED.'''
	ledOnSize18=.875
	ledOnSize30=1.0625
	ledOnSize11=.8125
	ledOnSize3=.6875
	ledOnSize12=.475
	ledOnSizeBP=.425
	ledOnSize16=.75
	ledOnSizeElseIndoor=.6
	ledOnSizeETN9x16Outdoor=.8
	ledOnSizeETN14x16TwoRow=.825
	ledOnSizeETN9x16Indoor=.525
	ledOnSizeETN14x16OneRow=.545
	ledOffSize=.25
	AMBER_LED="#FAA61A"
	RED_LED="#ED1C24"
	GREEN_LED="#A6CE39"
	OFF_LED="#434A4F"
	WHITE="#FFFFFF"

	def __init__ (self, LEDs_On=0, color='AMBER', scorelink=0, parent=None, pcbSize='18', pcbType='digit'):
		super(LED, self).__init__(parent)
		self.scorelink=scorelink
		if color=='WHITE' or scorelink:
			self.color=QColor(self.WHITE)
		elif color=='RED':
			self.color=QColor(self.RED_LED)
		elif color=='GREEN':
			self.color=QColor(self.GREEN_LED)
		elif color=='AMBER':
			self.color=QColor(self.AMBER_LED)
		self.ledSize=.1
		#print pcbType[-4:], pcbSize, pcbType, pcbType[:2]
		if LEDs_On:
			if pcbType[-4:]=='door':
				if pcbSize=='5':
					if pcbType[0]=='7':
						self.ledSize=self.ledOnSizeETN14x16TwoRow
					elif pcbType[0]=='9':
						self.ledSize=self.ledOnSizeETN9x16Indoor
				elif pcbSize=='7':
					if pcbType[:2]=='14':
						self.ledSize=self.ledOnSizeETN14x16OneRow
					elif pcbType[0]=='9':
						self.ledSize=self.ledOnSizeETN9x16Outdoor
			elif pcbSize=='18' or pcbSize=='15' or pcbSize=='4':
				self.ledSize=self.ledOnSize18
			elif pcbSize=='24' or pcbSize=='30' or pcbSize=='7' or pcbSize=='10':
				self.ledSize=self.ledOnSize30
			elif pcbSize=='11':
				self.ledSize=self.ledOnSize11
			elif (pcbSize=='12' or pcbSize=='9') and pcbType[:5]=='colon':
				self.ledSize=self.ledOnSize12
			elif pcbSize=='3' and (pcbType[:6]=='bonus_' or pcbType[:5]=='Bposs'):
				self.ledSize=self.ledOnSizeBP
			elif pcbSize=='3':
				self.ledSize=self.ledOnSize3
			elif pcbSize=='16' and not pcbType[:5]=='colon':
				self.ledSize=self.ledOnSize16
			else:
				self.ledSize=self.ledOnSizeElseIndoor
		else:
			self.color = QColor(self.OFF_LED)
			self.ledSize=self.ledOffSize
		#print self.ledSize


		self.centerAdjust=self.ledSize/2
		if self.scorelink:
			self.boundingRect = QRectF(-1, -1.875, 2, 3.75)
		else:
			self.boundingRect = QRectF(-self.centerAdjust, -self.centerAdjust, self.ledSize, self.ledSize)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the LED.'''
		painter.setBrush(self.color)
		painter.setPen(Qt.NoPen)
		if self.scorelink:
			painter.drawRoundedRect(self.boundingRect, .25, .25)
		else:
			painter.drawEllipse(QRectF(0-self.centerAdjust, 0-self.centerAdjust, self.ledSize, self.ledSize))#Origin

class PCB_Border(QGraphicsWidget):
	'''
	A border used to highlight a PCB.
	'''
	MEAN_1_V1="#FA0000"
	MEAN_1_V2="#FFFC4A"
	MEAN_1_V3="#4AFF4A"
	MEAN_2_V1="#57F0F2"
	MEAN_2_V2="#5064EB"
	MEAN_2_V3="#E82EC6"
	MEAN_3_V1="#807A7F"
	MEAN_3_V2="#FFCC00"
	MEAN_3_V3="#D4D4D4"
	WHITE="#FFFFFF"
	colorNameList=['MEAN_1_V1', 'MEAN_1_V2', 'MEAN_1_V3', 'MEAN_2_V1', 'MEAN_2_V2', 'MEAN_2_V3', 'MEAN_3_V1', 'MEAN_3_V2', 'MEAN_3_V3', 'WHITE']
	colorList=["#FA0000", "#FFFC4A", "#4AFF4A", "#57F0F2", "#5064EB", "#E82EC6", "#807A7F", "#FFCC00", "#D4D4D4", "#FFFFFF"]
	colorDict={}
	for x, name in enumerate(colorNameList):
		colorDict[name]=QColor(colorList[x])

	def __init__ (self, border, parent=None, color=9):
		super(PCB_Border, self).__init__(parent)
		self.boundingRect=border
		self.color=color

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the PCB border.'''
		color = self.colorDict[self.colorNameList[self.color]]
		if self.color==9:
			thickness=.2
		else:
			thickness=.3
		pen = QPen(color, thickness, Qt.SolidLine)
		painter.setPen(pen)
		painter.drawRect(self.boundingRect)

class PCB(QGraphicsItemGroup):
	'''
	Graphical representation of a PCB with only LEDs visible.
	'''
	def __init__ (self, pcbSize='18', pcbType='digit', pcbValue='', color='AMBER', parent=None, maskType=None):
		super(PCB, self).__init__(parent)
		self.pcbSize=pcbSize
		self.pcbType=pcbType
		self.pcbValue=pcbValue
		self.LED_ON_Color=color
		self.maskType=maskType
		self.pcbClicked=False
		self.setToolTip(self.pcbSize+' Inch '+self.pcbType+'\n'+self.pcbValue)
		self.segDict={}

		self.colorSelect()
		self.positionDict, self.segmentDict, self.specs = readLED_Positions(self.pcbSize, self.pcbType)
		self.addLEDs()

		self.boundingRect = QRectF(\
		self.specs['boundingX'], self.specs['boundingY'], \
		self.specs['boundingWidth'], -self.specs['boundingHeight'])
		self.border=PCB_Border(self.boundingRect, self)
		self.border.setVisible(False)

	def colorSelect(self):
		'''Selects the correct color for indoor digits.'''
		if self.maskType is not None:
			red=self.maskType=='9inClock' or self.maskType=='12inClock' or self.maskType=='16inClock' \
			or self.maskType[:7]=='5inPoss' or self.maskType[:7]=='3inPoss' or self.maskType=='9inTo9_red' \
			or self.maskType=='12inTo9_red' or self.maskType=='6inTo99_red' \
			or (self.maskType[:12]=='3inBonusPoss' and self.pcbType[:5]=='Bposs') \
			or (self.maskType=='LX2180' and self.pcbSize!='6') or self.maskType=='LX2160' or self.maskType=='LX7406'
			amber=self.maskType=='9inTo19' or self.maskType=='12inTo199' or self.maskType=='16inTo199' \
			or self.maskType=='9inTo199' or self.maskType=='12inTo19' or self.maskType=='6inTo99_amber' \
			or self.maskType=='9inTo99_amber'
			green=self.maskType=='12inTo99' or self.maskType[:8]=='3inBonus' or self.maskType=='9inTo9' \
			or self.maskType=='12inTo9' or self.maskType=='9inPenClock' or self.maskType[:11]=='5inDblBonus' \
			or self.maskType=='6inTo9' or self.maskType=='6inTo99_green' or self.maskType=='9inTo99_green' \
			or (self.maskType=='LX2180' and self.pcbType=='digit' and self.pcbSize=='6')
			if red:
				self.LED_ON_Color='RED'
			elif amber:
				self.LED_ON_Color='AMBER'
			elif green:
				self.LED_ON_Color='GREEN'

	def addLEDs(self):
		'''
		Creates a dictionary of the PCBs LEDs on and off.
		On LEDs are on top of off LEDs and always bigger.
		Toggling visibility of on LEDs gives the desired effect.
		'''
		for on in range(2):
			for y, segment in enumerate(self.segmentDict.keys()):
				self.ledsPerSegment=self.segmentDict[segment]
				for led in self.ledsPerSegment:
					if not on:
						ledName='off_'+str(led)
					else:
						ledName='on_'+str(led)
					ledName=ledName
					if self.pcbType=='scorelink':
						self.segDict[ledName]=LED(on, self.LED_ON_Color, scorelink=1, pcbSize=self.pcbSize, pcbType=self.pcbType)
					else:
						self.segDict[ledName]=LED(on, self.LED_ON_Color, scorelink=0, pcbSize=self.pcbSize, pcbType=self.pcbType)
					pos=self.positionDict[led]
					self.segDict[ledName].setPos(pos[0],pos[1])
					if on:
						self.segDict[ledName].setVisible(False)
					self.addToGroup(self.segDict[ledName])

	def addToMask(self, maskType='18inTo9', position=1, parent=None):
		'''
		PUBLIC METHOD

		Adds the PCB to a mask in the desired position.
		'''
		self.maskType=maskType
		self.partsDict, self.positionDict, self.maskWidth, self.maskHeight, self.maskRadius = readMaskParts(self.maskType)
		self.setPos(self.positionDict[str(position)][2],self.positionDict[str(position)][3])
		self.setParentItem(parent)

	def updateSegment(self, segment='A', SEG_On=1):
		'''
		PUBLIC METHOD

		Sets the visibility of all LEDs in the segment to the value of SEG_On.
		'''
		self.ledsPerSegment=self.segmentDict[segment]
		#print self.segmentDict[segment]
		for led in self.ledsPerSegment:
			self.segDict['on_'+str(led)].setVisible(SEG_On)

	def mousePressEvent(self, event):
		'''* **Toggles the PCB borders visibility when clicked.**'''
		self.pcbClicked=True
		self.border.setVisible(not self.border.isVisible())

class ETN_Panel(QGraphicsItemGroup):
	'''
	Graphical representation of an ETN panel with only the LEDs visible.
	'''
	def __init__ (self, pcbSize='5', pcbType='9x16Indoor', pcbValue='', color='AMBER', borderColor=8, parent=None, maskType=None):
		super(ETN_Panel, self).__init__(parent)
		self.pcbSize=pcbSize
		self.pcbType=pcbType
		self.pcbValue=pcbValue
		self.LED_ON_Color=color
		self.maskType=maskType
		self.borderColor=borderColor-1
		if self.pcbType[-4:]=='half':
			self.pcbType=self.pcbType[:-5]
			self.cut=True
		else:
			self.cut=False
		self.pcbClicked=False
		self.setToolTip(self.pcbSize+' Inch '+self.pcbType+'\n'+self.pcbValue)

		self.segDict={}
		self.positionDict, self.segmentDict, self.specs = readLED_Positions(self.pcbSize, self.pcbType)
		self.addLEDs()
		if self.cut:
			shift=0
			if self.pcbType[-6:]=='Indoor':
				shift=4.560
			elif self.pcbType[-7:]=='Outdoor':
				shift=6.798
			self.boundingRect = QRectF(\
			self.specs['boundingX']+shift, self.specs['boundingY'], \
			self.specs['boundingWidth']/2, -self.specs['boundingHeight'])
			self.translate(-shift, 0)
		else:
			self.boundingRect = QRectF(\
			self.specs['boundingX'], self.specs['boundingY'], \
			self.specs['boundingWidth'], -self.specs['boundingHeight'])
		self.border=PCB_Border(self.boundingRect, self, color=self.borderColor)
		self.border.setVisible(False)

	def addLEDs(self):
		'''
		Creates a dictionary of the ETN panels LEDs on and off.
		On LEDs are on top of off LEDs and always bigger.
		Toggling visibility of on LEDs gives the desired effect.
		'''
		for on in range(2):
			for y, segment in enumerate(self.segmentDict.keys()):
				if segment=='' and self.cut:
					self.ledsPerSegment=[]
				else:
					self.ledsPerSegment=self.segmentDict[segment]
				for led in self.ledsPerSegment:
					if not on:
						ledName='off_'+str(led)
					else:
						ledName='on_'+str(led)
					ledName=ledName
					self.segDict[ledName]=LED(on, self.LED_ON_Color, scorelink=0, pcbSize=self.pcbSize, pcbType=self.pcbType)
					pos=self.positionDict[led]
					self.segDict[ledName].setPos(pos[0],pos[1])
					if on:
						self.segDict[ledName].setVisible(False)
					self.addToGroup(self.segDict[ledName])

	def addToMask(self, maskType='18inTo9', position=1, parent=None):
		'''
		PUBLIC METHOD

		Adds the ETN panel to a mask in the desired position.
		'''
		self.maskType=maskType
		self.partsDict, self.positionDict, self.maskWidth, self.maskHeight, self.maskRadius = readMaskParts(self.maskType)
		self.setPos(self.positionDict[str(position)][2],self.positionDict[str(position)][3])
		self.setParentItem(parent)

	def updatePanel(self, matrix=[], blank=None, lamp=None):
		'''
		PUBLIC METHOD

		Sets the visibility of all LEDs in the segment to the values of matrix.
		'''
		if blank is None and lamp is None:
			pos=0
			for x,row in enumerate(matrix):
				for column in range(16):
					#print x, row, binar(row), column, binar(column), binar(row&(1<<column)), column+1+(x)*16, pos
					if row&(1<<column):
						SEG_On=True
					else:
						SEG_On=False
					pos=column+1+(x)*16
					if self.segDict.has_key('on_'+str(pos)):
						self.segDict['on_'+str(pos)].setVisible(SEG_On)
		else:
			if blank:
				for seg in self.segDict:
					self.segDict[seg].setVisible(False)
			if lamp:
				for seg in self.segDict:
					self.segDict[seg].setVisible(True)

	def mousePressEvent(self, event):
		'''* **Toggles the PCB borders visibility when clicked.**'''
		self.pcbClicked=True
		self.border.setVisible(not self.border.isVisible())

class Mask(QGraphicsItem):
	'''
	Graphical representation of a mask.
	'''
	def __init__ (self, maskType='24inTo9', scaleFactor=1, parent=None, boardColor=None):
		super(Mask, self).__init__(parent)
		self.maskType=maskType
		self.boardColor=boardColor
		self.partsDict, self.positionDict, self.maskWidth, self.maskHeight, self.maskRadius = readMaskParts(self.maskType)
		self.setAcceptHoverEvents(True)
		self.scale(scaleFactor,scaleFactor)
		self.boundingRect = QRectF(0, 0, self.maskWidth, self.maskHeight)
		if self.maskType=='3inBPossR':
			self.setRotation(180)
			self.translate(self.maskWidth, self.maskHeight)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the mask.'''
		painter.setBrush(QColor('#000000'))#NoBrush)#
		painter.setPen(Qt.NoPen)#black)#
		if self.maskType=='3inBonusPossL':
			painter.drawRoundedRect(QRectF(0, 0, 5.85, 9.5), self.maskRadius, self.maskRadius)
			painter.drawRoundedRect(QRectF(0, 4.1, 10.6, 5.4), self.maskRadius, self.maskRadius)
		elif self.maskType=='3inBonusPossR':
			painter.drawRoundedRect(QRectF(4.75, 0, 5.85, 9.5), self.maskRadius, self.maskRadius)
			painter.drawRoundedRect(QRectF(0, 4.1, 10.6, 5.4), self.maskRadius, self.maskRadius)
		elif self.maskType=='scorelink':
			painter.setBrush(QColor('#222222'))
			painter.drawRoundedRect(QRectF(0, 0, self.maskWidth, self.maskHeight), self.maskRadius, self.maskRadius)
		else:
			painter.drawRoundedRect(QRectF(0, 0, self.maskWidth, self.maskHeight), self.maskRadius, self.maskRadius)

	def addToBoard(self, model='LX1030', maskID='scorelink', parent=None):
		'''
		PUBLIC METHOD

		Adds the mask to a board in the desired position.
		'''
		self.model=model
		self.maskID=maskID
		self.partsDict, self.positionDict, self.heightDict, self.boardWidth, self.boardHeight = readMasksPerModel(self.model)
		self.setPos(self.positionDict[maskID][0],self.positionDict[maskID][1])
		self.setParentItem(parent)

	def mousePressEvent(self, event):
		'''* **Pushes the object down one layer on the graphics stack when clicked.**'''
		self.setZValue(self.zValue() - 1)

	def hoverEnterEvent(self, event):
		'''* **Changes the cursor to an arrow if cursor is over the object.**'''
		self.setCursor(QCursor(Qt.ArrowCursor))

class JUMPER(QGraphicsItem):
	'''
	Graphical representation of a labeled jumper.
	'''
	def __init__ (self, lxWidth=3.75, label='', highlight=0, parent=None):
		super(JUMPER, self).__init__(parent)
		self.lxWidth=lxWidth
		self.label=label
		self.highlight=highlight
		self.boundingRect = QRectF(0, 0, self.lxWidth/8, self.lxWidth/8)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the jumper.'''
		if self.highlight:
			painter.setBrush(QColor('#0000aa'))
			painter.setPen(QColor('#FFFFFF'))
		else:
			painter.setBrush(QColor('#00aa00'))
			painter.setPen(QColor('#FFFFFF'))
		font=QFont('Arial')
		font.setPointSizeF(1)
		painter.setFont(font)
		painter.drawRect(0, 0, self.lxWidth/8, self.lxWidth/8)#Origin
		painter.drawText(self.boundingRect, Qt.AlignCenter, self.label)

class HEADER(QGraphicsItem):
	'''
	Graphical representation of a labeled header.
	'''
	def __init__ (self, lxWidth=3.75, label='', highlight=0, parent=None):
		super(HEADER, self).__init__(parent)
		self.lxWidth=lxWidth
		self.label=label
		self.highlight=highlight
		self.boundingRect = QRectF(0, 0, self.lxWidth/4, self.lxWidth/4)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the header.'''
		if self.highlight:
			painter.setBrush(QColor('#FFFFFF'))
			painter.setPen(QColor('#000000'))
		else:
			painter.setBrush(QColor('#000000'))
			painter.setPen(QColor('#FFFFFF'))
		font=QFont('Tahoma')
		font.setPointSizeF(4)
		painter.setFont(font)
		painter.drawRect(0, 0, self.lxWidth/4, self.lxWidth/4)#Origin
		painter.drawText(self.boundingRect, Qt.AlignCenter, self.label)

class LX_Border(QGraphicsWidget):
	'''
	A border used to highlight an LX driver.
	'''
	def __init__ (self, border, parent=None):
		super(LX_Border, self).__init__(parent)
		self.boundingRect=border

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the LX border.'''
		pen = QPen(Qt.black, 2, Qt.SolidLine)
		painter.setPen(pen)
		painter.drawRect(self.boundingRect)

class LX_Label(QGraphicsWidget):
	'''
	A label used on an LX driver.
	'''
	def __init__ (self, label, border, parent=None):
		super(LX_Label, self).__init__(parent)
		self.label=label
		self.boundingRect=border
		self.lxWidth=self.boundingRect.width()
		self.lxHeight=self.boundingRect.height()

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the LX label.'''
		painter.setPen(QColor('#FFFFFF'))
		font=QFont('Arial')
		font.setPointSizeF(8)
		painter.setFont(font)
		name=QRectF(0, self.lxHeight*6/8, self.lxWidth, self.lxHeight/5)
		painter.drawText(name, Qt.AlignCenter, self.label)

class LX(QGraphicsWidget):
	'''
	Graphical representation of an LX driver.
	'''
	def __init__ (self, label='LX22', scaleFactor=1 , dataOrder='',parent=None):
		super(LX, self).__init__(parent)
		self.label=label
		self.dataOrder=dataOrder

		self.lxWidth=3.75*10
		self.lxHeight=5*10
		if label[:3]=='ETN':
			self.headerList=[('J10',1,5),('J11',1,3),('J14',5,5),('J15',5,3)]
			self.jumperList=[('H9',3.5,1),('H10',3.5,2),('H11',3.5,3),('H12',3.5,4),('H13',3.5,5),('H16',3.5,7)]
		else:
			self.headerList=[('J4',1.5,5),('J5',1.5,3),('J6',1.5,1),('J8',4.5,5),('J9',4.5,3),('J10',4.5,1)]
			self.jumperList=[('H13',.2,2),('H16',.2,3),('H14',.2,4),('H17',.2,5),('H15',.2,6),('H18',.2,7),('H2',3.5,4),('H4',3.5,5),('H12',3.5,6),('H3',.2,8.5),('H11',.2,9.5)]
		self.headerDict={}
		self.jumperDict={}
		self.headerClicked=(False,'')
		self.jumperClicked=(False,'')
		self.doubleClicked=(False,'')
		self.installEventFilter(self)
		self.addHeaders()
		self.addJumpers()

		self.boundingRect = QRectF(0, 0, self.lxWidth, self.lxHeight)

		self.border=LX_Border(self.boundingRect, self)
		self.border.setVisible(False)
		self.labelGraphic=LX_Label(self.label, self.boundingRect, self)
		self.scale(.1,.1)
		self.scale(scaleFactor,scaleFactor)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the LX driver.'''
		painter.setBrush(QColor('#00CC00'))
		painter.setPen(QColor('#FFFFFF'))
		painter.drawRect(0, 0, self.lxWidth, self.lxHeight)#Origin

		font=QFont('Arial')
		font.setPointSizeF(5)
		painter.setFont(font)
		painter.setPen(QColor('#ff0000'))
		dataOrder=QRectF(0, self.lxHeight*.1/8, self.lxWidth*7.6/8, self.lxHeight/8)
		painter.drawText(dataOrder, Qt.AlignRight, self.dataOrder)

	def addHeaders(self):
		'''
		Creates a dictionary of the headers on and off.
		On headers are on top of off LEDs.
		Toggling visibility of on headers inverts the colors.
		'''
		for x in [0,1]:
			for header in self.headerList:
				self.headerDict[header[0]+'_'+str(x)]=HEADER(self.lxWidth, header[0], x, self)
				self.headerDict[header[0]+'_'+str(x)].setPos(self.lxWidth*header[1]/8, self.lxWidth*header[2]/8)
				if x:
					self.headerDict[header[0]+'_'+str(x)].setVisible(False)

	def addJumpers(self):
		'''
		Creates a dictionary of the jumpers on and off.
		On jumpers are on top of off LEDs.
		Toggling visibility of on jumpers inverts the colors.
		'''
		for x in [0,1]:
			for jumper in self.jumperList:
				self.jumperDict[jumper[0]+'_'+str(x)]=JUMPER(self.lxWidth, jumper[0], x, self)
				self.jumperDict[jumper[0]+'_'+str(x)].setPos(self.lxWidth*jumper[1]/8, self.lxWidth*jumper[2]/8)
				if x:
					self.jumperDict[jumper[0]+'_'+str(x)].setVisible(False)

	def addToChassis(self, maskType='11inTo99', position=1, parent=None):
		'''
		PUBLIC METHOD

		Adds the LX driver to a chassis in the desired position.
		'''
		self.maskType=maskType
		if self.maskType=='18inTo199':
			self.maskType='18inTo99'
		self.partsDict, self.positionDict = readChassisParts(self.maskType)

		if maskType=='9inClock' or maskType=='12inClock':
			self.setPos(self.positionDict['LX_'+str(position)][0]+.5,self.positionDict['LX_'+str(position)][1]+1)
		elif maskType=='3_5_Indoor' or maskType=='3_Indoor' or maskType=='4_5_Indoor' or maskType=='9pix_END' or maskType=='14pix_END':
			if maskType=='9pix_END' or maskType=='14pix_END':
				self.setPos(1,1)
		else:
			self.setPos(self.positionDict['LX_'+str(position)][0]+.84,self.positionDict['LX_'+str(position)][1]-.59)

		self.setParentItem(parent)

	def mousePressEvent(self, event):
		'''* **Calling this method and doing nothing makes the LX driver clickable without the chassis moving below the mask.**'''
		pass

	def eventFilter(self, source, event):
		'''
		Handles all input events for the object.

		* **Toggles the visibility of the inverted color version of a jumper or header if the cursor is over it when clicked.**

		* **Do not toggle jumpers or headers if double clicked.**
		'''
		if event.type()==QEvent.GraphicsSceneMousePress:
			for header in self.headerList:
				if self.headerDict[header[0]+'_0'].contains(self.mapToItem(self.headerDict[header[0]+'_0'], event.pos())):
					self.headerDict[header[0]+'_1'].setVisible(not self.headerDict[header[0]+'_1'].isVisible())
					self.headerClicked=(True,header[0])
			for jumper in self.jumperList:
				if self.jumperDict[jumper[0]+'_0'].contains(self.mapToItem(self.jumperDict[jumper[0]+'_0'], event.pos())):
					self.jumperDict[jumper[0]+'_1'].setVisible(not self.jumperDict[jumper[0]+'_1'].isVisible())
					self.jumperClicked=(True,jumper[0])
		elif event.type()==QEvent.GraphicsSceneMouseDoubleClick:
			clean=True
			for header in self.headerList:
				if self.headerDict[header[0]+'_0'].contains(self.mapToItem(self.headerDict[header[0]+'_0'], event.pos())):
					clean=False
			for jumper in self.jumperList:
				if self.jumperDict[jumper[0]+'_0'].contains(self.mapToItem(self.jumperDict[jumper[0]+'_0'], event.pos())):
					clean=False
			if clean:
				self.doubleClicked=(True, self.label)

		return QWidget.eventFilter(self, source, event)

class PS_Invert(QGraphicsWidget):
	'''
	Graphical representation of a power supply with inverted colors.
	'''
	def __init__ (self, border, label='PS_1', parent=None):
		super(PS_Invert, self).__init__(parent)
		self.label=label
		self.boundingRect=border

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the power supply with inverted colors.'''
		painter.setBrush(QColor('#FFFFFF'))
		painter.setPen(QColor('#bbbbbb'))

		painter.drawRect(self.boundingRect)#Origin

		font=QFont('Arial')
		font.setPointSizeF(2)
		painter.setFont(font)
		name=QRectF(self.boundingRect)
		painter.drawText(name, Qt.AlignCenter, self.label)

class PS(QGraphicsWidget):
	'''
	Graphical representation of a power supply.
	'''
	def __init__ (self, label='1', scaleFactor=1, parent=None):
		super(PS, self).__init__(parent)
		self.label=label
		self.psWidth=8.5
		self.psHeight=4.5
		self.psClicked=(False,'')
		self.installEventFilter(self)


		self.boundingRect = QRectF(0, 0, self.psWidth, self.psHeight)
		self.scale(scaleFactor,scaleFactor)
		self.PS_I=PS_Invert(self.boundingRect, label=self.label, parent=self)
		self.PS_I.setVisible(False)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the power supply with inverted colors.'''
		painter.setBrush(QColor('#bbbbbb'))
		painter.setPen(QColor('#FFFFFF'))

		painter.drawRect(self.boundingRect)#Origin

		font=QFont('Arial')
		font.setPointSizeF(2)
		painter.setFont(font)
		name=QRectF(self.boundingRect)
		painter.drawText(name, Qt.AlignCenter, self.label)

	def addToChassis(self, maskType='11inTo99', position=1, parent=None):
		'''
		PUBLIC METHOD

		Adds the power supply to a chassis in the desired position.
		'''
		self.maskType=maskType
		if self.maskType=='18inTo199':
			self.maskType='18inTo99'
		self.partsDict, self.positionDict = readChassisParts(self.maskType)
		if maskType=='9inClock' or maskType=='12inClock':
			self.setPos(self.positionDict['PS_'+str(position)][0]+.5,self.positionDict['PS_'+str(position)][1]+.5)
		elif maskType=='3_5_Indoor' or maskType=='3_Indoor' or maskType=='4_5_Indoor' \
		or maskType=='9inPenClock' or maskType=='6inTo99_amber':
			self.setVisible(False)
		else:
			self.setPos(self.positionDict['PS_'+str(position)][0]+.84,self.positionDict['PS_'+str(position)][1]-.59)
		if maskType=='15inTo9':
			self.rotate(90)
		self.setParentItem(parent)

	def mousePressEvent(self, event):
		'''* **Calling this method and doing nothing makes the power supply clickable without the chassis moving below the mask.**'''
		pass

	def eventFilter(self, source, event):
		'''
		Handles all input events for the object.

		* **Toggles the visibility of the inverted color version of the power supply the cursor is over it when clicked.**
		'''
		if event.type()==QEvent.GraphicsSceneMousePress:
			self.PS_I.setVisible(not self.PS_I.isVisible())
			self.psClicked=(True, self.label)
		return QWidget.eventFilter(self, source, event)

class Chassis_Mark(QGraphicsItem):
	'''
	Graphical representation of the sticker used to identify a mask with a chissis behind it.
	'''
	def __init__ (self, border, parent=None):
		super(Chassis_Mark, self).__init__(parent)
		self.boundingRect=border

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the chassis mark.'''
		painter.setBrush(QColor('#cccccc'))
		painter.setPen(QColor('#888888'))

		rect=QRectF(\
		self.boundingRect.x()+self.boundingRect.width()-.5, \
		self.boundingRect.y()+self.boundingRect.height()+.2, \
		-self.boundingRect.width()/3, .1)
		painter.drawRect(rect)

class Chassis(QGraphicsItem):
	'''
	Graphical representation of a chassis.
	'''
	def __init__ (self, maskType='24inTo9', scaleFactor=1, parent=None):
		super(Chassis, self).__init__(parent)
		self.maskBorderSize=.84
		self.maskType=maskType
		self.partsDict, self.positionDict, self.maskWidth, self.maskHeight, self.maskRadius = readMaskParts(self.maskType)
		self.scale(scaleFactor,scaleFactor)
		self.boundingRect = QRectF(self.maskBorderSize, self.maskBorderSize, self.maskWidth-2*self.maskBorderSize, self.maskHeight-2*self.maskBorderSize)
		self.mark=Chassis_Mark(self.boundingRect, self)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the chassis.'''
		painter.setBrush(QColor('#CCCCCC'))#NoBrush)#
		painter.setPen(Qt.NoPen)#black)#
		painter.drawRect(self.boundingRect)
		if self.maskType=='30inTo9':
			painter.setPen(QColor('#000000'))#NoPen)#
			painter.drawLine(self.maskBorderSize, 13.5, self.maskWidth, 13.5)#Origin

	def addToBoard(self, model='LX1030', maskID='scorelink', parent=None):
		'''
		PUBLIC METHOD

		Adds the chassis to a board in the desired position.
		'''
		self.model=model
		self.maskID=maskID
		self.partsDict, self.positionDict, self.heightDict, self.boardWidth, self.boardHeight = readMasksPerModel(self.model)
		self.setPos(self.positionDict[maskID][0],self.positionDict[maskID][1])
		self.setParentItem(parent)

	def mousePressEvent(self, event):
		'''* **Pushes the object down one layer on the graphics stack when clicked.**'''
		self.setZValue(self.zValue() - 1)

class Board(QGraphicsItem):
	'''
	Graphical representation of a scoreboard.
	'''
	colorDict={}
	colorDict['HUNTER_GREEN']=QColor('#044840')
	colorDict['MATTE_BLACK']=QColor('#110f0e')
	colorDict['SILVER_GRAY']=QColor('#77797c')
	colorDict['WHITE']=QColor('#ffffff')
	colorDict['COMPANY_LOGO']=QColor('#ab2c29')
	colorDict['JOLLY_GREEN']=QColor('#01583f')
	colorDict['NAVY_BLUE']=QColor('#12264b')
	colorDict['EGYPTIAN_BLUE']=QColor('#273879')
	colorDict['ROYAL_BLUE']=QColor('#174994')
	colorDict['ICY_BLUE']=QColor('#3ca5d5')
	colorDict['SHAMROCK_GREEN']=QColor('#026d3b')
	colorDict['INDIGO_PURPLE']=QColor('#5f3781')
	colorDict['POWER_PURPLE']=QColor('#642558')
	colorDict['MERCHANT_MAROON']=QColor('#67091b')
	colorDict['CARDINAL_RED']=QColor('#9f1d20')
	colorDict['METALLIC_GOLD']=QColor('#97814e')
	colorDict['GOLDEN_YELLOW']=QColor('#faa819')
	colorDict['TIGER_ORANGE']=QColor('#f26922')
	colorDict['RACING_RED']=QColor('#b62025')

	def __init__ (self, scoreboard=None, LEDcolor='red', boardColor='COMPANY_LOGO', captionColor='WHITE', \
	stripeColor='WHITE', scaleFactor=1, driverType='LXDriver', parent=None, scene=None):
		super(Board, self).__init__(parent, scene)
		if scoreboard is not None:
			self.scoreboard=scoreboard
			self.model=self.scoreboard.model
			self.LEDcolor=LEDcolor
			self.vboseList=self.scoreboard.vboseList
			self.verbose=self.vboseList[0] #Method Name or arguments
			self.verboseMore=self.vboseList[1] #Deeper loop information in methods
			self.verboseMost=self.vboseList[2] #Crazy Deep Stuff
			verbose(['\nCreating Scoreboard Graphics object'], self.verbose)
			self.boardColorName=boardColor
			self.captionColorName=captionColor
			self.stripeColorName=stripeColor

			self.boardColor=self.colorDict[boardColor]
			self.captionColor=str(self.colorDict[captionColor].name())
			self.stripeColor=str(self.colorDict[stripeColor].name())

			self.scaleFactor=scaleFactor
			self.driverType=driverType
			self.boundingRect=QRectF(0, 0, 0, 0)
			self.partsDict, self.positionDict, self.heightDict, self.boardWidth, self.boardHeight = readMasksPerModel(self.model)
			self.scale(scaleFactor,scaleFactor)

			for cabinet in self.heightDict.keys():
				if cabinet=='1':
					self.face1Rect = QRectF(0, 0, self.boardWidth, self.heightDict['1'])
					self.boundingRect = self.face1Rect
				elif cabinet=='2':
					self.face2Rect = QRectF(0, self.heightDict['1']+.250*scaleFactor, self.boardWidth, self.heightDict['2'])
					self.boundingRect = QRectF(0, 0, self.boardWidth, self.heightDict['1']+.250*scaleFactor+self.heightDict['2'])
					if self.model=='LX2056' or self.model=='LX2055' or self.model=='LX2555' or self.model=='LX2556' or self.model=='LX2575' or self.model=='LX2576':
						self.face2Rect = QRectF(self.boardWidth+self.scoreboard.statWidth*scaleFactor, 0, self.boardWidth, self.heightDict['2'])
						self.boundingRect = QRectF(0, 0, self.boardWidth*2+self.scoreboard.statWidth*scaleFactor, self.heightDict['1'])

			#build dictionary with special case tags for models with multiple vinyl graphics
			self.graphicsDict={0:''}
			if self.model=='LX1320':
				self.graphicsDict.update({1:'f',2:'p'})
			elif self.model=='LX6324':
				self.graphicsDict.update({1:'f',2:'b'})
			elif self.model=='LX1360' or self.model=='LX1390' or self.model=='LX3450' \
			or self.model=='LX6434' or self.model=='LX6436' or self.model=='LX6544' \
			or self.model=='LX6546' or self.model=='LX6744' or self.model=='LX6746' \
			or self.model=='LX6944' or self.model=='LX6946':
				self.graphicsDict.update({1:'f'})
			elif self.model=='LX2545' or self.model=='LX2645' or \
			self.model=='LX2655' or self.model=='LX2665' or self.model=='LX2745':
				self.graphicsDict.update({1:'w'})

			if self.model=='LX2555' or self.model=='LX2556':
				model='LX2550'
			elif self.model=='LX2575' or self.model=='LX2576':
				model='LX2570'
			else:
				model=self.model

			#change colors of vinyl in all versions of this models svg files
			for graphic in range(len(self.graphicsDict)):
				tag=self.graphicsDict[graphic]
				graphicsFileName='Graphics/'+model+tag+'.svg'
				self.loadCaptionColor(graphicsFileName)
				self.loadStripeColor(graphicsFileName)

			#Load all vinyl to board and set the default visible only
			try:
				for graphic in range(len(self.graphicsDict)):
					tag=self.graphicsDict[graphic]
					graphicsFileName='Graphics/'+model+tag+'.svg'
					self.graphicsDict[graphic]=QGraphicsSvgItem(graphicsFileName, self)
					self.graphicsDict[graphic].setZValue(2)
					if graphic:
						self.graphicsDict[graphic].setVisible(False)
			except:
				print 'Error loading vinyl----------------'
				pass
			self.setZValue(-1)

			self.loadMaskAssemblies()
			self.loadBoard()
			printDict(self.__dict__)

	def boundingRect(self):
		'''Clickable area.'''
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		'''Draws the faces.'''
		painter.setBrush(self.boardColor)#NoBrush)#
		painter.setPen(QColor('#83909B'))#black)#
		painter.drawRoundedRect(self.face1Rect, 0, 0)
		try:
			painter.drawRoundedRect(self.face2Rect, 0, 0)
		except:
			pass

	def loadCaptionColor(self, graphicsFileName):
		'''Modifies the color of the captions of the models .svg files.'''
		try:
			captionTree=ET.parse(graphicsFileName)
			svg=captionTree.getroot()
			color=self.captionColor
			namespace='{http://www.w3.org/2000/svg}'
			for groupLevel_1 in svg:
				if groupLevel_1.attrib['id']=='Captions':
					for childLevel_1 in groupLevel_1:
						childLevel_1.attrib['fill']=color
						if childLevel_1.tag==namespace+'g':
							for groupLevel_2 in childLevel_1:
								groupLevel_2.attrib['fill']=color
								if groupLevel_2.tag==namespace+'g':
									for groupLevel_3 in groupLevel_2:
										groupLevel_3.attrib['fill']=color
			captionTree.write(graphicsFileName, encoding='utf-8', xml_declaration=True)
		except:
			print 'Error in loadCaptionColor method-------------'
			pass

	def loadStripeColor(self, graphicsFileName):
		'''Modifies the color of the stripe of the models .svg files.'''
		try:
			stripeTree=ET.parse(graphicsFileName)
			svg=stripeTree.getroot()
			color=self.stripeColor
			namespace='{http://www.w3.org/2000/svg}'
			for groupLevel_1 in svg:
				if groupLevel_1.attrib['id']=='Accent_Striping':
					for childLevel_1 in groupLevel_1:
						childLevel_1.attrib['fill']=color
						if childLevel_1.tag==namespace+'g':
							for groupLevel_2 in childLevel_1:
								groupLevel_2.attrib['fill']=color
								if groupLevel_2.tag==namespace+'g':
									for groupLevel_3 in groupLevel_2:
										groupLevel_3.attrib['fill']=color
			stripeTree.write(graphicsFileName, encoding='utf-8', xml_declaration=True)
		except:
			print 'Error in loadStripeColor method-------------'
			pass

	def loadMaskAssemblies(self):
		'''
		This method creates all of the graphic items for the scoreboard other than the board and vinyl.
		'''
		#Create empty dictionaries
		self.pcbGraphicItemDict={}
		self.maskGraphicItemDict={}
		self.lxGraphicItemDict={}
		self.psGraphicItemDict={}

		#Create all masks
		for maskID in self.scoreboard.maskID_List:
			verbose(['loading maskID',maskID], self.verboseMore)
			for function in self.scoreboard.functionDict.keys():
				if self.scoreboard.functionDict[function]['mask_ID']==maskID:
					maskType=self.scoreboard.functionDict[function]['maskType']
					LXDriver=self.scoreboard.functionDict[function]['LXDriver']
					self.maskGraphicItemDict[maskID]=Mask(maskType, boardColor=self.boardColor)
					self.maskGraphicItemDict[maskID].setZValue(1)

		#Create all chassis, power supply graphics, and LX graphics

		#Create chassis with power supply only for special case of stat panel
		if self.model=='LX2055' or self.model=='LX2056':
			if self.model=='LX2055':
				statMaskTeamOne='teamOnePlayerOne'
				statMaskTeamTwo='teamTwoPlayerOne'
			else:
				statMaskTeamOne='teamOnePlayerTwo'
				statMaskTeamTwo='teamTwoPlayerTwo'
			self.scoreboard.chassisDict[statMaskTeamOne]=Chassis('6inTo99_red')
			self.scoreboard.chassisDict[statMaskTeamOne].setZValue(1)
			self.mark=Chassis_Mark(self.scoreboard.chassisDict[statMaskTeamOne].boundingRect, self.maskGraphicItemDict[statMaskTeamOne])
			self.scoreboard.chassisDict[statMaskTeamTwo]=Chassis('6inTo99_red')
			self.scoreboard.chassisDict[statMaskTeamTwo].setZValue(1)
			self.mark=Chassis_Mark(self.scoreboard.chassisDict[statMaskTeamTwo].boundingRect, self.maskGraphicItemDict[statMaskTeamTwo])
			self.psGraphicItemDict['1']=PS(self.scoreboard.powerSupplyDict['1'][1][1])
			self.psGraphicItemDict['2']=PS(self.scoreboard.powerSupplyDict['2'][1][1])
			self.psGraphicItemDict['1'].addToChassis('6inTo99_red', 1, self.scoreboard.chassisDict[statMaskTeamOne])
			self.psGraphicItemDict['2'].addToChassis('6inTo99_red', 1, self.scoreboard.chassisDict[statMaskTeamTwo])

		#Create the rest of the chassis
		for chassis in self.scoreboard.chassisList:
			maskType=self.scoreboard.maskID_Dict[chassis]
			self.scoreboard.chassisDict[chassis]=Chassis(maskType)
			self.scoreboard.chassisDict[chassis].setZValue(1)
			self.mark=Chassis_Mark(self.scoreboard.chassisDict[chassis].boundingRect, self.maskGraphicItemDict[chassis])

			#Add lx graphics to chassis
			for driver in self.scoreboard.lxPerChassisDict[chassis]:
				self.lxGraphicItemDict[driver]=LX(driver, dataOrder=self.scoreboard.lxDataOrderDict[driver])
				self.lxGraphicItemDict[driver].addToChassis(maskType, int(self.scoreboard.driverPosDict[driver]), self.scoreboard.chassisDict[chassis])
				for jumper in self.scoreboard.lxDict[driver].jumpers:
					if self.scoreboard.lxDict[driver].jumperDict[jumper]:
						self.lxGraphicItemDict[driver].jumperDict[jumper+'_1'].setVisible(True)

			#Add power supply graphics to chassis
			for supply in self.scoreboard.powerSupplyList:
				if self.model=='LX2055' or self.model=='LX2056':
						pass
				elif self.scoreboard.psChassisDict[supply]==chassis:
					self.psGraphicItemDict[supply]=PS(self.scoreboard.powerSupplyDict[supply][1][1])
					if self.model=='LX7860':
						self.psGraphicItemDict[supply].addToChassis(maskType, int(self.scoreboard.powerSupplyDict[supply][1][0]), self.scoreboard.chassisDict['teamTwoPlayerTwoPenaltySeconds'])
					else:
						self.psGraphicItemDict[supply].addToChassis(maskType, int(self.scoreboard.powerSupplyDict[supply][1][0]), self.scoreboard.chassisDict[chassis])

		#Create all PCBs via their function in the board
		for function in self.scoreboard.functionDict.keys():
			maskType=self.scoreboard.functionDict[function]['maskType']
			maskID=self.scoreboard.functionDict[function]['mask_ID']
			pcbSize=self.scoreboard.functionDict[function]['pcbSize']
			pcbType=self.scoreboard.functionDict[function]['pcbType']
			borderColor=int(self.scoreboard.functionDict[function]['psWires'])
			pcbValue=function
			positionRtoL=self.scoreboard.functionDict[function]['positionRtoL']
			verbose(['function', function, 'pcbSize', pcbSize, 'pcbType', pcbType], self.verboseMore)
			#print pcbSize, pcbType, self.LEDcolor, maskType, function, function[-3:]
			if function[-3:]=='ETN':
				self.pcbGraphicItemDict[function]=ETN_Panel(pcbSize, pcbType, pcbValue, self.LEDcolor, maskType=maskType, borderColor=borderColor)
				self.pcbGraphicItemDict[function].addToMask(maskType, positionRtoL, self.maskGraphicItemDict[maskID])
			else:
				self.pcbGraphicItemDict[function]=PCB(pcbSize, pcbType, pcbValue, self.LEDcolor, maskType=maskType)
				self.pcbGraphicItemDict[function].addToMask(maskType, positionRtoL, self.maskGraphicItemDict[maskID])

	def Reset(self):
		self.scoreboard.boardReset()
		self.setZValue(-1)
		self.loadMaskAssemblies()
		self.loadBoard()
		printDict(self.__dict__)

	def loadBoard(self):
		'''
		Create scoreboard face, stripes, and captions, then attach the masks to the board.
		'''
		#Attach all masks to the board at the correct position
		for maskID in self.scoreboard.positionDict.keys():
			positionTopToBot=int(self.scoreboard.positionDict[maskID][2])
			if positionTopToBot==1:
				if self.scoreboard.chassisDict.has_key(maskID):
					self.scoreboard.chassisDict[maskID].addToBoard(self.model, maskID, self)
				if self.maskGraphicItemDict.has_key(maskID):
					self.maskGraphicItemDict[maskID].addToBoard(self.model, maskID, self)
			elif positionTopToBot==2:
				if self.scoreboard.chassisDict.has_key(maskID):
					self.scoreboard.chassisDict[maskID].addToBoard(self.model, maskID, self)
					if self.model=='LX2056' or self.model=='LX2055' or self.model=='LX2555' or self.model=='LX2556' or self.model=='LX2575' or self.model=='LX2576':
						self.scoreboard.chassisDict[maskID].translate(self.boardWidth+self.scoreboard.statWidth*self.scaleFactor,0)
					else:
						self.scoreboard.chassisDict[maskID].translate(0,self.heightDict['1']+.250*self.scaleFactor)
				if self.maskGraphicItemDict.has_key(maskID):
					self.maskGraphicItemDict[maskID].addToBoard(self.model, maskID, self)
					if self.model=='LX2056' or self.model=='LX2055' or self.model=='LX2555' or self.model=='LX2556' or self.model=='LX2575' or self.model=='LX2576':
						self.maskGraphicItemDict[maskID].translate(self.boardWidth+self.scoreboard.statWidth*self.scaleFactor,0)
					else:
						self.maskGraphicItemDict[maskID].translate(0,self.heightDict['1']+.250*self.scaleFactor)

	def data2GraphicDrivers(self):
		'''Updates graphics of the scoreboard with the scoreboard.functionList.'''
		#Update the LEDs of each pcb in the pcbGraphicItemDict dictionary based on their function
		#MAKE ONLY ON CHANGE
		tic=time.time()
		for function in self.scoreboard.functionList:
			verbose(['function', function], self.verboseMore)
			LXDriver=self.scoreboard.functionDict[function]['LXDriver']
			LXHeader=self.scoreboard.functionDict[function]['LXHeader']
			if function[-3:]=='ETN':
				try:
					panelNumber=int(function[7])
				except:
					print 'ERROR in panelNumber=int(function[7])', 'function', function
				#ETN updatePanel call, send each pcb in ETN mask in order from left to right
				if self.scoreboard.game.gameSettings['blankTestFlag']:
					self.pcbGraphicItemDict[function].updatePanel(blank=True)
				elif self.scoreboard.game.gameSettings['lampTestFlag']:
					self.pcbGraphicItemDict[function].updatePanel(lamp=True)
				else:
					self.pcbGraphicItemDict[function].updatePanel(self.scoreboard.lxDict[LXDriver].displayHeaderDict[LXHeader][panelNumber])
			else:
				if self.scoreboard.lxDict[LXDriver].outputDict.has_key(LXHeader):
					for segment in list(self.scoreboard.lxDict[LXDriver].segments):
						if self.scoreboard.lxDict[LXDriver].outputDict[LXHeader][segment]:
							#print 'Turn on LEDs in Graphical segment '+segment+'.'
							self.pcbGraphicItemDict[function].updateSegment(segment, 1)
						else:
							#print 'Turn Off LEDs in Graphical segment '+segment+'.'
							self.pcbGraphicItemDict[function].updateSegment(segment, 0)
			#
		toc=time.time()
		#print 'data2GraphicDrivers Time =',(toc-tic)*1000 #milliseconds

	def showDefaultJumpers(self):
		'''
		PUBLIC METHOD

		Resets the default jumpers of LX driver graphics of the scoreboard.
		'''
		for chassis in self.scoreboard.chassisList:
			for driver in self.scoreboard.lxPerChassisDict[chassis]:
				for jumper in self.scoreboard.lxDict[driver].jumpers:
					if self.scoreboard.lxDict[driver].jumperDict[jumper]:
						self.lxGraphicItemDict[driver].jumperDict[jumper+'_1'].setVisible(True)
					else:
						self.lxGraphicItemDict[driver].jumperDict[jumper+'_1'].setVisible(False)

	def wheelEvent (self, event):
		'''* **Enables zooming when mouse is inside bounding rectangle.**'''
		super (Board, self).wheelEvent(event)
		factor = 1.2
		if event.delta() < 0 :
			factor = 1.0 / factor
		self.scale(factor, factor)

def test():
	'''Test function if module ran independently.'''
	'''
	print "ON"
	DigitCount = 1
	lx=ETN_Driver('ETN8', [])#'H16''H13', 'H14', 'H17'
	mp=MP_Data_Handler()
	word=1
	wordStr='word'+str(word)
	LHword0 = mp.Encode(2, 3, word, 1, 0, 0, 0, 0, 0)
	sendList=[LHword0]

	group, bank, word, I_Bit, numericData = mp.Decode(sendList[0])
	#lx.addrDecode(group, bank, word, I_Bit, numericData)
	'''

	print "ON"
	sport='MPSOCCER_LX1-soccer'
	c=Config()
	configDict=readConfig()
	c.writeSport(sport)
	c.writeSERVER(True)
	model= Scoreboard(modelName='LX6630', driverType='LXDriver', serialInputFlag=0, checkEventsFlag=True)

	app = QApplication(sys.argv)
	scene = GraphicsScene()
	view = GraphicsView(scene)

	board=Board(model, LEDcolor='AMBER', boardColor='COMPANY_LOGO', captionColor='WHITE', stripeColor='WHITE', \
	driverType='LXDriver', scaleFactor=.3, parent=None, scene=scene)
	board.data2GraphicDrivers()
	#print model.game.getTeamData(model.game.home, 'possession')
	width = 500
	height = 300
	scene.setSceneRect(0, 0, width, height)
	'''
	#scene.setItemIndexMethod(QGraphicsScene.NoIndex)
	maskType='9pix_END_flip'
	mask=Mask(maskType)
	mask.setPos(5,5)
	pcb=ETN_Panel('7', '9x16Outdoor')
	scene.addItem(mask)
	pcb.addToMask(maskType, 1, mask)
	#pcb.updateSegment('A', 1)

	#pcb2=ETN_Panel('5', '7x16Outdoor')
	#pcb2.addToMask(maskType, 2, mask)

	#pcb3=ETN_Panel('7', '9x16Outdoor')
	#pcb3.addToMask(maskType, 4, mask)

	#pcb4=ETN_Panel('5', '9x16Indoor_half')
	#pcb4.addToMask(maskType, 4, mask)

	K=[0,0,2016,8184,12300,28134,61431,60471,60471,60471,60471,32759,7654,49164,32760,8160]
	K=fontTrim(K,False,14)
	#print fontWidth(K)

	#pcb2.updatePanel(K[:8])
	#pcb.updatePanel(K[7:])

	pcb5=PCB('16', 'digit')
	pcb5.addToMask(maskType, 5, mask)



	chassis=Chassis(maskType)
	#chassis.setPos(5,5)
	scene.addItem(chassis)
	lx=LX(dataOrder='8')
	lx.addToChassis(maskType,1,chassis)

	ps=PS()
	ps.addToChassis(maskType,1,chassis)
	ps2=PS('1')
	ps2.addToChassis(maskType,1,chassis)

	#ps.PS_I.setVisible(True)

	#scene.addItem(lx)
	#scene.addItem(lx.headerDict['J6_1'])
	lx.headerDict['J6_1'].setVisible(False)
	#segDon.setZValue(1)
	#printDict(mask.__dict__)
	'''
	#led=LED(LEDs_On=0, color='amber', scorelink=0, parent=None, pcbSize='18', pcbType='digit')
	#printDict(led.__dict__)
	view.setRenderHint(QPainter.Antialiasing)
	#view.setBackgroundBrush(QBrush(QPixmap('Graphics/cheese.jpg')))
	#view.setCacheMode(QGraphicsView.CacheBackground)
	#view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)

	#view.setDragMode(QGraphicsView.ScrollHandDrag)
	#view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
	#view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
	view.setWindowTitle("Digit")
	view.resize(width+300, height+300)
	view.scale(20,20)
	view.show()
	printDictsExpanded(model, 1)
	#raw_input()
	#lx.border.setVisible(True)
	#raw_input()
	#lx.headerDict['J6_1'].setVisible(False)
	'''
	#cycle through segments
	for digit in mask.positionRtoL_List:
		for seg in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
			pcb.updateSegment(seg, 1)
			raw_input()
			pcb.updateSegment(seg, 0)
	for digit in mask.positionRtoL_List:
		for seg in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
			pcb2.updateSegment(seg, 1)
			raw_input()
			pcb2.updateSegment(seg, 0)
	for digit in mask.positionRtoL_List:
		for seg in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
			pcb3.updateSegment(seg, 1)
			raw_input()
			pcb3.updateSegment(seg, 0)
	'''
	sys.exit(app.exec_())

if __name__ == '__main__':
	import sys
	from MP_Data_Handler import MP_Data_Handler
	from Config import Config
	from Driver import LX_Driver, ETN_Driver
	from Scoreboard import Scoreboard
	test()
