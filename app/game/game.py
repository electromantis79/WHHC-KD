#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module holds the game data for all sports.

	:Created Date: 3/12/2015
	:Author: **Craig Gunter**

"""

import threading

import app.utils.functions
import app.utils.reads
import app.game.team
import app.game.option_jumpers
import app.game.clock


class Game(object):
	"""Generic base class for all sports."""
	
	def __init__(self, config_dict, number_of_teams=2):
		self.configDict = config_dict
		self.numberOfTeams = number_of_teams

		# Build dictionaries from files
		self.gameSettings = app.utils.reads.read_game_default_settings()
		self.segmentTimerSettings = app.utils.reads.read_segment_timer_settings()
		self.gameSettings.update(self.segmentTimerSettings)  # Don't use the same names
		self.gameData = app.utils.reads.csv_one_row_read(file_name='Spreadsheets/gameDefaultValues.csv')

		# Classes and attributes
		self.gameData['sportType'] = "GENERIC"
		self.gameData['sport'] = self.configDict['sport']
		self.gameData['optionJumpers'] = self.configDict['optionJumpers']
		self.gameData['Version'] = self.configDict['Version']

		# Handle option jumpers
		self.optionJumpers = app.game.option_jumpers.OptionJumpers(
			self.gameData['sport'], app.utils.functions.SPORT_LIST, jumper_string=self.gameData['optionJumpers'])
		self.gameSettings = self.optionJumpers.get_options(self.gameSettings)
		
		self.decimalIndicator = not self.gameData['colonIndicator']

		self._create_teams()

		self._add_team_name_data()

		self.clockDict = {}
		self._create_clock_dict()

		# Digit values common to all sports
		self.set_game_data('segmentCount', self.get_game_data('segmentCount'))
		self.set_game_data('period', self.get_game_data('period'))

		if self.gameData['sport'][-4:] == 'ball' or self.gameData['sport'][-6:] == 'soccer':
			self.gameSettings['multisportMenuFlag'] = True
		else:
			self.gameSettings['multisportMenuFlag'] = False

		if self.gameData['sport'][-8:] == 'football' or self.gameData['sport'][-6:] == 'soccer':
			self.gameSettings['multisportChoiceFlag'] = True
		else:
			self.gameSettings['multisportChoiceFlag'] = False
		
		# Variables
		self.hitCount = self.gameSettings['hitIndicatorFlashCount']
		self.errorCount = self.gameSettings['errorIndicatorFlashCount']
		self.activeGuestPlayerList = []
		self.activeHomePlayerList = []
		self.statNumberList = []
		self.notActiveIndex = None
		
	def _create_teams(self):
		"""Instantiate all teams into a dictionary."""
		self.teamsDict = {}
		self.teamNamesList = []
		for team in range(self.numberOfTeams):
			name = 'TEAM_'+str(team+1)
			self.teamNamesList.append(name)
			self.teamsDict[name] = app.game.team.Team(sport_type=self.gameData['sportType'])

	def _add_team_name_data(self):
		self.home = self.teamNamesList[self.gameSettings['home']]
		self.guest = self.teamNamesList[self.gameSettings['guest']]
		self.teamsDict[self.guest].teamData['name'] = self.gameSettings['teamOneName']
		self.teamsDict[self.home].teamData['name'] = self.gameSettings['teamTwoName']
		self.teamsDict[self.guest].teamData['font'] = self.gameSettings['teamOneFont']
		self.teamsDict[self.home].teamData['font'] = self.gameSettings['teamTwoFont']
		self.teamsDict[self.guest].teamData['justify'] = self.gameSettings['teamOneJustify']
		self.teamsDict[self.home].teamData['justify'] = self.gameSettings['teamTwoJustify']

	def _create_clock_dict(self):
		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['timeOutTimer'] = app.game.clock.Clock(
			False, self.gameSettings['timeOutTimerMaxSeconds'], clock_name='timeOutTimer')
		
		self.clockDict['timeOfDayClock'] = app.game.clock.Clock(
			True, max_seconds=self.gameSettings['timeOfDayClockMaxSeconds'],
			resolution=0.1, hours_flag=True, clock_name='timeOfDayClock')
		
		self.clockDict['segmentTimer'] = app.game.clock.Clock(
			self.gameSettings['segmentTimerCountUp'], self.gameSettings['segmentTimerMaxSeconds'], clock_name='segmentTimer')
		
		self.clockDict['flashTimer'] = app.game.clock.Clock(
			False, self.gameSettings['flashTimerMaxSeconds'], clock_name='flashTimer')
		
		self.clockDict['intervalTimer'] = app.game.clock.Clock(
			False, self.gameSettings['intervalTimerMaxSeconds'], clock_name='intervalTimer')
		
		self.clockDict['periodHornFlashTimer'] = app.game.clock.Clock(
			False, self.gameSettings['periodHornFlashDuration'], clock_name='periodHornFlashTimer')
		
		self.clockDict['periodBlinkyFlashTimer'] = app.game.clock.Clock(False, .5, clock_name='periodBlinkyFlashTimer')
		
		# game_data_update adds values to the gameData dictionary
		self.gameData = self.clockDict['timeOutTimer'].game_data_update(self.gameData, name='timeOutTimer')
		self.gameData = self.clockDict['timeOfDayClock'].game_data_update(self.gameData, name='timeOfDayClock')
		self.gameData = self.clockDict['segmentTimer'].game_data_update(self.gameData, name='segmentTimer')

		if self.gameData['sport'] == "MPGENERIC":
			self.clockDict['periodClock'] = app.game.clock.Clock(
				self.gameSettings['periodClockCountUp'], 15 * 60, clock_name='periodClock')
			self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData, name='periodClock')

	def _reverse_home_and_guest(self):
		# method never used
		self.home, self.guest = self.guest, self.home

	# END INIT ------------------------

	# PUBLIC methods

	def kill_clock_threads(self):
		for clock in self.clockDict:
			self.clockDict[clock].kill_()

	def get_player_data(self, team, data_name, player_id=None, player_number=None):
		if player_id is None and player_number is None:
			print(team, data_name, 'player_id=None, player_number=None')
		elif player_id is not None:
			return self.teamsDict[team].playersDict[player_id].playerData[data_name]
		elif player_number is not None:
			for player_id in list(self.teamsDict[team].playersDict.keys()):
				if self.teamsDict[team].playersDict[player_id].playerData['playerNumber'] == player_number:
					return player_id
		else:
			return self.teamsDict[team].playersDict[player_id].playerData[data_name]

	def get_team_data(self, team, data_name):
		return self.teamsDict[team].teamData[data_name]

	def get_game_data(self, data_name):
		return self.gameData[data_name]

	def get_clock_data(self, clock_name, data_name):
		if clock_name in self.clockDict:
			return self.clockDict[clock_name].timeUnitsDict[data_name]
		else:
			return None

	def set_player_data(self, team, player, data_name, value, places=2):
		if player in self.teamsDict[team].playersDict:
			player_data = self.teamsDict[team].playersDict[player].playerData
			if places == 3:
				player_data[data_name + 'Hundreds'] = value // 100
				player_data[data_name + 'Tens'] = value // 10 % 10
				player_data[data_name + 'Units'] = value % 10
				player_data[data_name] = value
			elif places == 2:
				if data_name == 'playerNumber':
					player_data[data_name + 'Tens'] = value[0]
					player_data[data_name + 'Units'] = value[1]
					player_data[data_name] = value
				else:
					player_data[data_name + 'Tens'] = value // 10
					player_data[data_name + 'Units'] = value % 10
					player_data[data_name] = value
			elif places == 1:
				if data_name == '0' or data_name == '':
					pass
				else:
					player_data[data_name] = value
			else:
				print('Failed to set '+team, data_name, 'value of', value)
				print('places', places, 'player', player, 'player_data', player_data)
		else:
			print('Player %s is not in self.teamsDict[team].playersDict.' % player)

	def set_team_data(self, team, data_name, value, places=2):
		team_data = self.teamsDict[team].teamData
		if value is not None:
			if places == 3:
				team_data[data_name + 'Hundreds'] = value // 100
				team_data[data_name + 'Tens'] = value // 10 % 10
				team_data[data_name + 'Units'] = value % 10
				team_data[data_name] = value
			elif places == 2:
				if value == 255:
					team_data[data_name + 'Tens'] = 15
					team_data[data_name + 'Units'] = 15
					team_data[data_name] = value
				else:
					team_data[data_name + 'Tens'] = value // 10
					team_data[data_name + 'Units'] = value % 10
					team_data[data_name] = value
			elif places == 1:
				if data_name == '0' or data_name == '':
					pass
				else:
					team_data[data_name] = value
			else:
				print('Failed to set %s %s value of %d.' % (team, data_name, value))
				print('places', places, 'team_data', team_data)
		else:
				print('Failed to set %s %s value of None.' % (team, data_name))
				print('places', places, 'team_data', team_data)

	def set_game_data(self, data_name, value, places=2):
		if places == 3:
			self.gameData[data_name + 'Hundreds'] = value // 100
			self.gameData[data_name + 'Tens'] = value // 10 % 10
			self.gameData[data_name + 'Units'] = value % 10
			self.gameData[data_name] = value
		elif places == 2:
			if value == 255:
				self.gameData[data_name + 'Tens'] = 15
				self.gameData[data_name + 'Units'] = 15
				self.gameData[data_name] = value
			else:
				self.gameData[data_name + 'Tens'] = value // 10
				self.gameData[data_name + 'Units'] = value % 10
				self.gameData[data_name] = value
		elif places == 1:
			if data_name == '0' or data_name == '':
				pass
			else:
				self.gameData[data_name] = value
		else:
			print('Failed to set %s value of %d.' % (data_name, value))

	def set_clock_data(self, clock_name, data_name, value, places=2):

		clock_data = self.clockDict[clock_name].timeUnitsDict
		if places == 3:
			clock_data[data_name + 'Hundreds'] = value // 100
			clock_data[data_name + 'Tens'] = value // 10 % 10
			clock_data[data_name + 'Units'] = value % 10
			clock_data[data_name] = value
		elif places == 2:
			clock_data[data_name + 'Tens'] = value // 10
			clock_data[data_name + 'Units'] = value % 10
			clock_data[data_name] = value
		elif places == 1:
			if data_name == '0' or data_name == '':
				pass
			else:
				clock_data[data_name] = value
		else:
			print('Failed to set %s %s value of %d.' % (clock_name, data_name, value))

	def mod_player_data(self, team, player, data_name, modulus_value=100, operator='+', mod_value=1, places=2):
		player_data = self.teamsDict[team].playersDict[player].playerData
		if data_name != 'playerNumber':
			if operator == '+':
				player_data[data_name] = (player_data[data_name] + mod_value) % modulus_value
			elif operator == '-':
				player_data[data_name] = (player_data[data_name] - mod_value) % modulus_value
			elif operator == '*':
				player_data[data_name] = (player_data[data_name] * mod_value) % modulus_value
			elif operator == '/':
				player_data[data_name] = (player_data[data_name] // mod_value) % modulus_value
			elif operator == 'toggle':
				player_data[data_name] = not player_data[data_name]
				places = 0
			if places == 3:
				player_data[data_name + 'Hundreds'] = player_data[data_name] // 100
				player_data[data_name + 'Tens'] = player_data[data_name] // 10 % 10
				player_data[data_name + 'Units'] = player_data[data_name] % 10
			elif places == 2:
				player_data[data_name + 'Tens'] = player_data[data_name] // 10
				player_data[data_name + 'Units'] = player_data[data_name] % 10

	def mod_team_data(self, team, data_name, modulus_value=100, operator='+', mod_value=1, places=2):
		team_data = self.teamsDict[team].teamData
		if operator == '+':
			team_data[data_name] = (team_data[data_name] + mod_value) % modulus_value
		elif operator == '-':
			team_data[data_name] = (team_data[data_name] - mod_value) % modulus_value
		elif operator == '*':
			team_data[data_name] = (team_data[data_name] * mod_value) % modulus_value
		elif operator == '/':
			team_data[data_name] = (team_data[data_name] // mod_value) % modulus_value
		elif operator == 'toggle':
			team_data[data_name] = not team_data[data_name]
			places = 0
		if places == 3:
			team_data[data_name + 'Hundreds'] = team_data[data_name] // 100
			team_data[data_name + 'Tens'] = team_data[data_name] // 10 % 10
			team_data[data_name + 'Units'] = team_data[data_name] % 10
		elif places == 2:
			team_data[data_name + 'Tens'] = team_data[data_name] // 10
			team_data[data_name + 'Units'] = team_data[data_name] % 10

	def mod_game_data(self, data_name, modulus_value=100, operator='+', mod_value=1, places=2):
		if operator == '+':
			self.gameData[data_name] = (self.gameData[data_name] + mod_value) % modulus_value
		elif operator == '-':
			self.gameData[data_name] = (self.gameData[data_name] - mod_value) % modulus_value
		elif operator == '*':
			self.gameData[data_name] = (self.gameData[data_name] * mod_value) % modulus_value
		elif operator == '/':
			self.gameData[data_name] = (self.gameData[data_name] // mod_value) % modulus_value
		elif operator == 'toggle':
			self.gameData[data_name] = not self.gameData[data_name]
			places = 0
		if places == 3:
			self.gameData[data_name + 'Hundreds'] = self.gameData[data_name] // 100
			self.gameData[data_name + 'Tens'] = self.gameData[data_name] // 10 % 10
			self.gameData[data_name + 'Units'] = self.gameData[data_name] % 10
		elif places == 2:
			self.gameData[data_name + 'Tens'] = self.gameData[data_name] // 10
			self.gameData[data_name + 'Units'] = self.gameData[data_name] % 10

	def mod_clock_data(self, clock_name, data_name, operator='+', modulus_value=60, mod_value=1, places=2):

		clock_data = self.clockDict[clock_name].timeUnitsDict
		if operator == '+':
			clock_data[data_name] = (clock_data[data_name] + mod_value) % modulus_value
		elif operator == '-':
			clock_data[data_name] = (clock_data[data_name] - mod_value) % modulus_value
		elif operator == '*':
			clock_data[data_name] = (clock_data[data_name] * mod_value) % modulus_value
		elif operator == '/':
			clock_data[data_name] = (clock_data[data_name] // mod_value) % modulus_value
		elif operator == 'toggle':
			clock_data[data_name] = not clock_data[data_name]
			places = 0
		if places == 3:
			clock_data[data_name + 'Hundreds'] = clock_data[data_name] // 100
			clock_data[data_name + 'Tens'] = clock_data[data_name] // 10 % 10
			clock_data[data_name + 'Units'] = clock_data[data_name] % 10
		elif places == 2:
			clock_data[data_name + 'Tens'] = clock_data[data_name] // 10
			clock_data[data_name + 'Units'] = clock_data[data_name] % 10

	# Keypad methods

	# GENERIC METHODS----------------------------------------

	def handheldButton1(self):
		self.clockDict['delayOfGameClock'].reset_(self.gameSettings['delayOfGameMaxSeconds1'])

	def handheldButton2(self):
		self.clockDict['delayOfGameClock'].reset_(self.gameSettings['delayOfGameMaxSeconds2'])

	def handheldButton3(self):
		if self.clockDict['delayOfGameClock'].running:
			self.clockDict['delayOfGameClock'].stop_()
		else:
			self.clockDict['delayOfGameClock'].start_()

	def guestScorePlusTen(self):
		team = self.guest
		self.mod_team_data(team, data_name='score', operator='+', modulus_value=100, mod_value=10)

	def guestScorePlusOne(self):
		if not self.gameSettings['menuFlag']:
			team = self.guest
			data_name = 'score'
			if self.gameSettings['scoreTo19Flag']:
				self.mod_team_data(team, data_name, operator='+', modulus_value=20, mod_value=1)
			elif (
					self.gameData['sport'] == 'MPBASKETBALL1' or self.gameData['sport'] == 'MPHOCKEY_LX1'
					or self.gameData['sport'] == 'MPHOCKEY1'):
				self.mod_team_data(team, data_name, operator='+', modulus_value=200, mod_value=1, places=3)
			else:
				self.mod_team_data(team, data_name, operator='+', modulus_value=100, mod_value=1)

	def guestScoreMinusOne(self):
		team = self.guest
		self.mod_team_data(team, data_name='score', operator='-', modulus_value=100, mod_value=1)

	def homeScorePlusTen(self):
		team = self.home
		self.mod_team_data(team, data_name='score', operator='+', modulus_value=100, mod_value=10)

	def homeScorePlusOne(self):
		if not self.gameSettings['menuFlag']:
			team = self.home
			data_name = 'score'
			if self.gameSettings['scoreTo19Flag']:
				self.mod_team_data(team, data_name, operator='+', modulus_value=20, mod_value=1)
			elif (
					self.gameData['sport'] == 'MPBASKETBALL1' or self.gameData['sport'] == 'MPHOCKEY_LX1'
					or self.gameData['sport'] == 'MPHOCKEY1'):
				self.mod_team_data(team, data_name, operator='+', modulus_value=200, mod_value=1, places=3)
			else:
				self.mod_team_data(team, data_name, operator='+', modulus_value=100, mod_value=1)

	def homeScoreMinusOne(self):
		team = self.home
		self.mod_team_data(team, data_name='score', operator='-', modulus_value=100, mod_value=1)

	def Horn(self):
		if self.gameSettings['periodHornEnable']:
			if self.gameSettings['endOfTimeOutTimerHornEnable'] and self.gameData['sportType'] == 'football':
				print('\a\aHORN ON')
				self.gameData['periodHorn'] = True
			elif self.gameSettings['endOfPeriodHornEnable']:
				print('\a\aHORN ON')
				self.gameData['periodHorn'] = True
			if self.gameSettings['visualHornEnable']:
				self.gameData['visualHornIndicator1'] = True
				print('VISUAL HORN ON')
				if self.gameData['sportType'] == 'basketball' or self.gameData['sportType'] == 'hockey':
					self.gameData['visualHornIndicator2'] = True
			threading.Timer(self.gameSettings['periodHornFlashDuration'], self.hornOff).start()

	def shotHorn(self):
		if self.gameSettings['shotClockHornEnable']:
			if self.gameSettings['endOfShotClockHornEnable']:
				print('\a\aSHOT CLOCK HORN ON')
				self.gameData['shotClockHorn'] = True
			threading.Timer(self.gameSettings['shotClockHornFlashDuration'], self.shotHornOff).start()

	def delayOfGameHorn(self):
		if self.gameSettings['delayOfGameHornEnable']:
			print('\a\aDELAY OF GAME CLOCK HORN ON')
			self.gameData['delayOfGameHorn'] = True
			threading.Timer(self.gameSettings['delayOfGameHornFlashDuration'], self.delayOfGameHornOff).start()

	def hornOff(self):
		print('\aHORNS OFF')
		self.gameData['periodHorn'] = False
		self.gameData['visualHornIndicator1'] = False
		if self.gameData['sportType'] == 'basketball':
			self.gameData['visualHornIndicator2'] = False

	def shotHornOff(self):
		print('\aSHOT CLOCK HORN OFF')
		self.gameData['shotClockHorn'] = False

	def delayOfGameHornOff(self):
		print('\aDELAY OF GAME CLOCK HORN OFF')
		self.gameData['delayOfGameHorn'] = False

	def periodClockOnOff(self):
		if self.gameSettings['segmentTimerEnable']:
			clock_name = 'segmentTimer'
		elif self.gameSettings['timeOutTimerEnable']:
			self.gameSettings['timeOutTimerEnable'] = False
			clock_name = 'timeOutTimer'
			self.clockDict[clock_name].stop_()
			self.clockDict[clock_name].reset_()
			clock_name = 'periodClock'
		else:
			clock_name = 'periodClock'

		if self.gameSettings['precisionEnable'] or self.gameSettings['lampTestFlag'] or self.gameSettings['blankTestFlag']:
			print('periodClockOnOff button not active')
			return

		else:
			if not self.clockDict[clock_name].running:
				self.clockDict[clock_name].start_()
				if self.gameData['sport'] == 'MPBASKETBALL1' or self.gameData['sportType'] == 'hockey':
					self.clockDict['shotClock'].start_()
					if self.gameData['sportType'] == 'hockey':
						for clock_name in list(self.clockDict.keys()):
							if clock_name[:7] == 'penalty':
								self.clockDict[clock_name].start_()
			else:
				self.clockDict[clock_name].stop_()
				if self.gameData['sport'] == 'MPBASKETBALL1' or self.gameData['sportType'] == 'hockey':
					self.clockDict['shotClock'].stop_()
					if self.gameData['sportType'] == 'hockey':
							for clock_name in list(self.clockDict.keys()):
								if clock_name[:7] == 'penalty':
									self.clockDict[clock_name].stop_()

	def minutesMinusOne(self):
		if not self.clockDict['periodClock'].running:
			if self.clockDict['periodClock'].currentTime <= 60:  # don't allow negative time
				self.clockDict['periodClock'].change_seconds(-self.clockDict['periodClock'].currentTime)
			else:
				self.clockDict['periodClock'].change_seconds(-60)

	def secondsMinusOne(self):
		if not self.clockDict['periodClock'].running:
			if self.clockDict['periodClock'].currentTime <= 1:  # don't allow negative time
				self.clockDict['periodClock'].change_seconds(-self.clockDict['periodClock'].currentTime)
			else:
				self.clockDict['periodClock'].change_seconds(-1)

	def secondsPlusOne(self):
		if not self.clockDict['periodClock'].running:
			self.clockDict['periodClock'].change_seconds(1)

	def quartersPlusOne(self):
		modulus_value = self.gameSettings['quarterMax']+1
		self.mod_game_data(data_name='quarter', modulus_value=modulus_value, mod_value=1, places=1, operator='+')

	def periodsPlusOne(self):
		modulus_value = (self.gameSettings['periodMax']+1)
		self.mod_game_data(data_name='period', modulus_value=modulus_value, mod_value=1, places=1, operator='+')

	def possession(self):
		guest_possession = self.get_team_data(self.guest, 'possession')
		home_possession = self.get_team_data(self.home, 'possession')
		if not guest_possession and not home_possession:
			self.set_team_data(self.guest, 'possession', True, places=1)
		else:
			self.mod_team_data(self.home, 'possession', operator='toggle')
			self.mod_team_data(self.guest, 'possession', operator='toggle')

	def numberPressed(self, key):
		pass

	def Number_7_ABC(self):
		self.numberPressed(7)

	def Number_8_DEF(self):
		self.numberPressed(8)

	def Number_9_GHI(self):
		self.numberPressed(9)

	def Number_4_JKL(self):
		self.numberPressed(4)

	def Number_5_MNO(self):
		self.numberPressed(5)

	def Number_6_PQR(self):
		self.numberPressed(6)

	def Number_1_STU(self):
		self.numberPressed(1)

	def Number_2_VWX(self):
		self.numberPressed(2)

	def Number_3_YZ(self):
		self.numberPressed(3)

	def Number_0(self):
		self.numberPressed(0)

	def clear_(self):
		pass

	def enter_(self):
		pass

	def setGuestScore(self):
		pass

	def setHomeScore(self):
		pass

	def setGuestFunctions(self):
		pass

	def setHomeFunctions(self):
		pass

	def shotClocks(self):
		pass

	def setClock(self):
		pass

	def playClocks(self):
		pass

	def setClockTenthSec(self):
		pass

	def tenthSecOnOff(self):
		pass

	def clockUpDown(self):
		pass

	def autoHorn(self):
		pass

	def timeOfDay(self):
		pass

	def timeOutTimer(self):
		pass

	def NewGame(self):
		pass

	def blank(self):
		pass

	def periodClockReset(self):
		pass

	# END OF GENERIC METHODS-----------
	# BASEBALL METHODS----------------------------------------

	def clear_FlashHit(self):
		if self.gameSettings['menuFlag'] or self.gameSettings['hitIndicatorFlashOn']:
			pass
		else:
			self.gameSettings['hitIndicatorFlashOn'] = True
			self.hitToggle()

	def enter_FlashError(self):
		if self.gameSettings['menuFlag'] or self.gameSettings['errorIndicatorFlashOn']:
			pass
		else:
			self.gameSettings['errorIndicatorFlashOn'] = True
			self.errorToggle()

	def hitToggle(self):
		self.hitCount -= 1
		if self.hitCount <= 0:
			self.gameSettings['hitIndicatorFlashOn'] = False
			self.gameData['hitIndicator'] = False
		else:
			self.mod_game_data('hitIndicator', operator='toggle')
			threading.Timer(self.gameSettings['hitFlashDuration'], self.hitToggle).start()

	def errorToggle(self):
		self.errorCount -= 1
		if self.errorCount <= 0:
			self.gameSettings['errorIndicatorFlashOn'] = False
			self.gameData['errorIndicator'] = False
		else:
			self.mod_game_data('errorIndicator', operator='toggle')
			threading.Timer(self.gameSettings['errorFlashDuration'], self.errorToggle).start()

	def hitsPlusOne(self):
		if self.gameSettings['inningBot']:
			team = self.home
		else:
			team = self.guest
		self.mod_team_data(team, 'hits')
		self.clear_FlashHit()

	def errorsPlusOne(self):
		if self.gameSettings['inningBot']:
			team = self.guest
		else:
			team = self.home
		self.mod_team_data(team, 'errors')
		self.enter_FlashError()

	def setSinglePitchCount(self, team):
		self.set_game_data('singlePitchCount', self.get_team_data(team, 'pitchCount'), places=3)

	def setSinglePitchCountFromMenu(self):
		if self.gameData['sportType'] == 'baseball':
			data_name = 'atBatIndicator'
			guest_at_bat = self.get_team_data(self.guest, data_name)
			home_at_bat = self.get_team_data(self.home, data_name)
			if not guest_at_bat and not home_at_bat:
				team = self.guest
			else:
				if guest_at_bat:
					team = self.home
				if home_at_bat:
					team = self.guest
		elif self.gameData['sportType'] == 'linescore':
			if self.gameSettings['linescoreStart']:
				team = self.guest
			elif self.gameSettings['inningBot']:
				team = self.guest
			else:
				team = self.home
		self.setSinglePitchCount(team)

	def teamAtBat(self):
		data_name = 'atBatIndicator'
		guest_at_bat = self.get_team_data(self.guest, data_name)
		home_at_bat = self.get_team_data(self.home, data_name)
		if not guest_at_bat and not home_at_bat:
			team = self.home
			self.set_team_data(self.guest, data_name, True, places=1)
		else:
			if guest_at_bat:
				team = self.guest
			if home_at_bat:
				team = self.home
			self.mod_team_data(self.home, data_name, operator='toggle')
			self.mod_team_data(self.guest, data_name, operator='toggle')
		self.setSinglePitchCount(team)

	def singlePitchesPlusOne(self):
		if self.gameSettings['inningBot']:
			self.guestPitchesPlusOne()
			team = self.guest
		else:
			self.homePitchesPlusOne()
			team = self.home
		self.setSinglePitchCount(team)

	def guestPitchesPlusOne(self):
		self.mod_team_data(self.guest, 'pitchCount', modulus_value=200, places=3)
		if self.get_team_data(self.home, 'atBatIndicator'):
			self.setSinglePitchCount(self.guest)

	def homePitchesPlusOne(self):
		self.mod_team_data(self.home, 'pitchCount', modulus_value=200, places=3)
		if self.get_team_data(self.guest, 'atBatIndicator'):
			self.setSinglePitchCount(self.home)

	def inningsPlusOne(self):
		self.mod_game_data('inning', modulus_value=20)

	def ballsPlusOne(self):
		self.mod_game_data('balls', modulus_value=self.gameSettings['ballsMax']+1, places=1)

	def strikesPlusOne(self):
		self.mod_game_data('strikes', modulus_value=self.gameSettings['strikesMax']+1, places=1)

	def outsPlusOne(self):
		self.mod_game_data('outs', modulus_value=self.gameSettings['outsMax']+1, places=1)

	def incInningTop_Bot(self):
		inn = self.get_game_data('inning')
		if self.gameSettings['linescoreStart']:
			self.gameSettings['linescoreStart'] = False
			self.gameSettings['inningBot'] = False
			self.gameData['inning'] = 1
			self.setSinglePitchCount(self.home)
		elif self.gameSettings['inningBot']:
			self.gameSettings['inningBot'] = False
			self.inningsPlusOne()
			if inn <= 10 and inn != 0:
				data_name = 'scoreInn'+str(inn)
				if self.get_team_data(self.home, data_name) == 255:
					self.set_team_data(self.home, data_name, value=0, places=1)
			self.setSinglePitchCount(self.home)
		else:
			self.gameSettings['inningBot'] = True
			if inn <= 10 and inn != 0:
				data_name = 'scoreInn'+str(inn)
				if self.get_team_data(self.guest, data_name) == 255:
					self.set_team_data(self.guest, data_name, value=0, places=1)
			self.setSinglePitchCount(self.guest)

	def runsPlusOne(self):
		inn = self.get_game_data('inning')
		if self.gameSettings['linescoreStart']:
			if self.gameSettings['inningBot']:
				team = self.guest
			else:
				team = self.home
			self.mod_team_data(team, 'score')
		else:
			if self.gameSettings['inningBot']:
				team = self.home
				self.mod_team_data(team, 'score')
			else:
				team = self.guest
				self.mod_team_data(team, 'score')
			if inn <= 10 and inn != 0:
				data_name = 'scoreInn'+str(inn)
				if self.get_team_data(team, data_name) == 255:
					self.set_team_data(team, data_name, value=0, places=1)
				self.mod_team_data(team, data_name, modulus_value=10, places=1)

	def assignError(self):
		pass

	def setPitchCounts(self):
		pass

	def setBatterNumber(self):
		pass

	def setTotalRuns(self):
		pass

	def setTotalHits(self):
		pass

	def setTotalErrors(self):
		pass

	def setRuns_Innings(self):
		pass

	def setInningTop_Bot(self):
		pass

	# END OF BASEBALL METHODS-----------
	# FOOTBALL METHODS----------------------------------------

	def guestTimeOutsMinusOne(self):
		pass

	def homeTimeOutsMinusOne(self):
		pass

	def downsPlusOne(self):
		self.mod_game_data('down', modulus_value=5, places=1)

	def yardsToGoMinusTen(self):
		if self.gameData['yardsToGo'] <= 10:
			self.set_game_data('yardsToGo', 0)
		else:
			self.mod_game_data('yardsToGo', operator='-', mod_value=10)

	def yardsToGoMinusOne(self):
		if self.gameData['yardsToGo'] <= 1:
			self.set_game_data('yardsToGo', 0)
		else:
			self.mod_game_data('yardsToGo', operator='-', mod_value=1)

	def yardsToGoReset(self):
		pass

	def setGuestTimeOuts(self):
		pass

	def setHomeTimeOuts(self):
		pass

	def setYardsToGo(self):
		pass

	def setBallOn(self):
		pass

	# END OF FOOTBALL METHODS-----------
	# SOCCER METHODS----------------------------------------

	def clear_GuestGoal(self):
		if self.gameSettings['menuFlag']:
			pass
		else:
			self.mod_team_data(self.guest, 'goalIndicator', operator='toggle')

	def enter_HomeGoal(self):
		if self.gameSettings['menuFlag']:
			pass
		else:
			self.mod_team_data(self.home, 'goalIndicator', operator='toggle')

	def guestPenaltyPlusOne(self):
		self.mod_team_data(self.guest, 'penaltyCount', modulus_value=10, places=1)

	def homePenaltyPlusOne(self):
		self.mod_team_data(self.home, 'penaltyCount', modulus_value=10, places=1)

	def guestShotsPlusOne(self):
		self.mod_team_data(self.guest, 'shots')

	def homeShotsPlusOne(self):
		self.mod_team_data(self.home, 'shots')

	def guestKicksPlusOne(self):
		self.mod_team_data(self.guest, 'kicks')

	def homeKicksPlusOne(self):
		self.mod_team_data(self.home, 'kicks')

	def guestSavesPlusOne(self):
		self.mod_team_data(self.guest, 'saves')

	def homeSavesPlusOne(self):
		self.mod_team_data(self.home, 'saves')

	# END OF SOCCER METHODS-----------
	# HOCKEY METHODS----------------------------------------

	def guestPenalty(self):
		pass

	def homePenalty(self):
		pass

	# END OF HOCKEY METHODS-----------
	# BASKETBALL METHODS----------------------------------------

	def guestTeamFoulsPlusOne(self):
		self.mod_team_data(self.guest, 'fouls', modulus_value=self.gameSettings['FoulsMax']+1, operator='+', places=2)
		return

	def homeTeamFoulsPlusOne(self):
		self.mod_team_data(self.home, 'fouls', modulus_value=self.gameSettings['FoulsMax']+1, operator='+', places=2)
		return

	def guestBonusPlusOne(self):
		self.mod_team_data(self.guest, 'bonus', modulus_value=3, operator='+', places=1)
		return

	def homeBonusPlusOne(self):
		self.mod_team_data(self.home, 'bonus', modulus_value=3, operator='+', places=1)
		return

	def playerMatchGame(self):
		return

	def playerFoul(self):
		return

	# END OF BASKETBALL METHODS-----------
	# CRICKET METHODS----------------------------------------

	def oversPlusOne(self):
		self.gameData['overs'] = (self.gameData['overs'] + 1) % 100

	def player1ScorePlusOne(self):
		self.gameData['player1Score'] = (self.gameData['player1Score'] + 1) % 200

	def player2ScorePlusOne(self):
		self.gameData['player2Score'] = (self.gameData['player2Score'] + 1) % 200

	def wicketsPlusOne(self):
		self.gameData['wickets'] = (self.gameData['wickets'] + 1) % 10

	def setPlayer1Number(self):
		pass

	def setPlayer2Number(self):
		pass

	def setPlayer1Score(self):
		pass

	def setPlayer2Score(self):
		pass

	def setTotalScore(self):
		pass

	def setOvers(self):
		pass

	def setLastMan(self):
		pass

	def setLastWicket(self):
		pass

	def set1eInnings(self):
		pass

	# END OF CRICKET METHODS-----------
	# RACETRACK METHODS----------------------------------------

	# END OF RACETRACK METHODS-----------
	# STAT METHODS----------------------------------------

	def fouls_digsMinusOne(self):
		active_player_list, team, team_name = app.utils.functions.active_player_list_select(self)  # Only team needed
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber'] != '  ':
			player_id = self.get_player_data(team, 'playerNumber', player_number=self.gameSettings['playerNumber'])
			self.mod_player_data(team, player_id, 'fouls', operator='-')
			self.mod_team_data(team, 'fouls', modulus_value=self.gameSettings['FoulsMax']+1, operator='-', places=2)

	def fouls_digsPlusOne(self):
		active_player_list, team, team_name = app.utils.functions.active_player_list_select(self)  # Only team needed
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber'] != '  ':
			player_id = self.get_player_data(team, 'playerNumber', player_number=self.gameSettings['playerNumber'])
			self.mod_player_data(team, player_id, 'fouls', operator='+')
			self.mod_team_data(team, 'fouls', modulus_value=self.gameSettings['FoulsMax']+1, operator='+', places=2)

	def guest_homeSwitch(self):
		self.gameSettings['currentTeamGuest'] = not self.gameSettings['currentTeamGuest']
		if self.gameSettings['currentTeamGuest']:
			active_player_list = self.activeGuestPlayerList
		else:
			active_player_list = self.activeHomePlayerList
		if len(active_player_list) == 0:
			stat_index = 0
		else:
			stat_index = 1
		self.gameSettings['statNumber'] = self.statNumberList[stat_index]

	def points_killsMinusOne(self):
		active_player_list, team, team_name = app.utils.functions.active_player_list_select(self)  # Only team needed
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber'] != '  ':
			player_id = self.get_player_data(team, 'playerNumber', player_number=self.gameSettings['playerNumber'])
			self.mod_player_data(team, player_id, 'points', operator='-')
			self.mod_team_data(team, 'score', modulus_value=200, operator='-', places=3)

	def points_killsPlusOne(self):
		active_player_list, team, team_name = app.utils.functions.active_player_list_select(self)  # Only team needed
		if self.gameSettings['statNumber'] is not None or self.gameSettings['playerNumber'] != '  ':
			player_id = self.get_player_data(team, 'playerNumber', player_number=self.gameSettings['playerNumber'])
			self.mod_player_data(team, player_id, 'points', operator='+')
			self.mod_team_data(team, 'score', modulus_value=200, operator='+', places=3)

	def nextPlayer(self):
		active_player_list, team, team_name = app.utils.functions.active_player_list_select(self)
		not_active_list = []
		for playerID in list(self.teamsDict[team].playersDict.keys()):
			player_number = self.get_player_data(team, 'playerNumber', player_id=playerID)
			player_active = self.get_player_data(team, 'playerActive', player_id=playerID)
			if player_number != '  ' and not player_active:
				not_active_list.append(player_number)
		not_active_list.sort()
		active_index = self.statNumberList.index(self.gameSettings['statNumber'])

		# Enter index governed list choosing area
		if active_index and self.notActiveIndex is not None:
			if active_index >= len(active_player_list):
				self.notActiveIndex = 0
				self.gameSettings['statNumber'] = self.statNumberList[0]
				self.gameSettings['playerNumber'] = not_active_list[self.notActiveIndex]
			else:
				self.gameSettings['statNumber'] = self.statNumberList[active_index+1]
				self.gameSettings['playerNumber'] = active_player_list[active_index]
		elif active_index:
			if active_index >= len(active_player_list):
				self.gameSettings['statNumber'] = self.statNumberList[1]
				self.gameSettings['playerNumber'] = active_player_list[0]
			else:
				self.gameSettings['statNumber'] = self.statNumberList[active_index+1]
				self.gameSettings['playerNumber'] = active_player_list[active_index]
		elif self.notActiveIndex is not None:
			if self.notActiveIndex+1 >= len(not_active_list):
				self.notActiveIndex = 0
				if len(active_player_list):
					return_to_active = 1
					self.gameSettings['playerNumber'] = active_player_list[active_index]
				else:
					return_to_active = 0
					self.gameSettings['playerNumber'] = not_active_list[self.notActiveIndex]
				self.gameSettings['statNumber'] = self.statNumberList[return_to_active]
			else:
				self.notActiveIndex += 1
				self.gameSettings['statNumber'] = self.statNumberList[0]
				self.gameSettings['playerNumber'] = not_active_list[self.notActiveIndex]
		else:
			print('No players in roster')

	def previousPlayer(self):
		active_player_list, team, team_name = app.utils.functions.active_player_list_select(self)
		index = self.statNumberList.index(self.gameSettings['statNumber'])
		if len(active_player_list):
			if index == 1:
				self.gameSettings['statNumber'] = self.statNumberList[len(active_player_list)]
				self.gameSettings['playerNumber'] = active_player_list[len(active_player_list)-1]
			else:
				self.gameSettings['statNumber'] = self.statNumberList[index-1]
				self.gameSettings['playerNumber'] = active_player_list[index-2]

	def subPlayer(self):
		pass

	def addPlayer(self):
		pass

	def deletePlayer(self):
		pass

	def displaySize(self):
		pass

	def editPlayer(self):
		pass

	# END OF STAT METHODS-----------


class Baseball(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Baseball, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = "baseball"
		if self.gameSettings['hoursFlagJumper']:
			self.gameSettings['hoursFlag'] = True
		if (
				self.gameData['sport'] == 'MPLINESCORE4' or self.gameData['sport'] == 'MPLINESCORE5'
				or self.gameData['sport'] == 'MPMP-15X1' or self.gameData['sport'] == 'MPMP-14X1'):
			self.gameData['sportType'] = 'linescore'
			self.gameSettings['hoursFlag'] = True

		if self.gameData['sport'][0:2] == 'MM':
			self.gameSettings['baseballPeriodClockMaxSeconds'] = self.gameSettings['MM_baseballPeriodClockMaxSeconds']
		else:
			self.gameSettings['baseballPeriodClockMaxSeconds'] = self.gameSettings['MP_baseballPeriodClockMaxSeconds']

		self.set_game_data('singlePitchCount', self.get_team_data(self.home, 'pitchCount'), places=3)
		self.set_game_data('inning', self.get_game_data('inning'))

		if self.gameData['outs'] >= 2:
			self.gameData['outs1'] = True
			self.gameData['outs2'] = True
		elif self.gameData['outs'] == 1:
			self.gameData['outs1'] = True
			self.gameData['outs2'] = False
		else:
			self.gameData['outs1'] = False
			self.gameData['outs2'] = False

		self.set_game_data('pitchSpeed', self.get_game_data('pitchSpeed'), places=3)
		self.set_game_data('batterNumber', self.get_game_data('batterNumber'))

		self.gameSettings['errorIndicatorFlashOn'] = False
		self.gameSettings['hitIndicatorFlashOn'] = False

		self._create_teams()

		self._add_team_name_data()

		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['shotClock'] = app.game.clock.Clock(
			False, self.gameSettings['shotClockMaxSeconds1'], clock_name='shotClock')
		
		self.clockDict['delayOfGameClock'] = app.game.clock.Clock(
			False, self.gameSettings['delayOfGameMaxSeconds1'], clock_name='delayOfGameClock')
		
		self.clockDict['periodClock'] = app.game.clock.Clock(
			self.gameSettings['periodClockCountUp'], self.gameSettings['baseballPeriodClockMaxSeconds'],
			self.gameSettings['periodClockResolution'], self.gameSettings['hoursFlag'], clock_name='periodClock')
		
		self.gameData = self.clockDict['shotClock'].game_data_update(self.gameData, 'shotClock')
		self.gameData = self.clockDict['delayOfGameClock'].game_data_update(self.gameData, 'delayOfGameClock')
		self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData)

	def periodClockReset(self):
		if not self.gameSettings['menuFlag']:
			if not self.clockDict['periodClock'].running:
				self.gameSettings['periodClockResetFlag'] = True
				period_max = self.gameSettings['baseballPeriodClockMaxSeconds']
				if self.clockDict['periodClock'].currentTime >= (90*60):
					self.clockDict['periodClock'].reset_(period_max)
				elif self.clockDict['periodClock'].currentTime >= (60*60):
					self.clockDict['periodClock'].reset_(90 * 60)
				elif self.clockDict['periodClock'].currentTime >= (30*60):
					self.clockDict['periodClock'].reset_(60 * 60)
				elif self.clockDict['periodClock'].currentTime >= (15*60):
					self.clockDict['periodClock'].reset_(30 * 60)
				elif self.clockDict['periodClock'].currentTime >= period_max:
					self.clockDict['periodClock'].reset_(15 * 60)
				elif self.clockDict['periodClock'].currentTime < period_max:
					self.clockDict['periodClock'].reset_(period_max)


class Football(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Football, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = 'football'

		if self.gameData['sport'][0:2] == 'MM':
			self.gameSettings['footballPeriodClockMaxSeconds'] = self.gameSettings['MM_footballPeriodClockMaxSeconds']
		else:
			self.gameSettings['footballPeriodClockMaxSeconds'] = self.gameSettings['MP_footballPeriodClockMaxSeconds']

		if self.gameData['quarter'] == 4:
			self.gameData['quarter4'] = True
		else:
			self.gameData['quarter4'] = False

		self.set_game_data('yardsToGo', self.gameData['yardsToGo'])
		self.set_game_data('ballOn', self.gameData['ballOn'])

		self._create_teams()

		self._add_team_name_data()
		
		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['delayOfGameClock'] = app.game.clock.Clock(
			False, self.gameSettings['delayOfGameMaxSeconds1'], clock_name='delayOfGameClock')
		
		self.clockDict['periodClock'] = app.game.clock.Clock(
			self.gameSettings['periodClockCountUp'], self.gameSettings['footballPeriodClockMaxSeconds'],
			self.gameSettings['periodClockResolution'], clock_name='periodClock')
		
		self.gameData = self.clockDict['delayOfGameClock'].game_data_update(self.gameData, name='delayOfGameClock')
		self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData, name='periodClock')

	def periodClockReset(self):
		if not self.gameSettings['menuFlag']:
			if not self.clockDict['periodClock'].running:
				self.gameSettings['periodClockResetFlag'] = True
				period_max = self.gameSettings['footballPeriodClockMaxSeconds']
				if self.clockDict['periodClock'].currentTime >= (90*60):
					self.clockDict['periodClock'].reset_(period_max)
				elif self.clockDict['periodClock'].currentTime >= (60*60):
					self.clockDict['periodClock'].reset_(90 * 60)
				elif self.clockDict['periodClock'].currentTime >= (30*60):
					self.clockDict['periodClock'].reset_(60 * 60)
				elif self.clockDict['periodClock'].currentTime >= (15*60):
					self.clockDict['periodClock'].reset_(30 * 60)
				elif self.clockDict['periodClock'].currentTime >= period_max:
					self.clockDict['periodClock'].reset_(15 * 60)
				elif self.clockDict['periodClock'].currentTime < period_max:
					self.clockDict['periodClock'].reset_(period_max)

	def guestTimeOutsMinusOne(self):
		self.mod_team_data(self.guest, 'timeOutsLeft', modulus_value=self.gameSettings['TOLMaxFB']+1, operator='-', places=1)

	def homeTimeOutsMinusOne(self):
		self.mod_team_data(self.home, 'timeOutsLeft', modulus_value=self.gameSettings['TOLMaxFB']+1, operator='-', places=1)


class Soccer(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Soccer, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = 'soccer'

		self._create_teams()

		self._add_team_name_data()
		
		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['delayOfGameClock'] = app.game.clock.Clock(
			False, self.gameSettings['delayOfGameMaxSeconds1'], clock_name='periodClock')

		self.clockDict['periodClock'] = app.game.clock.Clock(
			self.gameSettings['periodClockCountUp'], self.gameSettings['MP_soccerPeriodClockMaxSeconds'],
			self.gameSettings['periodClockResolution'], clock_name='periodClock')

		self.gameData = self.clockDict['delayOfGameClock'].game_data_update(self.gameData, 'delayOfGameClock')
		self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData, 'periodClock')


class Hockey(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Hockey, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = 'hockey'

		self._create_teams()

		self._add_team_name_data()

		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['penalty1_teamOne'] = app.game.clock.Clock(False, 0, clock_name='penalty1_teamOne')
		self.clockDict['penalty1_teamTwo'] = app.game.clock.Clock(False, 0, clock_name='penalty1_teamTwo')
		self.clockDict['penalty2_teamOne'] = app.game.clock.Clock(False, 0, clock_name='penalty2_teamOne')
		self.clockDict['penalty2_teamTwo'] = app.game.clock.Clock(False, 0, clock_name='penalty2_teamTwo')
		self.clockDict['penalty3_teamOne'] = app.game.clock.Clock(False, 0, clock_name='penalty3_teamOne')
		self.clockDict['penalty3_teamTwo'] = app.game.clock.Clock(False, 0, clock_name='penalty3_teamTwo')
		self.clockDict['penalty4_teamOne'] = app.game.clock.Clock(False, 0, clock_name='penalty4_teamOne')
		self.clockDict['penalty4_teamTwo'] = app.game.clock.Clock(False, 0, clock_name='penalty4_teamTwo')
		self.clockDict['shotClock'] = app.game.clock.Clock(
			False, self.gameSettings['shotClockMaxSeconds1'], clock_name='shotClock')

		self.clockDict['periodClock'] = app.game.clock.Clock(
			self.gameSettings['periodClockCountUp'], self.gameSettings['MP_hockeyPeriodClockMaxSeconds'],
			self.gameSettings['periodClockResolution'], clock_name='periodClock')

		self.gameData = self.clockDict['penalty1_teamOne'].game_data_update(self.gameData, 'penalty1_teamOne')
		self.gameData = self.clockDict['penalty1_teamTwo'].game_data_update(self.gameData, 'penalty1_teamTwo')
		self.gameData = self.clockDict['penalty2_teamOne'].game_data_update(self.gameData, 'penalty2_teamOne')
		self.gameData = self.clockDict['penalty2_teamTwo'].game_data_update(self.gameData, 'penalty2_teamTwo')
		self.gameData = self.clockDict['penalty3_teamOne'].game_data_update(self.gameData, 'penalty3_teamOne')
		self.gameData = self.clockDict['penalty3_teamTwo'].game_data_update(self.gameData, 'penalty3_teamTwo')
		self.gameData = self.clockDict['penalty4_teamOne'].game_data_update(self.gameData, 'penalty4_teamOne')
		self.gameData = self.clockDict['penalty4_teamTwo'].game_data_update(self.gameData, 'penalty4_teamTwo')
		self.gameData = self.clockDict['shotClock'].game_data_update(self.gameData, 'shotClock')
		self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData, 'periodClock')

	def handheldButton1(self):
		self.clockDict['shotClock'].reset_(self.gameSettings['shotClockMaxSeconds1'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable'] = True

	def handheldButton2(self):
		self.clockDict['shotClock'].reset_(self.gameSettings['shotClockMaxSeconds2'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable'] = True

	def handheldButton3(self):
		if self.gameSettings['shotClockBlankEnable']:
			self.gameSettings['shotClockBlankEnable'] = False
		else:
			self.gameSettings['shotClockBlankEnable'] = True
		if self.clockDict['shotClock'].currentTime:
			self.gameSettings['shotClockHornEnable'] = False
			self.clockDict['shotClock'].reset_(0)


class Basketball(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Basketball, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = 'basketball'

		self._create_teams()

		self._add_team_name_data()

		if self.gameData['sport'][0:2] == 'MM':
			self.basketballPeriodClockMaxSeconds = (self.gameSettings['MM_basketballPeriodClockMaxSeconds'])
		else:
			self.basketballPeriodClockMaxSeconds = (self.gameSettings['MP_basketballPeriodClockMaxSeconds'])

		self.gameSettings['periodClockTenthsFlag'] = True

		self.set_game_data('playerNumber', self.gameData['playerNumber'])
		self.set_game_data('playerFouls', self.gameData['playerFouls'])
		
		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['shotClock'] = app.game.clock.Clock(
			False, self.gameSettings['shotClockMaxSeconds1'], clock_name='shotClock')

		self.clockDict['periodClock'] = app.game.clock.Clock(
			self.gameSettings['periodClockCountUp'], self.basketballPeriodClockMaxSeconds,
			self.gameSettings['periodClockResolution'], clock_name='periodClock')

		self.gameData = self.clockDict['shotClock'].game_data_update(self.gameData, 'shotClock')
		self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData, 'periodClock')

	def handheldButton1(self):
		self.clockDict['shotClock'].reset_(self.gameSettings['shotClockMaxSeconds1'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable'] = True

	def handheldButton2(self):
		self.clockDict['shotClock'].reset_(self.gameSettings['shotClockMaxSeconds2'])
		self.gameSettings['shotClockBlankEnable'] = False
		self.gameSettings['shotClockHornEnable'] = True

	def handheldButton3(self):
		if self.gameSettings['shotClockBlankEnable']:
			self.gameSettings['shotClockBlankEnable'] = False
		else:
			self.gameSettings['shotClockBlankEnable'] = True
		if self.clockDict['shotClock'].currentTime:
			self.gameSettings['shotClockHornEnable'] = False
			self.clockDict['shotClock'].reset_(0)

	def periodClockReset(self):
		if not self.gameSettings['menuFlag']:
			if not self.clockDict['periodClock'].running:
				self.gameSettings['periodClockResetFlag'] = True
				period_max = self.basketballPeriodClockMaxSeconds
				if self.clockDict['periodClock'].currentTime >= (90*60):
					self.clockDict['periodClock'].reset_(period_max)
				elif self.clockDict['periodClock'].currentTime >= (60*60):
					self.clockDict['periodClock'].reset_(90 * 60)
				elif self.clockDict['periodClock'].currentTime >= (30*60):
					self.clockDict['periodClock'].reset_(60 * 60)
				elif self.clockDict['periodClock'].currentTime >= (15*60):
					self.clockDict['periodClock'].reset_(30 * 60)
				elif self.clockDict['periodClock'].currentTime >= period_max:
					self.clockDict['periodClock'].reset_(15 * 60)
				elif self.clockDict['periodClock'].currentTime < period_max:
					self.clockDict['periodClock'].reset_(period_max)

	def guestTimeOutsMinusOne(self):
		self.mod_team_data(self.guest, 'timeOutsLeft', modulus_value=self.gameSettings['TOLMaxBB']+1, operator='-', places=1)
		return

	def homeTimeOutsMinusOne(self):
		self.mod_team_data(self.home, 'timeOutsLeft', modulus_value=self.gameSettings['TOLMaxBB']+1, operator='-', places=1)
		return


class Cricket(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Cricket, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = 'cricket'

		self.gameSettings['MP_cricketPeriodClockMaxSeconds'] = self.gameSettings['MP_cricketPeriodClockMaxSeconds']

		self._create_teams()

		self._add_team_name_data()

		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['periodClock'] = app.game.clock.Clock(
			self.gameSettings['periodClockCountUp'], self.gameSettings['MP_cricketPeriodClockMaxSeconds'],
			self.gameSettings['periodClockResolution'], clock_name='periodClock')

		self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData)


class Racetrack(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Racetrack, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = 'racetrack'

		self.MP_racetrackPeriodClockMaxSeconds = (self.gameSettings['MP_racetrackPeriodClockMaxSeconds'])

		self._create_teams()

		self._add_team_name_data()

		# Order of thread creation sets priority when init same class, last is highest
		self.clockDict['periodClock'] = app.game.clock.Clock(
			self.gameSettings['periodClockCountUp'], self.gameSettings['MP_racetrackPeriodClockMaxSeconds'],
			self.gameSettings['periodClockResolution'], clock_name='periodClock')

		self.gameData = self.clockDict['periodClock'].game_data_update(self.gameData)


class Stat(Game):
	def __init__(self, config_dict, number_of_teams=2):
		super(Stat, self).__init__(config_dict, number_of_teams=number_of_teams)

		self.gameData['sportType'] = 'stat'

		self._create_teams()

		self._add_team_name_data()

		self.gameSettings['currentTeamGuest'] = True
		if self.gameSettings['vollyballFlag']:
			self.maxActive = 6
		else:
			self.maxActive = 5

		self.statNumberList = [None, 'One', 'Two', 'Three', 'Four', 'Five', 'Six']
		self.gameSettings['statNumber'] = self.statNumberList[0]
		self.gameSettings['playerNumber'] = '  '
		self.notActiveIndex = None
		self.activeGuestPlayerList = []
		self.activeHomePlayerList = []
