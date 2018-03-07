#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 30%  **LX CLASS COMPLETION** = 90%  Sphinx Approved = *False*

.. topic:: Overview

    This module simulates all drivers.

    :Created Date: 3/16/2015
    :Modified Date: 10/14/2016
    :Author: **Craig Gunter**

"""

from functions import *
from MP_Data_Handler import MP_Data_Handler

class Driver(object):
	'''
	Base class for drivers

	Contains the common public method receive.
	'''
	def __init__(self, driverName='GENERIC'):
		self.driverType='GENERIC'
		self.driverName=driverName
		self.verbose=False
		self.mp=MP_Data_Handler()
		self.fontReceivedGuest=3
		self.justifyReceivedGuest=2
		self.fontReceivedHome=3
		self.justifyReceivedHome=2
		self.fontJustifyControl=0
		self.team='TEAM_1'

	#Start init methods for subclasses

	def defaultJumpers(self):
		self.jumperDict, self.sizeDict = readLXJumperDefinition(self.driverType, self.driverName)
		self.jumperDict.update(dict.fromkeys(self.extraJumpers, 1))
		self.setJumpers()

	def checkDefaultJumpers(self):
		currentJumpers=self.jumperDict
		readLXJumperDefinition(self.driverType, self.driverName)
		if currentJumpers==self.jumperDict:
			check=True
		else:
			check=False
			self.jumperDict.clear()
			self.jumperDict.update(currentJumpers)
		return check

	#End init methods
	#---------------------------------------------------------------
	#Start receive methods

	def receive(self, sendList):
		if self.verbose:
			pass#print 'receive'
		#self.setJumpers()
		for i, j in enumerate(sendList):
			group, bank, word, I_Bit, numericData = self.mp.Decode(sendList[i])
			self.addrDecode(group, bank, word, I_Bit, numericData)

	def getJumpers(self):
		pass

	#End receive methods

class LX_Driver(Driver):
	def __init__(self, driverName, extraJumpers=[]):
		super(LX_Driver, self).__init__(driverName)
		self.driverName=driverName
		self.extraJumpers=extraJumpers
		self.driverType='LXDriver'

		self.J4=self.J5=self.J6=self.J8=self.J9=self.J10=0
		self.horn1=self.horn2=0
		self.legacyDimmingEnable=0
		self.displayEnable=1
		self.brightness=100
		self.quantumDimmingTunnel=0
		self.quantumETNTunnel=0

		self.letters='HGFEDCBA'
		self.segments=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
		self.headers=['J4', 'J5', 'J6', 'J8', 'J9', 'J10']
		self.jumpers=['H13','H16','H14','H17','H15','H18','H2','H4','H12','H3','H11']
		self.blankTypes=['blankIfZeroTens', 'blankIfZeroTens_If_Not100', 'blankIfZeroTens_And_BlankIfZeroUnits_If_TensIsBlank']
		self.refreshStatus()

		#Dictionaries
		self.outputDict = {}
		self.outputDict={\
		'J4':{'A':0, 'B':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0}, \
		'J5':{'A':0, 'B':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0}, \
		'J6':{'A':0, 'B':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0}, \
		'J9':{'A':0, 'B':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0}, \
		'J8':{'A':0, 'B':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0}, \
		'J10':{'A':0, 'B':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0}}

	#Start init methods

	def refreshStatus(self):
		self.defaultJumpers()

	def setJumpers(self, jumperClicked=('',False)):
		if jumperClicked[0]!='':
			self.jumperDict[jumperClicked[0]]=jumperClicked[1]

		if self.jumperDict['H3']:
			self.team=1
		else:
			self.team=0

		if self.jumperDict['H2']:
			self.group=2
			if self.jumperDict['H4']:
				if self.jumperDict['H12']:
					self.bank=4
				else:
					self.bank=3
			else:
				if self.jumperDict['H12']:
					self.bank=2
				else:
					self.bank=1
		else:
			self.group=1
			if self.jumperDict['H4']:
				if self.jumperDict['H12']:
					self.bank=4
				else:
					self.bank=3
			else:
				if self.jumperDict['H12']:
					self.bank=2
				else:
					self.bank=1
		if self.verbose:
			print 'group', self.group, 'bank', self.bank

		self.modeDict={'lampTest':0, 'blankTest':0, 'stat':0}
		if self.jumperDict['H15'] and self.jumperDict['H18']:
			self.modeDict['stat']=1
		elif self.jumperDict['H15']:
			self.modeDict['blankTest']=1
		elif self.jumperDict['H18']:
			self.modeDict['lampTest']=1

		self.word1BlankingJumpersDict = dict.fromkeys(self.blankTypes, 0)
		if self.jumperDict['H16'] and self.jumperDict['H13']:
			self.word1BlankingJumpersDict['blankIfZeroTens_And_BlankIfZeroUnits_If_TensIsBlank']=1
		elif self.jumperDict['H16']:
			self.word1BlankingJumpersDict['blankIfZeroTens']=1
		elif self.jumperDict['H13']:
			self.word1BlankingJumpersDict['blankIfZeroTens_If_Not100']=1

		self.word2BlankingJumpersDict = dict.fromkeys(self.blankTypes, 0)
		if self.jumperDict['H14'] and self.jumperDict['H17']:
			self.word2BlankingJumpersDict['blankIfZeroTens_And_BlankIfZeroUnits_If_TensIsBlank']=1
		elif self.jumperDict['H14']:
			self.word2BlankingJumpersDict['blankIfZeroTens']=1
		elif self.jumperDict['H17']:
			self.word2BlankingJumpersDict['blankIfZeroTens_If_Not100']=1

	#End init methods
	#---------------------------------------------------------------
	#Start receive methods

	def segs2dict(self, data, header):
		if self.verbose:
			print 'seg2dict', data, header
		for segment in self.letters:
			self.outputDict[header][segment]=0
		if data >=0xa:
			pass
		else:
			for segment in list(self.mp._segmentDecode(data, 1)):
				self.outputDict[header][segment]=1

	def handleBlankType(self, word, blankType, numericData, I_Bit):
		if self.verbose:
			pass#print 'handleBlankType', word, blankType, numericData, I_Bit
		if self.modeDict['stat']:
			if word==1:
				self.J4=Units = numericData & 0x0f
				UnitsHeader='J5'
				self.J5=Tens = (numericData & 0xf0) >> 4
				TensHeader='J4'
			elif word==2:
				self.J6=Units= numericData & 0x0f
				UnitsHeader='J8'
				self.J9=Tens = (numericData & 0xf0) >> 4
				TensHeader='J6'
			elif word==3:
				self.J8=Units= numericData & 0x0f
				UnitsHeader='J10'
				self.J10=Tens = (numericData & 0xf0) >> 4
				TensHeader='J9'
		else:
			if word==1:
				self.J4=Units = numericData & 0x0f
				UnitsHeader='J4'
				self.J5=Tens = (numericData & 0xf0) >> 4
				TensHeader='J5'
			elif word==2:
				self.J6=Units= numericData & 0x0f
				UnitsHeader='J6'
				self.J9=Tens = (numericData & 0xf0) >> 4
				TensHeader='J9'

		if blankType==self.blankTypes[0]:#blankIfZeroTens
			if Tens == 0:
				Tens_data=0xf
			else:
				Tens_data=Tens
			Units_data=Units
		elif blankType==self.blankTypes[1]:#blankIfZeroTens_If_Not100
			if Tens == 0 and I_Bit == 0:
				Tens_data=0xf
			else:
				Tens_data=Tens
			Units_data=Units
		elif blankType==self.blankTypes[2]:#blankIfZeroTens_And_BlankIfZeroUnits_If_TensIsBlank
			if Tens == 0 and Units == 0:
				Tens_data=0xf
				Units_data=0xf
			elif Tens == 0:
				Tens_data=0xf
				Units_data=Units
			else:
				Tens_data=Tens
				Units_data=Units
		else:
			Tens_data=Tens
			Units_data=Units
		self.segs2dict(Tens_data, TensHeader)
		self.segs2dict(Units_data, UnitsHeader)

	def checkBlankType(self, word):
		if word==1:
			dictionary = self.word1BlankingJumpersDict
		else:
			dictionary = self.word2BlankingJumpersDict
		for Type in range(3):
			if dictionary[self.blankTypes[Type]]:
				if self.verbose:
					print self.blankTypes[Type]
				return self.blankTypes[Type]

	def handleQuantum(self, word, numericData):
		if word==1:
			if numericData>=0xaa and numericData<0xf0:
				print 'Quantum data tunnel open!!!!'
				if numericData==0xbc:
					print 'Quantum dimming tunnel open!!!!'
					self.quantumDimmingTunnel=1
				elif numericData==0xad:
					print 'Quantum ETN tunnel open!!!!'
					self.quantumETNTunnel=1
				return 1
		elif word==2:
			#print 'numericData', numericData
			if self.quantumDimmingTunnel:
				self.brightness=(numericData & 0x0f) + ((numericData & 0xf0) >> 4)*10
				return 1
			elif self.quantumETNTunnel:
				return 1
		elif word==3:
			if self.quantumETNTunnel:
				return 1
		elif word==4:
			if self.quantumETNTunnel and self.fontJustifyControl:
				return 1
			elif self.quantumETNTunnel:
				self.rightETNByte=numericData

				return 1
		return 0

	def addrDecode(self, group, bank, word, I_Bit, numericData):
		if self.verbose:
			pass#print 'addrDecode', group, bank, word, I_Bit, numericData,
		self.lastWord=word
		if self.modeDict['blankTest']:
			for header in self.headers:
				if self.outputDict.has_key(header):
					for segment in list(self.segments):
						self.outputDict[header][segment]=0
		elif self.modeDict['lampTest']:
			for header in self.headers:
				if self.outputDict.has_key(header):
					for segment in list(self.segments):
						self.outputDict[header][segment]=1
		elif self.modeDict['stat']:
			if group==self.group and bank==self.bank and I_Bit==self.team:
				if word==1:
					if self.handleQuantum(word, numericData):
						pass
					else:
						self.quantumDimmingTunnel=0
						self.outputDict['J4']['I']=I_Bit
						self.outputDict['J5']['I']=I_Bit
						blankType=self.checkBlankType(word)
						self.handleBlankType(word, blankType, numericData, I_Bit)
						self.outputDict['J4']['H']=I_Bit
						self.outputDict['J5']['H']=I_Bit
						self.horn1=I_Bit
						if self.verbose:
							pass#print self.outputDict['J5'], self.outputDict['J4']
				elif word==2:
					if self.handleQuantum(word, numericData):
						pass
					else:
						self.outputDict['J6']['I']=I_Bit
						self.outputDict['J9']['I']=I_Bit
						blankType=self.checkBlankType(word)
						self.handleBlankType(word, blankType, numericData, I_Bit)
						self.outputDict['J6']['H']=I_Bit
						self.outputDict['J9']['H']=I_Bit
						self.horn2=I_Bit
						if self.verbose:
							pass#print self.outputDict['J9'], self.outputDict['J6']
				elif word==3:
					if self.handleQuantum(word, numericData):
						pass
					else:
						self.outputDict['J8']['I']=I_Bit
						self.outputDict['J10']['I']=I_Bit
						blankType=self.checkBlankType(word)
						self.handleBlankType(word, blankType, numericData, I_Bit)
						self.outputDict['J8']['H']=I_Bit
						self.outputDict['J10']['H']=I_Bit
						if self.verbose:
							pass#print self.outputDict['J8'], self.outputDict['J10']
				self._updateDisplay()
		else:
			#NORMAL data for LX Headers
			if group==self.group and bank==self.bank:
				if word==1:
					if self.handleQuantum(word, numericData):
						pass
					else:
						self.quantumDimmingTunnel=0
						self.outputDict['J4']['I']=I_Bit
						self.outputDict['J5']['I']=I_Bit
						blankType=self.checkBlankType(word)
						self.handleBlankType(word, blankType, numericData, I_Bit)
						self.outputDict['J4']['H']=I_Bit
						self.outputDict['J5']['H']=I_Bit
						self.horn1=I_Bit
						if self.verbose:
							pass#print self.outputDict['J5'], self.outputDict['J4']
				elif word==2:
					if self.handleQuantum(word, numericData):
						pass
					else:
						self.outputDict['J6']['I']=I_Bit
						self.outputDict['J9']['I']=I_Bit
						blankType=self.checkBlankType(word)
						self.handleBlankType(word, blankType, numericData, I_Bit)
						self.outputDict['J6']['H']=I_Bit
						self.outputDict['J9']['H']=I_Bit
						self.horn2=I_Bit
						if self.verbose:
							pass#print self.outputDict['J9'], self.outputDict['J6']
				elif word==3:
					if self.handleQuantum(word, numericData):
						pass
					else:
						header='J8'
						segments=self.bin2seg(numericData, header)
						self.outputDict[header]['I']=I_Bit
						self.legacyDimmingEnable=I_Bit
						self.J8=segments
						if self.verbose:
							pass#print self.outputDict[header]
				elif word==4:
					if self.handleQuantum(word, numericData):
						pass
					else:
						header='J10'
						segments=self.bin2seg(numericData, header)
						self.outputDict[header]['I']=I_Bit
						self.displayEnable=I_Bit
						self.J10=segments
						if self.verbose:
							pass#print self.outputDict[header]
				else:
					raise ValueError
				self._updateDisplay()
			else:
				pass#print 'Data not for me'

	def bin2seg(self, data, header):
		segments=''
		binary=[128, 64, 32, 16, 8, 4, 2, 1]
		for count, x in enumerate(binary):
			if data-x>=0:
				segments+=self.letters[count]
				data=data-x
		for segment in self.letters:
			self.outputDict[header][segment]=0
		for segment in list(segments):
			self.outputDict[header][segment]=1
		return segments

	def _updateDisplay(self):
		#Only used for diagnostics
		#print '-----Start of word %d Output-----' % self.lastWord
		for header in self.headers:
			if self.outputDict.has_key(header):
				#print
				#print header
				for segment in list(self.segments):
					if self.outputDict[header][segment]:
						#print 'Light LEDs in segment '+segment+'.'
						pass
		#print '------End of word %d Output------' % self.lastWord
		#print

	#End receive methods

class ETN_Driver(Driver):
	def __init__(self, driverName, extraJumpers=[]):
		super(ETN_Driver, self).__init__(driverName)
		self.driverName=driverName
		self.extraJumpers=extraJumpers
		self.driverType='ETNDriver'

		self.horn1=self.horn2=0
		self.legacyDimmingEnable=0
		self.displayEnable=1
		self.brightness=100
		self.quantumDimmingTunnel=0
		self.quantumETNTunnel=0
		self.lastWord=0

		self.allHeaders=['J10', 'J11', 'J12', 'J13', 'J14', 'J15', 'J16', 'J17']
		self.jumpers=['H9','H10','H11','H12','H13','H16']

		#Dictionaries
		self.captionDict = {'TEAM_1':'GUEST', 'TEAM_2':'HOME'}
		self.displayDict = {'TEAM_1':[], 'TEAM_2':[]}

		self.modeDict={'lampTest':0, 'blankTest':0}
		self.refreshStatus()

	#Start init methods

	def refreshStatus(self):
		self.defaultJumpers()
		self.buildFontDict()
		self.buildDisplayHeaderDict()
		self._updateDisplay()

	def readFont(self, name):
		f = open(name, "r")
		font={}
		font=eval(f.read())
		#print fontDict[str(ord('C'))]
		f.close()
		return font

	def buildFontDict(self):
		self.fontList=['ETN09CondensedCG', 'ETN09RegularCG', 'ETN09BoldCG', 'ETN14CondensedCG', 'ETN14RegularCG', 'ETN14BoldCG']
		self.fontDict={}
		self.fontDict[self.fontList[0]]=self.readFont('Graphics/ETN09CondensedCG_20160506.txt')
		self.fontDict[self.fontList[1]]=self.readFont('Graphics/ETN09RegularCG_20160509.txt')
		self.fontDict[self.fontList[2]]=self.readFont('Graphics/ETN09BoldCG_20160504.txt')
		self.fontDict[self.fontList[3]]=self.readFont('Graphics/ETN14CondensedCG_20160508.txt')
		self.fontDict[self.fontList[4]]=self.readFont('Graphics/ETN14RegularCG_20160512.txt')
		self.fontDict[self.fontList[5]]=self.readFont('Graphics/ETN14BoldCG_20160507.txt')
		#self.fontName=self.fontList[0]
		self.fontSpaceing=1
		for fonts in self.fontDict:
			self.fontDict[fonts]['32']=[0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0, 0]


		#print self.fontDict['ETN09RegularCG']['32']
		for eachFont in self.fontList:
			shift1=True
			if eachFont=='ETN14BoldCG':
				shift1=False
			for character in range(32,127):
				c=self.fontDict[eachFont][str(character)]
				c=fontTrim(c, shift=shift1, displayHeight=self.displayHeight)
				self.fontDict[eachFont][str(character)]=c
		#print self.fontDict['ETN09RegularCG']['32']
		#raw_input()

	def setJumpers(self, jumperClicked=('',False)):
		self.lampDisplay=[]
		if jumperClicked[0]!='':
			self.jumperDict[jumperClicked[0]]=jumperClicked[1]
		if self.jumperDict['H16']:
			self.modeDict['lampTest']=1
		else:
			self.modeDict['lampTest']=0
		bitShift=4
		self.sizeAddress=0
		for x, jumper in enumerate(self.jumpers):
			if jumper=='H16':
				pass
			else:
				self.sizeAddress+=self.jumperDict[jumper]<<bitShift
				bitShift-=1
		try:
			self.sizeDict['ETN'+str(self.sizeAddress)]
			driverName='ETN'+str(self.sizeAddress)
		except:
			print 'NOT a real ETN Driver setting'
			driverName=self.driverName
		self.displayWidth=self.sizeDict[driverName]['width']
		self.displayHeight=self.sizeDict[driverName]['height']
		self.displayRows=self.sizeDict[driverName]['rows']
		self.totalPanels=self.displayWidth/16+bool(self.displayWidth%16)
		self.halfPanelFlag=bool(self.displayWidth%16)
		if self.displayRows==2:
			self.twoRows=True
		else:
			self.twoRows=False

		val=2**(self.displayWidth)-1
		for x in range(self.displayHeight):
			self.lampDisplay.append(val)
		'''
		print 'self.displayWidth', self.displayWidth, \
		'self.displayHeight', self.displayHeight, \
		'self.totalPanels', self.totalPanels, \
		'self.halfPanelFlag', self.halfPanelFlag, \
		'self.displayRows', self.displayRows, \
		'self.twoRows', self.twoRows
		'''

	def buildDisplayHeaderDict(self):
		if self.twoRows:
			self.headers=['J10', 'J11', 'J14', 'J15']
		else:
			self.headers=['J10', 'J14']
		self.displayHeaderDict=dict.fromkeys(self.headers, [])
		panel=self.totalPanels
		for header in self.headers:
			self.displayHeaderDict[header]=dict([])
		self.headers=['J10', 'J14']

		#print self.displayHeaderDict

	#End init methods
	#---------------------------------------------------------------
	#Start receive methods

	def handleQuantum(self, word, numericData):
		if word==1:
			if numericData>=0xaa and numericData<0xf0:
				print 'Quantum data tunnel open!!!!'
				if numericData==0xbc:
					print 'Quantum dimming tunnel open!!!!'
					self.quantumDimmingTunnel=1
					return 1
				elif numericData==0xad:
					print 'Quantum ETN tunnel open!!!!'
					self.quantumETNTunnel=1
					return 1
		elif word==2:
			#print 'numericData', numericData
			if self.quantumDimmingTunnel:
				self.brightness=(numericData & 0x0f) + ((numericData & 0xf0) >> 4)*10
				return 1
			elif self.quantumETNTunnel:
				if numericData>=64:
					numericData-=64
					self.team='TEAM_2'
					#print 'self.team =', self.team
				else:
					self.team='TEAM_1'
					#print 'self.team =', self.team

				if numericData:
					#address pair
					self.fontJustifyControl=0
					#print 'address pair', numericData
					self.addressPair=numericData
				else:
					#control for font-justify
					self.fontJustifyControl=1

				return 1
		elif word==3:
			if self.quantumETNTunnel and not self.fontJustifyControl:
				self.leftETNByte=numericData
				#print 'leftETNByte', numericData

				#self.captionDict[self.team]=self.captionDict[self.team]+chr(self.leftETNByte)
				return 1
		elif word==4:
			if self.quantumETNTunnel and self.fontJustifyControl:
				if self.team=='TEAM_1':
					self.fontReceivedGuest=numericData/6+1
					self.justifyReceivedGuest=numericData%6+1
				elif self.team=='TEAM_2':
					self.fontReceivedHome=numericData/6+1
					self.justifyReceivedHome=numericData%6+1
				return 1
			elif self.quantumETNTunnel:
				self.rightETNByte=numericData
				#print 'rightETNByte', numericData
				if self.leftETNByte and self.rightETNByte:
					self.captionDict[self.team]=self.captionDict[self.team][:(self.addressPair-1)*2]+chr(self.leftETNByte)+chr(self.rightETNByte)
				elif self.leftETNByte:
					self.captionDict[self.team]=self.captionDict[self.team][:(self.addressPair-1)*2]+chr(self.leftETNByte)
				elif self.rightETNByte:
					print 'ERROR - should not send 0 in word 3 and something in word 4'
				else:
					self.captionDict[self.team]=''
				return 1
		return 0

	def addrDecode(self, group, bank, word, I_Bit, numericData):
		if self.verbose:
			pass#print 'addrDecode', group, bank, word, I_Bit, numericData

		self.lastWord=word
		if self.modeDict['lampTest']==1:
			pass
		else:
			if word==1:
				if self.handleQuantum(word, numericData):
					pass
				else:
					self.quantumDimmingTunnel=0
					self.quantumETNTunnel=0
					self.fontJustifyControl=0
			elif word==2:
				if self.handleQuantum(word, numericData):
					pass
			elif word==3:
				if self.handleQuantum(word, numericData):
					pass
			elif word==4:
				if self.handleQuantum(word, numericData):
					pass
			else:
				raise ValueError
			if word==4:
				self._updateDisplay()

	def _updateDisplay(self):
		#print '-----Start of word %d Output-----' % self.lastWord
		for caption in self.captionDict.keys():
			if caption=='TEAM_1':
				fontReceived=self.fontReceivedGuest
				justifyReceived=self.justifyReceivedGuest
			elif caption=='TEAM_2':
				fontReceived=self.fontReceivedHome
				justifyReceived=self.justifyReceivedHome

			invertFlag=False
			if fontReceived==4 or fontReceived==5 or fontReceived>=6:
				invertFlag=True
				fontReceived-=3
			#switch to current font
			font=fontReceived-1
			if self.displayHeight==14:
				font+=3
			self.fontName=self.fontList[font]

			#self.displayDict[caption]=[]
			if self.modeDict['lampTest']==1:
				self.displayDict[caption]=self.lampDisplay
			else:
				self.displayDict[caption]=self._stringToDisplay(self.captionDict[caption])
			#print 'Panel '+caption+' contains "'+self.captionDict[caption]+'".'
			#print self._stringToDisplay(self.captionDict[caption])
			shift=0
			#switch to current justification
			if justifyReceived==1:
				#Left justify
				shift=0
				#print 'shift=', shift
			elif justifyReceived==2:
				#Center Justify
				shift=self.displayWidth/2-fontWidth(self.displayDict[caption])/2
				#print 'shift=', shift
			elif justifyReceived==3:
				#Right Justify
				shift=self.displayWidth-fontWidth(self.displayDict[caption])
				#print 'shift=', shift, self.displayWidth,fontWidth(self.displayDict[caption])
			for x, element in enumerate(self.displayDict[caption]):
				if shift<0:
					self.displayDict[caption][x]=element>>abs(shift)
				else:
					self.displayDict[caption][x]=element<<shift

				if invertFlag:
					self.displayDict[caption][x]=~self.displayDict[caption][x]

		self._updateDisplayHeaders()

		#print '------End of word %d Output------' % self.lastWord
		#print

	def _updateDisplayHeaders(self):
		#print 'Enter updateDisplayHeaders'
		panel=self.totalPanels
		for header in self.headers:
			#print header
			if header=='J10':
				team='TEAM_1'
				headerTop='J11'
			elif header=='J14':
				team='TEAM_2'
				headerTop='J15'
			tempList=list(self.displayDict[team])
			#for panel in range((self.totalPanels+1)):
			#	self.displayHeaderDict[header].clear()
			#print 'tempList', tempList
			while panel:
				#print 'before', tempList
				if panel==self.totalPanels and self.halfPanelFlag:
					shift=8
					for x, element in enumerate(tempList):
						tempList[x]=element<<shift
					if self.twoRows:
						self.displayHeaderDict[header][panel]=list(tempList[:7])
						try:
							self.displayHeaderDict[headerTop][panel]=list(tempList[7:])
						except:
							pass
					else:
						self.displayHeaderDict[header][panel]=list(tempList)
				elif self.halfPanelFlag:
					shift=16
					for x, element in enumerate(tempList):
						tempList[x]=element>>shift
					if self.twoRows:
						self.displayHeaderDict[header][panel]=list(tempList[:7])
						try:
							self.displayHeaderDict[headerTop][panel]=list(tempList[7:])
						except:
							pass
					else:
						self.displayHeaderDict[header][panel]=list(tempList)
				else:
					shift=16
					if self.twoRows:
						self.displayHeaderDict[header][panel]=list(tempList[:7])
						try:
							self.displayHeaderDict[headerTop][panel]=list(tempList[7:])
						except:
							pass
					else:
						self.displayHeaderDict[header][panel]=list(tempList)
					for x, element in enumerate(tempList):
						tempList[x]=element>>shift
				#print 'shift', shift, 'panel', panel
				#print 'after', tempList

				panel-=1
			panel=self.totalPanels
		#print self.displayHeaderDict

		#self.displayHeaderDict['J14']=self.displayDict['TEAM_2']

	def _stringToDisplay(self, string):
		'''Converts caption string to a bit map of LEDs regardless of panels connected. Left Justified.'''
		display=[]
		#print 'string', string
		for y, character in enumerate(string):
			if y==0:
				display=list(self.fontDict[self.fontName][str(ord(string[0]))])
				#print '0', string[0], display, 'fontWidth(display)', fontWidth(display)
				if ord(string[y])==32:
					space=True
				else:
					space=False
				displayWidth=0
				currentCharacterWidth=fontWidth(display, space=space, fontName=self.fontName)
			else:
				previousCharacter=list(self.fontDict[self.fontName][str(ord(string[y-1]))])
				currentCharacter=list(self.fontDict[self.fontName][str(ord(string[y]))])
				if ord(string[y-1])==32:
					space=True
				else:
					space=False
				previousCharacterWidth=fontWidth(previousCharacter, space=space, fontName=self.fontName)
				if ord(string[y])==32:
					space=True
				else:
					space=False
				currentCharacterWidth=fontWidth(currentCharacter, space=space, fontName=self.fontName)
				if self.displayHeight==14:
					self.fontSpaceing=2
				else:
					self.fontSpaceing=1
				displayWidth=previousCharacterWidth+self.fontSpaceing+displayWidth

				for x, element in enumerate(currentCharacter):
					currentCharacter[x]=element<<displayWidth
					display[x]+=currentCharacter[x]
		return display

	#End receive methods

class Triac_Driver(LX_Driver):
	def __init__(self, driverName):
		super(Triac_Driver, self).__init__(driverName)
		self.driverType='triacDriver'
		self.blankTypes=['blankIfZeroTens', 'blankIfZeroTens_If_Not100']
		self.headers=['J4', 'J5', 'J6', 'J8', 'J9', 'J10']#fix

	def handleQuantum(self, word, numericData):
		return 0

	def handleBlankType(self, wordStr, blankType, numericData, I_Bit):
		if wordStr=='word1':
			self.J4=Units = numericData & 0x0f
			UnitsHeader='J4'
			self.J5=Tens = (numericData & 0xf0) >> 4
			TensHeader='J5'
		elif wordStr=='word2':
			self.J6=Units= numericData & 0x0f
			UnitsHeader='J6'
			self.J9=Tens = (numericData & 0xf0) >> 4
			TensHeader='J9'

		if blankType==self.blankTypes[0]:#blankIfZeroTens
			if Tens == 0:
				Tens_data=0xf
			else:
				Tens_data=Tens
			Units_data=Units
		elif blankType==self.blankTypes[1]:#blankIfZeroTens_If_Not100
			if Tens == 0 and I_Bit == 0:
				Tens_data=0xf
			else:
				Tens_data=Tens
			Units_data=Units
		else:
			Tens_data=Tens
			Units_data=Units
		self.segs2dict(Tens_data, wordStr, TensHeader)
		self.segs2dict(Units_data, wordStr, UnitsHeader)

class LDM_Driver(Driver):
	def __init__(self, driverName):
		super(LDM_Driver, self).__init__(driverName)
		self.driverType='LDMDriver'
		self.blankTypes=['blankIfZeroTens', 'blankIfZeroTens_If_Not100', 'blankUnderMinute']#fix
		self.headers=[\
		'J5', 'J4', 'J17', 'J6', 'J16', 'J18', \
		'J8', 'J7', 'J20', 'J9', 'J19', 'J21', \
		'J11', 'J10', 'J23', 'J12', 'J22', 'J24', \
		'J15'] #I-Bits(bank 3 and 4), Colon, Decimal, J19-abcd

		if 'GS1' in self.jumperDict:
			self.group=2
		elif 'GS2' in self.jumperDict:
			self.group=1

	def handleQuantum(self, word, numericData):
		return 0


def test():
	'''Test function if module ran independently.'''
	print "ON"
	lx=ETN_Driver(driverName='ETN16', extraJumpers=[])#'H16''H13', 'H14', 'H17'
	mp=MP_Data_Handler()
	F=1
	J=1
	FJ=(F-1)*6+J-1
	#raw_input()
	#LHword0 = mp.Encode(group, bank, word, I_Bit, H_Bit, highNibble, lowNibble, blankType, segmentData, statFlag=False, pass3_4Flag=False)
	LHword1 = mp.Encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
	LHword2 = mp.Encode(2, 4, 2, 0, 0, 0, 1, 0, 0, pass3_4Flag=True)
	LHword3 = mp.Encode(2, 4, 3, 0, 0, 0, ord('C'), 0, '', pass3_4Flag=True)
	LHword4 = mp.Encode(2, 4, 4, 0, 0, 0, 0, 0, '', pass3_4Flag=True)
	LHword5 = mp.Encode(2, 4, 2, 0, 0, 0, 1, 0, 0, pass3_4Flag=True)
	LHword6 = mp.Encode(2, 4, 3, 0, 0, 0, ord('C'), 0, '', pass3_4Flag=True)
	LHword7 = mp.Encode(2, 4, 4, 0, 0, 0, ord('H'), 0, '', pass3_4Flag=True)
	LHword8 = mp.Encode(2, 4, 2, 0, 0, 0, 2, 0, 0, pass3_4Flag=True)
	LHword9 = mp.Encode(2, 4, 3, 0, 0, 0, ord('A'), 0, '', pass3_4Flag=True)
	LHword10 = mp.Encode(2, 4, 4, 0, 0, 0, 0, 0, '', pass3_4Flag=True)
	LHword11 = mp.Encode(2, 4, 2, 0, 0, 0, 2, 0, 0, pass3_4Flag=True)
	LHword12 = mp.Encode(2, 4, 3, 0, 0, 0, ord('A'), 0, '', pass3_4Flag=True)
	LHword13 = mp.Encode(2, 4, 4, 0, 0, 0, ord('P'), 0, '', pass3_4Flag=True)
	sendList=[LHword1 , LHword2, LHword3, LHword4, LHword5, LHword6, LHword7, LHword8, LHword9, LHword10, LHword11, LHword12, LHword13]

	LH2word1 = mp.Encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
	LH2word2 = mp.Encode(2, 4, 2, 0, 0, 0, 65, 0, 0, pass3_4Flag=True)
	LH2word3 = mp.Encode(2, 4, 3, 0, 0, 0, ord('J'), 0, '', pass3_4Flag=True)
	LH2word4 = mp.Encode(2, 4, 4, 0, 0, 0, 0, 0, '', pass3_4Flag=True)
	LH2word5 = mp.Encode(2, 4, 2, 0, 0, 0, 65, 0, 0, pass3_4Flag=True)
	LH2word6 = mp.Encode(2, 4, 3, 0, 0, 0, ord('@'), 0, '', pass3_4Flag=True)
	LH2word7 = mp.Encode(2, 4, 4, 0, 0, 0, ord('O'), 0, '', pass3_4Flag=True)
	LH2word8 = mp.Encode(2, 4, 2, 0, 0, 0, 66, 0, 0, pass3_4Flag=True)
	LH2word9 = mp.Encode(2, 4, 3, 0, 0, 0, ord('$'), 0, '', pass3_4Flag=True)
	LH2word10 = mp.Encode(2, 4, 4, 0, 0, 0, 0, 0, '', pass3_4Flag=True)
	LH2word11 = mp.Encode(2, 4, 2, 0, 0, 0, 66, 0, 0, pass3_4Flag=True)
	LH2word12 = mp.Encode(2, 4, 3, 0, 0, 0, ord(' '), 0, '', pass3_4Flag=True)
	LH2word13 = mp.Encode(2, 4, 4, 0, 0, 0, ord(' '), 0, '', pass3_4Flag=True)
	LH2word14 = mp.Encode(2, 4, 2, 0, 0, 0,  67, 0, 0, pass3_4Flag=True)
	LH2word15 = mp.Encode(2, 4, 3, 0, 0, 0, ord('~'), 0, '', pass3_4Flag=True)
	LH2word16 = mp.Encode(2, 4, 4, 0, 0, 0, 0, 0, '', pass3_4Flag=True)
	sendList2=[LH2word1 , LH2word2, LH2word3, LH2word4, LH2word5, LH2word6, LH2word7, LH2word8, LH2word9, LH2word10, LH2word11, LH2word12, LH2word13, LH2word14, LH2word15, LH2word16]

	#LHword1 = mp.Encode(2, 3, 4, 0, 1, 0, 0, 0, 'a')
	#sendList=[LHword1]
	lx.receive(sendList)
	lx.receive(sendList2)
	#guestDisplay=lx.displayDict['TEAM_1']
	#homeDisplay=lx.displayDict['TEAM_2']
	#print guestDisplay, homeDisplay

	printDictsExpanded(lx)

	raw_input()


if __name__ == '__main__':
	from Game import printDict
	import sys
	test()
