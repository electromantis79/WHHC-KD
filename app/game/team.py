#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module simulates a team for all sports.

	:Created Date: 3/12/2015
	:Author: **Craig Gunter**

"""

import app.utils.reads
import app.game.player


class Team(object):
	"""Generic base class for all teams."""

	def __init__(self, sport_type='generic', number_of_players=None):
		self.sportType = sport_type
		self.numberOfPlayers = number_of_players

		# Build dictionary from file
		self.teamData = app.utils.reads.csv_one_row_read(file_name='Spreadsheets/teamDefaultValues.csv')

		# Choose default number of players if not given
		if self.numberOfPlayers is None:
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
			else:
				self.numberOfPlayers = 1  # number_of_players (generic , racetrack = 1)

		# Build player dictionary
		self.playersDict = {}
		for player in range(self.numberOfPlayers):
			name = 'PLAYER_'+str(player+1)
			self.playersDict[name] = app.game.player.Player()

		# Add data to teamData dict

		# All sports
		self.teamData['teamType'] = self.sportType
		self._set_data('score', self.teamData['score'], places=3)

		# Baseball
		self._set_data('pitchCount', self.teamData['pitchCount'], places=3)
		self._set_data('hits', self.teamData['hits'], places=3)
		self._set_data('errors', self.teamData['errors'])

		# Football
		# None

		# Soccer
		self._set_data('shots', self.teamData['shots'])
		self._set_data('kicks', self.teamData['kicks'])
		self._set_data('saves', self.teamData['saves'])

		# Hockey
		self._set_data('TIMER1_PLAYER_NUMBER', self.teamData['TIMER1_PLAYER_NUMBER'])
		self._set_data('TIMER2_PLAYER_NUMBER', self.teamData['TIMER2_PLAYER_NUMBER'])

		# Basketball
		self._set_data('fouls', self.teamData['fouls'])
		self.teamData['timeOutsLeft'] = self.teamData['TIME_OUTS_LEFT_BASK']

		# Stat
		self._set_data('playerOne', self.teamData['playerOne'])
		self._set_data('playerTwo', self.teamData['playerTwo'])
		self._set_data('playerThree', self.teamData['playerThree'])
		self._set_data('playerFour', self.teamData['playerFour'])
		self._set_data('playerFive', self.teamData['playerFive'])
		self._set_data('playerSix', self.teamData['playerSix'])

		self._set_data('foulOne', self.teamData['foulOne'])
		self._set_data('foulTwo', self.teamData['foulTwo'])
		self._set_data('foulThree', self.teamData['foulThree'])
		self._set_data('foulFour', self.teamData['foulFour'])
		self._set_data('foulFive', self.teamData['foulFive'])
		self._set_data('foulSix', self.teamData['foulSix'])

		self._set_data('pointsOne', self.teamData['pointsOne'])
		self._set_data('pointsTwo', self.teamData['pointsTwo'])
		self._set_data('pointsThree', self.teamData['pointsThree'])
		self._set_data('pointsFour', self.teamData['pointsFour'])
		self._set_data('pointsFive', self.teamData['pointsFive'])
		self._set_data('pointsSix', self.teamData['pointsSix'])

	def _set_data(self, data_name, value, places=2):
		if places == 3:
			self.teamData[data_name + 'Hundreds'] = value / 100
			self.teamData[data_name + 'Tens'] = value / 10 % 10
			self.teamData[data_name + 'Units'] = value % 10
			self.teamData[data_name] = value
		elif places == 2:
			if value == 255:
				self.teamData[data_name + 'Tens'] = 15
				self.teamData[data_name + 'Units'] = 15
				self.teamData[data_name] = value
			else:
				self.teamData[data_name + 'Tens'] = value / 10
				self.teamData[data_name + 'Units'] = value % 10
				self.teamData[data_name] = value
		else:
			print('Failed to set %s value of %d.' % (data_name, value))
