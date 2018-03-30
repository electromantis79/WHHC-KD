#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. topic:: Overview

	This module holds all functions for reading files to build python objects.

	:Created Date: 3/29/2018
	:Author: **Craig Gunter**
"""

import csv


def read_config():
	"""
	Returns a dictionary of the userConfig file.
	"""
	import config_default_settings
	c = config_default_settings.Config(write=False, file_type='user')
	return c.get_dict()


def read_game_default_settings():
	"""
	Returns a dictionary of the gameUserSettings file.
	"""
	import app.game.game_default_settings
	g = app.game.game_default_settings.GameDefaultSettings(
		write=False, file_type='user')  # All values and keys are in string format
	return g.get_dict()


def read_segment_timer_settings():
	"""
	Returns a dictionary of the segmentTimerUserSettings file.
	"""
	import app.game.segment_timer_default_settings
	g = app.game.segment_timer_default_settings.SegmentTimerSettings(
		write=False, file_type='user')  # All values and keys are in string format
	return g.get_dict()


def csv_one_row_read(file_name):
	"""
	Creates a dictionary from the csv data with only 1 row of keys and 1 row of values.

	..warning: Path to file_name must be from app folder.
	"""
	file_mode = 'r'  # read
	binary_file = 'b'
	file_mode += binary_file
	f = open(file_name, file_mode)

	csv_reader = csv.DictReader(f, delimiter=',', quotechar="'")
	row = None
	for row in csv_reader:
		try:
			values = row.values()
			keys = row.keys()
			for i in range(len(row)):
				if values[i] == '':
					del row[keys[i]]
				elif values[i] == 'True' or values[i] == 'TRUE':
					row[keys[i]] = True
				elif values[i] == 'False' or values[i] == 'FALSE':
					row[keys[i]] = False
				else:
					row[keys[i]] = int(values[i])

		except ValueError:
			pass
	f.close()
	return row


def read_address_map(sport, sport_type, word_list_addr):
	"""
	Return an address map of the current sport with *all* alternates.

	This is built with "Spreadsheets/AddressMap.csv"
	"""
	address_map = 'Spreadsheets/AddressMap.csv'
	csv_reader = csv.DictReader(open(address_map, 'rb'), delimiter=',', quotechar="'")
	alt_dict = {}
	dictionary = dict.fromkeys(word_list_addr, 0)
	for row in csv_reader:
		try:
			sport_row = row['SPORT']
			sport_type_row = row['SPORT_TYPE']
			if sport_row == sport and sport_type_row == sport_type:
				address_word = int(row['ADDRESS_WORD_NUMBER'])
				alt = int(row['ALT'])
				del row['SPORT']
				del row['SPORT_TYPE']
				del row['ADDRESS_WORD_NUMBER']
				del row['ALT']

				if address_word in dictionary:
					if dictionary[address_word] == 0:
						alt_dict.clear()
						alt_dict[alt] = row
						dictionary[address_word] = alt_dict.copy()
					elif alt in dictionary[address_word]:
						alt_dict.clear()
						alt_dict[alt] = row
						dictionary[address_word] = alt_dict.copy()
					else:
						alt_dict[alt] = row
						dictionary[address_word] = alt_dict.copy()

			else:
				pass

		except ValueError:
			pass
	return dictionary


# Simulator functions


def readLXJumperDefinition(driverType, driverName):
	"""
	Return a jumperDict and a sizeDict.

	This is built with "Spreadsheets/ETN_Jumper_Definition.csv" or "Spreadsheets/LX_Jumper_Definition.csv"
	"""

	# Can't be used by base class because of driverType
	if driverType == 'ETNDriver':
		AddressMap = 'Spreadsheets/ETN_Jumper_Definition.csv'
	else:
		AddressMap = 'Spreadsheets/LX_Jumper_Definition.csv'

	csvReader = csv.DictReader(open(AddressMap, 'rb'), delimiter=',', quotechar="'")
	jumperDict = {}
	sizeDict = {}
	if driverName[-2] == '_':
		dn = driverName[:-2]
	else:
		dn = driverName
	for row in csvReader:
		try:
			driver = row['DRIVER']
			del row['DRIVER']

			if driver == '':
				pass
			elif driver == dn:
				jumperDict = row
			if driverType == 'ETNDriver':
				sizeDict[driver] = dict(row)
				del sizeDict[driver]['H9']
				del sizeDict[driver]['H10']
				del sizeDict[driver]['H11']
				del sizeDict[driver]['H12']
				del sizeDict[driver]['H13']
				del sizeDict[driver]['H16']
				del row['height']
				del row['width']
				del row['rows']
		except ValueError:
			pass

	for jumper in jumperDict:
		if jumperDict[jumper] == '':
			jumperDict[jumper] = 0
		else:
			jumperDict[jumper] = 1

	for driver in sizeDict:
		for element in sizeDict[driver]:
			sizeDict[driver][element] = int(sizeDict[driver][element])

	return jumperDict, sizeDict


def readMP_Keypad_Layouts():
	"""
	Uses Spreadsheets/MP_Keypad_Layouts.csv to build a dictionary of all keypads.
	"""
	# TODO: finish doing clean inspections from here
	MP_Keypad_Layouts='Spreadsheets/MP_Keypad_Layouts.csv'
	csvReader=csv.DictReader(open(MP_Keypad_Layouts, 'rb'), delimiter=',', quotechar="'")
	keypad=[]
	dictionary = {}
	for count, row in enumerate(csvReader):
		try:
			#print 'row', row
			values=row.values()
			#print values
			keypad.append(row['KEYPAD'])
			keys=row.keys()
			#print keys
			del row['KEYPAD']
			#print 'len-row', len(row)
			for i in range(len(row)+1):
				#raw_input('\nPress Enter to continue through loop\n')
				#print 'i', i
				#print values[i]
				if values[i]=='':
					#print '\nDeleting ', keys[i], ' because it is empty.\n'
					del row[keys[i]]
			#print row
			if row:
				dictionary[keypad[count]]=row
		except ValueError:
			print 'error, Check spreadsheet'

	#print dictionary.keys()
	return dictionary


def readMasksPerModel(model):
	"""
	Read Spreadsheets/Masks_Per_Model.csv and build 3 dictionaries and 3 variables.
	"""
	masksPerModel='Spreadsheets/Masks_Per_Model.csv'
	csvReader=csv.DictReader(open(masksPerModel, 'rb'), delimiter=',', quotechar="'")
	partsDict={}
	positionDict={}
	heightDict={}
	for count, row in enumerate(csvReader):
		try:
			modelRow=row['model']
			if modelRow=='':
				pass
			elif modelRow==model:
				del row['model']
				mask_ID=row['mask_ID']
				partsDict[modelRow]=row
				heightDict[row['positionTopToBot']]=float(row['boardHeight'])
				x=float(row['X'])
				y=float(row['Y'])
				coord=(x,y, row['positionTopToBot'])
				positionDict[mask_ID]=coord
				if row.has_key(''):
					del row['']
		except ValueError:
			pass

	boardWidth=float(partsDict[model]['boardWidth'])
	boardHeight=float(partsDict[model]['boardHeight'])
	return partsDict, positionDict, heightDict, boardWidth, boardHeight


def readLED_Positions(pcbSize, pcbType):
	"""
	Uses Spreadsheets/LED_Positions.csv to build a few dictionaries.
	"""
	LED_Positions='Spreadsheets/LED_Positions.csv'
	csvReader=csv.DictReader(open(LED_Positions, 'rb'), delimiter=',', quotechar="'")
	positionDict={}
	from collections import defaultdict
	segmentDict=defaultdict(list)
	segments={}
	specs={}
	for count, row in enumerate(csvReader):
		try:
			pcbSizeRow=row['pcbSize']
			pcbTypeRow=row['pcbType']
			if pcbSizeRow=='':
				pass
			elif pcbSizeRow==pcbSize:
				if pcbTypeRow==pcbType:
					designator=int(row['RefDes'])
					segment=row['segment']
					segments[segment]=0
					x=float(row['X'])/1000
					y=float(row['Y'])/-1000
					boundingX=float(row['boundingX'])/1000
					boundingY=float(row['boundingY'])/-1000
					boundingWidth=float(row['boundingWidth'])/1000
					boundingHeight=float(row['boundingHeight'])/-1000
					specs['boundingX']=boundingX
					specs['boundingY']=boundingY
					specs['boundingWidth']=boundingWidth
					specs['boundingHeight']=boundingHeight
					coord=(x,y)
					segmentDict[segment].append(designator)
					positionDict[designator]=coord
					#print self.positionDict, self.segmentDict
					if row.has_key(''):
						del row['']
					#raw_input()
		except ValueError:
			pass
	return positionDict, segmentDict, specs


def readMaskParts(maskType):
	"""
	Uses Spreadsheets/Masks_Parts.csv to build a few dictionaries.
	"""
	maskParts='Spreadsheets/Mask_Parts.csv'
	csvReader=csv.DictReader(open(maskParts, 'rb'), delimiter=',', quotechar="'")
	partsDict={}
	positionDict={}
	for count, row in enumerate(csvReader):
		try:
			mType=row['maskType']
			if mType=='':
				pass
			elif mType==maskType:
				del row['maskType']
				positionRtoL=row['positionRtoL']
				partsDict[mType]=row
				pcbSize=int(row['pcbSize'])
				pcbType=row['pcbType']
				x=float(row['X'])
				y=float(row['Y'])
				coord=(pcbSize, pcbType, x,y)
				positionDict[positionRtoL]=coord
				if row.has_key(''):
					del row['']
		except ValueError:
			pass
	#print self.positionDict
	maskWidth=float(partsDict[maskType]['maskWidth'])
	maskHeight=float(partsDict[maskType]['maskHeight'])
	maskRadius=float(partsDict[maskType]['maskRadius'])
	return partsDict, positionDict, maskWidth, maskHeight, maskRadius


def readChassisParts(maskType):
	"""
	Uses Spreadsheets/Chassis_Parts.csv to build a few dictionaries.
	"""
	chassisParts='Spreadsheets/Chassis_Parts.csv'
	csvReader=csv.DictReader(open(chassisParts, 'rb'), delimiter=',', quotechar="'")
	partsDict={}
	positionDict={}
	for count, row in enumerate(csvReader):
		try:
			mType=row['maskType']
			if mType=='':
				pass
			elif mType==maskType:
				del row['maskType']
				partsDict[mType]=row
				x=float(row['X'])
				y=float(row['Y'])
				coord=(x,y)
				positionDict[row['partType']+'_'+row['positionLtoR']]=coord
				if row['']=='':
					del row['']#This requires spreadsheet to have a note in a column with no row 1 value
		except ValueError:
			pass
	return partsDict, positionDict


def readLCDButtonMenus():
	"""Builds self.Menu_LCD_Text[func+menuNum]=row from the Spreadsheets/MenuMap.csv file."""
	MenuMap='Spreadsheets/MenuMap.csv'
	csvReader=csv.DictReader(open(MenuMap, 'rb'), delimiter=',', quotechar="'")
	Menu_LCD_Text={}
	for row in csvReader:
		try:
			func=row['function']
			menuNum=row['menuNumber']
			if func=='':
				pass
			else:
				if row['']=='':
					del row['']#This requires spreadsheet to have a note in a column with no row 1 value
				if row['varName']=='':
					row['varName']=None
				if row['varClock']=='':
					row['varClock']=None
				if row['team']=='':
					row['team']=None
				if row['gameSettingsFlag']=='':
					row['gameSettingsFlag']=None
				if row['blockNumList']=='':
					row['blockNumList']=None
				if row['places']=='':
					row['places']=None
				if row['col']=='':
					row['col']=None
				if row['row']=='':
					row['row']=None
				if row['startingMenuNumber']=='':
					row['startingMenuNumber']=None
				if row['endingMenuNumber']=='':
					row['endingMenuNumber']=None
				Menu_LCD_Text[func+menuNum]=row
		except ValueError:
			pass
	return Menu_LCD_Text


def readMP_Keypad_Button_Names():
	"""
	Uses Spreadsheets/MP_Keypad_Button_Names.csv to build a dictionary functions corresponding with the text on the button.
	"""
	MP_Keypad_Button_Names='Spreadsheets/MP_Keypad_Button_Names.csv'
	csvReader=csv.DictReader(open(MP_Keypad_Button_Names, 'rb'), delimiter=',', quotechar="'")
	dictionary = {}
	for row in csvReader:
		try:
			function=row['FUNCTION']
			buttonName=row['BUTTON_NAME']
			if row:
				dictionary[function]=buttonName
		except ValueError:
			print 'error'
	#print dictionary
	return dictionary
