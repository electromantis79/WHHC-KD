#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 99%  Sphinx Approved = **True**

.. topic:: Overview

    This module reads, writes, or modifies the defaultConfig and userConfig files.

    :Created Date: 3/12/2015
    :Modified Date: 8/31/2016
    :Author: **Craig Gunter**

"""

import time, csv
#import pkg_resources

from functions import *
from configobj import ConfigObj

class Config:
	'''Writes the chosen file or reads it and builds a dictionary of it named configDict.'''
	def __init__(self, write=False, fileType='user'):
		self.fileType=fileType
		self.write=write
		self.Start()

	def Start(self):
		'''Choose read or write and default or user'''
		if self.fileType=='default':
			self.configDict = ConfigObj('defaultConfig')
			if self.write:
				self.writeAll()
			else:
				self.configFile = ConfigObj('defaultConfig')# All values and keys are in string format
				self.readAll()
		elif self.fileType=='user':
			self.configDict = ConfigObj('userConfig')
			if self.write:
				self.writeAll()
			else:
				self.configFile = ConfigObj('userConfig')# All values and keys are in string format
				self.readAll()

	def writeOptionJumpers(self, optionJumpers):
		'''Update optionJumpers in object and file.'''
		if self.fileType=='default':
			self.configDict = ConfigObj('defaultConfig')
		elif self.fileType=='user':
			self.configDict = ConfigObj('userConfig')# All values and keys are in string format
		self.configDict['optionJumpers']=optionJumpers
		if optionJumpers[0]=='B' and (self.configDict['sport']=='MPMULTISPORT1-baseball' or self.configDict['sport']=='MPMULTISPORT1-football'):
			self.configDict['MPLX3450Flag']=True
		else:
			self.configDict['MPLX3450Flag']=False
		self.configDict.write()

	def writeSport(self, sport):
		'''Update sport in object and file.'''
		if self.fileType=='default':
			self.configDict = ConfigObj('defaultConfig')
		elif self.fileType=='user':
			self.configDict = ConfigObj('userConfig')# All values and keys are in string format
		self.configDict['sport']=sport
		self.keypadType = sport[0:2]
		self.configDict['keypadType']=self.keypadType
		self.configDict.write()

	def writeSERVER(self, server):
		'''Update SERVER in object and file.'''
		if self.fileType=='default':
			self.configDict = ConfigObj('defaultConfig')
		elif self.fileType=='user':
			self.configDict = ConfigObj('userConfig')# All values and keys are in string format
		self.configDict['SERVER']=server
		self.configDict.write()

	def writeUI(self, model, boardColor, captionColor, stripeColor, LEDcolor):
		'''Update UI variables in object and file.'''
		if self.fileType=='default':
			self.configDict = ConfigObj('defaultConfig')
		elif self.fileType=='user':
			self.configDict = ConfigObj('userConfig')# All values and keys are in string format
		self.configDict['model']=model
		self.configDict['boardColor']=boardColor
		self.configDict['captionColor']=captionColor
		self.configDict['stripeColor']=stripeColor
		self.configDict['LEDcolor'] = LEDcolor
		self.configDict.write()

	def writeAll(self):
		'''Write all configurations to object and file.'''
		self.tock=time.time()

		self.configDict['Version'] = 999
		self.configDict['sport'] = 'MPLINESCORE5' # needs user control and new instance definition for change
		self.configDict['model'] = 'LX1750'
		self.configDict['boardColor'] = 'COMPANY_LOGO'
		self.configDict['captionColor'] = 'WHITE'
		self.configDict['stripeColor'] = 'WHITE'
		self.configDict['LEDcolor'] = 'RED'
		self.configDict['keypadType'] = self.configDict['sport'][0:2]
		self.configDict['optionJumpers'] = '0000'
		self.configDict['MPLX3450Flag'] = False
		self.configDict['BOUNCETIME'] = 100
		self.configDict['splashTime'] = 3

		# adhoc_tranceiver self.config variables
		self.configDict['SERVER'] = True
		self.configDict['HOST'] = '192.168.1.1'
		self.configDict['port'] = 60032
		self.configDict['Baud'] = 115200


		#THIS SECTION BUILDS THE self.config OBJECT THAT IS WRITTEN TO THE FILE

		print "WROTE TO FILE"

		self.configDict.write() #Create 'defaultConfig' file. Everything will be converted to strings
		self.tick=time.time()

	def readAll(self):
		'''Read all configurations from file and store in object.'''
		self.tock=time.time()
		self.configDict = {}

		for key in self.configFile.keys():
			if self.configFile[key]=='False' or self.configFile[key]=='True':
				self.configDict[key]=tf(self.configFile[key])
			elif key=='HOST' or key=='sport' or key=='model' or key=='optionJumpers' \
			or key=='boardColor' or key=='captionColor' or key=='stripeColor' :
				self.configDict[key]=self.configFile[key]
			elif self.configFile[key].find('.')!=-1:
				self.configDict[key]=float(self.configFile[key])
			elif unicode(self.configFile[key]).isdigit():
				self.configDict[key]=int(self.configFile[key])
			elif unicode(self.configFile[key]).isalnum() or self.configFile[key].isalpha():
				self.configDict[key]=self.configFile[key]
			else:
				print self.configFile[key]
				raise error('format not recognized')
		self.tick=time.time()

	def getDict(self):
		'''Return **configDict**.'''
		return self.configDict

	def user2default(self):
		'''Update userConfig file with defaultConfig file values.'''
		self.userConfigDict = ConfigObj('userConfig')
		self.fileType='default'
		self.write=False
		self.Start()
		self.userConfigDict.update(self.configDict)
		self.userConfigDict.write()

def createConfigFiles():
	'''
	Run this module with writeConfigFlag=True to create the defaultConfig file.
	Next press enter to copy it to the userConfig file.
	'''
	print "ON"
	from Game import printDict
	writeConfigFlag=True
	#writeConfigFlag=False
	if writeConfigFlag:
		silentremove('defaultConfig')
	c=Config(writeConfigFlag,'default')
	#print c.__dict__
	printDict(c.__dict__)
	print "%f seconds to run config file setup." % (c.tick-c.tock)
	raw_input()
	silentremove('userConfig')
	c.user2default()
	#c.writeSport('djdjdjdjd')
	#print c.__dict__
	printDict(c.__dict__)
	print "%f seconds to run config file setup." % (c.tick-c.tock)


if __name__ == '__main__':
	createConfigFiles()
