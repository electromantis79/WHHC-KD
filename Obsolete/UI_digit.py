#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

from functions import *
from pyqt_subclasses import * #Holds PyQt4 imports

class LED(QGraphicsItem):

	ledOnSize18=.875
	ledOnSize30=1.0625
	ledOnSize11=.8125
	ledOnSize3=.6875
	ledOnSize12=.475
	ledOnSizeBP=.425
	ledOnSize16=.75
	ledOnSizeElseIndoor=.6
	ledOnSizeETN7=.8
	ledOnSizeETN11=.825
	ledOnSizeETN5=.525
	ledOnSizeETN8=.545
	ledOffSize=.25
	AMBER_LED="#FAA61A"
	RED_LED="#ED1C24"
	GREEN_LED="#A6CE39"
	OFF_LED="#434A4F"
	WHITE="#FFFFFF"

	def __init__ (self, LEDs_On=0, color='amber', scorelink=0, parent=None, pcbSize='18', pcbType='digit'):
		super(LED, self).__init__(parent)
		self.scorelink=scorelink
		if color=='white' or scorelink:
			self.color=QColor(self.WHITE)
		elif color=='red':
			self.color=QColor(self.RED_LED)
		elif color=='green':
			self.color=QColor(self.GREEN_LED)
		elif color=='amber':
			self.color=QColor(self.AMBER_LED)
		if LEDs_On:
			if pcbSize=='18' or pcbSize=='15' or pcbSize=='4':
				self.ledSize=self.ledOnSize18
			elif pcbSize=='24' or pcbSize=='30' or pcbSize=='7' or pcbSize=='10':
				self.ledSize=self.ledOnSize30
			elif pcbSize=='11':
				self.ledSize=self.ledOnSize11
			elif (pcbSize=='12' or pcbSize=='9') and pcbType[:5]=='colon':
				self.ledSize=self.ledOnSize12
			elif pcbSize=='3' and (pcbType[:5]=='bonus' or pcbType[:5]=='Bposs'):
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


		self.centerAdjust=self.ledSize/2
		if self.scorelink:
			self.boundingRect = QRectF(-1, -1.875, 2, 3.75)
		else:
			self.boundingRect = QRectF(-self.centerAdjust, -self.centerAdjust, self.ledSize, self.ledSize)

	def boundingRect(self):
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		painter.setBrush(self.color)
		painter.setPen(Qt.NoPen)
		if self.scorelink:
			painter.drawRoundedRect(self.boundingRect, .25, .25)
		else:
			painter.drawEllipse(QRectF(0-self.centerAdjust, 0-self.centerAdjust, self.ledSize, self.ledSize))#Origin

class PCB(QGraphicsItemGroup):
	def __init__ (self, pcbSize='18', pcbType='digit', color='amber', parent=None, maskType=None):
		super(PCB, self).__init__(parent)
		self.pcbSize=pcbSize
		self.pcbType=pcbType
		self.LED_ON_Color=color
		self.maskType=maskType
		self.colorSelect()
		self.segDict={}
		self.readLED_Positions()
		self.addLEDs()
		self.boundingRect = QRectF(\
		self.specs['boundingX'], self.specs['boundingY'], \
		self.specs['boundingWidth'], self.specs['boundingHeight'])

	def boundingRect(self):
		return self.boundingRect

	def colorSelect(self):
		if self.maskType is not None:
			red=self.maskType=='9inClock' or self.maskType=='12inClock' or self.maskType=='16inClock' \
			or self.maskType[:7]=='5inPoss' or self.maskType[:7]=='3inPoss' or self.maskType=='9inTo9_red' \
			or self.maskType=='12inTo9_red' or self.maskType=='6inTo99_red'
			amber=self.maskType=='9inTo19' or self.maskType=='12inTo199' or self.maskType=='16inTo199' \
			or self.maskType=='9inTo199' or self.maskType=='12inTo19' or self.maskType=='6inTo99_amber' \
			or self.maskType=='9inTo99_amber'
			green=self.maskType=='12inTo99' or self.maskType[:8]=='3inBonus' or self.maskType=='9inTo9' \
			or self.maskType=='12inTo9' or self.maskType=='9inPenClock' or self.maskType[:11]=='5inDblBonus' \
			or self.maskType=='6inTo9' or self.maskType=='6inTo99_green' or self.maskType=='9inTo99'
			if red:
				self.LED_ON_Color='red'
			elif amber:
				self.LED_ON_Color='amber'
			elif green:
				self.LED_ON_Color='green'

	def addLEDs(self):
		for on in range(2):
			for y, segment in enumerate(self.segmentList):
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
		self.maskType=maskType
		self.readMaskParts()
		self.setPos(self.positionDict[str(position)][2],self.positionDict[str(position)][3])
		self.setParentItem(parent)

	def readLED_Positions(self):
		LED_Positions='Spreadsheets/LED_Positions.csv'
		csvReader=csv.DictReader(open(LED_Positions, 'rb'), delimiter=',', quotechar="'")
		self.positionDict={}
		from collections import defaultdict
		self.segmentDict=defaultdict(list)
		segments={}
		self.specs={}
		for count, row in enumerate(csvReader):
			try:
				pcbSize=row['pcbSize']
				pcbType=row['pcbType']
				if pcbSize=='':
					pass
				elif pcbSize==self.pcbSize:
					if pcbType==self.pcbType:
						designator=int(row['RefDes'])
						segment=row['segment']
						segments[segment]=0
						x=float(row['X'])/1000
						y=float(row['Y'])/-1000
						boundingX=float(row['boundingX'])/1000
						boundingY=float(row['boundingY'])/-1000
						boundingWidth=float(row['boundingWidth'])/1000
						boundingHeight=float(row['boundingHeight'])/-1000
						self.specs['boundingX']=boundingX
						self.specs['boundingY']=boundingY
						self.specs['boundingWidth']=boundingWidth
						self.specs['boundingHeight']=boundingHeight
						coord=(x,y)
						self.segmentDict[segment].append(designator)
						self.positionDict[designator]=coord
						#print self.positionDict, self.segmentDict
						if row['']=='':
							del row['']#This requires spreadsheet to have a note in a column with no row 1 value
						#raw_input()
			except ValueError:
				pass
		self.segmentList=segments.keys()

	def readMaskParts(self):
		maskParts='Spreadsheets/Mask_Parts.csv'
		csvReader=csv.DictReader(open(maskParts, 'rb'), delimiter=',', quotechar="'")
		self.partsDict={}
		self.positionDict={}
		for count, row in enumerate(csvReader):
			try:
				mType=row['maskType']
				if mType=='':
					pass
				elif mType==self.maskType:
					del row['maskType']
					positionRtoL=row['positionRtoL']
					self.partsDict[mType]=row
					pcbSize=int(row['pcbSize'])
					pcbType=row['pcbType']
					x=float(row['X'])
					y=float(row['Y'])
					coord=(pcbSize, pcbType, x,y)
					self.positionDict[positionRtoL]=coord
					if row['']=='':
						del row['']#This requires spreadsheet to have a note in a column with no row 1 value
			except ValueError:
				pass
		#print self.positionDict
		self.maskWidth=float(self.partsDict[self.maskType]['maskWidth'])
		self.maskHeight=float(self.partsDict[self.maskType]['maskHeight'])
		self.maskRadius=float(self.partsDict[self.maskType]['maskRadius'])
		self.positionRtoL_List=self.positionDict.keys()

	def updateSegment(self, segment='A', SEG_On=1):
		self.ledsPerSegment=self.segmentDict[segment]
		#print self.segmentDict[segment]
		for led in self.ledsPerSegment:
			self.segDict['on_'+str(led)].setVisible(SEG_On)

	def mousePressEvent(self, event):
		itemPosition = self.mapToItem(self, event.pos())
		print 'Mouse at view position ',event.pos(), 'and event position ', itemPosition

class Mask(QGraphicsItem):
	def __init__ (self, maskType='24inTo9', scaleFactor=1, parent=None):
		super(Mask, self).__init__(parent)
		self.maskType=maskType
		self.readMaskParts()
		self.scale(scaleFactor,scaleFactor)
		self.boundingRect = QRectF(0, 0, self.maskWidth, self.maskHeight)

	def boundingRect(self):
		return self.boundingRect

	def paint(self, painter=None, option=None, widget=None):
		painter.setBrush(QColor('#000000'))#NoBrush)#
		painter.setPen(Qt.NoPen)#black)#
		painter.drawRoundedRect(QRectF(0, 0, self.maskWidth, self.maskHeight), self.maskRadius, self.maskRadius)

	def addToBoard(self, model='LX1030', maskID='scorelink', parent=None):
		self.model=model
		self.maskID=maskID
		self.readMasksPerModel()
		self.setPos(self.positionDict[maskID][0],self.positionDict[maskID][1])
		self.setParentItem(parent)

	def readMaskParts(self):
		maskParts='Spreadsheets/Mask_Parts.csv'
		csvReader=csv.DictReader(open(maskParts, 'rb'), delimiter=',', quotechar="'")
		self.partsDict={}
		self.positionDict={}
		for count, row in enumerate(csvReader):
			try:
				mType=row['maskType']
				if mType=='':
					pass
				elif mType==self.maskType:
					del row['maskType']
					positionRtoL=row['positionRtoL']
					self.partsDict[mType]=row
					pcbSize=int(row['pcbSize'])
					pcbType=row['pcbType']
					x=float(row['X'])
					y=float(row['Y'])
					coord=(pcbSize, pcbType, x,y)
					self.positionDict[positionRtoL]=coord
					if row['']=='':
						del row['']#This requires spreadsheet to have a note in a column with no row 1 value
			except ValueError:
				pass
		#print self.positionDict
		self.maskWidth=float(self.partsDict[self.maskType]['maskWidth'])
		self.maskHeight=float(self.partsDict[self.maskType]['maskHeight'])
		self.maskRadius=float(self.partsDict[self.maskType]['maskRadius'])
		self.positionRtoL_List=self.positionDict.keys()

	def readMasksPerModel(self):
		masksPerModel='Spreadsheets/Masks_Per_Model.csv'
		csvReader=csv.DictReader(open(masksPerModel, 'rb'), delimiter=',', quotechar="'")
		self.partsDict={}
		self.positionDict={}
		for count, row in enumerate(csvReader):
			try:
				model=row['model']
				if model=='':
					pass
				elif model==self.model:
					del row['model']
					mask_ID=row['mask_ID']
					self.partsDict[model]=row
					x=float(row['X'])
					y=float(row['Y'])
					coord=(x,y)
					self.positionDict[mask_ID]=coord
					if row['']=='':
						del row['']#This requires spreadsheet to have a note in a column with no row 1 value
			except ValueError:
				pass
		#print self.positionDict
		width=self.partsDict[self.model]['boardWidth']
		height=self.partsDict[self.model]['boardHeight']
		self.boardWidth=float(width)
		self.boardHeight=float(height)

def UI_main():
	print "ON"
	DigitCount = 1
	lx=LX_Driver('LX22', [])#'H16''H13', 'H14', 'H17'
	mp=MP_Data_Handler()
	word=1
	wordStr='word'+str(word)
	LHword0 = mp.Encode(2, 3, word, 1, 0, 0, 0, 0, 0)
	sendList=[LHword0]

	group, bank, word, I_Bit, numericData = mp.Decode(sendList[0])
	#lx.addrDecode(group, bank, word, I_Bit, numericData)
	app = QApplication(sys.argv)
	#qsrand(QTime(0,0,0).secsTo(QTime.currentTime()))
	width = 700
	height = 600

	scene = GraphicsScene()
	view = GraphicsView(scene)

	scene.setSceneRect(0, 0, width, height)
	#scene.setItemIndexMethod(QGraphicsScene.NoIndex)
	mask=Mask('16inClock')
	mask.setPos(5,5)
	pcb=PCB('16', 'digit')
	pcb.addToMask('16inClock', 1, mask)

	pcb2=PCB('16', 'digit')
	pcb2.addToMask('16inClock', 2, mask)

	pcb3=PCB('16', 'colonDec')
	pcb3.addToMask('16inClock', 3, mask)

	pcb4=PCB('16', 'digit')
	pcb4.addToMask('16inClock', 4, mask)

	pcb5=PCB('16', 'digit')
	pcb5.addToMask('16inClock', 5, mask)
	''''''
	scene.addItem(mask)

	#segDon.setZValue(1)
	#printDict(mask.__dict__)
	led=LED(LEDs_On=0, color='amber', scorelink=0, parent=None, pcbSize='18', pcbType='digit')
	printDict(led.__dict__)
	view.setRenderHint(QPainter.Antialiasing)
	#view.setBackgroundBrush(QBrush(QPixmap('Graphics/cheese.jpg')))
	#view.setCacheMode(QGraphicsView.CacheBackground)
	#view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)

	view.setDragMode(QGraphicsView.ScrollHandDrag)
	view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
	view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
	view.setWindowTitle("Digit")
	view.resize(width, height)
	view.scale(20,20)
	view.show()
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
	from MP_Data_Handler import *
	from Driver import *

	UI_main()

