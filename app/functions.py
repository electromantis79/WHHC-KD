#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. topic:: Overview

    This module holds all of the global functions.

    :Created Date: 3/12/2015
    :Author: **Craig Gunter**
"""

# All Functions

import time, os, timeit
from sys import platform as _platform

# thread_timer related
if _platform == "linux" or _platform == "linux2":
	try:
		import prctl
	except:
		pass

SPORT_LIST = [
	'MMBASEBALL3', 'MPBASEBALL1', 'MMBASEBALL4', 'MPLINESCORE4', 'MPLINESCORE5', 
	'MPMP-15X1', 'MPMP-14X1', 'MPMULTISPORT1-baseball', 'MPMULTISPORT1-football', 'MPFOOTBALL1', 'MMFOOTBALL4',
	'MPBASKETBALL1', 'MPSOCCER_LX1-soccer', 'MPSOCCER_LX1-football', 'MPSOCCER1', 'MPHOCKEY_LX1', 'MPHOCKEY1',
	'MPCRICKET1', 'MPRACETRACK1', 'MPLX3450-baseball', 'MPLX3450-football', 'MPGENERIC',  'MPSTAT']


def thread_timer(passed_function, period=.01, arg=None, align_time=0.0):
	next_call = time.time()
	start_time = time.time()
	#print 'start_time', start_time
	if _platform == "linux" or _platform == "linux2":
		os.nice(-1)
		if align_time:
			#print 'align_time', align_time
			#print 'start_time', start_time
			next_call = align_time
			count = 0
			while (next_call-start_time) < 0:
				next_call = next_call+period
				count += 1
			next_call = next_call+period*count
			#print count, next_call

	stamp = 0
	#name = threading.current_thread().getName()+str(passed_function)
	if _platform == "linux" or _platform == "linux2":
		try:
			prctl.set_name(passed_function.__name__)
		except:
			pass
	while 1:
		stamp += 1
		#start_time=time.time()
		#print name, 'stamp1', stamp, next_call-1486587172
		next_call = next_call+period
		#print name, 'stamp2', stamp, next_call-1486587172
		if arg is not None:
			passed_function(arg)
		else:
			passed_function()
		#endTime=time.time()
		#elapse=endTime-start_time
		count = 0

		try:
			now = time.time()
			time.sleep(next_call-now)
		except Exception as err:
			#print name, 'thread_timer sleep error is', err, 'for', function
			#print name, 'stamp3', stamp, next_call-1486587172, 'next_call-time.time()', next_call-now
			while (next_call-now) < 0:
				next_call = next_call+period
				count += 1
			#print name, 'stamp4', stamp, 'count', count
			#print name, 'stamp5', stamp, next_call-1486587172
			next_call = next_call+period*count
			#print name, 'stamp6', stamp, next_call-1486587172
			#next_call=next_call+period*(count+1)
			#print name, 'stamp7', stamp, 'count', count, next_call-1486587172, next_call-now
			try:
				now = time.time()
				time.sleep(next_call-now)
			except:
				#print name, 'stamp8', stamp, 'count', count, next_call-1486587172, next_call-now
				#next_call=next_call+period*(count+3)
				time.sleep(period)


def elapse_time(passed_function, lower_limit=0, on=False, time_it=False):
	"""
	Simple function to test execution time of the passed function.
	Does not accept args.
	"""
	if on:
		start_time = time.time()
		result = passed_function()
		end_time = time.time()
		total_time = (end_time-start_time)*1000
		if total_time >= lower_limit*1000:
			print passed_function, 'took', total_time, 'ms, lower limit=', str(lower_limit)
	else:
		result = passed_function()

	if time_it:
		t = timeit.Timer(passed_function, "print 'time_it'")
		print t.timeit(1)*1000, 'ms'

	return result


def tf(string):
	"""
	Returns boolean True for string = 'True' or string = 'TRUE'
	or returns boolean False for string = 'False' or string = 'FALSE'.
	"""
	if string == 'True' or string == 'TRUE':
		return True
	elif string == 'False' or string == 'FALSE':
		return False
	return None


def verbose(messages, enable=True):
	"""
	Prints a list of items for debugging.
	.. warning:: Only send list type messages.
	"""
	# Use list format for messages
	if enable:
		for x, message in enumerate(messages):
			if x == len(messages)-1:
				print message
			else:
				print message,


def select_sport_instance(sport='GENERIC', number_of_teams=2, mp_lx3450_flag=False):
	"""
	Returns an object from the *Game* module based on the sport passed.
	"""
	import config_default_settings
	c = config_default_settings.Config()
	if sport == 'MPMULTISPORT1-baseball' and mp_lx3450_flag:
		sport = 'MPLX3450-baseball'
	elif sport == 'MPMULTISPORT1-football' and mp_lx3450_flag:
		sport = 'MPLX3450-football'
	c.write_sport(sport)

	choice = SPORT_LIST.index(sport) + 1

	# 'MMBASEBALL3'#'MPBASEBALL1'#'MMBASEBALL4'
	# 'MPMULTISPORT1-baseball'#'MPLX3450-baseball'
	# 'MPLINESCORE4'#'MPLINESCORE5'#'MPMP-15X1'#'MPMP-14X1'
	if (1 <= choice <= 8) or choice == 20:
		from game.game import Baseball
		game = Baseball(number_of_teams)

	# 'MPMULTISPORT1-football'#'MPFOOTBALL1'#'MMFOOTBALL4'
	# 'MPSOCCER_LX1-football'#'MPLX3450-football'
	elif (9 <= choice <= 11) or choice == 14 or choice == 21:
		from game.game import Football
		game = Football(number_of_teams)

	elif choice == 12:  # 'MPBASKETBALL1'
		from game.game import Basketball
		game = Basketball(number_of_teams)

	elif choice == 13 or choice == 15:  # 'MPSOCCER_LX1-soccer'#'MPSOCCER1'
		from game.game import Soccer
		game = Soccer(number_of_teams)

	elif choice == 16 or choice == 17:  # 'MPHOCKEY_LX1'#'MPHOCKEY1'
		from game.game import Hockey
		game = Hockey(number_of_teams)

	elif choice == 18:  # 'MPCRICKET1'
		from game.game import Cricket
		game = Cricket(number_of_teams)

	elif choice == 19:  # 'MPRACETRACK1'
		from game.game import Racetrack
		game = Racetrack(number_of_teams)
	elif choice == 23:  # 'STAT'
		from game.game import Stat
		game = Stat(number_of_teams)
	elif choice == 22:  # 'GENERIC'
		from game.game import Game
		game = Game(number_of_teams)
	else:
		print 'sport not in list'
		raise Exception
	return game


def printDict(Dict, PrintDicts=True):
	"""
	Prints an alphebetized display of a dictionaries contents for debugging.
	"""
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
	"""
	Prints an alphebetized display of a dictionaries contents for debugging then does again for each element in main dictionary.
	"""
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


def silentremove(filename):
	"""
	Deletes a file but doesn't care if it is not there to begin with.
	"""
	import os, errno
	try:
		os.remove(filename)
	except OSError as e: # this would be "except OSError, e:" before Python 2.6
		if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
			raise # re-raise exception if a different error occured


def save_obj(obj, name ):
	"""
	Creates a .txt file with the objects name in obj folder.
	"""
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
	"""
	Loads the current list of active players for the current team.
	"""
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
	"""
	Function rename to avoid conflict with PyQt bin() function.
	"""
	return bin(bina)


def _bitLen(int_type):
	length = 0
	while (int_type):
		int_type >>= 1
		length += 1
	return(length)


def fontWidth(list_type, space=False, fontName=None):
	"""
	Measures width of ETN character.
	"""
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
	"""
	Trims the pixels around a ETN character. Standard font is in a 16 x 16 grid.
	"""
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
	import app.configobj
	try:
		configObj = app.configobj.ConfigObj(dictionaryName)
		silentremove(dictionaryName)
	except:
		print 'Object does not exist!'
		raise

	try:
		configObj.clear()
		configObj.update(dictionary)
		configObj.write()
	except:
		print 'Saving Object Failed!'
		raise
