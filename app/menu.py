#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module simulates a menu with LED only feedback.
	It is a complicated state machine.

	:Created Date: 6/18/2018
	:Author: **Craig Gunter**

"""

import app.utils.functions


class MenuEventHandler(object):
	"""Object that displays information and responds to current events based on past input."""
	def __init__(self, game):
		self.verbose = False

		app.utils.functions.verbose(['\nCreating MenuEventHandler object'], self.verbose)
		self.game = game

		self.enterFlag = False
		self.clearFlag = False
		self.menuFlag = False
		self.startFlag = False
		self.currentMenuString = ''
		self.funcString = ''
		self.teamNameString = ''
		self.teamNameNumpadFlag = False
		self.teamNameNumpadTimerFlag = False
		self.teamNameNumpadFlagCount = 0

		self.currentData = None

		self.menuTimerFlag = False
		self.NewGameMenu = 1

		self.menuNumber = 1
		self.startingMenuNumber = 1
		self.endingMenuNumber = 1

		self.numberPressedSequence = []
		self.numpadSequence = None
		self.lastNumberPressed = None

		self.precisionMenuFlag = False
		self.dimmingMenuFlag = False
		self.teamNameMenuFlag = False
		self.segmentTimerMenuFlag = False

		self.numberPressedFlag = False
		self.blockNumList = None

		self.funcDict = None

		self._build_func_dict()

	# Init methods

	def _build_func_dict(self):
		"""Build dictionary of game function keys matched to menu class functions."""
		# All games
		self.funcDict = {
			'NewGame': self.NewGame, 'setClock': self.setClock, 'setClockTenthSec': self.setClockTenthSec,
			'autoHorn': self.autoHorn, 'timeOfDay': self.timeOfDay, 'timeOutTimer': self.timeOutTimer,
			'setHomeScore': self.setHomeScore, 'setGuestScore': self.setGuestScore, 'clockUpDown': self.clockUpDown,
			'playClocks': self.playClocks, 'shotClocks': self.shotClocks, 'tenthSecOnOff': self.tenthSecOnOff,
			'periodClockReset': self.periodClockReset, 'guestScorePlusOne': self.guestScorePlusOne,
			'homeScorePlusOne': self.homeScorePlusOne, 'teamNameMenu': self.teamNameMenu,
			'segmentTimerMenu': self.segmentTimerMenu, 'mode': self.mode,
			'handheldButton1': self.do_nothing, 'handheldButton2': self.do_nothing, 'handheldButton3': self.do_nothing}

		# Number pad
		self.funcDict.update({
			'Number_7_ABC': self.Number_7_ABC, 'Number_8_DEF': self.Number_8_DEF, 'Number_9_GHI': self.Number_9_GHI,
			'Number_5_MNO': self.Number_5_MNO, 'Number_6_PQR': self.Number_6_PQR, 'Number_1_STU': self.Number_1_STU,
			'Number_2_VWX': self.Number_2_VWX, 'Number_3_YZ': self.Number_3_YZ, 'Number_4_JKL': self.Number_4_JKL,
			'Number_0_&-.!': self.Number_0, 'clear': self.clear_, 'enter': self.enter_,
			'clear_FlashHit': self.clear_, 'enter_FlashError': self.enter_})

		# All games - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'guestScorePlusTen': self.do_nothing, 'homeScorePlusTen': self.do_nothing,
			'secondsMinusOne': self.do_nothing, 'possession': self.do_nothing, 'horn': self.do_nothing,
			'minutesMinusOne': self.do_nothing, 'periodClockOnOff': self.do_nothing,
			'secondsPlusOne': self.do_nothing, 'blank': self.do_nothing, 'None': self.do_nothing, '': self.do_nothing})

		# hockey
		self.funcDict.update({
			'clear_GuestGoal': self.clear_, 'enter_HomeGoal': self.enter_, 'play_shotClocks': self.play_shotClocks,
			'setGuestFunctions': self.setGuestFunctions, 'setHomeFunctions': self.setHomeFunctions,
			'guestPenalty': self.guestPenalty, 'homePenalty': self.homePenalty})

		# hockey - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'guestShotsPlusOne': self.do_nothing, 'homeShotsPlusOne': self.do_nothing, 'qtrs_periodsPlusOne': self.do_nothing,
			'guestPenaltyPlusOne': self.do_nothing, 'homePenaltyPlusOne': self.do_nothing,
			'guestKicksPlusOne': self.do_nothing, 'homeKicksPlusOne': self.do_nothing,
			'guestSavesPlusOne': self.do_nothing, 'homeSavesPlusOne': self.do_nothing})

		# soccer
		self.funcDict.update({
			'setGuestFunctions': self.setGuestFunctions, 'setHomeFunctions': self.setHomeFunctions,
			'play_shotClocks': self.play_shotClocks, 'clear_GuestGoal': self.clear_, 'enter_HomeGoal': self.enter_})

		# soccer - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'guestKicksPlusOne': self.do_nothing, 'homeKicksPlusOne': self.do_nothing,
			'guestSavesPlusOne': self.do_nothing, 'homeSavesPlusOne': self.do_nothing, 'qtrs_periodsPlusOne': self.do_nothing,
			'guestShotsPlusOne': self.do_nothing, 'homeShotsPlusOne': self.do_nothing,
			'guestPenaltyPlusOne': self.do_nothing, 'homePenaltyPlusOne': self.do_nothing})

		# basketball
		self.funcDict.update({
			'playerMatchGame': self.playerMatchGame, 'playerFoul': self.playerFoul,
			'setHomeTimeOuts': self.setHomeTimeOuts, 'setGuestTimeOuts': self.setGuestTimeOuts})

		# basketball - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'guestTeamFoulsPlusOne': self.do_nothing, 'homeTeamFoulsPlusOne': self.do_nothing,
			'homeBonus': self.do_nothing, 'guestBonus': self.do_nothing, 'qtrs_periodsPlusOne': self.do_nothing})

		# football
		self.funcDict.update({
			'yardsToGoReset': self.yardsToGoReset, 'setYardsToGo': self.setYardsToGo, 'setBallOn': self.setBallOn})

		# football - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'yardsToGoMinusOne': self.do_nothing, 'yardsToGoMinusTen': self.do_nothing,
			'guestTimeOutsMinusOne': self.do_nothing, 'homeTimeOutsMinusOne': self.do_nothing, 'downsPlusOne': self.do_nothing,
			'qtrs_periodsPlusOne': self.do_nothing, 'quartersPlusOne': self.do_nothing})

		# baseball
		self.funcDict.update({
			'setPitchCounts': self.setPitchCounts, 'setBatterNumber': self.setBatterNumber, 'clear_FlashHit': self.clear_,
			'enter_FlashError': self.enter_, 'assignError': self.assignError, 'setTotalRuns': self.setTotalRuns,
			'setTotalHits': self.setTotalHits, 'setTotalErrors': self.setTotalErrors,
			'setRuns_Innings': self.setRuns_Innings, 'setInningTop_Bot': self.setInningTop_Bot})

		# baseball - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'ballsPlusOne': self.do_nothing, 'homePitchesPlusOne': self.do_nothing, 'singlePitchesPlusOne': self.do_nothing,
			'strikesPlusOne': self.do_nothing, 'outsPlusOne': self.do_nothing, 'inningsPlusOne': self.do_nothing,
			'teamAtBat': self.do_nothing, 'guestPitchesPlusOne': self.do_nothing, 'incInningTop_Bot': self.do_nothing,
			'runsPlusOne': self.do_nothing, 'hitsPlusOne': self.do_nothing,	'flashHitIndicator': self.do_nothing,
			'flashErrorIndicator': self.do_nothing, 'errorsPlusOne': self.do_nothing})

		# stat
		self.funcDict.update({
			'addPlayer': self.addPlayer, 'deletePlayer': self.deletePlayer, 'displaySize': self.displaySize,
			'editPlayer': self.editPlayer, 'nextPlayer': self.nextPlayer, 'subPlayer': self.subPlayer,
			'previousPlayer': self.previousPlayer})

		# stat - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'fouls_digsMinusOne': self.do_nothing, 'fouls_digsPlusOne': self.do_nothing,
			'points_killsMinusOne': self.do_nothing, 'points_killsPlusOne': self.do_nothing})

		# cricket
		self.funcDict.update({
			'setPlayer1Number': self.setPlayer1Number, 'setPlayer2Number': self.setPlayer2Number,
			'setPlayer1Score': self.setPlayer1Score, 'setPlayer2Score': self.setPlayer2Score,
			'setTotalScore': self.setTotalScore, 'setOvers': self.setOvers, 'setLastMan': self.setLastMan,
			'setLastWicket': self.setLastWicket, 'set1eInnings': self.set1eInnings})

		# cricket - do nothing--------------------------------------------------------------
		self.funcDict.update({
			'oversPlusOne': self.do_nothing, 'player1ScorePlusOne': self.do_nothing,
			'player2ScorePlusOne': self.do_nothing, 'wicketsPlusOne': self.do_nothing})

	# Externally callable methods

	def map_(self, func_string='None'):
		"""Main function called when there is a key press event to update the LCD screen."""
		app.utils.functions.verbose(['\nMap---'], self.verbose)
		self.funcString = func_string

		# Call the function - This is the area to control if this func_string has a menu or only uses it in certain cases
		self.call_function()

		# Main function for controlling menus
		self._update_menu()

		# refresh_leds updates the current LED state
		self.refresh_leds()

	# Generic Methods

	def refresh_leds(self):
		pass

	def call_function(self):
		"""Calls the current menu function corresponding to the key pressed.
		This is the area to control if this **funcString** has a menu or only uses it in certain cases"""
		app.utils.functions.verbose(['\nCalling the Menu function -', self.funcString], self.verbose)
		if self.funcString in self.funcDict:
			self.funcDict[self.funcString]()
		else:
			app.utils.functions.verbose(['\nNot in menu.funcDict!!!!'])

	def _mod_menu_num(self, operator='+', value=1):
		"""Modifies the current menu number."""
		app.utils.functions.verbose(['\n_mod_menu_num - self.menuNumber:', self.menuNumber], self.verbose)
		if operator == '+':
			self.menuNumber += value
		elif operator == '-':
			self.menuNumber -= value
		app.utils.functions.verbose(['self.menuNumber:', self.menuNumber], self.verbose)

	def _block_number(self):
		"""Bypasses a keypress from the number pad if it is in the blocked number list."""
		if self.numberPressedFlag:
			app.utils.functions.verbose(['\nBlocked Key Check'], self.verbose)
			if self.blockNumList is not None:
				for block in self.blockNumList:
					if self.lastNumberPressed == block:
						app.utils.functions.verbose(['\nBlocked Key', block], self.verbose)
						return 1
		return 0

	def _clear_num_seq(self):
		"""Clear the stored list of keys pressed."""
		self.numberPressedFlag = False
		self.numberPressedSequence = []

	def _exit_menu(self):
		"""Fully resets all variables to the default state when a menu is exited."""
		app.utils.functions.verbose(['\n_exit_menu!!!!!'], self.verbose)
		self.menuNumber = 1
		self.startingMenuNumber = 1
		self.endingMenuNumber = 1
		self.enterFlag = False
		self.clearFlag = False
		self.menuFlag = False
		self.game.gameSettings['menuFlag'] = False

		self.precisionMenuFlag = False
		self.dimmingMenuFlag = False
		self.teamNameMenuFlag = False
		self.segmentTimerMenuFlag = False
		self.setPlayerActive = False
		self.game.gameSettings['lampTestFlag'] = False
		self.game.gameSettings['blankTestFlag'] = False
		self.menuTimerFlag = False

		self.numberPressedFlag = False
		self.lastNumberPressed = None
		self.numberPressedSequence = []
		self.numpadSequence = 0
		self.currentData = None
		self.NewGameMenu = 1

		self.currentMenuString = ''
		self.funcString = ''
		self.teamNameString = ''
		self.teamNameNumpadFlag = False
		self.teamNameNumpadTimerFlag = False
		self.teamNameNumpadFlagCount = 0

	# Main branch function

	def _update_menu(self):
		"""Main update function which branches to a sub-function based on key pressed and previous state.

		**Sub-functions**

		* Start function = First call to this menu from the default screen.

		* Self function = Same key pressed as the current menu.

		* Exit function = Key pressed has a special menu close function.

		* Clear function = Clear key is pressed.

		* Enter function = Enter key is pressed.

		* Number pad function = Keys 0 through 9 is pressed.

		* Do nothing function = Key press did not trigger any other sub-functions.
		"""
		app.utils.functions.verbose(
			['\n_update_menu---', 'self.currentMenuString', self.currentMenuString, 'self.menuNumber', self.menuNumber],
			self.verbose)
		
		if self.menuFlag:
			if self.startFlag:
				self.startFlag = False
				self._start_func()
			else:
				if self.funcString == self.currentMenuString:
					self._self_func()
				elif self.clearFlag:
					self.clearFlag = False
					self._clear_func()
				elif self.enterFlag:
					self.enterFlag = False
					self._enter_func()
				elif self.numberPressedFlag:
					self._num_pad_func()
				else:
					self.do_nothing()

	def _start_func(self):
		"""Prepare and display first menu in menu chain, set **menuFlag**, and start menu timer."""
		app.utils.functions.verbose(['\n_start_func---'], self.verbose)
		self.game.gameSettings['menuFlag'] = True
		self.currentMenuString = self.funcString

		# Do stuff

		self.menuTimerFlag = True

	def _self_func(self):
		"""This method controls behavior for the case when the same key as the current active menu is pressed."""
		app.utils.functions.verbose(['\n_self_func---'], self.verbose)

		# Do stuff

		self._clear_num_seq()

	def _num_pad_func(self):
		"""This method controls behavior for the case when key numbers 0 through 9 are pressed."""
		app.utils.functions.verbose(['\n_num_pad_func---'], self.verbose)

		if self._block_number():
			pass  # Quit if number is in block list
		else:
			pass  # Do stuff

	def _clear_func(self):
		"""This method controls behavior for the case when the clear key is pressed."""
		app.utils.functions.verbose(['\n_clear_func---'], self.verbose)
		self._clear_num_seq()

		# Do stuff

		self._mod_menu_num(operator='-')

		# Move back a menu or exit menu

	def _enter_func(self):
		"""This method controls behavior for the case when the enter key is pressed."""
		app.utils.functions.verbose(['\n_enter_func---'], self.verbose)

		if self.numberPressedFlag:
			pass  # Handle

		# Go to next menu
		self._mod_menu_num()
		self._clear_num_seq()

		# Move forward a menu or exit menu

	# Special menu methods for _update_menu's children

	# Button Press Functions----------------------------------------

	def _menu_on(self):
		if not self.menuFlag:
			self.startFlag = True
		self.menuFlag = True
		app.utils.functions.verbose(['\n_menu_on - self.menuFlag:', self.menuFlag, 'self.startFlag:', self.startFlag], self.verbose)

	def _menu_off(self):  # not currently used
		self.menuFlag = False

	def do_nothing(self):
		"""Duh!"""
		app.utils.functions.verbose(
			['\nDoing Nothing...', 'funcString', self.funcString, 'currentMenuString', self.currentMenuString], self.verbose)

	def Numbers(self, key):
		"""Common method for any number key press."""
		app.utils.functions.verbose(['\nNumbers - key:', key], self.verbose)
		if self.menuFlag:
			self.numberPressedFlag = True
			self.lastNumberPressed = key
			self.numberPressedSequence.append(str(key))
			app.utils.functions.verbose(
				['self.lastNumberPressed:', key, 'self.numberPressedSequence', self.numberPressedSequence], self.verbose)
			self.funcDict[self.currentMenuString]()
		else:
			self._exit_menu()

	def Number_7_ABC(self):
		key = 7
		self.Numbers(key)

	def Number_8_DEF(self):
		key = 8
		self.Numbers(key)

	def Number_9_GHI(self):
		key = 9
		self.Numbers(key)

	def Number_4_JKL(self):
		key = 4
		self.Numbers(key)

	def Number_5_MNO(self):
		key = 5
		self.Numbers(key)

	def Number_6_PQR(self):
		key = 6
		self.Numbers(key)

	def Number_1_STU(self):
		key = 1
		self.Numbers(key)

	def Number_2_VWX(self):
		key = 2
		self.Numbers(key)

	def Number_3_YZ(self):
		key = 3
		self.Numbers(key)

	def Number_0(self):
		key = 0
		self.Numbers(key)

	def clear_(self):
		if self.menuFlag:
			self.clearFlag = True
		app.utils.functions.verbose(['\nclear_ - self.clearFlag:', self.clearFlag], self.verbose)

	def enter_(self):
		if self.menuFlag:
			self.enterFlag = True
		app.utils.functions.verbose(['\nenter_ - self.enterFlag:', self.enterFlag], self.verbose)

	def NewGame(self):
		self._menu_on()

	def mode(self):
		self._menu_on()

	def periodClockReset(self):
		pass

	def guestScorePlusOne(self):
		self._menu_on()

	def homeScorePlusOne(self):
		self._menu_on()

	def yardsToGoReset(self):
		self._menu_on()

	def assignError(self):
		self._menu_on()

	def setClock(self):
		if not self.game.clockDict['periodClock'].running:
			self._menu_on()

	def clockUpDown(self):
		if not self.game.clockDict['periodClock'].running:
			self._menu_on()

	def setClockTenthSec(self):
		if not self.game.clockDict['periodClock'].running:
			self._menu_on()

	def tenthSecOnOff(self):
		self._menu_on()

	def autoHorn(self):
		self._menu_on()

	def timeOfDay(self):
		self._menu_on()

	def timeOutTimer(self):
		self._menu_on()

	def setBatterNumber(self):
		self._menu_on()

	def setPitchCounts(self):
		self._menu_on()

	def setGuestScore(self):
		self._menu_on()

	def setHomeScore(self):
		self._menu_on()

	def playClocks(self):
		self._menu_on()

	def setYardsToGo(self):
		self._menu_on()

	def setBallOn(self):
		self._menu_on()

	def setTotalRuns(self):
		self._menu_on()

	def setTotalHits(self):
		self._menu_on()

	def setTotalErrors(self):
		self._menu_on()

	def setRuns_Innings(self):
		self._menu_on()

	def setInningTop_Bot(self):
		self._menu_on()

	def setGuestTimeOuts(self):
		self._menu_on()

	def setHomeTimeOuts(self):
		self._menu_on()

	def play_shotClocks(self):
		if self.funcString == 'play_shotClocks':
			if self.game.gameData['sportType'] == 'soccer':
				self.funcString = 'playClocks'
			else:
				self.funcString = 'shotClocks'
		self._menu_on()

	def shotClocks(self):
		self._menu_on()

	def playerMatchGame(self):
		self._menu_on()

	def playerFoul(self):
		self._menu_on()

	def setGuestFunctions(self):
		self._menu_on()

	def setHomeFunctions(self):
		self._menu_on()

	def guestPenalty(self):
		self._menu_on()

	def homePenalty(self):
		self._menu_on()

	# STAT-------------------------------------------------

	def addPlayer(self):
		self._menu_on()

	def deletePlayer(self):
		self._menu_on()

	def subPlayer(self):
		self._menu_on()

	def editPlayer(self):
		self._menu_on()

	def displaySize(self):
		# self._menu_on()
		pass

	def nextPlayer(self):
		# self._menu_on()
		pass

	def previousPlayer(self):
		# self._menu_on()
		pass

	# CRICKET-------------------------------------------------

	def setPlayer1Number(self):
		self._menu_on()

	def setPlayer2Number(self):
		self._menu_on()

	def setPlayer1Score(self):
		self._menu_on()

	def setPlayer2Score(self):
		self._menu_on()

	def setTotalScore(self):
		self._menu_on()

	def setOvers(self):
		self._menu_on()

	def setLastMan(self):
		self._menu_on()

	def setLastWicket(self):
		self._menu_on()

	def set1eInnings(self):
		self._menu_on()

	def teamNameMenu(self):
		self._menu_on()

	def segmentTimerMenu(self):
		self._menu_on()
