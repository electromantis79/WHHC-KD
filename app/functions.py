#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. topic:: Overview

    This module holds all of the global functions.

    :Created Date: 3/12/2015
    :Author: **Craig Gunter**
"""

# All Functions

import csv, time, os, timeit
from sys import platform as _platform

if _platform == "linux" or _platform == "linux2":
	try:
		import prctl
	except:
		pass

MIN = 1000
MAX = 0

sportList = [
	'MMBASEBALL3', 'MPBASEBALL1', 'MMBASEBALL4', 'MPLINESCORE4', 'MPLINESCORE5', 
	'MPMP-15X1', 'MPMP-14X1', 'MPMULTISPORT1-baseball', 'MPMULTISPORT1-football', 'MPFOOTBALL1', 'MMFOOTBALL4',
	'MPBASKETBALL1', 'MPSOCCER_LX1-soccer', 'MPSOCCER_LX1-football', 'MPSOCCER1', 'MPHOCKEY_LX1', 'MPHOCKEY1',
	'MPCRICKET1', 'MPRACETRACK1', 'MPLX3450-baseball', 'MPLX3450-football', 'MPGENERIC',  'MPSTAT']


def threadTimer(passed_function, period=.01, arg=None, alignTime=0.0):
	nextCall = time.time()
	startTime = time.time()
	#print 'startTime', startTime
	if _platform == "linux" or _platform == "linux2":
		os.nice(-1)
		if alignTime:
			#print 'alignTime', alignTime
			#print 'startTime', startTime
			nextCall = alignTime
			count = 0
			while (nextCall-startTime) < 0:
				nextCall = nextCall+period
				count += 1
			nextCall = nextCall+period*count
			#print count, nextCall

	stamp = 0
	#name = threading.current_thread().getName()+str(passed_function)
	if _platform == "linux" or _platform == "linux2":
		try:
			prctl.set_name(passed_function.__name__)
		except:
			pass
	while 1:
		stamp += 1
		#startTime=time.time()
		#print name, 'stamp1', stamp, nextCall-1486587172
		nextCall = nextCall+period
		#print name, 'stamp2', stamp, nextCall-1486587172
		if arg is not None:
			passed_function(arg)
		else:
			passed_function()
		#endTime=time.time()
		#elapse=endTime-startTime
		count = 0

		try:
			now = time.time()
			time.sleep(nextCall-now)
		except Exception as err:
			#print name, 'threadTimer sleep error is', err, 'for', function
			#print name, 'stamp3', stamp, nextCall-1486587172, 'nextCall-time.time()', nextCall-now
			while (nextCall-now) < 0:
				nextCall = nextCall+period
				count += 1
			#print name, 'stamp4', stamp, 'count', count
			#print name, 'stamp5', stamp, nextCall-1486587172
			nextCall = nextCall+period*count
			#print name, 'stamp6', stamp, nextCall-1486587172
			#nextCall=nextCall+period*(count+1)
			#print name, 'stamp7', stamp, 'count', count, nextCall-1486587172, nextCall-now
			try:
				now = time.time()
				time.sleep(nextCall-now)
			except:
				#print name, 'stamp8', stamp, 'count', count, nextCall-1486587172, nextCall-now
				#nextCall=nextCall+period*(count+3)
				time.sleep(period)


def elapseTime(passed_function, lowerLimit=0, On=False, Timeit=False):
	"""
	Simple function to test execution time of the passed function.
	Does not accept args.
	"""
	if On:
		startTime = time.time()
		result = passed_function()
		endTime = time.time()
		total_time = (endTime-startTime)*1000
		if total_time >= lowerLimit*1000:
			print passed_function, 'took', total_time, 'ms, lower limit=', str(lowerLimit)
	else:
		result = passed_function()

	if Timeit:
		t = timeit.Timer(passed_function, "print 'Timeit'")
		print t.timeit(1)*1000, 'ms'

	return result


def broadcast(server_socket, sock, message, SOCKET_LIST):
	# broadcast chat messages to all connected clients
	for socket in SOCKET_LIST:
		# send the message only to peer
		if socket != server_socket:
			try :
				socket.send(message)
			except :
				# broken socket connection
				socket.close()
				# broken socket, remove it
				if socket in SOCKET_LIST:
					SOCKET_LIST.remove(socket)
	return SOCKET_LIST

def tf(string):
	'''
	Returns boolean True for string = 'True' or string = 'TRUE' or returns boolean False for string = 'False' or string = 'FALSE'.
	'''
	if (string=='True' or string=='TRUE'):
		return True
	elif (string=='False' or string=='FALSE'):
		return False
	return

def verbose(messages=[], enable=1):
	'''
	Prints a list of items for debugging.
	'''
	#Use list format for messages
	if enable:
		for x, message in enumerate(messages):
			if x==len(messages)-1:
				print message
			else:
				print message,

def toggle(data):
	'''
	Inverts a boolean value.
	'''
	if data==True:
		data=False
	elif data==False:
		data=True
	else:
		raise ValueError('Only Boolean values allowed!!!!!')
	return data

def selectSportInstance(sport='GENERIC', numberOfTeams=2, MPLX3450Flag=False):
	'''
	Returns an object from the *Game* module based on the sport passed.
	'''
	from Config import Config
	c=Config()
	if sport=='MPMULTISPORT1-baseball' and MPLX3450Flag:
		sport='MPLX3450-baseball'
	elif sport=='MPMULTISPORT1-football' and MPLX3450Flag:
		sport='MPLX3450-football'
	c.writeSport(sport)

	choice=sportList.index(sport)+1
	#'MMBASEBALL3'#'MPBASEBALL1'#'MMBASEBALL4'
	#'MPMULTISPORT1-baseball'#'MPLX3450-baseball'
	#'MPLINESCORE4'#'MPLINESCORE5'#'MPMP-15X1'#'MPMP-14X1'
	if (choice>=1 and choice<=8) or choice==20:
		from game.Game import Baseball
		game=Baseball(numberOfTeams)

	#'MPMULTISPORT1-football'#'MPFOOTBALL1'#'MMFOOTBALL4'
	#'MPSOCCER_LX1-football'#'MPLX3450-football'
	elif choice==9 or choice==10 or choice==11 or choice==14 or choice==21:
		from game.Game import Football
		game=Football(numberOfTeams)

	elif choice==12:#'MPBASKETBALL1'
		from game.Game import Basketball
		game=Basketball(numberOfTeams)

	elif choice==13 or choice==15:#'MPSOCCER_LX1-soccer'#'MPSOCCER1'
		from game.Game import Soccer
		game=Soccer(numberOfTeams)

	elif choice==16 or choice==17:#'MPHOCKEY_LX1'#'MPHOCKEY1'
		from game.Game import Hockey
		game=Hockey(numberOfTeams)

	elif choice==18:#'MPCRICKET1'
		from game.Game import Cricket
		game=Cricket(numberOfTeams)

	elif choice==19:#'MPRACETRACK1'
		from game.Game import Racetrack
		game=Racetrack(numberOfTeams)
	elif choice==23:#'STAT'
		from game.Game import Stat
		game=Stat(numberOfTeams)
	elif choice==22:#'GENERIC'
		from game.Game import Game
		game=Game(numberOfTeams)
	return game

def readConfig():
	'''
	Returns a dictionary of the userConfig file.
	'''
	from Config import Config
	con = Config(write=False, fileType='user')
	configDict={}
	configDict = con.getDict()
	return configDict

def readGameDefaultSettings():
	'''
	Returns a dictionary of the gameUserSettings file.
	'''
	from app.game.GameDefaultSettings import GameDefaultSettings
	g = GameDefaultSettings(write=False, fileType='user')# All values and keys are in string format
	gameSettings = g.getDict()
	return gameSettings

def readSegmentTimerSettings():
	'''
	Returns a dictionary of the segmentTimerUserSettings file.
	'''
	from app.game.SegmentTimerDefaultSettings import SegmentTimerSettings
	g = SegmentTimerSettings(write=False, fileType='user')# All values and keys are in string format
	gameSettings = g.getDict()
	return gameSettings

def readAddressMap(sport, sportType, wordListAddr):
	'''
	Return an address map of the current sport with *all* alternates.

	This is built with "Spreadsheets/AddressMap.csv"
	'''
	AddressMap='Spreadsheets/AddressMap.csv'
	csvReader=csv.DictReader(open(AddressMap, 'rb'), delimiter=',', quotechar="'")
	AltDict = {}
	dictionary = dict.fromkeys(wordListAddr, 0)
	for row in csvReader:
		try:
			sportRow=row['SPORT']
			sportTypeRow=row['SPORT_TYPE']
			if sportRow==sport and sportTypeRow==sportType:
				addressWord=int(row['ADDRESS_WORD_NUMBER'])
				ALT=int(row['ALT'])
				#print '\nsport', sportRow,'\nsportType', sportTypeRow,'\naddressWord', addressWord,'\nALT', ALT
				del row['SPORT']
				del row['SPORT_TYPE']
				del row['ADDRESS_WORD_NUMBER']
				del row['ALT']

				if dictionary.has_key(addressWord):
					if dictionary[addressWord]==0:
						AltDict.clear()
						AltDict[ALT]=row
						copyDict=AltDict.copy()
						dictionary[addressWord]=copyDict
					elif dictionary[addressWord].has_key(ALT):
						AltDict.clear()
						AltDict[ALT]=row
						copyDict=AltDict.copy()
						dictionary[addressWord]=copyDict
					else:
						AltDict[ALT]=row
						copyDict=AltDict.copy()
						dictionary[addressWord]=copyDict


				#print '\nAltDict\n', AltDict, '\ndictionary\n', dictionary[addressWord]
				#AltDict.clear()
				#raw_input()
			else:
				#raw_input()
				pass

		except ValueError:
			print '\npass\n'
			raw_input()
			pass
	#print sport, sportType, dictionary
	return dictionary

def readLXJumperDefinition(driverType, driverName):
	#Can't be used by base class because of driverType
	if driverType=='ETNDriver':
		AddressMap='Spreadsheets/ETN_Jumper_Definition.csv'
	else:
		AddressMap='Spreadsheets/LX_Jumper_Definition.csv'
	csvReader=csv.DictReader(open(AddressMap, 'rb'), delimiter=',', quotechar="'")
	jumperDict = {}
	sizeDict = {}
	if driverName[-2]=='_':
		dn=driverName[:-2]
	else:
		dn=driverName
	for row in csvReader:
		try:
			driver=row['DRIVER']
			del row['DRIVER']

			if driver=='':
				pass
			elif driver==dn:
				jumperDict=row
			if driverType=='ETNDriver':
				sizeDict[driver]=dict(row)
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
		if jumperDict[jumper]=='':
			jumperDict[jumper]=0

		else:
			jumperDict[jumper]=1
	for driver in sizeDict:
		for element in sizeDict[driver]:
			sizeDict[driver][element]=int(sizeDict[driver][element])
	#print jumperDict
	return jumperDict, sizeDict

def readMP_Keypad_Layouts():
	'''
	Uses Spreadsheets/MP_Keypad_Layouts.csv to build a dictionary of all keypads.
	'''
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
	'''
	Read Spreadsheets/Masks_Per_Model.csv and build 3 dictionaries and 3 variables.
	'''
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
	'''
	Uses Spreadsheets/LED_Positions.csv to build a few dictionaries.
	'''
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
	'''
	Uses Spreadsheets/Masks_Parts.csv to build a few dictionaries.
	'''
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
	'''
	Uses Spreadsheets/Chassis_Parts.csv to build a few dictionaries.
	'''
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
	'''Builds self.Menu_LCD_Text[func+menuNum]=row from the Spreadsheets/MenuMap.csv file.'''
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
	'''
	Uses Spreadsheets/MP_Keypad_Button_Names.csv to build a dictionary functions corresponding with the text on the button.
	'''
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

def printDict(Dict, PrintDicts=True):
	'''
	Prints an alphebetized display of a dictionaries contents for debugging.
	'''
	keys = Dict.keys()
	values = []
	keys.sort(key=str.lower)
	for x in range(len(Dict)):
		valuex=Dict[keys[x]]
		values.append(valuex)
	count=0
	print
	if PrintDicts:
		for x in range(len(Dict)):
			if keys[x]=='addrFuncDict' or keys[x]=='funcDict' or keys[x]=='functionDict' or keys[x]=='Menu_LCD_Text' or keys[x]=='fontDict' or keys[x]=='gameFuncDict':
				print keys[x], ' = a huge dictionary...'
				print
			else:
				print keys[x], ' = ', values[x]
				print
		print
	else:
		for x in range(len(Dict)):
			try:
				values[x].values()
			except:
				print keys[x], ' = ', values[x]
				count += 1
		print '\n', count, 'Individual Variables'

	print len(Dict), 'Variables including Dictionaries'

def printDictsExpanded(Dict, PrintDict=True):
	'''
	Prints an alphebetized display of a dictionaries contents for debugging then does again for each element in main dictionary.
	'''
	printDict(Dict.__dict__, PrintDict)
	print 'Main Dictionary'
	raw_input()
	for data in Dict.__dict__:
		print('-----------------------------------')
		try:
			Dict2 = vars(Dict)[data]
			printDict(Dict2, PrintDict)
			print 'Dictionary', data
		except:
			print data, vars(Dict)[data]
		raw_input()

def csvOneRowRead(fileName):
	'''
	Creates a dictionary from the csv data with only 1 row of keys and 1 row of values.
	'''
	fileMode='r' #read
	binaryFile='b'
	fileMode+=binaryFile
	#print os.getcwd()
	f=open(fileName, fileMode)
	
	csvReader=csv.DictReader(f, delimiter=',', quotechar="'")
	for row in csvReader:
		try:
			#print 'row', row
			values=row.values()
			keys=row.keys()
			#print 'len-row', len(row)
			for i in range(len(row)):
				#raw_input('\nPress Enter to continue through loop\n')
				#print 'i', i
				if values[i]=='':
					#print '\nDeleting ', keys[i], ' because it is empty.\n'
					del row[keys[i]]
				elif values[i]=='True' or values[i]=='TRUE':
					row[keys[i]]=True
					#print '\nFound True or TRUE\n'
				elif values[i]=='False' or values[i]=='FALSE':
					row[keys[i]]=False
					#print '\nFound False or FALSE\n'
				else:
					row[keys[i]]=int(values[i])
					#print '\nFound Value\n'

				#print 'row', row
				#raw_input('\nPress Enter to continue through loop\n')
		except ValueError:
			pass
	f.close()
	return row

def silentremove(filename):
	'''
	Deletes a file but doesn't care if it is not there to begin with.
	'''
	import os, errno
	try:
		os.remove(filename)
	except OSError as e: # this would be "except OSError, e:" before Python 2.6
		if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
			raise # re-raise exception if a different error occured

def save_obj(obj, name ):
	'''
	Creates a .txt file with the objects name in obj folder.
	'''
	try:
		output_file=open('obj/'+name+'.txt','w')
		sortObj=obj.keys()
		sortObj.sort(key=str.lower)
		for element in sortObj:
			output_file.write(element+' = '+str(obj[element])+'\n')
		output_file.close()
	except Exception as er:
		print er

def _load_obj(name ):
	#broke
	try:
		input_file=open('obj/'+name+'.txt','r')
		obj = eval(input_file.read())
		input_file.close()
		return obj
	except Exception as er:
		print er

def activePlayerListSelect(game):
	'''
	Loads the current list of active players for the current team.
	'''
	activePlayerList=None
	if game.gameSettings['currentTeamGuest']:
		teamName='GUEST'
		team=game.guest
		try:
			activePlayerList=game.activeGuestPlayerList
		except:
			pass
	else:
		teamName=' HOME'
		team=game.home
		try:
			activePlayerList=game.activeHomePlayerList
		except:
			pass
	return activePlayerList, team, teamName

def binar(bina):
	'''
	Function rename to avoid conflict with PyQt bin() function.
	'''
	return bin(bina)

def _bitLen(int_type):
	length = 0
	while (int_type):
		int_type >>= 1
		length += 1
	return(length)

def fontWidth(list_type, space=False, fontName=None):
	'''
	Measures width of ETN character.
	'''
	#Use only after trim
	if space:
		if fontName is None:
			return 4
		elif fontName=='ETN14BoldCG':
			return 2
		elif fontName=='ETN14CondensedCG' or fontName=='ETN14RegularCG':
			return 3
		else:
			return 4
	else:
		maxWidth=[]
		#print 'list_type', list_type,
		for x, element in enumerate(list_type):
			maxWidth.append(_bitLen(list_type[x]))
		#print max(maxWidth)
		if len(maxWidth):
			return max(maxWidth)
		else:
			return 0

def fontTrim(fontList, shift=True, displayHeight=9):
	'''
	Trims the pixels around a ETN character. Standard font is in a 16 x 16 grid.
	'''
	if displayHeight==14:
		x=2
	else:
		x=7
	fontList.reverse()
	while x:
		fontList.pop()
		x-=1
	for x, element in enumerate(fontList):
		if shift:
			fontList[x]=element>>2
	return fontList

def saveObject2File(dictionary, dictionaryName):
	from configobj import ConfigObj
	try:
		configObj = ConfigObj(dictionaryName)
		silentremove(dictionaryName)
	except:
		raise
		print 'Object does not exist!'

	try:
		configObj.clear()
		configObj.update(dictionary)
		configObj.write()
	except:
		raise
		print 'Saving Object Failed!'
