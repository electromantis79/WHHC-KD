#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. topic:: Overview

    This module simulates a player for all sports.

    :Created Date: 3/12/2015
    :Author: **Craig Gunter**
"""

import app.functions


class Player(object):

	def __init__(self):

		# Build dictionaries from files

		self.__dict__.update(app.functions.csvOneRowRead(fileName='Spreadsheets/playerDefaultValues.csv'))

		self.pointsUnits = self.points % 10
		self.pointsTens = self.points/10
		self.pointsHundreds = self.points/100

		self.foulsUnits = self.fouls % 10
		self.foulsTens = self.fouls/10

		self.playerNumber = '  '
		self.playerNumberUnits = ' '
		self.playerNumberTens = ' '
		# NOT using this right for stat
		# TODO: remove tens units concept from game modules
