#!/usr/bin/env python

# by Craig Gunter
#
# "CG_Console Main Program Module"
#
# 	CG_Console()Input = None
#


#	Varibles available /w Defaults
"""




"""
import time
from time import sleep

from Config import Config
from clock import clock
from Game import *
from User_Interface_Handler import User_Interface_Handler
#from Legacy_Display_Handler import Legacy_Display_Handler


def tf(string):
	if string=="True":
		return True
	elif string=="False":
		return False
	return

def flashHit(hitIndicatorFlashCount, Game, AddrMap, LCD):
	if Game.hitFlashTimer.currentTime==0.000:
		if hitIndicatorFlashCount:
			Game.hitFlashTimer.Reset(Game.hitFlashDuration)
			Game.hitFlashTimer.Start()
			AddrMap = AddrMap._flashHitIndicator(Game, AddrMap)
			Game, LCD = LCD.RefreshDefaultScreen(Game, LCD)
			Game.hitIndicator = not Game.hitIndicator
			hitIndicatorFlashCount-=1
		else:#last time
			Game.hitIndicator=False
			Game.hitIndicatorFlashOn=False
			hitIndicatorFlashCount=Game.hitIndicatorFlashCount-1
			AddrMap = AddrMap._flashHitIndicator(Game, AddrMap)
			Game, LCD = LCD.RefreshDefaultScreen(Game, LCD)
	return hitIndicatorFlashCount, Game, AddrMap

def flashError(errorIndicatorFlashCount, Game, AddrMap, LCD):
	if Game.errorFlashTimer.currentTime==0.000:
		if errorIndicatorFlashCount:
			Game.errorFlashTimer.Reset(Game.errorFlashDuration)
			Game.errorFlashTimer.Start()
			Game, LCD = LCD.RefreshDefaultScreen(Game, LCD)
			AddrMap = AddrMap._flashErrorIndicator(Game, AddrMap)
			Game.errorIndicator = not Game.errorIndicator
			errorIndicatorFlashCount-=1
		else:#last time
			Game.errorIndicator=False
			Game.errorIndicatorFlashOn=False
			errorIndicatorFlashCount=Game.errorIndicatorFlashCount-1
			AddrMap = AddrMap._flashErrorIndicator(Game, AddrMap)
			Game, LCD = LCD.RefreshDefaultScreen(Game, LCD)
	return errorIndicatorFlashCount, Game, AddrMap

''' Instance definitions'''
config=Config()
configDict=config.getDict()
game=Game_Variables(configDict)
game=game.ResetGame(game)
ui=User_Interface_Handler(config, game)
legacy=Legacy_Display_Handler(config, game)


''' Class pointers'''
Keypad=ui.keypad
Game=ui.keypad.game
GameClock=ui.keypad.game.gameClock
Numpad=ui.keypad.game.numpad
KeyMap=ui.keypad.keyMap
LCD=legacy.lcd
Legacy=legacy
LampTest=legacy.lampTest
BlankTest=legacy.blankTest
AddrMap=legacy.addrMap
Words=legacy.words
Adhoc=legacy.adhoc
MP=legacy.addrMap.mp

conn=0

print "ON"

Game, AddrMap = AddrMap.Initialize_Legacy_Display(Game, AddrMap)

lastHours = GameClock.hours
lastMinutes = GameClock.minutes
lastSeconds = GameClock.seconds
lastTenths_hundredths = GameClock.tenths_hundredths
lastLcdScreen = ''

Game, LCD = LCD.Splash(Game, LCD)

dimmingCount=0
whileTime=whileCount=tick=tock=timeMeasureFlag=0
if Game.sportName=='baseball':
	hitIndicatorFlashCount=Game.hitIndicatorFlashCount-1
	errorIndicatorFlashCount=Game.errorIndicatorFlashCount-1
Game, LCD = LCD.RefreshDefaultScreen(Game, LCD)
#Game.scoreTo19Flag=True

while 1:


	if CONSOLE:
		timeString=GameClock.Update()	# this must be in the while loop to update the clock at high speed for display
		Game.gameHornFlashTimer.Update()
		if Game.sportName=='baseball':
			Game.hitFlashTimer.Update()
			Game.errorFlashTimer.Update()
		Game.newGameMenuTimer.Update()

		if (GameClock.hours != lastHours) and Game.hoursFlag and Game.sportName=='baseball':
			lastHours = GameClock.hours
			AddrMap = AddrMap._clock(Game, AddrMap)
			hours="%d"%lastHours
			LCD.lcd.setCursor(4,0)# fix location
			LCD.lcd.message(hours)

		if (GameClock.minutes != lastMinutes):
			lastMinutes = GameClock.minutes
			#AddrMap.words[5] = MP.Encode(1,2,1,0,0,'BCD',lastMinutes,1,0,'')
			AddrMap = AddrMap._clock(Game, AddrMap)
			minutes="%02d"%lastMinutes
			if Game.sportName=='baseball':
				LCD.lcd.setCursor(4,0)
			elif Game.sportName=='football' or Game.sportName=='basketball':
				LCD.lcd.setCursor(5,0)
			LCD.lcd.message(minutes)

		if (GameClock.seconds != lastSeconds):
			lastSeconds = GameClock.seconds
			#AddrMap.words[7] = MP.Encode(1,2,3,0,0,'digit',GameClock.secondsUnits,0,0,'')
			#AddrMap.words[8] = MP.Encode(1,2,4,1,0,'digit',GameClock.secondsTens,0,0,'')
			AddrMap = AddrMap._clock(Game, AddrMap)
			seconds="%02d"%lastSeconds
			if Game.sportName=='baseball':
				LCD.lcd.setCursor(7,0)
			elif Game.sportName=='football' or Game.sportName=='basketball':
				LCD.lcd.setCursor(8,0)
			LCD.lcd.message(seconds)

		if (GameClock.tenths_hundredths != lastTenths_hundredths):
			lastTenths_hundredths = GameClock.tenths_hundredths
			#AddrMap.words[6] = MP.Encode(1,2,2,0,0,'BCD',lastTenths_hundredths,0,0,'')

		if Game.keyPressFlag:
			tock=time.time()
			Tock=Keypad.tock
			print 'while,key - lastKeyPressedString: ', Game.lastKeyPressedString
			Game, LCD = LCD.Map(Game, LCD)
			Game.keyPressFlag=False# Must be after data changes. It is used in earlier functions
			Game, AddrMap = AddrMap.Map(KeyMap.funcString, Game, AddrMap)
			Game.refreshDefaultScreenFlag=True
			#timeMeasureFlag=True
			#Keypad.eventFlag=False
			Game.keyPressFlag=False
			#Keypad.callbackFlag=False
			tick=time.time()
			print tick-tock
			print tick-Tock

		if conn:
			if Game.lampTestFlag:					# normal check for word change
				Words.checkWords(LampTest, Adhoc)
			elif Game.blankTestFlag:
				Words.checkWords(BlankTest, Adhoc)
			else:										# lamp test instance
				Words.checkWords(AddrMap, Adhoc)

		if timeMeasureFlag:
			timeMeasureFlag=False
			tick=time.time()
			print tick-tock

		if Game.gameHornFlashTimer.currentTime==0.000:
			Game.gameHorn=False
			Game.gameHornFlashTimer.Reset(Game.gameHornFlashDuration)
			Game.visualHornIndicator1=False
			AddrMap = AddrMap.Horn(Game, AddrMap)

		if Game.sportName=='baseball':
			if Game.hitIndicatorFlashOn:
				hitIndicatorFlashCount, Game, AddrMap = flashHit(hitIndicatorFlashCount, Game, AddrMap, LCD)
			if Game.errorIndicatorFlashOn:
				errorIndicatorFlashCount, Game, AddrMap = flashError(errorIndicatorFlashCount, Game, AddrMap, LCD)

		if Game.resetGameFlag:
			Game.resetGameFlag=False
			Game.ResetGame(Game)
			Game=KeyMap.changeKeypad(Game)
			Game.refreshDefaultScreenFlag=True

		if Game.refreshDisplayFlag:# re-populates default game data to the word dictionary
			Game.refreshDisplayFlag=False
			Game, AddrMap = AddrMap.changeAddrMap(Game, AddrMap)
			Game, AddrMap = AddrMap.Initialize_Legacy_Display(Game, AddrMap)

		if Game.lampTestFlag or Game.blankTestFlag or Game.menuFlag==False:
			Game.newGameMenuTimer.Stop()
			Game.newGameMenuTimer.Reset(newGameMenuTimerDuration)
		elif Game.newGameMenuTimer.currentTime==0.000:
			print "timeout"
			Game.newGameMenuTimer.Stop()
			Game.newGameMenuTimer.Reset(newGameMenuTimerDuration)
			LCD._end(Game, LCD)
			Game.lastKeyPressedString='full'
			Game.refreshDefaultScreenFlag=True


#G1		B1=1,2,3,4		B2=5,6,7,8 		B3=9,10,11,12, 		B4=13,14,15,16
#G2		B1=17,18,19,20 	B2=21,22,23,24 	B3=25,26,27,28 		B4=29,30,31,32


		if Game.dimmingFlag:# each entery cycles through 6 brightness levels and sends them to each bank
			Game.dimmingFlag=False
			if keypadType=='MM':
				Game.brightness=dimmingCount+18
			dimmingCount+=9
			print Game.brightness
			for i in range(2):
				for j in range(4):
					Words.words[(i*4+j)*4+1] = MP.Encode(i+1,j+1,1,0,0,'BCD',0,3,0,'')	# '3' in blankIfZero sends the 'BC' quantum tunneling value for Dimming
					Words.words[(i*4+j)*4+2] = MP.Encode(i+1,j+1,2,0,0,'BCD',Game.brightness,0,0,'')
					Adhoc.IO_adhoc(Words.words[(i*4+j)*4+1])
					Adhoc.IO_adhoc(Words.words[(i*4+j)*4+2])

			if dimmingCount>9*5: #cycles back to lowest brightness
				dimmingCount=0

		if Game.refreshDefaultScreenFlag:
			Game, LCD = LCD.RefreshDefaultScreen(Game, LCD)


