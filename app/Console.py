# !/usr/bin/env python
#  -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module simulates a console with limited functionality of interpreting MP data.

	:Created Date: 3/11/2015
	:Author: **Craig Gunter**

"""

import threading
import time

import app.utils.functions
import app.utils.reads
import app.mp_data_handler
import app.serial_IO.serial_packet
import app.address_mapping

from sys import platform as _platform


class Console(object):
	"""
	Builds a console object.
		*Contains verbose comments option*
	"""

	def __init__(
			self, vbose_list=(1, 0, 0), check_events_flag=True,
			serial_input_flag=0, serial_input_type='MP', serial_output_flag=1, encode_packet_flag=False,
			server_thread_flag=True):
		self.className = 'console'

		self.checkEventsFlag = check_events_flag
		self.serialInputFlag = serial_input_flag
		self.serialInputType = serial_input_type
		self.serialOutputFlag = serial_output_flag
		self.encodePacketFlag = encode_packet_flag
		self.serverThreadFlag = server_thread_flag
		self.vboseList = vbose_list
		self.verbose = self.vboseList[0]  # Method Name or arguments
		self.verboseMore = self.vboseList[1]  # Deeper loop information in methods
		self.verboseMost = self.vboseList[2]  # Crazy Deep Stuff

		app.utils.functions.verbose(['\nCreating Console object'], self.verbose)

		self.MP_StreamRefreshFlag = True
		self.printTimesFlag = False
		self.check_events_active_flag = False
		self.check_events_over_period_flag = False
		self.count_event_time = 0
		self.count_event_time_list = []
		self.ETNSendListCount = 0
		self.ETNSendListLength = 0
		self.verboseDiagnostic = False
		self.print_input_time_flag = False
		self.serial_input_verbose_flag = False
		self.print_check_events_elapse_time_flag = False
		self.count_events_time_flag = False
		self.initTime = time.time()
		import datetime
		print datetime.datetime.now()

		self.reset()

	# INIT Functions

	def reset(self, internal_reset=0):
		"""Resets the console to a new game."""
		app.utils.functions.verbose(['\nConsole Reset'], self.verbose)

		# Create Game object
		self.configDict = app.utils.reads.read_config()
		if internal_reset:
			self.game.kill_clock_threads()
		self.game = app.utils.functions.select_sport_instance(self.configDict, number_of_teams=2)

		print 'sport', self.game.gameData['sport'], 'sportType', self.game.gameData['sportType']

		# Build address maps
		self.addrMap = app.address_mapping.AddressMapping(game=self.game)
		self.lampTest = app.address_mapping.LamptestMapping(game=self.game)
		self.blankTest = app.address_mapping.BlanktestMapping(game=self.game)
		self.mp = app.mp_data_handler.MpDataHandler()
		self.addrMap.map()

		# Variables
		self.dirtyDict = {}
		self.sendList = []
		self.ETNSendList = []
		self.quickKeysPressedList = []
		self.sendListFlag = False
		self.ETN_DataFlag = False
		self.ETNSendListFlag = False
		self.quantumTunnelFlag = False
		self.switchKeypadFlag = False
		self.elapseTimeFlag = False
		self.busyCheckEventsFlag = True
		self.keyPressedFlag = False
		
		self.broadcastFlag = False
		self.broadcastString = ''
		self.showOutputString = False
		self.sp = app.serial_IO.serial_packet.SerialPacket(self.game)
		self.serialInputRefreshFrequency = 0.1
		self.serialOutputRefreshFrequency = 0.1
		self.checkEventsRefreshFrequency = self.game.gameSettings['periodClockResolution']  # 0.1ms
		self.serialString = ''

		self.MPWordDict = dict(self.addrMap.wordsDict)
		self.previousMPWordDict = dict(self.addrMap.wordsDict)
		self.dataUpdateIndex = 1
		self.shotClockSportsFlag = (
				self.game.gameData['sport'] == 'MPBASKETBALL1' or self.game.gameData['sport'] == 'MPHOCKEY_LX1'
				or self.game.gameData['sport'] == 'MPHOCKEY1')

		self.priorityListEmech = self._select_mp_data_priority()

		self._setup_threads(internal_reset)  # internal_reset not used with this converter

	def _select_mp_data_priority(self):
		# Select priority order list
		# G1		B1 = 1,2,3,4		B2 = 5,6,7,8 		B3 = 9,10,11,12, 		B4 = 13,14,15,16
		# G2		B1 = 17,18,19,20 	B2 = 21,22,23,24 	B3 = 25,26,27,28 		B4 = 29,30,31,32
		if self.game.gameData['sportType'] == 'soccer' or self.game.gameData['sportType'] == 'hockey':
			key = 'Sockey'
		elif self.game.gameData['sportType'] == 'stat':
			key = 'Stat'
		else:
			key = '402'
		print 'Priority Key = ', key
		# Add code here for getting to the other priorities

		# All known priorities
		if (
				key == '402'
				and self.game.gameData['sport'] == 'MPFOOTBALL1'
				and self.game.gameSettings['trackClockEnable']

				or key == 'Emech'
		):
			priority_list_emech = [
				18, 11, 22, 1, 6, 5, 21, 2, 7, 25, 9, 8, 24, 3, 23, 4, 20, 19, 17, 12, 10, 16, 15,
				14, 13, 28, 27, 26, 32, 31, 30, 29]
		elif key == '402':
			priority_list_emech = [
				22, 1, 6, 5, 21, 2, 7, 25, 9, 8, 24, 3, 23, 4, 20, 19, 17, 12, 10, 16, 15, 14, 13,
				28, 27, 26, 32, 31, 30, 29, 18, 11]
		elif key == 'Sockey' and self.game.gameData['sportType'] == 'soccer' and self.game.gameSettings[
			'trackClockEnable']:
			priority_list_emech = [
				18, 11, 6, 5, 25, 22, 1, 7, 21, 2, 10, 14, 12, 13, 17, 29, 4, 9, 8, 3, 15, 16, 26,
				30, 24, 20, 23, 19, 28, 27, 32, 31]
		elif key == 'Sockey':
			priority_list_emech = [
				22, 6, 1, 5, 25, 21, 7, 2, 10, 14, 12, 13, 17, 29, 4, 9, 8, 3, 11, 15, 16, 18, 26,
				30, 24, 20, 23, 19, 28, 27, 32, 31]
		elif key == '314' or key == '313':
			priority_list_emech = [
				24, 23, 22, 21, 4, 3, 2, 1, 8, 7, 6, 5, 20, 19, 18, 17, 12, 11, 10, 9, 16, 15, 14,
				13, 28, 27, 26, 25, 32, 21, 30, 29]
		elif key == 'Stat':
			priority_list_emech = self.addrMap.wordListAddrStat
		# self.priority_list_emech = [1,2,3,5,6,7,9,10,11,13,14,15,17,18,19,21,22,
		# 23,33,34,35,37,38,39,41,42,43,45,46,47,49,50,51,53,54,55]
		else:
			priority_list_emech = range(32)
		return priority_list_emech

	def _setup_threads(self, internal_reset):
		# Platform Dependencies
		if _platform == "linux" or _platform == "linux2":
			print 'Platform is', _platform
			if self.serialInputFlag and not internal_reset:
				app.utils.functions.verbose(['\nSerial Input On'], self.verbose)
				import serial_IO.mp_serial
				self.s = serial_IO.mp_serial.MpSerialHandler(
					serial_input_type=self.serialInputType, game=self.game, verbose_flag=self.serial_input_verbose_flag)
				self.refresherSerialInput = threading.Thread(
					target=app.utils.functions.thread_timer, args=(self._serial_input, self.serialInputRefreshFrequency))
				self.refresherSerialInput.daemon = True
				self.refresherSerialInput.name = '_serial_input'
				self.previousByteCount = 0
				self.refresherSerialInput.start()

			if self.checkEventsFlag and not internal_reset:
				self.refresherCheckEvents = threading.Thread(
					target=app.utils.functions.thread_timer, args=(self._check_events, self.checkEventsRefreshFrequency))
				self.refresherCheckEvents.daemon = True
				self.refresherCheckEvents.name = '_check_events'
				self.refresherCheckEvents.start()

			if self.serialOutputFlag and not internal_reset:
				app.utils.functions.verbose(['\nSerial Output On, self.encodePacketFlag', self.encodePacketFlag], self.verbose)
				self.refresherSerialOutput = threading.Thread(
					target=app.utils.functions.thread_timer, args=(self._serial_output, self.serialOutputRefreshFrequency))
				self.refresherSerialOutput.daemon = True
				self.refresherSerialOutput.name = '_serial_output'
				self.refresherSerialOutput.start()		

		elif _platform == "darwin":
			#  OS X
			print 'Apple Sucks!!!!!', 'Disabling input and output flags'
			self.serialOutputFlag = False
			self.serialInputFlag = False
		elif _platform == "win32":
			print '\nSerial Input not working for', _platform, 'Disabling input and output flags'
			self.serialOutputFlag = False
			self.serialInputFlag = False
			# self.showOutputString = True
			if self.checkEventsFlag and not internal_reset:
				threading.Timer(.1, self._check_events).start()
				
			if self.serialOutputFlag and not internal_reset:
				app.utils.functions.verbose(['\nSerial Output On, self.encodePacketFlag', self.encodePacketFlag], self.verbose)
				self.refresherSerialOutput = threading.Thread(
					target=app.utils.functions.thread_timer, args=(self._serial_output, self.serialOutputRefreshFrequency))
				self.refresherSerialOutput.daemon = True
				self.refresherSerialOutput.name = '_serial_output'
				self.refresherSerialOutput.start()

	# THREADS

	def _serial_input(self):
		"""Inputs serial packets."""
		if self.print_input_time_flag:
			tic = time.time()
			init_elapse = tic-self.initTime
			print '(serial Input %s)' % init_elapse

		self.s.serial_input()

	def _serial_output(self):
		"""Outputs serial packets."""
		if self.printTimesFlag or self.verboseDiagnostic:
			tic = time.time()
			init_elapse = tic-self.initTime
			print '(-----------serial Output %s)' % init_elapse

		try:
			self.s.serial_output(self.serialString)
			if self.printTimesFlag or self.verboseDiagnostic or self.ETNSendListFlag:
				pass  # print 'Serial Output', self.serialString
		except:
			if not (_platform == "win32" or _platform == "darwin"):
				print 'Serial Output Error', self.serialString

	# Timer called events for the main program -----------------

	def _check_events(self):
		"""
		Checks all events.

		This is called at the checkEventsRefreshFrequency and could be thought of as the main interrupt in a micro-controller.

		The console only updates data for the outside world at this time.
		"""
		tic = time.time()
		if self.printTimesFlag or self.verboseDiagnostic:
			init_elapse = tic-self.initTime
			print '(-----_check_events %s)' % init_elapse

		# This is how the check events function is called when not on linux
		if (_platform == "win32" or _platform == "darwin") and self.checkEventsFlag:
			self.checkEventsTimer = threading.Timer(self.checkEventsRefreshFrequency, self._check_events).start()

		# This flag is to eliminate double entry to this area (Should never happen anyway)
		if not self.check_events_active_flag:
			self.check_events_active_flag = True
			
			# Select normal packet or packet from ETN packet list
			if self.s.ETNpacketList and not self.ETNSendListFlag:
				packet = self.s.ETNpacketList[-1]
				self.s.ETNpacketList.pop(0)
			else:
				packet = self.s.packet

			self.sp.process_packet(print_string=False, packet=packet)

			self._update_mp_words_dict()

			self._update_mp_serial_string()

			# Time measurement for testing
			toc = time.time()
			elapse = (toc-tic)
			if elapse > self.checkEventsRefreshFrequency or self.print_check_events_elapse_time_flag:
				print '_check_events elapse', elapse*1000, ' ms'
				print

			if self.count_events_time_flag:
				self.count_event_time += 1
				if elapse > self.checkEventsRefreshFrequency:
					self.count_event_time_list.append((self.count_event_time, elapse))
					print '----------self.count_event_time =', self.count_event_time_list
					self.count_event_time = 0
				self.check_events_over_period_flag = True

			self.check_events_active_flag = False

		# End Check Events --------------------------------------------------------------------

	def _update_mp_words_dict(self):
		"""Update address map and MPWordDict and send to drivers if class is scoreboard."""
		# Select current map
		if self.game.gameSettings['blankTestFlag']:
			self.blankTest.map()
			self.MPWordDict = dict(self.blankTest.wordsDict)
		elif self.game.gameSettings['lampTestFlag']:
			self.lampTest.map()
			self.MPWordDict = dict(self.lampTest.wordsDict)
		else:
			self.addrMap.map()
			self.MPWordDict = dict(self.addrMap.wordsDict)

	def _update_mp_serial_string(self):
		"""Updates 18 bytes (9 MP words) into self.sendList and converts it to the self.serialString."""

		# Check for changes in data
		if cmp(self.MPWordDict, self.previousMPWordDict) != 0:
			for address in self.MPWordDict.keys():
				if self.previousMPWordDict[address] != self.MPWordDict[address]:
					self.dirtyDict[address] = self.MPWordDict[address]
		self.previousMPWordDict = dict(self.MPWordDict)

		# Print dirty list
		if len(self.dirtyDict) and self.verboseDiagnostic:
			print '\n---self.dirtyDict', self.dirtyDict, '\nlength', len(self.dirtyDict)

		# Clear send list
		self.sendList = []

		# Make custom send list for ASCII to MP ETN send
		self._custom_send_list_ascii_to_mp_etn()

		# Append dirty words to send list
		remove_count = 0
		if len(self.dirtyDict) and not self.ETNSendListFlag:
			for addr in self.priorityListEmech:
				if remove_count <= 8:
					if addr in self.dirtyDict:
						remove_count += 1
						self.sendList.append(self.dirtyDict[addr])
						
						if self.verboseDiagnostic:
							# Print info for dirty words
							group, bank, word, i_bit, numeric_data = self.mp.decode(self.dirtyDict[addr])
							print (
								'group', group, 'bank', bank, 'word', word, 'addr', self.mp.gbw_to_mp_address(group, bank, word) + 1,
								'i_bit', i_bit, 'data', bin(numeric_data), bin(self.dirtyDict[addr]))
							
						del self.dirtyDict[addr]
		space_left = 9-remove_count

		# Append remaining words to fill send list
		if self.MP_StreamRefreshFlag and not self.ETNSendListFlag:
			for x in range(space_left):
				if self.game.gameData['sportType'] == 'stat':
					
					self.sendList.append(self.MPWordDict[self.priorityListEmech[self.dataUpdateIndex-1]])
					
					if self.verboseDiagnostic:
						# Print info for remaining words
						print (
							'self.dataUpdateIndex', self.dataUpdateIndex, 'self.priorityListEmech[self.dataUpdateIndex]',
							self.priorityListEmech[self.dataUpdateIndex-1])
						group, bank, word, i_bit, numeric_data = self.mp.decode(
							self.MPWordDict[self.priorityListEmech[self.dataUpdateIndex-1]])
						print (
							'group', group, 'bank', bank, 'word', word, 'addr', self.mp.gbw_to_mp_address(group, bank, word) + 1,
							'i_bit', i_bit, 'data', bin(numeric_data), bin(self.MPWordDict[self.priorityListEmech[self.dataUpdateIndex-1]]),
							self.MPWordDict[self.priorityListEmech[self.dataUpdateIndex-1]])
						
					self.dataUpdateIndex += 1
					if self.dataUpdateIndex > len(self.priorityListEmech):
						self.dataUpdateIndex = 1
					
				else:
					
					self.sendList.append(self.MPWordDict[self.dataUpdateIndex])
					# print 'self.dataUpdateIndex',self.dataUpdateIndex
					
					if self.verboseDiagnostic:
						# Print info for remaining words
						group, bank, word, i_bit, numeric_data = self.mp.decode(self.MPWordDict[self.dataUpdateIndex])
						print (
							'group', group, 'bank', bank, 'word', word,
							'addr', self.mp.gbw_to_mp_address(group, bank, word) + 1,
							'i_bit', i_bit, 'data', bin(numeric_data), bin(self.MPWordDict[self.dataUpdateIndex]),
							self.MPWordDict[self.dataUpdateIndex])
						
					self.dataUpdateIndex += 1
					if self.dataUpdateIndex > len(self.MPWordDict):
						self.dataUpdateIndex = 1

		# Clear for next run
		if self.check_events_over_period_flag:
			self.check_events_over_period_flag = False

		# This reopens the path to process a new ETN change event
		if not self.ETNSendList:
			self.ETNSendListFlag = False

		# Create string for transport
		serial_string = ''
		for word in self.sendList:
			first_byte = chr((word & 0xFF00) >> 8)
			second_byte = chr((word & 0xFF))
			serial_string += first_byte+second_byte
		self.serialString = serial_string

		if self.showOutputString:
			print self.serialString

	def _custom_send_list_ascii_to_mp_etn(self):
		if self.sp.ETNChangeFlag:
			self.sp.ETNChangeFlag = False

			self.ETNSendListFlag = True
			self.ETNSendList = []

			if self.sp.guestNameChangeFlag:
				self.sp.guestNameChangeFlag = False

				self._guest_name_change()

			if self.sp.homeNameChangeFlag:
				self.sp.homeNameChangeFlag = False

				self._home_name_change()

			if self.sp.guestFontJustifyChangeFlag:
				self.sp.guestFontJustifyChangeFlag = False

				self._guest_font_justify_change()

			if self.sp.homeFontJustifyChangeFlag:
				self.sp.homeFontJustifyChangeFlag = False

				self._home_font_justify_change()

			self.ETNSendListLength = len(self.ETNSendList)

		if self.ETNSendListFlag:
			pass  # self.printTimesFlag = True
		else:
			pass  # self.printTimesFlag = False

		# Something is in ETN send list and the initial event buffer count is zero
		# and an over period event has not just happened
		# Then put one ETN packet in the main send list
		if self.ETNSendListFlag and self.ETNSendList and not self.check_events_over_period_flag and self.ETNSendListCount < 1:
			print self.ETNSendList
			self.sendList = self.ETNSendList[0]
			self.ETNSendList.pop(0)

			# Reset initial event buffer
			if (self.ETNSendListLength - 1) == len(self.ETNSendList):
				self.ETNSendListCount = 3

		elif self.ETNSendListFlag and not self.check_events_over_period_flag:
			# Wait for _check_events to settle before sending ETN packets
			self.ETNSendListCount -= 1

	def _guest_name_change(self):
		# ETN character change section
		name = self.game.get_team_data('TEAM_1', 'name')
		length = len(name)
		pairs_list = []
		team_addr_override = False
		if length:
			if self.sp.guestNameChangeOneCharFlag:
				self.sp.guestNameChangeOneCharFlag = False
				single_addr = length / 2 + length % 2
				addr_length = range(abs(length % 2 - 1))
				team_addr_override = True
			else:
				addr_length = range(int(length / 2))

			for address in addr_length:
				left_etn_byte = name[address * 2]
				right_etn_byte = name[address * 2 + 1]
				pairs_list.append((left_etn_byte, right_etn_byte))

			if length % 2:
				# Odd Length Ending Section
				left_etn_byte = name[-1]
				right_etn_byte = 0
				pairs_list.append((left_etn_byte, right_etn_byte))

		else:
			# Blank Name Section
			pairs_list.append((' ', 0))

		team_addr_shift = 0

		for y, pair in enumerate(pairs_list):
			left_etn_byte = pair[0]
			right_etn_byte = pair[1]

			if team_addr_override:
				team_addr = team_addr_shift + single_addr
			# print 'single team addr'
			else:
				team_addr = y + 1 + team_addr_shift

			# print 'normal team addr'
			# 0xbc = tunnel code
			# word 2 = address of character pair
			# word 3 = left_etn_byte
			# word 4 = right_etn_byte or controlByte(if addr = 0or64)

			if right_etn_byte == 0:
				right_etn_byte = chr(right_etn_byte)
			word1 = self.mp.encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
			word2 = self.mp.encode(2, 4, 2, 0, 0, 0, team_addr, 0, 0, pass3_4_flag=True)
			word3 = self.mp.encode(2, 4, 3, 0, 0, 0, ord(left_etn_byte), 0, '', pass3_4_flag=True)
			word4 = self.mp.encode(2, 4, 4, 0, 0, 0, ord(right_etn_byte), 0, '', pass3_4_flag=True)

			send_list = [
				word1, word2, word3, word4, self.MPWordDict[29], self.MPWordDict[30],
				self.MPWordDict[31], self.MPWordDict[32]]
			self.ETNSendList.append(send_list)

	def _home_name_change(self):
		# ETN character change section
		name = self.game.get_team_data('TEAM_2', 'name')
		length = len(name)
		pairs_list = []
		team_addr_override = False
		if length:
			if self.sp.homeNameChangeOneCharFlag:
				self.sp.homeNameChangeOneCharFlag = False
				single_addr = length / 2 + length % 2
				addr_length = range(abs(length % 2 - 1))
				team_addr_override = True
			else:
				addr_length = range(int(length / 2))

			for address in addr_length:
				left_etn_byte = name[address * 2]
				right_etn_byte = name[address * 2 + 1]
				pairs_list.append((left_etn_byte, right_etn_byte))

			if length % 2:
				# Odd Length Ending Section
				left_etn_byte = name[-1]
				right_etn_byte = 0
				pairs_list.append((left_etn_byte, right_etn_byte))

		else:
			# Blank Name Section
			pairs_list.append((' ', 0))

		team_addr_shift = 64

		for y, pair in enumerate(pairs_list):
			left_etn_byte = pair[0]
			right_etn_byte = pair[1]
			if team_addr_override:
				team_addr = team_addr_shift + single_addr
			# print 'single team addr'
			else:
				team_addr = y + 1 + team_addr_shift
			# print 'normal team addr'

			# 0xbc = tunnel code
			# word 2 = address of character pair
			# word 3 = left_etn_byte
			# word 4 = right_etn_byte or controlByte(if addr = 0or64)

			if right_etn_byte == 0:
				right_etn_byte = chr(right_etn_byte)
			word1 = self.mp.encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
			word2 = self.mp.encode(2, 4, 2, 0, 0, 0, team_addr, 0, 0, pass3_4_flag=True)
			word3 = self.mp.encode(2, 4, 3, 0, 0, 0, ord(left_etn_byte), 0, '', pass3_4_flag=True)
			word4 = self.mp.encode(2, 4, 4, 0, 0, 0, ord(right_etn_byte), 0, '', pass3_4_flag=True)

			send_list = [
				word1, word2, word3, word4,
				self.MPWordDict[29], self.MPWordDict[30], self.MPWordDict[31], self.MPWordDict[32]]
			self.ETNSendList.append(send_list)

	def _guest_font_justify_change(self):
		# ETN font_justify change section

		justify_ = self.game.get_team_data('TEAM_1', 'justify')
		font_ = self.game.get_team_data('TEAM_1', 'font')
		font_justify = (font_ - 1) * 6 + justify_ - 1

		team_addr_shift = 0

		jword1 = self.mp.encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
		jword2 = self.mp.encode(2, 4, 2, 0, 0, 0, team_addr_shift, 0, 0, pass3_4_flag=True)
		jword4 = self.mp.encode(2, 4, 4, 0, 0, 0, font_justify, 0, '', pass3_4_flag=True)

		send_list = [jword1, jword2, jword4, self.MPWordDict[29], self.MPWordDict[30], self.MPWordDict[32]]
		self.ETNSendList.append(send_list)

	def _home_font_justify_change(self):
		# ETN font_justify change section

		justify_ = self.game.get_team_data('TEAM_2', 'justify')
		font_ = self.game.get_team_data('TEAM_2', 'font')
		font_justify = (font_ - 1) * 6 + justify_ - 1

		team_addr_shift = 64

		jword1 = self.mp.encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
		jword2 = self.mp.encode(2, 4, 2, 0, 0, 0, team_addr_shift, 0, 0, pass3_4_flag=True)
		jword4 = self.mp.encode(2, 4, 4, 0, 0, 0, font_justify, 0, '', pass3_4_flag=True)

		send_list = [jword1, jword2, jword4, self.MPWordDict[29], self.MPWordDict[30], self.MPWordDict[32]]
		self.ETNSendList.append(send_list)


def test():
	"""Creates an interpreter."""
	print "ON"
	sport = 'MPBASKETBALL1'
	c = Config()
	c.write_sport(sport)
	c.write_option_jumpers('0000')
	Console(
		check_events_flag=True, serial_input_flag=True, serial_input_type='ASCII',
		serial_output_flag=True, encode_packet_flag=True, server_thread_flag=True)
	while 1:
		time.sleep(2)
		# break

	# SPORT_LIST = [
	# 'MMBASEBALL3', 'MPBASEBALL1', 'MMBASEBALL4', 'MPLINESCORE4', 'MPLINESCORE5',
	# 'MPMP-15X1', 'MPMP-14X1', 'MPMULTISPORT1-baseball', 'MPMULTISPORT1-football', 'MPFOOTBALL1', 'MMFOOTBALL4',
	# 'MPBASKETBALL1', 'MPSOCCER_LX1-soccer', 'MPSOCCER_LX1-football', 'MPSOCCER1', 'MPHOCKEY_LX1', 'MPHOCKEY1',
	# 'MPCRICKET1', 'MPRACETRACK1', 'MPLX3450-baseball', 'MPLX3450-football', 'MPGENERIC',  'MPSTAT']


if __name__ == '__main__':
	from config_default_settings import Config
	test()
