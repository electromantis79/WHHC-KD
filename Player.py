#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 99%  Sphinx Approved = **True**

.. topic:: Overview

    This module simulates a player for all sports.

    :Created Date: 3/12/2015
    :Modified Date: 10/28/2016
    :Author: **Craig Gunter**

"""

from functions import *

class Player(object):
	def __init__(self):
		self._Reset()

	def _Reset(self):
		#build dictionaries	from files

		self.playerData=csvOneRowRead(fileName='Spreadsheets/playerDefaultValues.csv')

		self.playerData['pointsUnits'] = self.playerData['points']%10
		self.playerData['pointsTens'] = self.playerData['points']/10
		self.playerData['pointsHundreds'] = self.playerData['points']/100

		self.playerData['foulsUnits']=self.playerData['fouls']%10
		self.playerData['foulsTens']=self.playerData['fouls']/10

		self.playerData['playerNumber']='  '
		self.playerData['playerNumberUnits']=' '
		self.playerData['playerNumberTens']=' '
		#NOT using this right for stat
		return

	def setData(self, dataName, value, places=2):
		if places==3:
			self.teamData[dataName+'Hundreds'] = value/100
			self.teamData[dataName+'Tens'] = value/10%10
			self.teamData[dataName+'Units'] = value%10
			self.teamData[dataName] = value
		elif places==2:
			if value==255:
				self.teamData[dataName+'Tens'] = 15
				self.teamData[dataName+'Units'] = 15
				self.teamData[dataName] = value
			else:
				self.teamData[dataName+'Tens'] = value/10
				self.teamData[dataName+'Units'] = value%10
				self.teamData[dataName] = value
		elif places==1:
			if dataName=='0' or dataName=='':
				pass
			else:
				self.gameData[dataName] = value
		else:
			print 'Failed to set %s value of %d.' % (dataName, value)
def test():
	'''Test function if module ran independently.'''
	while 1:
		print "ON"
		printDictsExpanded(Player())


if __name__ == '__main__':
	test()

