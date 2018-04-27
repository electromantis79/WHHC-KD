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

		*Value* = Pointer to game.[*functionName*]
	"""

	def __init__(self, game, reverse_home_and_guest=False, keypad3150=False, mm_basketball=False, whh_baseball=False):
		self.funcString = ''
		self.keyPressFlag = False
		self.reverseHomeAndGuest = reverse_home_and_guest
		self.keypad3150 = keypad3150
		self.MMBasketball = mm_basketball
		self.WHHBaseball = whh_baseball

		self.gameFuncDict = {
			'guestScorePlusTen': game.guestScorePlusTen, 'guestScorePlusOne': game.guestScorePlusOne,
			'NewGame':  game.NewGame, 'homeScorePlusTen': game.homeScorePlusTen, 'homeScorePlusOne': game.homeScorePlusOne,
			'secondsMinusOne': game.secondsMinusOne, 'minutesMinusOne': game.minutesMinusOne,
			'periodClockOnOff': game.periodClockOnOff, 'quartersPlusOne': game.quartersPlusOne, 'setClock': game.setClock,
			'setClockTenthSec': game.setClockTenthSec, 'tenthSecOnOff': game.tenthSecOnOff, 'clockUpDown': game.clockUpDown,
			'autoHorn': game.autoHorn, 'timeOfDay': game.timeOfDay, 'timeOutTimer': game.timeOutTimer,
			'possession': game.possession, 'secondsPlusOne': game.secondsPlusOne, 'horn': game.Horn,
			'setHomeScore': game.setHomeScore, 'setGuestScore': game.setGuestScore, 'setGuestFunctions': game.setGuestFunctions,
			'setHomeFunctions': game.setHomeFunctions, 'guestShotsPlusOne': game.guestShotsPlusOne,
			'homeShotsPlusOne': game.homeShotsPlusOne, 'periodClockReset': game.periodClockReset,
			'handheldButton1': game.handheldButton1, 'handheldButton2': game.handheldButton2,
			'handheldButton3': game.handheldButton3, 'playClocks': game.playClocks, 'shotClocks': game.shotClocks,
			'mode': game.blank, 'blank': game.blank, 'None': game.blank, '': game.blank}

		self.gameFuncDict.update({
			'Number_7_ABC': game.Number_7_ABC, 'Number_8_DEF': game.Number_8_DEF, 'Number_9_GHI': game.Number_9_GHI,
			'Number_5_MNO': game.Number_5_MNO, 'Number_6_PQR': game.Number_6_PQR, 'Number_1_STU': game.Number_1_STU,
			'Number_2_VWX': game.Number_2_VWX, 'Number_3_YZ': game.Number_3_YZ, 'Number_4_JKL': game.Number_4_JKL,
			'Number_0_&-.!': game.Number_0, 'clear': game.clear_, 'enter': game.enter_})

		# Multi-sport buttons that call different functions
		if game.gameData['sportType'] == 'football':
			self.gameFuncDict['qtrs_periodsPlusOne'] = game.quartersPlusOne
		else:
			self.gameFuncDict['qtrs_periodsPlusOne'] = game.periodsPlusOne

		if game.gameData['sportType'] == 'soccer':
			self.gameFuncDict['guestKicksPlusOne'] = game.guestKicksPlusOne
			self.gameFuncDict['guestSavesPlusOne'] = game.guestSavesPlusOne
			self.gameFuncDict['homeKicksPlusOne'] = game.homeKicksPlusOne
			self.gameFuncDict['homeSavesPlusOne'] = game.homeSavesPlusOne
			self.gameFuncDict['play_shotClocks'] = game.playClocks
		elif game.gameData['sportType'] == 'hockey':
			self.gameFuncDict['guestKicksPlusOne'] = game.blank
			self.gameFuncDict['guestSavesPlusOne'] = game.blank
			self.gameFuncDict['homeKicksPlusOne'] = game.blank
			self.gameFuncDict['homeSavesPlusOne'] = game.blank
			self.gameFuncDict['play_shotClocks'] = game.shotClocks

		# Hockey
		self.gameFuncDict.update({
			'clear_GuestGoal': game.clear_GuestGoal, 'enter_HomeGoal': game.enter_HomeGoal,
			'guestPenalty': game.guestPenalty, 'homePenalty': game.homePenalty})

		# Soccer
		self.gameFuncDict.update({
			'guestPenaltyPlusOne': game.guestPenaltyPlusOne, 'homePenaltyPlusOne': game.homePenaltyPlusOne})

		# Basketball
		self.gameFuncDict.update({
			'guestTeamFoulsPlusOne': game.guestTeamFoulsPlusOne, 'homeTeamFoulsPlusOne': game.homeTeamFoulsPlusOne,
			'homeBonus': game.homeBonusPlusOne, 'playerMatchGame': game.playerMatchGame, 'playerFoul': game.playerFoul,
			'guestBonus': game.guestBonusPlusOne, 'setHomeTimeOuts': game.setHomeTimeOuts,
			'setGuestTimeOuts': game.setGuestTimeOuts})

		# Football
		self.gameFuncDict.update({
			'setYardsToGo': game.setYardsToGo, 'setBallOn': game.setBallOn, 'yardsToGoReset': game.yardsToGoReset,
			'yardsToGoMinusOne': game.yardsToGoMinusOne, 'yardsToGoMinusTen': game.yardsToGoMinusTen,
			'downsPlusOne': game.downsPlusOne, 'guestTimeOutsMinusOne': game.guestTimeOutsMinusOne,
			'homeTimeOutsMinusOne': game.homeTimeOutsMinusOne})

		# Baseball or Linescore
		self.gameFuncDict.update({
			'flashHitIndicator': game.clear_FlashHit, 'flashErrorIndicator': game.enter_FlashError,
			'ballsPlusOne': game.ballsPlusOne, 'strikesPlusOne': game.strikesPlusOne, 'outsPlusOne': game.outsPlusOne,
			'inningsPlusOne': game.inningsPlusOne, 'teamAtBat': game.teamAtBat, 'setPitchCounts': game.setPitchCounts,
			'setBatterNumber': game.setBatterNumber, 'guestPitchesPlusOne': game.guestPitchesPlusOne,
			'homePitchesPlusOne': game.homePitchesPlusOne, 'clear_FlashHit': game.clear_FlashHit,
			'enter_FlashError': game.enter_FlashError, 'assignError': game.assignError,
			'singlePitchesPlusOne': game.singlePitchesPlusOne, 'setTotalRuns': game.setTotalRuns,
			'setTotalHits': game.setTotalHits, 'setTotalErrors': game.setTotalErrors, 'setRuns_Innings': game.setRuns_Innings,
			'incInningTop_Bot': game.incInningTop_Bot, 'runsPlusOne': game.runsPlusOne, 'hitsPlusOne': game.hitsPlusOne,
			'errorsPlusOne': game.errorsPlusOne, 'setInningTop_Bot': game.setInningTop_Bot,
			'guestScoreMinusOne': game.guestScoreMinusOne, 'homeScoreMinusOne': game.homeScoreMinusOne})

		# Stat
		self.gameFuncDict.update({
			'addPlayer': game.addPlayer, 'deletePlayer': game.deletePlayer, 'displaySize': game.displaySize,
			'editPlayer': game.editPlayer, 'fouls_digsMinusOne': game.fouls_digsMinusOne,
			'fouls_digsPlusOne': game.fouls_digsPlusOne, 'nextPlayer': game.nextPlayer, 'subPlayer': game.subPlayer,
			'points_killsMinusOne': game.points_killsMinusOne, 'points_killsPlusOne': game.points_killsPlusOne,
			'previousPlayer': game.previousPlayer, 'guest_homeSwitch': game.guest_homeSwitch})

		# Cricket
		self.gameFuncDict.update({
			'oversPlusOne': game.oversPlusOne, 'player1ScorePlusOne': game.player1ScorePlusOne,
			'player2ScorePlusOne': game.player2ScorePlusOne, 'wicketsPlusOne': game.wicketsPlusOne})

		all_keypad_keys = app.utils.reads.readMP_Keypad_Layouts()

		# Update with MPCRICKET1, MPRACETRACK1, STAT keypads
		self.Keypad_Keys = {}
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

		position = sport_list.index(game.gameData['sport'])
		loop_list = [
			(0, 1), (8, 9), (4, 5), (27, 27), (27, 27),
			(27, 27), (27, 27), (10, 11), (12, 13), (14, 15),
			(6, 7), (24, 25), (18, 19), (20, 21), (16, 17),
			(16, 17), (16, 17), (26, 26), (8, 9), (10, 11),
			(12, 13), (8, 9), (28, 28), (2, 3), (22, 23),
			(29, 29), (30, 30)]

		# Need to make MM Combos work on simulator
		if position == 10 and self.keypad3150:
			position = 23
		elif position == 11 and self.MMBasketball:
			position = 24
		elif game.gameData['sportType'] == 'baseball' and self.WHHBaseball:
			position = 25
		elif self.WHHBaseball:
			position = 26
		if not self.reverseHomeAndGuest:
			self.keypadName = keypad_list[loop_list[position][0]]
		else:
			self.keypadName = keypad_list[loop_list[position][1]]
		self.Keypad_Keys = all_keypad_keys[self.keypadName]

	def map_(self, game, key_pressed):
		"""
		Matches grid location to function name
		All combinations of B through F with 8 through 1
		Calls game object method
		Sets the keyPressFlag used by the Menu_Class
		"""
		# PUBLIC method
		self.funcString = self.Keypad_Keys[key_pressed]  # find function name
		print 'funcString: ', self.funcString
		print "Pressed Key:%s" % key_pressed
		self.gameFuncDict[self.funcString]()  # call game function
		self.keyPressFlag = True
		return game, self.funcString

	def _test_all_buttons(self, game):
		# Method for testing this module only
		letters = ['B', 'C', 'D', 'E', 'F']
		numbers = ['8', '7', '6', '5', '4', '3', '2', '1']
		for i in range(8):
			for j in range(5):
				function_ = letters[j]+numbers[i]
				print function_
				self.map_(game, function_)
				print game.gameData
				raw_input()


"""
def test():
	print "ON"
	c=Config()
	sportList = [\
	'MMBASEBALL3','MPBASEBALL1','MMBASEBALL4','MPLINESCORE4','MPLINESCORE5',\
	'MPMP-15X1','MPMP-14X1','MPMULTISPORT1-baseball','MPMULTISPORT1-football', 'MPFOOTBALL1',\
	'MMFOOTBALL4','MPBASKETBALL1', 'MPSOCCER_LX1-soccer','MPSOCCER_LX1-football','MPSOCCER1',\
	'MPHOCKEY_LX1','MPHOCKEY1','MPCRICKET1','MPRACETRACK1','MPLX3450-baseball',\
	'MPLX3450-football','MPGENERIC', 'MPSTAT']#22
	# 23 in list, 5 per line
	sport=sportList[1]
	c.writeSport(sport)
	game = selectSportInstance(sport)
	print game.sport
	# True False
	reverseHomeAndGuest=False
	keypad3150=False
	MMBasketball=False
	WHHBaseball=True
	keyMap=KeypadMapping(game, reverseHomeAndGuest, keypad3150, MMBasketball, WHHBaseball)
	print '\nreverseHomeAndGuest', reverseHomeAndGuest, 
	'\nkeypad3150', keypad3150, '\nMMBasketball', MMBasketball, '\nWHHBaseball', WHHBaseball
	print '\nkeypadName', keyMap.keypadName
	printDictsExpanded(keyMap, 1)
	raw_input()

	keyMap._test_all_buttons(game)

	while 1:
		PRESSED=raw_input('                                     Type key (Ex. B8): ')
		keyMap.map_(game, PRESSED)
		gameDict=game.__dict__
		printDict(gameDict)
"""
