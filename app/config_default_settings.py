#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module reads, writes, or modifies the defaultConfig and userConfig files.

	:Created Date: 3/12/2015
	:Author: **Craig Gunter**

"""

import time
# import pkg_resources  # Not sure if i need this

import app.utils.functions
import app.utils.misc
import app.utils.configobj


class Config:
	"""Writes the chosen file or reads it and builds a dictionary of it named configDict."""

	def __init__(self, write=False, file_type='user'):
		self.fileType = file_type
		self.write = write
		self.tic = 0.0
		self.toc = 0.0
		self.configDict = {}
		self.configFile = {}
		self.userConfigDict = {}
		self._process_selection()

	def _process_selection(self):
		# Choose read or write and default or use
		if self.fileType == 'default':
			self.configDict = app.utils.configobj.ConfigObj('defaultConfig')
			if self.write:
				self._write_all()
			else:
				self.configFile = app.utils.configobj.ConfigObj('defaultConfig')  # All values and keys are in string format
				self._read_all()
		elif self.fileType == 'user':
			self.configDict = app.utils.configobj.ConfigObj('userConfig')
			if self.write:
				self._write_all()
			else:
				self.configFile = app.utils.configobj.ConfigObj('userConfig')  # All values and keys are in string format
				self._read_all()

	def write_option_jumpers(self, option_jumpers):
		"""Update optionJumpers in object and file."""
		if self.fileType == 'default':
			self.configDict = app.utils.configobj.ConfigObj('defaultConfig')
		elif self.fileType == 'user':
			self.configDict = app.utils.configobj.ConfigObj('userConfig')  # All values and keys are in string format
		self.configDict['optionJumpers'] = option_jumpers
		if (
				option_jumpers[0] == 'B'
				and (
						self.configDict['sport'] == 'MPMULTISPORT1-baseball'
						or self.configDict['sport'] == 'MPMULTISPORT1-football')):
			self.configDict['MPLX3450Flag'] = True
		else:
			self.configDict['MPLX3450Flag'] = False
		self.configDict.write()

	def write_sport(self, sport):
		"""Update sport in object and file."""
		if self.fileType == 'default':
			self.configDict = app.utils.configobj.ConfigObj('defaultConfig')
		elif self.fileType == 'user':
			self.configDict = app.utils.configobj.ConfigObj('userConfig')  # All values and keys are in string format
		self.configDict['sport'] = sport
		self.configDict.write()

	def write_server(self, server):
		"""Update SERVER in object and file."""
		if self.fileType == 'default':
			self.configDict = app.utils.configobj.ConfigObj('defaultConfig')
		elif self.fileType == 'user':
			self.configDict = app.utils.configobj.ConfigObj('userConfig')  # All values and keys are in string format
		self.configDict['SERVER'] = server
		self.configDict.write()

	def write_ui(self, model, board_color, caption_color, stripe_color, led_color):
		"""Update UI variables in object and file."""
		if self.fileType == 'default':
			self.configDict = app.utils.configobj.ConfigObj('defaultConfig')
		elif self.fileType == 'user':
			self.configDict = app.utils.configobj.ConfigObj('userConfig')  # All values and keys are in string format
		self.configDict['model'] = model
		self.configDict['boardColor'] = board_color
		self.configDict['captionColor'] = caption_color
		self.configDict['stripeColor'] = stripe_color
		self.configDict['LEDcolor'] = led_color
		self.configDict.write()

	def _write_all(self):
		# Write all configurations to object and file
		self.toc = time.time()

		self.configDict['Version'] = 999
		self.configDict['sport'] = 'MPLINESCORE5'  # needs user control and new instance definition for change

		self.configDict['optionJumpers'] = '0000'
		self.configDict['MPLX3450Flag'] = False
		self.configDict['BOUNCETIME'] = 100
		self.configDict['splashTime'] = 3

		# UI variables
		self.configDict['model'] = 'LX1750'
		self.configDict['boardColor'] = 'COMPANY_LOGO'
		self.configDict['captionColor'] = 'WHITE'
		self.configDict['stripeColor'] = 'WHITE'
		self.configDict['LEDcolor'] = 'RED'

		# adhoc_tranceiver self.config variables
		self.configDict['SERVER'] = True
		self.configDict['scoreNetHostAddress'] = '192.168.8.1'
		self.configDict['socketServerPort'] = 60032
		self.configDict['Baud'] = 115200

		# THIS SECTION BUILDS THE self.config OBJECT THAT IS WRITTEN TO THE FILE

		print "WROTE TO FILE"

		self.configDict.write()  # Create 'defaultConfig' file. Everything will be converted to strings
		self.tic = time.time()

	def _read_all(self):
		# Read all configurations from file and store in object
		self.toc = time.time()
		self.configDict = {}

		for key in self.configFile.keys():
			if self.configFile[key] == 'False' or self.configFile[key] == 'True':
				self.configDict[key] = app.utils.functions.tf(self.configFile[key])
			elif (
					key == 'scoreNetHostAddress' or key == 'sport' or key == 'model' or key == 'optionJumpers'
					or key == 'boardColor' or key == 'captionColor' or key == 'stripeColor'):
				self.configDict[key] = self.configFile[key]
			elif self.configFile[key].find('.') != -1:
				self.configDict[key] = float(self.configFile[key])
			elif unicode(self.configFile[key]).isdigit():
				self.configDict[key] = int(self.configFile[key])
			elif unicode(self.configFile[key]).isalnum() or self.configFile[key].isalpha():
				self.configDict[key] = self.configFile[key]
			else:
				print self.configFile[key], 'format not recognized'
				raise Exception
		self.tic = time.time()

	def get_dict(self):
		"""Return **configDict**."""
		return self.configDict

	def user_equals_default(self):
		"""Update userConfig file with defaultConfig file values."""
		self.userConfigDict = app.utils.configobj.ConfigObj('userConfig')
		self.fileType = 'default'
		self.write = False
		self._process_selection()
		self.userConfigDict.update(self.configDict)
		self.userConfigDict.write()


def create_config_files():
	"""
	Run this module with write_config_flag=True to create the defaultConfig file.
	Next press enter to copy it to the userConfig file.
	"""
	print "ON"
	write_config_flag = True
	if write_config_flag:
		app.utils.misc.silent_remove('defaultConfig')
	c = Config(write_config_flag, 'default')
	app.utils.misc.print_dict(c.__dict__)
	print "%f seconds to run config file setup." % (c.tic - c.toc)
	raw_input()

	app.utils.misc.silent_remove('userConfig')
	c.user_equals_default()
	app.utils.misc.print_dict(c.__dict__)
	print "%f seconds to run config file setup." % (c.tic - c.toc)


if __name__ == '__main__':
	create_config_files()
