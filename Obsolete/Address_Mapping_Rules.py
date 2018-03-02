#!/usr/bin/env python

# by Craig Gunter
#
# "Address_Mapping_Rules module"
#
# 	Address_Mapping_Rules()Input = None
#
# 		Initialize() = Prepare keypad event detection
#
#			main() = Initialize and wait for keypresses


#	Varibles available /w Defaults
"""

Don't Use this file


"""

from time import sleep

from Config import *
from Game import *
from MP_Data_Handler import *

class Address_Mapping_Rules(object):

	def __init__(self, sport):

		self.sport = sport
		self.funcStrings = []
		self.Rule_1_Flag = False

		self.mp = MP_Data_Handler()

		self.rulesFuncDict = {'noRules':self.noRules, 'alterGuestScoreBlanking':self.alterGuestScoreBlanking}

		if self.sport == 'MMBASEBALL3':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MMBASEBALL4':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPBASEBALL1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPFOOTBALL1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MMFOOTBALL4':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport=='MPLINESCORE5' or self.sport=='MPLINESCORE4'or self.sport=='MPMULTISPORT1' or self.sport=='MPLX3450' or self.sport=='MPMP-15X1' or self.sport=='MPMP-14X1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPBASKETBALL1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPHOCKEY_LX1' or self.sport == 'MPHOCKEY1' or self.sport == 'MPSOCCER1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}
		elif self.sport == 'MPSOCCER_LX1':
			self.funcStrings = ['', 'guestScorePlusTen']
			self.AddrRules = {'Rule 0':'noRules', 'Rule 1':'alterGuestScorePlusTen'}

	def Check(self, funcString, game):
		RuleString = self.AddrRules[self._lookup(funcString)]
		if RuleString!='':
			game=self.rulesFuncDict[RuleString](game)
		

	def _lookup(self, funcString):

		if self.Rule_1_Flag and self.funcStrings[1]==funcString:
			return 'Rule 1'

		return	'Rule 0'

	def alterGuestScoreBlanking(self, game, addrMap):
		addrMap.words[26]=self.mp.Encode(2, 3, 2, game.innings/10, 0, 'BCD', game.guestScore, 0, 0, 0)
#		addrMap.words[6]=self.mp.Encode(1, 2, 2, game.innings/10, 0, 'BCD', game.guestScore, 0, 0, 0)
		addrMap.words[10]=self.mp.Encode(1, 3, 2, game.innings/10, 0, 'BCD', game.guestScore, 0, 0, 0)
		return game, addrMap

	def noRules(self, game, addrMap):
		return game, addrMap


def main():
	print "ON"
	config = Config()
	configDict = config.getDict()
	game = selectSportInstance(configDict)
	addrRules=Address_Mapping_Rules(configDict['sport'])



if __name__ == '__main__':
	main()
