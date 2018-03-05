#!/usr/bin/env python

# by Craig Gunter
#
# "Keypad_Mapping_Rules module"
#
# Keypad_Mapping_Rules()Input = None
#
# 		() =
#
#
#			main() =


#	Varibles available /w Defaults
"""




"""
from time import sleep

from Config import *
from Game import *

class Keypad_Mapping_Rules(object):


	def __init__(self, game):

		self.sport = game.sport
		self.funcStrings = []
		self.Rule_1_Flag = False

		self.keyRulesFuncDict = {'noRules':self.noRules, 'alterGuestScorePlusTen':self.alterGuestScorePlusTen}

		if self.sport == 'MMBASEBALL3':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MMBASEBALL4':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPBASEBALL1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPFOOTBALL1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MMFOOTBALL4':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport=='MPLINESCORE5' or self.sport=='MPLINESCORE4'or self.sport=='MPMULTISPORT1' or self.sport=='MPLX3450' or self.sport=='MPMP-15X1' or self.sport=='MPMP-14X1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPBASKETBALL1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPHOCKEY_LX1' or self.sport == 'MPHOCKEY1' or self.sport == 'MPSOCCER1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPSOCCER_LX1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.KeyRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}

	def Check(self, funcString, game):
		RuleString = self.KeyRules[self._lookup(funcString)]# find function name for active rules
		if RuleString!='':
			game=self.keyRulesFuncDict[RuleString](game)# call game function rule
		return game


	def _lookup(self, funcString):

		if self.Rule_1_Flag and self.funcStrings[1]==funcString:
			return 'Rule 1'

		return	'Rule 0'

	def alterGuestScorePlusTen(self, game): # fake test rule
		game.guestScore += 100
		print "Plus 100 to Guest Score with 'Rule 1' has applied."
		return game

	def noRules(self, game):
		return game

def main():
	print "ON"
	c=Config()
	sport='MPBASEBALL1'
	c.writeSport(sport)
	game = selectSportInstance(sport)
	keyRules = Keypad_Mapping_Rules(game)

	print game.guestScore
	keyRules.Rule_1_Flag = True
	funcString = 'guestScorePlusTen'
	keyRules.Check(funcString, game)
	print game.guestScore

#	while 1:

#		sleep(1)

if __name__ == '__main__':
	main()
