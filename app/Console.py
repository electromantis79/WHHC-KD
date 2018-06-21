# !/usr/bin/env python
#  -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module simulates a console with the limited functionality of interpreting MP data.

	:Created Date: 3/11/2015
	:Author: **Craig Gunter**

"""

import os
import threading
import time
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename

import app.utils.functions
import app.utils.reads
import app.address_mapping
import app.mp_data_handler
import app.serial_IO.serial_packet
import app.keypad_mapping
import app.menu

from sys import platform as _platform

UPLOAD_FOLDER = '/Repos/WHHC-node/app/uploads'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']

api = Flask(__name__)
api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class Console(object):
	"""
	Builds a console object only geared to convert MP data to ASCII data.
	"""

	BOOT_UP_MODE = 0
	LISTENING_MODE = 1
	DISCOVERED_MODE = 2
	TRANSFER_MODE = 3
	CONNECTED_MODE = 4

	modeNameDict = {0: 'BOOT_UP_MODE', 1: 'LISTENING_MODE', 2: 'DISCOVERED_MODE', 3: 'TRANSFER_MODE', 4: 'CONNECTED_MODE'}

	def __init__(
			self, check_events_flag=True, serial_input_flag=False, serial_input_type='MP',
			serial_output_flag=True, encode_packet_flag=False, server_thread_flag=False, whh_flag=False):
		self.initTime = time.time()

		self.checkEventsFlag = check_events_flag
		self.serialInputFlag = serial_input_flag
		self.serialInputType = serial_input_type
		self.serialOutputFlag = serial_output_flag
		self.encodePacketFlag = encode_packet_flag
		self.serverThreadFlag = server_thread_flag
		self.whh_flag = whh_flag

		# Print Flags
		self.printProductionInfo = True
		self.printTimesFlag = False
		self.printInputTimeFlag = False
		self.verboseDiagnostic = False
		self.serial_input_verbose_flag = False
		self.print_check_events_elapse_time_flag = False

		app.utils.functions.verbose(['\nCreating Console object'], self.printProductionInfo)

		# Thread times in seconds
		self.serialInputRefreshFrequency = 0.1
		self.serialOutputRefreshFrequency = 0.1
		self.checkEventsRefreshFrequency = 0.1
		self.socketServerFrequency = 0.1
		self.startTime = time.time()

		# Variables that don't need resetting through internal reset
		self.className = 'console'
		self.serialString = ''
		self.checkEventsActiveFlag = False
		self.MP_StreamRefreshFlag = True
		self.check_events_over_period_flag = False
		self.count_event_time = 0
		self.count_event_time_list = []
		self.ETNSendListCount = 0
		self.ETNSendListLength = 0
		self.count_events_time_flag = False
		self.dirtyDict = {}
		self.sendList = []
		self.ETNSendList = []
		self.ETNSendListFlag = False
		self.quickKeysPressedList = []
		self.keyPressedFlag = False
		self.broadcastFlag = False
		self.broadcastString = ''
		self.modeLogger = None
		self.master_socket = None
		self._create_rotating_log('mode')

		self.dataUpdateIndex = 1

		# Main module items set in reset
		self.configDict = None
		self.game = None
		self.keyMap = None
		self.menu = None
		self.addrMap = None
		self.blankMap = None
		self.lampMap = None
		self.MPWordDict = None
		self.previousMPWordDict = None
		self.mp = None
		self.sp = None
		self.priorityListEmech = []
		self.mode = None

		self.reset()

	# INIT Functions

	def _create_rotating_log(self, log_name):
		"""
		Creates a rotating log
		"""
		self.modeLogger = logging.getLogger(log_name + " log")
		self.modeLogger.setLevel(logging.DEBUG)

		# add a rotating handler
		handler = RotatingFileHandler(log_name + '.log', maxBytes=50000, backupCount=5)
		handler.setLevel(logging.DEBUG)

		# create formatter
		formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

		# add formatter to handler
		handler.setFormatter(formatter)

		# add handler to logger
		self.modeLogger.addHandler(handler)

	def reset(self, internal_reset=0):
		"""Resets the console to a new game."""
		app.utils.functions.verbose(['\nConsole Reset'], self.printProductionInfo)

		self.mode = self.BOOT_UP_MODE
		self.modeLogger.info(self.modeNameDict[self.mode])

		# Create Game object
		self.configDict = app.utils.reads.read_config()
		if internal_reset:
			self.game.kill_clock_threads()
		self.game = app.utils.functions.select_sport_instance(self.configDict, number_of_teams=2)
		self.set_keypad(whh_flag=self.whh_flag)
		app.utils.functions.verbose(
			['sport', self.game.gameData['sport'], 'sportType', self.game.gameData['sportType']],
			self.printProductionInfo)
		self.menu = app.menu.MenuEventHandler(self.game)

		self.addrMap = app.address_mapping.AddressMapping(game=self.game)
		self.addrMap.map()
		self.blankMap = app.address_mapping.BlanktestMapping(game=self.game)
		self.lampMap = app.address_mapping.LamptestMapping(game=self.game)
		self.MPWordDict = dict(self.blankMap.wordsDict)

		self.previousMPWordDict = dict(self.blankMap.wordsDict)
		for addr in self.previousMPWordDict:
			self.previousMPWordDict[addr] = 666666

		self.mp = app.mp_data_handler.MpDataHandler()

		self.sp = app.serial_IO.serial_packet.SerialPacket(self.game)

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
		if (_platform == "linux" or _platform == "linux2") and not internal_reset:
			print 'Platform is', _platform
			if self.serialInputFlag or self.serialOutputFlag:
				app.utils.functions.verbose(['\nSerial Port On'], self.printProductionInfo)

				import serial_IO.mp_serial

				self.s = serial_IO.mp_serial.MpSerialHandler(
					serial_input_type=self.serialInputType, game=self.game, verbose_flag=self.serial_input_verbose_flag)

			if self.serialInputFlag:
				app.utils.functions.verbose(['\nSerial Input On'], self.printProductionInfo)
				self.refresherSerialInput = threading.Thread(
					target=app.utils.functions.thread_timer, args=(self._serial_input, self.serialInputRefreshFrequency))
				self.refresherSerialInput.daemon = True
				self.refresherSerialInput.name = '_serial_input'
				self.previousByteCount = 0
				self.refresherSerialInput.start()

			if self.checkEventsFlag:
				self.refresherCheckEvents = threading.Thread(
					target=app.utils.functions.thread_timer, args=(self._check_events, self.checkEventsRefreshFrequency))
				self.refresherCheckEvents.daemon = True
				self.refresherCheckEvents.name = '_check_events'
				self.refresherCheckEvents.start()

			if self.serialOutputFlag:
				app.utils.functions.verbose(
					['\nSerial Output On, self.encodePacketFlag', self.encodePacketFlag], self.printProductionInfo)
				self.refresherSerialOutput = threading.Thread(
					target=app.utils.functions.thread_timer, args=(self._serial_output, self.serialOutputRefreshFrequency))
				self.refresherSerialOutput.daemon = True
				self.refresherSerialOutput.name = '_serial_output'
				self.refresherSerialOutput.start()

			if self.serverThreadFlag:
				self.serverThread = threading.Thread(target=self._socket_server)
				self.serverThread.daemon = True
				self.serverThread.start()
			else:
				self.mode = self.CONNECTED_MODE
				self.modeLogger.info(self.modeNameDict[self.mode])

	# THREADS

	def _serial_input(self):
		if self.printInputTimeFlag:
			tic = time.time()
			init_elapse = tic-self.initTime
			print '(serial Input %s)' % init_elapse

		self.s.serial_input()

	def _serial_output(self):
		if self.printTimesFlag or self.verboseDiagnostic:
			tic = time.time()
			init_elapse = tic-self.initTime
			print '(-----------serial Output %s)' % init_elapse

		try:
			self.s.serial_output(self.serialString)
			if self.verboseDiagnostic:
				print 'Serial Output', self.serialString
		except:
			if not (_platform == "win32" or _platform == "darwin"):
				print 'Serial Output Error', self.serialString

	def _check_events(self):
		tic = time.time()
		if self.printTimesFlag or self.verboseDiagnostic:
			init_elapse = tic-self.initTime
			print '(-----_check_events %s)' % init_elapse

		# This is how the check events function is called when not on linux
		if (_platform == "win32" or _platform == "darwin") and self.checkEventsFlag:
			self.checkEventsTimer = threading.Timer(self.checkEventsRefreshFrequency, self._check_events).start()

		# This flag is to eliminate double entry to this area (Should never happen anyway)
		if not self.checkEventsActiveFlag:
			self.checkEventsActiveFlag = True

			if self.mode == self.BOOT_UP_MODE:
				self._update_mp_serial_string()
			elif self.mode == self.LISTENING_MODE:
				pass
			elif self.mode == self.DISCOVERED_MODE:
				self.mode = self.TRANSFER_MODE
				self.modeLogger.info(self.modeNameDict[self.mode])
			elif self.mode == self.TRANSFER_MODE:
				self.mode = self.CONNECTED_MODE
				self.modeLogger.info(self.modeNameDict[self.mode])
			elif self.mode == self.CONNECTED_MODE:
				self._connected_mode()

			# Time measurement for testing
			toc = time.time()
			elapse = (toc-tic)
			if elapse > self.checkEventsRefreshFrequency or self.print_check_events_elapse_time_flag:
				print '_check_events elapse', elapse*1000, ' ms'
				print

			# Time testing area for finding frequency of over period events
			if self.count_events_time_flag:
				self.count_event_time += 1
				if elapse > self.checkEventsRefreshFrequency:
					self.count_event_time_list.append((self.count_event_time, elapse))
					print '----------self.count_event_time =', self.count_event_time_list
					self.count_event_time = 0
				self.check_events_over_period_flag = True

			self.checkEventsActiveFlag = False

		# End Check Events --------------------------------------------------------------------

	def _connected_mode(self):
		# Handle a key press
		if self.keyPressedFlag:
			self.keyPressedFlag = False
			# print 'checkEvents key pressed'

			# Handle multiple incoming button presses
			for keyPressed in self.quickKeysPressedList:
				self.modeLogger.info(keyPressed + ' received')

				# Handle byte pair
				if len(keyPressed) == 3:
					# Received byte pair is in key map format
					last_byte = keyPressed[-1]
					byte_pair = keyPressed[:2]

					# Check for byte pair
					if self.keyMap.check_for_byte_pair(byte_pair):

						# Check for Up or Down byte
						if last_byte == 'D' or last_byte == 'U':

							if last_byte == 'D':
								direction = '_DOWN'
							elif last_byte == 'U':
								direction = '_UP'

							# Trigger most keys here on down press
							func_string = self.keyMap.map_(keyPressed[:2], direction=direction)
							self.menu.map_(func_string)
							# self.send_state_change_over_network(func_string)

							# Effects after button and menu are handled
							if func_string == 'periodClockOnOff' and direction == '_DOWN' and self.game.clockDict['periodClock'].running:
								print("Don't stop clock but send LED off")

							elif func_string == 'mode':
								if direction == '_DOWN':
									print('=== ENTER Command State ===')
								elif direction == '_UP':
									print('Reset Command Timer')
						else:
							print('\nOnly accepts U or D, No action performed with', byte_pair)
					else:
						print('\n', byte_pair, 'byte_pair not in key map')
				else:
					print('\nDid not receive 3 bytes in ', keyPressed)
					# Non-keyMap data received
					if keyPressed == '@':
						# If received the resend symbol resend
						self.send_state_change_over_network(None)
					else:
						# This are handles all other cases of data received
						try:
							# Special display of rssi for testing
							self.command = int(keyPressed)
							self.commandFlag = True
							self.addrMap.rssi = self.command
							self.addrMap.rssiFlag = self.commandFlag
						except:
							pass

			# Clear keys pressed list
			self.quickKeysPressedList = []

		# self.timeEvents()  # DO we need anything here?

		# self.dataEvents()  # DO we need anything here?

		# Update the new data in addrMap wordDict
		self._update_mp_words_dict()

		# Prepare data for the output thread
		self._update_mp_serial_string()

	def send_state_change_over_network(self, func_string):
		if self.game.clockDict['periodClock'].running:
			self.broadcastString += 'P1'
		else:
			self.broadcastString += 'P0'

		if 'delayOfGameClock' in self.game.clockDict:
			if self.game.clockDict['delayOfGameClock'].running:
				self.broadcastString += 'D1'
			else:
				self.broadcastString += 'D0'

		if 'segmentTimer' in self.game.clockDict:
			if self.game.clockDict['segmentTimer'].running:
				self.broadcastString += 'T1'
			else:
				self.broadcastString += 'T0'

		if 'shotClock' in self.game.clockDict:
			if self.game.clockDict['shotClock'].running:
				self.broadcastString += 'S1'
			else:
				self.broadcastString += 'S0'

		if self.game.gameSettings['inningBot']:
			self.broadcastString += 'IB'
		else:
			self.broadcastString += 'IT'

		if func_string is None:
			self.broadcastString += '@'

		self.broadcastFlag = True

	def _update_mp_words_dict(self):
		if self.game.gameSettings['blankTestFlag']:
			self.MPWordDict = dict(self.blankMap.wordsDict)
		elif self.game.gameSettings['lampTestFlag']:
			self.MPWordDict = dict(self.lampMap.wordsDict)
		else:
			self.addrMap.map()
			self.MPWordDict = dict(self.addrMap.wordsDict)

	def _update_mp_serial_string(self):
		# Check for changes in data
		if cmp(self.MPWordDict, self.previousMPWordDict) != 0:
			for address in self.MPWordDict.keys():
				if self.previousMPWordDict[address] != self.MPWordDict[address]:
					self.dirtyDict[address] = self.MPWordDict[address]
		elif self.mode == self.BOOT_UP_MODE and len(self.dirtyDict) == 0:
			self.mode = self.LISTENING_MODE
			self.modeLogger.info(self.modeNameDict[self.mode])

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

		# Something is in ETN send list and the initial event buffer count is zero
		# and an over period event has not just happened
		# Then put one ETN packet in the main send list
		if self.ETNSendListFlag and self.ETNSendList and not self.check_events_over_period_flag and self.ETNSendListCount < 1:
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
		if length:
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

			team_addr = y + 1 + team_addr_shift

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
		if length:
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
			team_addr = y + 1 + team_addr_shift

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

		word1 = self.mp.encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
		word2 = self.mp.encode(2, 4, 2, 0, 0, 0, team_addr_shift, 0, 0, pass3_4_flag=True)
		word4 = self.mp.encode(2, 4, 4, 0, 0, 0, font_justify, 0, '', pass3_4_flag=True)

		send_list = [word1, word2, word4, self.MPWordDict[29], self.MPWordDict[30], self.MPWordDict[32]]
		self.ETNSendList.append(send_list)

	def _home_font_justify_change(self):
		# ETN font_justify change section

		justify_ = self.game.get_team_data('TEAM_2', 'justify')
		font_ = self.game.get_team_data('TEAM_2', 'font')
		font_justify = (font_ - 1) * 6 + justify_ - 1

		team_addr_shift = 64

		word1 = self.mp.encode(2, 4, 1, 0, 1, 10, 13, 0, 0)
		word2 = self.mp.encode(2, 4, 2, 0, 0, 0, team_addr_shift, 0, 0, pass3_4_flag=True)
		word4 = self.mp.encode(2, 4, 4, 0, 0, 0, font_justify, 0, '', pass3_4_flag=True)

		send_list = [word1, word2, word4, self.MPWordDict[29], self.MPWordDict[30], self.MPWordDict[32]]
		self.ETNSendList.append(send_list)

	# PUBLIC FUNCTIONS --------------------------------

	def set_keypad(self, reverse_home_and_guest=False, keypad3150=False, mm_basketball=False, whh_flag=False):
		"""Sets the keypad."""
		# PUBLIC
		self.keyMap = app.keypad_mapping.KeypadMapping(
			self.game, reverse_home_and_guest=reverse_home_and_guest, keypad3150=keypad3150,
			mm_basketball=mm_basketball, whh_flag=whh_flag)

	def key_pressed(self, key_pressed):
		"""Simulates pressing a key."""
		# PUBLIC
		self.keyPressedFlag = True
		self.quickKeysPressedList.append(key_pressed)
		print '\nConsole key pressed', key_pressed, 'of self.quickKeysPressedList', self.quickKeysPressedList

	# THREADS ------------------------------------------

	def _socket_server(self):
		# Tcp Chat server
		# RUN IN ITS OWN THREAD-PROCESS

		import socket
		import select
		import sys
		import multiprocessing

		h_o_s_t = self.configDict['scoreNetHostAddress']
		socket_list = []
		receive_buffer = 4096
		p_o_r_t = self.configDict['socketServerPort']

		p = multiprocessing.current_process()
		print 'Starting:', p.name, p.pid
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		while self.mode == self.BOOT_UP_MODE:
			time.sleep(1)
		try:
			server_socket.bind((h_o_s_t, p_o_r_t))
		except socket.error as err:
			print 'errno', err.errno
			if err.errno == 98:
				# This means we already have a server
				connected = 0
				while not connected:
					time.sleep(3)
					try:
						server_socket.bind((h_o_s_t, p_o_r_t))
						connected = 1
					except:
						pass
			else:
				sys.exit(err.errno)

		server_socket.listen(10)

		# add server socket object to the list of readable connections
		socket_list.append(server_socket)

		start_message = "Chat server started on port " + str(p_o_r_t)
		print start_message
		self.modeLogger.info(start_message)

		while 1:
			tic = time.time()
			# print(tic-self.startTime)

			# get the list sockets which are ready to be read through select
			# 4th arg, time_out  = 0 : poll and never block
			ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)

			for sock in ready_to_read:
				# a new connection request received
				# print '----- socket_list', socket_list, 'ready_to_read', ready_to_read
				if sock == server_socket:
					sockfd, addr = server_socket.accept()
					socket_list.append(sockfd)
					print "[%s, %s] is connected" % (sockfd, addr)
					message = "[%s:%s] entered our chatting room" % (sockfd, addr)
					socket_list = self._broadcast_or_remove(server_socket, message, socket_list)
					if self.master_socket is None:
						self.mode = self.DISCOVERED_MODE
						self.modeLogger.info(self.modeNameDict[self.mode])
						self.modeLogger.info("[%s:%s] joined first" % (sockfd, addr))
						self.master_socket = sockfd
					else:
						self.modeLogger.info("[%s:%s] joined" % (sockfd, addr))

				else:
					# process data received from client
					try:
						# receiving data from the socket.
						data = sock.recv(receive_buffer)
						if data:
							if self.master_socket is None:
								self.master_socket = sock
								self.mode = self.DISCOVERED_MODE
								self.modeLogger.info(self.modeNameDict[self.mode])

							# there is something in the socket
							if sock == self.master_socket:
								# print 'master', sock, self.master_socket
								self.key_pressed(data)
							else:
								print 'other', sock, self.master_socket

							socket_list = self._broadcast_or_remove(server_socket, data, socket_list)
						else:
							# at this stage, no data means probably the connection has been broken
							message = "[%s] is offline, no data" % sock
							socket_list = self._broadcast_or_remove(server_socket, message, socket_list)

					# exception
					except:
						message = "[%s] is offline, exception" % sock
						socket_list = self._broadcast_or_remove(server_socket, message, socket_list)

			# Broadcast triggered from check_events
			if self.broadcastFlag:
				self.broadcastFlag = False
				socket_list = self._broadcast_or_remove(server_socket, self.broadcastString, socket_list)
				self.broadcastString = ''

			toc = time.time()
			elapse = toc - tic
			time.sleep(self.socketServerFrequency-elapse)

		server_socket.close()
		'''
		import Network, logging
		jobs=[]
		server=multiprocessing.Process(name='server', target=Network.chat_server)
		jobs.append(server)
		multiprocessing.log_to_stderr(logging.DEBUG)
		server.start()
		server.join()
		while 1:
			#
			if not server.is_alive() and configDict['SERVER']==True:
				print server.exitcode
				configDict['SERVER']=False
				c.writeSERVER(False)
				server.terminate()
			elif configDict['SERVER']==False:
				time.sleep(3)
				server=multiprocessing.Process(name='server', target=Network.chat_server)
				jobs.append(server)
				server.start()
				server.join()
		'''

	def _broadcast_or_remove(self, server_socket, message, socket_list):
		# broadcast chat messages to all connected clients
		for socket in socket_list:
			# send the message only to peer
			if socket != server_socket:
				try:
					socket.send(message)
				except:
					self.modeLogger.info(message)
					# broken socket connection
					if socket == self.master_socket:
						self.master_socket = None
						self.mode = self.LISTENING_MODE
						self.modeLogger.info(self.modeNameDict[self.mode])
					socket.close()
					# broken socket, remove it
					if socket in socket_list:
						socket_list.remove(socket)
		return socket_list


@api.route("/hello")
def hello_world():
	return "Hello, World"


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(api.config['UPLOAD_FOLDER'], filename)


@api.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file_ = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file_.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file_ and allowed_file(file_.filename):
			filename = secure_filename(file_.filename)
			file_.save(os.path.join(api.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file', filename=filename))
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form method=post enctype=multipart/form-data>
		<input type=file name=file>
		<input type=submit value=Upload>
	</form>
	'''


def test():
	"""Runs the converter with the sport and jumper settings hardcoded in this function."""
	print "ON"
	sport = 'MPBASEBALL1'
	jumpers = '0000'
	print 'sport', sport, 'jumpers', jumpers

	c = Config()
	c.write_sport(sport)
	c.write_option_jumpers(jumpers)

	cons = Console(
		check_events_flag=True, serial_input_flag=False, serial_input_type='MP',
		serial_output_flag=True, encode_packet_flag=False, server_thread_flag=True,
		whh_flag=True)

	h_o_s_t = '192.168.8.1'
	p_o_r_t = 60050
	start_message = "API server started on port " + str(p_o_r_t)
	print start_message
	cons.modeLogger.info(start_message)

	api.run(host=h_o_s_t, debug=False, port=p_o_r_t)


	# SPORT_LIST = [
	# 'MMBASEBALL3', 'MPBASEBALL1', 'MMBASEBALL4', 'MPLINESCORE4', 'MPLINESCORE5',
	# 'MPMP-15X1', 'MPMP-14X1', 'MPMULTISPORT1-baseball', 'MPMULTISPORT1-football', 'MPFOOTBALL1', 'MMFOOTBALL4',
	# 'MPBASKETBALL1', 'MPSOCCER_LX1-soccer', 'MPSOCCER_LX1-football', 'MPSOCCER1', 'MPHOCKEY_LX1', 'MPHOCKEY1',
	# 'MPCRICKET1', 'MPRACETRACK1', 'MPLX3450-baseball', 'MPLX3450-football', 'MPGENERIC',  'MPSTAT']


if __name__ == '__main__':
	from config_default_settings import Config
	test()
