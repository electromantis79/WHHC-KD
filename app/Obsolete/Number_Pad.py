#!/usr/bin/env python

# by Craig Gunter
#
# "Number_Pad module"
#
# Number_Pad()Input = None
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

class Number_Pad(object):

	def __init__(self, configDict):
		self.sport = configDict['sport']
		self.clearFlag = False
		self.enterFlag = False
		self.lastNumberPressed = 0
		self.numberPressedSequence = ''

	def numberPressed(self, game, key):
		if not game.lampTestFlag and not game.blankTestFlag:
			game.numpad.lastNumberPressed = key
			game.numpad.numberPressedSequence+=str(game.numpad.lastNumberPressed)

		return game

	def Number_7_ABC(self, game):
		key=7
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_8_DEF(self, game):
		key=8
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_9_GHI(self, game):
		key=9
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_4_JKL(self, game):
		key=4
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_5_MNO(self, game):
		key=5
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_6_PQR(self, game):
		key=6
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_1_STU(self, game):
		key=1
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_2_VWX(self, game):
		key=2
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_3_YZ(self, game):
		key=3
		game=game.numpad.numberPressed(game, key)
		return game

	def Number_0(self, game):
		key=0
		game=game.numpad.numberPressed(game, key)
		return game

	def clear_FlashHit(self, game):
		if game.menuFlag:
			pass
		else:
			if game.sport=='MPBASEBALL1' or self.sport=='MPLINESCORE5' or self.sport=='MPLINESCORE4'or \
			self.sport=='MPMULTISPORT1' or self.sport=='MPMP-15X1' or self.sport=='MPMP-14X1':
				game.flashHitIndicator(game)
		game.numpad.clearFlag = True
		return game

	def enter_FlashError(self, game):
		if game.menuFlag:
			pass
		else:
			if game.sport=='MPBASEBALL1' or self.sport=='MPLINESCORE5' or self.sport=='MPLINESCORE4'or \
			self.sport=='MPMULTISPORT1' or self.sport=='MPMP-15X1' or self.sport=='MPMP-14X1':
				game.flashErrorIndicator(game)
		game.numpad.enterFlag = True
		return game

# Can't run by it's self because of circular import through Game_Variables.
# Test by running Game_Variables.

