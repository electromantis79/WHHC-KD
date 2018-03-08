#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 90%  Sphinx Approved = **True**

.. topic:: Overview

    This module simulates a scoreboard.

    :Created Date: 3/16/2015
    :Modified Date: 10/24/2016
    :Author: **Craig Gunter**

"""




from functions import *
from Console import Console
from Driver import LX_Driver
from Driver import ETN_Driver

from app.pyqt.pyqt_subclasses import * #Holds PyQt4 imports
from app.pyqt.UI_Scoreboard_Parts import *

class Scoreboard(Console):
	'''
	Simulation of a scoreboard with a built-in console.
	'''
	def __init__(self, modelName='LX1030', driverType='LXDriver', \
	parent=None, scene=None, vboseList=[1,0,0], boardColor='COMPANY_LOGO', \
	captionColor='WHITE', stripeColor='WHITE', checkEventsFlag=True, \
	serialInputFlag=0, serialOutputFlag=1, encodePacketFlag=False):

		if modelName=='modelList':
			self.model=modelName
			self.readDigitsPerModel()
		else:
			super(Scoreboard, self).__init__(\
			vboseList=vboseList, checkEventsFlag=checkEventsFlag, \
			serialInputFlag=serialInputFlag, serialOutputFlag=serialOutputFlag, \
			encodePacketFlag=encodePacketFlag)
			verbose(['\nCreating Scoreboard object'], self.verbose)
			self.className='scoreboard'
			self.model=modelName
			self.driverType=driverType
			self.graphicParent=parent
			self.graphicScene=scene
			self.boardColor=boardColor
			self.captionColor=captionColor
			self.stripeColor=stripeColor
			self.statWidth=12
			self.resetGraphicsFlag=False
			self.boardReset()

	def boardReset(self):
		'''Reinitialize scoreboard.'''
		#Build dictionaries and components
		print self.driverType
		self.readDigitsPerModel()
		self.loadDrivers()
		for driver in self.driverList:
			if driver[:3]=='ETN':
					self.lxDict[driver].captionDict[self.game.guest]=self.game.teamsDict[self.game.guest].teamData['name']
					self.lxDict[driver].captionDict[self.game.home]=self.game.teamsDict[self.game.home].teamData['name']
					self.lxDict[driver].fontReceivedGuest=self.game.teamsDict[self.game.guest].teamData['font']
					self.lxDict[driver].fontReceivedHome=self.game.teamsDict[self.game.home].teamData['font']
					self.lxDict[driver].justifyReceivedGuest=self.game.teamsDict[self.game.guest].teamData['justify']
					self.lxDict[driver].justifyReceivedHome=self.game.teamsDict[self.game.home].teamData['justify']
		self.partsDict, self.positionDict, self.heightDict, self.boardWidth, self.boardHeight = readMasksPerModel(self.model)

		self.addrMap.adjustAllBanks()
		#self.data2Drivers(self.addrMap.wordList)

	#Init functions section

	def readDigitsPerModel(self):
		'''
		Read Spreadsheets/Digits_Per_Model.csv and build many dictionaries out of it.
		'''
		digitsPerModel='Spreadsheets/Digits_Per_Model.csv'
		csvReader=csv.DictReader(open(digitsPerModel, 'rb'), delimiter=',', quotechar="'")
		self.lxDict={}
		headerDict={}
		self.maskID_Dict={}
		self.addressWordDict={}
		modelDict={}
		self.functionDict={}
		self.driverPosDict={}
		self.powerSupplyDict={}
		self.driversPoweredByDict={}
		self.lxChassisDict={}
		self.lxDataOrderDict={}
		self.lxPerChassisDict={}
		self.chassisDict={}
		self.psChassisDict={}
		self.functionList=[]
		for count, row in enumerate(csvReader):
			try:
				model=row['model']
				if model=='':
					pass
				elif model!=self.model:
					#Doing this to make a list of all models on the spread sheet
					modelDict[model]=0
				else:
					modelDict[model]=0
					pcbValue=row['pcbValue']
					self.functionList.append(pcbValue)
					row['addressWord']=int(row['addressWord'])
					del row['model']
					del row['pcbValue']
					if row['']=='':
						del row['']#This requires spreadsheet to have a note in a column with no row 1 value
					self.functionDict[pcbValue]=row
			except ValueError:
				pass
		self.modelList=modelDict.keys()
		for function in self.functionList:
			self.driverPosDict[self.functionDict[function]['LXDriver']]=self.functionDict[function]['lxPosition']
			headerDict[self.functionDict[function]['LXHeader']]=0
			self.maskID_Dict[self.functionDict[function]['mask_ID']]=self.functionDict[function]['maskType']
			self.addressWordDict[self.functionDict[function]['addressWord']]=0
			self.powerSupplyDict[self.functionDict[function]['psChassis']]=(self.functionDict[function]['psPosition'], self.functionDict[function]['psLabel'])
			if self.functionDict[function]['LXDriver'][:3]=='ETN':
				if self.game.gameData['sportType']=='basketball' or self.game.gameData['sportType']=='hockey':
					self.driversPoweredByDict[self.functionDict[function]['LXDriver']]=1
				else:
					self.driversPoweredByDict[self.functionDict[function]['LXDriver']]=self.functionDict[function]['lxPosition']
			else:
				self.driversPoweredByDict[self.functionDict[function]['LXDriver']]=self.functionDict[function]['psChassis']
			self.lxChassisDict[self.functionDict[function]['LXDriver']]=self.functionDict[function]['chassisMask']
			self.lxDataOrderDict[self.functionDict[function]['LXDriver']]=self.functionDict[function]['dataOrder']
			self.psChassisDict[self.functionDict[function]['psChassis']]=self.functionDict[function]['chassisMask']
			self.chassisDict[self.functionDict[function]['chassisMask']]=0

		self.chassisList=self.chassisDict.keys()
		self.driverList=self.driverPosDict.keys()
		self.headerList=headerDict.keys()
		self.maskID_List=self.maskID_Dict.keys()
		self.powerSupplyList=self.powerSupplyDict.keys()

		for supply in self.powerSupplyList:
			self.powerSupplyDict[supply]=([], self.powerSupplyDict[supply])
			for driver in self.driverList:
				if self.driversPoweredByDict[driver]==supply:
					self.powerSupplyDict[supply][0].append(driver)
				elif \
				(self.game.gameData['sportType']=='basketball' or \
				self.game.gameData['sportType']=='hockey') and driver[:3]=='ETN':
					self.powerSupplyDict[supply][0].append(driver)
		for chassis in self.chassisList:
			self.lxPerChassisDict[chassis]=[]
			for driver in self.driverList:
				if self.lxChassisDict[driver]==chassis:
					self.lxPerChassisDict[chassis].append(driver)
		print self.driverList

	def loadDrivers(self):
		'''Creates a dictionary of all driver objects in the scoreboard.'''
		if self.driverType=='LXDriver':
			for driver in self.driverList:
				verbose(['loading driver', driver], self.verboseMore)
				if driver[:3]=='ETN':
					self.lxDict[driver]=ETN_Driver(driver, extraJumpers=[])
				else:
					self.lxDict[driver]=LX_Driver(driver, extraJumpers=[])


	#End init functions

	#Callable functions section

	def data2Drivers(self, sendList):
		'''
		Main function used to communicate to drivers.
		'''
		#Send data to each driver
		for driver in self.driverList:
			verbose(['sending data to driver', driver], self.verboseMore)
			self.lxDict[driver].receive(sendList)

def test():
	'''Test function if module ran independently.'''
	print "ON"
	sport='MPHOCKEY_LX1'
	c=Config()
	configDict=readConfig()
	c.writeSport(sport)
	c.writeSERVER(True)
	model= Scoreboard(modelName='LX8350', driverType='LXDriver', \
	serialInputFlag=1, serialOutputFlag=1, encodePacketFlag=True)
	while 1:
		pass
	#print model.game.clockDict['periodClock'].countUp
	#printDictsExpanded(model,1)
	#printDict(model.__dict__,1)

if __name__ == '__main__':
	from Config import Config
	from MP_Data_Handler import MP_Data_Handler
	import multiprocessing
	test()
