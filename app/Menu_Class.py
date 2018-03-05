#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
**COMPLETION** = 80%  Sphinx Approved = **True**

.. topic:: Overview

    This module simulates the 16 x 2 LCD screen.
    It is a complicated state machine.

    :Created Date: 3/16/2015
    :Modified Date: 8/31/2016
    :Author: **Craig Gunter**

'''

import threading

from functions import *
from Config import Config

class Menu_Event_Handler(object):
	'''Object that displays information and responds to current events based on past input.'''
	def __init__(self, sport='MPBASEBALL1', splashTime=5, vboseList=[1,0,0]):
		self.vboseList=vboseList
		self.verbose=self.vboseList[0] #Method Name or arguments
		self.verboseMore=self.vboseList[1] #Deeper loop information in methods
		self.verboseMost=self.vboseList[2] #Crazy Deep Stuff

		verbose(['\nCreating Menu_Event_Handler object'], self.verbose)
		self.configDict=readConfig()
		self.sport=sport
		self.splashTime = splashTime
		from Game import readGameDefaultSettings
		self.gameSettings=readGameDefaultSettings()

		self.enterFlag = False
		self.clearFlag = False
		self.menuFlag = False
		self.startFlag = False
		self.setPlayerActive=False
		self.currentMenuString = ''
		self.funcString=''
		self.teamNameString=''
		self.teamNameNumpadFlag=False
		self.teamNameNumpadTimerFlag=False
		self.teamNameNumpadFlagCount=0

		self.lastVarName=''
		self.lastCol=0
		self.lastRow=0
		self.lastPlaces=1
		self.lastTeam=255
		self.lastBlockNumList=[]
		self.lastVarClock=False
		self.varName=None
		self.team=None
		self.varClock=None
		self.currentData=None
		self.col=0
		self.row=0
		self.places=1
		self.splashTimerFlag=False
		self.menuTimerFlag=False
		self.NewGameMenu=1

		self.menuNumber=1
		self.startingMenuNumber=1
		self.endingMenuNumber=1
		self.timerNumberGuest=1
		self.timerNumberHome=1

		self.numberPressedSequence=[]
		self.numpadSequence=None
		self.lcdTextDisplay='Blank'
		self.row1=''
		self.row2=''

		self.precisionMenuFlag=False
		self.dimmingMenuFlag=False
		self.teamNameMenuFlag=False
		self.segmentTimerMenuFlag=False
		self.addVariableFlag=True
		self.statFlag=False

		self.mappedFlag = False
		self.internalRefreshFlag = False

		self.numberPressedFlag = False
		self.tempDict={}

		self.buildFuncDict()
		self.Menu_LCD_Text = readLCDButtonMenus()

	#Init methods

	def buildFuncDict(self):
		'''Build dictionary of game function keys matched to menu class functions.'''
		#All games
		self.funcDict = {'Splash':self.Splash, 'NewGame':self.NewGame,'setClock':self.setClock, 'setClockTenthSec':self.setClockTenthSec, \
		'autoHorn':self.autoHorn, 'timeOfDay':self.timeOfDay, 'timeOutTimer':self.timeOutTimer, \
		'setHomeScore':self.setHomeScore,'setGuestScore':self.setGuestScore,'clockUpDown':self.clockUpDown,\
		'playClocks':self.playClocks, 'shotClocks':self.shotClocks,'tenthSecOnOff':self.tenthSecOnOff, \
		'periodClockReset':self.periodClockReset, 'guestScorePlusOne':self.guestScorePlusOne,'homeScorePlusOne':self.homeScorePlusOne, \
		'teamNameMenu':self.teamNameMenu, 'segmentTimerMenu':self.segmentTimerMenu, \
		'handheldButton1':self.doNothing, 'handheldButton2':self.doNothing, 'handheldButton3':self.doNothing}

		#Number pad
		self.funcDict.update({'Number_7_ABC':self.Number_7_ABC, 'Number_8_DEF':self.Number_8_DEF, 'Number_9_GHI':self.Number_9_GHI, \
		'Number_5_MNO':self.Number_5_MNO, 'Number_6_PQR':self.Number_6_PQR,  'Number_1_STU':self.Number_1_STU, \
		'Number_2_VWX':self.Number_2_VWX, 'Number_3_YZ':self.Number_3_YZ,'Number_4_JKL':self.Number_4_JKL,'Number_0_&-.!':self.Number_0,\
		'clear':self.clear_, 'enter':self.enter_, 'clear_FlashHit':self.clear_,'enter_FlashError':self.enter_})

			#All games - no nothing--------------------------------------------------------------
		self.funcDict.update({'guestScorePlusTen':self.doNothing, 'homeScorePlusTen':self.doNothing,\
		'secondsMinusOne':self.doNothing,'possession':self.doNothing,'horn':self.doNothing,\
		'minutesMinusOne':self.doNothing, 'periodClockOnOff':self.doNothing, \
		'secondsPlusOne':self.doNothing,'blank':self.doNothing,'None':self.doNothing, '':self.doNothing})

		#hockey
		self.funcDict.update({'clear_GuestGoal':self.clear_,'enter_HomeGoal':self.enter_,'play_shotClocks':self.play_shotClocks,\
		'setGuestFunctions':self.setGuestFunctions, 'setHomeFunctions':self.setHomeFunctions,\
		'guestPenalty':self.guestPenalty, 'homePenalty':self.homePenalty,})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'guestShotsPlusOne':self.doNothing,'homeShotsPlusOne':self.doNothing,'qtrs_periodsPlusOne':self.doNothing,\
		'guestPenaltyPlusOne':self.doNothing, 'homePenaltyPlusOne':self.doNothing,\
		'guestKicksPlusOne':self.doNothing,'homeKicksPlusOne':self.doNothing,\
		'guestSavesPlusOne':self.doNothing,'homeSavesPlusOne':self.doNothing})

		#soccer
		self.funcDict.update({'setGuestFunctions':self.setGuestFunctions, 'setHomeFunctions':self.setHomeFunctions, \
		'play_shotClocks':self.play_shotClocks,'clear_GuestGoal':self.clear_,'enter_HomeGoal':self.enter_})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'guestKicksPlusOne':self.doNothing,'homeKicksPlusOne':self.doNothing,\
		'guestSavesPlusOne':self.doNothing,'homeSavesPlusOne':self.doNothing,'qtrs_periodsPlusOne':self.doNothing,\
		'guestShotsPlusOne':self.doNothing,'homeShotsPlusOne':self.doNothing, \
		'guestPenaltyPlusOne':self.doNothing, 'homePenaltyPlusOne':self.doNothing})

		#basketball
		self.funcDict.update({ 'playerMatchGame':self.playerMatchGame, 'playerFoul':self.playerFoul,\
		'setHomeTimeOuts':self.setHomeTimeOuts,'setGuestTimeOuts':self.setGuestTimeOuts})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'guestTeamFoulsPlusOne':self.doNothing, 'homeTeamFoulsPlusOne':self.doNothing, \
		'homeBonus':self.doNothing,'guestBonus':self.doNothing,'qtrs_periodsPlusOne':self.doNothing})

		#football
		self.funcDict.update({'yardsToGoReset':self.yardsToGoReset,'setYardsToGo':self.setYardsToGo, 'setBallOn':self.setBallOn})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'yardsToGoMinusOne':self.doNothing,'yardsToGoMinusTen':self.doNothing,\
		'guestTimeOutsMinusOne':self.doNothing,'homeTimeOutsMinusOne':self.doNothing,'downsPlusOne':self.doNothing,\
		'qtrs_periodsPlusOne':self.doNothing,'quartersPlusOne':self.doNothing,})

		#baseball
		self.funcDict.update({'setPitchCounts':self.setPitchCounts,'setBatterNumber':self.setBatterNumber,'clear_FlashHit':self.clear_,\
		'enter_FlashError':self.enter_,'assignError':self.assignError,'setTotalRuns':self.setTotalRuns,'setTotalHits':self.setTotalHits,\
		'setTotalErrors':self.setTotalErrors, 'setRuns_Innings':self.setRuns_Innings,'setInningTop_Bot':self.setInningTop_Bot})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'ballsPlusOne':self.doNothing,'homePitchesPlusOne':self.doNothing,'singlePitchesPlusOne':self.doNothing,\
		'strikesPlusOne':self.doNothing, 'outsPlusOne':self.doNothing, 'inningsPlusOne':self.doNothing,'teamAtBat':self.doNothing, \
		'guestPitchesPlusOne':self.doNothing,'incInningTop_Bot':self.doNothing, 'runsPlusOne':self.doNothing,'hitsPlusOne':self.doNothing,\
		'flashHitIndicator':self.doNothing,'flashErrorIndicator':self.doNothing,'errorsPlusOne':self.doNothing})

		#stat
		self.funcDict.update({'addPlayer':self.addPlayer, 'deletePlayer':self.deletePlayer, 'displaySize':self.displaySize, \
		'editPlayer':self.editPlayer,'nextPlayer':self.nextPlayer,'subPlayer':self.subPlayer,'previousPlayer':self.previousPlayer})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'fouls_digsMinusOne':self.doNothing, 'fouls_digsPlusOne':self.doNothing,\
		'points_killsMinusOne':self.doNothing, 'points_killsPlusOne':self.doNothing})

		#cricket
		self.funcDict.update({'setPlayer1Number':self.setPlayer1Number, 'setPlayer2Number':self.setPlayer2Number, 'setPlayer1Score':self.setPlayer1Score, \
			'setPlayer2Score':self.setPlayer2Score, 'setTotalScore':self.setTotalScore, 'setOvers':self.setOvers, 'setLastMan':self.setLastMan, \
			'setLastWicket':self.setLastWicket, 'set1eInnings':self.set1eInnings})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'oversPlusOne':self.doNothing, 'player1ScorePlusOne':self.doNothing, \
			'player2ScorePlusOne':self.doNothing, 'wicketsPlusOne':self.doNothing})

	#Externally callable methods

	def Map(self, game, funcString='None'):
		'''Main function called when there is a key press event to update the LCD screen.'''
		verbose(['\nMap---'], self.verbose)
		self.funcString=funcString

		#Call the function - This is the area to control if this funcString has a menu or only uses it in certain cases
		self.callFunction(game)

		#Main function for controlling menus
		game = self.UpdateMenu(game)

		#RefreshScreen displays the default screen for each sport when not in a menu
		self.RefreshScreen(game)

		return game

	#Default screen methods

	def RefreshScreen(self, game):
		'''Builds the default screen for the sport if not in a menu.'''
		verbose(['\nRefreshScreen - sportType:', game.gameData['sportType'], ', self.menuFlag:', self.menuFlag], self.verbose)
		if not self.menuFlag or self.currentMenuString=='yardsToGoReset':
			if game.clockDict.has_key('periodClock'):
				if game.clockDict['periodClock'].countUp:
					clockType='U'
				else:
					clockType='D'
				if game.gameSettings['precisionEnable']:
					clockType='P'
				if game.gameSettings['timeOfDayClockEnable']:
					clockType='C'
				if self.gameSettings['segmentTimerEnable']:
					clockName='segmentTimer'
				elif game.gameSettings['timeOutTimerEnable']:
					clockType='T'
					clockName='timeOutTimer'
				elif game.gameSettings['timeOfDayClockEnable']:
					clockName='timeOfDayClock'
				else:
					clockName='periodClock'
				if game.gameSettings['timeOfDayClockEnable']:
					minutes=game.clockDict[clockName].hours
					seconds=game.clockDict[clockName].minutes
				else:
					minutes=game.clockDict[clockName].minutes
					seconds=game.clockDict[clockName].seconds

			verbose(['\n', game.gameData['sportType']+'screen'], self.verbose)
			if game.gameSettings['segmentTimerEnable']:
				self.segmentTimerScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='baseball':
				self.baseballScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='linescore':
				self.linescoreScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='football':
				self.footballScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='soccer':
				self.soccerScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='hockey':
				self.hockeyScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='basketball':
				self.basketballScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='cricket':
				self.cricketScreen(game, clockType, minutes, seconds)
			elif game.gameData['sportType']=='stat':
				self.statScreen(game)
		self.lcdDefaultScreen = '\n ------LCD------\n'+self.row1+'\n'+self.row2
		verbose([self.lcdDefaultScreen], self.verbose)

	def segmentTimerScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for the segment timer.'''
		self.row1 = 'SEG %02d     %02d:%02d' % (\
		game.gameSettings['segmentNumber'], minutes, seconds)
		self.row2 = 'PROGRAM %02d' % (game.gameSettings['programID'])

	def baseballScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for non-linescore baseball.'''
		dataName='atBatIndicator'
		guestP = game.getTeamData(game.guest, dataName)
		homeP = game.getTeamData(game.home, dataName)
		if game.gameData['hitIndicator']:
			left='H'
		else:
			if guestP:
				left='<'
			else:
				left=' '
		if game.gameData['errorIndicator']:
			right='E'
		else:
			if homeP:
				right='>'
			else:
				right=' '
		if game.clockDict['periodClock'].timeUnitsDict['hoursUnits']==0:
			if game.getGameData('inning')==0:
				inn='- '
				self.row1 = '%02d %s%02d:%02d  %s %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, minutes, seconds, inn, \
				game.getTeamData(game.home, 'score')\
				)
			else:
				inn=game.getGameData('inning')
				self.row1 = '%02d %s%02d:%02d  %02d %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, minutes, seconds, inn, \
				game.getTeamData(game.home, 'score')\
				)
		else:
			if game.clockDict['periodClock'].timeUnitsDict['blinky']:
				blink='*'
			else:
				blink=' '
			if game.getGameData('inning')==0:
				inn='- '
				self.row1 = '%02d %s%d:%02d%s  %s %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, game.clockDict['periodClock'].timeUnitsDict['hoursUnits'], game.clockDict['periodClock'].minutes, blink, inn, \
				game.getTeamData(game.home, 'score')\
				)
			else:
				inn=game.getGameData('inning')
				self.row1 = '%02d %s%d:%02d%s  %02d %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, game.clockDict['periodClock'].timeUnitsDict['hoursUnits'], game.clockDict['periodClock'].minutes, blink, inn, \
				game.getTeamData(game.home, 'score')\
				)
		self.row2 = '%s%03d %d-%d-%d %03d %s' % (left, game.getTeamData(game.guest, 'pitchCount'), \
		game.gameData['balls'], game.gameData['strikes'], game.gameData['outs'], game.getTeamData(game.home, 'pitchCount'), right)

	def linescoreScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for linescore baseball.'''
		if game.gameSettings['inningBot']:
			innType='B'
		else:
			innType='T'
		if game.clockDict['periodClock'].timeUnitsDict['hoursUnits']==0:
			if game.gameSettings['linescoreStart']:
				inn='- '
				self.row1 = '%02d %s%02d:%02d %s%s %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, minutes, seconds, innType, inn, \
				game.getTeamData(game.home, 'score')\
				)
			else:
				inn=game.getGameData('inning')
				self.row1 = '%02d %s%02d:%02d %s%02d %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, minutes, seconds, innType, inn, \
				game.getTeamData(game.home, 'score')\
				)
		else:
			if game.clockDict['periodClock'].timeUnitsDict['blinky']:
				blink='*'
			else:
				blink=' '
			if game.gameSettings['linescoreStart']:
				inn='- '
				self.row1 = '%02d %s%d:%02d%s %s%s %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, game.clockDict['periodClock'].timeUnitsDict['hoursUnits'], game.clockDict['periodClock'].minutes, blink, innType, inn, \
				game.getTeamData(game.home, 'score')\
				)
			else:
				inn=game.getGameData('inning')
				self.row1 = '%02d %s%d:%02d%s %s%02d %02d' % (\
				game.getTeamData(game.guest, 'score'), \
				clockType, game.clockDict['periodClock'].timeUnitsDict['hoursUnits'], game.clockDict['periodClock'].minutes, blink, innType, inn, \
				game.getTeamData(game.home, 'score')\
				)
		self.row2 = '%d %02d %d-%d-%d  %02d %d' % (game.getTeamData(game.guest, 'errors'), game.getTeamData(game.guest, 'hits'), \
		game.gameData['balls'], game.gameData['strikes'], game.gameData['outs'], game.getTeamData(game.home, 'hits'), game.getTeamData(game.home, 'errors'))

	def footballScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for football.'''
		if game.getTeamData(game.guest, 'possession'):
			leftPoss='<'
		else:
			leftPoss=' '
		if game.getTeamData(game.home, 'possession'):
			rightPoss='>'
		else:
			rightPoss=' '
		self.row1 = '%02d  %s%02d:%02d %d  %02d' % (\
		game.getTeamData(game.guest, 'score'), \
		clockType, minutes, seconds, game.gameData['quarter'], \
		game.getTeamData(game.home, 'score')\
		)
		self.row2 = '%s%d  %d %02d %02d   %d%s' % (leftPoss, game.getTeamData(game.guest, 'timeOutsLeft'), \
		game.gameData['down'], game.gameData['yardsToGo'], game.gameData['ballOn'], game.getTeamData(game.home, 'timeOutsLeft'), rightPoss)

	def soccerScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for soccer.'''
		if game.getTeamData(game.guest, 'goalIndicator'):
			leftGoal='<'
		else:
			leftGoal=' '
		if game.getTeamData(game.home, 'goalIndicator'):
			rightGoal='>'
		else:
			rightGoal=' '
		self.row1 = '%02d%s %s%02d:%02d   %s%02d' % (\
		game.getTeamData(game.guest, 'score'), leftGoal, \
		clockType, minutes, seconds, \
		rightGoal, game.getTeamData(game.home, 'score')\
		)
		self.row2 = ' %02d %02d %d  %02d %02d' % (game.getTeamData(game.guest, 'shots'), \
		game.getTeamData(game.guest, 'kicks'), game.gameData['period'], \
		game.getTeamData(game.home, 'kicks'), game.getTeamData(game.home, 'shots'))

	def hockeyScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for hockey.'''
		if game.getTeamData(game.guest, 'goalIndicator'):
			leftGoal='<'
		else:
			leftGoal=' '
		if game.getTeamData(game.home, 'goalIndicator'):
			rightGoal='>'
		else:
			rightGoal=' '
		self.row1 = '%03d  %s%02d:%02d  %03d' % (\
		game.getTeamData(game.guest, 'score'),  \
		clockType, minutes, seconds, game.getTeamData(game.home, 'score')\
		)
		self.row2 = '%s%02d    %d     %02d%s' % (leftGoal, game.getTeamData(game.guest, 'shots'), \
		game.gameData['period'], game.getTeamData(game.home, 'shots'), rightGoal)

	def basketballScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for basketball.'''
		if game.getTeamData(game.guest, 'possession'):
			leftPoss='<'
		else:
			leftPoss=' '
		if game.getTeamData(game.home, 'possession'):
			rightPoss='>'
		else:
			rightPoss=' '
		if game.getTeamData(game.guest, 'bonus')==1:
			leftBonus='b'
		elif game.getTeamData(game.guest, 'bonus')==2:
			leftBonus='B'
		else:
			leftBonus=' '
		if game.getTeamData(game.home, 'bonus')==1:
			rightBonus='b'
		elif game.getTeamData(game.home, 'bonus')==2:
			rightBonus='B'
		else:
			rightBonus=' '
		if game.gameData['playerNumber']==255:
			playNum=0
		else:
			playNum=game.gameData['playerNumber']
		if game.gameData['playerFouls']==255:
			playFoul=0
		else:
			playFoul=game.gameData['playerFouls']
		self.row1 = '%03d %s%02d:%02d %d %03d' % (\
		game.getTeamData(game.guest, 'score'),  \
		clockType, minutes, seconds, game.gameData['period'], \
		game.getTeamData(game.home, 'score')\
		)
		self.row2 = '%s%s %02d %02d %d %02d %s%s' % (leftPoss, leftBonus, game.getTeamData(game.guest, 'fouls'), \
		playNum, playFoul, game.getTeamData(game.home, 'fouls'), rightBonus, rightPoss)

	def cricketScreen(self, game, clockType, minutes, seconds):
		'''Builds the default screen for cricket.'''
		self.row1 = '%03d %s%02d:%02d %d %03d' % (\
		game.gameData['player1Score'], clockType, minutes, seconds, game.gameData['wickets'], \
		game.gameData['player2Score']\
		)
		self.row2 = '  %02d  %03d  %02d   ' % (game.gameData['player1Number'], game.gameData['totalScore'], game.gameData['player2Number'])

	def statScreen(self, game):
		'''Builds the default screen for stat.'''
		activePlayerList, team, teamName=activePlayerListSelect(game)
		self.row1 = '%03d %02d    %02d %03d' % (\
		game.getTeamData(game.guest, 'score'), \
		game.getTeamData(game.guest, 'fouls'), game.getTeamData(game.home, 'fouls'), \
		game.getTeamData(game.home, 'score')\
		)
		if len(activePlayerList)==0 and game.notActiveIndex is None:
			self.row2 ='%s  __ 00  00' % (teamName)
		else:
			playerID=game.getPlayerData(team, 'playerID', playerNumber=game.gameSettings['playerNumber'])
			if playerID is not None:
				self.playerID=playerID
			if game.getPlayerData(team, 'playerActive', playerID=self.playerID):
				active='*'
			else:
				active=' '
			playerNumber=game.getPlayerData(team, 'playerNumber', self.playerID)
			if playerNumber[0]==' ':
				playerNumber='_'+playerNumber[1]
			self.row2 ='%s %s%s %02d  %02d' % (teamName, active, playerNumber, \
			game.getPlayerData(team, 'fouls', self.playerID), game.getPlayerData(team, 'points', self.playerID))

	#Generic Methods

	def loadMenuMapValues(self, game,  function):
		'''Builds the **tempDict** which is a dictionary of the current state of all menu data based on the current menu being displayed.'''
		verbose(['\nloadMenuMapValues - function:', function, 'self.menuNumber:', self.menuNumber], self.verbose)
		self.tempDict.clear()

		for name in self.Menu_LCD_Text[function].keys():
			verbose([name, self.Menu_LCD_Text[function][name]], self.verboseMost)

			#Build tempDict with Menu_LCD_Text
			if name=='menuNumber' or name=='startingMenuNumber' or name=='endingMenuNumber'or name=='gameSettingsFlag':
				if self.Menu_LCD_Text[function][name] is not None:
					self.tempDict[name]=int(self.Menu_LCD_Text[function][name])
				else:
					self.tempDict[name]=self.Menu_LCD_Text[function][name]
			elif name=='row_1' or name=='row_2' or name=='function' or name=='varClock':
				self.tempDict[name]=self.Menu_LCD_Text[function][name]
			elif name=='places' or name=='col' or name=='row' or name=='blockNumList' or name=='varName':
				if self.Menu_LCD_Text[function][name] is not None:
					self.tempDict[name]=self.Menu_LCD_Text[function][name].split('.')
					if len(self.tempDict[name])==1:
						if name=='varName':
							self.tempDict[name]=self.tempDict[name][0]
						else:
							self.tempDict[name]=int(self.tempDict[name][0])
				else:
					self.tempDict[name]=self.Menu_LCD_Text[function][name]
			elif name=='team':
				if self.Menu_LCD_Text[function]['team']=='guest':
					self.tempDict['team']=game.guest
				elif self.Menu_LCD_Text[function]['team']=='home':
					self.tempDict['team']=game.home
				elif self.Menu_LCD_Text[function]['team']=='stat':
					self.statFlag=True
					if game.gameSettings['currentTeamGuest']:
						self.tempDict['team']=game.guest
					else:
						self.tempDict['team']=game.home
				else:
					self.tempDict[name]=self.Menu_LCD_Text[function][name]

			#Further format only tempDict
			if name=='blockNumList' and self.Menu_LCD_Text[function]['blockNumList'] is not None:
				for x, each in enumerate(self.tempDict['blockNumList']):
					self.tempDict['blockNumList'][x]=int(self.tempDict['blockNumList'][x])
			if name=='places' and self.Menu_LCD_Text[function]['places'] is not None:
				if isinstance(self.tempDict['places'], list):
					for x, each in enumerate(self.tempDict['places']):
						self.tempDict['places'][x]=int(self.tempDict['places'][x])
			if name=='col' or name=='row' or name=='menuNumber' or name=='startingMenuNumber'\
			 or name=='endingMenuNumber'and self.Menu_LCD_Text[function][name] is not None:
				if isinstance(self.tempDict[name], list):
					for x, each in enumerate(self.tempDict[name]):
						self.tempDict[name][x]=int(self.tempDict[name][x])
						if name=='col' or name=='row':
							self.tempDict[name][x]-=1
				elif isinstance(self.tempDict[name], str) or isinstance(self.tempDict[name], int):
					if self.tempDict.has_key(name):
						self.tempDict[name]=int(self.tempDict[name])
						if name=='col' or name=='row':
							self.tempDict[name]-=1

			if not name=='':
				verbose([name, self.tempDict[name]], self.verboseMost)
		verbose([self.tempDict], self.verboseMore)
		self.__dict__.update(self.tempDict)
		return game

	def getMenu(self, function, menuNumber=1):
		'''Loads the current menu in to the LCD screens row 1 and/or row 2.'''
		verbose(['\ngetMenu---'], self.verbose)
		if self.funcDict.has_key(function):
			if menuNumber:
				verbose(['\nfunction:', function, type(function), 'menuNumber:', menuNumber, type(menuNumber)], self.verboseMore)
				row1=self.Menu_LCD_Text[function+str(menuNumber)]['row_1']
				row2=self.Menu_LCD_Text[function+str(menuNumber)]['row_2']
				if row1!='':
					self.row1=row1
					self.row2=row2
				else:
					self.row2=row2
		else:
			verbose(["\nYou didn't put this function in!!!!!!"])

	def showCurrentMenu(self, game, overrideData=0):
		'''Adds any variables to the current menu.'''
		verbose(['\nshowCurrentMenu---'], self.verbose)
		self.getMenu(self.currentMenuString, self.menuNumber)

		if isinstance(self.places, list):
			for position, place in enumerate(self.places):
				if not overrideData:
					self._getCurrentData(game, position)
				self.addVariable(position)
		else:
			if not overrideData:
				self._getCurrentData(game)
			self.addVariable()

	def addVariable(self, listPosition=0):
		'''Prepares a variable or list of variables and adds them to the LCD screen at the correct column and row.'''
		verbose(['\naddVariable - self.currentData:', self.currentData, ', self.col:', self.col, ', self.row:', self.row, ', self.places:', self.places], self.verbose)
		if self.currentData is not None:
			if isinstance(self.currentData, str):
				if self.currentMenuString=='deletePlayer':
					print 'stat'
				else:
					#Team name
					self.row2=self.currentData
					return
			if self.currentData==255:
				self.currentData=0
			if isinstance(self.places, list):
				col=self.col[listPosition]
				row=self.row[listPosition]
				if self.places[listPosition]=='1' or self.places[listPosition]==1:
					variable='%d' % (self.currentData)
				elif self.places[listPosition]=='2' or self.places[listPosition]==2:
					variable='%02d' % (self.currentData)
				elif self.places[listPosition]=='3' or self.places[listPosition]==3:
					variable='%03d' % (self.currentData)
				places=self.places[listPosition]
			else:
				col=self.col
				row=self.row
				if isinstance(self.currentData, str):
					if self.places=='1' or self.places==1:
						variable=self.currentData
					elif self.places=='2' or self.places==2:
						variable=self.currentData
					elif self.places=='3' or self.places==3:
						variable=self.currentData
				else:
					if self.places=='1' or self.places==1:
						variable='%d' % (self.currentData)
					elif self.places=='2' or self.places==2:
						variable='%02d' % (self.currentData)
					elif self.places=='3' or self.places==3:
						variable='%03d' % (self.currentData)
				places=self.places
			verbose(['variable', variable], self.verbose)
			if self.row:
				self.row2=self.row2[:col]+variable+self.row2[col+int(places):]
			else:
				self.row1=self.row1[:col]+variable+self.row1[col+int(places):]
			if self.verboseMost:
				self.lcdDefaultScreen = '\n ------LCD------\n'+self.row1+'\n'+self.row2
				verbose([self.lcdDefaultScreen], self.verboseMost)

	def callFunction(self, game):
		'''Calls the current menu function corresponding to the key pressed.
		This is the area to control if this **funcString** has a menu or only uses it in certain cases'''
		verbose(['\nCalling the Menu function -', self.funcString], self.verbose)
		if self.funcString in self.funcDict:
			self.funcDict[self.funcString](game)
		else:
			verbose(['\nNot in self.funcDict!!!!'])

	def modMenuNumber(self, operator='+', value=1):
		'''Modifies the current menu number.'''
		verbose(['\nmodMenuNumber - self.menuNumber:', self.menuNumber], self.verbose)
		if operator=='+':
			self.menuNumber+=value
		elif operator=='-':
			self.menuNumber-=value
		verbose(['self.menuNumber:', self.menuNumber], self.verbose)

	def blockNumber(self, game):
		'''Bypasses a keypress from the number pad if it is in the blocked number list.'''
		if self.numberPressedFlag:
			verbose(['\nBlocked Key Check'], self.verbose)
			if self.blockNumList is not None:
				for block in self.blockNumList:
					if self.lastNumberPressed==block:
						verbose(['\nBlocked Key', block], self.verbose)
						#self.numberPressedSequence.pop()
						return 1
		return 0

	def clearNumSeq(self):
		'''Clear the stored list of keys pressed.'''
		self.numberPressedFlag=False
		self.numberPressedSequence=[]

	def exitMenu(self, game):
		'''Fully resets all variables to the default state when a menu is exited.'''
		verbose(['\nexitMenu!!!!!'], self.verbose)
		self.menuNumber=1
		self.startingMenuNumber=1
		self.endingMenuNumber=1
		self.editInning=0
		#self.startFlag=True
		self.enterFlag=False
		self.clearFlag=False
		self.menuFlag=False
		game.gameSettings['menuFlag']=False
		self.varName=None
		self.team=None
		self.varClock=None
		#self.refreshDefaultScreenFlag=True
		self.precisionMenuFlag=False
		self.dimmingMenuFlag=False
		self.teamNameMenuFlag=False
		self.segmentTimerMenuFlag=False
		self.setPlayerActive=False
		game.gameSettings['lampTestFlag']=False
		game.gameSettings['blankTestFlag']=False
		game.gameSettings['playerStatDoubleZeroFlag']=False
		self.menuTimerFlag=False
		self.currentData=None
		self.col=0
		self.row=0
		self.places=1

		self.numberPressedFlag = False
		self.lastNumberPressed = None
		self.numberPressedSequence=[]
		self.numpadSequence=0
		self.NewGameMenu=1

		self.currentMenuString=''
		self.funcString=''
		self.teamNameString=''
		self.teamNameNumpadFlag=False
		self.teamNameNumpadTimerFlag=False
		self.teamNameNumpadFlagCount=0

		return game

	#Main branch function

	def UpdateMenu(self, game):
		'''Main update function which branches to a sub-function based on key pressed and previous state.

		**Sub-functions**

		* Start function = First call to this menu from the default screen.

		* Self function = Same key pressed as the current menu.

		* Exit function = Key pressed has a special menu close function.

		* Clear function = Clear key is pressed.

		* Enter function = Enter key is pressed.

		* Number pad function = Keys 0 through 9 is pressed.

		* Do nothing function = Key press did not trigger any other sub-functions.
		'''
		verbose(['\nUpdateMenu---', 'self.currentMenuString', self.currentMenuString, 'self.menuNumber', self.menuNumber], self.verbose)
		if self.menuFlag:
			if self.startFlag:
				self.startFlag=False
				game=self.StartFunc(game)
			else:
				if self.funcString==self.currentMenuString:
					game=self.SelfFunc(game)
				elif self.currentMenuString=='yardsToGoReset' and self.funcString!=self.currentMenuString:
					game=self.exitMenu(game)
				elif self.clearFlag:
					self.clearFlag=False
					game=self.ClearFunc(game)
				elif self.enterFlag:
					self.enterFlag=False
					game=self.EnterFunc(game)
				elif self.numberPressedFlag:
					game=self.NumpadFunc(game)
				else:
					self.doNothing(game)
		return game

	def StartFunc(self, game):
		'''Prepare and display first menu in menu chain, set **menuFlag**, and start menu timer.'''
		verbose(['\nStartFunc---'], self.verbose)
		game.gameSettings['menuFlag']=True
		self.currentMenuString=self.funcString

		#Special cases before loading menu
		if self.currentMenuString=='yardsToGoReset':
			self.endingMenuNumber=10
			game.setGameData('yardsToGo', 10)
			return game
		elif self.currentMenuString=='deletePlayer':
			activePlayerList, team, teamName=activePlayerListSelect(game)
			if len(activePlayerList)==0:
				game=self.exitMenu(game)
				return game

		hockeyORbasketball=game.gameData['sportType']=='basketball' or game.gameData['sportType']=='hockey'
		setHomeORGuestScore=self.currentMenuString=='setGuestScore' or self.currentMenuString=='setHomeScore'
		if hockeyORbasketball and setHomeORGuestScore:
			self.menuNumber=2
		if game.gameData['sportType']=='linescore' and self.currentMenuString=='setPitchCounts':
			self.menuNumber=3
		setClockANDlinescoreORbaseball=\
		(game.gameData['sportType']=='linescore' or game.gameData['sportType']=='baseball') and self.currentMenuString=='setClock'
		BB1andBB3andNOThoursFlagJumper=self.sport=='MMBASEBALL3' or self.sport=='MPBASEBALL1' and not game.gameSettings['hoursFlagJumper']
		if setClockANDlinescoreORbaseball:
			if not BB1andBB3andNOThoursFlagJumper:
				self.menuNumber=2
		if self.currentMenuString=='setRuns_Innings':
			self.editInning=game.gameData['inning']
		if self.currentMenuString=='setInningTop_Bot':
			self.changeInning=game.gameData['inning']

		#Load menu data from file
		self.loadMenuMapValues(game, self.currentMenuString+str(self.menuNumber))

		#Special case manipulation of menu data after loading
		if self.currentMenuString=='playerMatchGame':
			self._getCurrentData(game)
			if self.currentData<10 and not game.gameSettings['playerMatchGameFlag']:
				self.places=1
				self.col=14
				self.showCurrentMenu(game, 1)
				self.menuTimerFlag=True
				self.places=2
				self.col=13
				return game
		elif self.currentMenuString=='deletePlayer':
			if game.gameSettings['playerNumber'][0]==' ':
				if game.gameSettings['playerNumber']==' ':
					return game
				else:
					self.currentData=game.gameSettings['playerNumber'][1]
					self.places=1
					self.col=14
					self.showCurrentMenu(game, 1)
					self.menuTimerFlag=True
					self.places=2
					self.col=13
					return game
			else:
				self.currentData=game.gameSettings['playerNumber']
		elif self.currentMenuString=='addPlayer':
			print game.teamsDict[self.team].playersDict.keys()
			for playerID in game.teamsDict[self.team].playersDict.keys():
				print playerID, game.teamsDict[self.team].playersDict[playerID].playerData['playerNumber']
				if game.teamsDict[self.team].playersDict[playerID].playerData['playerNumber']=='  ':
					self.showCurrentMenu(game)
					self.menuTimerFlag=True
					return game
			game=self.exitMenu(game)
			return game
		elif self.currentMenuString=='guestPenalty' or self.currentMenuString=='homePenalty':
			penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
			dataName='TIMER'+str(timerNumber)+'_PLAYER_NUMBER'
			self.currentData=game.getTeamData(self.team, dataName)
			self.getMenu(self.currentMenuString, self.menuNumber)
			variable='%d' % (timerNumber)
			self.row2=self.row2[:3]+variable+self.row2[3+int(1):]
			variable='%d' % (self.currentData)
			self.row2=self.row2[:14]+variable+self.row2[14+int(1):]
			self.menuTimerFlag=True
			return game

		#Combine menu data and current variable values
		self.showCurrentMenu(game)
		self.menuTimerFlag=True
		return game

	def SelfFunc(self, game):
		'''This method controls behavior for the case when the same key as the current active menu is pressed.'''
		verbose(['\nSelfFunc---'], self.verbose)

		#Special cases before loading next menu
		if self.currentMenuString=='NewGame':
			if game.configDict['keypadType']=='MM':
				if self.menuNumber==1:
					game.gameSettings['lampTestFlag']=True
					self.modMenuNumber()
				elif self.menuNumber==2:
					game.gameSettings['lampTestFlag']=False
					game=self.exitMenu(game)
				return game
			else:
				game=self.exitMenu(game)
				return game
		elif self.currentMenuString=='yardsToGoReset':
			if self.menuNumber==9:
				game.setGameData('yardsToGo', 99)
			else:
				game.modGameData('yardsToGo', modValue=10)
		elif self.currentMenuString=='addPlayer':
			game=self.exitMenu(game)
			return game
		elif self.currentMenuString=='timeOfDay' and self.menuNumber==1:
			if not game.gameSettings['timeOfDayClockEnable']:
				game=self.exitMenu(game)
				return game
		elif (self.currentMenuString=='setHomeFunctions' or self.currentMenuString=='setGuestFunctions') and self.menuNumber==2:
			game=self.exitMenu(game)
			return game
		elif self.currentMenuString=='guestPenalty' or self.currentMenuString=='homePenalty':
			if self.menuNumber%2==1:
				penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
				clockName='penalty'+str(timerNumber)+'_'+'team'+penaltyTeamNumberString
				if timerNumber==1:
					if game.clockDict['penalty'+'4'+'_'+'team'+penaltyTeamNumberString].currentTime:
						self._modCurrentTeamTimerNumber('=', 4)
					elif game.clockDict['penalty'+'3'+'_'+'team'+penaltyTeamNumberString].currentTime:
						self._modCurrentTeamTimerNumber('=', 3)
					elif game.clockDict['penalty'+'2'+'_'+'team'+penaltyTeamNumberString].currentTime:
						self._modCurrentTeamTimerNumber('=', 2)
					else:
						pass
				else:
					self._modCurrentTeamTimerNumber('-', 1)
				self.clearNumSeq()
				name=self.currentMenuString+str(self.menuNumber)
				self.loadMenuMapValues(game, name)
				self.showCurrentMenu(game)
				return game


		#Load next menu data from file
		self.modMenuNumber()

		#Special cases after loading the next menu
		if self.menuNumber>self.endingMenuNumber:
			if self.currentMenuString=='yardsToGoReset':
				game.setGameData('yardsToGo', 0)
			game=self.exitMenu(game)
			return game
		else:
			if self.currentMenuString=='setRuns_Innings' and self.editInning==0:
				game=self.exitMenu(game)
				return game
			elif self.currentMenuString=='autoHorn' and self.menuNumber==2:
				verbose(['\nautoHorn and menuNumber 1'], self.verbose)
				if game.gameData['sportType']=='baseball' or game.gameData['sportType']=='linescore':
					game=self.exitMenu(game)
					return game
				elif game.gameData['sportType']=='football' or game.gameData['sportType']=='soccer':
					self.modMenuNumber()
			elif self.currentMenuString=='yardsToGoReset':
				return game
			elif self.currentMenuString=='Splash':
				self.clearNumSeq()
				name=self.currentMenuString+str(self.menuNumber)
				self.loadMenuMapValues(game, name)
				self.showCurrentMenu(game)
				return game

		self.clearNumSeq()
		name=self.currentMenuString+str(self.menuNumber)

		#Load menu data from file
		self.loadMenuMapValues(game, name)

		#Combine menu data and current variable values
		self.showCurrentMenu(game)
		return game

	def numpadNewGameMenus(self, game):
		if self.menuNumber==0 or self.menuNumber==1:
			#Reset game or menu selection
			if self.lastNumberPressed==3 or self.lastNumberPressed==6:
				pass
			elif self.lastNumberPressed!=1 and self.lastNumberPressed!=0:
				self.menuNumber=self.lastNumberPressed
				self.clearNumSeq()
				name='NewGame'+str(self.menuNumber)
				self.loadMenuMapValues(game, name)
				self.getMenu(self.currentMenuString, self.menuNumber)
				if self.lastNumberPressed==2:
					self.currentData=game.gameSettings['brightness']
					self.addVariable()
				elif self.lastNumberPressed==4:
					game.gameSettings['blankTestFlag']=True
					verbose(['\ngame.gameSettings[blankTestFlag]', game.gameSettings['blankTestFlag']], self.verbose)
					return game
				elif self.lastNumberPressed==5:
					game.gameSettings['lampTestFlag']=True
					verbose(['\ngame.gameSettings[lampTestFlag]', game.gameSettings['lampTestFlag']], self.verbose)
					return game
				elif self.lastNumberPressed==7:
					self.currentData=1
					self.addVariable()
				elif self.lastNumberPressed==8:
					self.currentData=game.gameSettings['precisionEnable']
					self.addVariable()
				elif self.lastNumberPressed==9:
					self.currentData=0
					self.addVariable()
				else:
					pass
					self._getCurrentData(game)
			else:
				self.currentData=self.numpadSequence

		elif self.menuNumber==2:
			#Dimming
			self.currentData=self.numpadSequence
		elif self.menuNumber==3:
			#Not Used
			pass
		elif self.menuNumber==4:
			#Blank Test
			pass
		elif self.menuNumber==5:
			#Lamp Test
			pass
		elif self.menuNumber==6:
			#Not Used
			pass
		elif self.menuNumber==7:
			#Team Name
			self.currentData=self.lastNumberPressed
			verbose(['\nTeam Name:', self.currentData], self.verbose)
		elif self.menuNumber==8:
			#Precision Time
			self.currentData=self.lastNumberPressed
		elif self.menuNumber==9:
			#Segment Timer
			self.currentData=self.lastNumberPressed
			verbose(['\nSegment Timer', self.currentData], self.verbose)

		if self.blockNumber(game):
			#Quit if number is in block list
			return game
		self.addVariable()
		return game

	def teamNameNumpad(self, game):
		self.teamNameNumpadFlag=True
		if self.menuNumber==1 or self.menuNumber==4:
			previousNumber=None
			currentNumber=int(self.numberPressedSequence[-1])
			if len(self.numberPressedSequence)>1:
				previousNumber=int(self.numberPressedSequence[-2])
			charList=(('&','-','.','!'),('S','T','U'),('V','W','X'),('Y','Z'),('J','K','L'),('M','N','O'),('P','Q','R'),('A','B','C'),('D','E','F'),('G','H','I'))
			charSetLength=len(charList[currentNumber])

			if currentNumber!=previousNumber:
				self.teamNameNumpadFlagCount=0
			else:
				if charSetLength>self.teamNameNumpadFlagCount+1:
					self.teamNameNumpadFlagCount+=1
				else:
					self.teamNameNumpadFlagCount=0

			if self.teamNameNumpadTimerFlag:
				if self.teamNameNumpadFlagCount or currentNumber==previousNumber:
					self.teamNameString=self.teamNameString[:-1]

			self.teamNameString+=charList[currentNumber][self.teamNameNumpadFlagCount]

			self.currentData=self.teamNameString
			self.addVariable()
			return game
			#self.lastNumberPressed = key
		else:
			self.addVariable()
			return game

	def NumpadFunc(self, game):
		'''This method controls behavior for the case when key numbers 0 through 9 are pressed.'''
		verbose(['\nNumpadFunc---'], self.verbose)
		self._digitSequence(game)

		#Special cases before loading next menu
		if self.currentMenuString=='NewGame':
			game=self.numpadNewGameMenus(game)
			return game

		if self.blockNumber(game):
			#Quit if number is in block list
			return game

		#All cases for data saving and displaying
		self.currentData=self.numpadSequence
		if self.currentMenuString=='setClock':
			#Must be a clock type
			linescoreORbaseball=game.gameData['sportType']=='linescore' or game.gameData['sportType']=='baseball'
			BB1andBB3andNOThoursFlagJumper=self.sport=='MMBASEBALL3' or self.sport=='MPBASEBALL1' and not game.gameSettings['hoursFlagJumper']
			if linescoreORbaseball:
				if not BB1andBB3andNOThoursFlagJumper:
					Vars=self._clockSequence(game, self.varName[0], self.varName[1], self.varName[2])
					for position, name in enumerate(self.varName):
						self.currentData=Vars[position]
						self.addVariable(position)
				else:
					Vars=self._clockSequence(game, self.varName[0], self.varName[1])
					for position, name in enumerate(self.varName):
						self.currentData=Vars[position]
						self.addVariable(position)
			else:
				Vars=self._clockSequence(game, self.varName[0], self.varName[1])
				for position, name in enumerate(self.varName):
					self.currentData=Vars[position]
					self.addVariable(position)
		elif self.currentMenuString=='setClockTenthSec':
			#Must be a clock type
			Vars=self._clockTenthsSequence(game, self.varName[0], self.varName[1])
			for position, name in enumerate(self.varName):
				self.currentData=Vars[position]
				self.addVariable(position)
		elif (self.currentMenuString=='timeOutTimer' and self.menuNumber==2) or (self.currentMenuString=='timeOfDay' and self.menuNumber>2):
			#Must be a clock type
			Vars=self._clockSequence(game, self.varName[0], self.varName[1])
			for position, name in enumerate(self.varName):
				self.currentData=Vars[position]
				self.addVariable(position)
		elif self.currentMenuString=='playerMatchGame':
			if len(self.numberPressedSequence)==1:
				self.places=1
				self.col=14
				self.showCurrentMenu(game, 1)
				self.addVariable(1)
				self.places=2
				self.col=13
			else:
				self.addVariable(1)
		elif self.currentMenuString=='addPlayer'and self.menuNumber==1:
			if len(self.numberPressedSequence)==1:
				self.places=1
				self.col=14
				self.showCurrentMenu(game, 1)
				self.addVariable(1)
				self.places=2
				self.col=13
			else:
				self.addVariable(1)
		elif self.currentMenuString=='deletePlayer':
			pass
		elif self.currentMenuString=='addPlayer'and self.menuNumber==2:
			pass
		elif self.currentMenuString=='teamNameMenu':
			if self.blockNumber(game):
				#Quit if number is in block list
				return game
			game=self.teamNameNumpad(game)
		elif self.currentMenuString=='guestPenalty' or self.currentMenuString=='homePenalty':
			if self.menuNumber%2==1:
				if len(self.numberPressedSequence)==1:
					self.currentData=int(self.numberPressedSequence[-1])
					self.getMenu(self.currentMenuString, self.menuNumber)
					variable='%d' % (self.currentData)
					self.row2=self.row2[:14]+variable+self.row2[14+int(1):]
				else:
					self.currentData=int(self.numberPressedSequence[-1]) + int(self.numberPressedSequence[-2])*10
					variable='%02d' % (self.currentData)
					self.row2=self.row2[:13]+variable+self.row2[13+int(2):]
				penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
				variable='%d' % (timerNumber)
				self.row2=self.row2[:3]+variable+self.row2[3+int(1):]
			else:
				Vars=self._clockSequence(game, self.varName[0], self.varName[1])
				for position, name in enumerate(self.varName):
					self.currentData=Vars[position]
					self.addVariable(position)
		else:
			self.addVariable()
		return game

	def ClearFunc(self, game):
		'''This method controls behavior for the case when the clear key is pressed.'''
		verbose(['\nClearFunc---'], self.verbose)
		self.clearNumSeq()

		#Special cases and going back to previous menu
		if self.currentMenuString=='NewGame':
			game=self.exitMenu(game)
			return game
		elif self.currentMenuString=='teamNameMenu' and (self.menuNumber==1 or self.menuNumber==4):
			if len(self.teamNameString):
				self.teamNameNumpadFlag=True
				self.teamNameString=self.teamNameString[:-1]
				self.currentData=self.teamNameString
				self.addVariable()
				return game
			else:
				self.clearNumSeq()
				self.currentData=None
				self.modMenuNumber('-')
		else:
			self.modMenuNumber('-')

		#Exit if no previous menu or load it
		if self.menuNumber<self.startingMenuNumber:
			game=self.exitMenu(game)
			return game
		else:
			name=self.currentMenuString+str(self.menuNumber)
			self.loadMenuMapValues(game, name)
			self.showCurrentMenu(game)
		return game

	def enterNewGameMenus(self, game):
		if self.menuNumber==4 or self.menuNumber==5:
			return game

		if self.blockNumber(game):
			#Quit if number is in block list
			return game

		if self.numberPressedFlag:
			if self.menuNumber==0 or self.menuNumber==1:
				game=self._setCurrentData(game)
				verbose(['\ngame.gameSettings[resetGameFlag]', game.gameSettings['resetGameFlag']], self.verbose)
				if game.gameSettings['resetGameFlag']:
					game.gameSettings['resetGameFlag']=False
					self.splashTimerFlag=True
					self.menuNumber=1
					self.Splash(game)
					return game
			elif self.menuNumber==2:
				if self.numpadSequence<=100 and self.numpadSequence>=50:
					game=self._setCurrentData(game)
					verbose(['\ngame.gameSettings[brightness]', game.gameSettings['brightness']], self.verbose)
			elif self.menuNumber==7 and self.lastNumberPressed:
				game=self.exitMenu(game)
				self.Map(game, funcString='teamNameMenu')
				return game
			elif self.menuNumber==8:
				game=self._setCurrentData(game)
				verbose(['\ngame.gameSettings[precisionEnable]', game.gameSettings['precisionEnable']], self.verbose)
			elif self.menuNumber==9 and self.lastNumberPressed:
				game=self.exitMenu(game)
				game.gameSettings['segmentTimerEnable']=True
				verbose(['\ngame.gameSettings[segmentTimerEnable]', game.gameSettings['segmentTimerEnable']], self.verbose)
				self.Map(game, funcString='segmentTimerMenu')
				return game
		else:
			if self.menuNumber==0 or self.menuNumber==1:
				game.gameSettings['resetGameFlag']=False
				verbose(['\ngame.gameSettings[resetGameFlag]', game.gameSettings['resetGameFlag']], self.verbose)
			elif self.menuNumber==2:
				pass
			elif self.menuNumber==7:
				game=self.exitMenu(game)
				self.Map(game, funcString='teamNameMenu')
				return game
			elif self.menuNumber==8:
				verbose(['\ngame.gameSettings[precisionEnable]', game.gameSettings['precisionEnable']], self.verbose)
			elif self.menuNumber==9:
				pass
		game=self.exitMenu(game)
		return game

	def EnterFunc(self, game):
		'''This method controls behavior for the case when the enter key is pressed.'''
		verbose(['\nEnterFunc---'], self.verbose)

		#Handle all special enter events
		if self.currentMenuString=='NewGame':
			game=self.enterNewGameMenus(game)
			return game
		if self.currentMenuString=='setRuns_Innings' and self.menuNumber==1:
			verbose(['\nsetRuns_Innings and menuNumber 1'], self.verbose)
			if self.numberPressedFlag:
				game=self._setCurrentData(game)
			if self.editInning==0:
				game=self.exitMenu(game)
				return game
		elif self.currentMenuString=='setInningTop_Bot' and self.menuNumber==1:
			verbose(['\nsetInningTop_Bot and menuNumber 1'], self.verbose)
			self.changeInning=self.currentData
		elif self.currentMenuString=='setInningTop_Bot' and self.menuNumber==2:
			verbose(['\nsetRuns_Innings and menuNumber 2'], self.verbose)
			if self.changeInning!=0:
				game.gameSettings['linescoreStart']=False
			game.gameData['inning']=self.changeInning
			if self.numberPressedFlag:
				game=self._setCurrentData(game)
		elif self.currentMenuString=='autoHorn' and self.menuNumber==1:
			verbose(['\nautoHorn and menuNumber 1'], self.verbose)
			if game.gameData['sportType']=='baseball' or game.gameData['sportType']=='linescore':
				game=self._setCurrentData(game)
				game=self.exitMenu(game)
				return game
			elif game.gameData['sportType']=='football' or game.gameData['sportType']=='soccer':
				game=self._setCurrentData(game)
				self.modMenuNumber()
		elif self.currentMenuString=='assignError':
			self.errorPosition=self.currentData
			self.gameSettings['assignErrorFlashEnable'] = True
			self.assignErrorCount=self.gameSettings['assignErrorFlashCount']
			game=self.assignErrorToggle(game)
		elif self.currentMenuString=='playerMatchGame':
			game=self._zeroOrDoubleZeroDisplayFlagControl(game, 'playerMatchGameFlag')
			if self.numberPressedFlag:
				game=self._setCurrentData(game)
		elif (self.currentMenuString=='guestPenalty' or self.currentMenuString=='homePenalty'):
			if self.menuNumber%2==1:
				penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
				varName='timer'+str(timerNumber)+'team'+penaltyTeamNumberString+'playerFlag'
				game=self._zeroOrDoubleZeroDisplayFlagControl(game, varName)
				if self.numberPressedFlag:
					if len(self.numberPressedSequence)==1:
						self.numpadSequence=int(self.numberPressedSequence[-1])
					elif len(self.numberPressedSequence)>=2:
						self.numpadSequence=int(self.numberPressedSequence[-1]) + int(self.numberPressedSequence[-2])*10
					game=self._setCurrentData(game, 1)
			else:
				if self.numberPressedFlag:
					for position, place in enumerate(self.places):
						game=self._setCurrentData(game, position)
					penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
					if timerNumber==4:
						self._modCurrentTeamTimerNumber('=', 1)
					else:
						self._modCurrentTeamTimerNumber('+', 1)
					self.clearNumSeq()
					game=self.exitMenu(game)
					return game
		elif self.currentMenuString=='addPlayer' and self.menuNumber==2:
			if self.numberPressedFlag and self.lastNumberPressed==1:#set to players not greater than max players
				self.setPlayerActive=True
			else:
				self.setPlayerActive=False
			game=self._setCurrentData(game)
		elif self.currentMenuString=='deletePlayer':
			if self.numberPressedFlag and self.lastNumberPressed==1:
				game=self._setCurrentData(game)
		elif self.currentMenuString=='teamNameMenu':
			if self.menuNumber==1 or self.menuNumber==4:
				if self.numberPressedFlag:
					game=self._setCurrentData(game)
				self.teamNameString=''
			else:
				if self.numberPressedFlag:
					game=self._setCurrentData(game)

		elif self.currentMenuString=='timeOfDay' and self.menuNumber==1:
			if self.numberPressedFlag:
				game=self._setCurrentData(game)
			if not game.gameSettings['timeOfDayClockEnable']:
				game=self.exitMenu(game)
				return game


		#If normal save the current data
		else:
			if self.numberPressedFlag:
				if isinstance(self.places, list):
					for position, place in enumerate(self.places):
						game=self._setCurrentData(game, position)
				else:
					game=self._setCurrentData(game)
			else:
				pass

		#Handle events after data from numpad is saved
		if self.currentMenuString=='setPitchCounts':
			game.setSinglePitchCountFromMenu()
		elif self.currentMenuString=='timeOutTimer' and self.menuNumber==2:
			game.gameSettings['timeOutTimerEnable']=True
			game.clockDict['timeOutTimer'].Start()
		elif (self.currentMenuString=='setHomeFunctions' or self.currentMenuString=='setGuestFunctions') and self.menuNumber==2:
			game=self.exitMenu(game)
			return game
		elif self.currentMenuString=='Splash' and self.menuNumber==2:
			print self.configDict['sport'][:13]
			if self.numberPressedFlag and game.gameSettings['multisportMenuFlag']:
				if self.configDict['sport'][:13]=='MPMULTISPORT1':
					if game.gameSettings['multisportChoiceFlag']:
						sport='MPMULTISPORT1-football'
					else:
						sport='MPMULTISPORT1-baseball'
				elif self.configDict['sport'][:8]=='MPLX3450':
					if game.gameSettings['multisportChoiceFlag']:
						sport='MPLX3450-football'
					else:
						sport='MPLX3450-baseball'
				elif self.configDict['sport'][:12]=='MPSOCCER_LX1':
					if game.gameSettings['multisportChoiceFlag']:
						sport='MPSOCCER_LX1-soccer'
					else:
						sport='MPSOCCER_LX1-football'
				c=Config()
				c.writeSport(sport)
				self.configDict.clear()
				self.configDict=readConfig()

			game.gameSettings['resetGameFlag']=True
			return game

		#Go to next menu
		self.modMenuNumber()
		self.clearNumSeq()

		#Exit if no next menu or load it
		if self.menuNumber>self.endingMenuNumber:
			verbose(['self.menuNumber:',self.menuNumber, 'self.endingMenuNumber:', self.endingMenuNumber], self.verboseMore)
			game=self.exitMenu(game)
			return game
		else:
			name=self.currentMenuString+str(self.menuNumber)
			self.loadMenuMapValues(game, name)
			self.showCurrentMenu(game)

		return game

	#Special menu methods for UpdateMenu's children

	def _digitSequence(self, game):
		verbose(['\n_digitSequence - self.places:', self.places, 'self.numberPressedSequence', self.numberPressedSequence], self.verbose)
		if self.numberPressedSequence:
			if self.places=='1' or self.places==1 or len(self.numberPressedSequence)==1:
				self.numpadSequence=int(self.numberPressedSequence[-1])
			elif self.places=='2' or self.places==2 or len(self.numberPressedSequence)==2:
				self.numpadSequence=int(self.numberPressedSequence[-1]) + int(self.numberPressedSequence[-2])*10
			elif self.places=='3' or self.places==3 or len(self.numberPressedSequence)>=2:
				self.numpadSequence=int(self.numberPressedSequence[-1]) + int(self.numberPressedSequence[-2])*10 + int(self.numberPressedSequence[-3])*100
		else:
			self.numpadSequence=None
		verbose(['\nself.numpadSequence:', self.numpadSequence], self.verbose)

	def _clockSequence(self, game, var1=0, var2=0, var3=None):
		verbose(['\n_clockSequence start-------', self.numberPressedSequence], self.verbose)
		if var3 is not None:
			if len(self.numberPressedSequence)==1:
				var1=0
				var2=0
				var3=int(self.numberPressedSequence[-1])
			elif len(self.numberPressedSequence)==2:
				var1=0
				var2=0
				var3=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
			elif len(self.numberPressedSequence)==3:
				var1=0
				var2=int(self.numberPressedSequence[-3])
				var3=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
			elif len(self.numberPressedSequence)==4:
				var1=0
				var2=int(self.numberPressedSequence[-3])+int(self.numberPressedSequence[-4])*10
				var3=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
			elif len(self.numberPressedSequence)>=5:
				var1=int(self.numberPressedSequence[-5])
				var2=int(self.numberPressedSequence[-3])+int(self.numberPressedSequence[-4])*10
				var3=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
			else:
				print '\n_clockSequence ERROR\n'
			verbose(['Return (var1, var2, var3)=', var1, var2, var3], self.verbose)
			return var1, var2, var3
		else:
			if len(self.numberPressedSequence)==1:
				var1=0
				var2=int(self.numberPressedSequence[-1])
			elif len(self.numberPressedSequence)==2:
				var1=0
				var2=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
			elif len(self.numberPressedSequence)==3 or ((self.currentMenuString=='timeOutTimer' or self.currentMenuString=='guestPenalty' or self.currentMenuString=='guestPenalty')\
			 and len(self.numberPressedSequence)>=3):
				var1=int(self.numberPressedSequence[-3])
				var2=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
			elif len(self.numberPressedSequence)>=4:
				var1=int(self.numberPressedSequence[-3])+int(self.numberPressedSequence[-4])*10
				var2=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
			else:
				print '\n_clockSequence ERROR\n'
			verbose(['Return (var1, var2)=', var1, var2], self.verbose)
			return var1, var2

	def _clockTenthsSequence(self, game, var1=0, var2=0.0):
		verbose(['\n__clockTenthsSequence start-------', self.numberPressedSequence], self.verbose)
		if len(self.numberPressedSequence)==1:
			var1=0
			var2=int(self.numberPressedSequence[-1])
		elif len(self.numberPressedSequence)==2:
			var1=int(self.numberPressedSequence[-2])
			var2=int(self.numberPressedSequence[-1])
		elif len(self.numberPressedSequence)>=3:
			var1=int(self.numberPressedSequence[-2])+int(self.numberPressedSequence[-3])*10
			var2=int(self.numberPressedSequence[-1])
		else:
			print '\n__clockTenthsSequence ERROR\n'
		verbose(['Return (var1, var2)=', var1, var2], self.verbose)
		return var1, var2

	def _penaltyTeamNumberExtract(self, penaltyTeamNumberString=None):
		if self.currentMenuString[:5]=='guest':
			penaltyTeamNumberString='One'
		elif self.currentMenuString[:4]=='home':
			penaltyTeamNumberString='Two'
		return penaltyTeamNumberString

	def _modCurrentTeamTimerNumber(self, modOperator='+', modValue=1):
		penaltyTeamNumberString=self._penaltyTeamNumberExtract()
		if modOperator=='+':
			if penaltyTeamNumberString=='One':
				self.timerNumberGuest+=modValue
			elif penaltyTeamNumberString=='Two':
				self.timerNumberHome+=modValue
		elif modOperator=='-':
			if penaltyTeamNumberString=='One':
				self.timerNumberGuest-=modValue
			elif penaltyTeamNumberString=='Two':
				self.timerNumberHome-=modValue
		elif modOperator=='=':
			if penaltyTeamNumberString=='One':
				self.timerNumberGuest=modValue
			elif penaltyTeamNumberString=='Two':
				self.timerNumberHome=modValue
		else:
			print 'ERROR -- ', modOperator, 'is not a valid modOperator!!!'

	def _getCurrentTeamAndTimerNumber(self):
		penaltyTeamNumberString=self._penaltyTeamNumberExtract()
		if penaltyTeamNumberString=='One':
			timerNumber=self.timerNumberGuest
		elif penaltyTeamNumberString=='Two':
			timerNumber=self.timerNumberHome
		return penaltyTeamNumberString, timerNumber

	def _zeroOrDoubleZeroDisplayFlagControl(self, game, varName):
		verbose(['\n_zeroOrDoubleZeroDisplayFlagControl---Start self.varName:', game.gameSettings[varName]], self.verbose)
		verbose(['self.varName=', varName], self.verbose)
		if self.numberPressedFlag:
			if len(self.numberPressedSequence)>=2 and int(self.numberPressedSequence[-2])==0:
				game.gameSettings[varName]=True
			elif len(self.numberPressedSequence)==1:
				game.gameSettings[varName]=False
		verbose(['_zeroOrDoubleZeroDisplayFlagControl---End self.varName:', game.gameSettings[varName]], self.verbose)
		return game

	def _getCurrentData(self, game, listPosition=0):
		RW='R'
		verbose(['\n_getCurrentData - self.varName:', self.varName, ', self.varClock:', self.varClock, ', self.team:', self.team, 'self.gameSettingsFlag', self.gameSettingsFlag], self.verbose)
		self._gameDataFunc(game, RW, listPosition)
		return game

	def _setCurrentData(self, game, listPosition=0):
		RW='W'
		verbose(['\n_setCurrentData - self.varName:', self.varName, ', self.varClock:', self.varClock, ', self.team:', self.team, 'self.gameSettingsFlag', self.gameSettingsFlag, \
		self.team, 'self.numpadSequence', self.numpadSequence], self.verbose)
		self._gameDataFunc(game, RW, listPosition)
		return game

	def _gameDataFunc(self, game, RW, listPosition):
		'''
		Function to read or write data by the proper means.
			*The big nasty beast of data fondling*
		'''
		#All data to be saved or read must have a varName
		if self.varName is not None:
			#Game settings variables will have a '1' in the gameSettingsFlag cell of the MenuMap
			if self.gameSettingsFlag and game.gameSettings['segmentTimerEnable']:
				#does this need to be here?
				if RW=='R':
					#NORMAL read of gameSettings data
					if isinstance(self.varName, list):
						self.currentData=game.gameSettings[self.varName[listPosition]]
					else:
						self.currentData=game.gameSettings[self.varName]
				elif RW=='W':
					#NORMAL write of gameSettings data
					if isinstance(self.varName, list):
						game.gameSettings[self.varName[listPosition]]=self.numpadSequence
					else:
						game.gameSettings[self.varName]=self.numpadSequence
			elif self.gameSettingsFlag:
				if RW=='R':
					#NORMAL read of gameSettings data
					if isinstance(self.varName, list):
						self.currentData=game.gameSettings[self.varName[listPosition]]
					else:
						self.currentData=game.gameSettings[self.varName]
				elif RW=='W':
					#NORMAL write of gameSettings data
					if isinstance(self.varName, list):
						game.gameSettings[self.varName[listPosition]]=self.numpadSequence
					else:
						game.gameSettings[self.varName]=self.numpadSequence
			else:
				#gameSettingsFlag not set
				if self.team is not None:
					#If a team name such as home or guest is in the team column of the MenuMap go here
					if self.varName=='scoreInn':
						if self.editInning==0:
							game=self.exitMenu(game)
							return game
						self.varName=self.varName+str(self.editInning)

					elif RW=='R':
						if isinstance(self.varName, list):
							penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
							if self.varName[listPosition]=='timerNumber':
								self.currentData=timerNumber
							elif self.varName[listPosition]=='playerNumber':
								dataName='TIMER'+str(timerNumber)+'_PLAYER_NUMBER'
								self.currentData=game.getTeamData(self.team, dataName)
							else:
								#NORMAL read of team data LIST type
								self.currentData=game.getTeamData(self.team, self.varName[listPosition])
						elif self.varName[:6]=='player':
							print 'self.varName', self.varName
							if self.varName=='playerNumber':
								self.currentData=game.gameSettings['playerNumber']
							else:
								self.currentData=None
						else:
							#NORMAL read of team data
							self.currentData=game.getTeamData(self.team, self.varName)
							#print 'game.getTeamData(self.team, self.varName)',game.getTeamData(self.team, self.varName)

						#Type change to integer unless a string
						if not (self.varName=='name' or self.varName[:6]=='player'):
							self.currentData=int(self.currentData)

					elif RW=='W':
						if not (self.varName=='name' or self.varName[:6]=='player'):
							if self.varName[listPosition]=='playerNumber':
								penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
								dataName='TIMER'+str(timerNumber)+'_PLAYER_NUMBER'
								game.setTeamData(self.team, dataName, self.numpadSequence, self.places[listPosition])
							else:
								#NORMAL write of team data
								game.setTeamData(self.team, self.varName, self.numpadSequence, self.places)
						else:
							if self.varName=='player':
								#Check if leading zero to format ans set game.gameSettings['playerNumber']
								game=self._zeroOrDoubleZeroDisplayFlagControl(game, 'playerStatDoubleZeroFlag')
								activePlayerList, team, teamName=activePlayerListSelect(game)
								if self.numpadSequence<10:
									if game.gameSettings['playerStatDoubleZeroFlag']:
										game.gameSettings['playerNumber']='0'+str(self.numpadSequence)
									else:
										game.gameSettings['playerNumber']=' '+str(self.numpadSequence)
								else:
									game.gameSettings['playerNumber']=str(self.numpadSequence)
								print 'game.gameSettings[playerNumber]', game.gameSettings['playerNumber']

								#Check for duplicate playerNumber in current list, show error
								for playerNumber in activePlayerList:
									print 'playerNumber', playerNumber
									if game.gameSettings['playerNumber']==playerNumber:
										self.menuNumber=0 #1 minus real menu and let modMenu increment
										self.currentMenuString='StatSplashes'
										return game

								self.playerID=game.getPlayerData(self.team, 'playerID', playerNumber=game.gameSettings['playerNumber'])
								if self.playerID is None:
									for playerID in game.teamsDict[self.team].playersDict.keys():
										if game.teamsDict[self.team].playersDict[playerID].playerData['playerNumber']=='  ':
											self.playerID=playerID
											return game

							elif self.varName=='playerActive':
								print 'game.maxActive', game.maxActive
								activePlayerList, team, teamName=activePlayerListSelect(game)

								if self.setPlayerActive:
									#Check if list is full
									if len(activePlayerList)>=game.maxActive:
										self.menuNumber=1 #1 minus real menu and let modMenu increment
										self.currentMenuString='StatSplashes'
									else:
										#Add active player to list
										game.setPlayerData(self.team, self.playerID, 'playerActive', True, 1)
										self._updateActivePlayerList(game)

								game.setPlayerData(self.team, self.playerID, 'playerNumber', game.gameSettings['playerNumber'], 2)
								if game.notActiveIndex is None:
									game.notActiveIndex=0
								#Always set LCD and display control to first in current list
								if len(activePlayerList):
									game=self._activePlayerListSort(game)
									game.gameSettings['playerNumber']=activePlayerList[0]
									game.gameSettings['statNumber']=game.statNumberList[1]
								else:
									game.gameSettings['statNumber']=game.statNumberList[0]
							elif self.varName=='playerNumber':
								game.setPlayerData(self.team, self.playerID, 'playerNumber', '  ')
								game.setPlayerData(self.team, self.playerID, 'playerActive', False, 1)
								game.setPlayerData(self.team, self.playerID, 'fouls', 0)
								game.setPlayerData(self.team, self.playerID, 'points', 0)
								self._updateActivePlayerList(game, removeFlag=True)
								if len(activePlayerList):
									game=self._activePlayerListSort(game)
									game.gameSettings['playerNumber']=activePlayerList[0]
									game.gameSettings['statNumber']=game.statNumberList[1]
								else:
									game.gameSettings['playerNumber']='  '
									game.gameSettings['statNumber']=game.statNumberList[0]
							else:
								#ETN variable 'name'
								game.setTeamData(self.team, self.varName, self.teamNameString, 1)
				else:
					#No value in team column of MenuMap
					if self.varClock is not None:
						#Value is in the varClock column of the MenuMap
						if RW=='R':
							if isinstance(self.varName, list):
								if self.varClock=='penalty':
									penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
									clockName=self.varClock+str(timerNumber)+'_'+'team'+penaltyTeamNumberString
									self.currentData=game.getClockData(clockName, self.varName[listPosition])
									self.currentData=int(self.currentData)
								else:
									#NORMAL read of clock data LIST type
									self.currentData=game.getClockData(self.varClock, self.varName[listPosition])
									self.currentData=int(self.currentData)
							else:
								#NORMAL read of clock data
								self.currentData=game.getClockData(self.varClock, self.varName)
								self.currentData=int(self.currentData)

						elif RW=='W':
							if isinstance(self.varName, list):
								if self.currentMenuString=='setClock':
									linescoreORbaseball=game.gameData['sportType']=='linescore' or game.gameData['sportType']=='baseball'
									BB1andBB3andNOThoursFlagJumper=self.sport=='MMBASEBALL3' or self.sport=='MPBASEBALL1' and not game.gameSettings['hoursFlagJumper']
									if linescoreORbaseball:
										if not BB1andBB3andNOThoursFlagJumper:
											Vars=self._clockSequence(game, self.varName[0], self.varName[1], self.varName[2])
											if Vars[1]>59:
												game=self.exitMenu(game)
												return game
											time=Vars[0]*60*60+Vars[1]*60+Vars[2]
											game.clockDict[self.varClock].Reset(time)
										else:
											Vars=self._clockSequence(game, self.varName[0], self.varName[1])
											if Vars[1]>59:
												game=self.exitMenu(game)
												return game
											time=Vars[0]*60+Vars[1]
											game.clockDict[self.varClock].Reset(time)
									else:
										Vars=self._clockSequence(game, self.varName[0], self.varName[1])
										if Vars[1]>59:
											game=self.exitMenu(game)
											return game
										time=Vars[0]*60+Vars[1]
										game.clockDict[self.varClock].Reset(time)
								elif self.currentMenuString=='setClockTenthSec':
									Vars=self._clockTenthsSequence(game, self.varName[0], self.varName[1])
									if Vars[0]>59:
										game=self.exitMenu(game)
										return game
									time=Vars[0]+float(Vars[1])/10
									game.clockDict[self.varClock].Reset(time)
								elif (self.currentMenuString=='guestPenalty' or self.currentMenuString=='homePenalty') and self.menuNumber%2==0:
									Vars=self._clockSequence(game, self.varName[0], self.varName[1])
									if Vars[1]>59:
										game=self.exitMenu(game)
										return game
									time=Vars[0]*60+Vars[1]
									penaltyTeamNumberString, timerNumber=self._getCurrentTeamAndTimerNumber()
									clockName=self.varClock+str(timerNumber)+'_'+'team'+penaltyTeamNumberString
									game.clockDict[clockName].Reset(time)
								elif self.currentMenuString=='timeOutTimer' and self.menuNumber==2:
									Vars=self._clockSequence(game, self.varName[0], self.varName[1])
									if Vars[1]>59:
										game=self.exitMenu(game)
										return game
									time=Vars[0]*60+Vars[1]
									game.clockDict[self.varClock].Reset(time)
								elif self.currentMenuString=='timeOfDay' and self.menuNumber>2:
									Vars=self._clockSequence(game, self.varName[0], self.varName[1])
									if Vars[1]>59 or Vars[0]<1 or (Vars[0]>24 and Vars[1]>59):
										game=self.exitMenu(game)
										return game
									time=Vars[0]*60*60+Vars[1]*60
									game.clockDict[self.varClock].Reset(time)

								else:
									#NORMAL write of clock data LIST type not used
									print 'NOTHING SAVED'
							else:
								#NORMAL write of clock data
								game.setClockData(self.varClock, self.varName, self.numpadSequence, self.places)
					else:
						if RW=='R':
							#NORMAL read of game data
							self.currentData=game.getGameData(self.varName)
						elif RW=='W':
							if self.currentMenuString=='setRuns_Innings':
								self.editInning=self.numpadSequence
							else:
								#NORMAL write of game data
								game.setGameData(self.varName, self.numpadSequence, self.places)
		else:
			#If MenuMap row does not effect data go here (Such as a menu showing a temporary message)
			if RW=='R':
				self.currentData=None
			elif RW=='W':
				pass
		#For verbose display of currentData only
		if RW=='R':
			verbose(['self.currentData:', self.currentData], self.verbose)
		elif RW=='W':
			pass
		return game

	def _activePlayerListSort(self, game):
		if game.gameSettings['currentTeamGuest']:
			game.activeGuestPlayerList.sort()
		else:
			game.activeHomePlayerList.sort()
		return game

	def _updateActivePlayerList(self, game, removeFlag=False):
		activePlayerList, team, teamName=activePlayerListSelect(game)

		if removeFlag:
			activePlayerList.remove(game.gameSettings['playerNumber'])
		else:
			activePlayerList.append(game.gameSettings['playerNumber'])

		if len(activePlayerList)==0:
			game.gameSettings['playerNumber']='  '

		print 'guest active', game.activeGuestPlayerList, 'home active', game.activeHomePlayerList


	#Button Press Functions----------------------------------------

	def menuOn(self, game):
		if not self.menuFlag:
			self.startFlag=True
		self.menuFlag=True
		verbose(['\nmenuOn - self.menuFlag:', self.menuFlag, 'self.startFlag:', self.startFlag], self.verbose)
		return game

	def _menuOff(self, game): #not currently used
		self.menuFlag=False
		return game

	def doNothing(self, game):
		'''Duh!'''
		verbose(['\nDoing Nothing...', 'funcString', self.funcString, 'currentMenuString', self.currentMenuString], self.verbose)
		return game

	def Numbers(self, game, key):
		'''Common method for any number key press.'''
		verbose(['\nNumbers - key:', key], self.verbose)
		if self.menuFlag:
			self.numberPressedFlag=True
			self.lastNumberPressed = key
			self.numberPressedSequence.append(str(key))
			verbose(['self.lastNumberPressed:', key, 'self.numberPressedSequence', self.numberPressedSequence], self.verbose)
			game = self.funcDict[self.currentMenuString](game)# call LCD function
		else:
			game=self.exitMenu(game)
		return game

	def Number_7_ABC(self, game):
		key=7
		self.Numbers(game, key)
		return game

	def Number_8_DEF(self, game):
		key=8
		self.Numbers(game, key)
		return game

	def Number_9_GHI(self, game):
		key=9
		self.Numbers(game, key)
		return game

	def Number_4_JKL(self, game):
		key=4
		self.Numbers(game, key)
		return game

	def Number_5_MNO(self, game):
		key=5
		self.Numbers(game, key)
		return game

	def Number_6_PQR(self, game):
		key=6
		self.Numbers(game, key)
		return game

	def Number_1_STU(self, game):
		key=1
		self.Numbers(game, key)
		return game

	def Number_2_VWX(self, game):
		key=2
		self.Numbers(game, key)
		return game

	def Number_3_YZ(self, game):
		key=3
		self.Numbers(game, key)
		return game

	def Number_0(self, game):
		key=0
		self.Numbers(game, key)
		return game

	def clear_(self, game):
		if self.menuFlag:
			self.clearFlag=True
		verbose(['\nclear_ - self.clearFlag:', self.clearFlag], self.verbose)
		return game

	def enter_(self, game):
		if self.menuFlag:
			self.enterFlag=True
		verbose(['\nenter_ - self.enterFlag:', self.enterFlag], self.verbose)
		return game

	def Splash(self, game):
		'''Splash screen used to display basic setting information after a game reset.'''
		name='Splash'+str(self.menuNumber)
		self.loadMenuMapValues(game, name)
		self.currentMenuString='Splash'
		if self.menuNumber==1:
			self.startFlag=False
			print 'Version:', game.configDict['Version'], 'sport:', game.sport, 'option jumpers:', game.configDict['optionJumpers'], 'restoreFlag:', game.gameSettings['restoreFlag']
			self.currentData=game.configDict['Version']
			self.showCurrentMenu(game, overrideData=1)
			if game.gameData['sportType']=='linescore' or game.gameData['sportType']=='basketball' or game.sport[:7]=='MPMULTI':
				if game.sport[:4]=='MPMP':
					self.row2=game.sport[2:8]+'      '+game.configDict['optionJumpers']
				else:
					self.row2=game.sport[2:12]+'  '+game.configDict['optionJumpers']
			elif game.gameData['sportType']=='stat':
				self.row2=game.sport[2:6]+'        '+game.configDict['optionJumpers']
			elif game.sport[:4]=='MPLX':
				self.row2=game.sport[2:8]+'      '+game.configDict['optionJumpers']
			elif game.gameData['sportType']=='GENERIC' or game.gameData['sportType']=='cricket':
				self.row2=game.sport[2:9]+'     '+game.configDict['optionJumpers']
			elif game.gameData['sportType']=='soccer':
				if game.sport[8]=='1':
					self.row2=game.sport[2:8]+'      '+game.configDict['optionJumpers']
				else:
					self.row2=game.sport[2:11]+'   '+game.configDict['optionJumpers']
			elif game.gameData['sportType']=='hockey' or game.gameData['sportType']=='racetrack':
				if game.sport[8]=='1':
					self.row2=game.sport[2:8]+'      '+game.configDict['optionJumpers']
				else:
					self.row2=game.sport[2:11]+'   '+game.configDict['optionJumpers']
			else:
				print game.gameData['optionJumpers']
				self.row2=game.sport[2:10]+'_'+game.sport[10]+'  '+game.configDict['optionJumpers']
		return game

	def NewGame(self, game):
		self.menuOn(game)
		return game

	def periodClockReset(self, game):
		verbose(['currentMenuString', self.currentMenuString, 'keypadType', game.configDict['keypadType'], 'menuNumber', self.menuNumber], self.verbose)
		if self.currentMenuString=='NewGame' and game.configDict['keypadType']=='MM':
			game.gameSettings['resetGameFlag']=True
			game=self.exitMenu(game)
		return game

	def guestScorePlusOne(self, game):
		verbose(['currentMenuString', self.currentMenuString, 'keypadType', game.configDict['keypadType'], 'menuNumber', self.menuNumber], self.verbose)
		if self.currentMenuString=='NewGame' and game.configDict['keypadType']=='MM' and self.menuNumber==1:
			game.gameSettings['dimmingFlag']=True
			game.gameSettings['brightness']=game.gameSettings['dimmingCount']+18
			print 'Brightness set to', game.gameSettings['brightness']
			game.gameSettings['dimmingCount']+=9
			if game.gameSettings['dimmingCount']>9*5: #cycles back to lowest brightness
				game.gameSettings['dimmingCount']=0
			game=self.exitMenu(game)
		return game

	def homeScorePlusOne(self, game):
		verbose(['currentMenuString', self.currentMenuString, 'keypadType', game.configDict['keypadType'], 'menuNumber', self.menuNumber], self.verbose)
		if self.currentMenuString=='NewGame' and game.configDict['keypadType']=='MM' and self.menuNumber==1:
			game.gameSettings['dimmingFlag']=True
			game.gameSettings['brightness']=game.gameSettings['dimmingCount']+18
			print 'Brightness set to', game.gameSettings['brightness']
			game.gameSettings['dimmingCount']-=9
			if game.gameSettings['dimmingCount']>9*5: #cycles back to lowest brightness
				game.gameSettings['dimmingCount']=0
			game=self.exitMenu(game)
		return game

	def yardsToGoReset(self, game):
		self.menuOn(game)
		return game

	def assignErrorToggle(self, game):
		self.assignErrorCount-=1
		if self.assignErrorCount<=0:
			game.gameSettings['assignErrorFlashEnable'] = False
			game.gameData['errorPosition']=255
			game.gameData['errorIndicator']=False
		else:
			if game.gameData['errorPosition']==255:
				game.gameData['errorPosition']=self.errorPosition
				game.gameData['errorIndicator']=True
			else:
				game.gameData['errorPosition']=255
				game.gameData['errorIndicator']=False
			threading.Timer(game.gameSettings['assignErrorFlashDuration'], self.assignErrorToggle, [game]).start()
		return game

	def assignError(self, game):
		self.menuOn(game)
		return game

	def setClock(self, game):
		if not game.clockDict['periodClock'].running:
			self.menuOn(game)
		return game

	def clockUpDown(self, game):
		if not game.clockDict['periodClock'].running:
			self.menuOn(game)
		return game

	def setClockTenthSec(self, game):
		if game.gameSettings['periodClockTenthsFlag'] and not game.clockDict['periodClock'].running and not game.gameSettings['clock_3D_or_less_Flag']:
			self.menuOn(game)
		return game

	def tenthSecOnOff(self, game):
		if not game.clockDict['periodClock'].running and not game.gameSettings['clock_3D_or_less_Flag'] \
		and not game.gameData['sportType']=='baseball' or game.gameData['sport']=='MPMULTISPORT1-baseball'or game.gameData['sport']=='MPLX3450-baseball':
			self.menuOn(game)
		else:
			self.menuOn(game)
		return game

	def autoHorn(self, game):
		self.menuOn(game)
		return game

	def timeOfDay(self, game):
		self.menuOn(game)
		return game

	def timeOutTimer(self, game):
		if game.gameSettings['timeOutTimerEnable'] and not self.menuFlag:
			game.gameSettings['timeOutTimerEnable']=False
			clockName='timeOutTimer'
			game.clockDict[clockName].Stop()
			game.clockDict[clockName].Reset()
			return game
		if not (game.gameData['sportType']=='baseball' or game.gameData['sportType']=='linescore'):
			self.menuOn(game)
		return game

	def setBatterNumber(self, game):
		if not game.gameData['sportType']=='baseball' or game.gameData['sport']=='MPMULTISPORT1-baseball'or game.gameData['sport']=='MPLX3450-baseball':
			self.menuOn(game)
		return game

	def setPitchCounts(self, game):
		self.menuOn(game)
		return game

	def setGuestScore(self, game):
		self.menuOn(game)
		return game

	def setHomeScore(self, game):
		self.menuOn(game)
		return game

	def playClocks(self, game):
		self.menuOn(game)
		return game

	def setYardsToGo(self, game):
		self.menuOn(game)
		return game

	def setBallOn(self, game):
		self.menuOn(game)
		return game

	def setTotalRuns(self, game):
		self.menuOn(game)
		return game

	def setTotalHits(self, game):
		self.menuOn(game)
		return game

	def setTotalErrors(self, game):
		self.menuOn(game)
		return game

	def setRuns_Innings(self, game):
		self.menuOn(game)
		return game

	def setInningTop_Bot(self, game):
		self.menuOn(game)
		return game

	def setGuestTimeOuts(self, game):
		self.menuOn(game)
		return game

	def setHomeTimeOuts(self, game):
		self.menuOn(game)
		return game

	def play_shotClocks(self, game):
		if self.funcString=='play_shotClocks':
			if game.gameData['sportType']=='soccer':
				self.funcString='playClocks'
			else:
				self.funcString='shotClocks'
		self.menuOn(game)
		return game

	def shotClocks(self, game):
		self.menuOn(game)
		return game

	def playerMatchGame(self, game):
		self.menuOn(game)
		return game

	def playerFoul(self, game):
		self.menuOn(game)
		return game

	def setGuestFunctions(self, game):
		self.menuOn(game)
		return game

	def setHomeFunctions(self, game):
		self.menuOn(game)
		return game

	def guestPenalty(self, game):
		self.menuOn(game)
		return game

	def homePenalty(self, game):
		self.menuOn(game)
		return game

	#STAT-------------------------------------------------

	def addPlayer(self, game):
		self.menuOn(game)
		return game

	def deletePlayer(self, game):
		self.menuOn(game)
		return game

	def subPlayer(self, game):
		self.menuOn(game)
		return game

	def editPlayer(self, game):
		self.menuOn(game)
		return game

	def displaySize(self, game):
		#self.menuOn(game)
		return game

	def nextPlayer(self, game):
		#self.menuOn(game)
		return game

	def previousPlayer(self, game):
		#self.menuOn(game)
		return game

	#CRICKET-------------------------------------------------

	def setPlayer1Number(self, game):
		self.menuOn(game)
		return game

	def setPlayer2Number(self, game):
		self.menuOn(game)
		return game

	def setPlayer1Score(self, game):
		self.menuOn(game)
		return game

	def setPlayer2Score(self, game):
		self.menuOn(game)
		return game

	def setTotalScore(self, game):
		self.menuOn(game)
		return game

	def setOvers(self, game):
		self.menuOn(game)
		return game

	def setLastMan(self, game):
		self.menuOn(game)
		return game

	def setLastWicket(self, game):
		self.menuOn(game)
		return game

	def set1eInnings(self, game):
		self.menuOn(game)
		return game

	def teamNameMenu(self, game):
		self.menuOn(game)
		return game

	def segmentTimerMenu(self, game):
		self.menuOn(game)
		return game

	#Methods for use with test function below

	def _testLCDsequence(self, game, buttonSequence):
		print
		for function in buttonSequence:
			self.Map(game, function)
			print '---------------------------------------------'
			raw_input()

def test():
	'''Test function if module ran independently.'''
	print "ON"
	c=Config()
	sport='MPSTAT'
	c.writeSport(sport)
	game = selectSportInstance(sport)
	lcd=Menu_Event_Handler(sport)
	printDict(lcd.__dict__, 1)
	buttonSequence=['addPlayer', 'Number_0_&-.!', 'Number_1_STU', 'enter', 'enter', 'deletePlayer', 'Number_1_STU', 'enter']
	#buttonSequence=['clockUpDown', 'Number_1_STU']
	#buttonSequence=['None', 'NewGame', 'Number_2_VWX', 'NewGame', 'NewGame', 'Number_5_MNO', 'Number_3_YZ', 'Number_4_JKL', 'enter', 'setTotalErrors', 'enter', 'clear']
	#buttonSequence=['clockUpDown', 'Number_1_STU', 'Number_1_STU', 'Number_1_STU']
	lcd._testLCDsequence(game, buttonSequence)

if __name__ == '__main__':
	from Config import Config
	test()

'''
self.funcDict.update({'Number_7_ABC':self.Number_7_ABC, 'Number_8_DEF':self.Number_8_DEF, 'Number_9_GHI':self.Number_9_GHI, \
'Number_5_MNO':self.Number_5_MNO, 'Number_6_PQR':self.Number_6_PQR,  'Number_1_STU':self.Number_1_STU, \
'Number_2_VWX':self.Number_2_VWX, 'Number_3_YZ':self.Number_3_YZ,'Number_4_JKL':self.Number_4_JKL,'Number_0_&-.!':self.Number_0,\
'clear':self.clear_, 'enter':self.enter_, 'clear_FlashHit':self.clear_,'enter_FlashError':self.enter_})
'''
