#!/usr/bin/python
# # -*- coding: utf-8 -*-

"""

.. topic:: Overview

    This module handles MP style communication on the native serial ports.

    :Created Date: 3/16/2015
    :Author: **Craig Gunter**

"""

import app.serial_IO.serial_packet
import app.serial_IO.Platform


class MP_Serial_Handler(object):
	"""Creates a serial port object."""

	def __init__(self, timeout=0, serialInputType='MP', verboseFlag=False, game=None):
		self.serialInputType = serialInputType
		self.verboseFlag = verboseFlag
		self.game = game

		# Variables
		self.receiveList = []
		self.packet = ''
		self.ETNpacketList = []

		# Prepare for ETN packet inspection
		self.sp = app.serial_IO.serial_packet.SerialPacket(self.game)
		self.sp.ETNFlag = False
		self.sp.decodePacket = 'from serial ETN check'
		self.sp.MPserial = True

		# Mulit-platform support
		PLATFORM = app.serial_IO.Platform.platform_detect()
		if PLATFORM == 2:
			import Adafruit_BBIO.UART as UART
			import serial
			UART.setup('UART1')
			portName = '/dev/ttyO1'
		elif PLATFORM == 1:
			import serial
			portName = '/dev/ttyS0'
		else:
			print ("Don't work on windows yet")
			return  # Needed to skip the rest of __init__

		# Select input type
		if self.serialInputType == 'MP':
			self.previousLowByte = None
			self.maxBytes = 10
		elif self.serialInputType == 'ASCII':
			timeout = 0.008
			self.maxBytes = 1024

		# Setup serial port
		print ('portName', portName)
		self.ser = serial.Serial(port=portName, baudrate=38400, bytesize=8, timeout=timeout)

		# TODO: Do I need these 3 lines?
		self.ser.close()
		self.ser.open()
		self.ser.flushInput()

	# PUBLIC methods

	def serialInput(self):
		if self.serialInputType == 'MP':
			"""Handles serial input."""

			if self.verboseFlag:
				print ('---- self.previousLowByte', self.previousLowByte)
			try:
				
				data_out = bytearray(self.ser.read(1))

				if self.verboseFlag:
					print ('data_out', data_out)
				for x, byte in enumerate(data_out):
					if byte > 127:
						byteType = 'high'
						if self.previousLowByte is not None:
							word = (self.previousLowByte << 8)+byte
							self.receiveList.append(word)
					else:
						byteType = 'low'
						self.previousLowByte = byte
					if self.verboseFlag:
						print (byte)

				if self.verboseFlag and data_out:
					print (byteType, byte)
					print ('self.receiveList', self.receiveList)
					if self.ser.inWaiting():
						print (self.ser.inWaiting(), 'bytes in buffer')

			except:
				print ('ERROR serialInput function')

			if self.verboseFlag:
				print ('---')
				
		elif self.serialInputType == 'ASCII':
			if self.verboseFlag:
				print ('ASCII')
			try:
				self.packet = self.ser.read(self.maxBytes)
				string = ''
				self.sp._version_i_d_byte(string, packet=self.packet, length_check=1)
				if self.sp.ETNFlag:
					self.sp.ETNFlag = False
					self.ETNpacketList.append(self.packet)
				if self.verboseFlag and len(self.ETNpacketList) > 0:
					print ('-----len(self.ETNpacketList', len(self.ETNpacketList))
			except:
				print ('ERROR serialInput function')
			if self.verboseFlag:
				print (self.packet)

	def serialOutput(self, data):
		"""Handles serial output."""
		data_in = data
		try:
			self.ser.write(data_in)
		except:
			print ('ERROR serial output function')

# TODO: clean this function and create real test functions

	"""
def test():
	'''Test function if module ran independently.
	Called in a thread every serialInputRefreshFrequency.
	'''
	tic = time.time()
	count = 0
	byte = s.ser.inWaiting()
	if byte:
		count += 1
	elapseTime(s.serialInput, On=False)
	toc = time.time()
	elaps = toc-tic
	print 'Test', byte, elaps, (tic-1446587172)


if __name__ == '__main__':
	import thread, threading, time, timeit, os, sys
	from sys import platform as _platform
	from threading import Thread
	
	from app.MP_Data_Handler import MP_Data_Handler
	s = MP_Serial_Handler(verbose=False)
	mp = MP_Data_Handler()
	serialInputRefreshFrequency = .001
	refresherSerialInput = Thread(target=threadTimer, args=(test, serialInputRefreshFrequency))
	#refresherSerialInput.daemon=True
	verbose(['\nSerial Input On'], 1)
	refresherSerialInput.start()
	#test(serialInputRefreshFrequency)
	stop=1
	while stop:
		#This is where we wait while test function thread runs
		stop-=1
		sleep(2)
	for words in s.receiveList:
		group, bank, word, I_Bit, numericData = mp.Decode(words)
		print  'group', group, 'bank', bank, 'word', word, 'addr', mp.GBW_to_MP_Address(
			group, bank, word)+1, 'I_Bit', I_Bit, 'data', bin(numericData), bin(words)
	'''
	try:
		s.ser.close()
	except:
		print 'ERROR close'
	'''
	print 'DONE'
	
	"""
