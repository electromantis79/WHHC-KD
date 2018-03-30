#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. topic:: Overview

	This module simulates a player for all sports.

	:Created Date: 3/12/2015
	:Author: **Craig Gunter**
"""

import app.utils.reads


class Player(object):

	def __init__(self):

		# Build dictionary from file
		self.playerData = app.utils.reads.csv_one_row_read(file_name='Spreadsheets/playerDefaultValues.csv')

		self.playerData['pointsUnits'] = self.playerData['points'] % 10
		self.playerData['pointsTens'] = self.playerData['points']/10
		self.playerData['pointsHundreds'] = self.playerData['points']/100

		self.playerData['foulsUnits'] = self.playerData['fouls'] % 10
		self.playerData['foulsTens'] = self.playerData['fouls']/10

		self.playerData['playerNumber'] = '  '
		self.playerData['playerNumberUnits'] = ' '
		self.playerData['playerNumberTens'] = ' '
		# NOT using this right for stat
