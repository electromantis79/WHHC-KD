#!/usr/bin/env python

# by Craig Gunter
#
# "User_Interface_Handler module"
#
# User_Interface_Handler()Input = Sport
#
# 		__Init__() = Load default Classes
#
#
#			main() =


#	Varibles available /w Defaults
"""




"""

from time import sleep

from Config import *
#from GameDefaultSettings import *
from Game import *
from Keypad_Mapping import Keypad_Mapping
#from Legacy_Keypad_Interface import Legacy_Keypad_Interface
#from LCD_16X2_Display_Handler import LCD_16X2_Display_Handler


class User_Interface_Handler(object):

	def __init__(self, game): # create default instances for all classes
		self.consoleDisplayType = game.configDict['consoleDisplayType']

		if game.configDict['keypadType']=='MM' or game.configDict['keypadType']=='MP':
			self.keyMap=Keypad_Mapping(game)
			game=self.keyMap.selectKeypad(game)
			#self.keypad=Legacy_Keypad_Interface(game, self.keyMap)


def main():
	print "ON"
	c=Config(1)
	sport=c.config['sport']
	storedSportName=c.config['storedSportName']
	game = selectSportInstance(sport, storedSportName)
	ui=User_Interface_Handler(game)

	while 1:
		key=raw_input('Type key (Ex. B8): ')
		ui.keyMap.Map(key, game)
		gameDict=game.__dict__
		printDict(gameDict)

if __name__ == '__main__':
	main()
