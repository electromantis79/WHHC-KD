#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
**COMPLETION** = 100%  Sphinx Approved = **True**

.. topic:: Overview

    This module manipulates MP style data.

    :Created Date: 3/12/2015
    :Modified Date: 9/1/2016
    :Author: **Craig Gunter**

'''

class MP_Data_Handler(object):
	'''Creates an object to manipulate MP style data.'''
	def __init__ (self):
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
		self.verbose=False
		self.pass3_4Flag=False
		self.bitwise_Flag=False

	def GBW_to_MP_Address (self, group, bank, word): #Can be used externaly
		'''Returns MP format address.'''
		#print group, bank, word
		self.addr = (((( (group-1) << 2) | (bank-1)) << 2) | (word-1))
		#print 'addr', bin(self.addr)
		return self.addr

	def _GBWD_to_Segment_Address (self):#2
		'''Builds the segment address from the group, bank, word, and data.'''
		self.seg_addr = (self.GBW_to_MP_Address(self.group, self.bank, self.word) << 9) | self.data

	def _lowHigh_Protocol_Wrapper (self, seg_addr):#3
		'''Converts the Low and High Byes into the LowHigh Word format. (0LLLLLLL 1HHHHHHH)'''
		#print 'segaddr', bin(seg_addr)
		self.highByte = ((seg_addr & 0x3f80) >> 7) | 0x80
		#print bin(self.highByte)
		self.lowByte = (seg_addr & 0x007f)
		#print bin(self.lowByte)
		self.LH_Word = (self.lowByte << 8) | (self.highByte)

		if self.verbose:
			print "LH Word:0x%02X%02X" % (self.lowByte, self.highByte),
			print bin(self.LH_Word), self.LH_Word,
			print "GBWD: G%d B%d W%d %s" % (self.group, self.bank, self.word, bin(self.data))

		return self.LH_Word

	def _segmentsChange (self, segments):
		try:
			segments = list(segments.lower())
		except:
			if self.verbose:
				print '_segmentsChange received segment value', segments
		#print segments
		self.segData = 0b00000000
		if segments is not None:
			for seg in segments:
				if seg=='a':
					self.segData = self.segData | 0b00000001
				elif seg=='b':
					self.segData = self.segData | 0b00000010
				elif seg=='c':
					self.segData = self.segData | 0b00000100
				elif seg=='d':
					self.segData = self.segData | 0b00001000
				elif seg=='e':
					self.segData = self.segData | 0b00010000
				elif seg=='f':
					self.segData = self.segData | 0b00100000
				elif seg=='g':
					self.segData = self.segData | 0b01000000
				self.data = self.segData

	def _segmentDecode (self, digit, segLookup=0):
		if digit is not None:
			if not segLookup:
				if self.verbose:
					print "segDecode:%2d"%digit
				SegmentTable = [#        HGFEDCBA
				0b00111111, # 0 = ABCDEF
				0b00000110, # 1 =  BC
				0b01011011, # 2 = AB DE G
				0b01001111, # 3 = ABCD  G
				0b01100110, # 4 =  BC  FG
				0b01101101, # 5 = A CD FG
				0b01111101, # 6 = A CDEFG
				0b00000111, # 7 = ABC
				0b01111111, # 8 = ABCDEFG
				0b01101111, # 9 = ABCDFG
				0b01110111, # A = ABCEFG
				0b01111100, # b = CDEFG
				0b01111001, # C = ADEFG
				0b01011110, # d = BCDEG
				0b01111001, # E = ADEFG
				0b01110001  # F = AEFG
				]
			else:
				#segLookup is used in Driver.py
				SegmentTable = [
				'ABCDEF', # 0
				'BC', # 1
				'ABDEG', # 2
				'ABCDG', # 3
				'BCFG', # 4
				'ACDFG', # 5
				'ACDEFG', # 6
				'ABC', # 7
				'ABCDEFG', # 8
				'ABCDFG', # 9
				'ABCEFG', # A
				'CDEFG', # b
				'ADEFG', # C
				'BCDEG', # d
				'ADEFG', # E
				'AEFG'  # F
				]
				if self.verbose:
					print "Inverse segDecode:",SegmentTable[digit]
			try:
				digit = SegmentTable[digit]
			except:
				print '_segmentDecode ERROR digit =', digit
		return digit

	def _valueRangeCheck (self):
		'''Check if nibbles are out of range, if so print.'''
		#Do we need to change the nibble values?
		
		Return=1
		highOut=(self.highNibble > 15 or self.highNibble < 0)
		lowOut=(self.lowNibble > 15 or self.lowNibble < 0)
		if highOut and lowOut:
			#self.highNibble = 0b01000000
			#self.lowNibble = 0b01000000
			print 'Error: highNibble and lowNibble value out of range (0-15)dec'
			Return=0
		elif highOut:
			#self.highNibble = 0b01000000
			print 'Error: highNibble value out of range (0-15)dec'
			Return=0
		elif lowOut:
			#self.lowNibble = 0b01000000
			print 'Error: lowNibble value out of range (0-15)dec'
			Return=0

		if not Return:
			print 'addr:', self.GBW_to_MP_Address(self.group, self.bank, self.word)+1, 'I:', self.I_Bit, 'H:', self.H_Bit, \
			'highNibble:', self.highNibble, 'lowNibble:', self.lowNibble, 'blankType:', self.blankType, 'segmentData:', self.segmentData	
					
		return Return

	def _blank(self, value):
		'''Blank value bitwise or BCD and set blankedFlag.'''
		self.blankedFlag=True
		if self.bitwise_Flag:
			value=0x0
			if self.verbose:
				print 'value 0'
		else:
			value=0xf
			if self.verbose:
				print 'value f'
		return value

	def _blankCheck(self):
		'''Perform blanking based on selected blank type.'''
		
		#Always blank section
		if self.blankType=='AlwaysHighLow':
			self.highNibble = self._blank(self.highNibble)
			self.lowNibble = self._blank(self.lowNibble)
		elif self.blankType=='AlwaysHigh':
			self.highNibble = self._blank(self.highNibble)
		elif self.blankType=='AlwaysLow':
			self.lowNibble = self._blank(self.lowNibble)
		elif self.blankType=='AlwaysZeroLow':
			self.lowNibble = 0
			
		#Numeric dependent section
		elif self.blankType=='L':
			self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=None)
		elif self.blankType=='H':
			self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=None)
		elif self.blankType=='HL':
			self.highNibble, self.lowNibble = self._checkNext(units=self.lowNibble, tens=self.highNibble, hundredsFlag=None)
		elif self.blankType=='LH':
			self.lowNibble, self.highNibble = self._checkNext(units=self.highNibble, tens=self.lowNibble, hundredsFlag=None)
		elif self.blankType=='IbL':
			self.I_Bit, self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=self.I_Bit)
		elif self.blankType=='IbH':
			self.I_Bit, self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=self.I_Bit)
		elif self.blankType=='HbL':
			self.H_Bit, self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=self.H_Bit)
		elif self.blankType=='HbH':
			self.H_Bit, self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=self.H_Bit)
		elif self.blankType=='IbHL':
			self.I_Bit, self.highNibble, self.lowNibble = self._checkNext(units=self.lowNibble, tens=self.highNibble, hundredsFlag=self.I_Bit)
		elif self.blankType=='IbLH':
			self.I_Bit, self.lowNibble, self.highNibble = self._checkNext(units=self.highNibble, tens=self.lowNibble, hundredsFlag=self.I_Bit)
		elif self.blankType=='HbHL':
			self.H_Bit, self.highNibble, self.lowNibble = self._checkNext(units=self.lowNibble, tens=self.highNibble, hundredsFlag=self.H_Bit)
		elif self.blankType=='HbLH':
			self.H_Bit, self.lowNibble, self.highNibble = self._checkNext(units=self.highNibble, tens=self.lowNibble, hundredsFlag=self.H_Bit)
		elif self.blankType=='NObHL':
			#Blank both if both zero
			#Example = MPLX3450-baseball,baseball,2,1,1,1,2,visualHornIndicator1,0,inningTens,inningUnits,NObHL,,
			self.highNibble, self.lowNibble = self._checkNext(units=self.lowNibble, tens=self.highNibble, hundredsFlag=None, HL_unitsBlank=True)
			
		#Isolated section
		elif self.blankType=='IsolateHL':
			self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=None)
			self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=None)
			
			#word 3 or 4 and lowNibble is not zero then decode value, weird?
			if self.bitwise_Flag and self.lowNibble!=0:
				self.lowNibble = self._segmentDecode(self.lowNibble)
				
		elif self.blankType=='IsolateIbL_H':
			self.I_Bit, self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=self.I_Bit)
			self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=None)
		elif self.blankType=='IsolateIbH_L':
			self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=None)
			self.I_Bit, self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=self.I_Bit)
		elif self.blankType=='IsolateHbL_H':
			self.H_Bit, self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=self.H_Bit)
			self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=None)
		elif self.blankType=='IsolateHbH_L':
			self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=None)
			self.H_Bit, self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=self.H_Bit)
		elif self.blankType=='IsolateIbLHbH':
			self.I_Bit, self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=self.I_Bit)
			self.H_Bit, self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=self.H_Bit)
		elif self.blankType=='IsolateIbHHbL':
			self.I_Bit, self.highNibble = self._checkNext(units=self.highNibble, tens=None, hundredsFlag=self.I_Bit)
			self.H_Bit, self.lowNibble = self._checkNext(units=self.lowNibble, tens=None, hundredsFlag=self.H_Bit)

	def _checkNext(self, units=None, tens=None, hundredsFlag=None, HL_unitsBlank=False):
		'''Check higher place values and blank accordingly.'''
		
		if units is None:
			raise error('You have to give me a units value to use this function!!!!')
			
		if hundredsFlag is None:
			#No hundereds value
			
			if tens is None:
				#Units only zone
				#IsolateHL, H, L
				
				if units==0:
					units=self._blank(units)
					
				#print units
				return units
				
			else:
				#Tens and units zone
				#HL, LH
				
				if tens==0:
					tens=self._blank(tens)
				else:
					#Don't blank units if zero if tens is not zero
					HL_unitsBlank=False
				
				#Blank all if zero and flag
				if units==0 and HL_unitsBlank:
					units=self._blank(units)
					
				#print tens, units
				return tens, units

		else:
			#Check hundreds
			
			if tens is None:
				#1 and a half digit numbers with no tens
				
				if units==0:
					units=self._blank(units)
				print 'Do I ever use this?, from MP_Data_Handler._checkNext'
					
				#print hundredsFlag, units
				return hundredsFlag, units
			else:
				#2 and a half digit numbers (199)
				
				if tens==0:
					if not hundredsFlag:
						tens=self._blank(tens)
						
				#print hundredsFlag, tens, units
				return hundredsFlag, tens, units

		print 'missed it somehow!!!!!!!!!!!'
		raise

	def Encode (self, group, bank, word, I_Bit, H_Bit, highNibble, lowNibble, blankType, segmentData, statFlag=False, pass3_4Flag=False):
		'''Encodes the input data into an MP protocol two byte word formated for its given blanking status.'''
		self.group = group
		self.bank = bank
		self.word = word
		self.I_Bit = I_Bit
		self.H_Bit = H_Bit
		self.highNibble = highNibble
		self.lowNibble = lowNibble
		self.blankType = blankType
		self.segmentData = segmentData
		self.statFlag=statFlag
		self.pass3_4Flag=pass3_4Flag

		if self.verbose:
			print 'addr:', self.GBW_to_MP_Address(group, bank, word)+1, 'I:', I_Bit, 'H:', H_Bit, \
			'highNibble', highNibble, 'lowNibble', lowNibble, 'blankType', blankType, \
			'segmentData', segmentData, 'statFlag', statFlag, 'pass3_4Flag', pass3_4Flag
		
		#Clear data	
		self.data = 0x0
		self.blankedFlag = False
		self.bitwise_Flag = False

		#Process data -----
		if self.segmentData!='' and self.segmentData!=0:
			#Process segment data
			
			if self.verbose:
				print 'segmentData'
				
			self._segmentsChange(segmentData) #Only accepts A-G characters, not case sensitive
			
			if H_Bit:
				self.data = self.data | 0x80
			else:
				self.data = self.data & 0x17f
				
		elif self.pass3_4Flag:
			#Do not change data if word 3 or 4
			
			if self.verbose:
				print 'pass3_4Flag'
				
			if word==1 or word==2:#BCD
				self._blankCheck()
				self.data = (self.highNibble << 4) | (self.lowNibble)
			elif word==3 or word==4:#bitwise
				self.data = self.lowNibble
				#print 'self.data, self.lowNibble', self.data , self.lowNibble
			else:
				print "ERROR - word must be int 1, 2, 3, or 4\n"
				
		elif self.statFlag:
			#Process stat style data
			
			if self.verbose:
				print 'statFlag'
				
			if self._valueRangeCheck():
				#If out of range skip formatting data		
					
				if word==1 or word==2 or word==3:#BCD
					self._blankCheck()
					self.data = (self.highNibble << 4) | (self.lowNibble)
				elif word==4:#bitwise
					pass
				else:
					print "ERROR - word must be int 1, 2, 3, or 4\n"	
							
		else:
			#Normal Operation
			
			if self.verbose:
				print 'Normal Operation'
				
			if self._valueRangeCheck():
				#If out of range skip formatting data
				
				if word==1 or word==2:
					#BCD
					
					#Process blank type
					self._blankCheck()
					
					#Format self.data
					self.data = (self.highNibble << 4) | (self.lowNibble)
					
				elif word==3 or word==4:
					#bitwise or digit
										
					#Process blank type
					self.bitwise_Flag=1
					self._blankCheck()

					#Process digit type
					if not self.blankedFlag:
						self.lowNibble = self._segmentDecode(self.lowNibble)
					#print self.lowNibble
					
					#Format self.data
					self.data = self.lowNibble
					
					#Add H bit to self.data
					if H_Bit:
						self.data = self.data | 0x80
					else:
						self.data = self.data & 0x17f
				else:
					print "ERROR - word must be int 1, 2, 3, or 4\n"

		#Add I bit to self.data -----
		if I_Bit:
			self.data = self.data | 0x100
		else:
			self.data = self.data & 0xff

		#Format packet ----
		self._GBWD_to_Segment_Address()
		self._lowHigh_Protocol_Wrapper(self.seg_addr)
		
		return self.LH_Word

		#THE FLIP SIDE.....
	def _lowHigh_Protocol_UNWrapper (self, LH_Word):
		#print 'LH_Word', bin(LH_Word)
		LH = ((LH_Word & 0x7f00) >> 1) | (LH_Word & 0x007f)
		#print 'LH', bin(LH)
		self.lowByte = ((LH & 0x3f80) >> 7)
		self.highByte = (LH & 0x007f)  << 7
		self.seg_addr = self.highByte | self.lowByte
		#print 'segaddr', bin(self.seg_addr)
		return self.seg_addr

	def _Segment_Address_to_GBWD (self, seg_addr):#1
		group = ((seg_addr & 0x2000) >> 13)+1
		#print 'group', bin(self.group)
		bank = ((seg_addr & 0x1800) >> 11)+1
		#print 'bank', bin(self.bank)
		word = ((seg_addr & 0x0600) >> 9)+1
		#print 'word', bin(self.word)
		data = (seg_addr & 0x1ff)
		#print 'data', bin(self.data)
		return group, bank, word, data

	def numericDataDecode(self, numericData): #Can be used externaly
		'''Returns the decimal value of the 7 segment Character 0-9 and A-F.'''
		SegmentTable = [#        HGFEDCBA
		0b00111111, # 0 = ABCDEF
		0b00000110, # 1 =  BC
		0b01011011, # 2 = AB DE G
		0b01001111, # 3 = ABCD  G
		0b01100110, # 4 =  BC  FG
		0b01101101, # 5 = A CD FG
		0b01111101, # 6 = A CDEFG
		0b00000111, # 7 = ABC
		0b01111111, # 8 = ABCDEFG
		0b01101111, # 9 = ABCDFG
		0b01110111, # A = ABCEFG
		0b01111100, # b = CDEFG
		0b01111001, # C = ADEFG
		0b01011110, # d = BCDEG
		0b01111001, # E = ADEFG
		0b01110001, # F = AEFG
		0b00000000  # blank = ''
		]
		for digit, value in enumerate(SegmentTable):
			if value==numericData:
				numericData=digit
				break #this avoids value 0 also calling value blank								
				
		return numericData

	def Decode(self, LH_Word):
		'''Decodes a MP protocol word and returns the group, bank, word, I Bit, and segments A-G.'''
		seg_addr = self._lowHigh_Protocol_UNWrapper(LH_Word)
		group, bank, word, data = self._Segment_Address_to_GBWD(seg_addr)

		if ((data & 0x0100) >> 8):
			I_Bit = 1
		else:
			I_Bit = 0
		numericData = (data & 0x00ff)

		return group, bank, word, I_Bit, numericData

def test():
	'''Test function if module ran independently.'''
	print "Program Started\n"
	mp=MP_Data_Handler()
	choice=100
	mpOUT=MP_Data_Handler()

	while choice:
		if choice == 100:
			print
			print '0 - Quit'
			#print "1 - _Segment_Address_to_GBWD"
			print "2 - _GBWD_to_Segment_Address"
			print "3 - _lowHigh_Protocol_Wrapper"
			#print "4 - lowHigh_Protocol_UNWrapper"
			#print "5 - _toggle_segment"
			print "6 - _segmentsChange"
			print "7 - _digitChange"
			print "8 - _BCDchange"
			#print "9 - MP_Address_to_GBWD"
			#print "10 - GBWD_to_MP_Address"
			print "11 - _blankChange"
			print "12 - Encode"
			print '13 - Decode'
			print '14 - Encode then Decode'
			try:
				choice = input("\nWhich do you select? ")
			except:
				choice=100
				pass
			print

		elif choice == 2:
			data1 = input("Input Group: ")
			data2 = input("Input Bank: ")
			data3 = input("Input Word: ")
			data4 = int(float.fromhex(raw_input("Input hex Data: ")))
			print "Segment Address: 0x%X" % mp._GBWD_to_Segment_Address(data1, data2, data3, data4)
			choice = 100

		elif choice == 3:
			data = int(float.fromhex(raw_input("Input 14-bit hex value to be converted: ")))
			#print "Wrapped LowHigh Word: %X" % mp._lowHigh_Protocol_Wrapper(data)
			print "Data before: %s, Data after: %s" % (bin(data), bin(mp._lowHigh_Protocol_Wrapper(data)))
			choice = 100


		elif choice == 6:
			data = int(float.fromhex(raw_input("Input hex Data: ")))
			segment = raw_input("Input character string a to g to be set: ")
			print "Data before: 0x%X, Data after: 0x%X" % (data, mp._segmentsChange(segment, data))
			choice = 100

		elif choice == 7:
			data = int(float.fromhex(raw_input("Input hex Data: ")))
			digit = int(float.fromhex(raw_input("Input a digit to be added to data: ")))
			print "Data before: 0x%X, Data after: 0x%X" % (data, mp._digitChange(digit, data))
			choice = 100

		elif choice == 8:
			data = int(float.fromhex(raw_input("Input hex Data: ")))
			digit = input("Input a a 2 digit number to be added to data in BCD: ")
			print "Data before: 0x%X, Data after: 0x%X" % (data, mp._BCDchange(digit, data))
			choice = 100

		elif choice == 11:
			data1 = raw_input("Input Data Format: ")
			data2 = input("Input Numeric Data: ")
			data3 = input("Input 1 for Blank if Zero: ")
			data4 = input("Input 1 for Place Holder: ")
			print "Data Blanked: 0x%X" % mp._blankChange(data1, data2, data3, data4)
			choice = 100

		elif choice == 12:
			data1 = input("Input Group: ")
			data2 = input("Input Bank: ")
			data3 = input("Input Word: ")
			data4 = input("Input I Segment: ")
			data5 = input("Input H Segment: ")
			data6 = input("Input High Nibble: ")
			data7 = input("Input Low Nibble: ")
			data8 = input("Input Blank Type: ")
			data9 = raw_input("Input Segment Data: ")
			data10 = input("Input pass3_4Flag: ")

			print
			print "data = 0x%03X" % mp.data
			print "addr = 0x%02X" % mp.addr
			print "highNibble = ", mp.highNibble
			print "lowNibble = ", mp.lowNibble
			print "blankType = ", mp.blankType
			print "segmentData = ", mp.segmentData
			print "group = ", mp.group
			print "bank = ", mp.bank
			print "word = ", mp.word
			print "I_Bit = ", mp.I_Bit
			print "H_Bit = ", mp.H_Bit
			print "LH_Word = %s" % mp.LH_Word
			print "seg_addr = 0x%04X" % mp.seg_addr
			print "Input pass3_4Flag = ", mp.pass3_4Flag
			print
			mpEncode = mp.Encode(data1, data2, data3, data4, data5, data6, data7, data8, data9, pass3_4Flag=data10)
			print "Encoded Data: 0x%02X%02X" % (mp.lowByte, mp.highByte)
			print
			print "data = 0x%03X" % mp.data
			print "addr = 0x%02X" % mp.addr
			print "highNibble = ", mp.highNibble
			print "lowNibble = ", mp.lowNibble
			print "blankType = ", mp.blankType
			print "segmentData = ", mp.segmentData
			print "group = ", mp.group
			print "bank = ", mp.bank
			print "word = ", mp.word
			print "I_Bit = ", mp.I_Bit
			print "H_Bit = ", mp.H_Bit
			print "LH_Word = %s" % mp.LH_Word
			print "seg_addr = 0x%04X" % mp.seg_addr
			print "Input pass3_4Flag = ", mp.pass3_4Flag
			print
			choice = 100

		elif choice == 13:
			data3 = input("Input LH_Word: ")

			print
			print "data = 0x%03X" % mp.data
			print "addr = 0x%02X" % mp.addr
			print "numericData = ", mp.numericData
			print "blankIFzero = ", mp.blankIFzero
			print "placeHolder = ", mp.placeHolder
			print "segmentData = ", mp.segmentData
			print "group = ", mp.group
			print "bank = ", mp.bank
			print "word = ", mp.word
			print "I_Bit = ", mp.I_Bit
			print "H_Bit = ", mp.H_Bit
			print "LH_Word = %s" % mp.LH_Word
			print "seg_addr = 0x%04X" % mp.seg_addr
			print
			mpDecode = mp.Decode(data3)
			print
			print "data = 0x%03X" % mp.data
			print "addr = 0x%02X" % mp.addr
			print "numericData = ", mp.numericData
			print "blankIFzero = ", mp.blankIFzero
			print "placeHolder = ", mp.placeHolder
			print "segmentData = ", mp.segmentData
			print "group = ", mp.group
			print "bank = ", mp.bank
			print "word = ", mp.word
			print "I_Bit = ", mp.I_Bit
			print "H_Bit = ", mp.H_Bit
			print "LH_Word = %s" % mp.LH_Word
			print "seg_addr = 0x%04X" % mp.seg_addr
			print
			choice = 100

		elif choice == 14:
			data1 = input("Input Group: ")
			data2 = input("Input Bank: ")
			data3 = input("Input Word: ")
			data4 = input("Input I Segment: ")
			data5 = input("Input H Segment: ")
			data6 = input("Input High Nibble: ")
			data7 = input("Input Low Nibble: ")
			data8 = input("Input Blank Type: ")
			data9 = raw_input("Input Segment Data: ")

			print
			print "data = 0x%03X" % mp.data
			print "addr = 0x%02X" % mp.addr
			print "highNibble = ", mp.highNibble
			print "lowNibble = ", mp.lowNibble
			print "blankType = ", mp.blankType
			print "segmentData = ", mp.segmentData
			print "group = ", mp.group
			print "bank = ", mp.bank
			print "word = ", mp.word
			print "I_Bit = ", mp.I_Bit
			print "H_Bit = ", mp.H_Bit
			print "LH_Word = %s" % mp.LH_Word
			print "seg_addr = 0x%04X" % mp.seg_addr
			print
			mpEncode = mp.Encode(data1, data2, data3, data4, data5, data6, data7, data8, data9)
			print "Encoded Data: 0x%02X%02X" % (mp.lowByte, mp.highByte)
			print
			print "data = 0x%03X" % mp.data
			print "addr = 0x%02X" % mp.addr
			print "highNibble = ", mp.highNibble
			print "lowNibble = ", mp.lowNibble
			print "blankType = ", mp.blankType
			print "segmentData = ", mp.segmentData
			print "group = ", mp.group
			print "bank = ", mp.bank
			print "word = ", mp.word
			print "I_Bit = ", mp.I_Bit
			print "H_Bit = ", mp.H_Bit
			print "LH_Word = %s" % mp.LH_Word
			print "seg_addr = 0x%04X" % mp.seg_addr
			print
			mpOUTDecode = mpOUT.Decode(mpEncode)

			print "group = ", mpOUT.group
			print "bank = ", mpOUT.bank
			print "word = ", mpOUT.word
			print "I_Bit = ", mpOUT.I_Bit
			print "numericData = ", mpOUT.numericData
			choice = 100

		elif choice == 0:
			break
		else:
			choice = 100

'''
		elif choice == 1:
			data = int(float.fromhex(raw_input("Input 14-bit hex value to be converted: ")))
			print "Group: %X, Bank: %X, Word: %X, Data: 0x%X" % mp._Segment_Address_to_GBWD(data)
			choice = 100
'''
'''
		elif choice == 4:
			data = int(float.fromhex(raw_input("Input 14-bit hex value to be converted: ")))
			#print "UN-Wrapped LowHigh Word: %X" % mp.lowHigh_Protocol_UNWrapper(data)
			print "Data before: 0x%X, Data after: 0x%X" % (data, mp._lowHigh_Protocol_UNWrapper(data))
			choice = 100


		elif choice == 5:
			data = int(float.fromhex(raw_input("Input hex Data: ")))
			segment = raw_input("Input a character a to i to be toggled: ")
			print "Data before: 0x%X, Data after: 0x%X" % (data, mp._toggle_segment(segment, data))
			choice = 100
'''
'''
		elif choice == 9:
			data = int(float.fromhex(raw_input("Input 5-bit hex value to be converted: ")))
			print "Group: %X, Bank: %X, Word: %X" % mp.MP_Address_to_GBW(data)
			choice = 100

		elif choice == 10:
			data1 = input("Input Group: ")
			data2 = input("Input Bank: ")
			data3 = input("Input Word: ")
			print "Segment Address: 0x%X" % mp._GBW_to_MP_Address(data1, data2, data3)
			choice = 100
'''

if __name__ == '__main__':
	test()
