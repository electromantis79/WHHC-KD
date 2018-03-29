#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. topic:: Overview

    This clock module is used for all scoreboard timers.

    :Created Date: 3/11/2015
    :Author: **Craig Gunter**
"""

import threading

from sys import platform as _platform

from app.functions import *


class clock(object):
	"""
	Implements a clock.
	"""
	def __init__(
			self, countUp=False, maxSeconds=86399.999, resolution=0.01,
			hoursFlag=False, clockName='generic', internalClock=False):
		self.countUp = countUp
		self.maxSeconds = maxSeconds  # must be in seconds
		self.resolution = resolution
		self.hoursFlag = hoursFlag
		self.clockName = clockName
		self.internalClock = internalClock
		if (_platform == "linux" or _platform == "linux2") and (clockName == 'periodClock' or clockName == 'shotClock'):
			os.nice(-1)

		# Flags
		self.autoStop = False
		self.autoStop2 = False
		self.running = False
		self.PM = False

		# Variables
		self.days = 0
		self.hours = 0
		self.minutes = 0
		self.seconds = 0
		self.tenths_hundredths = 0
		self.initStart = time.time()

		self._start = 0.0
		self._stop = 0.0
		self.changeTime = 0.0

		self.timeListNames = [
			'daysTens', 'daysUnits', 'hoursTens', 'hoursUnits', 'minutesTens', 'minutesUnits', 'secondsTens',
			'secondsUnits', 'tenthsUnits', 'hundredthsUnits']
		self.timeUnitsDict = dict.fromkeys(self.timeListNames, 0)

		# Prepare current time
		if self.countUp:
			self.currentTime = 0.0
		else:
			self.currentTime = self.maxSeconds
		self.timeUnitsDict['currentTime'] = self.currentTime

		if self.clockName == 'timeOfDayClock':
			self.currentTime = self.maxSeconds

		self.Update()

		self.refresher = clockThread(self.Update, self.resolution, name=self.clockName)
		self.refresher.start()

	def Update(self):
		"""
		Updates the current time.
		"""
		#print 'Update', time.time()-self.initStart

		if self.clockName == 'timeOfDayClock':

			# Select local time or user value for time
			if self.internalClock:
				hours = time.localtime().tm_hour
				if hours > 12:
					hours -= 12
				minutes = time.localtime().tm_min
				seconds = time.localtime().tm_sec

			else:
				# User input
				elapse_time = time.time() - self._start

				# If user time is outside of clock time cancel
				if self.currentTime > 86399.999:
					self.Reset(0)
					return

				self.currentTime = self.maxSeconds + elapse_time

				hours = int(self.currentTime)/(60*60)
				minutes = int(self.currentTime/60)-hours*60
				seconds = int(self.currentTime-minutes*60-hours*60*60)

				# Adjust military or standard
				if hours > 12:
					self.PM = True
					hours -= 12
				else:
					self.PM = False
					if hours == 0:
						hours = 12

			self.timeUnitsDict['currentTime'] = self.currentTime

			self.hours = hours
			self.timeUnitsDict['hoursUnits'] = self.hours % 10
			self.timeUnitsDict['hoursTens'] = self.hours / 10
			self.timeUnitsDict['PM'] = self.PM

			self.minutes = minutes
			self.timeUnitsDict['minutesUnits'] = self.minutes % 10
			self.timeUnitsDict['minutesTens'] = self.minutes / 10

			self.seconds = seconds
			self.timeUnitsDict['secondsUnits'] = self.seconds % 10
			self.timeUnitsDict['secondsTens'] = self.seconds / 10

			self.timeUnitsDict['daysUnits'] = 0
			self.timeUnitsDict['daysTens'] = 0

			self.timeUnitsDict['blinky'] = True

			self.timeUnitsDict['hours'] = self.hours
			self.timeUnitsDict['minutes'] = self.minutes
			self.timeUnitsDict['seconds'] = self.seconds

			return self.timeUnitsDict

		if self.running:
			elapse_time = time.time() - self._start - self.changeTime

			if self.countUp:
				self.currentTime = elapse_time
				if self.currentTime >= self.maxSeconds:
					self._stop = time.time() - self._start
					self.currentTime = self.maxSeconds
					self.running = False
					self.autoStop = True
					self.refresher.pause()
					print 'self.autoStop up', self.autoStop
			else:
				# Down counting clocks
				self.currentTime = self.maxSeconds - elapse_time

				# Check for auto stop
				if self.clockName == 'shotClock':
					if self.currentTime < 0:
						self.currentTime = 0
						if not self.autoStop2:
							self._stop = time.time() - self._start
							self.running = False
							self.autoStop = True
							self.autoStop2 = True
							self.refresher.pause()
							print 'self.autoStop shotClock', self.autoStop2

				elif self.currentTime < 0:
					self._stop = time.time() - self._start
					self.currentTime = 0.0
					self.running = False
					self.autoStop = True
					self.refresher.pause()
					print 'self.autoStop down', self.autoStop
				else:
					# Generic clock not stopping
					pass
		else:
			# No negative times allowed
			if self.currentTime < 0:
				self.currentTime = 0

		# Float time calculations
		self.timeUnitsDict['currentTime'] = self.currentTime
		if self.hoursFlag:
			self.days = int(self.currentTime/(60*60*24))
			self.hours = int(self.currentTime/(60*60))-self.days*24

			self.timeUnitsDict['hoursUnits'] = self.hours % 10
			self.timeUnitsDict['hoursTens'] = self.hours / 10
			self.timeUnitsDict['daysUnits'] = self.days % 10
			self.timeUnitsDict['daysTens'] = self.days / 10

			self.minutes = int(self.currentTime/60)-self.hours*60-self.days*60*24
			self.seconds = int(self.currentTime - self.minutes*60-self.hours*60*60-self.days*60*60*24)
			self.tenths_hundredths = int(
				(self.currentTime - self.seconds-self.minutes*60-self.hours*60*60-self.days*60*60*24)*100)

		else:
			self.timeUnitsDict['hoursUnits'] = 0
			self.timeUnitsDict['hoursTens'] = 0
			self.timeUnitsDict['daysUnits'] = 0
			self.timeUnitsDict['daysTens'] = 0

			self.minutes = int(self.currentTime/60)
			self.seconds = int(self.currentTime - self.minutes*60)
			self.tenths_hundredths = int((self.currentTime - self.seconds-self.minutes*60)*100)

		self.timeUnitsDict['minutes'] = self.minutes
		self.timeUnitsDict['seconds'] = self.seconds
		self.timeUnitsDict['tenths_hundredths'] = self.tenths_hundredths

		self.timeUnitsDict['hundredthsUnits'] = self.tenths_hundredths % 10
		self.timeUnitsDict['tenthsUnits'] = self.tenths_hundredths / 10
		self.timeUnitsDict['secondsUnits'] = self.seconds % 10
		self.timeUnitsDict['secondsTens'] = self.seconds / 10
		self.timeUnitsDict['minutesUnits'] = self.minutes % 10
		self.timeUnitsDict['minutesTens'] = self.minutes / 10

		if (self.timeUnitsDict['tenthsUnits'] % 10) > 4:
			self.timeUnitsDict['blinky'] = True
		else:
			self.timeUnitsDict['blinky'] = False
		return self.timeUnitsDict

	def gameDataUpdate(self, gameData, name='periodClock'):
		"""
		Used to store UnMapped data in the game object. (Scoreboard data received from another console)
		"""
		for each in self.timeListNames:
			gameData[name+'_'+each] = self.timeUnitsDict[each]
		return gameData

	def changeSeconds(self, change):
		"""
		Changes the time while retaining the maximum time.
		"""
		self.changeTime += change
		self.currentTime += change
		self.Update()

	def Start(self):
		"""
		Starts the clock if stopped.
		"""
		if not self.running:
			self._start = time.time() - self._stop
			self.running = True
			self.autoStop = False
			self.autoStop2 = False
			self.refresher.resume()

	def Stop(self):
		"""
		Stops the clock if running.
		"""
		if self.running:
			self._stop = time.time() - self._start
			self.running = False
			self.refresher.pause()

	def Reset(self, resetValueSeconds=None):
		"""
		Resets the clock to passed value.
		"""
		if self.clockName == 'timeOfDayClock' and not self.internalClock:
			if resetValueSeconds is not None:
				self.currentTime = self.maxSeconds
				self.maxSeconds = resetValueSeconds
			if self.currentTime > 46799.999:
				self.PM = True
			else:
				self.PM = False
			self._start = time.time()
		else:
			if resetValueSeconds is not None:
				self.maxSeconds = resetValueSeconds
			self.running = False
			self.autoStop = False
			self.autoStop2 = False
			self._start = 0.0
			self._stop = 0.0
			self.changeTime = 0.0

			if self.countUp:
				self.currentTime = 0.0
			else:
				self.currentTime = self.maxSeconds
		self.Update()

	def Kill(self):
		"""Kills update thread"""
		if (_platform == "linux" or _platform == "linux2") and (
				self.clockName == 'periodClock' or self.clockName == 'shotClock'):
			os.nice(1)
		self.refresher.resume()
		self.refresher.kill()


class clockThread(threading.Thread):
	"""Pausable thread for clock"""
	def __init__(self, function, period, name='Generic'):
		threading.Thread.__init__(self)
		self.function = function
		self.period = period
		self.clockName = name
		if _platform == "linux" or _platform == "linux2":
			try:
				prctl.set_name(name)  # Used on BBB to show name of process in htop
			except:
				pass
		#self.daemon=True TODO: check this
		self.nextCall = 0.0
		self.paused = True
		self._stopevent = threading.Event()
		self.state = threading.Condition()

	def run(self):
		self.nextCall = time.time()

		stamp = 0
		name = self.clockName, threading.current_thread().getName()
		while not self._stopevent.isSet():
			with self.state:
				if self.paused:
					self.state.wait()

			stamp += 1

			self.nextCall = self.nextCall+self.period
			self.function()

			count = 0
			try:
				now = time.time()
				time.sleep(self.nextCall-now)
			except Exception as err:

				while (self.nextCall-now) < 0:
					self.nextCall = self.nextCall+self.period
					count += 1

				self.nextCall = self.nextCall+self.period*count

				try:
					now = time.time()
					time.sleep(self.nextCall-now)
				except:
					print name, 'double except', stamp, 'count', count, self.nextCall-1486587172, self.nextCall-now
					self.nextCall = self.nextCall+self.period*count
					time.sleep(self.nextCall-now)
		print 'Thread', name, 'killed'

	def resume(self):
		with self.state:
			self.paused = False
			self.state.notify()
			self.nextCall = time.time()

	def pause(self):
		with self.state:
			self.paused = True

	def kill(self):
		self._stopevent.set()

# TODO: clean this function and create real test functions


"""

tic = time.time()
print 'OK'
toc = time.time()
elapse = toc-tic
#print toc, tic, elapse, type(elapse)
#direction=input("Input clock direction ('0' = down): ")
#length=input("Input Max time until stop in seconds: ")
#hours=input("Input '1' for Hours mode or '0' for Minutes Mode: ")

#periodClock=clock(countUp=direction, maxSeconds=length, resolution=0.01, hoursFlag=hours, clockName='generic', internalClock=False)
periodClock=clock(maxSeconds=10, countUp=False, clockName='shotClock', resolution=0.01)
#clockThread(thread_timer(periodClock.Update, 0.01), 0.01)

#clocky = periodClock.Update()
periodClock.Start()
while periodClock.running:
	#periodClock.updateValues()
	print (
		periodClock.timeUnitsDict['minutesTens'], periodClock.timeUnitsDict['minutesUnits'],
		periodClock.timeUnitsDict['secondsTens'], periodClock.timeUnitsDict['secondsUnits'],
		periodClock.timeUnitsDict['tenthsUnits'], periodClock.timeUnitsDict['hundredthsUnits'])
	time.sleep(0.01)
	if periodClock.timeUnitsDict['secondsUnits']<=5:
		periodClock.Kill()
		break
periodClock.Stop()
time.sleep(.2)

while 1:
	pass
app.utils.misc.print_dict(periodClock.__dict__)

import cProfile, pstats, StringIO
tic = time.time()
pr = cProfile.Profile()
pr.enable()
# ... do something ...
elapse_time(periodClock.Update, On=True)
pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print 'stat', s.getvalue()
toc = time.time()
elapse = toc-tic
print 'elapse', elapse*1000, 'ms'
"""