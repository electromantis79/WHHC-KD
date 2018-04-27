#!/usr/bin/python
# # -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module handles MP style communication on the native serial ports.

	:Created Date: 3/16/2015
	:Author: **Craig Gunter**

"""

import app.serial_IO.serial_packet
import app.utils.Platform


class MpSerialHandler(object):
	"""Creates a serial port object."""

	def __init__(self, timeout=0, serial_input_type='MP', verbose_flag=False, game=None):
		self.timeout = timeout
		self.serialInputType = serial_input_type
		self.verboseFlag = verbose_flag
		self.game = game

		# Variables
		self.receiveList = []
		self.packet = ''
		self.ETNpacketList = []

		# Prepare for ETN packet inspection
		self.sp = app.serial_IO.serial_packet.SerialPacket(self.game)

		# Mulit-platform support
		platform = app.utils.Platform.platform_detect()
		if platform == 2:
			import Adafruit_BBIO.UART as UART
			import serial
			UART.setup('UART1')
			port_name = '/dev/ttyO1'
		elif platform == 1:
			import serial
			port_name = '/dev/ttyS0'
		else:
			print ("Don't work on windows yet")
			return  # Needed to skip the rest of __init__

		# Select input type
		if self.serialInputType == 'MP':
			self.previousLowByte = None
			self.maxBytes = 10
			self.timeout = 0
		elif self.serialInputType == 'ASCII':
			self.maxBytes = 250
			self.timeout = 0.008

		# Setup serial port
		print ('port_name', port_name)
		# 2400 baud is for wifi demo to match MIC revision used, normally 38400
		self.ser = serial.Serial(port=port_name, baudrate=2400, bytesize=8, timeout=self.timeout)

		# TODO: Do I need these 3 lines?
		self.ser.close()
		self.ser.open()
		self.ser.flushInput()

	# PUBLIC methods

	def serial_input(self):
		"""Handles serial input."""
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
						byte_type = 'high'
						if self.previousLowByte is not None:
							word = (self.previousLowByte << 8) + byte
							self.receiveList.append(word)
					else:
						byte_type = 'low'
						self.previousLowByte = byte
					if self.verboseFlag:
						print (byte)

				if self.verboseFlag and data_out:
					print (byte_type, byte)
					print ('self.receiveList', self.receiveList)
					if self.ser.inWaiting():
						print (self.ser.inWaiting(), 'bytes in buffer')

			except:
				print ('ERROR _serial_input function')

			if self.verboseFlag:
				print ('---')

		elif self.serialInputType == 'ASCII':
			if self.verboseFlag:
				print ('ASCII')
			try:
				self.packet = self.ser.read(self.maxBytes)

				# Check if packet is ETN format and append to list
				if self.sp.etn_check(self.packet):
					self.ETNpacketList.append(self.packet)
				if self.verboseFlag and len(self.ETNpacketList) > 0:
					print ('-----len(self.ETNpacketList', len(self.ETNpacketList))

			except:
				print ('ERROR _serial_input function')
			if self.verboseFlag:
				print (self.packet)

	def serial_output(self, data):
		"""Handles serial output."""
		try:
			self.ser.write(data)
		except:
			print ('ERROR serial output function')
