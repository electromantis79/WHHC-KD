#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
**COMPLETION** = 99%  Sphinx Approved = **True**

.. topic:: Overview

    This clock module is used for all scoreboard timers.

    :Created Date: 3/11/2015
    :Modified Date: 8/31/2016
    :Author: **Craig Gunter**

'''

import time, threading

class clock(object):
	"""
	Implements a clock.
	"""
	def __init__(self, countUp=False, maxSeconds=86399.999, resolution=0.001, hoursFlag=False, clockName='generic', internalClock=False):

		self.autoStop = False
		self.autoStop2 = False
		self.running = False
		self.resolution = resolution
		self.days = 0
		self.hours = 0
		self.minutes = 0
		self.seconds = 0
		self.tenths_hundredths = 0
		self.next_call = time.time()

		self._start = 0.0
		self._stop = 0.0
		self.changeTime = 0.0

		self.hundredthsUnits = 0
		self.tenthsUnits = 0
		self.secondsUnits = 0
		self.secondsTens = 0
		self.minutesUnits = 0
		self.minutesTens = 0
		self.hoursUnits = 0
		self.hoursTens = 0
		self.daysUnits = 0
		self.daysTens = 0
		self.PM=False

		self.countUp = countUp
		self.maxSeconds = maxSeconds # must be in seconds
		self.hoursFlag = hoursFlag
		self.clockName=clockName
		self.internalClock=internalClock

		if self.countUp:
			self.currentTime = 0.0
		else:
			self.currentTime = self.maxSeconds
		if self.clockName=='timeOfDayClock':
			self.currentTime = self.maxSeconds
			self._start = time.time()
			self.running = True


		self.Update()

	def Update(self):
		"""
		Updates the current time.
		"""
		next_call = time.time()
		while True:
			#print datetime.datetime.now()

			if self.clockName=='timeOfDayClock':
				if self.internalClock:
					self.hours = time.localtime().tm_hour
					if self.hours>12:
						self.hours-=12
					self.minutes = time.localtime().tm_min
				else:
					elapseTime = time.time() - self._start

					if self.currentTime>86399.999:
						self.Reset(0)
						return
					else:
						self.currentTime = self.maxSeconds + elapseTime

				hours = int(self.currentTime)/(60*60)
				minutes = int((self.currentTime)/60)-hours*60
				seconds = int(self.currentTime-minutes*60-hours*60*60)

				if hours>12:
					self.PM=True
					hours-=12
				else:
					self.PM=False
					if hours==0:
						hours=12

				self.hours = hours
				self.hoursUnits = self.hours % 10
				self.hoursTens = self.hours / 10

				self.minutes = minutes
				self.minutesUnits = self.minutes % 10
				self.minutesTens = self.minutes / 10

				self.seconds = seconds
				self.secondsUnits = self.seconds % 10
				self.secondsTens = self.seconds / 10

				self.daysUnits = 0
				self.daysTens = 0

				self.blinky=False

				self.timeList = [\
				self.daysTens, self.daysUnits, self.hoursTens, self.hoursUnits, \
				self.minutesTens, self.minutesUnits, self.secondsTens, self.secondsUnits, \
				self.tenthsUnits, self.hundredthsUnits]

				self.next_call = self.next_call+self.resolution
				if self.running:
					self.refresh = threading.Timer( self.next_call - time.time(), self.Update).start()
				return self.timeList

			if self.running:
				elapseTime = time.time() - self._start - self.changeTime
				if self.countUp:
					self.currentTime =  elapseTime
				else:
					if self.clockName=='shotClock':
						self.currentTime =  self.maxSeconds - elapseTime
						if self.currentTime<0:
							self.currentTime=0
							if not self.autoStop2:
								self._stop = time.time() - self._start
								self.running=False
								self.autoStop=True
								self.autoStop2=True
								print 'self.autoStop shotClock', self.autoStop2
					else:
						self.currentTime =  self.maxSeconds - elapseTime

				# Check for auto stop
				if not self.countUp and self.currentTime <0 and not self.clockName=='shotClock':
					self._stop = time.time() - self._start
					self.currentTime = 0.0
					self.running=False
					self.autoStop=True
					print 'self.autoStop down', self.autoStop
				elif self.countUp and self.currentTime >= self.maxSeconds:
					self._stop = time.time() - self._start
					self.currentTime = self.maxSeconds
					self.running=False
					self.autoStop=True
					print 'self.autoStop up', self.autoStop
			else:
				if self.currentTime<0:
					self.currentTime=0


			if self.hoursFlag:
				self.days = int((self.currentTime)/(60*60*24))
				self.hours = int((self.currentTime)/(60*60))-self.days*24

				self.hoursUnits = self.hours % 10
				self.hoursTens = self.hours / 10
				self.daysUnits = self.days % 10
				self.daysTens = self.days / 10

				self.minutes = int((self.currentTime)/60)-self.hours*60-self.days*60*24
				self.seconds = int(self.currentTime - self.minutes*60-self.hours*60*60-self.days*60*60*24)
				self.tenths_hundredths = int((self.currentTime - self.seconds-self.minutes*60-self.hours*60*60-self.days*60*60*24)*100)
			else:
				self.hoursUnits = 0
				self.hoursTens = 0
				self.daysUnits = 0
				self.daysTens = 0
				self.minutes = int((self.currentTime)/60)
				self.seconds = int(self.currentTime - self.minutes*60)
				self.tenths_hundredths = int((self.currentTime - self.seconds-self.minutes*60)*100)

			self.hundredthsUnits = self.tenths_hundredths % 10
			self.tenthsUnits = self.tenths_hundredths / 10
			self.secondsUnits = self.seconds % 10
			self.secondsTens = self.seconds / 10
			self.minutesUnits = self.minutes % 10
			self.minutesTens = self.minutes / 10

			if (self.tenthsUnits%10)>4:
				self.blinky=True
			else:
				self.blinky=False

			self.timeList = [\
			self.daysTens, self.daysUnits, self.hoursTens, self.hoursUnits, \
			self.minutesTens, self.minutesUnits, self.secondsTens, self.secondsUnits, \
			self.tenthsUnits, self.hundredthsUnits]
			#print self.timeList
			self.next_call = self.next_call+self.resolution

			if self.running:
				self.refresh = threading.Timer( self.next_call - time.time(), self.Update).start()
			wait=next_call - time.time()
			print self.timeList, wait
			time.sleep(abs(wait))		
		return self.timeList

	def gameDataUpdate(self, gameData, name='periodClock'):
		'''
		Used to store UnMapped data in the game object. (Scoreboard data received from another console)
		'''
		timeListNames=['daysTens', 'daysUnits', 'hoursTens', \
		'hoursUnits', 'minutesTens', 'minutesUnits', 'secondsTens', \
		'secondsUnits', 'tenthsUnits', 'hundredthsUnits']
		for x, each in enumerate(timeListNames):
			gameData[name+'_'+each]=self.timeList[x]
		return gameData

	def changeSeconds(self, change):
		'''
		Changes the time while retaining the maximum time.
		'''
		self.changeTime += change
		self.currentTime += change
		self.Update()
		return

	def Start(self):
		"""
		Starts the clock if stopped.
		"""
		if not self.running:
			self._start = time.time() - self._stop
			self.running = True
			self.autoStop=False
			self.Update()
		return

	def Stop(self):
		"""
		Stops the clock if running.
		"""
		if self.running:
			self._stop = time.time() - self._start
			self.running = False
			self.Update()
		return

	def Reset(self, resetValueSeconds=None):
		"""
		Resets the clock to passed value.
		"""
		if self.clockName=='timeOfDayClock' and not self.internalClock:
			#print 'self.maxSeconds', self.maxSeconds, 'self.currentTime', self.currentTime
			if resetValueSeconds is not None:
				self.currentTime = self.maxSeconds
				self.maxSeconds = resetValueSeconds
			if self.currentTime>46799.999:
				self.PM=True
			else:
				self.PM=False
			self._start = time.time()
			self.next_call = time.time()
			#print 'self.next_call', self.next_call, 'self.currentTime', self.currentTime
		else:
			if resetValueSeconds is not None:
				self.maxSeconds = resetValueSeconds
			self.next_call = time.time()
			self.running = False
			self.autoStop=False
			self.autoStop2 = False
			self._start = 0.0
			self._stop = 0.0
			self.changeTime = 0.0

			if self.countUp:
				self.currentTime = 0.0
			else:
				self.currentTime = self.maxSeconds
		self.Update()
		return


def test():
	'''Test function if module ran independently.'''
	print 'OK'
	#print time.localtime().tm_min
	from Game import printDict

	direction=0#input("Input clock direction ('0' = down): ")
	length=10#input("Input Max time until stop in seconds: ")
	hours=0#input("Input '1' for Hours mode or '0' for Minutes Mode: ")

	periodClock=clock(direction,length,hours)
	#clocky = periodClock.Update()
	#periodClock.Start()
	#while periodClock.running:
	#	print periodClock.Update()
	#printDict(periodClock.__dict__)


if __name__ == '__main__':
	test()
