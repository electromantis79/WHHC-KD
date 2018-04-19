#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

.. topic:: Overview

	This module maps data stored in memory to the 32 or 64 bank MP architecture for a given sport.
	This can be done in either direction (memory to MP word or MP word to memory)

	:Created Date: 3/16/2015
	:Author: **Craig Gunter**

	.. warning:: This is *where the magic happens*.
"""

import app.utils.functions
import app.utils.reads
import app.mp_data_handler


class AddressMapping(object):
	"""

	**Initialization**

	* Build a dictionary of the 32 possible words of a sport named **wordsDict**.

		This will be the default values for that sport.

		*Key* = binary address of group and bank

		*Value* = a 16-bit word in the low-byte then high-byte format

			**Word** in this context is one packet of information a driver needs to update a single header

				==========  =========
				High Byte    Low Byte
				==========  =========
				1GBBWWIH     0GFEDCBA
				==========  =========

				G = Group, B = Bank, W = Word (Different than the word mentioned above)

				I = Control bit, H through A = The eight segments of display data

				.. note:: Low byte is received first and the high byte is received second

	*

	"""

	def __init__(self, game=None, sport=None, sport_type=None):
		self.game = game
		self.sport = sport
		self.sportType = sport_type

		# Override parameters if we have a game object
		if self.game is not None:
			self.sport = self.game.gameData['sport']
			self.sportType = self.game.gameData['sportType']

		# Variables and Dictionaries
		self.verbose = False
		self.verboseTunnel = False
		self.rssi = 0
		self.rssiFlag = False
		self.tenthsTransitionFlag = False
		self.multisportChangeSportFlag = False
		self.multisportChangeSportCount = 0
		self.brightness = 100
		self.quantumDimmingTunnel = 0
		self.quantumETNTunnel = 0
		self.fontJustifyControl = 0
		self.leftETNByte = 0
		self.rightETNByte = 0
		self.quantumETNTunnelTeam = ''
		self.addressPair = 1
		self.quantumETNTunnelNameProcessed = False
		self.quantumETNTunnelFontJustifyProcessed = False
		self.wordListAddrStat = [
			1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23, 33, 34, 35, 37, 38, 39, 41, 42,
			43, 45, 46, 47, 49, 50, 51, 53, 54, 55]
		self.tempClockDict = {}

		if self.sportType == 'stat':
			self.statFlag = True
			self.wordListAddr = self.wordListAddrStat
		else:
			self.statFlag = False
			self.wordListAddr = range(1, 33)

		self.mp = app.mp_data_handler.MpDataHandler()
		self.wordsDict = dict.fromkeys(self.wordListAddr, 0)
		self._blank_map()

		self.addressMapDict = {}
		if self.sport is not None and self.sportType is not None:
			self.fullAddressMapDict = app.utils.reads.read_address_map(self.sport, self.sportType, self.wordListAddr)
			self._build_addr_map()

		self.periodClockUnMapKeysList = [
			'hoursUnits', 'minutesTens', 'minutesUnits', 'secondsTens', 'secondsUnits', 'tenthsUnits',
			'hundredthsUnit', 'colonIndicator']
		self.periodClockUnMapDict = dict.fromkeys(self.periodClockUnMapKeysList)

	# Startup methods
	def _blank_map(self):
		# Build blank MP wordsDict
		if self.statFlag:
			for k in range(2):
				for i in range(2):
					for j in range(4):
						self.wordsDict[((i*4+j)*4+1)+k*32] = self.mp.encode(
							i + 1, j + 1, 1, k, 0, 0x0, 0x0, 'AlwaysHighLow', 0, True)
						self.wordsDict[((i*4+j)*4+2)+k*32] = self.mp.encode(
							i + 1, j + 1, 2, k, 0, 0x0, 0x0, 'AlwaysHighLow', 0, True)
						self.wordsDict[((i*4+j)*4+3)+k*32] = self.mp.encode(
							i + 1, j + 1, 3, k, 0, 0x0, 0x0, 'AlwaysHighLow', 0, True)
						self.wordsDict[((i*4+j)*4+4)+k*32] = self.mp.encode(
							i + 1, j + 1, 4, k, 0, 0, 0, 'AlwaysHighLow', 0)
		else:
			for i in range(2):
				for j in range(4):
					self.wordsDict[(i*4+j)*4+1] = self.mp.encode(i + 1, j + 1, 1, 0, 0, 0x0, 0x0, 'AlwaysHighLow', 0)
					self.wordsDict[(i*4+j)*4+2] = self.mp.encode(i + 1, j + 1, 2, 0, 0, 0x0, 0x0, 'AlwaysHighLow', 0)
					self.wordsDict[(i*4+j)*4+3] = self.mp.encode(i + 1, j + 1, 3, 0, 0, 0, 0, 'AlwaysHighLow', 0)
					self.wordsDict[(i*4+j)*4+4] = self.mp.encode(i + 1, j + 1, 4, 1, 0, 0, 0, 'AlwaysHighLow', 0)

	def _build_addr_map(self):
		# Build an address map with the current state of flag selected alternates
		for address in self.wordListAddr:
			try:
				self.addressMapDict[address] = self.fullAddressMapDict[address][1]
			except:
				print 'Error', address, self.addressMapDict

	# startup methods end

	# callable methods and internal methods start -----

	def map(self):
		"""
		Updates the wordsDict of MP Formatted data packs.

		"""
		# PUBLIC method
		self._adjust_all_banks()

	# G1		B1=1, 2, 3, 4		B2=5, 6, 7, 8 		B3=9, 10, 11, 12, 		B4=13, 14, 15, 16
	# G2		B1=17, 18, 19, 20 	B2=21, 22, 23, 24 	B3=25, 26, 27, 28 		B4=29, 30, 31, 32

	# Map()'s main methods - "The _adjust_all_banks chain"

	def _adjust_all_banks(self):
		# Checks states of flags per sport and creates a list of alternate mapping addresses
		# and adds them to the standard addressMapDict.

		# Fetch the data, make any changes, and adjust the **wordsDict**.

		app.utils.functions.verbose('\n-------_adjust_all_banks-------\n', self.verbose)
		alts = []
		under_minute = False

		# Freeze clock data
		if 'periodClock' in self.game.clockDict:

			self.tempClockDict.clear()
			for clocks in self.game.clockDict.keys():
				self.tempClockDict[clocks] = dict(self.game.clockDict[clocks].timeUnitsDict)

			if (
					self.tempClockDict['periodClock']['daysTens'] == 0
					and self.tempClockDict['periodClock']['daysUnits'] == 0
					and self.tempClockDict['periodClock']['hoursTens'] == 0
					and self.tempClockDict['periodClock']['hoursUnits'] == 0
					and self.tempClockDict['periodClock']['minutesTens'] == 0
					and self.tempClockDict['periodClock']['minutesUnits'] == 0
					and self.tempClockDict['periodClock']['secondsTens'] < 6
			):
				under_minute = True

		# Check for any flag changes
		if self.sport == 'MPBASEBALL1' or self.sport == 'MMBASEBALL3':
			if under_minute:
				if self.game.gameSettings['2D_Clock']:
					alts = self._format_alts(alts, [2, 21], 2)
			else:
				if self.game.gameSettings['2D_Clock']:
					alts = self._format_alts(alts, [1, 2, 21, 22], 2)
			if self.game.gameSettings['hoursFlagJumper'] and self.game.gameSettings['2D_Clock']:
				alts = self._format_alts(alts, [3, 23], 2)
			if self.game.gameSettings['scoreTo19Flag']:
				alts = self._format_alts(alts, [5, 6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 28], 2)
			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [1, 2, 21, 22], 4)

		elif self.sport == 'MPLINESCORE5':
			if self.game.gameSettings['clock_3D_or_less_Flag'] and not under_minute:
				alts = self._format_alts(alts, [23], 2)

			if self.game.gameSettings['doublePitchCountFlag'] and self.game.gameSettings['pitchSpeedFlag']:
				alts = self._format_alts(alts, [5, 14, 15, 16, 31, 32], 2)
			elif self.game.gameSettings['doublePitchCountFlag']:
				alts = self._format_alts(alts, [14, 15, 16, 31, 32], 2)
			elif self.game.gameSettings['pitchSpeedFlag']:
				alts = self._format_alts(alts, [31, 32], 3)
				alts = self._format_alts(alts, [5], 2)

			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [21, 22], 4)
			elif under_minute and self.game.gameSettings['periodClockTenthsFlag']:
				alts = self._format_alts(alts, [21, 22], 2)

		elif self.sport == 'MPLINESCORE4':
			if under_minute and self.game.gameSettings['periodClockTenthsFlag']:
				alts = self._format_alts(alts, [21, 22], 2)
			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [21, 22], 4)

		elif self.sport == 'MPMP_15X1' or self.sport == 'MPMP_14X1' or self.sport == 'MMBASEBALL4':
			pass

		elif (
				self.sport == 'MPMULTISPORT1-football' or self.sport == 'MPMULTISPORT1-baseball' or
				self.sport == 'MPLX3450-football' or self.sport == 'MPLX3450-baseball'
		):
			if self.sport == 'MPLX3450-baseball' and under_minute:
				alts = self._format_alts(alts, [1], 2)
			if under_minute and self.game.gameSettings['periodClockTenthsFlag']:
				alts = self._format_alts(alts, [6, 7, 8, 21, 22], 2)
				if self.sport == 'MPLX3450-football':
					alts = self._format_alts(alts, [1, 2], 2)
			if self.game.gameSettings['clock_3D_or_less_Flag'] and (
					self.sport == 'MPLX3450-baseball' or self.sport == 'MPMULTISPORT1-baseball'):
				alts = self._format_alts(alts, [31], 2)
				if under_minute:
					alts = self._format_alts(alts, [8], 3)
				else:
					alts = self._format_alts(alts, [8], 5)

			if self.sport == 'MPMULTISPORT1-football':
				if self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
					alts = self._format_alts(alts, [6, 7, 8, 21, 22], 3)
				if self.game.gameSettings['timeOfDayClockEnable']:
					alts = self._format_alts(alts, [6, 7, 8, 21, 22], 4)

			elif self.sport == 'MPLX3450-football':
				if self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
					alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 3)
				if self.game.gameSettings['timeOfDayClockEnable']:
					alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 4)

			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [6, 7, 8, 21, 22], 4)

		elif self.sport == 'MPFOOTBALL1':
			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 3)
			elif under_minute:
				if not self.game.gameSettings['trackClockEnable'] and self.game.gameSettings['periodClockTenthsFlag']:
					alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 2)

			if self.game.gameSettings['trackClockEnable']:  # Just Tenths Units word 3 or 4
				if self.game.gameSettings['periodClockTenthsFlag']:
					alts = self._format_alts(alts, [11, 18], 2)

			if self.game.gameSettings['yardsToGoUnits_to_quarter']:  # or 1:# This added for a range test with a 2180 WARNING
				alts = self._format_alts(alts, [23], 2)

		elif self.sport == 'MMFOOTBALL4':
			if under_minute and self.game.gameSettings['periodClockTenthsFlag']:
				alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 2)
			if self.game.gameSettings['yardsToGoUnits_to_quarter']:
				alts = self._format_alts(alts, [3, 23], 2)

		elif self.sport == 'MPSOCCER_LX1-football' or self.sport == 'MPSOCCER_LX1-soccer':
			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [6, 7, 8, 21, 22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				alts = self._format_alts(alts, [6, 7, 8, 21, 22], 3)
			elif under_minute:
				if not self.game.gameSettings['trackClockEnable'] and self.game.gameSettings['periodClockTenthsFlag']:
					alts = self._format_alts(alts, [6, 7, 8, 21, 22], 2)

			if self.game.gameSettings['trackClockEnable']:
				if self.game.gameSettings['periodClockTenthsFlag']:
					alts = self._format_alts(alts, [18], 2)

		elif self.sport == 'MPBASKETBALL1':
			if self.game.gameSettings['shotClockBlankEnable']:
				alts = self._format_alts(alts, [5], 3)
			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 3)
			elif under_minute and self.game.gameSettings['periodClockTenthsFlag']:
				alts = self._format_alts(alts, [1, 2, 6, 7, 8, 21, 22], 2)

		elif self.sport == 'MPHOCKEY_LX1':
			if self.game.gameSettings['shotClockBlankEnable']:
				alts = self._format_alts(alts, [5], 3)
			if self.game.gameSettings['timeOfDayClockEnable']:
				alts = self._format_alts(alts, [6, 7, 8, 21, 22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				alts = self._format_alts(alts, [6, 7, 8, 21, 22], 3)
			elif under_minute and self.game.gameSettings['periodClockTenthsFlag']:
				alts = self._format_alts(alts, [6, 7, 8, 21, 22], 2)

		# Build addressMapDict with all level 1 alts
		self._build_addr_map()

		# Use addressMapDict to get values, format them and update the wordsDict
		self._update_addr_words(alts)

	@staticmethod
	def _format_alts(list_, addresses, alt):
		for address in addresses:
			list_.append((address, alt))
		return list_

	def _update_addr_words(self, alts):
		app.utils.functions.verbose(['alts', alts], self.verbose)

		# Method for blanking others in time of day clock mode
		if self.game.gameSettings['timeOfDayClockBlankingEnable']:
			self.addressMapDict.clear()
			self._blank_map()
			address_list = []
			for index, addressTup in enumerate(alts):
				if addressTup[1] != 4:
					alts.remove(alts[index])
				else:
					address_list.append(addressTup[0])
		else:
			# Normal Operation
			address_list = self.wordListAddr

		# Switch out alternates
		for addressTup in alts:
			try:
				self.addressMapDict[addressTup[0]] = self.fullAddressMapDict[addressTup[0]][addressTup[1]]
			except:
				print 'alts', alts, 'Not in address map'

		# Sort the players on a stat board
		if self.statFlag and 0:  # 0 for ASCII 2 MP converter
			self._sort_players()

		# Use map to get correct variable, then store in the words dictionary
		for address in address_list:

			# Fetch all data values
			(
				group, bank, word, i_bit, h_bit,
				high_nibble, low_nibble, blank_type, segment_data) = self._load_from_add_dict(address)

			# Replace 221 with rssi value - For testing of WHH Console
			if group == 2 and bank == 2 and word == 1 and self.rssiFlag:
				high_nibble = self.rssi/10
				low_nibble = self.rssi % 10

			# encode values into MP style word and fill wordsDict
			self.wordsDict[address] = self.mp.encode(
				group, bank, word, i_bit, h_bit,
				high_nibble, low_nibble, blank_type, segment_data, stat_flag=self.statFlag)

	def _sort_players(self):
		# Only needed for menu controlled sorting
		active_player_list, team, team_name = app.utils.functions.active_player_list_select(self.game)
		active_player_list.sort()

		for x, player_number in enumerate(active_player_list):
			player_id = self.game.get_player_data(team, 'playerNumber', player_number=player_number)
			self.game.set_team_data(team, 'player' + self.game.statNumberList[x + 1], int(player_number), 2)
			foul = self.game.get_player_data(team, 'fouls', player_id=player_id)
			self.game.set_team_data(team, 'foul' + self.game.statNumberList[x + 1], foul, 2)
			points = self.game.get_player_data(team, 'points', player_id=player_id)
			self.game.set_team_data(team, 'points' + self.game.statNumberList[x + 1], points, 2)
		if len(active_player_list) < self.game.maxActive:
			for x in range((len(self.game.statNumberList)-1)-len(active_player_list)):
				self.game.set_team_data(team, 'player' + self.game.statNumberList[x + 1 + len(active_player_list)], 255, 2)
				self.game.set_team_data(team, 'foul' + self.game.statNumberList[x + 1 + len(active_player_list)], 255, 2)
				self.game.set_team_data(team, 'points' + self.game.statNumberList[x + 1 + len(active_player_list)], 255, 2)

	def _load_from_add_dict(self, address):  # This is the beginning of data manipulation into the MP Format!!!
		# Get word info, adjust it, and convert it to memory value.

		# addressMapDict fetch
		group = int(self.addressMapDict[address]['GROUP'])  # INT
		word = int(self.addressMapDict[address]['WORD'])  # INT
		bank = int(self.addressMapDict[address]['BANK'])  # INT
		i_bit = self.addressMapDict[address]['I_BIT']
		h_bit = self.addressMapDict[address]['H_BIT']
		high_nibble = self.addressMapDict[address]['HIGH_NIBBLE']
		low_nibble = self.addressMapDict[address]['LOW_NIBBLE']
		blank_type = self.addressMapDict[address]['BLANK_TYPE']
		segment_data = self.addressMapDict[address]['SEGMENT_DATA']
		if self.verbose:
			print group, bank, word, i_bit, h_bit, high_nibble, low_nibble, blank_type, segment_data

		# Prepare values for encoding
		i_bit = self._i_bit_format(i_bit)  # string to int

		h_bit = self._h_bit_format(h_bit)  # string to int

		high_nibble, low_nibble, blank_type = self._nibble_format(high_nibble, low_nibble, blank_type, word, address)

		segment_data = self._segment_data_format(segment_data)  # string to int

		if self.verbose:
			print group, bank, word, i_bit, h_bit, high_nibble, low_nibble, blank_type, segment_data
		return group, bank, word, i_bit, h_bit, high_nibble, low_nibble, blank_type, segment_data

	# Formatting Functions

	def _i_bit_format(self, i_bit):
		# Format data - i_bit
		team = self._team_extract(i_bit)
		if i_bit == '0'or i_bit == '':
			i_bit = 0
		elif i_bit == '1' or i_bit == 'active':
			i_bit = 1
		elif i_bit == 'teamOneBonus2' or i_bit == 'teamTwoBonus2':
			value = self.game.get_team_data(team, 'bonus')
			if value == 2:
				i_bit = 1
			else:
				i_bit = 0
		elif i_bit[:7] == 'teamTwo' or i_bit[:7] == 'teamOne':
			i_bit = i_bit[:7] + str.lower(i_bit[7]) + i_bit[8:]
			i_bit = self.game.get_team_data(team, i_bit[7:])
		elif i_bit[:7] == 'penalty':
			timer_number = i_bit[7]
			i_bit = self._trim_penalty(i_bit)
			team_string = i_bit[:7]
			i_bit = self._trim_team_name(i_bit)
			if i_bit[:5] == 'colon':
				team = self._team_extract(team_string)
				i_bit = self.game.get_team_data(team, 'TIMER' + timer_number + '_COLON_INDICATOR')
		elif i_bit == 'outs1':
			outs = self.game.get_game_data('outs')
			if outs >= 1:
				i_bit = 1
			else:
				i_bit = 0
		elif i_bit == 'outs2':
			outs = self.game.get_game_data('outs')
			if outs >= 2:
				i_bit = 1
			else:
				i_bit = 0
		elif i_bit == 'quarter4':
			quarter = self.game.get_game_data('quarter')
			if quarter >= 4:
				i_bit = 1
			else:
				i_bit = 0
		else:
			i_bit = self.game.get_game_data(i_bit)
		return i_bit

	def _h_bit_format(self, h_bit):
		# Format data - h_bit
		team = self._team_extract(h_bit)
		if h_bit == '0'or h_bit == '':
			h_bit = 0
		elif h_bit == '1':
			h_bit = 1
		elif h_bit[:7] == 'teamTwo' or h_bit[:7] == 'teamOne':
			h_bit = h_bit[:7] + str.lower(h_bit[7]) + h_bit[8:]
			h_bit = self.game.get_team_data(team, h_bit[7:])
		elif h_bit[:7] == 'penalty':
			timer_number = h_bit[7]
			h_bit = self._trim_penalty(h_bit)
			team_string = h_bit[:7]
			h_bit = self._trim_team_name(h_bit)
			if h_bit[:5] == 'colon':
				team = self._team_extract(team_string)
				h_bit = self.game.get_team_data(team, 'TIMER' + timer_number + '_COLON_INDICATOR')
		else:
			h_bit = self.game.get_game_data(h_bit)
		return h_bit

	def _team_extract(self, value):
		team = None
		if value[:7] == 'teamOne' or value[9:16] == 'teamOne':
			team = self.game.guest
		elif value[:7] == 'teamTwo' or value[9:16] == 'teamTwo':
			team = self.game.home
		return team

	@staticmethod
	def _trim_penalty(name):
		return name[9:]

	@staticmethod
	def _trim_team_name(name):
		return str.lower(name[7])+name[8:]

	@staticmethod
	def _period_clock_value_check(value):
		return (
				value == 'hoursUnits' or value == 'tenthsUnits' or value == 'minutesUnits'
				or value == 'minutesTens'or value == 'secondsUnits'or value == 'secondsTens')

	@staticmethod
	def _team_value_check(value):
		return value[:4] == 'team' or value[9:13] == 'team'

	def _game_value_check(self, value):
		if self._period_clock_value_check(value):
			return 0
		elif self._team_value_check(value):
			return 0
		return 1

	def _nibble_format(self, high_nibble_name, low_nibble_name, blank_type, word, addr_word_number):
		# Gets the current game data values with these names, formats them, and returns them.

		app.utils.functions.verbose([
			'\n_nibble_format(before) - high_nibble_name, low_nibble_name, blank_type, word, addr_word_number - \n',
			high_nibble_name, low_nibble_name, blank_type, word, addr_word_number], self.verbose)

		# Handle nibble blanking
		if high_nibble_name == 'blank'and low_nibble_name == 'blank':
			high_nibble = low_nibble = high_nibble_name = low_nibble_name = 0
			blank_type = 'AlwaysHighLow'

		elif high_nibble_name == 'blank':
			high_nibble = high_nibble_name = 0
			blank_type = 'AlwaysHigh'

		elif low_nibble_name == 'blank':
			low_nibble = low_nibble_name = 0
			blank_type = 'AlwaysLow'

		# Handle rejected values
		if high_nibble_name == '' or high_nibble_name == '0':
			high_nibble = high_nibble_name = 0

		if low_nibble_name == '' or low_nibble_name == '0':
			low_nibble = low_nibble_name = 0

		# High nibble
		blank_type_high = False
		if high_nibble_name != 0:
			team_high = self._team_extract(high_nibble_name)

			if self._period_clock_value_check(high_nibble_name):

				# cancel blanking for this
				line5_and_c_jumper = self.game.gameData['sport'] == 'MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']
				basball_1_3_and_c_jumper = (
						(self.game.gameData['sport'] == 'MPBASEBALL1' or self.game.gameData['sport'] == 'MMBASEBALL3')
						and 'C' in self.game.gameData['optionJumpers'])
				multi_bb_and_c_jumper = (
						(self.sport == 'MPMULTISPORT1-baseball' or self.sport == 'MPLX3450-baseball')
						and 'C' in self.game.gameData['optionJumpers'])
				if (
						basball_1_3_and_c_jumper or line5_and_c_jumper or multi_bb_and_c_jumper
						or self.tempClockDict['periodClock']['hoursUnits'] != 0
						or self.game.gameSettings['hoursFlag']
						and (high_nibble_name == 'minutesTens' or high_nibble_name == 'secondsTens')):

					if self.game.gameData['sport'] == 'MPLINESCORE5' and 'C' not in self.game.gameData['optionJumpers']:
						pass
					else:
						blank_type = 0

				high_nibble = self.tempClockDict['periodClock'][high_nibble_name]  # int

			elif high_nibble_name == 'delayOfGameClock_secondsTens':
				high_nibble = self.tempClockDict['delayOfGameClock'][high_nibble_name[17:]]  # int

				if high_nibble == 255 or high_nibble == 25:
					blank_type_high = True

			elif high_nibble_name == 'shotClock_secondsTens':
				high_nibble = self.tempClockDict['shotClock'][high_nibble_name[10:]]  # int

				if high_nibble == 255 or high_nibble == 25:
					blank_type_high = True

			elif high_nibble_name == 'timeOutTimer_secondsTens' or high_nibble_name == 'timeOutTimer_minutesTens':
				high_nibble = self.tempClockDict['timeOutTimer'][high_nibble_name[13:]]  # int

			elif high_nibble_name == 'segmentTimer_secondsTens' or high_nibble_name == 'segmentTimer_minutesTens':
				high_nibble = self.tempClockDict['segmentTimer'][high_nibble_name[13:]]  # int

			elif high_nibble_name == 'timeOfDayClock_hoursTens' or high_nibble_name == 'timeOfDayClock_minutesTens':
				high_nibble = self.tempClockDict['timeOfDayClock'][high_nibble_name[15:]]  # int

			elif high_nibble_name[:7] == 'penalty':
				timer_number = high_nibble_name[7]

				high_nibble_name = self._trim_penalty(high_nibble_name)

				team_string = high_nibble_name[:7]

				high_nibble_name = self._trim_team_name(high_nibble_name)

				if high_nibble_name[:6] == 'player':
					place = high_nibble_name[6:]
					team_high = self._team_extract(team_string)
					_flag_check_high = self._flag_check('timer'+timer_number+team_string+'playerFlag')

					high_nibble = self.game.get_team_data(team_high, 'TIMER' + timer_number + '_PLAYER_NUMBER' + place)  # int

					if high_nibble == 0 and _flag_check_high:
						blank_type = 0

					if high_nibble == 255 or high_nibble == 25:
						blank_type_high = True

				elif high_nibble_name[:5] == 'colon':
					team_high = self._team_extract(team_string)
					high_nibble = self.game.get_team_data(team_high, 'TIMER' + timer_number + '_COLON_INDICATOR')  # int

				else:
					high_nibble = self.tempClockDict['penalty'+timer_number+'_'+team_string][high_nibble_name]  # int

					if high_nibble == 255 or high_nibble == 25:
						blank_type_high = True

			elif self._team_value_check(high_nibble_name):
				high_nibble_name = self._trim_team_name(high_nibble_name)
				high_nibble = self.game.get_team_data(team_high, high_nibble_name)  # int

				if high_nibble == 255 or high_nibble == 25:
					blank_type_high = True

			else:
				high_nibble = self.game.get_game_data(high_nibble_name)  # int

				if high_nibble == 255 or high_nibble == 25:
					blank_type_high = True

				elif high_nibble == 0 and self.game.gameSettings['playerMatchGameFlag']:
					# Need to comment explicitly
					blank_type = 0

		# Low nibble
		blank_type_low = False
		if low_nibble_name != 0:
			team_low = self._team_extract(low_nibble_name)

			if self._period_clock_value_check(low_nibble_name):
				low_nibble = self.tempClockDict['periodClock'][low_nibble_name]  # int

			elif low_nibble_name == 'inningUnits':
				low_nibble = self.game.get_game_data(low_nibble_name)  # int

				if self.game.get_game_data('inningTens'):
					blank_type = 0

			elif low_nibble_name == 'singlePitchCountTens':
				low_nibble = self.game.get_game_data(low_nibble_name)  # int

				if self.game.get_game_data('singlePitchCountHundreds'):
					blank_type = 0

			elif low_nibble_name == 'pitchSpeedUnits':
				low_nibble = self.game.get_game_data(low_nibble_name)  # int

				if self.game.get_game_data('pitchSpeedHundreds'):
					blank_type = 0

			elif low_nibble_name == 'delayOfGameClock_secondsUnits':
				low_nibble = self.tempClockDict['delayOfGameClock'][low_nibble_name[17:]]  # int

				if low_nibble == 255 or low_nibble == 25:
					blank_type_low = True

			elif low_nibble_name == 'shotClock_secondsUnits':
				low_nibble = self.tempClockDict['shotClock'][low_nibble_name[10:]]  # int

				if low_nibble == 255 or low_nibble == 25:
					blank_type_low = True

			elif (
					low_nibble_name == 'timeOutTimer_secondsUnits' or low_nibble_name == 'timeOutTimer_minutesUnits'
					or low_nibble_name == 'timeOutTimer_minutesTens'):
				low_nibble = self.tempClockDict['timeOutTimer'][low_nibble_name[13:]]  # int

			elif (
					low_nibble_name == 'segmentTimer_secondsUnits' or low_nibble_name == 'segmentTimer_minutesUnits'
					or low_nibble_name == 'segmentTimer_minutesTens'):
				low_nibble = self.tempClockDict['segmentTimer'][low_nibble_name[13:]]  # int

			elif (
					low_nibble_name == 'timeOfDayClock_hoursUnits' or low_nibble_name == 'timeOfDayClock_minutesUnits'
					or low_nibble_name == 'timeOfDayClock_hoursTens'):
				low_nibble = self.tempClockDict['timeOfDayClock'][low_nibble_name[15:]]  # int

			elif low_nibble_name[:7] == 'penalty':
				timer_number = low_nibble_name[7]

				low_nibble_name = self._trim_penalty(low_nibble_name)

				team_string = low_nibble_name[:7]

				low_nibble_name = self._trim_team_name(low_nibble_name)

				if low_nibble_name[:6] == 'player':
					place = low_nibble_name[6:]
					team_low = self._team_extract(team_string)
					_flag_check_low = self._flag_check('timer'+timer_number+team_string+'playerFlag')
					low_nibble = self.game.get_team_data(team_low, 'TIMER' + timer_number + '_PLAYER_NUMBER' + place)  # int

					if low_nibble == 0 and _flag_check_low:
						blank_type = 0

					if low_nibble == 255 or low_nibble == 25:
						blank_type_low = True

				elif low_nibble_name[:5] == 'colon':
					team_low = self._team_extract(team_string)
					low_nibble = self.game.get_team_data(team_low, 'TIMER' + timer_number + '_COLON_INDICATOR')  # int

				else:
					low_nibble = self.tempClockDict['penalty'+timer_number+'_'+team_string][low_nibble_name]  # int
					if low_nibble == 255 or low_nibble == 25:
						blank_type_low = True

			elif self._team_value_check(low_nibble_name):
				team_string = low_nibble_name[:7]
				low_nibble_name = self._trim_team_name(low_nibble_name)

				if low_nibble_name[:6] == 'player':
					team_low = self._team_extract(team_string)
					if team_low == self.game.guest:
						active_player_list = self.game.activeGuestPlayerList
					elif team_low == self.game.home:
						active_player_list = self.game.activeHomePlayerList
					else:
						active_player_list = []

					stat_number = low_nibble_name[6:-4]
					low_nibble = self.game.get_team_data(team_low, low_nibble_name)  # int

					active_index = self.game.statNumberList.index(stat_number)
					if active_index <= len(active_player_list):
						player_number = active_player_list[active_index-1]
						try:
							if player_number[0] == '0':
								blank_type = 0
						except:
							pass

					if low_nibble == 255 or low_nibble == 25:
						blank_type_low = True

				elif low_nibble_name == 'pitchCountTens':
					low_nibble = self.game.get_team_data(team_low, low_nibble_name)  # int

					if self.game.get_team_data(team_low, 'pitchCountHundreds'):
						blank_type = 0
				else:
					low_nibble = self.game.get_team_data(team_low, low_nibble_name)  # int

					if low_nibble == 255 or low_nibble == 25:
						blank_type_low = True
			else:
				low_nibble = self.game.get_game_data(low_nibble_name)  # int

				if low_nibble == 255 or low_nibble == 25:
					blank_type_low = True

		# Blanking dependent on 255 value
		if blank_type_high and blank_type_low:
			blank_type = 'AlwaysHighLow'
			high_nibble = 0
			low_nibble = 0
		elif blank_type_high:
			blank_type = 'AlwaysHigh'
			high_nibble = 0
		elif blank_type_low:
			blank_type = 'AlwaysLow'
			low_nibble = 0

		if self.verbose or 0:
			print (
				'\n_nibble_format(after) - high_nibble, low_nibble, blank_type, word, addr_word_number -- \n',
				high_nibble, low_nibble, blank_type, word, addr_word_number)
		return high_nibble, low_nibble, blank_type

	def _flag_check(self, var_name):
		if self.game.gameSettings[var_name]:
			_flag_check = 1
		else:
			_flag_check = 0
		return _flag_check

	def _segment_data_format(self, segment_data):
		# Format data - segment_data

		if segment_data == '' or segment_data == '0':
			segment_data = 0
		elif segment_data == 'BSO':
			segment_data = self._bso_decode()
		elif segment_data == 'Down_Quarter':
			segment_data = self.__down_quarter_decode()
		elif segment_data == 'fQtr4_gDec':
			segment_data = ''
			if self.game.get_game_data('decimalIndicator'):
				segment_data = 'g'
			if self.game.gameData['sportType'] == 'soccer':
				value = 'period'
			else:
				value = 'quarter'
			if self.game.get_game_data(value) >= 4:
				segment_data += 'f'
		elif segment_data == 'gDec':
			if self.game.get_game_data('decimalIndicator'):
				segment_data = 'g'
			else:
				segment_data = ''
		elif segment_data == 'f_hitIndicator':
			if self.game.get_game_data('hitIndicator'):
				segment_data = 'f'
			else:
				segment_data = ''
		elif segment_data == 'abcBall_efStrike':
			segment_data = ''
			balls = self.game.get_game_data('balls')
			strikes = self.game.get_game_data('strikes')
			if balls == 0:
				pass
			elif balls == 1:
				segment_data = 'a'
			elif balls == 2:
				segment_data = 'ab'
			elif balls >= 3:
				segment_data = 'abc'
			if strikes == 0:
				pass
			elif strikes == 1:
				segment_data += 'e'
			elif strikes >= 2:
				segment_data += 'ef'
		elif segment_data == 'bc_strike':
			segment_data = ''
			strikes = self.game.get_game_data('strikes')
			if strikes == 0:
				pass
			elif strikes == 1:
				segment_data += 'b'
			elif strikes >= 2:
				segment_data += 'bc'
		elif segment_data == 'abcBall_deOut_gDec':
			segment_data = ''
			balls = self.game.get_game_data('balls')
			outs = self.game.get_game_data('outs')
			if balls == 0:
				pass
			elif balls == 1:
				segment_data = 'a'
			elif balls == 2:
				segment_data = 'ab'
			elif balls >= 3:
				segment_data = 'abc'
			if outs == 0:
				pass
			elif outs == 1:
				segment_data += 'd'
			elif outs >= 2:
				segment_data += 'de'
			if self.game.get_game_data('decimalIndicator'):
				segment_data += 'g'
		elif segment_data == 'aGeHposs_fQrt4_gDec':
			segment_data = ''
			if self.game.get_team_data(self.game.guest, 'possession'):
				segment_data = 'a'
			if self.game.get_team_data(self.game.home, 'possession'):
				segment_data += 'e'
			if self.game.get_game_data('decimalIndicator'):
				segment_data += 'g'
			if self.game.get_game_data('quarter') >= 4:
				segment_data += 'f'
		elif segment_data == 'abcde_PossBonus':
			segment_data = ''
			if self.game.get_team_data(self.game.home, 'possession'):
				segment_data = 'a'
			if self.game.get_team_data(self.game.guest, 'possession'):
				segment_data += 'b'
			home_bonus = self.game.get_team_data(self.game.home, 'bonus')
			guest_bonus = self.game.get_team_data(self.game.guest, 'bonus')
			if home_bonus == 0:
				pass
			if home_bonus == 1:
				segment_data += 'c'
			if home_bonus >= 2:
				segment_data += 'ce'
			if guest_bonus == 0:
				pass
			if guest_bonus >= 1:
				segment_data += 'd'
		elif segment_data == 'home_ace_PossBonus':
			segment_data = ''
			if self.game.get_team_data(self.game.home, 'possession'):
				segment_data = 'a'
			home_bonus = self.game.get_team_data(self.game.home, 'bonus')
			if home_bonus == 0:
				pass
			if home_bonus == 1:
				segment_data += 'c'
			if home_bonus >= 2:
				segment_data += 'ce'
		elif segment_data == 'guest_ace_PossBonus':
			segment_data = ''
			if self.game.get_team_data(self.game.guest, 'possession'):
				segment_data = 'a'
			guest_bonus = self.game.get_team_data(self.game.guest, 'bonus')
			if guest_bonus == 0:
				pass
			if guest_bonus == 1:
				segment_data += 'c'
			if guest_bonus >= 2:
				segment_data += 'ce'
		elif segment_data == 'period_efg':
			segment_data = ''
			period = self.game.get_game_data('period')
			if period == 0:
				pass
			elif period == 1:
				segment_data += 'e'
			elif period == 2:
				segment_data += 'ef'
			elif period == 3:
				segment_data += 'efg'
			elif period >= 4:
				segment_data += 'efg'
		elif segment_data == 'bc_detect':
			segment_data = 0
		else:
			print 'Address Map spreadsheet has a segment data value not handled yet'

		if segment_data == '':
			segment_data = None
		return segment_data

	# Segment Decode Functions
	def _bso_decode(self):
		segment_data = ''
		balls = self.game.get_game_data('balls')
		strikes = self.game.get_game_data('strikes')
		outs = self.game.get_game_data('outs')
		if balls == 0:
			pass
		elif balls == 1:
			segment_data = 'a'
		elif balls == 2:
			segment_data = 'ab'
		elif balls >= 3:
			segment_data = 'abc'
		if strikes == 0:
			pass
		elif strikes == 1:
			segment_data += 'd'
		elif strikes >= 2:
			segment_data += 'de'
		if outs == 0:
			pass
		elif outs == 1:
			segment_data += 'f'
		elif outs >= 2:
			segment_data += 'fg'
		return segment_data

	def __down_quarter_decode(self):
		segment_data = ''
		down = self.game.get_game_data('down')
		quarter = self.game.get_game_data('quarter')
		if down == 0:
			pass
		elif down == 1:
			segment_data = 'a'
		elif down == 2:
			segment_data = 'ab'
		elif down == 3:
			segment_data = 'abc'
		elif down >= 4:
			segment_data = 'abcd'
		if quarter == 0:
			pass
		elif quarter == 1:
			segment_data += 'e'
		elif quarter == 2:
			segment_data += 'ef'
		elif quarter == 3:
			segment_data += 'efg'
		elif quarter >= 4:
			segment_data += 'efg'
		return segment_data

	# Segment Decode Functions End
	# Formatting Functions End

	# map() END-------------------------------------------------------

	def un_map(self, word_list):  # MP Data decoded and stored in Game Object
		"""
		Decodes words in the word_list and saves them to the game object based on sport.
		"""
		# PUBLIC method
		if self.verbose:
			print '--------------word_list---------------', word_list

		address_word_list = self._select_address_word_list()

		# Update game data with word list
		for element in word_list:
			group, bank, word, i_bit, numeric_data = self.mp.decode(element)
			addr = self.mp.gbw_to_mp_address(group, bank, word) + 1
			decode_data = addr, group, bank, word, i_bit, numeric_data
			if self.verbose:
				print '\naddr:', addr, group, bank, word, 'I:', i_bit, 'Data:', numeric_data, bin(numeric_data)

			if self._tunnel_check(word, numeric_data):
				if self.verbose:
					print 'tunnel_check True'
				# Tunneling data
				app.utils.functions.verbose(['word', word], self.verboseTunnel)
				if word == 1:
					if numeric_data == 0xbc:
						app.utils.functions.verbose(['Quantum dimming tunnel open!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel = 1
					elif numeric_data == 0xad:
						app.utils.functions.verbose(['Quantum ETN tunnel open!!!!'], self.verboseTunnel)
						self.quantumETNTunnel = 1

			elif self.quantumDimmingTunnel or self.quantumETNTunnel:
				if self.verbose:
					print 'self.quantumDimmingTunnel or self.quantumETNTunnel'
				app.utils.functions.verbose(['word', word], self.verboseTunnel)
				if word == 1:
					if not (0xaa <= numeric_data < 0xf0):
						app.utils.functions.verbose(['Quantum data tunnel closed!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel = 0
						self.quantumETNTunnel = 0

				elif word == 2:
					app.utils.functions.verbose(['numeric_data', numeric_data], self.verboseTunnel)
					if self.quantumDimmingTunnel:
						self.brightness = (numeric_data & 0x0f) + ((numeric_data & 0xf0) >> 4)*10
					elif self.quantumETNTunnel:
						if numeric_data >= 64:
							# Trim Team bit
							numeric_data -= 64

							self.quantumETNTunnelTeam = self.game.home
						else:
							self.quantumETNTunnelTeam = self.game.guest

							app.utils.functions.verbose(['self.quantumETNTunnelTeam =', self.quantumETNTunnelTeam], self.verboseTunnel)

						if numeric_data:
							# Address pair
							self.fontJustifyControl = 0
							app.utils.functions.verbose(['address pair', numeric_data], self.verboseTunnel)
							self.addressPair = numeric_data
						else:
							# Control for font-justify either team because of trimming
							self.fontJustifyControl = 1

				elif word == 3:
					if self.quantumETNTunnel and not self.fontJustifyControl:
						self.leftETNByte = numeric_data
						app.utils.functions.verbose(['leftETNByte', numeric_data], self.verboseTunnel)

				elif word == 4:
					if self.quantumETNTunnel and self.fontJustifyControl:
						font = numeric_data/6+1
						justify = numeric_data % 6+1

						self.game.set_team_data(self.quantumETNTunnelTeam, 'font', font, 1)
						self.game.set_team_data(self.quantumETNTunnelTeam, 'justify', justify, 1)
						app.utils.functions.verbose(['font', font, 'justify', justify], self.verboseTunnel)

						app.utils.functions.verbose(['Quantum data tunnel closed!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel = 0
						self.quantumETNTunnel = 0
						self.quantumETNTunnelFontJustifyProcessed = True

					elif self.quantumETNTunnel:
						self.rightETNByte = numeric_data
						app.utils.functions.verbose(['rightETNByte', numeric_data], self.verboseTunnel)
						if self.leftETNByte and self.rightETNByte:
							name = self.game.get_team_data(
								self.quantumETNTunnelTeam, 'name'
							)[:(self.addressPair-1)*2]+chr(self.leftETNByte)+chr(self.rightETNByte)
						elif self.leftETNByte:
							name = self.game.get_team_data(
								self.quantumETNTunnelTeam, 'name'
							)[:(self.addressPair-1)*2]+chr(self.leftETNByte)
						elif self.rightETNByte:
							app.utils.functions.verbose([
								'ERROR - should not send 0 in word 3 and something in word 4',
								self.leftETNByte and self.rightETNByte], self.verboseTunnel)
							name = ''
						else:
							name = self.game.get_team_data(self.quantumETNTunnelTeam, 'name')

						self.game.set_team_data(self.quantumETNTunnelTeam, 'name', name, 1)
						app.utils.functions.verbose(['name-', name, '-'], self.verboseTunnel)

						app.utils.functions.verbose(['Quantum data tunnel closed!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel = 0
						self.quantumETNTunnel = 0
						self.quantumETNTunnelNameProcessed = True

			else:
				# Normal data
				if self.verbose:
					print 'normal un_map'
				if addr in address_word_list:
					# Handle persistent alt selection
					alt = 1
					base1_or_base3 = self.game.gameData['sport'] == 'MPBASEBALL1' or self.game.gameData['sport'] == 'MMBASEBALL3'
					multi_base_or_3450_base_c_jumper = (
							self.game.gameData['sport'] == 'MPMULTISPORT1-baseball'
							or self.game.gameData['sport'] == 'MPLX3450-baseball'
							and 'C' in self.game.gameData['optionJumpers'])
					line5_and_c_jumper = self.game.gameData['sport'] == 'MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']

					if (
							not base1_or_base3 and not line5_and_c_jumper and not multi_base_or_3450_base_c_jumper
							and (addr == 21 or addr == 22)):
						if self.periodClockUnMapDict['colonIndicator'] == 0 or self.tenthsTransitionFlag:
							alt = 2
					elif line5_and_c_jumper or multi_base_or_3450_base_c_jumper:
						if addr == 21 and self.tenthsTransitionFlag:
							alt = 2
					elif (
							addr == 18
							and (
									self.game.gameData['sport'] == 'MPFOOTBALL1'
									or self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer'
									or self.game.gameData['sport'] == 'MPSOCCER_LX1-football')
							and 'E' in self.game.gameData['optionJumpers']
					):
						alt = 2
					elif self.game.gameData['sport'] == 'MPLINESCORE5':
						if 'D' in self.game.gameData['optionJumpers'] and 'B' in self.game.gameData['optionJumpers']:
							if addr == 14 or addr == 15 or addr == 16 or addr == 31 or addr == 32:
								alt = 2
							elif addr == 5 or addr == 7:
								alt = 2
						elif 'D' in self.game.gameData['optionJumpers']:
							if addr == 14 or addr == 15 or addr == 16 or addr == 31 or addr == 32:
								alt = 2
						elif 'B' in self.game.gameData['optionJumpers']:
							if addr == 31 or addr == 32:
								alt = 3
							elif addr == 5 or addr == 7:
								alt = 2
						else:
							pass
					elif base1_or_base3:
						if 'C' in self.game.gameData['optionJumpers']:
							if addr == 21 or addr == 22:
								alt = 2

					if self.verbose:
						print 'alt', alt

					# Shift address for stat home team
					if self.statFlag:
						if i_bit:
							addr = addr+32

					# Get the current variable names for all bits
					data_names = self._get_dict_info(addr, alt=alt)

					# Save values if checks are passed
					self._save_data(decode_data, data_names)

		self._multisport_state_check()

	def _select_address_word_list(self):
		# Create address word list to target one address for each data type or allow passed value

		# sportList = [
		# 'MMBASEBALL3', 'MPBASEBALL1', 'MMBASEBALL4', 'MPLINESCORE4', 'MPLINESCORE5', 'MPMP-15X1', 'MPMP-14X1',
		# 'MPMULTISPORT1-baseball', 'MPMULTISPORT1-football', 'MPFOOTBALL1', 'MMFOOTBALL4', 'MPBASKETBALL1',
		# 'MPSOCCER_LX1-soccer', 'MPSOCCER_LX1-football', 'MPSOCCER1', 'MPHOCKEY_LX1', 'MPHOCKEY1', 'MPCRICKET1',
		# 'MPRACETRACK1', 'MPLX3450-baseball', 'MPLX3450-football', 'MPGENERIC', 'MPSTAT']

		if self.game.gameData['sport'] == 'MPBASKETBALL1':
			address_word_list = [5, 13, 14, 15, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
		elif self.game.gameData['sport'] == 'MPFOOTBALL1' or self.game.gameData['sport'] == 'MMFOOTBALL4':
			address_word_list = [5, 19, 20, 21, 22, 24, 25, 26, 29, 30, 31, 32]
			if 'E' in self.game.gameData['optionJumpers']:
				address_word_list.append(18)
		elif self.game.gameData['sport'] == 'MPHOCKEY_LX1':
			address_word_list = [
				1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
		elif self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer':
			address_word_list = [5, 9, 10, 13, 14, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31]
		elif self.game.gameData['sport'] == 'MPSOCCER_LX1-football':
			address_word_list = [5, 13, 18, 19, 20, 21, 22, 24, 25, 26, 29, 30, 32]
		elif self.game.gameData['sport'] == 'MPLINESCORE5':
			address_word_list = [
				1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
				17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
		elif self.game.gameData['sport'] == 'MPBASEBALL1' or self.game.gameData['sport'] == 'MMBASEBALL3':
			address_word_list = [5, 6, 7, 13, 14, 15, 16, 17, 18, 21, 22, 23, 24]
		elif self.game.gameData['sport'] == 'MMBASEBALL4':
			address_word_list = [9, 10, 11, 13, 14, 15, 21, 22, 23]
		elif self.game.gameData['sport'] == 'MPMULTISPORT1-baseball':
			address_word_list = [5, 9, 11, 10, 13, 14, 15, 16, 17, 18, 21, 22, 24, 29, 30, 31, 32, 12]
		elif self.game.gameData['sport'] == 'MPMULTISPORT1-football':
			address_word_list = [5, 9, 10, 19, 20, 21, 22, 24, 29, 30, 31, 11, 12]
		elif self.game.gameData['sport'] == 'MPLX3450-baseball':
			address_word_list = [5, 9, 11, 10, 13, 14, 15, 16, 17, 18, 21, 22, 24, 29, 30, 31, 32, 12]
		elif self.game.gameData['sport'] == 'MPLX3450-football':
			address_word_list = [5, 9, 10, 19, 20, 21, 22, 24, 29, 30, 31, 11, 12]
		elif self.statFlag:
			address_word_list = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23]
		else:
			address_word_list = []
		return address_word_list

	def _multisport_state_check(self):
		mp_multisport1 = (
				self.game.gameData['sport'] == 'MPMULTISPORT1-baseball'
				or self.game.gameData['sport'] == 'MPMULTISPORT1-football')
		mp_lx3450 = (
				self.game.gameData['sport'] == 'MPLX3450-baseball'
				or self.game.gameData['sport'] == 'MPLX3450-football')
		mp_soccer_lx1 = (
				self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer'
				or self.game.gameData['sport'] == 'MPSOCCER_LX1-football')
		multisport_type = mp_multisport1 or mp_lx3450 or mp_soccer_lx1

		if multisport_type:
			# If correct sports only check for reset state every second
			if self.multisportChangeSportCount < 10:
				self.multisportChangeSportCount += 1
			else:
				self.multisportChangeSportCount = 0
				change_flag = False
				sport = self.game.gameData['sport']

				# Select values to compare
				if mp_multisport1:
					if self.game.gameData['sport'] == 'MPMULTISPORT1-baseball':
						# Baseball
						if self.game.gameData['segmentQuarterFlag']:
							change_flag = True
						sport = 'MPMULTISPORT1-football'

					else:
						# Football
						if self.game.teamsDict['TEAM_2'].teamData['timeOutsLeft'] == 16:
							change_flag = True
						sport = 'MPMULTISPORT1-baseball'

				elif mp_lx3450:
					if self.game.gameData['sport'] == 'MPLX3450-baseball':
						# Baseball
						if self.game.gameData['segmentQuarterFlag']:
							change_flag = True
						sport = 'MPLX3450-football'

					else:
						# Football
						if self.game.teamsDict['TEAM_2'].teamData['timeOutsLeft'] == 16:
							change_flag = True
						sport = 'MPLX3450-baseball'

				elif mp_soccer_lx1:
					if self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer':
						# Soccer
						if self.game.gameData['bcDetectFlag']:
							change_flag = True
						sport = 'MPSOCCER_LX1-football'

					else:
						# Football
						if self.game.gameData['down'] == 0:
							change_flag = True
						sport = 'MPSOCCER_LX1-soccer'

				# Check for multisport reset state
				if change_flag:

					# Change sport
					from config_default_settings import Config
					c = Config()
					c.write_sport(sport)

					# Tell console to reset
					self.game.gameSettings['resetGameFlag'] = True

	@staticmethod
	def _tunnel_check(word, numeric_data):
		high_data = (numeric_data & 0xf0) >> 4
		low_data = numeric_data & 0x0f
		if word == 1 and ((low_data >= 0xa and low_data != 0xf) or (high_data >= 0xa and high_data != 0xf)):
			return 1
		return 0

	def _get_dict_info(self, addr, alt=1):
		i_bit = self.fullAddressMapDict[addr][alt]['I_BIT']
		h_bit = self.fullAddressMapDict[addr][alt]['H_BIT']
		low_nibble = self.fullAddressMapDict[addr][alt]['LOW_NIBBLE']
		high_nibble = self.fullAddressMapDict[addr][alt]['HIGH_NIBBLE']
		segment_data = self.fullAddressMapDict[addr][alt]['SEGMENT_DATA']
		return i_bit, h_bit, high_nibble, low_nibble, segment_data

	def _save_data(self, decode_data, data_names):
		addr, group, bank, word, i_bit, numeric_data = decode_data
		i_bit_name, h_bit_name, high_nibble_name, low_nibble_name, segment_data = data_names
		if not self.statFlag and (word == 3 or word == 4):
			# Word 3 and 4 Section

			high_data = 0
			low_data = numeric_data & 0x7f
			low_data = self.mp.numeric_data_decode(low_data)
			h_bit = (numeric_data & 0x80) >> 7
			if segment_data == '':
				h_bit_team = self._team_extract(h_bit_name)
				i_bit_team = self._team_extract(i_bit_name)
				low_nibble_team = self._team_extract(low_nibble_name)

				data_names = self._check_period_clock_state(decode_data, data_names, high_data, low_data, h_bit=h_bit)
				i_bit_name, h_bit_name, high_nibble_name, low_nibble_name, segment_data = data_names

				self._set_period_clock_un_map_dict(i_bit_name, i_bit)
				self._set_period_clock_un_map_dict(h_bit_name, h_bit)
				self._set_period_clock_un_map_dict(low_nibble_name, low_data)

				# Special cases not to save I Bit --------------------
				if 0:
					# Don't save duplicates
					pass
				else:
					self._set_data(i_bit_name, i_bit, i_bit_team)
					if self.verbose:
						print 'i_bit_name', i_bit_name, 'saved'

				# Special cases not to save H Bit --------------------
				hockey_27_28 = (addr == 27 or addr == 28) and self.game.gameData['sport'] == 'MPHOCKEY_LX1'
				soc_soc_32 = addr == 32 and self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer'
				bb4_11 = addr == 11 and self.game.gameData['sport'] == 'MMBASEBALL4'

				if hockey_27_28 or bb4_11 or soc_soc_32:
					# Don't save duplicates
					pass
				else:
					self._set_data(h_bit_name, h_bit, h_bit_team)
					if self.verbose:
						print 'h_bit_name', h_bit_name, 'saved'

				# Special cases not to save High Nibble -------------------
				# Not used

				# Special cases not to save Low Nibble --------------------
				self._set_data(low_nibble_name, low_data, low_nibble_team)
				if self.verbose:
					print 'low_nibble_name', low_nibble_name, 'saved'

				if self.verbose:
					print (
						'addr', addr, 'i_bit_team', i_bit_team, 'i_bit_name', i_bit_name, i_bit,
						'h_bit_team', h_bit_team, 'h_bit_name', h_bit_name, h_bit)
					print (
						'low_nibble_team', low_nibble_team, 'low_nibble_name', low_nibble_name, low_data)
			else:
				# Decode segment data's storage value
				if self.verbose:
					print 'segment_data', segment_data
				h_bit_team = self._team_extract(h_bit_name)

				data_names = self._check_period_clock_state(decode_data, data_names, high_data, low_data, h_bit=h_bit)
				i_bit_name, h_bit_name, high_nibble_name, low_nibble_name, segment_data = data_names

				self._set_period_clock_un_map_dict(h_bit_name, h_bit)

				# Special cases not to save H Bit --------------------
				soc_soc_31 = addr == 31 and self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer'
				if soc_soc_31:
					# Don't save duplicates
					pass
				else:
					self._set_data(h_bit_name, h_bit, h_bit_team)
					if self.verbose:
						print 'h_bit_name', h_bit_name, 'saved'

				# Area for all custom decoding, try to use data from a better location if possible
				if self.game.gameData['sportType'] == 'basketball':
					if segment_data == 'home_ace_PossBonus':
						if self.verbose:
							print bin(numeric_data), bin(0b00010000 & numeric_data), 0b00000001 & numeric_data
						if 0b00000001 & numeric_data:
							self._set_data('teamTwoPossession', True, self.game.home)
						elif 0b00000001 & numeric_data == 0:
							self._set_data('teamTwoPossession', False, self.game.home)
						if 0b00010000 & numeric_data:
							self._set_data('teamTwoBonus', 2, self.game.home)
						elif 0b00000100 & numeric_data:
							self._set_data('teamTwoBonus', 1, self.game.home)
						elif 0b00010000 & numeric_data == 0 or 0b00000100 & numeric_data == 0:
							self._set_data('teamTwoBonus', 0, self.game.home)
					if segment_data == 'guest_ace_PossBonus':
						if self.verbose:
							print bin(numeric_data), 0b00000000 & numeric_data, 0b00000001 & numeric_data
						if 0b00000001 & numeric_data:
							self._set_data('teamOnePossession', True, self.game.guest)
						elif 0b00000000 & numeric_data == 0:
							self._set_data('teamOnePossession', False, self.game.guest)
						if 0b00010000 & numeric_data:
							self._set_data('teamOneBonus', 2, self.game.guest)
						elif 0b00000100 & numeric_data:
							self._set_data('teamOneBonus', 1, self.game.guest)
						elif 0b00010000 & numeric_data == 0 or 0b00000100 & numeric_data == 0:
							self._set_data('teamOneBonus', 0, self.game.guest)
				elif self.game.gameData['sport'] == 'MPMULTISPORT1-football' or self.game.gameData['sport'] == 'MPLX3450-football':
					if segment_data == 'Down_Quarter':
						if 0b00010000 & numeric_data:
							self.game.gameData['segmentQuarterFlag'] = True
						elif 0b00010000 & numeric_data == 0:
							self.game.gameData['segmentQuarterFlag'] = False
				elif self.game.gameData['sport'] == 'MPMULTISPORT1-baseball' or self.game.gameData['sport'] == 'MPLX3450-baseball':
					if segment_data == 'bc_strike':
						if 0b00010000 & numeric_data:
							self.game.gameData['segmentQuarterFlag'] = True
						elif 0b00010000 & numeric_data == 0:
							self.game.gameData['segmentQuarterFlag'] = False
				elif self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer':
					if segment_data == 'bc_detect':
						if 0b00000110 & numeric_data:
							self.game.gameData['bcDetectFlag'] = True
						elif 0b00000110 & numeric_data == 0:
							self.game.gameData['bcDetectFlag'] = False

		else:
			# Word 1 and 2 Section

			high_data = (numeric_data & 0xf0) >> 4
			low_data = numeric_data & 0x0f

			i_bit_team = self._team_extract(i_bit_name)
			high_nibble_team = self._team_extract(high_nibble_name)
			low_nibble_team = self._team_extract(low_nibble_name)

			data_names = self._check_period_clock_state(decode_data, data_names, high_data, low_data)
			i_bit_name, h_bit_name, high_nibble_name, low_nibble_name, segment_data = data_names

			self._set_period_clock_un_map_dict(i_bit_name, i_bit)
			self._set_period_clock_un_map_dict(high_nibble_name, high_data)
			self._set_period_clock_un_map_dict(low_nibble_name, low_data)

			# Special cases not to save I Bit --------------------
			soc_soc_18 = addr == 18 and self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer'
			multibase3450base = (
					self.game.gameData['sport'] == 'MPMULTISPORT1-baseball'
					or self.game.gameData['sport'] == 'MPLX3450-baseball')
			line5_17_18 = (addr == 17 or addr == 18) and self.game.gameData['sport'] == 'MPLINESCORE5'

			base1_or_base3 = self.game.gameData['sport'] == 'MPBASEBALL1' or self.game.gameData['sport'] == 'MMBASEBALL3'
			_13or14 = addr == 13 or addr == 14
			# Together
			bb13_and_13_14 = base1_or_base3 and _13or14
			bb134_and_13_14 = (base1_or_base3 or self.game.gameData['sport'] == 'MMBASEBALL4') and _13or14
			multibase3450base_and_13_14 = multibase3450base and _13or14

			if soc_soc_18 or line5_17_18 or bb13_and_13_14:
				# Don't save duplicates
				pass
			else:
				self._set_data(i_bit_name, i_bit, i_bit_team)
				if self.verbose:
					print 'i_bit_name', i_bit_name, 'saved'

			# Special cases not to save High Nibble ----------------
			soc_soc_18 = addr == 18 and self.game.gameData['sport'] == 'MPSOCCER_LX1-soccer'
			not_e_jumper = not('E' in self.game.gameData['optionJumpers'])
			# Together
			soc_soc_18_and_not_e_jumper = soc_soc_18 and not_e_jumper

			if soc_soc_18_and_not_e_jumper:
				# Don't save duplicates
				pass
			else:
				self._set_data(high_nibble_name, high_data, high_nibble_team)
				if self.verbose:
					print 'high_nibble_name', high_nibble_name, 'saved'

			# Special cases not to save Low Nibble ------------------
			# soc_soc_18_and_not_e_jumper is above
			# bb134_and_13_14 is above
			if soc_soc_18_and_not_e_jumper or bb134_and_13_14 or multibase3450base_and_13_14:
				# Don't save duplicates
				pass
			else:
				self._set_data(low_nibble_name, low_data, low_nibble_team)
				if self.verbose:
					print 'low_nibble_name', low_nibble_name, 'saved'

			if self.verbose:
				print 'addr', addr, 'i_bit_team', i_bit_team, 'i_bit_name', i_bit_name, i_bit
				print (
					'high_nibble_team', high_nibble_team, 'high_nibble_name', high_nibble_name, high_data,
					'low_nibble_team', low_nibble_team, 'low_nibble_name', low_nibble_name, low_data)

	def _set_period_clock_un_map_dict(self, name, value):
		if name in self.periodClockUnMapDict:
			self.periodClockUnMapDict[name] = value

	def _check_period_clock_state(self, decode_data, data_names, high_data, low_data, h_bit=None):
		addr, group, bank, word, i_bit, numeric_data = decode_data
		i_bit_name, h_bit_name, high_nibble_name, low_nibble_name, segment_data = data_names
		line5_and_c_jumper = self.game.gameData['sport'] == 'MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']
		multibase_or_3450base_c_jumper = (
				(
						self.game.gameData['sport'] == 'MPMULTISPORT1-baseball'
						or self.game.gameData['sport'] == 'MPLX3450-baseball'
				) and 'C' in self.game.gameData['optionJumpers'])

		# Minutes received
		if high_nibble_name == 'minutesTens':
			pass

		# Seconds received
		elif high_nibble_name == 'secondsTens':
			if (
					low_data == 15
					or (self.periodClockUnMapDict['secondsTens'] == 0 and self.periodClockUnMapDict['secondsUnits'] == 0
						and high_data >= 6 and low_data == 0)
			):
				self.tenthsTransitionFlag = True
				data_names = self._get_dict_info(addr, alt=2)
				self._set_data('minutesTens', 0)
				self._set_data('minutesUnits', 0)
				if self.verbose:
					print 'self.tenthsTransitionFlag=True and set minutes to zero'
					print '\naddr', addr, 'i_bit_name', i_bit_name, i_bit, 'h_bit_name', h_bit_name, h_bit
					print 'high_nibble_name', high_nibble_name, high_data, 'low_nibble_name', low_nibble_name, low_data

			elif (
					(line5_and_c_jumper or multibase_or_3450base_c_jumper)
					and (0 <= low_data < 10) and self.tenthsTransitionFlag
			):
				self.tenthsTransitionFlag = False
				self._set_data('tenthsUnits', 0)
				if self.verbose:
					print 'self.tenthsTransitionFlag=False and set tenthsUnits to zero'
					print '\naddr', addr, 'i_bit_name', i_bit_name, i_bit, 'h_bit_name', h_bit_name, h_bit
					print 'high_nibble_name', high_nibble_name, high_data, 'low_nibble_name', low_nibble_name, low_data

		# Tenths received
		elif high_nibble_name == 'tenthsUnits':
			pass

		# Colon received
		elif h_bit_name == 'colonIndicator':
			if self.periodClockUnMapDict['colonIndicator'] == 0 and h_bit == 1:
				self.tenthsTransitionFlag = False
				self._set_data('tenthsUnits', 0)
				if self.verbose:
					print 'self.tenthsTransitionFlag=False and set tenthsUnits to zero'
					print '\naddr', addr, 'i_bit_name', i_bit_name, i_bit, 'h_bit_name', h_bit_name, h_bit
					print 'high_nibble_name', high_nibble_name, high_data, 'low_nibble_name', low_nibble_name, low_data

		return data_names

	def _set_data(self, name, value, team=None):
		if self._game_value_check(name):
			self.game.set_game_data(name, value, places=1)

		elif self._team_value_check(name):
			if name[:7] == 'penalty' and self.game.gameData['sport'] == 'MPHOCKEY_LX1':
				timer_number = name[7]
				name = self._trim_penalty(name)
				team_string = name[:7]
				name = self._trim_team_name(name)
				if name[:6] == 'player':
					place = name[6:]
					self.game.set_team_data(team, 'TIMER' + timer_number + '_PLAYER_NUMBER' + place, value, places=1)
				elif name[:5] == 'colon':
					if self.verbose:
						print 'skip penalty timer colons'
				else:
					clock_name = 'penalty'+str(timer_number)+'_'+team_string+'_'+name
					if self.verbose:
						print clock_name
					self.game.set_game_data(clock_name, value, places=1)
			else:
				name = self._trim_team_name(name)
				self.game.set_team_data(team, name, value, places=1)
		elif self._period_clock_value_check(name):
			self.game.set_game_data('periodClock_' + name, value, places=1)

		else:
			print 'FAIL'


class LamptestMapping(AddressMapping):
	"""Map of all non-horn segments on per the sport."""
	def __init__(self, game=None):
		super(LamptestMapping, self).__init__(game=game)

		if self.statFlag:
			for k in range(2):
				for i in range(2):
					for j in range(4):
						self.wordsDict[((i*4+j)*4+1)+k*32] = self.mp.encode(i + 1, j + 1, 1, k, 0, 8, 8, 0, 0, True)
						self.wordsDict[((i*4+j)*4+2)+k*32] = self.mp.encode(i + 1, j + 1, 2, k, 0, 8, 8, 0, 0, True)
						self.wordsDict[((i*4+j)*4+3)+k*32] = self.mp.encode(i + 1, j + 1, 3, k, 0, 8, 8, 0, 0, True)
						self.wordsDict[((i*4+j)*4+4)+k*32] = self.mp.encode(i + 1, j + 1, 4, k, 0, 0, 0, 0, 0, True)
		else:
			for i in range(2):
				for j in range(4):
					self.wordsDict[(i*4+j)*4+1] = self.mp.encode(
						i + 1, j + 1, 1, 1, 1, 8, 8, 0, 0)  # 0x58 is 88 in decimal for lamp test
					self.wordsDict[(i*4+j)*4+2] = self.mp.encode(i + 1, j + 1, 2, 1, 1, 8, 8, 0, 0)
					self.wordsDict[(i*4+j)*4+3] = self.mp.encode(i + 1, j + 1, 3, 1, 1, 0, 8, 0, 0)
					self.wordsDict[(i*4+j)*4+4] = self.mp.encode(i + 1, j + 1, 4, 1, 1, 0, 8, 0, 0)

		self._adjust_all_banks()

	def _blank_map(self):
		pass

	def _build_addr_map(self):
		pass

	def _adjust_all_banks(self):
		# Sets all non-horn segments on per the sport.

		if self.sport == 'MPBASEBALL1' or self.sport == 'MMBASEBALL3' or self.sport == 'MPLINESCORE5':
			self.wordsDict[1] = self.mp.encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[2] = self.mp.encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[8] = self.mp.encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport == 'MPLINESCORE4':
			self.wordsDict[4] = self.mp.encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[8] = self.mp.encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[24] = self.mp.encode(2, 2, 4, 1, 0, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport == 'MPMP_15X1' or self.sport == 'MPMP_14X1':
			self.wordsDict[1] = self.mp.encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[2] = self.mp.encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[8] = self.mp.encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[24] = self.mp.encode(2, 2, 4, 1, 0, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif (
				self.sport == 'MPMULTISPORT1-football' or self.sport == 'MPLX3450-football'
				or self.sport == 'MPMULTISPORT1-baseball' or self.sport == 'MPLX3450-baseball'
		):
			if self.sport == 'MPLX3450-football' or self.sport == 'MPLX3450-baseball':
				self.wordsDict[1] = self.mp.encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			else:
				self.wordsDict[2] = self.mp.encode(1, 1, 2, 0, 1, 8, 8, 0, 0)

			self.wordsDict[5] = self.mp.encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[6] = self.mp.encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[8] = self.mp.encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif (
				self.sport == 'MPFOOTBALL1' or self.sport == 'MMFOOTBALL4'
				or self.sport == 'MMBASEBALL4'or self.sport == 'MPBASKETBALL1'
		):
			self.wordsDict[1] = self.mp.encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[2] = self.mp.encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[5] = self.mp.encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[6] = self.mp.encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			if not self.sport == 'MPBASKETBALL1':
				self.wordsDict[8] = self.mp.encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport == 'MPHOCKEY_LX1':
			self.wordsDict[1] = self.mp.encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[5] = self.mp.encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[6] = self.mp.encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[12] = self.mp.encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.encode(2, 2, 1, 0, 1, 8, 8, 0, 0)

	def map(self):
		"""Overrides to be empty."""
		pass

	def un_map(self, word_list):
		"""Overrides to be empty."""
		pass


class BlanktestMapping(AddressMapping):
	"""Map of all segments off."""
	def __init__(self, game=None):
		super(BlanktestMapping, self).__init__(game=game)

	def _build_addr_map(self):
		pass

	def _adjust_all_banks(self):
		pass

	def map(self):
		"""Overrides to be empty."""
		pass

	def un_map(self, word_list):
		"""Overrides to be empty."""
		pass
