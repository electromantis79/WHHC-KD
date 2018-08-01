#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module manipulates MP style data.

	:Created Date: 3/12/2015
	:Author: **Craig Gunter**

"""


class MpDataHandler(object):
	"""Creates an object to manipulate MP style data."""

	def __init__(self, verbose=False):
		self.verbose = verbose
		self.data = 0x0
		self.addr = 0
		self.blankType = ''
		self.group = 0
		self.bank = 0
		self.word = 0
		self.I_Bit = 0
		self.H_Bit = 0
		self.highByte = 0
		self.lowByte = 0
		self.highNibble = 0
		self.lowNibble = 0
		self.LH_Word = 0
		self.seg_addr = 0
		self.segmentData = ''
		self.pass3_4Flag = False
		self.bitwise_Flag = False
		self.statFlag = False
		self.blankedFlag = False

	def gbw_to_mp_address(self, group, bank, word):
		"""Returns MP format address."""
		# PUBLIC method
		self.addr = ((((group - 1) << 2) | (bank - 1)) << 2) | (word - 1)
		return self.addr

	def _gbwd_to_segment_address(self):
		# Builds the segment address from the group, bank, word, and data.
		self.seg_addr = (self.gbw_to_mp_address(self.group, self.bank, self.word) << 9) | self.data

	def _low_high_protocol_wrapper(self, seg_addr):
		# Converts the Low and High Byes into the LowHigh Word format. (0LLLLLLL 1HHHHHHH)
		self.highByte = ((seg_addr & 0x3f80) >> 7) | 0x80
		self.lowByte = seg_addr & 0x007f
		self.LH_Word = (self.lowByte << 8) | self.highByte

		if self.verbose:
			print((
				"LH Word:0x%02X%02X" % (self.lowByte, self.highByte), bin(self.LH_Word), self.LH_Word,
				"GBWD: G%d B%d W%d %s" % (self.group, self.bank, self.word, bin(self.data))))

		return self.LH_Word

	def _segments_change(self, segments):
		try:
			segments = list(segments.lower())
		except:
			if self.verbose:
				print('_segments_change received segment value', segments)

		self.segData = 0b00000000
		if segments is not None:
			for seg in segments:
				if seg == 'a':
					self.segData = self.segData | 0b00000001
				elif seg == 'b':
					self.segData = self.segData | 0b00000010
				elif seg == 'c':
					self.segData = self.segData | 0b00000100
				elif seg == 'd':
					self.segData = self.segData | 0b00001000
				elif seg == 'e':
					self.segData = self.segData | 0b00010000
				elif seg == 'f':
					self.segData = self.segData | 0b00100000
				elif seg == 'g':
					self.segData = self.segData | 0b01000000
				self.data = self.segData

	def segment_decode(self, digit, seg_lookup=0):
		"""Decodes a number in to its 7 segment display representation."""
		# PUBLIC method

		if digit is not None:
			if not seg_lookup:
				if self.verbose:
					print("segDecode:%2d" % digit)
				segment_table = [  # HGFEDCBA
					0b00111111,  # 0 = ABCDEF
					0b00000110,  # 1 =  BC
					0b01011011,  # 2 = AB DE G
					0b01001111,  # 3 = ABCD  G
					0b01100110,  # 4 =  BC  FG
					0b01101101,  # 5 = A CD FG
					0b01111101,  # 6 = A CDEFG
					0b00000111,  # 7 = ABC
					0b01111111,  # 8 = ABCDEFG
					0b01101111,  # 9 = ABCDFG
					0b01110111,  # A = ABCEFG
					0b01111100,  # b = CDEFG
					0b01111001,  # C = ADEFG
					0b01011110,  # d = BCDEG
					0b01111001,  # E = ADEFG
					0b01110001  # F = AEFG
				]
			else:
				# segLookup is used in Driver.py
				segment_table = [
					'ABCDEF',  # 0
					'BC',  # 1
					'ABDEG',  # 2
					'ABCDG',  # 3
					'BCFG',  # 4
					'ACDFG',  # 5
					'ACDEFG',  # 6
					'ABC',  # 7
					'ABCDEFG',  # 8
					'ABCDFG',  # 9
					'ABCEFG',  # A
					'CDEFG',  # b
					'ADEFG',  # C
					'BCDEG',  # d
					'ADEFG',  # E
					'AEFG'  # F
				]
				if self.verbose:
					print("Inverse segDecode:", segment_table[digit])
			try:
				digit = segment_table[digit]
			except:
				print('segment_decode ERROR digit =', digit)
		return digit

	def _value_range_check(self):
		# Check if nibbles are out of range, if so print.
		high_out = (self.highNibble > 15 or self.highNibble < 0)
		low_out = (self.lowNibble > 15 or self.lowNibble < 0)
		if high_out or low_out:
			print((
				'addr:', self.gbw_to_mp_address(self.group, self.bank, self.word) + 1, 'I:', self.I_Bit,
				'H:', self.H_Bit, 'highNibble:', self.highNibble, 'lowNibble:', self.lowNibble, 'blankType:',
				self.blankType, 'segmentData:', self.segmentData))

		if high_out and low_out:
			# Example - self.highNibble = 0b01000000
			# Example - self.lowNibble = 0b01000000
			print('Error: highNibble and lowNibble value out of range (0-15)dec')
			return 0
		elif high_out:
			# Example - self.highNibble = 0b01000000
			print('Error: highNibble value out of range (0-15)dec')
			return 0
		elif low_out:
			# Example - self.lowNibble = 0b01000000
			print('Error: lowNibble value out of range (0-15)dec')
			return 0
		else:
			return 1

	def _blank(self):
		# Blank value bitwise or BCD and set blankedFlag.
		self.blankedFlag = True
		if self.bitwise_Flag:
			value = 0x0
			if self.verbose:
				print('value 0')
		else:
			value = 0xf
			if self.verbose:
				print('value f')
		return value

	def _blank_check(self):
		# Perform blanking based on selected blank type.

		# Always blank section
		if self.blankType == 'AlwaysHighLow':
			self.highNibble = self._blank()
			self.lowNibble = self._blank()
		elif self.blankType == 'AlwaysHigh':
			self.highNibble = self._blank()
		elif self.blankType == 'AlwaysLow':
			self.lowNibble = self._blank()
		elif self.blankType == 'AlwaysZeroLow':
			self.lowNibble = 0

		# Numeric dependent section
		elif self.blankType == 'L':
			self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=None)
		elif self.blankType == 'H':
			self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=None)
		elif self.blankType == 'HL':
			self.highNibble, self.lowNibble = self._check_next(
				units=self.lowNibble, tens=self.highNibble,	hundreds_flag=None)
		elif self.blankType == 'LH':
			self.lowNibble, self.highNibble = self._check_next(
				units=self.highNibble, tens=self.lowNibble, hundreds_flag=None)
		elif self.blankType == 'IbL':
			self.I_Bit, self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=self.I_Bit)
		elif self.blankType == 'IbH':
			self.I_Bit, self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=self.I_Bit)
		elif self.blankType == 'HbL':
			self.H_Bit, self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=self.H_Bit)
		elif self.blankType == 'HbH':
			self.H_Bit, self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=self.H_Bit)
		elif self.blankType == 'IbHL':
			self.I_Bit, self.highNibble, self.lowNibble = self._check_next(
				units=self.lowNibble, tens=self.highNibble, hundreds_flag=self.I_Bit)
		elif self.blankType == 'IbLH':
			self.I_Bit, self.lowNibble, self.highNibble = self._check_next(
				units=self.highNibble, tens=self.lowNibble, hundreds_flag=self.I_Bit)
		elif self.blankType == 'HbHL':
			self.H_Bit, self.highNibble, self.lowNibble = self._check_next(
				units=self.lowNibble, tens=self.highNibble, hundreds_flag=self.H_Bit)
		elif self.blankType == 'HbLH':
			self.H_Bit, self.lowNibble, self.highNibble = self._check_next(
				units=self.highNibble, tens=self.lowNibble, hundreds_flag=self.H_Bit)
		elif self.blankType == 'NObHL':
			# Blank both if both zero
			# Example = MPLX3450-baseball,baseball,2,1,1,1,2,visualHornIndicator1,0,inningTens,inningUnits,NObHL,,
			self.highNibble, self.lowNibble = self._check_next(
				units=self.lowNibble, tens=self.highNibble, hundreds_flag=None, h_l_units_blank=True)

		# Isolated section
		elif self.blankType == 'IsolateHL':
			self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=None)
			self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=None)

			# word 3 or 4 and lowNibble is not zero then decode value, weird?
			if self.bitwise_Flag and self.lowNibble != 0:
				self.lowNibble = self.segment_decode(self.lowNibble)

		elif self.blankType == 'IsolateIbL_H':
			self.I_Bit, self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=self.I_Bit)
			self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=None)
		elif self.blankType == 'IsolateIbH_L':
			self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=None)
			self.I_Bit, self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=self.I_Bit)
		elif self.blankType == 'IsolateHbL_H':
			self.H_Bit, self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=self.H_Bit)
			self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=None)
		elif self.blankType == 'IsolateHbH_L':
			self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=None)
			self.H_Bit, self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=self.H_Bit)
		elif self.blankType == 'IsolateIbLHbH':
			self.I_Bit, self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=self.I_Bit)
			self.H_Bit, self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=self.H_Bit)
		elif self.blankType == 'IsolateIbHHbL':
			self.I_Bit, self.highNibble = self._check_next(units=self.highNibble, tens=None, hundreds_flag=self.I_Bit)
			self.H_Bit, self.lowNibble = self._check_next(units=self.lowNibble, tens=None, hundreds_flag=self.H_Bit)

	def _check_next(self, units=None, tens=None, hundreds_flag=None, h_l_units_blank=False):
		# Check higher place values and blank accordingly

		if units is None:
			print('You have to give me a units value to use this function!!!!')
			raise Exception

		if hundreds_flag is None:
			# No hundreds value

			if tens is None:
				# Units only zone
				# IsolateHL, H, L

				if units == 0:
					units = self._blank()

				return units

			else:
				# Tens and units zone
				# HL, LH

				if tens == 0:
					tens = self._blank()
				else:
					# Don't blank units if zero if tens is not zero
					h_l_units_blank = False

				# Blank all if zero and flag
				if units == 0 and h_l_units_blank:
					units = self._blank()

				return tens, units

		else:
			# Check hundreds

			if tens is None:
				# 1 and a half digit numbers with no tens

				if units == 0:
					units = self._blank()
				print('Do I ever use this?, from MpDataHandler._check_next')

				return hundreds_flag, units
			else:
				# 2 and a half digit numbers (199)

				if tens == 0:
					if not hundreds_flag:
						tens = self._blank()

				return hundreds_flag, tens, units

	def encode(
			self, group, bank, word, i_bit, h_bit, high_nibble, low_nibble,
			blank_type, segment_data, stat_flag=False, pass3_4_flag=False):
		"""Encodes the input data into an MP protocol two byte word formatted for its given blanking status."""
		self.group = group
		self.bank = bank
		self.word = word
		self.I_Bit = i_bit
		self.H_Bit = h_bit
		self.highNibble = high_nibble
		self.lowNibble = low_nibble
		self.blankType = blank_type
		self.segmentData = segment_data
		self.statFlag = stat_flag
		self.pass3_4Flag = pass3_4_flag

		if self.verbose:
			print((
				'addr:', self.gbw_to_mp_address(group, bank, word) + 1, 'I:', i_bit, 'H:', h_bit,
				'high_nibble', high_nibble, 'low_nibble', low_nibble, 'blank_type', blank_type,
				'segment_data', segment_data, 'stat_flag', stat_flag, 'pass3_4_flag', pass3_4_flag))

		# Clear data
		self.data = 0x0
		self.blankedFlag = False
		self.bitwise_Flag = False

		# Process data -----
		if self.segmentData != '' and self.segmentData != 0:
			# Process segment data

			if self.verbose:
				print('segment_data')

			self._segments_change(segment_data)  # Only accepts A-G characters, not case sensitive

			if h_bit:
				self.data = self.data | 0x80
			else:
				self.data = self.data & 0x17f

		elif self.pass3_4Flag:
			# Do not change data if word 3 or 4

			if self.verbose:
				print('pass3_4_flag')

			if word == 1 or word == 2:  # BCD
				self._blank_check()
				self.data = (self.highNibble << 4) | self.lowNibble
			elif word == 3 or word == 4:  # bitwise
				self.data = self.lowNibble
			else:
				print("ERROR - word must be int 1, 2, 3, or 4\n")

		elif self.statFlag:
			# Process stat style data

			if self.verbose:
				print('stat_flag')

			if self._value_range_check():  # If out of range skip formatting data
				if word == 1 or word == 2 or word == 3:  # BCD
					self._blank_check()
					self.data = (self.highNibble << 4) | self.lowNibble
				elif word == 4:  # bitwise
					pass
				else:
					print("ERROR - word must be int 1, 2, 3, or 4\n")

		else:
			# Normal Operation

			if self.verbose:
				print('Normal Operation')

			if self._value_range_check():  # If out of range skip formatting data
				if word == 1 or word == 2:  # BCD

					# Process blank type
					self._blank_check()

					# Format self.data
					self.data = (self.highNibble << 4) | self.lowNibble

				elif word == 3 or word == 4:  # bitwise or digit

					# Process blank type
					self.bitwise_Flag = 1
					self._blank_check()

					# Process digit type
					if not self.blankedFlag:
						self.lowNibble = self.segment_decode(self.lowNibble)

					# Format self.data
					self.data = self.lowNibble

					# Add H bit to self.data
					if h_bit:
						self.data = self.data | 0x80
					else:
						self.data = self.data & 0x17f
				else:
					print("ERROR - word must be int 1, 2, 3, or 4\n")

		# Add I bit to self.data -----
		if i_bit:
			self.data = self.data | 0x100
		else:
			self.data = self.data & 0xff

		# Format packet ----
		self._gbwd_to_segment_address()
		self._low_high_protocol_wrapper(self.seg_addr)

		return self.LH_Word

	# decode methods ------------------------------

	def decode(self, low_high__word):
		"""Decodes a MP protocol word and returns the group, bank, word, I Bit, and segments A-G."""
		seg_addr = self._low_high_protocol_unwrapper(low_high__word)
		group, bank, word, data = self._segment_address_to_gbwd(seg_addr)

		if (data & 0x0100) >> 8:
			i_bit = 1
		else:
			i_bit = 0
		numeric_data = (data & 0x00ff)

		return group, bank, word, i_bit, numeric_data

	def _low_high_protocol_unwrapper(self, low_high_word):
		low_high = ((low_high_word & 0x7f00) >> 1) | (low_high_word & 0x007f)
		self.lowByte = (low_high & 0x3f80) >> 7
		self.highByte = (low_high & 0x007f) << 7
		self.seg_addr = self.highByte | self.lowByte
		return self.seg_addr

	@staticmethod
	def _segment_address_to_gbwd(seg_addr):
		group = ((seg_addr & 0x2000) >> 13) + 1
		bank = ((seg_addr & 0x1800) >> 11) + 1
		word = ((seg_addr & 0x0600) >> 9) + 1
		data = (seg_addr & 0x1ff)
		return group, bank, word, data

	@staticmethod
	def numeric_data_decode(numeric_data):
		"""Returns the decimal value of the 7 segment Character 0-9 and A-F."""
		# PUBLIC static method
		segment_table = [  # HGFEDCBA
			0b00111111,  # 0 = ABCDEF
			0b00000110,  # 1 =  BC
			0b01011011,  # 2 = AB DE G
			0b01001111,  # 3 = ABCD  G
			0b01100110,  # 4 =  BC  FG
			0b01101101,  # 5 = A CD FG
			0b01111101,  # 6 = A CDEFG
			0b00000111,  # 7 = ABC
			0b01111111,  # 8 = ABCDEFG
			0b01101111,  # 9 = ABCDFG
			0b01110111,  # A = ABCEFG
			0b01111100,  # b = CDEFG
			0b01111001,  # C = ADEFG
			0b01011110,  # d = BCDEG
			0b01111001,  # E = ADEFG
			0b01110001,  # F = AEFG
			0b00000000  # blank = ''
		]
		for digit, value in enumerate(segment_table):
			if value == numeric_data:
				numeric_data = digit
				break  # this avoids value 0 also calling value blank
		return numeric_data
