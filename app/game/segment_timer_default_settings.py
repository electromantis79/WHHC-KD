#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

    This module reads, writes, or modifies the segmentTimerDefaultSettings and segmentTimerUserSettings files.

    :Created Date: 3/12/2015
    :Author: **Craig Gunter**

"""

import time, os
#import pkg_resources  # Not sure if i need this

import app.functions
import app.configobj


class SegmentTimerSettings:
	"""Writes the chosen file or reads it and builds a dictionary of it named segmentTimerDefaultSettings."""

	def __init__(self, write=False, fileType='user'):
		self.fileType = fileType
		self.write = write
		self.tick = 0.0
		self.tock = 0.0
		self.segmentTimerSettings = {}
		self.segmentTimerSettingsFile = {}
		self.segmentTimerUserSettings = {}
		self.Start()

	def Start(self):
		"""Choose read or write and default or user"""
		if self.fileType == 'default':
			if self.write:
				self.segmentTimerSettings = app.configobj.ConfigObj('game/segmentTimerDefaultSettings')
				self.writeAll()
			else:
				self.segmentTimerSettingsFile = app.configobj.ConfigObj('game/segmentTimerDefaultSettings', file_error=True)
				self.readAll()
		elif self.fileType == 'user':
			if self.write:
				self.segmentTimerSettings = app.configobj.ConfigObj('game/segmentTimerUserSettings')
				self.writeAll()
			else:
				self.segmentTimerSettingsFile = app.configobj.ConfigObj('game/segmentTimerUserSettings', file_error=True)
				self.readAll()

	def writeAll(self):
		"""Write all configurations to object and file."""
		self.tock = time.time()

		# settings
		self.segmentTimerSettings['programID'] = 1
		self.segmentTimerSettings['overwriteFlag'] = False
		self.segmentTimerSettings['numberOfDigits'] = 4
		self.segmentTimerSettings['playClockEnable'] = False
		self.segmentTimerSettings['totalSegments'] = 1
		self.segmentTimerSettings['segmentTimerCountUp'] = False
		self.segmentTimerSettings['segmentTimerTenthsFlag'] = True
		self.segmentTimerSettings['intervalDisplayFlag'] = False
		self.segmentTimerSettings['endOfSegmentHorn'] = True
		self.segmentTimerSettings['segmentCountUp'] = True
		self.segmentTimerSettings['continuousPlayFlag'] = False
		self.segmentTimerSettings['continuousLoopFlag'] = False

		self.segmentTimerSettings['segmentTimerMaxSeconds'] = 0
		self.segmentTimerSettings['flashTimerMaxSeconds'] = 0
		self.segmentTimerSettings['intervalTimerMaxSeconds'] = 5

		self.segmentTimerSettings['segmentNumber'] = 1
		self.segmentTimerSettings['restoreProgramFlag'] = 1

		# THIS SECTION BUILDS THE self.config OBJECT THAT IS WRITTEN TO THE FILE
		print "WROTE TO FILE"

		self.segmentTimerSettings.write()  # Create 'config' file. Everything will be converted to strings
		self.tick = time.time()

	def readAll(self):
		"""Read all configurations from file and store in object."""
		self.tock = time.time()
		for key in self.segmentTimerSettingsFile.keys():
			if self.segmentTimerSettingsFile[key] == 'False' or self.segmentTimerSettingsFile[key] == 'True':
				self.segmentTimerSettings[key] = app.functions.tf(self.segmentTimerSettingsFile[key])
			elif self.segmentTimerSettingsFile[key].find('.') != -1:
				self.segmentTimerSettings[key] = float(self.segmentTimerSettingsFile[key])
			elif unicode(self.segmentTimerSettingsFile[key]).isdigit():
				self.segmentTimerSettings[key] = int(self.segmentTimerSettingsFile[key])
			elif unicode(self.segmentTimerSettingsFile[key]).isalnum() or self.segmentTimerSettingsFile[key].isalpha():
				self.segmentTimerSettings[key] = self.segmentTimerSettingsFile[key]
			elif self.segmentTimerSettingsFile[key] == '':
				self.segmentTimerSettings[key] = self.segmentTimerSettingsFile[key]
			else:
				print self.segmentTimerSettingsFile[key]
				raise error('format not recognized')
		self.tick = time.time()

	def getDict(self):
		"""Return **segmentTimerSettings** dictionary."""
		return self.segmentTimerSettings

	def userEqualsDefault(self):
		"""Update segmentTimerUserSettings file with segmentTimerDefaultSettings file values."""
		self.segmentTimerUserSettings = app.configobj.ConfigObj('game/segmentTimerUserSettings')
		self.fileType = 'default'
		self.write = False
		self.Start()
		self.segmentTimerUserSettings.clear()
		self.segmentTimerUserSettings.update(self.segmentTimerSettings)
		self.segmentTimerUserSettings.write()


def createSettingsFiles():
	"""
	Run this module with writeConfigFlag=True to create the segmentTimerDefaultSettings file.
	Next press enter to copy it to the segmentTimerUserSettings file.
	"""
	print "ON"
	writeSegmentTimerSettingsFlag = True
	#writeSegmentTimerSettingsFlag = False
	if writeSegmentTimerSettingsFlag:
		app.functions.silentremove('game/segmentTimerDefaultSettings')
	g = SegmentTimerSettings(writeSegmentTimerSettingsFlag, 'default')
	app.functions.printDict(g.__dict__)
	print "%f seconds to run 'segmentTimerSettings' file setup." % (g.tick-g.tock)
	raw_input()
	app.functions.silentremove('game/segmentTimerUserSettings')
	g.userEqualsDefault()
	app.functions.printDict(g.__dict__)

	print "%f seconds to run 'segmentTimerSettings' file setup." % (g.tick-g.tock)


if __name__ == '__main__':
	os.chdir('..') 
	"""Added this for csvOneRowRead to work with this structure, 
	add this line for each level below project root"""
	createSettingsFiles()
