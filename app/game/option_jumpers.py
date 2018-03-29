#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module simulates a console's option jumpers.

	:Created Date: 3/13/2015
	:Author: **Craig Gunter**

"""

# SPORT_LIST = ['MMBASEBALL3','MPBASEBALL1','MMBASEBALL4','MPLINESCORE4','MPLINESCORE5',
# 'MPMP-15X1','MPMP-14X1','MPMULTISPORT1-baseball','MPMULTISPORT1-football', 'MPFOOTBALL1',
# 'MMFOOTBALL4','MPBASKETBALL1','MPSOCCER_LX1-soccer','MPSOCCER_LX1-football','MPSOCCER1',
# 'MPHOCKEY_LX1','MPHOCKEY1','MPCRICKET1','MPRACETRACK1','MPLX3450-baseball','MPLX3450-football','MPGENERIC', 'MPSTAT']


class OptionJumpers(object):
	"""
	This class builds a dictionary of jumper options.
	The jumper string from the config file sets the special states for each sport.
	Call get_options to update the gameSettingsDict.
	"""

	# constructor
	def __init__(self, sport, sport_list, jumper_string='OOOO'):
		self.sport = sport
		self.sportList = sport_list
		self.jumperString = jumper_string
		self.optionsDict = {}

		if self.jumperString == 'OOOO':
			pass
		else:
			self._set_options()

	def _set_options(self):
		# Baseball
		if self.sport == 'MMBASEBALL3' or self.sport == 'MPBASEBALL1':
			if self.jumperString[0] == 'B':
				self.optionsDict['scoreTo19Flag'] = True
			if self.jumperString[1] == 'C':
				self.optionsDict['2D_Clock'] = True
			if self.jumperString[2] == 'D':
				self.optionsDict['hoursFlagJumper'] = True
			self._e_bso_433()

		if self.sport == 'MMBASEBALL4' or self.sport == 'MPMP-15X1':
			self._e_bso_433()

		if self.sport == 'MPLINESCORE4' or self.sport == 'MPMP-14X1':
			if self.jumperString[1] == 'C':
				self.optionsDict['pitchCountFlag'] = True
			self._e_bso_433()

		if self.sport == 'MPLINESCORE5':
			if self.jumperString[0] == 'B':
				self.optionsDict['pitchSpeedFlag'] = True
			if self.jumperString[1] == 'C':
				self.optionsDict['clock_3D_or_less_Flag'] = True
			if self.jumperString[2] == 'D':
				self.optionsDict['doublePitchCountFlag'] = True
			self._e_bso_433()

		# Football
		if self.sport == 'MPFOOTBALL1':
			if self.jumperString[0] == 'B':
				self.optionsDict['TOLMaxFB'] = 5
			if self.jumperString[1] == 'C':
				self.optionsDict['TOLMaxFB'] = 9
			if self.jumperString[2] == 'D':
				self.optionsDict['yardsToGoUnits_to_quarter'] = True
			if self.jumperString[3] == 'E':
				self.optionsDict['trackClockEnable'] = True

		if self.sport == 'MMFOOTBALL4':
			if self.jumperString[0] == 'B':
				self.optionsDict['quarterMax'] = 9
			if self.jumperString[2] == 'D':
				self.optionsDict['yardsToGoUnits_to_quarter'] = True

		# Multisport
		if (
				self.sport == 'MPMULTISPORT1-baseball' or self.sport == 'MPLX3450-baseball'
				or self.sport == 'MPMULTISPORT1-football' or self.sport == 'MPLX3450-football'):
			if self.jumperString[0] == 'B':
				self.optionsDict['MPLX3450Flag'] = True
			if self.jumperString[1] == 'C':
				self.optionsDict['clock_3D_or_less_Flag'] = True
			if self.jumperString[2] == 'D':
				self.optionsDict['MP320Flag'] = True
			self._e_bso_433()

		# Basketball
		if self.sport == 'MPBASKETBALL1':
			if self.jumperString[0] == 'B':
				self.optionsDict['periodMax'] = 9
			if self.jumperString[1] == 'C':
				self.optionsDict['I+2180Flag'] = True
			if self.jumperString[2] == 'D':
				self.optionsDict['Incandesent'] = True

		# Hockey
		if self.sport == 'MPHOCKEY_LX1' or self.sport == 'MPHOCKEY1':
			if self.jumperString[0] == 'B':
				self.optionsDict['penaltySortFlag'] = True
			if self.jumperString[1] == 'C':
				self.optionsDict['penaltyTwoActiveFlag'] = True
			if self.sport == 'MPHOCKEY_LX1':
				if self.jumperString[2] == 'D':
					self.optionsDict['penaltyClockEnable'] = True
			elif self.sport == 'MPHOCKEY1':
				if self.jumperString[2] == 'D':
					self.optionsDict['Incandesent'] = True
			if self.jumperString[3] == 'E':
				self.optionsDict['periodMax'] = 9

		# Soccer
		if self.sport == 'MPSOCCER_LX1-soccer' or self.sport == 'MPSOCCER_LX1-football' or self.sport == 'MPSOCCER1':
			if self.jumperString[0] == 'B':
				self.optionsDict['periodClockCountUp'] = False
			else:
				self.optionsDict['periodClockCountUp'] = True
			if self.jumperString[1] == 'C':
				self.optionsDict['quarterMax'] = 9
			if self.sport == 'MPSOCCER_LX1-soccer' or self.sport == 'MPSOCCER_LX1-football':
				if self.jumperString[2] == 'D':
					self.optionsDict['MP320Flag'] = True
			elif self.sport == 'MPSOCCER1':
				pass
			if self.jumperString[3] == 'E':
				self.optionsDict['trackClockEnable'] = True

	def _e_bso_433(self):
		if self.jumperString[3] == 'E':
			self.optionsDict['ballsMax'] = 4
			self.optionsDict['strikesMax'] = 3
			self.optionsDict['outsMax'] = 3

	# PUBLIC method

	def get_options(self, game_settings):
		"""Update **game_settings** with the current **optionsDict**."""
		game_settings.update(self.optionsDict)
		return game_settings
