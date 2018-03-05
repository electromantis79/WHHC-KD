#!/usr/bin/env python

# by Craig Gunter
#
# "LCD_16X2_Display_Handler module"
#
# LCD_16X2_Display_Handler()Input = None
#
# 		Initalize() = Set defaults for correct sport
#
#
#			main() =

from time import sleep
from clock import clock

from Game import *
from GameDefaultSettings import *
#from LCD_16X2_Display import Adafruit_CharLCDPlate

def verbose(messages, enable=1):
	#Use list format for messages
	if enable:
		for x, message in enumerate(messages):
			if x==len(messages)-1:
				print message
			else:
				print message,

class LCD_16X2_Display_Handler(object):
	vboseList=[1,1,0]
	#verbose([], self.verbose)
	verbose=vboseList[0] #Method Name or arguments
	verboseMore=vboseList[1] #Deeper loop information in methods
	verboseMost=vboseList[2] #Crazy Deep Stuff

	def __init__(self, sport='MPBASEBALL1', splashTime=5):
		verbose(['\nCreating LCD_16X2_Display_Handler object'], self.verbose)
		self.sport=sport
		self.splashTime = splashTime
		from Game import readGameDefaultSettings
		self.gameSettings=readGameDefaultSettings()
		self.menuTimerDuration = self.gameSettings['menuTimerDuration']

		self.enterFlag = False
		self.clearFlag = False
		self.menuFlag = False
		self.startFlag = False
		self.currentMenuString = ''
		self.funcString=''

		self.lastVarName=''
		self.lastCol=0
		self.lastRow=0
		self.lastPlaces=1
		self.lastTeam=255
		self.lastBlockNumList=[]
		self.lastVarClock=False

		self.splashTimer=clock(False, self.splashTime)
		self.menuTimer=clock(False, self.menuTimerDuration)
		self.NewGameMenu=1

		self.menuNumber=1
		self.startingMenuNumber=1
		self.endingMenuNumber=1

		self.numberPressedSequence=[]
		self.lcdTextDisplay='Blank'
		self.row1=''
		self.row2=''

		self.precisionMenuFlag=False
		self.dimmingMenuFlag=False
		self.teamNameMenuFlag=False
		self.segmentTimerMenuFlag=False
		self.addVariableFlag=True

		self.mappedFlag = False
		self.internalRefreshFlag = False

		self.numberPressedFlag = False

		self.buildFuncDict()
		self.Menu_LCD_Text = self.readLCDButtonMenus()
		verbose([self.Menu_LCD_Text], self.verboseMost)

	def buildFuncDict(self):
		#All games
		self.funcDict = {'NewGame':self.NewGame,'setClock':self.setClock, 'setClockTenthSec':self.setClockTenthSec, \
		'autoHorn':self.autoHorn, 'timeOfDay':self.timeOfDay, 'timeOutTimer':self.timeOutTimer, \
		'setHomeScore':self.setHomeScore,'setGuestScore':self.setGuestScore,'clockUpDown':self.clockUpDown,\
		'playClocks':self.playClocks, 'shotClocks':self.shotClocks,'tenthSecOnOff':self.tenthSecOnOff, \
		'NewGame_2':self.NewGame_2, 'NewGame_3':self.NewGame_3, 'NewGame_4':self.NewGame_4, 'NewGame_5':self.NewGame_5, \
		'NewGame_6':self.NewGame_6, 'NewGame_7':self.NewGame_7, 'NewGame_8':self.NewGame_8, 'NewGame_9':self.NewGame_9, \
		'periodClockReset':self.periodClockReset, 'guestScorePlusOne':self.guestScorePlusOne,'homeScorePlusOne':self.homeScorePlusOne}

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
		self.funcDict.update({'clear_GuestGoal':self.clear_,'enter_HomeGoal':self.enter_,'play_shotClocks':self.shotClocks,\
		'setGuestFunctions':self.setGuestFunctions, 'setHomeFunctions':self.setHomeFunctions,\
		'guestPenalty':self.guestPenalty, 'homePenalty':self.homePenalty,})

			#no nothing--------------------------------------------------------------
		self.funcDict.update({'guestShotsPlusOne':self.doNothing,'homeShotsPlusOne':self.doNothing,'qtrs_periodsPlusOne':self.doNothing,\
		'guestPenaltyPlusOne':self.doNothing, 'homePenaltyPlusOne':self.doNothing,\
		'guestKicksPlusOne':self.doNothing,'homeKicksPlusOne':self.doNothing,\
		'guestSavesPlusOne':self.doNothing,'homeSavesPlusOne':self.doNothing})

		#soccer
		self.funcDict.update({'setGuestFunctions':self.setGuestFunctions, 'setHomeFunctions':self.setHomeFunctions, \
		'play_shotClocks':self.playClocks,'clear_GuestGoal':self.clear_,'enter_HomeGoal':self.enter_})

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

	def readLCDButtonMenus(self):
		LCDtext='Spreadsheets/LCDtext.csv'
		csvReader=csv.DictReader(open(LCDtext, 'rb'), delimiter=',', quotechar="'")
		function=[]
		dictionary = {}
		count=0
		for row in csvReader:
			try:
				#print 'row', row
				values=row.values()
				#print values
				function.append(row['FUNCTION'])
				keys=row.keys()
				#print keys
				del row['FUNCTION']
				#print 'len-row', len(row)
				for i in range(len(row)+1):
					#raw_input('\nPress Enter to continue through loop\n')
					#print 'i', i
					#print values[i]
					if values[i]=='':
						#print '\nDeleting ', keys[i], ' because it is empty.\n'
						del row[keys[i]]
					else:
						#print 'value', values[i]
						if values[i].find('&')!=-1:
							if values[i].find('&')==0:
								row1=None
								row2=values[i][values[i].find('&')+1:]
							else:
								row1=values[i][:values[i].find('&')]
								row2=values[i][values[i].find('&')+1:]
							row[keys[i]]={'ROW_1':row1, 'ROW_2':row2}
				#print row
				if row:
					dictionary[function[count]]=row

				#print dictionary

			except ValueError:
				print 'error'
			count+=1
		return dictionary

	def getMenu(self, function, menuNumber=1):
		#display message from LCDtext.csv
		if menuNumber:
			row1=self.Menu_LCD_Text[function]['MENU_'+str(menuNumber)]['ROW_1']
			row2=self.Menu_LCD_Text[function]['MENU_'+str(menuNumber)]['ROW_2']
			if row1:
				self.row1=row1
				self.row2=row2
			else:
				self.row2=row2

	def Map(self, game, funcString):
		verbose(['\nMap start-------'], self.verbose)

		if self.menuFlag:
			verbose(['\ncontinueChain start-------'], self.verbose)
			game = self.continueChain(game, funcString)
			verbose(['\nRefreshScreen start-------'], self.verbose)
			self.RefreshScreen(game)
		else:
			verbose(['\nstartChain start-------'], self.verbose)
			game = self.startChain(game, funcString)

		return game

	def startChain(self, game, funcString):
		self.menuFlag=True
		game.gameSettings['menuFlag']=True
		self.startFlag=True
		self.currentMenuString=funcString
		self.funcString=funcString
		self.menuTimer.Start()
		game = self.allButtons(game)
		verbose(['key pressed:', self.funcString, '     current menu:', self.currentMenuString], self.verbose)
		verbose(['\nCalling LCD function', self.funcString], self.verbose)
		self.funcDict[self.funcString](game)
		return game

	def continueChain(self, game, funcString):
		self.funcString=funcString
		verbose(['key pressed:', self.funcString, '     current menu:', self.currentMenuString], self.verbose)
		self.allButtons(game)
		if game.gameSettings['lampTestFlag'] or game.gameSettings['blankTestFlag']:
			if self.funcString=='clear_FlashHit' or self.funcString=='clear_GuestGoal' or \
			self.funcString=='clear_' or (self.funcString=='NewGame' and self.currentMenuString=='NewGame_4')\
			 or (self.funcString=='NewGame' and self.currentMenuString=='NewGame_5'):
				verbose(['\nCalling LCD function', self.funcString], self.verbose)
				self.funcDict[self.funcString](game)# call LCD function
		else:
			self.menuTimer.Start()
			verbose(['\nCalling LCD function', self.funcString], self.verbose)
			self.funcDict[self.funcString](game)# call LCD function
		return game

	def endChain(self, game):
		self.menuNumber=1
		self.startingMenuNumber=1
		self.endingMenuNumber=1
		self.startFlag=False
		self.enterFlag=False
		self.clearFlag=False
		self.menuFlag=False
		game.gameSettings['menuFlag']=False
		self.refreshDefaultScreenFlag=True
		self.precisionMenuFlag=False
		self.dimmingMenuFlag=False
		self.teamNameMenuFlag=False
		self.segmentTimerMenuFlag=False
		game.gameSettings['lampTestFlag']=False
		game.gameSettings['blankTestFlag']=False
		self.menuTimer.Stop()
		self.menuTimer.Reset()

		self.numberPressedFlag = False
		self.lastNumberPressed = 255
		self.numberPressedSequence=[]
		self.NewGameMenu=1

		self.currentMenuString=''
		self.funcString=''
		verbose(['\nEnd menu chain!!!!!'], self.verbose)
		return game

	def RefreshScreen(self, game):
		verbose(['\nmainInfoScreen start-------'], self.verbose)
		if not self.menuFlag:
			verbose(['Not in a menu'], self.verbose)
			if game.clockDict['periodClock'].countUp:
				clockType='U'
			else:
				clockType='D'
			if game.gameSettings['precisionEnable']:
				clockType='P'
			verbose(['Calling', game.gameData['sportType'], 'Default Screen'])
			if game.gameData['sportType']=='baseball':
				self.baseballScreen(game, clockType)
			elif game.gameData['sportType']=='linescore':
				self.linescoreScreen(game, clockType)
			elif game.gameData['sportType']=='football':
				self.footballScreen(game, clockType)
			elif game.gameData['sportType']=='soccer':
				self.soccerScreen(game, clockType)
			elif game.gameData['sportType']=='hockey':
				self.hockeyScreen(game, clockType)
			elif game.gameData['sportType']=='basketball':
				self.basketballScreen(game, clockType)
			elif game.gameData['sportType']=='cricket':
				self.cricketScreen(game, clockType)
			if self.verbose:
				self.lcdDefaultScreen = '\n ------LCD------\n'+self.row1+'\n'+self.row2
				verbose([self.lcdDefaultScreen], self.verbose)
		else:
			if self.verbose:
				self.lcdDefaultScreen = '\n ------LCD------\n'+self.row1+'\n'+self.row2
				verbose(['Still in a menu - No Default Screen', self.lcdDefaultScreen], self.verbose)

	def baseballScreen(self, game, clockType):
		if game.gameData['hitIndicator']:
			hit='H'
		else:
			hit=' '
		if game.gameData['errorIndicator']:
			error='E'
		else:
			error=' '
		self.row1 = '%02d %s%02d:%02d %2d  %02d' % (\
		game.getTeamData(game.guest, 'score'), \
		clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, game.getGameData('inning'), \
		game.getTeamData(game.home, 'score')\
		)
		self.row2 = '%s%3d %d-%d-%d %3d %s' % (hit, game.getTeamData(game.guest, 'pitchCount'), \
		game.gameData['balls'], game.gameData['strikes'], game.gameData['outs'], game.getTeamData(game.home, 'pitchCount'), error)

	def linescoreScreen(self, game, clockType):
		if game.gameSettings['inningBot']:
			innType='B'
		else:
			innType='T'
		if game.gameSettings['linescoreStart']:
			innType='B'
			inn='- '
			self.row1 = '%02d %s%02d:%02d %s%s %02d' % (\
			game.getTeamData(game.guest, 'score'), \
			clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, innType, inn, \
			game.getTeamData(game.home, 'score')\
			)
		else:
			inn=game.getGameData('inning')
			self.row1 = '%02d %s%02d:%02d %s%02d %02d' % (\
			game.getTeamData(game.guest, 'score'), \
			clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, innType, inn, \
			game.getTeamData(game.home, 'score')\
			)
		self.row2 = '%d %02d %d-%d-%d  %02d %d' % (game.getTeamData(game.guest, 'errors'), game.getTeamData(game.guest, 'hits'), \
		game.gameData['balls'], game.gameData['strikes'], game.gameData['outs'], game.getTeamData(game.home, 'hits'), game.getTeamData(game.home, 'errors'))

	def footballScreen(self, game, clockType):
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
		clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, game.gameData['quarter'], \
		game.getTeamData(game.home, 'score')\
		)
		self.row2 = '%s%d  %d %02d %02d   %d%s' % (leftPoss, game.getTeamData(game.guest, 'timeOutsLeft'), \
		game.gameData['down'], game.gameData['yardsToGo'], game.gameData['ballOn'], game.getTeamData(game.home, 'timeOutsLeft'), rightPoss)

	def soccerScreen(self, game, clockType):
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
		clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, \
		rightGoal, game.getTeamData(game.home, 'score')\
		)
		self.row2 = ' %02d %02d %d  %02d %02d' % (game.getTeamData(game.guest, 'shots'), \
		game.getTeamData(game.guest, 'kicks'), game.gameData['period'], \
		game.getTeamData(game.home, 'kicks'), game.getTeamData(game.home, 'shots'))

	def hockeyScreen(self, game, clockType):
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
		clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, \
		game.getTeamData(game.home, 'score')\
		)
		self.row2 = '%s%02d    %d     %02d%s' % (leftGoal, game.getTeamData(game.guest, 'shots'), \
		game.gameData['period'], game.getTeamData(game.home, 'shots'), rightGoal)

	def basketballScreen(self, game, clockType):
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
		clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, game.gameData['period'], \
		game.getTeamData(game.home, 'score')\
		)
		self.row2 = '%s%s %02d %02d %d %02d %s%s' % (leftPoss, leftBonus, game.getTeamData(game.guest, 'fouls'), \
		playNum, playFoul, game.getTeamData(game.home, 'fouls'), rightBonus, rightPoss)

	def cricketScreen(self, game, clockType):
		self.row1 = '%03d %s%02d:%02d %d %03d' % (\
		game.gameData['player1Score'], clockType, game.clockDict['periodClock'].minutes, game.clockDict['periodClock'].seconds, game.gameData['wickets'], \
		game.gameData['player2Score']\
		)
		self.row2 = '  %02d  %03d  %02d   ' % (game.gameData['player1Number'], game.gameData['totalScore'], game.gameData['player2Number'])

	#MEAT!!!!!!!!!!!!!!
	def _digitSequence(self, game, places=1):
		if self.verbose:
			print '\n_digitSequence start-------'
			print 'Places', places
		if places==1 or len(self.numberPressedSequence)==1:
			data=self.lastNumberPressed
		elif places==2 or len(self.numberPressedSequence)==2:
			data=int(self.numberPressedSequence[-1]) + int(self.numberPressedSequence[-2])*10
		elif places==3:
			data=int(self.numberPressedSequence[-1]) + int(self.numberPressedSequence[-2])*10 + int(self.numberPressedSequence[-3])*100
		if self.verbose:
			print 'Return (data)=', data
		return data

	def addVariable(self, data, col, row,  places):
		if self.addVariableFlag:
			if self.verbose:
				print '\naddVariable start-------'
				print 'Data', data, 'Column', col, 'Row', row, 'Places', places
			if places=='1' or places==1:
				variable='%d' % (data)
			elif places=='2' or places==2:
				variable='%02d' % (data)
			elif places=='3' or places==3:
				variable='%03d' % (data)
			if self.verbose:
				print 'Variable', variable
			if row:
				self.row2=self.row2[:col]+variable+self.row2[col+int(places):]
			else:
				self.row1=self.row1[:col]+variable+self.row1[col+int(places):]

	def getCurrentData(self, game, varName, team, varClock):
		if self.verbose:
			print '\ngetCurrentData start-------'
			print 'VarName', varName, 'Team', team, 'VarClock', varClock
		if varName:
			if team==255:
				if varClock:
					currentData=game.getClockData('periodClock', varName)
				else:
					currentData=game.getGameData(varName)
			else:
				currentData=game.getTeamData(team, varName)
			currentData=int(currentData)
		else:
			currentData=None
		if self.verbose:
			print 'Return (currentData)=', currentData
		return currentData

	def genericSetValue(self, game, varName=None, col=14, row=1, places=1, team=255, blockNumList=[], varClock=False):
		if self.verbose:
			print '\ngenericSetValue start-------'
			print 'VarName', varName, 'Column', col, 'Row', row, 'Places', places, 'Team', team, 'BlockNumList', blockNumList, 'VarClock', varClock
		currentData=self.getCurrentData(game, varName, team, varClock)

		#Act according to which button was pressed----------------------------

		if self.startFlag:
			#First pass only
			if self.verbose:
				print '\nFirst menu------------------------------------'
			self.startFlag=False

		elif self.blockNumber(game, blockNumList):
			#Quit if number is in block list
			return game

		elif self.clearFlag:
			#Clear pressed
			if self.verbose:
				print '\nClear pressed. MenuNumber', self.menuNumber
			self.numberPressedFlag=False
			self.numberPressedSequence=[]

		elif self.enterFlag:
			#Enter pressed
			if self.verbose:
				print '\nEnter pressed. MenuNumber', self.menuNumber
			if self.numberPressedFlag:
				#Save input to game
				game=self.saveGameVariable(game)
				self.numberPressedFlag=False
				self.numberPressedSequence=[]

		elif self.funcString==self.currentMenuString:
			#Menu button pressed twice
			if self.menuNumber>self.endingMenuNumber:
				self.endChain(game)
				return game

		elif self.numberPressedFlag:
			#Numbers Pressed will display on LCD if not in the block list
			if self.verbose:
				print '\nNumber pressed. MenuNumber', self.menuNumber
			currentData=self._digitSequence(game, places)

		else:
			if self.verbose:
				print '\nNo action taken', self.menuNumber
				return game

		self.updateMenu(game, currentData, col, row,  places, team)
		self.savePrevious(varName, col, row, places, team, blockNumList, varClock, currentData)
		return game

	def savePrevious(self, varName, col, row, places, team, blockNumList, varClock, currentData):
		self.lastVarName=varName
		self.lastCol=col
		self.lastRow=row
		self.lastPlaces=places
		self.lastTeam=team
		self.lastBlockNumList=blockNumList
		self.lastVarClock=varClock
		self.previousData=currentData

	def blockNumber(self, game, blockNumList):
		if self.numberPressedFlag and not self.enterFlag:
			if self.verbose:
				print '\nBlocked Key Check'
			for block in blockNumList:
				if self.lastNumberPressed==block:
					if self.verbose:
						print 'Blocked Key', block
					self.numberPressedSequence.pop()
					return 1
		return 0

	def saveGameVariable(self, game):
		if self.verbose:
			print '\nsaveGameVariable start-------'
		if self.verbose:
			print 'VarName', self.lastVarName, 'VarClock', self.lastVarClock, 'Places', self.lastPlaces, 'Team', self.lastTeam
		sequenceValue=self._digitSequence(game, self.lastPlaces)
		if self.verbose:
			print 'Sequence Value', sequenceValue
		if self.lastVarName:
			if self.lastTeam==255:
				#Save input to game variable if NOT team specific
				if self.lastVarClock:
					#Save input to game variable if in the clock instance
					game.setClockData('periodClock', self.lastVarName, sequenceValue, self.lastPlaces)
				else:
					#Save input to game variable
					game.setGameData(self.lastVarName, sequenceValue, self.lastPlaces)
					#vars(game)[self.lastVarName]=sequenceValue
			else:
				#Save input to game variable if team specific
				game.setTeamData(self.lastTeam, self.lastVarName, sequenceValue, self.lastPlaces)
		return game

	def updateMenu(self, game, currentData, col, row,  places, team):
		if self.verbose:
			print '\nupdateMenu start-------'
			print 'CurrentData', currentData, 'Column', col, 'Row', row, 'Places', places, 'Team', team
			print 'menuNumber', self.menuNumber, 'endingMenuNumber', self.endingMenuNumber
		if self.menuNumber<self.startingMenuNumber or self.menuNumber>self.endingMenuNumber:
			if self.verbose:
				print 'Outside menu range!!!!!'
			self.endChain(game)
		else:
			if self.verbose:
				print 'Display Menu', self.menuNumber, 'on LCD'
			if self.currentMenuString[:7]=='NewGame':
				if len(self.currentMenuString)>7:
					#NewGame numbered menus
					self.getMenu('NewGame', self.NewGameMenu)
					self.addVariable(currentData, col, row,  places)
				else:
					#NewGame Called it
					self.getMenu(self.currentMenuString, self.menuNumber)
					if currentData==255:
						currentData=0
					self.addVariable(currentData, col, row,  places)
			else:
				self.getMenu(self.currentMenuString, self.menuNumber)
				if currentData==255:
					currentData=0
				self.addVariable(currentData, col, row,  places)

	#Button Press Functions------------------------

	def allButtons(self, game):
		if self.verbose:
			print '\nallButtons start-------'
		if self.startFlag:
			pass
		else:
			if self.funcString==self.currentMenuString:
				self.numberPressedFlag=False
				self.numberPressedSequence=[]
				self.previousMenuNumber=self.menuNumber
				self.menuNumber+=1
				if self.verbose:
					print 'self.funcString==self.currentMenuString\n', 'menuNumber', self.menuNumber
			elif self.currentMenuString=='yardsToGoReset':
				self.endChain(game)
		return game

	def allMenuButtons(self, game):
		if self.verbose:
			print '\nallMenuButtons start-------'
		if self.startFlag:
			pass
		else:
			pass
		return 0

	def Numbers(self, game, key):
		if self.startFlag:
			self.endChain(game)
		if self.menuFlag:
			self.numberPressedFlag=True
			self.lastNumberPressed = key
			self.numberPressedSequence.append(str(key))
			if self.verbose:
				print '\nNumbers start-------'
				print 'lastNumberPressed', key, 'numberPressedSequence', self.numberPressedSequence
			game = self.funcDict[self.currentMenuString](game)# call LCD function
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
		if self.verbose:
			print '\nclear_ start-------'
		self.clearFlag=True
		if self.startFlag:
			self.endChain(game)
		else:
			self.previousMenuNumber=self.menuNumber
			self.menuNumber-=1
			if self.verbose:
				print 'Calling LCD Function', self.currentMenuString, '\nmenuNumber', self.menuNumber
			game = self.funcDict[self.currentMenuString](game)# call LCD function
		self.clearFlag=False
		return game

	def enter_(self, game):
		if self.verbose:
			print '\nenter_ start-------'
		self.enterFlag=True
		if self.startFlag:
			self.endChain(game)
		else:
			self.previousMenuNumber=self.menuNumber
			self.menuNumber+=1
			if self.verbose:
				print 'Calling LCD Function', self.currentMenuString, '\nmenuNumber', self.menuNumber
			game = self.funcDict[self.currentMenuString](game)# call LCD function
		self.enterFlag=False
		return game

	def Splash(self, game):
		self.splashTimer.Start()
		print 'Version:', game.configDict['Version'], 'sport:', game.sport, 'option jumpers:', game.configDict['optionJumpers'], 'restoreFlag:', game.gameSettings['restoreFlag']
		self.getMenu('Splash', 1)
		self.addVariable(data=int(game.configDict['Version']), col=13, row=0,  places='3')
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
			print game.configDict['optionJumpers']
			self.row2=game.sport[2:10]+'_'+game.sport[10]+'  '+game.configDict['optionJumpers']
		return game

	def NewGameSetValue(self, game, varName=None, col=14, row=1, places=1, team=255, blockNumList=[], varClock=False):
		if self.verbose:
			print '\nNewGameSetValue start-------'
			print 'VarName', varName, 'Column', col, 'Row', row, 'Places', places, 'Team', team, 'BlockNumList', blockNumList, 'VarClock', varClock
		currentData=self.getCurrentData(game, varName, team, varClock)

		#Act according to which button was pressed----------------------------

		if self.startFlag:
			#First pass only
			if self.verbose:
				print '\nFirst menu------------------------------------'
			self.startFlag=False
			self.numberPressedFlag=False
			if self.NewGameMenu==2:
				self.numberPressedSequence=[]
				blockNumList=[]
			elif self.NewGameMenu==7:
				currentData=1
				self.lastNumberPressed=1
			elif self.NewGameMenu==9:
				currentData=0
				self.lastNumberPressed=0
		elif self.blockNumber(game, blockNumList):
			#Quit if number is in block list
			return game

		elif self.clearFlag:
			#Clear pressed
			if self.verbose:
				print '\nClear pressed. MenuNumber', self.menuNumber

		elif self.enterFlag:
			#Enter pressed
			if self.verbose:
				print '\nEnter pressed. MenuNumber', self.menuNumber
			if self.precisionMenuFlag:
				if self.numberPressedFlag:
					if self.lastNumberPressed==1:
						game.gameSettings['precisionEnable']=True
			elif self.dimmingMenuFlag:
				if self.numberPressedFlag:
					if self._digitSequence(game, places)<=100 and self._digitSequence(game, places)>=50:
						if self.verbose:
							print '\nBrightness set to', game.gameSettings['brightness']
						game.gameSettings['brightness']=self._digitSequence(game, places)
						game.gameSettings['dimmingFlag']=True
						#send quantum dimming here
			elif self.teamNameMenuFlag:
				if self.numberPressedFlag:
					if self.lastNumberPressed==1:
						game=self.teamNameMenu(game)
				else:
					game=self.teamNameMenu(game)
				print "teamNameMenu"
			elif self.segmentTimerMenuFlag:
				if self.numberPressedFlag:
					if self.lastNumberPressed==1:
						game=self.segmentTimerMenu(game)
				print "segmentTimerMenu"
			elif self.NewGameMenu==1 and self.lastNumberPressed==1:
				game=self.Splash(game)
				game.gameData['resetGameFlag']=True
				return game
			else:
				#Do nothing
				if self.verbose:
					print '\nNo action taken after enter press'
			self.endChain(game)
			return game

		elif self.funcString==self.currentMenuString or self.funcString==self.currentMenuString[:7]:
			#Menu button pressed twice
			self.endChain(game)
			return game

		elif self.numberPressedFlag:
			#Numbers Pressed will display on LCD if not in the block list
			if self.verbose:
				print '\nNumber pressed. MenuNumber', self.menuNumber, 'NewGameMenu', self.NewGameMenu
			if self.NewGameMenu==1:
				if self.lastNumberPressed==0 or self.lastNumberPressed==1:
					currentData=self.lastNumberPressed
				else:
					self.NewGameMenu=self.lastNumberPressed
					self.NewGame(game)
					return game
			else:
				currentData=self._digitSequence(game, places)
		else:
			if self.verbose:
				print '\nNo action taken', self.menuNumber
				return game

		self.updateMenu(game, currentData, col, row,  places, team)
		self.savePrevious(varName, col, row, places, team, blockNumList, varClock, currentData)
		return game

	def NewGame(self, game):
		if self.allMenuButtons(game):
			return game
		if self.verbose:
			print '\nNewGame start-------'
			print '\nMenuNumber', self.menuNumber, 'NewGameMenu', self.NewGameMenu
		if not game.clockDict['periodClock'].running:
			if game.configDict['keypadType']=='MM':
				if self.menuNumber==1:
					self.menuNumber=4
				if self.verbose:
					print '\nMenuNumber', self.menuNumber
				self.endingMenuNumber=6
				if self.menuNumber==4:
					if self.funcString==self.currentMenuString:
						self.menuNumber+=1
					if self.verbose:
						print '\nMenuNumber', self.menuNumber
				elif self.menuNumber==5:
					self.currentMenuString='NewGame_5'
					self.NewGameMenu=5
					self.NewGame_5(game)
				elif self.menuNumber>=6:
					game.gameSettings['lampTestFlag']=False
					self.endChain(game)
				return game
			elif game.configDict['keypadType']=='MP':
				pass
		if self.menuNumber<self.startingMenuNumber:
			self.endChain(game)
		else:
			if self.NewGameMenu==1:
				self.NewGameSetValue(game, varName='resetGameFlag')
			elif self.NewGameMenu==2:
				self.currentMenuString='NewGame_2'
				self.startFlag=True
				self.NewGame_2(game)
			elif self.NewGameMenu==3:
				self.currentMenuString='NewGame_3'
				self.NewGame_3(game)
			elif self.NewGameMenu==4:
				self.currentMenuString='NewGame_4'
				self.NewGame_4(game)
			elif self.NewGameMenu==5:
				self.currentMenuString='NewGame_5'
				self.NewGame_5(game)
			elif self.NewGameMenu==6:
				self.currentMenuString='NewGame_6'
				self.NewGame_6(game)
			elif self.NewGameMenu==7:
				self.currentMenuString='NewGame_7'
				self.startFlag=True
				self.NewGame_7(game)
			elif self.NewGameMenu==8:
				self.currentMenuString='NewGame_8'
				self.startFlag=True
				self.NewGame_8(game)
			elif self.NewGameMenu>=9:
				self.currentMenuString='NewGame_9'
				self.startFlag=True
				self.NewGame_9(game)
		return game

	def NewGame_2(self, game):
		self.dimmingMenuFlag=True
		self.NewGameSetValue(game, varName='brightness', col=11, row=1, places=3)
		return game

	def NewGame_3(self, game):
		self.endChain(game)
		return game

	def NewGame_4(self, game):
		self.addVariableFlag=False
		game.gameSettings['blankTestFlag']=True
		self.NewGameSetValue(game)
		self.addVariableFlag=True
		return game

	def NewGame_5(self, game):
		self.addVariableFlag=False
		game.gameSettings['lampTestFlag']=True
		self.NewGameSetValue(game)
		self.addVariableFlag=True
		return game

	def NewGame_6(self, game):
		self.endChain(game)
		return game

	def NewGame_7(self, game):
		self.teamNameMenuFlag=True
		self.NewGameSetValue(game, varName=None, col=14, row=1, places=1, team=255, blockNumList=[2,3,4,5,6,7,8,9])
		return game

	def NewGame_8(self, game):
		self.precisionMenuFlag=True
		self.NewGameSetValue(game, varName='precisionEnable', col=14, row=1, places=1, team=255, blockNumList=[2,3,4,5,6,7,8,9])
		return game

	def NewGame_9(self, game):
		self.segmentTimerMenuFlag=True
		self.NewGameSetValue(game, varName=None, col=14, row=1, places=1, team=255, blockNumList=[2,3,4,5,6,7,8,9])
		return game

	def periodClockReset(self, game):
		if self.allMenuButtons(game):
			return game
		if self.verbose:
			print 'currentMenuString', self.currentMenuString, 'keypadType', game.configDict['keypadType'], 'menuNumber', self.menuNumber
		if self.currentMenuString=='NewGame':
			if game.configDict['keypadType']=='MM':
				if self.menuNumber==5:
					game.gameSettings['resetGameFlag']=True
		self.endChain(game)
		return game

	def guestScorePlusOne(self, game):
		if self.allMenuButtons(game):
			return game
		if self.verbose:
			print 'currentMenuString', self.currentMenuString, 'keypadType', game.configDict['keypadType'], 'menuNumber', self.menuNumber
		if self.currentMenuString=='NewGame':
			if game.configDict['keypadType']=='MM':
				if self.menuNumber==5:
					game.gameSettings['dimmingFlag']=True
					game.gameSettings['brightness']=game.gameSettings['dimmingCount']+18
					print 'Brightness set to', game.gameSettings['brightness']
					game.gameSettings['dimmingCount']+=9
					if game.gameSettings['dimmingCount']>9*5: #cycles back to lowest brightness
						game.gameSettings['dimmingCount']=0
		self.endChain(game)
		return game

	def homeScorePlusOne(self, game):
		if self.allMenuButtons(game):
			return game
		if self.verbose:
			print 'currentMenuString', self.currentMenuString, 'keypadType', game.configDict['keypadType'], 'menuNumber', self.menuNumber
		if self.currentMenuString=='NewGame':
			if game.configDict['keypadType']=='MM':
				if self.menuNumber==5:
					game.gameSettings['dimmingFlag']=True
					game.gameSettings['brightness']=game.gameSettings['dimmingCount']+18
					print 'Brightness set to', game.gameSettings['brightness']
					game.gameSettings['dimmingCount']+=9
					if game.gameSettings['dimmingCount']>9*5: #cycles back to lowest brightness
						game.gameSettings['dimmingCount']=0
		self.endChain(game)
		return game

	def teamNameMenu(self, game):
		self.endChain(game)
		return game

	def segmentTimerMenu(self, game):
		self.endChain(game)
		return game

	def _clockSequence(self, game, var1=0, var2=0):
		if self.verbose:
			print '\n_clockSequence start-------'
		if len(self.numberPressedSequence)==1:
			var1=0
			var2=int(self.numberPressedSequence[-1])
		elif len(self.numberPressedSequence)==2:
			var1=0
			var2=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
		elif len(self.numberPressedSequence)==3:
			var1=int(self.numberPressedSequence[-3])
			var2=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
		elif len(self.numberPressedSequence)>=4:
			var1=int(self.numberPressedSequence[-3])+int(self.numberPressedSequence[-4])*10
			var2=int(self.numberPressedSequence[-1])+int(self.numberPressedSequence[-2])*10
		if self.verbose:
			print 'Return (var1, var2)=', var1, var2
		return var1, var2

	def setClock(self, game):
		if self.allMenuButtons(game):
			return game
		if self.verbose:
			print '\nsetClock start-------'
		if self.startFlag:
			#First pass only
			if self.verbose:
				print '\nFirst menu------------------------------------'
			self.startFlag=False
			self.getMenu(self.currentMenuString, self.menuNumber)
			self.addVariable(game.getClockData('periodClock', 'minutes'), col=10, row=1,  places=2)
			self.addVariable(game.getClockData('periodClock', 'seconds'), col=13, row=1,  places=2)

		elif self.clearFlag:
			#Clear pressed
			if self.verbose:
				print '\nClear pressed. MenuNumber', self.menuNumber
			self.endChain(game)

		elif self.enterFlag:
			#Enter pressed
			if self.verbose:
				print '\nEnter pressed. MenuNumber', self.menuNumber
			if self.numberPressedFlag:
				#Save input to game
				minutes, seconds=self._clockSequence(game, game.getClockData('periodClock', 'minutes'), game.getClockData('periodClock', 'seconds'))
				if seconds>59:
					self.endChain(game)
					return game
				game.setClockData('periodClock', 'minutes', minutes)
				game.setClockData('periodClock', 'seconds', seconds)
				time=minutes*60+seconds# check later
				game.clockDict['periodClock'].Reset(time)
				self.endChain(game)
			else:
				self.endChain(game)
				return game

		elif self.funcString==self.currentMenuString:
			if self.verbose:
				print '\nMenu pressed. MenuNumber', self.menuNumber
			self.endChain(game)

		elif self.numberPressedFlag:
			if self.verbose:
				print '\nNumber pressed. MenuNumber', self.menuNumber
			minutes, seconds=self._clockSequence(game, game.getClockData('periodClock', 'minutes'), game.getClockData('periodClock', 'seconds'))
			self.addVariable(minutes,col=10, row=1,  places=2)
			self.addVariable(seconds,col=13, row=1,  places=2)
		return game

	def clockUpDown(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='countUp', col=14, row=1, places=1, team=255, blockNumList=[2,3,4,5,6,7,8,9], varClock=True)
		return game

	def assignError(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='errorPosition', col=14, row=1, places=1)
		return game

	def setClockTenthSec(self, game):
		if self.allMenuButtons(game):
			return game
		self.endChain(game)
		return game

	def tenthSecOnOff(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='tenthsFlag', col=14, row=1, places=1, team=255, blockNumList=[2,3,4,5,6,7,8,9])
		return game

	def autoHorn(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='gameHornEnable', col=14, row=1, places=1, team=255, blockNumList=[2,3,4,5,6,7,8,9])
		return game

	def timeOfDay(self, game):
		if self.allMenuButtons(game):
			return game
		self.endChain(game)
		return game

	def timeOutTimer(self, game):
		if self.allMenuButtons(game):
			return game
		#self.genericSetValue(game, varName='timeOutTimer', col=14, row=1, places=1)
		if self.verbose:
			print '\nsetClock start-------'
		if self.startFlag:
			#First pass only
			if self.verbose:
				print '\nFirst menu------------------------------------'
			self.startFlag=False
			self.getMenu(self.currentMenuString, self.menuNumber)
			self.addVariable(game.getClockData('timeOutTimer', 'minutesUnits'), col=11, row=1,  places=1)
			self.addVariable(game.getClockData('timeOutTimer', 'seconds'), col=13, row=1,  places=2)

		elif self.clearFlag:
			#Clear pressed
			if self.verbose:
				print '\nClear pressed. MenuNumber', self.menuNumber
			self.endChain(game)

		elif self.enterFlag:
			#Enter pressed
			if self.verbose:
				print '\nEnter pressed. MenuNumber', self.menuNumber
			if self.numberPressedFlag:
				#Save input to game
				minutesUnits, seconds=self._clockSequence(game, game.getClockData('timeOutTimer', 'minutesUnits'), game.getClockData('timeOutTimer', 'seconds'))
				if seconds>59:
					self.endChain(game)
					return game
				game.setClockData('timeOutTimer', 'minutesUnits', minutesUnits)
				game.setClockData('timeOutTimer', 'seconds', seconds)
				time=minutesUnits*60+seconds# check later
				game.clockDict['timeOutTimer'].Reset(time)
				self.endChain(game)
			else:
				self.endChain(game)
				return game

		elif self.funcString==self.currentMenuString:
			if self.verbose:
				print '\nMenu pressed. MenuNumber', self.menuNumber
			self.endChain(game)

		elif self.numberPressedFlag:
			if self.verbose:
				print '\nNumber pressed. MenuNumber', self.menuNumber
			minutesUnits, seconds=self._clockSequence(game, game.getClockData('timeOutTimer', 'minutesUnits'), game.getClockData('timeOutTimer', 'seconds'))
			self.addVariable(minutesUnits,col=11, row=1,  places=1)
			self.addVariable(seconds,col=13, row=1,  places=2)
		return game

	def setBatterNumber(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='batterNumber', col=13, row=1, places=2)
		return game

	def setPitchCounts(self, game):
		if self.allMenuButtons(game):
			return game
		if game.gameData['sportType']=='linescore':
			self.startingMenuNumber=3
			self.endingMenuNumber=4
			if self.verbose:
				print 'startingMenuNumber', self.startingMenuNumber, 'endingMenuNumber', self.endingMenuNumber, 'menuNumber', self.menuNumber
			if self.menuNumber==1:
				self.menuNumber=3

			if self.menuNumber<self.startingMenuNumber:
				self.endChain(game)
			elif self.menuNumber==3:# Go to next menu
				self.genericSetValue(game, varName='pitchCount', col=12, row=1, places=3, team=game.guest)
			elif self.menuNumber>=4:
				self.genericSetValue(game, varName='pitchCount', col=12, row=1, places=3, team=game.home)
		else:
			self.endingMenuNumber=2
			if self.menuNumber<self.startingMenuNumber:
				self.endChain(game)
			elif self.menuNumber==1:# Go to next menu
				self.genericSetValue(game, varName='pitchCount', col=12, row=1, places=3, team=game.guest)
			elif self.menuNumber>=2:
				self.genericSetValue(game, varName='pitchCount', col=12, row=1, places=3, team=game.home)
		return game

	def setGuestScore(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='score', col=13, row=1, places=2, team=game.guest)
		return game

	def setHomeScore(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='score', col=13, row=1, places=2, team=game.home)
		return game

	def playClocks(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def yardsToGoReset(self, game):
		if self.allMenuButtons(game):
			return game
		self.endingMenuNumber=10
		if self.menuNumber>self.endingMenuNumber:
			game.setGameData('yardsToGo', 0)
			self.endChain(game)
			return game
		if self.startFlag:
			self.startFlag=False
			game.setGameData('yardsToGo', 10)
		else:
			if self.funcString==self.currentMenuString:
				if self.menuNumber==10:
					game.setGameData('yardsToGo', 99)
				else:
					game.modGameData('yardsToGo', modValue=10)
			else:
				self.endChain(game)
		return game

	def setYardsToGo(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='yardsToGo', col=13, row=1, places=2)
		return game

	def setBallOn(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='ballOn', col=13, row=1, places=2)
		return game

	def setTotalRuns(self, game):
		if self.allMenuButtons(game):
			return game
		self.endingMenuNumber=2
		if self.menuNumber<self.startingMenuNumber:
			self.endChain(game)
		elif self.menuNumber==1:# Go to next menu
			self.genericSetValue(game, varName='score', col=13, row=1, places=2, team=game.guest)
		elif self.menuNumber>=2:
			self.genericSetValue(game, varName='score', col=13, row=1, places=2, team=game.home)

		return game

	def setTotalHits(self, game):
		if self.allMenuButtons(game):
			return game
		self.endingMenuNumber=2
		if self.menuNumber<self.startingMenuNumber:
			self.endChain(game)
		elif self.menuNumber==1:# Go to next menu
			self.genericSetValue(game, varName='hits', col=13, row=1, places=2, team=game.guest)
		elif self.menuNumber>=2:
			self.genericSetValue(game, varName='hits', col=13, row=1, places=2, team=game.home)

		return game

	def setTotalErrors(self, game):
		if self.allMenuButtons(game):
			return game
		self.endingMenuNumber=2
		if self.menuNumber<self.startingMenuNumber:
			self.endChain(game)
		elif self.menuNumber==1:# Go to next menu
			self.genericSetValue(game, varName='errors', col=14, row=1, places=1, team=game.guest)
		elif self.menuNumber>=2:
			self.genericSetValue(game, varName='errors', col=14, row=1, places=1, team=game.home)
		return game

	def setRuns_InningsValue(self, game, varName, col=14, row=1, places=1, team=255, blockNumList=[], varClock=False):
		if self.verbose:
			print '\nsetRuns_InningsValue start-------'
			print 'VarName', varName, 'Column', col, 'Row', row, 'Places', places, 'Team', team, 'BlockNumList', blockNumList, 'VarClock', varClock
		currentData=0
		#Act according to which button was pressed----------------------------

		if self.startFlag:
			#First pass only
			if self.verbose:
				print '\nFirst menu------------------------------------'
			self.startFlag=False

		#Quit if number is in block list
		elif self.blockNumber(game, blockNumList):
			return game

		elif self.clearFlag:
			#Clear pressed
			if self.verbose:
				print '\nClear pressed. MenuNumber', self.menuNumber
			currentData=game.getTeamData(team, 'scoreInn'+self.editInningSelection)
			self.numberPressedFlag=False
			self.numberPressedSequence=[]

		elif self.enterFlag:
			#Enter pressed
			if self.verbose:
				print '\nEnter pressed. MenuNumber', self.menuNumber
			if self.numberPressedFlag:
				if self.menuNumber==2:
					if (self._digitSequence(game, self.lastPlaces)>=1 and self._digitSequence(game, self.lastPlaces)<=10):
						if self.verbose:
							print '\nsequence equals', self._digitSequence(game, self.lastPlaces)
						self.editInningSelection=str(self._digitSequence(game, self.lastPlaces))
						currentData=game.getTeamData(team, 'scoreInn'+self.editInningSelection)
						self.numberPressedFlag=False
						self.numberPressedSequence=[]
					else:
						self.endChain(game)
						return game
				elif self.menuNumber==3:
					currentData=game.getTeamData(team, 'scoreInn'+self.editInningSelection)
					game.setTeamData(self.lastTeam, 'scoreInn'+self.editInningSelection, self._digitSequence(game, self.lastPlaces))
					self.numberPressedFlag=False
					self.numberPressedSequence=[]
				elif self.menuNumber==4:
					game.setTeamData(self.lastTeam, 'scoreInn'+self.editInningSelection, self._digitSequence(game, self.lastPlaces))
					self.numberPressedFlag=False
					self.numberPressedSequence=[]
			else:
				if self.menuNumber==2:
					if self.previousData>=1 and self.previousData<=10:
						if self.verbose:
							print '\nself.previousData equals', self.previousData
							print '0 or 255 ends'
						self.editInningSelection=str(self.previousData)
						currentData=game.getTeamData(team, 'scoreInn'+self.editInningSelection)
						self.numberPressedFlag=False
						self.numberPressedSequence=[]
					else:
						self.endChain(game)
						return game
				elif self.menuNumber==3:
					currentData=game.getTeamData(team, 'scoreInn'+self.editInningSelection)
					game.setTeamData(self.lastTeam, 'scoreInn'+self.editInningSelection, self._digitSequence(game, self.lastPlaces))
					self.numberPressedFlag=False
					self.numberPressedSequence=[]
				elif self.menuNumber==4:
					game.setTeamData(self.lastTeam, 'scoreInn'+self.editInningSelection, self._digitSequence(game, self.lastPlaces))
					self.numberPressedFlag=False
					self.numberPressedSequence=[]

		elif self.funcString==self.currentMenuString:
			#Menu button pressed twice
			if self.verbose:
				print '\nself.funcString==self.currentMenuString. MenuNumber', self.menuNumber
			if self.menuNumber>self.endingMenuNumber:
				if self.verbose:
					print 'Outside menu range!!!!!'
				self.endChain(game)
				return game

			if self.menuNumber==2:
				if self.previousData>=1 and self.previousData<=10:
					if self.verbose:
						print '\nself.previousData equals', self.previousData
					self.editInningSelection=str(self.previousData)
					currentData=game.getTeamData(team, 'scoreInn'+self.editInningSelection)
					self.numberPressedFlag=False
					self.numberPressedSequence=[]
				else:
					self.endChain(game)
					return game

			elif self.menuNumber==3:
				currentData=game.getTeamData(team, 'scoreInn'+self.editInningSelection)
				game.setTeamData(self.lastTeam, 'scoreInn'+self.editInningSelection, self._digitSequence(game, self.lastPlaces))
				self.numberPressedFlag=False
				self.numberPressedSequence=[]
			elif self.menuNumber==4:
				game.setTeamData(self.lastTeam, 'scoreInn'+self.editInningSelection, self._digitSequence(game, self.lastPlaces))
				self.numberPressedFlag=False
				self.numberPressedSequence=[]

		elif self.numberPressedFlag:
			#Numbers Pressed will display on LCD if not in the block list
			if self.verbose:
				print '\nNumber pressed. MenuNumber', self.menuNumber
			currentData=self._digitSequence(game, places)

		else:
			if self.verbose:
				print '\nNo action taken', self.menuNumber
				return game

		self.updateMenu(game, currentData, col, row,  places, team)
		self.savePrevious(varName, col, row, places, team, blockNumList, varClock, currentData)
		return game

	def setRuns_Innings(self, game):
		if self.allMenuButtons(game):
			return game
		self.endingMenuNumber=3
		if self.menuNumber<self.startingMenuNumber:
			self.endChain(game)
		elif self.menuNumber==1:# Go to next menu
			self.genericSetValue(game, varName='inning', col=13, row=1, places=2)
		elif self.menuNumber==2:
			inn=str(game.getGameData('inning'))
			self.setRuns_InningsValue(game, varName='scoreInn'+inn, col=14, row=1, places=1, team=game.guest, blockNumList=[])
		elif self.menuNumber>=3:
			inn=str(game.getGameData('inning'))
			self.setRuns_InningsValue(game, varName='scoreInn'+inn, col=14, row=1, places=1, team=game.home, blockNumList=[])
		return game

	def setInningTop_BotValue(self, game, varName, col=14, row=1, places=1, team=255, blockNumList=[], varClock=False):
		if self.verbose:
			print '\nsetInningTop_BotValue start-------'
			print 'VarName', varName, 'Column', col, 'Row', row, 'Places', places, 'Team', team, 'BlockNumList', blockNumList, 'VarClock', varClock
		currentData=self.getCurrentData(game, varName, team, varClock)

		#Act according to which button was pressed----------------------------

		if self.startFlag:
			#First pass only
			if self.verbose:
				print '\nFirst menu------------------------------------'
			self.startFlag=False

		#Quit if number is in block list
		elif self.blockNumber(game, blockNumList):
			return game

		elif self.clearFlag:
			#Clear pressed
			if self.verbose:
				print '\nClear pressed. MenuNumber', self.menuNumber
			self.numberPressedFlag=False
			self.numberPressedSequence=[]

		elif self.enterFlag:
			#Enter pressed
			if self.verbose:
				print '\nEnter pressed. MenuNumber', self.menuNumber
			if self.numberPressedFlag:
				if self.menuNumber==2:
					if (self._digitSequence(game, self.lastPlaces)>=1 and self._digitSequence(game, self.lastPlaces)<=10):
						if self.verbose:
							print '\nsequence equals', self._digitSequence(game, self.lastPlaces)
							print 'normal values make game.linescoreStart=False'
						game.gameSettings['linescoreStart']=False
						game=self.saveGameVariable(game)
						self.numberPressedFlag=False
						self.numberPressedSequence=[]
					else:
						self.endChain(game)
						return game
				elif self.menuNumber==3:
					game=self.saveGameVariable(game)
			else:
				if self.menuNumber==2:
					if self.previousData>=1 and self.previousData<=10:
						self.numberPressedFlag=False
						self.numberPressedSequence=[]
					else:
						self.endChain(game)
						return game


		elif self.funcString==self.currentMenuString:
			#Menu button pressed twice
			if self.verbose:
				print '\nself.funcString==self.currentMenuString. MenuNumber', self.menuNumber
			if self.menuNumber>self.endingMenuNumber:
				if self.verbose:
					print 'Outside menu range!!!!!'
				self.endChain(game)
				return game
			if self.menuNumber==2:
				if self.previousData>=1 and self.previousData<=10:
					#Exit menu if no input because inning value is needed for next menu
					if self.verbose:
						print '\nself.previousData equals', self.previousData
					self.numberPressedFlag=False
					self.numberPressedSequence=[]
				else:
					self.endChain(game)
					return game

		elif self.numberPressedFlag:
			#Numbers Pressed will display on LCD if not in the block list
			if self.verbose:
				print '\nNumber pressed. MenuNumber', self.menuNumber
			currentData=self._digitSequence(game, places)

		else:
			if self.verbose:
				print '\nNo action taken', self.menuNumber
				return game

		self.updateMenu(game, currentData, col, row,  places, team)
		self.savePrevious(varName, col, row, places, team, blockNumList, varClock, currentData)
		return game

	def setInningTop_Bot(self, game):
		if self.allMenuButtons(game):
			return game
		self.endingMenuNumber=2
		if self.menuNumber<self.startingMenuNumber:
			self.endChain(game)
		elif self.menuNumber==1:# Go to next menu
			self.setInningTop_BotValue(game, varName='inning', col=13, row=1, places=2)
		elif self.menuNumber>=2:
			self.setInningTop_BotValue(game, varName='inningBot', col=14, row=1, places=1, team=255, blockNumList=[2,3,4,5,6,7,8,9])
		return game

	def setGuestTimeOuts(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='timeOutsLeft', col=14, row=1, places=1, team=game.guest)
		return game

	def setHomeTimeOuts(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='timeOutsLeft', col=14, row=1, places=1, team=game.home)
		return game

	def shotClocks(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def playerMatchGame(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='playerNumber', col=13, row=1, places=2)
		return game

	def playerFoul(self, game):
		if self.allMenuButtons(game):
			return game
		self.genericSetValue(game, varName='playerFouls', col=14, row=1, places=1)
		return game

	def setGuestFunctions(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setHomeFunctions(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def guestPenalty(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def homePenalty(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	#STAT-------------------------------------------------

	def addPlayer(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def deletePlayer(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def displaySize(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def editPlayer(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def nextPlayer(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def subPlayer(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def previousPlayer(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setPlayer1Number(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setPlayer2Number(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setPlayer1Score(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setPlayer2Score(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setTotalScore(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setOvers(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setLastMan(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def setLastWicket(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def set1eInnings(self, game):
		if self.allMenuButtons(game):
			return game
		return game

	def doNothing(self, game):
		self.menuFlag=False
		game.gameSettings['menuFlag']=False
		return game

def main():
	print "ON"
	c=Config()
	sport='MPBASEBALL1'
	c.writeSport(sport)
	game = selectSportInstance(sport)
	lcd=LCD_16X2_Display_Handler(sport)
	lcd.RefreshScreen(game)
	print

if __name__ == '__main__':
	main()
