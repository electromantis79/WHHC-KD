#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module reads, writes, or modifies the gameDefaultSettings and gameUserSettings files.

	:Created Date: 3/12/2015
	:Author: **Craig Gunter**

"""

import time
# import pkg_resources  # Not sure if i need this

import app.utils.functions
import app.utils.misc
import app.utils.configobj


class GameDefaultSettings:
	"""Writes the chosen file or reads it and builds a dictionary of it named gameDefaultSettings."""

	def __init__(self, write=False, file_type='user'):
		self.fileType = file_type
		self.write = write
		self.tic = 0.0
		self.toc = 0.0
		self.gameDefaultSettings = {}
		self.gameDefaultSettingsFile = {}
		self.gameUserSettings = {}
		self._process_selection()

	def _process_selection(self):
		# Choose read or write and default or user
		
		if self.fileType == 'default':
			if self.write:
				self.gameDefaultSettings = app.utils.configobj.ConfigObj('game/gameDefaultSettings')
				self._write_all()
			else:
				self.gameDefaultSettingsFile = app.utils.configobj.ConfigObj('game/gameDefaultSettings', file_error=True)
				if self.gameDefaultSettingsFile:
					self._read_all()
				else:
					print(os.getcwd())
		elif self.fileType == 'user':
			if self.write:
				self.gameDefaultSettings = app.utils.configobj.ConfigObj('game/gameUserSettings')
				self._write_all()
			else:
				file_name = 'game/gameUserSettings'
				self.gameDefaultSettingsFile = app.utils.configobj.ConfigObj(file_name, file_error=True)
				if self.gameDefaultSettingsFile:
					self._read_all()
				else:
					print(os.getcwd()+'+/'+file_name)

	def _write_all(self):
		# Write all configurations to object and file.
		self.toc = time.time()

		# settings
		self.gameDefaultSettings['brightness'] = 100
		self.gameDefaultSettings['scoreTo19Flag'] = False
		self.gameDefaultSettings['doublePitchCountFlag'] = False
		self.gameDefaultSettings['pitchCountFlag'] = False
		self.gameDefaultSettings['linescoreStart'] = True
		self.gameDefaultSettings['inningBot'] = True
		self.gameDefaultSettings['newGameCount'] = 0
		self.gameDefaultSettings['dimmingCount'] = 0
		self.gameDefaultSettings['MPLX3450Flag'] = False
		self.gameDefaultSettings['I+2180Flag'] = False
		self.gameDefaultSettings['penaltySortFlag'] = False
		self.gameDefaultSettings['penaltyTwoActiveFlag'] = False
		self.gameDefaultSettings['clock_3D_or_less_Flag'] = False
		self.gameDefaultSettings['2D_Clock'] = False
		self.gameDefaultSettings['resetGameFlag'] = False
		self.gameDefaultSettings['restoreGameFlag'] = True
		self.gameDefaultSettings['timerActivityIndicatorReadEnableFlag'] = False

		self.gameDefaultSettings['periodClockCountUp'] = False
		self.gameDefaultSettings['periodClockResetFlag'] = False
		self.gameDefaultSettings['restoreFlag'] = False

		self.gameDefaultSettings['lampTestFlag'] = False
		self.gameDefaultSettings['blankTestFlag'] = False
		self.gameDefaultSettings['dimmingFlag'] = False
		self.gameDefaultSettings['periodClockTenthsFlag'] = False
		self.gameDefaultSettings['lastKeyPressedString'] = ''
		self.gameDefaultSettings['menuFlag'] = False
		self.gameDefaultSettings['guest'] = 0
		self.gameDefaultSettings['home'] = 1
		self.gameDefaultSettings['hoursFlag'] = False
		self.gameDefaultSettings['hoursFlagJumper'] = False
		self.gameDefaultSettings['pitchSpeedFlag'] = False
		self.gameDefaultSettings['ballsMax'] = 3
		self.gameDefaultSettings['strikesMax'] = 2
		self.gameDefaultSettings['outsMax'] = 2
		self.gameDefaultSettings['TOLMaxFB'] = 3
		self.gameDefaultSettings['TOLMaxBB'] = 5
		self.gameDefaultSettings['FoulsMax'] = 19
		self.gameDefaultSettings['MP320Flag'] = False
		self.gameDefaultSettings['quarterMax'] = 4
		self.gameDefaultSettings['periodMax'] = 4
		self.gameDefaultSettings['yardsToGoUnits_to_quarter'] = False
		self.gameDefaultSettings['playerMatchGameFlag'] = False
		self.gameDefaultSettings['vollyballFlag'] = False
		self.gameDefaultSettings['playerStatDoubleZeroFlag'] = False
		self.gameDefaultSettings['timer1teamOneplayerFlag'] = False
		self.gameDefaultSettings['timer1teamTwoplayerFlag'] = False
		self.gameDefaultSettings['timer2teamOneplayerFlag'] = False
		self.gameDefaultSettings['timer2teamTwoplayerFlag'] = False
		self.gameDefaultSettings['timer3teamOneplayerFlag'] = False
		self.gameDefaultSettings['timer3teamTwoplayerFlag'] = False
		self.gameDefaultSettings['timer4teamOneplayerFlag'] = False
		self.gameDefaultSettings['timer4teamTwoplayerFlag'] = False

		# -------clock settings-------
		self.gameDefaultSettings['periodHornFlashDuration'] = 2
		self.gameDefaultSettings['shotClockHornFlashDuration'] = 2
		self.gameDefaultSettings['delayOfGameHornFlashDuration'] = 2
		self.gameDefaultSettings['menuTimerDuration'] = 8
		self.gameDefaultSettings['numberOfClockDigits'] = 4
		self.gameDefaultSettings['mainClockDisplayType'] = 'periodClock'
		self.gameDefaultSettings['hitIndicatorFlashCount'] = 8  # number must be total of ons and offs, 4 flashes is 8 counts
		self.gameDefaultSettings['hitFlashDuration'] = 0.5
		self.gameDefaultSettings['errorIndicatorFlashCount'] = 8  # num must be total of ons and offs, 4 flashes is 8 counts
		self.gameDefaultSettings['errorFlashDuration'] = 0.5
		self.gameDefaultSettings['assignErrorFlashCount'] = 8  # number must be total of ons and offs, 4 flashes is 8 counts
		self.gameDefaultSettings['assignErrorFlashDuration'] = 0.5

		self.gameDefaultSettings['timeOfDayClockMaxSeconds'] = 43200
		self.gameDefaultSettings['timeOutTimerMaxSeconds'] = 60
		self.gameDefaultSettings['delayOfGameMaxSeconds1'] = 40
		self.gameDefaultSettings['delayOfGameMaxSeconds2'] = 25
		self.gameDefaultSettings['homeTimer1_maxSeconds'] = 599
		self.gameDefaultSettings['homeTimer2_maxSeconds'] = 599
		self.gameDefaultSettings['guestTimer1_maxSeconds'] = 599
		self.gameDefaultSettings['guestTimer2_maxSeconds'] = 599
		self.gameDefaultSettings['shotClockMaxSeconds1'] = 35
		self.gameDefaultSettings['shotClockMaxSeconds2'] = 15

		# Period Clocks
		self.gameDefaultSettings['MM_baseballPeriodClockMaxSeconds'] = 720
		self.gameDefaultSettings['MP_baseballPeriodClockMaxSeconds'] = 60
		self.gameDefaultSettings['MM_footballPeriodClockMaxSeconds'] = 720
		self.gameDefaultSettings['MP_footballPeriodClockMaxSeconds'] = 720
		self.gameDefaultSettings['MM_basketballPeriodClockMaxSeconds'] = 720
		self.gameDefaultSettings['MP_basketballPeriodClockMaxSeconds'] = 480
		self.gameDefaultSettings['MP_soccerPeriodClockMaxSeconds'] = 2700
		self.gameDefaultSettings['MP_hockeyPeriodClockMaxSeconds'] = 480
		self.gameDefaultSettings['MP_cricketPeriodClockMaxSeconds'] = 480
		self.gameDefaultSettings['MP_racetrackPeriodClockMaxSeconds'] = 480
		self.gameDefaultSettings['periodClockCountUp'] = False
		self.gameDefaultSettings['periodClockResolution'] = 0.1

		# enable flags
		self.gameDefaultSettings['trackClockEnable'] = False
		self.gameDefaultSettings['periodClockEnable'] = True
		self.gameDefaultSettings['segmentTimerEnable'] = False
		self.gameDefaultSettings['etnEnable'] = True
		self.gameDefaultSettings['wirelessEnable'] = True
		self.gameDefaultSettings['dimmingEnable'] = True
		self.gameDefaultSettings['timeOfDayClockEnable'] = False
		self.gameDefaultSettings['timeOfDayClockBlankingEnable'] = False
		self.gameDefaultSettings['shotClockBlankEnable'] = False
		self.gameDefaultSettings['penaltyClockEnable'] = False

		self.gameDefaultSettings['periodHornEnable'] = True
		self.gameDefaultSettings['shotClockHornEnable'] = True
		self.gameDefaultSettings['delayOfGameHornEnable'] = True
		self.gameDefaultSettings['endOfPeriodHornEnable'] = True
		self.gameDefaultSettings['endOfShotClockHornEnable'] = True
		self.gameDefaultSettings['endOfTimeOutTimerHornEnable'] = True
		self.gameDefaultSettings['visualHornEnable'] = True
		self.gameDefaultSettings['timeOutTimerEnable'] = False
		self.gameDefaultSettings['timeOutTimerToScoreboard'] = False
		self.gameDefaultSettings['tenthsEnable'] = False
		self.gameDefaultSettings['precisionEnable'] = False
		self.gameDefaultSettings['periodHornFlashEnable'] = False
		self.gameDefaultSettings['hitIndicatorFlashEnable'] = False
		self.gameDefaultSettings['errorIndicatorFlashEnable'] = False
		self.gameDefaultSettings['assignErrorFlashEnable'] = True

		# default Flags
		self.gameDefaultSettings['currentTeamGuest'] = False
		self.gameDefaultSettings['lampTestFlag'] = False
		self.gameDefaultSettings['blankTestFlag'] = False
		self.gameDefaultSettings['checkLCDFlag'] = False
		self.gameDefaultSettings['menuFlag'] = False
		self.gameDefaultSettings['whh_flag'] = True
		self.gameDefaultSettings['keyPressFlag'] = False
		self.gameDefaultSettings['restoreFlag'] = False
		self.gameDefaultSettings['PitchSpeedFlag'] = False
		self.gameDefaultSettings['refreshDisplayFlag'] = False
		self.gameDefaultSettings['multisportMenuFlag'] = False
		self.gameDefaultSettings['multisportChoiceFlag'] = True

		self.gameDefaultSettings['statNumber'] = None
		self.gameDefaultSettings['playerNumber'] = 255
		self.gameDefaultSettings['teamOneName'] = 'GUEST'
		self.gameDefaultSettings['teamTwoName'] = 'HOME'
		self.gameDefaultSettings['teamOneFont'] = 3
		self.gameDefaultSettings['teamTwoFont'] = 3
		self.gameDefaultSettings['teamOneJustify'] = 2
		self.gameDefaultSettings['teamTwoJustify'] = 2

		# THIS SECTION BUILDS THE self.config OBJECT THAT IS WRITTEN TO THE FILE
		print("WROTE TO FILE")

		self.gameDefaultSettings.write()  # Create 'config' file. Everything will be converted to strings
		self.tic = time.time()

	def _read_all(self):
		# Read all configurations from file and store in object
		self.toc = time.time()
		self.gameDefaultSettings = {}
		for key in list(self.gameDefaultSettingsFile.keys()):
			if self.gameDefaultSettingsFile[key] == 'False' or self.gameDefaultSettingsFile[key] == 'True':
				self.gameDefaultSettings[key] = app.utils.functions.tf(self.gameDefaultSettingsFile[key])
			elif self.gameDefaultSettingsFile[key].find('.') != -1:
				self.gameDefaultSettings[key] = float(self.gameDefaultSettingsFile[key])
			elif str(self.gameDefaultSettingsFile[key]).isdigit():
				self.gameDefaultSettings[key] = int(self.gameDefaultSettingsFile[key])
			elif str(self.gameDefaultSettingsFile[key]).isalnum() or self.gameDefaultSettingsFile[key].isalpha():
				self.gameDefaultSettings[key] = self.gameDefaultSettingsFile[key]
			elif self.gameDefaultSettingsFile[key] == '':
				self.gameDefaultSettings[key] = self.gameDefaultSettingsFile[key]
			else:
				print(self.gameDefaultSettingsFile[key], 'format not recognized')
				raise Exception
		self.tic = time.time()

	def get_dict(self):
		"""Return **gameDefaultSettings** dictionary."""
		return self.gameDefaultSettings

	def user_equals_default(self):
		"""Update gameUserSettings file with gameDefaultSettings file values."""
		self.gameUserSettings = app.utils.configobj.ConfigObj('game/gameUserSettings')
		self.fileType = 'default'
		self.write = False
		self._process_selection()
		self.gameUserSettings.clear()
		self.gameUserSettings.update(self.gameDefaultSettings)
		self.gameUserSettings.write()


def create_settings_files():
	"""
	Run this module with writeConfigFlag=True to create the gameDefaultSettings file.
	Next press enter to copy it to the gameUserSettings file.
	"""
	print("ON")
	write_game_default_settings_flag = True
	if write_game_default_settings_flag:
		app.utils.misc.silent_remove('game/gameDefaultSettings')
	g = GameDefaultSettings(write_game_default_settings_flag, 'default')
	app.utils.misc.print_dict(g.__dict__)
	print("%f seconds to run 'gameSettings' file setup." % (g.tic - g.toc))
	input()
	app.utils.misc.silent_remove('game/gameUserSettings')
	g.user_equals_default()
	app.utils.misc.print_dict(g.__dict__)

	print("%f seconds to run 'gameSettings' file setup." % (g.tic - g.toc))


if __name__ == '__main__':
	import os
	os.chdir('..') 
	"""Added this for csv_one_row_read to work with this structure, 
	add this line for each level below project root"""
	create_settings_files()
