#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

    This module simulates a team for all sports.

    :Created Date: 3/12/2015
    :Author: **Craig Gunter**

"""

import app.functions
import app.game.player


class Team(object):
	"""Generic base class for all teams."""

	def __init__(self, sportType='generic', numberOfPlayers=1):
		self.sportType = sportType
		self.numberOfPlayers = numberOfPlayers

		# Build dictionary from file
		self.teamData = app.functions.csvOneRowRead(fileName='Spreadsheets/teamDefaultValues.csv')

		# Choose default number of players
		if self.sportType == 'baseball':
			self.numberOfPlayers = 25
		elif self.sportType == 'football':
			self.numberOfPlayers = 53
			self.teamData['timeOutsLeft'] = self.teamData['TIME_OUTS_LEFT_FB']
		elif self.sportType == 'soccer' or self.sportType == 'cricket':
			self.numberOfPlayers = 11
		elif self.sportType == 'hockey':
			self.numberOfPlayers = 20
		elif self.sportType == 'basketball':
			self.numberOfPlayers = 12
			self.teamData['timeOutsLeft'] = self.teamData['TIME_OUTS_LEFT_BASK']
		elif self.sportType == 'stat':
			self.numberOfPlayers = 32
		# numberOfPlayers (generic , racetrack = 1)

		# Build player dictionary
		self.playersDict = {}
		for player in range(self.numberOfPlayers):
			name = 'PLAYER_'+str(player+1)
			self.playersDict[name] = app.game.player.Player()

		# Add data to teamData dict

		# All sports
		self.teamData['teamType'] = self.sportType
		self._setData('score', self.teamData['score'], places=3)

		# Baseball
		self._setData('pitchCount', self.teamData['pitchCount'], places=3)
		self._setData('hits', self.teamData['hits'], places=3)
		self._setData('errors', self.teamData['errors'])

		# Football
		# None

		# Soccer
		self._setData('shots', self.teamData['shots'])
		self._setData('kicks', self.teamData['kicks'])
		self._setData('saves', self.teamData['saves'])

		# Hockey
		self._setData('TIMER1_PLAYER_NUMBER', self.teamData['TIMER1_PLAYER_NUMBER'])
		self._setData('TIMER2_PLAYER_NUMBER', self.teamData['TIMER2_PLAYER_NUMBER'])

		# Basketball
		self._setData('fouls', self.teamData['fouls'])
		self.teamData['timeOutsLeft'] = self.teamData['TIME_OUTS_LEFT_BASK']

		# Stat
		self._setData('playerOne', self.teamData['playerOne'])
		self._setData('playerTwo', self.teamData['playerTwo'])
		self._setData('playerThree', self.teamData['playerThree'])
		self._setData('playerFour', self.teamData['playerFour'])
		self._setData('playerFive', self.teamData['playerFive'])
		self._setData('playerSix', self.teamData['playerSix'])

		self._setData('foulOne', self.teamData['foulOne'])
		self._setData('foulTwo', self.teamData['foulTwo'])
		self._setData('foulThree', self.teamData['foulThree'])
		self._setData('foulFour', self.teamData['foulFour'])
		self._setData('foulFive', self.teamData['foulFive'])
		self._setData('foulSix', self.teamData['foulSix'])

		self._setData('pointsOne', self.teamData['pointsOne'])
		self._setData('pointsTwo', self.teamData['pointsTwo'])
		self._setData('pointsThree', self.teamData['pointsThree'])
		self._setData('pointsFour', self.teamData['pointsFour'])
		self._setData('pointsFive', self.teamData['pointsFive'])
		self._setData('pointsSix', self.teamData['pointsSix'])

	def _setData(self, dataName, value, places=2):
		if places == 3:
			self.teamData[dataName+'Hundreds'] = value/100
			self.teamData[dataName+'Tens'] = value/10 % 10
			self.teamData[dataName+'Units'] = value % 10
			self.teamData[dataName] = value
		elif places == 2:
			if value == 255:
				self.teamData[dataName+'Tens'] = 15
				self.teamData[dataName+'Units'] = 15
				self.teamData[dataName] = value
			else:
				self.teamData[dataName+'Tens'] = value/10
				self.teamData[dataName+'Units'] = value % 10
				self.teamData[dataName] = value
		else:
			print 'Failed to set %s value of %d.' % (dataName, value)
