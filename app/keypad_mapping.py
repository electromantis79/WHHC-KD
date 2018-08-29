#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module maps keys from the 5 x 8 grid of possible keys to the Game module method it corresponds to.

	:Created Date: 3/9/2015
	:Author: **Craig Gunter**

"""

import app.utils.reads


class KeypadMapping(object):
	"""
		**Initialization**

	* Builds a dictionary named **Keypad_Keys** simulating the desired keypad.

		*Key* = Button name Ex. "B8"

		*Value* = Pointer to self.game.[*functionName*]
	"""

	def __init__(self, game, reverse_home_and_guest=False, keypad3150=False, mm_basketball=False, whh_flag=False):
		self.funcString = ''
		self.game = game
		self.reverseHomeAndGuest = reverse_home_and_guest
		self.keypad3150 = keypad3150
		self.MMBasketball = mm_basketball
		self.WHHFlag = whh_flag

		# gameFuncDict = Key(button name) : Value(game function called)
		self.gameFuncDict = {
			'guestScorePlusTen': self.game.guestScorePlusTen, 'guestScorePlusOne': self.game.guestScorePlusOne,
			'NewGame':  self.game.NewGame, 'homeScorePlusTen': self.game.homeScorePlusTen,
			'homeScorePlusOne': self.game.homeScorePlusOne,
			'secondsMinusOne': self.game.secondsMinusOne, 'minutesMinusOne': self.game.minutesMinusOne,
			'periodClockOnOff': self.game.periodClockOnOff, 'quartersPlusOne': self.game.quartersPlusOne,
			'setClock': self.game.setClock,
			'setClockTenthSec': self.game.setClockTenthSec, 'tenthSecOnOff': self.game.tenthSecOnOff,
			'clockUpDown': self.game.clockUpDown,
			'autoHorn': self.game.autoHorn, 'timeOfDay': self.game.timeOfDay, 'timeOutTimer': self.game.timeOutTimer,
			'possession': self.game.possession, 'secondsPlusOne': self.game.secondsPlusOne, 'horn': self.game.Horn,
			'setHomeScore': self.game.setHomeScore, 'setGuestScore': self.game.setGuestScore,
			'setGuestFunctions': self.game.setGuestFunctions,
			'setHomeFunctions': self.game.setHomeFunctions, 'guestShotsPlusOne': self.game.guestShotsPlusOne,
			'homeShotsPlusOne': self.game.homeShotsPlusOne, 'periodClockReset': self.game.periodClockReset,
			'handheldButton1': self.game.handheldButton1, 'handheldButton2': self.game.handheldButton2,
			'handheldButton3': self.game.handheldButton3, 'playClocks': self.game.playClocks, 'shotClocks': self.game.shotClocks,
			'mode': self.game.blank, 'blank': self.game.blank, 'None': self.game.blank, '': self.game.blank}

		self.gameFuncDict.update({
			'Number_7_ABC': self.game.Number_7_ABC, 'Number_8_DEF': self.game.Number_8_DEF,
			'Number_9_GHI': self.game.Number_9_GHI,
			'Number_5_MNO': self.game.Number_5_MNO, 'Number_6_PQR': self.game.Number_6_PQR,
			'Number_1_STU': self.game.Number_1_STU,
			'Number_2_VWX': self.game.Number_2_VWX, 'Number_3_YZ': self.game.Number_3_YZ, 'Number_4_JKL': self.game.Number_4_JKL,
			'Number_0_&-.!': self.game.Number_0, 'clear': self.game.clear_, 'enter': self.game.enter_})

		# Multi-sport buttons that call different functions
		if self.game.gameData['sportType'] == 'football':
			self.gameFuncDict['qtrs_periodsPlusOne'] = self.game.quartersPlusOne
		else:
			self.gameFuncDict['qtrs_periodsPlusOne'] = self.game.periodsPlusOne

		if self.game.gameData['sportType'] == 'soccer':
			self.gameFuncDict['guestKicksPlusOne'] = self.game.guestKicksPlusOne
			self.gameFuncDict['guestSavesPlusOne'] = self.game.guestSavesPlusOne
			self.gameFuncDict['homeKicksPlusOne'] = self.game.homeKicksPlusOne
			self.gameFuncDict['homeSavesPlusOne'] = self.game.homeSavesPlusOne
			self.gameFuncDict['play_shotClocks'] = self.game.playClocks
		elif self.game.gameData['sportType'] == 'hockey':
			self.gameFuncDict['guestKicksPlusOne'] = self.game.blank
			self.gameFuncDict['guestSavesPlusOne'] = self.game.blank
			self.gameFuncDict['homeKicksPlusOne'] = self.game.blank
			self.gameFuncDict['homeSavesPlusOne'] = self.game.blank
			self.gameFuncDict['play_shotClocks'] = self.game.shotClocks

		# Hockey
		self.gameFuncDict.update({
			'clear_GuestGoal': self.game.clear_GuestGoal, 'enter_HomeGoal': self.game.enter_HomeGoal,
			'guestPenalty': self.game.guestPenalty, 'homePenalty': self.game.homePenalty})

		# Soccer
		self.gameFuncDict.update({
			'guestPenaltyPlusOne': self.game.guestPenaltyPlusOne, 'homePenaltyPlusOne': self.game.homePenaltyPlusOne})

		# Basketball
		self.gameFuncDict.update({
			'guestTeamFoulsPlusOne': self.game.guestTeamFoulsPlusOne, 'homeTeamFoulsPlusOne': self.game.homeTeamFoulsPlusOne,
			'homeBonus': self.game.homeBonusPlusOne, 'playerMatchGame': self.game.playerMatchGame,
			'playerFoul': self.game.playerFoul,
			'guestBonus': self.game.guestBonusPlusOne, 'setHomeTimeOuts': self.game.setHomeTimeOuts,
			'setGuestTimeOuts': self.game.setGuestTimeOuts})

		# Football
		self.gameFuncDict.update({
			'setYardsToGo': self.game.setYardsToGo, 'setBallOn': self.game.setBallOn, 'yardsToGoReset': self.game.yardsToGoReset,
			'yardsToGoMinusOne': self.game.yardsToGoMinusOne, 'yardsToGoMinusTen': self.game.yardsToGoMinusTen,
			'downsPlusOne': self.game.downsPlusOne, 'guestTimeOutsMinusOne': self.game.guestTimeOutsMinusOne,
			'homeTimeOutsMinusOne': self.game.homeTimeOutsMinusOne})

		# Baseball or Linescore
		self.gameFuncDict.update({
			'flashHitIndicator': self.game.clear_FlashHit, 'flashErrorIndicator': self.game.enter_FlashError,
			'ballsPlusOne': self.game.ballsPlusOne, 'strikesPlusOne': self.game.strikesPlusOne,
			'outsPlusOne': self.game.outsPlusOne,
			'inningsPlusOne': self.game.inningsPlusOne, 'teamAtBat': self.game.teamAtBat,
			'setPitchCounts': self.game.setPitchCounts,
			'setBatterNumber': self.game.setBatterNumber, 'guestPitchesPlusOne': self.game.guestPitchesPlusOne,
			'homePitchesPlusOne': self.game.homePitchesPlusOne, 'clear_FlashHit': self.game.clear_FlashHit,
			'enter_FlashError': self.game.enter_FlashError, 'assignError': self.game.assignError,
			'singlePitchesPlusOne': self.game.singlePitchesPlusOne, 'setTotalRuns': self.game.setTotalRuns,
			'setTotalHits': self.game.setTotalHits, 'setTotalErrors': self.game.setTotalErrors,
			'setRuns_Innings': self.game.setRuns_Innings,
			'incInningTop_Bot': self.game.incInningTop_Bot, 'runsPlusOne': self.game.runsPlusOne,
			'hitsPlusOne': self.game.hitsPlusOne,
			'errorsPlusOne': self.game.errorsPlusOne, 'setInningTop_Bot': self.game.setInningTop_Bot,
			'guestScoreMinusOne': self.game.guestScoreMinusOne, 'homeScoreMinusOne': self.game.homeScoreMinusOne})

		# Stat
		self.gameFuncDict.update({
			'addPlayer': self.game.addPlayer, 'deletePlayer': self.game.deletePlayer, 'displaySize': self.game.displaySize,
			'editPlayer': self.game.editPlayer, 'fouls_digsMinusOne': self.game.fouls_digsMinusOne,
			'fouls_digsPlusOne': self.game.fouls_digsPlusOne, 'nextPlayer': self.game.nextPlayer,
			'subPlayer': self.game.subPlayer,
			'points_killsMinusOne': self.game.points_killsMinusOne, 'points_killsPlusOne': self.game.points_killsPlusOne,
			'previousPlayer': self.game.previousPlayer, 'guest_homeSwitch': self.game.guest_homeSwitch})

		# Cricket
		self.gameFuncDict.update({
			'oversPlusOne': self.game.oversPlusOne, 'player1ScorePlusOne': self.game.player1ScorePlusOne,
			'player2ScorePlusOne': self.game.player2ScorePlusOne, 'wicketsPlusOne': self.game.wicketsPlusOne})

		all_keypad_keys = app.utils.reads.readMP_Keypad_Layouts()

		# Select keypad map section ----------------------

		sport_list = [
			'MMBASEBALL3', 'MPBASEBALL1', 'MMBASEBALL4', 'MPLINESCORE4', 'MPLINESCORE5',
			'MPMP-15X1', 'MPMP-14X1', 'MPMULTISPORT1-baseball', 'MPMULTISPORT1-football', 'MPFOOTBALL1',
			'MMFOOTBALL4', 'MPBASKETBALL1', 'MPSOCCER_LX1-soccer', 'MPSOCCER_LX1-football', 'MPSOCCER1',
			'MPHOCKEY_LX1', 'MPHOCKEY1', 'MPCRICKET1', 'MPRACETRACK1', 'MPLX3450-baseball',
			'MPLX3450-football', 'MPGENERIC', 'MPSTAT']  # 22
		# 23 in list, 5 per line

		keypad_list = [
			'MM_BASEBALL_G_H_CX4', 'MM_BASEBALL_H_G_CX4',
			'MM_FOOTBALL_G_H_CX4', 'MM_FOOTBALL_H_G_CX4',
			'MM_COMBO_G_H_CX4_baseball', 'MM_COMBO_H_G_CX4_baseball',
			'MM_COMBO_G_H_CX4_football', 'MM_COMBO_H_G_CX4_football',
			'MP_BASESOFT_G_H_CX4', 'MP_BASESOFT_H_G_CX4',
			'MP_BASEFOOT_G_H_CX4_baseball', 'MP_BASEFOOT_H_G_CX4_baseball',
			'MP_BASEFOOT_G_H_CX4_football', 'MP_BASEFOOT_H_G_CX4_football',
			'MP_FOOTBALL_G_H_CX4', 'MP_FOOTBALL_H_G_CX4',
			'MP_SOCKEY_G_H_CX4', 'MP_SOCKEY_H_G_CX4',
			'MP_SOCFOOT_G_H_CX4_soccer', 'MP_SOCFOOT_H_G_CX4_soccer',
			'MP_SOCFOOT_G_H_CX4_football', 'MP_SOCFOOT_H_G_CX4_football',
			'MM_BASKETBALL_G_H_OLD', 'MM_BASKETBALL_H_G_OLD',
			'MP_BASKETBALL_G_H_CX4', 'MP_BASKETBALL_H_G_CX4',
			'MP_CRICKET', 'MP_LINESCORE_CX4',
			'MP_STAT_CX803A', 'WHH_BASEBALL',
			'WHH_FOOTBALL']  # 30
		# 30 in list, 2 per line
		# pos=1 MPBASEBALL1, pos=21: MPGENERIC, pos=18: MPRACETRACK1 all MP_BASESOFT_CX4

		sport_list_index = sport_list.index(game.gameData['sport'])

		# This list corresponds to the sport list
		standard_and_reverse_teams_list = [
			(0, 1), (8, 9), (4, 5), (27, 27), (27, 27),
			(27, 27), (27, 27), (10, 11), (12, 13), (14, 15),
			(6, 7), (24, 25), (18, 19), (20, 21), (16, 17),
			(16, 17), (16, 17), (26, 26), (8, 9), (10, 11),
			(12, 13), (8, 9), (28, 28), (2, 3), (22, 23),
			(29, 29), (30, 30)]

		# Handle flags
		if sport_list_index == 10 and self.keypad3150:
			sport_list_index = 23
		elif sport_list_index == 11 and self.MMBasketball:
			sport_list_index = 24
		elif self.WHHFlag:
			if self.game.gameData['sportType'] == 'baseball':
				sport_list_index = 25
			elif self.game.gameData['sportType'] == 'football':
				sport_list_index = 26

		# Handle reverse keypad
		if self.reverseHomeAndGuest:
			self.keypadName = keypad_list[standard_and_reverse_teams_list[sport_list_index][1]]
		else:
			self.keypadName = keypad_list[standard_and_reverse_teams_list[sport_list_index][0]]

		# Create key map dictionary
		print('Keypad Name', self.keypadName)
		down_string = '_DOWN'
		up_string = '_UP'
		self.Keypad_Keys = {down_string: None, up_string: None}
		# print(self.keypadName+down_string, all_keypad_keys.keys())

		if self.keypadName+down_string in all_keypad_keys:
			self.Keypad_Keys[down_string] = all_keypad_keys[self.keypadName+down_string]
		else:
			self.Keypad_Keys[down_string] = all_keypad_keys[self.keypadName]

		if self.keypadName+up_string in all_keypad_keys:
			self.Keypad_Keys[up_string] = all_keypad_keys[self.keypadName+up_string]
		else:
			self.Keypad_Keys[up_string] = None

		# print(self.Keypad_Keys)

	def get_func_string(self, key_pressed, direction='_DOWN'):
		# PUBLIC method
		if direction is not None:
			if direction == '_BOTH':
				both = [self.Keypad_Keys['_UP'][key_pressed], self.Keypad_Keys['_DOWN'][key_pressed]]
				func_string = None
				for x, each in enumerate(both):
					if both[x] != 'None':
						func_string = both[x]

				return func_string
			else:
				if direction in self.Keypad_Keys and key_pressed in self.Keypad_Keys[direction]:
					return self.Keypad_Keys[direction][key_pressed]
				else:
					return ''
		else:
			return ''

	def check_for_byte_pair(self, byte_pair):
		# PUBLIC method
		if byte_pair in self.Keypad_Keys['_DOWN']:
			return 1
		else:
			return 0

	def map_(self, key_pressed, direction='_DOWN'):
		"""
		Matches grid location to function name
		All combinations of B through F with 8 through 1
		Calls game object method
		Sets the keyPressFlag used by the Menu_Class
		"""
		# PUBLIC method
		self.funcString = self.get_func_string(key_pressed, direction=direction)
		print("Key mapped %s" % key_pressed, 'to funcString "%s"' % self.funcString)
		print("Called", str(self.gameFuncDict[self.funcString]))
		self.gameFuncDict[self.funcString]()  # call game function
		return self.funcString
