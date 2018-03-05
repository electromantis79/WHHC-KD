#!/usr/bin/env python

# by Craig Gunter
#
# "Legacy_Keypad_Interface module"
#
# Legacy_Keypad_Interface()Input = The World...
#
# 		Initalize() = Setup and trigger a thread on any key presses
#
#			col8-col1()Input = Called when rising edge is detected.
#			col8-col1()Output = Calls Keypad_Mapping.Map('XX') where 'XX' is string of capital row letter and column number
#
#			main() = Run and wait for any key presses

# NOTES:
#		Works with MM or MP keypads.
#		Must use a MP keypad with all of the diodes shorted for this to work.

#	Varibles available /w Defaults
"""

		self.bouncetime = 100ms
#		self.settle=0.01s
		self.lastKeyPressed=''
		self.eventFlag=False

"""

#import RPi.GPIO as GPIO
from time import sleep
from Config import *
from Scoreboard import Game
from Keypad_Mapping import Keypad_Mapping

class Legacy_Keypad_Interface(object):

	def __init__(self, game, keyMap):

		self.bouncetime = config['BOUNCETIME'] # Debounce time in milliseconds.
		self.game = game #THIS IS THE REAL INSTANCE OF GAME VARIABLES!!!!!!!!!!
		self.keyMap = keyMap

		self.settle=0.01
		self.lastKeyPressed=''
		self.eventFlag=False # used to stop multi-calls
		self.callbackFlag=False
		self.rows=[17, 27, 22, 10, 9]
		self.cols=[18, 23, 24, 25, 8, 7, 11, 4]

		'''Prepare GPIO'''
		GPIO.setmode(GPIO.BCM) # Watch for rev changes to change these numbers
		GPIO.setwarnings(False) # Stops warnings printed to termial
		GPIO.setup(17, GPIO.OUT, initial=1) # Row B
		GPIO.setup(27, GPIO.OUT, initial=1) # Row C
		GPIO.setup(22, GPIO.OUT, initial=1) # Row D
		GPIO.setup(10, GPIO.OUT, initial=1) # Row E
		GPIO.setup(9, GPIO.OUT, initial=1) # Row F
		GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 8
		GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 7
		GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 6
		GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 5
		GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 4
		GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 3
		GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 2
		GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Column 1

#		activate threaded key press event interrupts
		GPIO.add_event_detect(18, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)
		GPIO.add_event_detect(23, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)
		GPIO.add_event_detect(24, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)
		GPIO.add_event_detect(25, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)
		GPIO.add_event_detect(8, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)
		GPIO.add_event_detect(7, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)
		GPIO.add_event_detect(11, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)
		GPIO.add_event_detect(4, GPIO.RISING, callback=self.Callback, bouncetime=self.bouncetime)

	def _rowCheck(self, channel):
		GPIO.output(27, 0) # Row C
		GPIO.output(22, 0) # Row D
		GPIO.output(10, 0) # Row E
		GPIO.output(9, 0) # Row F
		snap1=GPIO.input(channel)
		GPIO.output(17, 0) # Row B
		GPIO.output(27, 1) # Row C
		snap2=GPIO.input(channel)
		GPIO.output(27, 0) # Row C
		GPIO.output(22, 1) # Row D
		snap3=GPIO.input(channel)
		GPIO.output(22, 0) # Row D
		GPIO.output(10, 1) # Row E
		snap4=GPIO.input(channel)
		GPIO.output(10, 0) # Row E
		GPIO.output(9, 1) # Row F
		snap5=GPIO.input(channel)
		snap=snap1*1+snap2*2+snap3*3+snap4*4+snap5*5
#		print snap1,snap2,snap3,snap4,snap5,'snap:',snap
		return snap

	def _rowReset(self):
		GPIO.output(17, 1) # Row B
		GPIO.output(27, 1) # Row C
		GPIO.output(22, 1) # Row D
		GPIO.output(10, 1) # Row E
		GPIO.output(9, 1) # Row F
		sleep(self.settle)
		return

	def Callback(self, channel):
		Rows=['B','C','D','E','F']
		Cols=['8','7','6','5','4','3','2','1']
		if not self.eventFlag:
			self.eventFlag=True
			self.tock=time.time()
			for i in range(len(self.cols)):
				if channel==self.cols[i]:
					snap = self._rowCheck(channel)
#					print Rows[snap-1], Cols[i]
					self.lastKeyPressed = Rows[snap-1]+Cols[i]
					if snap:
						self.game = self.keyMap.Map(self.lastKeyPressed, self.game)
					self._rowReset()
					self.eventFlag=False
					return
		else:
			print 'callback'

def main():	# Feel free to un-comment any prints to examine inter workings #also this is broke
	print "ON"
	game=Game_Variables(config)
	game=game.ResetGame(game)
	keyMap=Keypad_Mapping(config, game)
	game=keyMap.changeKeypad(game)
	keypad=Legacy_Keypad_Interface(config, game, keyMap)

	while 1:

		sleep(1)

#	GPIO.cleanup()  #Use to cleanup I/O pins for other uses

if __name__ == '__main__':
	main()
