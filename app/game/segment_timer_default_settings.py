#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

    This module reads, writes, or modifies the segmentTimerDefaultSettings and segmentTimerUserSettings files.

    :Created Date: 3/12/2015
    :Author: **Craig Gunter**

"""

import time, os
# import pkg_resources  # Not sure if i need this

import app.functions
import app.configobj


class SegmentTimerSettings:
	"""Writes the chosen file or reads it and builds a dictionary of it named segmentTimerDefaultSettings."""

	def __init__(self, write=False, file_type='user'):
		self.fileType = file_type
		self.write = write
		self.tic = 0.0
		self.toc = 0.0
		self.segmentTimerSettings = {}
		self.segmentTimerSettingsFile = {}
		self.segmentTimerUserSettings = {}
		self._process_selection()

	def _process_selection(self):
		"""Choose read or write and default or user"""
		if self.fileType == 'default':
			if self.write:
				self.segmentTimerSettings = app.configobj.ConfigObj('game/segmentTimerDefaultSettings')
				self._write_all()
			else:
				self.segmentTimerSettingsFile = app.configobj.ConfigObj('game/segmentTimerDefaultSettings', file_error=True)
				self._read_all()
		elif self.fileType == 'user':
			if self.write:
				self.segmentTimerSettings = app.configobj.ConfigObj('game/segmentTimerUserSettings')
				self._write_all()
			else:
				self.segmentTimerSettingsFile = app.configobj.ConfigObj('game/segmentTimerUserSettings', file_error=True)
				self._read_all()

	def _write_all(self):
		"""Write all configurations to object and file."""
		self.toc = time.time()

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
		self.tic = time.time()

	def _read_all(self):
		# Read all configurations from file and store in object
		self.toc = time.time()
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
				print self.segmentTimerSettingsFile[key], 'format not recognized'
				raise Exception
		self.tic = time.time()

	def get_dict(self):
		"""Return **segmentTimerSettings** dictionary."""
		return self.segmentTimerSettings

	def user_equals_default(self):
		"""Update segmentTimerUserSettings file with segmentTimerDefaultSettings file values."""
		self.segmentTimerUserSettings = app.configobj.ConfigObj('game/segmentTimerUserSettings')
		self.fileType = 'default'
		self.write = False
		self._process_selection()
		self.segmentTimerUserSettings.clear()
		self.segmentTimerUserSettings.update(self.segmentTimerSettings)
		self.segmentTimerUserSettings.write()


def create_settings_files():
	"""
	Run this module with writeConfigFlag=True to create the segmentTimerDefaultSettings file.
	Next press enter to copy it to the segmentTimerUserSettings file.
	"""
	print "ON"
	write_segment_timer_settings_flag = True
	if write_segment_timer_settings_flag:
		app.functions.silentremove('game/segmentTimerDefaultSettings')
	g = SegmentTimerSettings(write_segment_timer_settings_flag, 'default')
	app.functions.printDict(g.__dict__)
	print "%f seconds to run 'segmentTimerSettings' file setup." % (g.tic - g.toc)
	raw_input()
	app.functions.silentremove('game/segmentTimerUserSettings')
	g.user_equals_default()
	app.functions.printDict(g.__dict__)

	print "%f seconds to run 'segmentTimerSettings' file setup." % (g.tic - g.toc)


if __name__ == '__main__':
	os.chdir('..') 
	"""Added this for csvOneRowRead to work with this structure, 
	add this line for each level below project root"""
	create_settings_files()
