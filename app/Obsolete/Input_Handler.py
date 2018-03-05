#!/usr/bin/env python

# by Craig Gunter
#
# "Input_Handler module"
#

from Config import *
from Game import *
from Keypad_Mapping import *

class Input_Handler(object):
	def __init__(self, game):

		self.keyMap=Keypad_Mapping(game)


def main():
	print "ON"
	sport='MMBASEBALL3'
	game = selectSportInstance(sport)
	printDict(game.__dict__)
	raw_input()
	In=Input_Handler(game)
	keyMap=Keypad_Mapping(game)

	while 1:
		PRESSED=raw_input('                                     Type key (Ex. B8): ')
		keyMap.Map(game, PRESSED)




if __name__ == '__main__':
	main()
