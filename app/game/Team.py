#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 99%  Sphinx Approved = **True**

.. topic:: Overview

    This module simulates a team for all sports.

    :Created Date: 3/12/2015
    :Modified Date: 10/21/2016
    :Author: **Craig Gunter**

"""

from app.functions import *
from Player import Player

class Team(object):
	'''Generic base class for all teams.'''
	def __init__(self, sportType='generic', numberOfPlayers=1):
		self.sportType=sportType
		self.numberOfPlayers=numberOfPlayers
		self._Reset()

	def _Reset(self):
		#build dictionaries	from files
		self.teamData=csvOneRowRead(fileName='Spreadsheets/teamDefaultValues.csv')

		#numberOfPlayers (generic , racetrack = 1)
		if self.sportType=='baseball':
			self.numberOfPlayers=25
		elif self.sportType=='football':
			self.numberOfPlayers=53
			self.teamData['timeOutsLeft'] = self.teamData['TIME_OUTS_LEFT_FB']
		elif self.sportType=='soccer' or self.sportType=='cricket':
			self.numberOfPlayers=11
		elif self.sportType=='hockey':
			self.numberOfPlayers=20
		elif self.sportType=='basketball':
			self.numberOfPlayers=12
			self.teamData['timeOutsLeft'] = self.teamData['TIME_OUTS_LEFT_BASK']
		elif self.sportType=='stat':
			self.numberOfPlayers=32

		self.playersDict={}
		self.playerNamesList=[]
		for player in range(self.numberOfPlayers):
			name='PLAYER_'+str(player+1)
			self.playerNamesList.append(name)
			self.playersDict[name]=Player()

		self.teamData['teamType'] = self.sportType
		self.setData('score', self.teamData['score'], places=3)

		#Baseball
		self.setData('pitchCount', self.teamData['pitchCount'], places=3)
		self.setData('hits', self.teamData['hits'], places=3)
		self.setData('errors', self.teamData['errors'])

		#Football
		#None

		#Soccer
		self.setData('shots', self.teamData['shots'])
		self.setData('kicks', self.teamData['kicks'])
		self.setData('saves', self.teamData['saves'])

		#Hockey
		self.setData('TIMER1_PLAYER_NUMBER', self.teamData['TIMER1_PLAYER_NUMBER'])
		self.setData('TIMER2_PLAYER_NUMBER', self.teamData['TIMER2_PLAYER_NUMBER'])

		#Basketball
		self.setData('fouls', self.teamData['fouls'])
		self.teamData['timeOutsLeft'] = self.teamData['TIME_OUTS_LEFT_BASK']

		#Stat
		self.setData('playerOne', self.teamData['playerOne'])
		self.setData('playerTwo', self.teamData['playerTwo'])
		self.setData('playerThree', self.teamData['playerThree'])
		self.setData('playerFour', self.teamData['playerFour'])
		self.setData('playerFive', self.teamData['playerFive'])
		self.setData('playerSix', self.teamData['playerSix'])

		self.setData('foulOne', self.teamData['foulOne'])
		self.setData('foulTwo', self.teamData['foulTwo'])
		self.setData('foulThree', self.teamData['foulThree'])
		self.setData('foulFour', self.teamData['foulFour'])
		self.setData('foulFive', self.teamData['foulFive'])
		self.setData('foulSix', self.teamData['foulSix'])

		self.setData('pointsOne', self.teamData['pointsOne'])
		self.setData('pointsTwo', self.teamData['pointsTwo'])
		self.setData('pointsThree', self.teamData['pointsThree'])
		self.setData('pointsFour', self.teamData['pointsFour'])
		self.setData('pointsFive', self.teamData['pointsFive'])
		self.setData('pointsSix', self.teamData['pointsSix'])
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
	'''Test function if module ran independently.
	Prints object data with printDictsExpanded function.'''
	while 1:
		print "ON"
		sport='baseball'
		printDictsExpanded(Team(sport))

if __name__ == '__main__':
	os.chdir('..') 
	'''Added this for csvOneRowRead to work with this structure, 
	add this line for each level below project root'''
	test()
