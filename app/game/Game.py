#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 99%  Sphinx Approved = **True**

.. topic:: Overview

    This module holds the game data for all sports.

    :Created Date: 3/12/2015
    :Modified Date: 10/21/2016
    :Author: **Craig Gunter**

"""

import threading

from app.functions import *
from app.game.clock import clock
from app.game.option_jumpers_class import OptionJumpers
from app.game.Team import Team

class Game(object):
	'''Generic base class for all sports.'''
	def __init__(self, numberOfTeams=2):
		self.numberOfTeams=numberOfTeams

		#build dictionaries	from files
		self.configDict=readConfig()
		self.gameSettings=readGameDefaultSettings()
		self.segmentTimerSettings=readSegmentTimerSettings()
		self.gameSettings.update(self.segmentTimerSettings)#Don't use the same names
		self.gameData=csvOneRowRead(fileName='Spreadsheets/gameDefaultValues.csv')

		#classes and attributes
		self.gameData['sportType']="GENERIC"
		self.gameData['sport']=self.configDict['sport']
		self.sport=self.configDict['sport']
		self.gameData['optionJumpers']=self.configDict['optionJumpers']
		self.gameData['Version']=self.configDict['Version']
		
		#Handle option jumpers
		self.optionJumpers=OptionJumpers(self.sport, sportList, jumperString=self.gameData['optionJumpers'])
		self.gameSettings=self.optionJumpers.getOptions(self.gameSettings)
		
		self.decimalIndicator=not self.gameData['colonIndicator']

		self._createTeams()

		self._addTeamNameData()

		self._createClockDict()

		#digit values common to all _sports
		self.setGameData('segmentCount', self.getGameData('segmentCount'))
		self.setGameData('period', self.getGameData('period'))

		if self.configDict['sport'][-4:]=='ball' or self.configDict['sport'][-6:]=='soccer':
			self.gameSettings['multisportMenuFlag'] = True
		else:
			self.gameSettings['multisportMenuFlag'] = False

		if self.configDict['sport'][-8:]=='football' or self.configDict['sport'][-6:]=='soccer':
			self.gameSettings['multisportChoiceFlag'] = True
		else:
			self.gameSettings['multisportChoiceFlag'] = False

		#This is problematic when switching sports alot while coding
		#saveObject2File(dictionary=self.gameSettings, dictionaryName='game/gameUserSettings')
		#print "Saved current user settings to file."

	def _createClockDict(self):
		#class object instantiation
		self.clockDict={}

		self.clockDict['timeOutTimer']=clock(False, self.gameSettings['timeOutTimerMaxSeconds'], clockName='timeOutTimer')
		self.gameData = self.clockDict['timeOutTimer'].gameDataUpdate(self.gameData, name='timeOutTimer') #function adds values to the gameData dictionary
		self.clockDict['timeOfDayClock']=clock(True, maxSeconds=self.gameSettings['timeOfDayClockMaxSeconds'], resolution=0.1, hoursFlag=True, clockName='timeOfDayClock')
		self.gameData = self.clockDict['timeOfDayClock'].gameDataUpdate(self.gameData, name='timeOfDayClock') #function adds values to the gameData dictionary
		self.clockDict['segmentTimer']=clock(self.gameSettings['segmentTimerCountUp'], self.gameSettings['segmentTimerMaxSeconds'], clockName='segmentTimer')
		self.gameData = self.clockDict['segmentTimer'].gameDataUpdate(self.gameData, name='segmentTimer') #function adds values to the gameData dictionary
		self.clockDict['flashTimer']=clock(False, self.gameSettings['flashTimerMaxSeconds'], clockName='flashTimer')
		self.clockDict['intervalTimer']=clock(False, self.gameSettings['intervalTimerMaxSeconds'], clockName='intervalTimer')
		self.clockDict['periodHornFlashTimer']=clock(False, self.gameSettings['periodHornFlashDuration'], clockName='periodHornFlashTimer')
		self.clockDict['periodBlinkyFlashTimer']=clock(False, .5, clockName='periodBlinkyFlashTimer')
		if self.gameData['sport']=="MPGENERIC":
			self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], 15*60, clockName='periodClock')
			self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData, name='periodClock') #function adds values to the gameData dictionary
		self.clockList=self.clockDict.keys()
		#print self.clockList
		
	def KillClockThreads(self):
		for clock in self.clockList:
			self.clockDict[clock].Kill()
		
	def _createTeams(self):
		'''Instantiate all teams into a dictionary.'''
		self.teamsDict={}
		self.teamNamesList=[]
		for team in range(self.numberOfTeams):
			name='TEAM_'+str(team+1)
			self.teamNamesList.append(name)
			self.teamsDict[name]=Team(self.gameData['sportType'])

	def _addTeamNameData(self):
		self.home=self.teamNamesList[self.gameSettings['home']]
		self.guest=self.teamNamesList[self.gameSettings['guest']]
		self.teamsDict[self.guest].teamData['name']=self.gameSettings['teamOneName']
		self.teamsDict[self.home].teamData['name']=self.gameSettings['teamTwoName']
		self.teamsDict[self.guest].teamData['font']=self.gameSettings['teamOneFont']
		self.teamsDict[self.home].teamData['font']=self.gameSettings['teamTwoFont']
		self.teamsDict[self.guest].teamData['justify']=self.gameSettings['teamOneJustify']
		self.teamsDict[self.home].teamData['justify']=self.gameSettings['teamTwoJustify']
		#print 'self.teamsDict[self.guest].teamData[name]', self.teamsDict[self.guest].teamData['name']

	def _reverseHomeAndGuest(self):
		#Never used
		self.home, self.guest = self.guest, self.home

	def getPlayerData(self, team, dataName, playerID=None, playerNumber=None):
		if playerID is None and playerNumber is None:
			print team, dataName, 'playerID=None, playerNumber=None'
		elif playerID  is not None:
			return self.teamsDict[team].playersDict[playerID].playerData[dataName]
		elif playerNumber is not None:
			for playerID in self.teamsDict[team].playersDict.keys():
				if self.teamsDict[team].playersDict[playerID].playerData['playerNumber']==playerNumber:
					return playerID
		else:
			return self.teamsDict[team].playersDict[playerID].playerData[dataName]

	def getTeamData(self, team, dataName):
		return self.teamsDict[team].teamData[dataName]

	def getGameData(self, dataName):
		return self.gameData[dataName]

	def getClockData(self, clockName, dataName):
		if self.clockDict.has_key(clockName):
			return self.clockDict[clockName].timeUnitsDict[dataName]
		else:
			return None

	def setPlayerData(self, team, player, dataName, value, places=2):
		if self.teamsDict[team].playersDict.has_key(player):
			playerData = self.teamsDict[team].playersDict[player].playerData
			if places==3:
				playerData[dataName+'Hundreds'] = value/100
				playerData[dataName+'Tens'] = value/10%10
				playerData[dataName+'Units'] = value%10
				playerData[dataName] = value
			elif places==2:
				if dataName=='playerNumber':
					playerData[dataName+'Tens'] = value[0]
					playerData[dataName+'Units'] = value[1]
					playerData[dataName] = value
				else:
					playerData[dataName+'Tens'] = value/10
					playerData[dataName+'Units'] = value%10
					playerData[dataName] = value
			elif places==1:
				if dataName=='0' or dataName=='':
					pass
				else:
					playerData[dataName] = value
			else:
				print 'Failed to set '+team,dataName, 'value of',value
				print 'places', places, 'player', player, 'playerData', playerData
		else:
			print 'Player %s is not in self.teamsDict[team].playersDict.' % (player)

	def setTeamData(self, team, dataName, value, places=2):
		teamData = self.teamsDict[team].teamData
		if value is not None:
			if places==3:
				teamData[dataName+'Hundreds'] = value/100
				teamData[dataName+'Tens'] = value/10%10
				teamData[dataName+'Units'] = value%10
				teamData[dataName] = value
			elif places==2:
				if value==255:
					teamData[dataName+'Tens'] = 15
					teamData[dataName+'Units'] = 15
					teamData[dataName] = value
				else:
					teamData[dataName+'Tens'] = value/10
					teamData[dataName+'Units'] = value%10
					teamData[dataName] = value
			elif places==1:
				if dataName=='0' or dataName=='':
					pass
				else:
					teamData[dataName] = value
			else:
				print 'Failed to set %s %s value of %d.' % (team, dataName, value)
				print 'places', places, 'teamData', teamData
		else:
				print 'Failed to set %s %s value of None.' % (team, dataName)
				print 'places', places, 'teamData', teamData

	def setGameData(self, dataName, value, places=2):
		if places==3:
			self.gameData[dataName+'Hundreds'] = value/100
			self.gameData[dataName+'Tens'] = value/10%10
			self.gameData[dataName+'Units'] = value%10
			self.gameData[dataName] = value
		elif places==2:
			if value==255:
				self.gameData[dataName+'Tens'] = 15
				self.gameData[dataName+'Units'] = 15
				self.gameData[dataName] = value
			else:
				self.gameData[dataName+'Tens'] = value/10
				self.gameData[dataName+'Units'] = value%10
				self.gameData[dataName] = value
		elif places==1:
			if dataName=='0' or dataName=='':
				pass
			else:
				self.gameData[dataName] = value
		else:
			print 'Failed to set %s value of %d.' % (dataName, value)

	def setClockData(self, clockName, dataName, value, places=2):
		#print 'clockName', clockName, 'dataName', dataName, 'value', value, 'places', places

		clockData = self.clockDict[clockName].timeUnitsDict
		if places==3:
			clockData[dataName+'Hundreds'] = value/100
			clockData[dataName+'Tens'] = value/10%10
			clockData[dataName+'Units'] = value%10
			clockData[dataName] = value
		elif places==2:
			clockData[dataName+'Tens'] = value/10
			clockData[dataName+'Units'] = value%10
			clockData[dataName] = value
		elif places==1:
			if dataName=='0' or dataName=='':
				pass
			else:
				clockData[dataName] = value
		else:
			print 'Failed to set %s %s value of %d.' % (clockName, dataName, value)

	def modPlayerData(self, team, player, dataName, modulusValue=100, operator = '+', modValue = 1, places=2):
		playerData = self.teamsDict[team].playersDict[player].playerData
		if dataName!='playerNumber':
			if operator=='+':
				playerData[dataName] = (playerData[dataName] + modValue) % modulusValue
			elif operator=='-':
				playerData[dataName] = (playerData[dataName] - modValue) % modulusValue
			elif operator=='*':
				playerData[dataName] = (playerData[dataName] * modValue) % modulusValue
			elif operator=='/':
				playerData[dataName] = (playerData[dataName] / modValue) % modulusValue
			elif operator=='toggle':
				playerData[dataName] = toggle(playerData[dataName])
				places=0
			if places==3:
				playerData[dataName+'Hundreds'] = playerData[dataName]/100
				playerData[dataName+'Tens'] = playerData[dataName]/10%10
				playerData[dataName+'Units'] = playerData[dataName]%10
			elif places==2:
				playerData[dataName+'Tens'] = playerData[dataName]/10
				playerData[dataName+'Units'] = playerData[dataName]%10

	def modTeamData(self, team, dataName, modulusValue=100, operator = '+', modValue = 1, places=2):
		teamData = self.teamsDict[team].teamData
		if operator=='+':
			teamData[dataName] = (teamData[dataName] + modValue) % modulusValue
		elif operator=='-':
			teamData[dataName] = (teamData[dataName] - modValue) % modulusValue
		elif operator=='*':
			teamData[dataName] = (teamData[dataName] * modValue) % modulusValue
		elif operator=='/':
			teamData[dataName] = (teamData[dataName] / modValue) % modulusValue
		elif operator=='toggle':
			teamData[dataName] = toggle(teamData[dataName])
			places=0
		if places==3:
			teamData[dataName+'Hundreds'] = teamData[dataName]/100
			teamData[dataName+'Tens'] = teamData[dataName]/10%10
			teamData[dataName+'Units'] = teamData[dataName]%10
		elif places==2:
			teamData[dataName+'Tens'] = teamData[dataName]/10
			teamData[dataName+'Units'] = teamData[dataName]%10

	def modGameData(self, dataName, modulusValue=100, operator = '+', modValue = 1, places=2):
		if operator=='+':
			self.gameData[dataName] = (self.gameData[dataName] + modValue) % modulusValue
		elif operator=='-':
			self.gameData[dataName] = (self.gameData[dataName] - modValue) % modulusValue
		elif operator=='*':
			self.gameData[dataName] = (self.gameData[dataName] * modValue) % modulusValue
		elif operator=='/':
			self.gameData[dataName] = (self.gameData[dataName] / modValue) % modulusValue
		elif operator=='toggle':
			self.gameData[dataName] = toggle(self.gameData[dataName])
			places=0
		if places==3:
			self.gameData[dataName+'Hundreds'] = self.gameData[dataName]/100
			self.gameData[dataName+'Tens'] = self.gameData[dataName]/10%10
			self.gameData[dataName+'Units'] = self.gameData[dataName]%10
		elif places==2:
			self.gameData[dataName+'Tens'] = self.gameData[dataName]/10
			self.gameData[dataName+'Units'] = self.gameData[dataName]%10

	def modClockData(self, clockName, dataName, operator = '+', modulusValue=60, modValue = 1, places=2):

		clockData = self.clockDict[clockName].timeUnitsDict
		if operator=='+':
			clockData[dataName] = (clockData[dataName] + modValue) % modulusValue
		elif operator=='-':
			clockData[dataName] = (clockData[dataName] - modValue) % modulusValue
		elif operator=='*':
			clockData[dataName] = (clockData[dataName] * modValue) % modulusValue
		elif operator=='/':
			clockData[dataName] = (clockData[dataName] / modValue) % modulusValue
		elif operator=='toggle':
			clockData[dataName] = toggle(clockData[dataName])
			places=0
		if places==3:
			clockData[dataName+'Hundreds'] = clockData[dataName]/100
			clockData[dataName+'Tens'] = clockData[dataName]/10%10
			clockData[dataName+'Units'] = clockData[dataName]%10
		elif places==2:
			clockData[dataName+'Tens'] = clockData[dataName]/10
			clockData[dataName+'Units'] = clockData[dataName]%10

	#Keypad Functions

	#GENERIC FUNCTIONS----------------------------------------

	def handheldButton1(self):
		self.clockDict['delayOfGameClock'].Reset(self.gameSettings['delayOfGameMaxSeconds1'])

	def handheldButton2(self):
		self.clockDict['delayOfGameClock'].Reset(self.gameSettings['delayOfGameMaxSeconds2'])

	def handheldButton3(self):
		if self.clockDict['delayOfGameClock'].running:
			self.clockDict['delayOfGameClock'].Stop()
		else:
			self.clockDict['delayOfGameClock'].Start()

	def guestScorePlusTen(self):
		team=self.guest
		self.modTeamData(team, dataName='score', operator = '+', modulusValue=100, modValue = 10)

	def guestScorePlusOne(self):
		if not self.gameSettings['menuFlag']:
			team=self.guest
			dataName='score'
			if self.gameSettings['scoreTo19Flag']:
				self.modTeamData(team, dataName, operator = '+', modulusValue=20, modValue = 1)
			elif self.gameData['sport']=='MPBASKETBALL1' or self.gameData['sport']=='MPHOCKEY_LX1' or self.gameData['sport']=='MPHOCKEY1':
				self.modTeamData(team, dataName, operator = '+', modulusValue=200, modValue = 1, places=3)
			else:
				self.modTeamData(team, dataName, operator = '+', modulusValue=100, modValue = 1)

	def guestScoreMinusOne(self):
		team=self.guest
		self.modTeamData(team, dataName='score', operator = '-', modulusValue=100, modValue = 1)

	def homeScorePlusTen(self):
		team=self.home
		self.modTeamData(team, dataName='score', operator = '+', modulusValue=100, modValue = 10)

	def homeScorePlusOne(self):
		if not self.gameSettings['menuFlag']:
			team=self.home
			dataName='score'
			if self.gameSettings['scoreTo19Flag']:
				self.modTeamData(team, dataName, operator = '+', modulusValue=20, modValue = 1)
			elif self.gameData['sport']=='MPBASKETBALL1' or self.gameData['sport']=='MPHOCKEY_LX1' or self.gameData['sport']=='MPHOCKEY1':
				self.modTeamData(team, dataName, operator = '+', modulusValue=200, modValue = 1, places=3)
			else:
				self.modTeamData(team, dataName, operator = '+', modulusValue=100, modValue = 1)

	def homeScoreMinusOne(self):
		team=self.home
		self.modTeamData(team, dataName='score', operator = '-', modulusValue=100, modValue = 1)

	def Horn(self):
		if self.gameSettings['periodHornEnable']:
			if self.gameSettings['endOfTimeOutTimerHornEnable'] and self.gameData['sportType']=='football':
				print '\a\aHORN ON'
				self.gameData['periodHorn'] = True
			elif self.gameSettings['endOfPeriodHornEnable']:
				print '\a\aHORN ON'
				self.gameData['periodHorn'] = True
			if self.gameSettings['visualHornEnable']:
				self.gameData['visualHornIndicator1']=True
				print 'VISUAL HORN ON'
				if self.gameData['sportType']=='basketball' or self.gameData['sportType']=='hockey':
					self.gameData['visualHornIndicator2']=True
			threading.Timer(self.gameSettings['periodHornFlashDuration'], self.hornOff).start()

	def shotHorn(self):
		if self.gameSettings['shotClockHornEnable']:
			if self.gameSettings['endOfShotClockHornEnable']:
				print '\a\aSHOT CLOCK HORN ON'
				self.gameData['shotClockHorn'] = True
			threading.Timer(self.gameSettings['shotClockHornFlashDuration'], self.shotHornOff).start()

	def delayOfGameHorn(self):
		if self.gameSettings['delayOfGameHornEnable']:
			print '\a\aDELAY OF GAME CLOCK HORN ON'
			self.gameData['delayOfGameHorn'] = True
			threading.Timer(self.gameSettings['delayOfGameHornFlashDuration'], self.delayOfGameHornOff).start()

	def hornOff(self):
		print '\aHORNS OFF'
		self.gameData['periodHorn'] = False
		self.gameData['visualHornIndicator1']=False
		if self.gameData['sportType']=='basketball':
			self.gameData['visualHornIndicator2']=False

	def shotHornOff(self):
		print '\aSHOT CLOCK HORN OFF'
		self.gameData['shotClockHorn'] = False

	def delayOfGameHornOff(self):
		print '\aDELAY OF GAME CLOCK HORN OFF'
		self.gameData['delayOfGameHorn'] = False

	def periodClockOnOff(self):
		if self.gameSettings['segmentTimerEnable']:
			clockName='segmentTimer'
		elif self.gameSettings['timeOutTimerEnable']:
			self.gameSettings['timeOutTimerEnable']=False
			clockName='timeOutTimer'
			self.clockDict[clockName].Stop()
			self.clockDict[clockName].Reset()
			clockName='periodClock'
		else:
			clockName='periodClock'

		if self.gameSettings['precisionEnable'] or self.gameSettings['lampTestFlag'] or self.gameSettings['blankTestFlag']:
			print 'periodClockOnOff button not active'
			return

		else:
			if not self.clockDict[clockName].running:
				self.clockDict[clockName].Start()
				if self.gameData['sport']=='MPBASKETBALL1' or self.gameData['sportType']=='hockey':
					self.clockDict['shotClock'].Start()
					if self.gameData['sportType']=='hockey':
						for clockName in self.clockDict.keys():
							if clockName[:7]=='penalty':
								self.clockDict[clockName].Start()
			else:
				self.clockDict[clockName].Stop()
				if self.gameData['sport']=='MPBASKETBALL1' or self.gameData['sportType']=='hockey':
					self.clockDict['shotClock'].Stop()
					if self.gameData['sportType']=='hockey':
							for clockName in self.clockDict.keys():
								if clockName[:7]=='penalty':
									self.clockDict[clockName].Stop()

	def minutesMinusOne(self):
		if not self.clockDict['periodClock'].running:
			if self.clockDict['periodClock'].currentTime<=60: # don't allow negative time
				self.clockDict['periodClock'].changeSeconds(-self.clockDict['periodClock'].currentTime)
			else:
				self.clockDict['periodClock'].changeSeconds(-60)

	def secondsMinusOne(self):
		if not self.clockDict['periodClock'].running:
			if self.clockDict['periodClock'].currentTime<=1: # don't allow negative time
				self.clockDict['periodClock'].changeSeconds(-self.clockDict['periodClock'].currentTime)
			else:
				self.clockDict['periodClock'].changeSeconds(-1)

	def secondsPlusOne(self):
		if not self.clockDict['periodClock'].running:
			self.clockDict['periodClock'].changeSeconds(1)

	def quartersPlusOne(self):
		modulusValue=(self.gameSettings['quarterMax']+1)
		self.modGameData(dataName='quarter', modulusValue=modulusValue, modValue = 1, places=1, operator = '+')

	def periodsPlusOne(self):
		modulusValue=(self.gameSettings['periodMax']+1)
		self.modGameData(dataName='period', modulusValue=modulusValue, modValue = 1, places=1, operator = '+')

	def possession(self):
		guestP = self.getTeamData(self.guest, 'possession')
		homeP = self.getTeamData(self.home, 'possession')
		#print 'guestP', guestP, 'homeP', homeP
		if guestP==False and homeP==False:
			self.setTeamData(self.guest, 'possession', True, places=1)
		else:
			self.modTeamData(self.home, 'possession', operator = 'toggle')
			self.modTeamData(self.guest, 'possession', operator = 'toggle')

	def numberPressed(self, key):
		pass

	def Number_7_ABC(self):
		key=7
		self.numberPressed(key)

	def Number_8_DEF(self):
		key=8
		self.numberPressed(key)

	def Number_9_GHI(self):
		key=9
		self.numberPressed(key)

	def Number_4_JKL(self):
		key=4
		self.numberPressed(key)

	def Number_5_MNO(self):
		key=5
		self.numberPressed(key)

	def Number_6_PQR(self):
		key=6
		self.numberPressed(key)

	def Number_1_STU(self):
		key=1
		self.numberPressed(key)

	def Number_2_VWX(self):
		key=2
		self.numberPressed(key)

	def Number_3_YZ(self):
		key=3
		self.numberPressed(key)

	def Number_0(self):
		key=0
		self.numberPressed(key)

	def clear_(self):
		pass

	def enter_(self):
		pass

	def setGuestScore(self):
		pass

	def setHomeScore(self):
		pass

	def setGuestFunctions(self):
		pass

	def setHomeFunctions(self):
		pass

	def shotClocks(self):
		pass

	def setClock(self):
		pass

	def playClocks(self):
		pass

	def setClockTenthSec(self):
		pass

	def tenthSecOnOff(self):
		pass

	def clockUpDown(self):
		pass

	def autoHorn(self):
		pass

	def timeOfDay(self):
		pass

	def timeOutTimer(self):
		pass

	def NewGame(self):
		pass

	def blank(self):
		pass

	def periodClockReset(self):
		pass

	#END OF GENERIC FUNCTIONS-----------
	#BASEBALL FUNCTIONS----------------------------------------

	def clear_FlashHit(self):
		if self.gameSettings['menuFlag'] or self.gameSettings['hitIndicatorFlashOn'] == True:
			pass
		else:
			self.gameSettings['hitIndicatorFlashOn'] = True
			self.hitCount=self.gameSettings['hitIndicatorFlashCount']
			self.hitToggle()

	def enter_FlashError(self):
		if self.gameSettings['menuFlag'] or self.gameSettings['errorIndicatorFlashOn'] == True:
			pass
		else:
			self.gameSettings['errorIndicatorFlashOn'] = True
			self.errorCount=self.gameSettings['errorIndicatorFlashCount']
			self.errorToggle()

	def hitToggle(self):
		self.hitCount-=1
		if self.hitCount<=0:
			self.gameSettings['hitIndicatorFlashOn'] = False
			self.gameData['hitIndicator']=False
		else:
			self.modGameData('hitIndicator', operator='toggle')
			threading.Timer(self.gameSettings['hitFlashDuration'], self.hitToggle).start()

	def errorToggle(self):
		self.errorCount-=1
		if self.errorCount<=0:
			self.gameSettings['errorIndicatorFlashOn'] = False
			self.gameData['errorIndicator']=False
		else:
			self.modGameData('errorIndicator', operator='toggle')
			threading.Timer(self.gameSettings['errorFlashDuration'], self.errorToggle).start()

	def hitsPlusOne(self):
		if self.gameSettings['inningBot']:
			team=self.home
		else:
			team=self.guest
		dataName = 'hits'
		self.modTeamData(team, dataName)
		self.clear_FlashHit()

	def errorsPlusOne(self):
		if self.gameSettings['inningBot']:
			team=self.guest
		else:
			team=self.home
		dataName = 'errors'
		self.modTeamData(team, dataName)
		self.enter_FlashError()

	def setSinglePitchCount(self, team):
		dataNameSPC = 'singlePitchCount'
		dataName='pitchCount'
		SPC = self.getTeamData(team, dataName)
		self.setGameData(dataNameSPC, SPC, places=3)

	def setSinglePitchCountFromMenu(self):
		if self.gameData['sportType']=='baseball':
			dataName='atBatIndicator'
			guestP = self.getTeamData(self.guest, dataName)
			homeP = self.getTeamData(self.home, dataName)
			if not guestP and not homeP:
				team=self.guest
			else:
				if guestP:
					team=self.home
				if homeP:
					team=self.guest
		elif self.gameData['sportType']=='linescore':
			if self.gameSettings['linescoreStart']:
				team=self.guest
			elif self.gameSettings['inningBot']:
				team=self.guest
			else:
				team=self.home
		self.setSinglePitchCount(team)

	def teamAtBat(self):
		dataName='atBatIndicator'
		guestP = self.getTeamData(self.guest, dataName)
		homeP = self.getTeamData(self.home, dataName)
		if not guestP and not homeP:
			team=self.home
			self.setTeamData(self.guest, dataName, True, places=1)
		else:
			if guestP:
				team=self.guest
			if homeP:
				team=self.home
			self.modTeamData(self.home, dataName, operator = 'toggle')
			self.modTeamData(self.guest, dataName, operator = 'toggle')
		self.setSinglePitchCount(team)

	def singlePitchesPlusOne(self):
		if self.gameSettings['inningBot']:
			self.guestPitchesPlusOne()
			team=self.guest
		else:
			self.homePitchesPlusOne()
			team=self.home
		self.setSinglePitchCount(team)

	def guestPitchesPlusOne(self):
		team=self.guest
		dataName = 'pitchCount'
		self.modTeamData(team, dataName, modulusValue=200, places=3)
		dataName='atBatIndicator'
		guestP = self.getTeamData(self.guest, dataName)
		homeP = self.getTeamData(self.home, dataName)
		if not guestP:
			self.setSinglePitchCount(team)

	def homePitchesPlusOne(self):
		team=self.home
		dataName = 'pitchCount'
		self.modTeamData(team, dataName, modulusValue=200, places=3)
		dataName='atBatIndicator'
		guestP = self.getTeamData(self.guest, dataName)
		if guestP:
			self.setSinglePitchCount(team)

	def inningsPlusOne(self):
		dataName = 'inning'
		self.modGameData(dataName, modulusValue=20)

	def ballsPlusOne(self):
		dataName = 'balls'
		modulusValue=self.gameSettings['ballsMax']+1
		self.modGameData(dataName, modulusValue, places=1)

	def strikesPlusOne(self):
		dataName = 'strikes'
		modulusValue=self.gameSettings['strikesMax']+1
		self.modGameData(dataName, modulusValue, places=1)

	def outsPlusOne(self):
		dataName = 'outs'
		modulusValue=self.gameSettings['outsMax']+1
		self.modGameData(dataName, modulusValue, places=1)

	def incInningTop_Bot(self):
		inn=self.getGameData('inning')
		if self.gameSettings['linescoreStart']:
			self.gameSettings['linescoreStart']=False
			self.gameSettings['inningBot']=False
			self.gameData['inning'] = 1
			team=self.home
			self.setSinglePitchCount(team)
		elif self.gameSettings['inningBot']:
			self.gameSettings['inningBot']=False
			self.inningsPlusOne()
			team=self.home
			if inn<=10 and inn!=0:
				dataName = 'scoreInn'+str(inn)
				if self.getTeamData(team, dataName)==255:
					self.setTeamData(team, dataName, value=0, places=1)
			self.setSinglePitchCount(team)
		else:
			self.gameSettings['inningBot']=True
			if inn<=10 and inn!=0:
				team=self.guest
				dataName = 'scoreInn'+str(inn)
				if self.getTeamData(team, dataName)==255:
					self.setTeamData(team, dataName, value=0, places=1)
			team=self.guest
			self.setSinglePitchCount(team)

	def runsPlusOne(self):
		inn=self.getGameData('inning')
		if self.gameSettings['linescoreStart']:
			if self.gameSettings['inningBot']:
				team=self.guest
			else:
				team=self.home
			dataName = 'score'
			self.modTeamData(team, dataName)
		else:
			if self.gameSettings['inningBot']:
				team=self.home
				dataName = 'score'
				self.modTeamData(team, dataName)
			else:
				team=self.guest
				dataName = 'score'
				self.modTeamData(team, dataName)
			if inn<=10 and inn!=0:
				dataName = 'scoreInn'+str(inn)
				if self.getTeamData(team, dataName)==255:
					self.setTeamData(team, dataName, value=0, places=1)
				self.modTeamData(team, dataName, modulusValue=10, places=1)

	def assignError(self):
		pass

	def setPitchCounts(self):
		pass

	def setBatterNumber(self):
		pass

	def setTotalRuns(self):
		pass

	def setTotalHits(self):
		pass

	def setTotalErrors(self):
		pass

	def setRuns_Innings(self):
		pass

	def setInningTop_Bot(self):
		pass

	#END OF BASEBALL FUNCTIONS-----------
	#FOOTBALL FUNCTIONS----------------------------------------

	def guestTimeOutsMinusOne(self):
		pass

	def homeTimeOutsMinusOne(self):
		pass

	def downsPlusOne(self):
		self.modGameData('down', modulusValue=5, places=1)

	def yardsToGoMinusTen(self):
		if self.gameData['yardsToGo']<=10:
			self.setGameData('yardsToGo', 0)
		else:
			self.modGameData('yardsToGo', operator='-', modValue=10)

	def yardsToGoMinusOne(self):
		if self.gameData['yardsToGo']<=1:
			self.setGameData('yardsToGo', 0)
		else:
			self.modGameData('yardsToGo', operator='-', modValue=1)

	def yardsToGoReset(self):
		pass

	def setGuestTimeOuts(self):
		pass

	def setHomeTimeOuts(self):
		pass

	def setYardsToGo(self):
		pass

	def setBallOn(self):
		pass

	#END OF FOOTBALL FUNCTIONS-----------
	#SOCCER FUNCTIONS----------------------------------------

	def clear_GuestGoal(self):
		if self.gameSettings['menuFlag']:
			pass
		else:
			team=self.guest
			self.modTeamData(team, 'goalIndicator', operator = 'toggle')
		return

	def enter_HomeGoal(self):
		if self.gameSettings['menuFlag']:
			pass
		else:
			team=self.home
			self.modTeamData(team, 'goalIndicator', operator = 'toggle')
		return

	def guestPenaltyPlusOne(self):
		team=self.guest
		self.modTeamData(team, 'penaltyCount', modulusValue=10, places=1)
		return

	def homePenaltyPlusOne(self):
		team=self.home
		self.modTeamData(team, 'penaltyCount', modulusValue=10, places=1)
		return

	def guestShotsPlusOne(self):
		team=self.guest
		self.modTeamData(team, 'shots')
		return

	def homeShotsPlusOne(self):
		team=self.home
		self.modTeamData(team, 'shots')
		return

	def guestKicksPlusOne(self):
		team=self.guest
		self.modTeamData(team, 'kicks')
		return

	def homeKicksPlusOne(self):
		team=self.home
		self.modTeamData(team, 'kicks')
		return

	def guestSavesPlusOne(self):
		team=self.guest
		self.modTeamData(team, 'saves')
		return

	def homeSavesPlusOne(self):
		team=self.home
		self.modTeamData(team, 'saves')
		return

	#END OF SOCCER FUNCTIONS-----------
	#HOCKEY FUNCTIONS----------------------------------------

	def guestPenalty(self):
		return

	def homePenalty(self):
		return

	#END OF HOCKEY FUNCTIONS-----------
	#BASKETBALL FUNCTIONS----------------------------------------

	def guestTeamFoulsPlusOne(self):
		team=self.guest
		modulusValue=self.gameSettings['FoulsMax']+1
		self.modTeamData(team, 'fouls', modulusValue, operator='+', places=2)
		return

	def homeTeamFoulsPlusOne(self):
		team=self.home
		modulusValue=self.gameSettings['FoulsMax']+1
		self.modTeamData(team, 'fouls', modulusValue, operator='+', places=2)
		return

	def guestBonusPlusOne(self):
		team=self.guest
		modulusValue=3
		self.modTeamData(team, 'bonus', modulusValue, operator='+', places=1)
		return

	def homeBonusPlusOne(self):
		team=self.home
		modulusValue=3
		self.modTeamData(team, 'bonus', modulusValue, operator='+', places=1)
		return

	def playerMatchGame(self):
		return

	def playerFoul(self):
		return

	#END OF BASKETBALL FUNCTIONS-----------
	#CRICKET FUNCTIONS----------------------------------------

	def oversPlusOne(self):
		self.gameData['overs'] = (self.gameData['overs'] + 1) % 100
		return

	def player1ScorePlusOne(self):
		self.gameData['player1Score'] = (self.gameData['player1Score'] + 1) % 200
		return

	def player2ScorePlusOne(self):
		self.gameData['player2Score'] = (self.gameData['player2Score'] + 1) % 200
		return

	def wicketsPlusOne(self):
		self.gameData['wickets'] = (self.gameData['wickets'] + 1) % 10
		return

	def setPlayer1Number(self):
		return

	def setPlayer2Number(self):
		return

	def setPlayer1Score(self):
		return

	def setPlayer2Score(self):
		return

	def setTotalScore(self):
		return

	def setOvers(self):
		return

	def setLastMan(self):
		return

	def setLastWicket(self):
		return

	def set1eInnings(self):
		return

	#END OF CRICKET FUNCTIONS-----------
	#RACETRACK FUNCTIONS----------------------------------------

	#END OF RACETRACK FUNCTIONS-----------
	#STAT FUNCTIONS----------------------------------------

	def fouls_digsMinusOne(self):
		activePlayerList, team, teamName=activePlayerListSelect(self)
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber']!='  ':
			playerID=self.getPlayerData(team, 'playerNumber', playerNumber=self.gameSettings['playerNumber'])
			self.modPlayerData(team, playerID, 'fouls', operator='-')
			modulusValue=self.gameSettings['FoulsMax']+1
			self.modTeamData(team, 'fouls', modulusValue, operator='-', places=2)
		return

	def fouls_digsPlusOne(self):
		activePlayerList, team, teamName=activePlayerListSelect(self)
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber']!='  ':
			playerID=self.getPlayerData(team, 'playerNumber', playerNumber=self.gameSettings['playerNumber'])
			self.modPlayerData(team, playerID, 'fouls', operator='+')
			modulusValue=self.gameSettings['FoulsMax']+1
			self.modTeamData(team, 'fouls', modulusValue, operator='+', places=2)
		return

	def guest_homeSwitch(self):
		self.gameSettings['currentTeamGuest']= not self.gameSettings['currentTeamGuest']
		if self.gameSettings['currentTeamGuest']:
			activePlayerList=self.activeGuestPlayerList
		else:
			activePlayerList=self.activeHomePlayerList
		if len(activePlayerList)==0:
			statIndex=0
		else:
			statIndex=1
		self.gameSettings['statNumber']=self.statNumberList[statIndex]
		return

	def points_killsMinusOne(self):
		activePlayerList, team, teamName=activePlayerListSelect(self)
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber']!='  ':
			playerID=self.getPlayerData(team, 'playerNumber', playerNumber=self.gameSettings['playerNumber'])
			self.modPlayerData(team, playerID, 'points', operator='-')
			modulusValue=200
			self.modTeamData(team, 'score', modulusValue, operator = '-', places=3)
		return

	def points_killsPlusOne(self):
		activePlayerList, team, teamName=activePlayerListSelect(self)
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber']!='  ':
			playerID=self.getPlayerData(team, 'playerNumber', playerNumber=self.gameSettings['playerNumber'])
			self.modPlayerData(team, playerID, 'points', operator='+')
			modulusValue=200
			self.modTeamData(team, 'score', modulusValue, operator = '+', places=3)
		return

	def nextPlayer(self):
		activePlayerList, team, teamName=activePlayerListSelect(self)
		notActiveList=[]
		for playerID in self.teamsDict[team].playersDict.keys():
			playerNumber=self.getPlayerData(team, 'playerNumber', playerID=playerID)
			playerActive=self.getPlayerData(team, 'playerActive', playerID=playerID)
			if playerNumber!='  ' and not playerActive:
				notActiveList.append(playerNumber)
		print 'notActiveList', notActiveList
		notActiveList.sort()
		print 'notActiveList', notActiveList

		activeIndex=self.statNumberList.index(self.gameSettings['statNumber'])
		print 'activeIndex', activeIndex, 'self.notActiveIndex', self.notActiveIndex
		print 'len(notActiveList)', len(notActiveList),'len(activePlayerList)', len(activePlayerList)
		print 'statNumber', self.gameSettings['statNumber']

		#Enter index governed list choosing area
		if activeIndex and self.notActiveIndex is not None:
			if activeIndex>=len(activePlayerList):
				self.notActiveIndex=0
				print 1
				print 'activeIndex', activeIndex, 'self.notActiveIndex', self.notActiveIndex
				print 'len(notActiveList)', len(notActiveList),'len(activePlayerList)', len(activePlayerList)
				print 'statNumber', self.gameSettings['statNumber']
				self.gameSettings['statNumber']=self.statNumberList[0]
				self.gameSettings['playerNumber']=notActiveList[self.notActiveIndex]
				print 'statNumber', self.gameSettings['statNumber']
				print 'playerNumber', self.gameSettings['playerNumber']
			else:
				print 2
				print 'activeIndex', activeIndex, 'self.notActiveIndex', self.notActiveIndex
				print 'len(notActiveList)', len(notActiveList),'len(activePlayerList)', len(activePlayerList)
				print 'statNumber', self.gameSettings['statNumber']
				self.gameSettings['statNumber']=self.statNumberList[activeIndex+1]
				self.gameSettings['playerNumber']=activePlayerList[activeIndex]
				print 'statNumber', self.gameSettings['statNumber']
				print 'playerNumber', self.gameSettings['playerNumber']
		elif activeIndex:
			if activeIndex>=len(activePlayerList):
				print 3
				print 'activeIndex', activeIndex, 'self.notActiveIndex', self.notActiveIndex
				print 'len(notActiveList)', len(notActiveList),'len(activePlayerList)', len(activePlayerList)
				print 'statNumber', self.gameSettings['statNumber']
				self.gameSettings['statNumber']=self.statNumberList[1]
				self.gameSettings['playerNumber']=activePlayerList[0]
				print 'statNumber', self.gameSettings['statNumber']
				print 'playerNumber', self.gameSettings['playerNumber']
			else:
				print 4
				print 'activeIndex', activeIndex, 'self.notActiveIndex', self.notActiveIndex
				print 'len(notActiveList)', len(notActiveList),'len(activePlayerList)', len(activePlayerList)
				print 'statNumber', self.gameSettings['statNumber']
				self.gameSettings['statNumber']=self.statNumberList[activeIndex+1]
				self.gameSettings['playerNumber']=activePlayerList[activeIndex]
				print 'statNumber', self.gameSettings['statNumber']
				print 'playerNumber', self.gameSettings['playerNumber']
		elif self.notActiveIndex is not None:
			if self.notActiveIndex+1>=len(notActiveList):
				print 5
				self.notActiveIndex=0
				print 'activeIndex', activeIndex, 'self.notActiveIndex', self.notActiveIndex
				print 'len(notActiveList)', len(notActiveList),'len(activePlayerList)', len(activePlayerList)
				print 'statNumber', self.gameSettings['statNumber']
				if len(activePlayerList):
					returnToActive=1
					self.gameSettings['playerNumber']=activePlayerList[activeIndex]
				else:
					returnToActive=0
					self.gameSettings['playerNumber']=notActiveList[self.notActiveIndex]
				self.gameSettings['statNumber']=self.statNumberList[returnToActive]
				print 'statNumber', self.gameSettings['statNumber']
				print 'playerNumber', self.gameSettings['playerNumber']
			else:
				print 6
				self.notActiveIndex+=1
				print 'activeIndex', activeIndex, 'self.notActiveIndex', self.notActiveIndex
				print 'len(notActiveList)', len(notActiveList),'len(activePlayerList)', len(activePlayerList)
				print 'statNumber', self.gameSettings['statNumber']
				self.gameSettings['statNumber']=self.statNumberList[0]
				self.gameSettings['playerNumber']=notActiveList[self.notActiveIndex]
				print 'statNumber', self.gameSettings['statNumber']
				print 'playerNumber', self.gameSettings['playerNumber']
		else:
			print 'No players in roster'
		return

	def previousPlayer(self):
		activePlayerList, team, teamName=activePlayerListSelect(self)

		index=self.statNumberList.index(self.gameSettings['statNumber'])
		if len(activePlayerList):
			if index==1:
				print 'end', len(activePlayerList), index
				self.gameSettings['statNumber']=self.statNumberList[len(activePlayerList)]
				self.gameSettings['playerNumber']=activePlayerList[len(activePlayerList)-1]
			else:
				print 'previous', len(activePlayerList), index
				self.gameSettings['statNumber']=self.statNumberList[index-1]
				self.gameSettings['playerNumber']=activePlayerList[index-2]
		else:
			pass
		return

	def subPlayer(self):
		return

	def addPlayer(self):
		return

	def deletePlayer(self):
		return

	def displaySize(self):
		return

	def editPlayer(self):
		return

	#END OF STAT FUNCTIONS-----------

class Baseball(Game):
	def __init__(self, numberOfTeams=2):
		super(Baseball, self).__init__(numberOfTeams)

		self.gameData['sportType']="baseball"
		if self.gameSettings['hoursFlagJumper']:
			self.gameSettings['hoursFlag']=True
		if self.gameData['sport']=='MPLINESCORE4' or self.gameData['sport']=='MPLINESCORE5' or self.gameData['sport']=='MPMP-15X1' or self.gameData['sport']=='MPMP-14X1':
			self.gameData['sportType']='linescore'
			self.gameSettings['hoursFlag']=True

		if self.configDict['keypadType']=='MM':
			self.gameSettings['baseballPeriodClockMaxSeconds'] = self.gameSettings['MM_baseballPeriodClockMaxSeconds']
		elif self.configDict['keypadType']=='MP':
			self.gameSettings['baseballPeriodClockMaxSeconds'] = self.gameSettings['MP_baseballPeriodClockMaxSeconds']

		homePC = self.getTeamData(self.home, 'pitchCount')
		self.setGameData('singlePitchCount', homePC, places=3)
		self.setGameData('inning', self.getGameData('inning'))

		if self.gameData['outs']>=2:
			self.gameData['outs1'] = True
			self.gameData['outs2'] = True
		elif self.gameData['outs']==1:
			self.gameData['outs1'] = True
			self.gameData['outs2'] = False
		else:
			self.gameData['outs1'] = False
			self.gameData['outs2'] = False

		self.setGameData('pitchSpeed', self.getGameData('pitchSpeed'), places=3)
		self.setGameData('batterNumber', self.getGameData('batterNumber'))

		self.gameSettings['errorIndicatorFlashOn']=False
		self.gameSettings['hitIndicatorFlashOn']=False

		self._createTeams()

		self._addTeamNameData()

		self.clockDict['shotClock']=clock(False, self.gameSettings['shotClockMaxSeconds1'], clockName='shotClock')
		self.gameData = self.clockDict['shotClock'].gameDataUpdate(self.gameData, 'shotClock')
		self.clockDict['delayOfGameClock']=clock(False, self.gameSettings['delayOfGameMaxSeconds1'], clockName='delayOfGameClock')
		self.gameData = self.clockDict['delayOfGameClock'].gameDataUpdate(self.gameData, 'delayOfGameClock')
		self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], self.gameSettings['baseballPeriodClockMaxSeconds'], \
		self.gameSettings['periodClockResolution'], self.gameSettings['hoursFlag'], clockName='periodClock')	
		self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData)	
		self.clockList=self.clockDict.keys()

	def periodClockReset(self):
		if not self.gameSettings['menuFlag']:
			if not self.clockDict['periodClock'].running:
				self.gameSettings['periodClockResetFlag']=True
				perMax=self.gameSettings['baseballPeriodClockMaxSeconds']
				if self.clockDict['periodClock'].currentTime>=(90*60):
					self.clockDict['periodClock'].Reset(perMax)
				elif self.clockDict['periodClock'].currentTime>=(60*60):
					self.clockDict['periodClock'].Reset(90*60)
				elif self.clockDict['periodClock'].currentTime>=(30*60):
					self.clockDict['periodClock'].Reset(60*60)
				elif self.clockDict['periodClock'].currentTime>=(15*60):
					self.clockDict['periodClock'].Reset(30*60)
				elif self.clockDict['periodClock'].currentTime>=perMax:
					self.clockDict['periodClock'].Reset(15*60)
				elif self.clockDict['periodClock'].currentTime<perMax:
					self.clockDict['periodClock'].Reset(perMax)

class Football(Game):
	def __init__(self, numberOfTeams=2):
		super(Football, self).__init__(numberOfTeams)

		self.gameData['sportType'] = 'football'

		if self.configDict['keypadType']=='MM':
			self.gameSettings['footballPeriodClockMaxSeconds'] = self.gameSettings['MM_footballPeriodClockMaxSeconds']
		elif self.configDict['keypadType']=='MP':
			self.gameSettings['footballPeriodClockMaxSeconds'] = self.gameSettings['MP_footballPeriodClockMaxSeconds']

		if self.gameData['quarter']==4:
			self.gameData['quarter4'] = True
		else:
			self.gameData['quarter4'] = False

		self.setGameData('yardsToGo', self.gameData['yardsToGo'])
		self.setGameData('ballOn', self.gameData['ballOn'])

		self._createTeams()

		self._addTeamNameData()
		
		self.clockDict['delayOfGameClock']=clock(False, self.gameSettings['delayOfGameMaxSeconds1'], clockName='delayOfGameClock')
		self.gameData = self.clockDict['delayOfGameClock'].gameDataUpdate(self.gameData, name='delayOfGameClock')
		self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], self.gameSettings['footballPeriodClockMaxSeconds'], self.gameSettings['periodClockResolution'], clockName='periodClock')
		self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData, name='periodClock')
		self.clockList=self.clockDict.keys()

	def periodClockReset(self):
		if not self.gameSettings['menuFlag']:
			if not self.clockDict['periodClock'].running:
				self.gameSettings['periodClockResetFlag']=True
				perMax=self.gameSettings['footballPeriodClockMaxSeconds']
				if self.clockDict['periodClock'].currentTime>=(90*60):
					self.clockDict['periodClock'].Reset(perMax)
				elif self.clockDict['periodClock'].currentTime>=(60*60):
					self.clockDict['periodClock'].Reset(90*60)
				elif self.clockDict['periodClock'].currentTime>=(30*60):
					self.clockDict['periodClock'].Reset(60*60)
				elif self.clockDict['periodClock'].currentTime>=(15*60):
					self.clockDict['periodClock'].Reset(30*60)
				elif self.clockDict['periodClock'].currentTime>=perMax:
					self.clockDict['periodClock'].Reset(15*60)
				elif self.clockDict['periodClock'].currentTime<perMax:
					self.clockDict['periodClock'].Reset(perMax)

	def guestTimeOutsMinusOne(self):
		team=self.guest
		modulusValue=self.gameSettings['TOLMaxFB']+1
		self.modTeamData(team, 'timeOutsLeft', modulusValue, operator='-', places=1)

	def homeTimeOutsMinusOne(self):
		team=self.home
		modulusValue=self.gameSettings['TOLMaxFB']+1
		self.modTeamData(team, 'timeOutsLeft', modulusValue, operator='-', places=1)

class Soccer(Game):
	def __init__(self, numberOfTeams=2):
		super(Soccer, self).__init__(numberOfTeams)

		self.gameData['sportType']='soccer'

		self._createTeams()

		self._addTeamNameData()
		
		self.clockDict['delayOfGameClock']=clock(False, self.gameSettings['delayOfGameMaxSeconds1'], clockName='periodClock')
		self.gameData = self.clockDict['delayOfGameClock'].gameDataUpdate(self.gameData, 'delayOfGameClock')
		self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], self.gameSettings['MP_soccerPeriodClockMaxSeconds'], self.gameSettings['periodClockResolution'], clockName='periodClock')
		self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData, 'periodClock')

		self.clockList=self.clockDict.keys()

class Hockey(Game):
	def __init__(self, numberOfTeams=2):
		super(Hockey, self).__init__(numberOfTeams)

		self.gameData['sportType']='hockey'

		self._createTeams()

		self._addTeamNameData()

		self.clockDict['penalty1_teamOne']=clock(False, 0, clockName='penalty1_teamOne')
		self.gameData = self.clockDict['penalty1_teamOne'].gameDataUpdate(self.gameData, 'penalty1_teamOne')
		self.clockDict['penalty1_teamTwo']=clock(False, 0, clockName='penalty1_teamTwo')
		self.gameData = self.clockDict['penalty1_teamTwo'].gameDataUpdate(self.gameData, 'penalty1_teamTwo')
		self.clockDict['penalty2_teamOne']=clock(False, 0, clockName='penalty2_teamOne')
		self.gameData = self.clockDict['penalty2_teamOne'].gameDataUpdate(self.gameData, 'penalty2_teamOne')
		self.clockDict['penalty2_teamTwo']=clock(False, 0, clockName='penalty2_teamTwo')
		self.gameData = self.clockDict['penalty2_teamTwo'].gameDataUpdate(self.gameData, 'penalty2_teamTwo')
		self.clockDict['penalty3_teamOne']=clock(False, 0, clockName='penalty3_teamOne')
		self.gameData = self.clockDict['penalty3_teamOne'].gameDataUpdate(self.gameData, 'penalty3_teamOne')
		self.clockDict['penalty3_teamTwo']=clock(False, 0, clockName='penalty3_teamTwo')
		self.gameData = self.clockDict['penalty3_teamTwo'].gameDataUpdate(self.gameData, 'penalty3_teamTwo')
		self.clockDict['penalty4_teamOne']=clock(False, 0, clockName='penalty4_teamOne')
		self.gameData = self.clockDict['penalty4_teamOne'].gameDataUpdate(self.gameData, 'penalty4_teamOne')
		self.clockDict['penalty4_teamTwo']=clock(False, 0, clockName='penalty4_teamTwo')
		self.gameData = self.clockDict['penalty4_teamTwo'].gameDataUpdate(self.gameData, 'penalty4_teamTwo')
		self.clockDict['shotClock']=clock(False, self.gameSettings['shotClockMaxSeconds1'], clockName='shotClock')
		self.gameData = self.clockDict['shotClock'].gameDataUpdate(self.gameData, 'shotClock')		
		self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], self.gameSettings['MP_hockeyPeriodClockMaxSeconds'], self.gameSettings['periodClockResolution'], clockName='periodClock')
		self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData, 'periodClock')		
		self.clockList=self.clockDict.keys()

	def handheldButton1(self):
		self.clockDict['shotClock'].Reset(self.gameSettings['shotClockMaxSeconds1'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable']=True

	def handheldButton2(self):
		self.clockDict['shotClock'].Reset(self.gameSettings['shotClockMaxSeconds2'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable']=True

	def handheldButton3(self):
		if self.gameSettings['shotClockBlankEnable']:
			self.gameSettings['shotClockBlankEnable'] = False
		else:
			self.gameSettings['shotClockBlankEnable'] = True
		if self.clockDict['shotClock'].currentTime:
			self.gameSettings['shotClockHornEnable']=False
			self.clockDict['shotClock'].Reset(0)

class Basketball(Game):
	def __init__(self, numberOfTeams=2):
		super(Basketball, self).__init__(numberOfTeams)

		self.gameData['sportType']='basketball'

		self._createTeams()

		self._addTeamNameData()

		if self.configDict['keypadType']=='MM':
			self.basketballPeriodClockMaxSeconds = (self.gameSettings['MM_basketballPeriodClockMaxSeconds'])
		elif self.configDict['keypadType']=='MP':
			self.basketballPeriodClockMaxSeconds = (self.gameSettings['MP_basketballPeriodClockMaxSeconds'])

		self.gameSettings['periodClockTenthsFlag']=True

		self.setGameData('playerNumber', self.gameData['playerNumber'])
		self.setGameData('playerFouls', self.gameData['playerFouls'])
		
		#Order of thread creation sets priority when init same class, last is highest
		self.clockDict['shotClock']=clock(False, self.gameSettings['shotClockMaxSeconds1'], clockName='shotClock')
		self.gameData = self.clockDict['shotClock'].gameDataUpdate(self.gameData, 'shotClock')
		self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], self.basketballPeriodClockMaxSeconds, self.gameSettings['periodClockResolution'], clockName='periodClock')
		self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData, 'periodClock')

		self.clockList=self.clockDict.keys()

	def handheldButton1(self):
		self.clockDict['shotClock'].Reset(self.gameSettings['shotClockMaxSeconds1'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable']=True

	def handheldButton2(self):
		self.clockDict['shotClock'].Reset(self.gameSettings['shotClockMaxSeconds2'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable']=True

	def handheldButton3(self):
		if self.gameSettings['shotClockBlankEnable']:
			self.gameSettings['shotClockBlankEnable'] = False
		else:
			self.gameSettings['shotClockBlankEnable'] = True
		if self.clockDict['shotClock'].currentTime:
			self.gameSettings['shotClockHornEnable']=False
			self.clockDict['shotClock'].Reset(0)

	def periodClockReset(self):
		if not self.gameSettings['menuFlag']:
			if not self.clockDict['periodClock'].running:
				self.gameSettings['periodClockResetFlag']=True
				perMax=self.basketballPeriodClockMaxSeconds
				if self.clockDict['periodClock'].currentTime>=(90*60):
					self.clockDict['periodClock'].Reset(perMax)
				elif self.clockDict['periodClock'].currentTime>=(60*60):
					self.clockDict['periodClock'].Reset(90*60)
				elif self.clockDict['periodClock'].currentTime>=(30*60):
					self.clockDict['periodClock'].Reset(60*60)
				elif self.clockDict['periodClock'].currentTime>=(15*60):
					self.clockDict['periodClock'].Reset(30*60)
				elif self.clockDict['periodClock'].currentTime>=perMax:
					self.clockDict['periodClock'].Reset(15*60)
				elif self.clockDict['periodClock'].currentTime<perMax:
					self.clockDict['periodClock'].Reset(perMax)

	def guestTimeOutsMinusOne(self):
		team=self.guest
		modulusValue=self.gameSettings['TOLMaxBB']+1
		self.modTeamData(team, 'timeOutsLeft', modulusValue, operator='-', places=1)
		return

	def homeTimeOutsMinusOne(self):
		team=self.home
		modulusValue=self.gameSettings['TOLMaxBB']+1
		self.modTeamData(team, 'timeOutsLeft', modulusValue, operator='-', places=1)
		return

class Cricket(Game):
	def __init__(self, numberOfTeams=2):
		super(Cricket, self).__init__(numberOfTeams)

		self.gameData['sportType']='cricket'

		self.gameSettings['MP_cricketPeriodClockMaxSeconds'] = self.gameSettings['MP_cricketPeriodClockMaxSeconds']

		self._createTeams()

		self._addTeamNameData()

		self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], self.gameSettings['MP_cricketPeriodClockMaxSeconds'], self.gameSettings['periodClockResolution'], clockName='periodClock')
		self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData)
		self.clockList=self.clockDict.keys()

class Racetrack(Game):
	def __init__(self, numberOfTeams=2):
		super(Racetrack, self).__init__(numberOfTeams)

		self.gameData['sportType']='racetrack'

		self.MP_racetrackPeriodClockMaxSeconds = (self.gameSettings['MP_racetrackPeriodClockMaxSeconds'])

		self._createTeams()

		self._addTeamNameData()

		self.clockDict['periodClock']=clock(self.gameSettings['periodClockCountUp'], self.gameSettings['MP_racetrackPeriodClockMaxSeconds'], self.gameSettings['periodClockResolution'], clockName='periodClock')
		self.gameData = self.clockDict['periodClock'].gameDataUpdate(self.gameData)
		self.clockList=self.clockDict.keys()

class Stat(Game):
	def __init__(self, numberOfTeams=2):
		super(Stat, self).__init__(numberOfTeams)

		self.gameData['sportType']='stat'

		self._createTeams()

		self._addTeamNameData()

		self.clockList=self.clockDict.keys()

		self.gameSettings['currentTeamGuest']=True
		if self.gameSettings['vollyballFlag']:
			self.maxActive=6
		else:
			self.maxActive=5
		self.statNumberList=[None,'One','Two','Three','Four','Five','Six']
		self.gameSettings['statNumber']=self.statNumberList[0]
		self.gameSettings['playerNumber']='  '
		self.notActiveIndex=None
		self.activeGuestPlayerList=[]
		self.activeHomePlayerList=[]

def test():
	'''Test function if module ran independently.
	Prints object data with printDictsExpanded function.'''
	print "ON"
	sport='MPLINESCORE5'
	game = selectSportInstance(sport)
	time.sleep(4)
	game.KillClockThreads()
	while 1:
		printDictsExpanded(game)

	'''
	print game.getPlayerData('TEAM_1', 'playerNumber', playerID='PLAYER_1', playerNumber='kk')
	game.setPlayerData('TEAM_1', 'PLAYER_1', 'playerNumber', ' 0', places=2)
	print game.getPlayerData('TEAM_1', 'playerNumber', playerID='PLAYER_1', playerNumber='kk')

	while 1:
		#game.homeScorePlusTen()
		#game.homeScorePlusOne()
		#game.guestScorePlusTen()
		#game.guestScorePlusOne()

		game.fouls_digsPlusOne()
		printDict(game.__dict__)
		game.getTeamData(game.home, 'foulOne')
		raw_input('\nPress enter to choose another sport\n')

		game.possession()
		#printDict(game.__dict__)
		#raw_input('\nPress enter to choose another sport\n')

	#attrs = vars(game)
	#print ''.join("%s: %s\n" % item for item in attrs.items())
	'''

if __name__ == '__main__':
	os.chdir('..') 
	'''Added this for csvOneRowRead to work with this structure, 
	add this line for each level below project root'''
	test()
