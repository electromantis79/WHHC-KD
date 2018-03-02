#!/usr/bin/python
# # -*- coding: utf-8 -*-

"""
**COMPLETION** = 100%  Sphinx Approved = **True**

.. topic:: Overview

    This module handles MP style communication on the native serial ports Biotch.

    :Created Date: 3/16/2015
    :Modified Date: 10/24/2016
    :Author: **Craig Gunter**

"""
from functions import *
from time import sleep
from serial_packet_Class import Serial_Packet

class MP_Serial_Handler(object):
	'''Creates a serial port object.'''
	def __init__(self, timeout=0, serialInputType='MP', verbose=False, game=None):
		self.serialInputType=serialInputType
		self.verbose=verbose
		self.game=game
		PLATFORM=platform_detect()

		if PLATFORM==2:
			import Adafruit_BBIO.GPIO as GPIO
			import Adafruit_BBIO.UART as UART
			import serial
			UART.setup('UART1')
			portName='/dev/ttyO1'
		elif PLATFORM==1:
			import RPi.GPIO as GPIO
			import serial
			portName='/dev/ttyS0'
		else:
			self.ser="Don't work on windows yet"
			print self.ser
			return
			
		if self.serialInputType=='MP':
			self.previousLowByte=None
			self.maxBytes=10
			self.bufferSize=0
		elif self.serialInputType=='ASCII':
			timeout=0.008
			self.maxBytes=1024
			self.bufferSize=0
			
		print 'portName', portName
		self.ser = serial.Serial(port = portName, baudrate=38400, bytesize=8, timeout=timeout)
		self.ser.close()
		self.ser.open()
		self.receiveList=[]
		self.packet=''
		self.ETNpacketList=[]
		self.sp=Serial_Packet()
		self.sp.ETNFlag=False
		self.sp.game=self.game
		self.sp.decodePacket='from serial ETN check'
		self.sp.MPserial=True

		self.ser.flushInput()

	def serialInput(self):
		if self.serialInputType=='MP':
			'''Handles serial input.'''

			#verbose(['---- self.previousLowByte', self.previousLowByte], self.verbose)
			try:
				
				data_out = bytearray(self.ser.read(1))
				
				#verbose(['data_out', data_out], self.verbose)
				for x, byte in enumerate(data_out):
					if byte>127:
						byteType='high'	
						if self.previousLowByte is not None:
							word=(self.previousLowByte<<8)+byte
							self.receiveList.append(word)
					else:
						byteType='low'
						self.previousLowByte=byte
					#verbose([byte], self.verbose)
				#verbose([byteType, byte], self.verbose)
				#verbose(['self.receiveList', self.receiveList], self.verbose)
				#self.ser.close()
				#self.bufferSize=self.ser.inWaiting()
				#if self.ser.inWaiting():
					#verbose([ self.ser.inWaiting(), 'bytes in buffer'], self.verbose)
				
				
			except:
				print 'ERROR serialInput function'#pass	
			#verbose(['---'], self.verbose)	
				
		elif self.serialInputType=='ASCII':
			#print 'ASCII'
			try:
				self.packet = self.ser.read(self.maxBytes)
				string=''
				self.sp.versionIDByte(string, packet=self.packet, lengthCheck=1)
				if self.sp.ETNFlag:
					self.sp.ETNFlag=False
					self.ETNpacketList.append(self.packet)
				if len(self.ETNpacketList)>0:
					pass#print '-----len(self.ETNpacketList', len(self.ETNpacketList)
			except:
				print 'ERROR serialInput function'
			#print self.packet


	def serialOutput(self, data):
		'''Handles serial output.'''
		data_in = data
		#print data
		try:
			self.ser.write(data_in)
		except:
			print 'ERROR serial output function'

	def flushInput(self):
		print 'self.bufferSize', self.bufferSize
		self.ser.flushInput()
		self.receiveList=[]

def test():
	'''Test function if module ran independently.
	Called in a thread every serialInputRefreshFrequency.
	'''
	tic=time.time()
	count=0
	byte=s.ser.inWaiting()
	if byte:
		count+=1
	ElapseTime=elapseTime(s.serialInput, On=False)
	toc=time.time()
	elaps=toc-tic
	#print 'Test', byte, elaps, (tic-1446587172)


if __name__ == '__main__':
	import thread, threading, time, timeit, os, sys
	from sys import platform as _platform
	from threading import Thread
	from MP_Data_Handler import MP_Data_Handler
	s = MP_Serial_Handler(verbose=False)
	mp=MP_Data_Handler()
	serialInputRefreshFrequency=.001
	refresherSerialInput=Thread(target=threadTimer, args=(test,serialInputRefreshFrequency))
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
		print  'group', group, 'bank', bank, 'word', word, 'addr', mp.GBW_to_MP_Address(group, bank, word)+1, 'I_Bit', I_Bit, 'data', bin(numericData), bin(words)
	'''
	try:
		s.ser.close()
	except:
		print 'ERROR close'
	'''
	print 'DONE'
