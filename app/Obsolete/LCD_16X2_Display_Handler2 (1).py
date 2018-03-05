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


#	Varibles available /w Defaults
"""




"""

from time import sleep
from clock import clock

from Config import *
from Game import *
#from LCD_16X2_Display import Adafruit_CharLCDPlate

class LCD_16X2_Display_Handler(object):

	def __init__(self):
		config=Config()
		self.configDict = config.getDict()
		self.sport=self.configDict['sport']
		#self.lcd = Adafruit_CharLCDPlate()
		#self.lcd.begin(0,0)

		self.clockUpDownCount=0
		self.setClockCount=0
		self.NewGameCount=0
		self.SplashCount=0
		self.setClockTenthSecCount=0
		self.tenthSecOnOffCount=0
		self.autoHornCount=0
		self.timeOfDayCount=0
		self.timeOutTimerCount=0
		self.setPitchCountsCount=0
		self.setBatterNumberCount=0
		self.setGuestScoreCount=0
		self.setHomeScoreCount=0
		self.assignErrorCount=0

		self.lcdDefaultScreen='    Engage&&'
		self.precisionMenuFlag=False

		if self.sport=='MMBASEBALL3' or self.sport=='MPBASEBALL1':
			self.Baseball_LCD_FuncDict = {'guestScorePlusTen':self.doNothing, 'guestScorePlusOne':self.doNothing, 'NewGame':self.NewGame, \
			'homeScorePlusTen':self.doNothing, 'homeScorePlusOne':self.doNothing, 'flashHitIndicator':self.doNothing, \
			'minutesMinusOne':self.doNothing, 'gameClockReset':self.doNothing, 'gameClockOnOff':self.doNothing, 'full':self.doNothing, \
			'secondsMinusOne':self.doNothing, 'flashErrorIndicator':self.doNothing, 'ballsPlusOne':self.doNothing, \
			'strikesPlusOne':self.doNothing, 'outsPlusOne':self.doNothing, 'inningsPlusOne':self.doNothing, 'blank':self.doNothing, \
			'setClock':self.setClock, 'setClockTenthSec':self.setClockTenthSec, 'tenthSecOnOff':self.tenthSecOnOff, 'clockUpDown':self.clockUpDown, \
			'Number_7_ABC':self.Number_7_ABC, 'Number_8_DEF':self.Number_8_DEF, 'Number_9_GHI':self.Number_9_GHI, 'teamAtBat':self.teamAtBat, \
			'autoHorn':self.autoHorn, 'timeOfDay':self.timeOfDay, 'timeOutTimer':self.timeOutTimer, 'Number_4_JKL':self.Number_4_JKL, \
			'Number_5_MNO':self.Number_5_MNO, 'Number_6_PQR':self.Number_6_PQR, 'setPitchCounts':self.setPitchCounts, 'Number_1_STU':self.Number_1_STU, \
			'Number_2_VWX':self.Number_2_VWX, 'Number_3_YZ':self.Number_3_YZ, 'setBatterNumber':self.setBatterNumber, 'setGuestScore':self.setGuestScore, \
			'setHomeScore':self.setHomeScore, 'guestPitchesPlusOne':self.doNothing, 'homePitchesPlusOne':self.doNothing, 'clear_FlashHit':self.clear_FlashHit, \
			'Number_0_&-.!':self.Number_0, 'enter_FlashError':self.enter_FlashError, 'assignError':self.assignError, 'horn':self.doNothing, 'Splash':self.Splash, \
			}

			self.Baseball_LCD_Text = self.readLCDButtonMenus()
			print self.Baseball_LCD_Text

	def readLCDButtonMenus(self):
		LCDtext='Spreadsheets/LCDtext.csv'
		csvReader=csv.DictReader(open(LCDtext, 'rb'), delimiter=',', quotechar="'")
		#keys=dict.keys(self.Baseball_LCD_FuncDict)
		dictFlag=0
		key=[]
		value=[]
		dictionary = {}
		for row in csvReader:
			try:
				key=row.keys()
				value=row.values()
				for i in range(len(row)-1):
					if not value[i+1]=='':
						dictFlag=1
				if dictFlag:
					dictFlag=0
					for i in range(len(value)):
						if not value[i]=='':
							tmp=(key[i])[5]
							if tmp!='N':
								dictionary[value[0]+tmp]=value[i]
			except ValueError:
				pass

		'''
		test_array=[]

		values=dict.values(self.Baseball_LCD_Text)
		row=(keys[0],values[0])
		print row
		test_file=open('test2.csv','wb')
		csvwriter = csv.writer(test_file, delimiter=',')
		csvwriter.writerow(row)

		test_file.close()
		'''
		return dictionary

	def Map(self, game):

		game = self.Baseball_LCD_FuncDict[game.lastKeyPressedString](game)# call LCD function

		return game

	def Splash(self, game):
		game.menuFlag=False
		#lcd.lcd.clear()
		startLCDRow=0
		last=game.lastKeyPressedString
		print 'Version:', game.Version, 'sport:', game.sport, 'option jumpers:', game.optionJumpers, 'restoreFlag:', game.restoreFlag
		game.lastKeyPressedString='Splash'
		game = lcd._start(game, startLCDRow, 0, 0, 0, '', 0, 0, 0, '', 0)
		game.lastKeyPressedString=last
		self.lcd.setCursor(13,0)
		self.lcd.message(game.Version+'&'+game.sport[2:10]+'_'+game.sport[10]+'  '+game.optionJumpers)
		sleep(game.splashTime)
		if game.restoreFlag:
			lcd.SplashCount=2
			menuString=game.currentMenuString
			menuNumber=lcd.SplashCount=2
			LCDRow=0
			lcd._displayCSVMessage(menuString, menuNumber, lcd, LCDRow)
			lcd.addVariable(1,14,1, '1')
			menuDuration=3
			Menu=clock(False, menuDuration)
			Menu.Start()
			while loop:
				Menu.Update()
				if game.numpad.enterFlag:
					game=lcd._1digitTFgame(game, 'restoreFlag')
					break
				else:
					lcd.addVariable(game.numpad.lastNumberPressed,14,1, '1')

				if Menu.currentTime==0.000:
					print 'restore timeout'
					Menu.Stop()
					Menu.Reset(menuDuration)
					break
					#Auto restore here since restore flag is already set

			game = lcd._end(game)
		return game

	def RefreshDefaultScreen(self, game):
		if (not game.lampTestFlag or not game.lampTestFlag):
			updateType = game.lastKeyPressedString

			#Formating section for data

			if game.gameClock.countUp:
				clockType='U'
			else:
				clockType='D'
			if game.precisionFlag:
				clockType='P'

			if game.hitIndicator:
				hit='H'
			else:
				hit=' '
			if game.errorIndicator:
				error='E'
			else:
				error=' '

			row1 = '%02d %s%02d:%02d %2d  %02d' % (game.guestScore, clockType, game.gameClock.minutes, game.gameClock.seconds, game.innings, game.homeScore)
			row2 = '%s%3d %d-%d-%d %3d %s' % (hit, game.guestPitchCount, game.balls, game.strikes, game.outs, game.homePitchCount, error)
			lcd.lcdDefaultScreen = row1+'&'+row2

			#This section is for updating the default screen after a non-menu event

			if game.menuFlag==False or updateType=='full':
				lcd.lcd.setCursor(0,0)
				lcd.lcd.message(lcd.lcdDefaultScreen)
			elif updateType=='flashHitIndicator':
				lcd.lcd.setCursor(0,1)
				lcd.lcd.message(hit)
			elif updateType=='flashErrorIndicator':
				lcd.lcd.setCursor(15,1)
				lcd.lcd.message(error)
			elif updateType=='guestScorePlusTen' or updateType=='guestScorePlusOne':
				score='%02d'%game.guestScore
				lcd.lcd.setCursor(1,0)
				lcd.lcd.message(score)
			elif updateType=='homeScorePlusTen' or updateType=='homeScorePlusOne':
				score='%02d'%game.homeScore
				lcd.lcd.setCursor(15,0)
				lcd.lcd.message(score)
			elif updateType=='inningsPlusOne':
				innings='%2d'%game.innings
				lcd.lcd.setCursor(10,0)
				lcd.lcd.message(innings)
			elif updateType=='homePitchesPlusOne':
				count='%3d'%game.homePitchCount
				lcd.lcd.setCursor(13,1)
				lcd.lcd.message(count)
			elif updateType=='guestPitchesPlusOne':
				count='%3d'%game.guestPitchCount
				lcd.lcd.setCursor(1,1)
				lcd.lcd.message(count)

			game.refreshDefaultScreenFlag=False
			print updateType, lcd.lcdDefaultScreen
		return game

	def addVariable(self, data, col, row,  places):
		self.lcd.setCursor(col, row)
		if places=='1':
			variable='%d' % (data)
		elif places=='2':
			variable='%02d' % (data)
		elif places=='3':
			variable='%03d' % (data)
		#print variable
		self.lcd.message(variable)
		return

	def _start(self, game, LCDRow, var1, var1col, var1row, var1places, var2, var2col, var2row, var2places, menuCount):
		if (game.lampTestFlag or game.blankTestFlag) and game.currentMenuString!='NewGame':#Skip start if in test mode
			game = lcd._end(game)
			return game
		if not game.menuFlag:
			game.menuFlag=True
			game.currentMenuString=game.lastKeyPressedString
			game.enterFlag = False
			game.lastNumberPressed = 255
			vars(lcd)[game.currentMenuString+'Count']=1 #Count= the MENU_ number
			print 'start of ', game.currentMenuString+str(vars(lcd)[game.currentMenuString+'Count'])
			lcd.lcd.setCursor(0, LCDRow)# set first or second row
			display=self.Baseball_LCD_Text[game.currentMenuString+str(vars(lcd)[game.currentMenuString+'Count'])]#add count string to name and find value of that variable, then add that number to the end of the name and search for it
			lcd.lcd.message(display)
			print display
			if not var1places=='':
				lcd.addVariable(var1,var1col,var1row, var1places)
			if not var2places=='':
				lcd.addVariable(var2,var2col,var2row, var2places)
			if menuCount:
				vars(lcd)[game.currentMenuString+'Count']=menuCount
		return game

	def _end(self, game):
		game.numpad.enterFlag=False
		game.numpad.cancelFlag=False
		game.menuFlag=False
		game.refreshDefaultScreenFlag=True
		lcd.precisionMenuFlag=False
		game.lampTestFlag=False
		game.blankTestFlag=False
		game.gameClock.running=False

		game.lastNumberPressed = 255
		game.numberPressedSequence=''
		game.newGameCount=0
		lcd.NewGameCount=0
		lcd.clockUpDownCount=0
		lcd.setClockCount=0

		game.currentMenuString='full'
		print'_end menu!!!!!'
		return game

	def _displayCSVMessage(self, menuString, menuNumber, lcd, LCDRow):#display message from row funcString and column MENU_X where X = the value of funcString+'count'
		if menuNumber:
			lcd.lcd.setCursor(0, LCDRow)# set first or second row
			display=self.Baseball_LCD_Text[menuString+str(menuNumber)]#add count string to name and find value of that variable, then add that number to the end of the name and search for it
			lcd.lcd.message(display)
			print display
		return

	def _1digitTFgameClock(self, game, varName):
		if game.numpad.lastNumberPressed==0:
			vars(game.gameClock)[varName]=False
		elif game.numpad.lastNumberPressed==1:
			vars(game.gameClock)[varName]=True
		return game

	def _1digitTFgame(self, game, varName):
		if game.numpad.lastNumberPressed==0:
			vars(game)[varName]=False
		elif game.numpad.lastNumberPressed==1:
			vars(game)[varName]=True
		return game

	def _2digitSequenceGame(self, game, varName):
		if len(game.numpad.numberPressedSequence)==1:
			vars(game)[varName]=int(game.numpad.numberPressedSequence[-1])
		elif len(game.numpad.numberPressedSequence)>=2:
			vars(game)[varName]=int(game.numpad.numberPressedSequence[-1]) + int(game.numpad.numberPressedSequence[-2])*10
		return game

	def _3digitSequenceGame(self, game, varName):
		if len(game.numpad.numberPressedSequence)==1:
			vars(game)[varName]=int(game.numpad.numberPressedSequence[-1])
		elif len(game.numpad.numberPressedSequence)==2:
			vars(game)[varName]=int(game.numpad.numberPressedSequence[-1]) + int(game.numpad.numberPressedSequence[-2])*10
		elif len(game.numpad.numberPressedSequence)>=3:
			vars(game)[varName]=int(game.numpad.numberPressedSequence[-1]) + int(game.numpad.numberPressedSequence[-2])*10 + int(game.numpad.numberPressedSequence[-3])*100
		return game

	def _clockSequenceGameClock(self, game, varName1, varName2):
		if len(game.numpad.numberPressedSequence)==1:
			vars(game.gameClock)[varName1]=0
			vars(game.gameClock)[varName2]=int(game.numpad.numberPressedSequence[-1])
		elif len(game.numpad.numberPressedSequence)==2:
			vars(game.gameClock)[varName1]=0
			vars(game.gameClock)[varName2]=int(game.numpad.numberPressedSequence[-1])+int(game.numpad.numberPressedSequence[-2])*10
		elif len(game.numpad.numberPressedSequence)==3:
			vars(game.gameClock)[varName1]=int(game.numpad.numberPressedSequence[-3])
			vars(game.gameClock)[varName2]=int(game.numpad.numberPressedSequence[-1])+int(game.numpad.numberPressedSequence[-2])*10
		elif len(game.numpad.numberPressedSequence)>=4:
			vars(game.gameClock)[varName1]=int(game.numpad.numberPressedSequence[-3])+int(game.numpad.numberPressedSequence[-4])*10
			vars(game.gameClock)[varName2]=int(game.numpad.numberPressedSequence[-1])+int(game.numpad.numberPressedSequence[-2])*10
		return game

	def _clockSequence(self, game, var1, var2):
		if len(game.numpad.numberPressedSequence)==1:
			var1=0
			var2=int(game.numpad.numberPressedSequence[-1])
		elif len(game.numpad.numberPressedSequence)==2:
			var1=0
			var2=int(game.numpad.numberPressedSequence[-1])+int(game.numpad.numberPressedSequence[-2])*10
		elif len(game.numpad.numberPressedSequence)==3:
			var1=int(game.numpad.numberPressedSequence[-3])
			var2=int(game.numpad.numberPressedSequence[-1])+int(game.numpad.numberPressedSequence[-2])*10
		elif len(game.numpad.numberPressedSequence)>=4:
			var1=int(game.numpad.numberPressedSequence[-3])+int(game.numpad.numberPressedSequence[-4])*10
			var2=int(game.numpad.numberPressedSequence[-1])+int(game.numpad.numberPressedSequence[-2])*10
		return var1, var2

	def NewGame(self, game):
		startLCDRow=0
		print 'last key:', game.lastKeyPressedString, 'menuFlag:', game.menuFlag, 'current menu:', game.currentMenuString, 'precision menu:', lcd.precisionMenuFlag
		if game.lastKeyPressedString=='NewGame' and game.menuFlag:# Close if pressed again while in menu
			game = lcd._end(game)
			return game
		game = lcd._start(game, startLCDRow, 0, 14, 1, '1', 0, 0, 0, '', 0)
		if game.numpad.enterFlag:#Casts _end when enter has been pressed
			if lcd.precisionMenuFlag:
				game=lcd._1digitTFgame(game, 'precisionFlag')
				print "precisionFlag: ", game.precisionFlag
			else:
				game=lcd._1digitTFgame(game, 'resetGameFlag')
				print "resetGameFlag: ", game.resetGameFlag
				if game.resetGameFlag:
					game=lcd.Splash(game)
		else:
			if game.numpad.lastNumberPressed!=255 and game.numpad.lastNumberPressed!=1 and game.numpad.lastNumberPressed!=0:
				menuString=game.currentMenuString
				menuNumber=game.numpad.lastNumberPressed
				LCDRow=0
				lcd._displayCSVMessage(menuString, menuNumber, lcd, LCDRow)

		return game

	def setClock(self, game):
		startLCDRow=1
		if game.lastKeyPressedString=='setClock' and game.menuFlag:# Close if pressed again while in menu
			game = lcd._end(game)
			return game
		game = lcd._start(game, startLCDRow, game.gameClock.minutes, 10, 1, '2', game.gameClock.seconds, 13, 1, '2', 0)
		if game.numpad.enterFlag:#Casts _end when enter has been pressed
			game=lcd._clockSequenceGameClock(game, 'minutes', 'seconds')
			time=game.gameClock.minutes*60+game.gameClock.seconds# check later
			game.gameClock.Reset(time)
		else:
			if game.numpad.lastNumberPressed!=255:
				minutes, seconds=lcd._clockSequence(game, 0, 0)
				lcd.addVariable(minutes,10,1, '2')
				lcd.addVariable(seconds,13,1, '2')

		return game

	def clockUpDown(self, game):
		startLCDRow=0
		if game.lastKeyPressedString=='clockUpDown' and game.menuFlag:# Close if pressed again while in menu
			game = lcd._end(game)
			return game
		game = lcd._start(game, startLCDRow, game.gameClock.countUp, 14, 1, '1', 0, 0, 0, '', 0)
		if game.numpad.enterFlag:#Casts _end when enter has been pressed
			game=lcd._1digitTFgameClock(game, 'countUp')

		return game

	def assignError(self, game):
		return game

	def setClockTenthSec(self, game):
		return game

	def tenthSecOnOff(self, game):
		return game

	def teamAtBat(self, game):
		return game

	def autoHorn(self, game):
		return game

	def timeOfDay(self, game):
		return game

	def Number_7_ABC(self, game):
		if game.menuFlag:
			game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_8_DEF(self, game):
		if game.menuFlag:
			if game.currentMenuString=='NewGame':
				lcd.precisionMenuFlag=True
				game = lcd.NewGame(game)# call LCD function
				lcd.addVariable(game.precisionFlag,14,1, '1')
			else:
				game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_9_GHI(self, game):
		if game.menuFlag:
			game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_4_JKL(self, game):
		if game.menuFlag:
			if game.currentMenuString=='NewGame' and not game.lampTestFlag:
				game.precisionMenuFlag=False
				game.blankTestFlag=True
				menuString='NewGame'
				menuNumber=4
				LCDRow=0
				lcd._displayCSVMessage(menuString, menuNumber, lcd, LCDRow)
			else:
				game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_5_MNO(self, game):
		if game.menuFlag:
			if game.currentMenuString=='NewGame' and not game.blankTestFlag:
				game.precisionMenuFlag=False
				game.lampTestFlag=True
				menuString='NewGame'
				menuNumber=5
				LCDRow=0
				lcd._displayCSVMessage(menuString, menuNumber, lcd, LCDRow)
			else:
				game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_6_PQR(self, game):
		if game.menuFlag:
			game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_1_STU(self, game):
		if game.menuFlag:
			if game.currentMenuString=='clockUpDown' or (game.currentMenuString=='NewGame' and (lcd.NewGameCount==1 or lcd.NewGameCount==8)):
				lcd.addVariable(game.numpad.lastNumberPressed,14,1, '1')
			else:
				game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_2_VWX(self, game):
		if game.menuFlag:
			game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_3_YZ(self, game):
		if game.menuFlag:
			game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def Number_0(self, game):
		if game.menuFlag:
			if game.currentMenuString=='clockUpDown' or (game.currentMenuString=='NewGame' and (lcd.NewGameCount==1 or lcd.NewGameCount==8)):
				lcd.addVariable(game.numpad.lastNumberPressed,14,1, '1')
			else:
				game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
		return game

	def clear_FlashHit(self, game):
		if game.menuFlag:
			game = lcd._end(game)
			game.hitIndicatorFlashOn=False
		return game

	def enter_FlashError(self, game):
		if game.menuFlag:
			game = self.Baseball_LCD_FuncDict[game.currentMenuString](game)# call LCD function
			game = lcd._end(game)
			game.errorIndicatorFlashOn=False
		return game

	def timeOutTimer(self, game):
		return game

	def setBatterNumber(self, game):
		return game

	def setPitchCounts(self, game):
		startLCDRow=1
		if game.lastKeyPressedString=='setPitchCounts' and game.menuFlag and lcd.setPitchCountsCount==1:# Go to next menu
			lcd.setPitchCountsCount=2
			menuString=game.currentMenuString
			menuNumber=lcd.setPitchCountsCount
			LCDRow=1
			lcd._displayCSVMessage(menuString, menuNumber, lcd, LCDRow)
			lcd.addVariable(game.homePitchCount,12,1, '3')
		elif game.lastKeyPressedString=='setPitchCounts' and game.menuFlag and lcd.setPitchCountsCount==2:# Close if pressed again while in menu
			game = lcd._end(game)
			return game
		game = lcd._start(game, startLCDRow, game.guestPitchCount, 12, 1, '3', 0, 0, 0, '', 0)

		if game.numpad.enterFlag and lcd.setPitchCountsCount==1:#Casts _end when enter has been pressed
			game=lcd._3digitSequenceGame(game, 'guestPitchCount')

		elif game.numpad.enterFlag and lcd.setPitchCountsCount==2:#Casts _end when enter has been pressed
			game=lcd._3digitSequenceGame(game, 'homePitchCount')

		elif lcd.setPitchCountsCount==1:
			if game.numpad.lastNumberPressed!=255:
				game=lcd._3digitSequenceGame(game, 'guestPitchCount')
				lcd.addVariable(game.guestPitchCount,12,1, '3')

		elif lcd.setPitchCountsCount==2:
			if game.numpad.lastNumberPressed!=255:
				game=lcd._3digitSequenceGame(game, 'homePitchCount')
				lcd.addVariable(game.homePitchCount,12,1, '3')
		return game

	def setGuestScore(self, game):
		startLCDRow=1
		if game.lastKeyPressedString=='setGuestScore' and game.menuFlag:# Close if pressed again while in menu
			game= lcd._end(game)
			return game
		game= lcd._start(game, startLCDRow, game.guestScore, 13, 1, '2', 0, 0, 0, '', 0)

		if game.numpad.enterFlag:#Casts _end when enter has been pressed
			game=lcd._2digitSequenceGame(game, 'guestScore')
		else:
			if game.numpad.lastNumberPressed!=255:
				game=lcd._2digitSequenceGame(game, 'guestScore')
				lcd.addVariable(game.guestScore,13,1, '2')
		return game

	def setHomeScore(self, game):
		startLCDRow=1
		if game.lastKeyPressedString=='setHomeScore' and game.menuFlag:# Close if pressed again while in menu
			game = lcd._end(game)
			return game
		game= lcd._start(gamestartLCDRow, game.homeScore, 13, 1, '2', 0, 0, 0, '', 0)

		if game.numpad.enterFlag:#Casts _end when enter has been pressed
			game=lcd._2digitSequenceGame(game, 'homeScore')
		else:
			if game.numpad.lastNumberPressed!=255:
				game=lcd._2digitSequenceGame(game, 'homeScore')
				lcd.addVariable(game.homeScore,13,1, '2')
		return game

	def doNothing(self, game):
		return game

def main():
	print "ON"
	c=Config()
	sport='MPBASEBALL1'
	c.writeSport(sport)
	game = selectSportInstance(sport, 'baseball')
	lcd=LCD_16X2_Display_Handler()
	#game.restoreFlag=True
	game=lcd.Splash(game)
	game.lastKeyPressedString='NewGame'
	lcd.RefreshDefaultScreen(game)
	end=4
	print 'before'
	while end:

		sleep(0)
		print 'while, end=', end
		end-=1
	print 'while, end=', end
if __name__ == '__main__':
	main()
