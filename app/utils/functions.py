#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module holds the main functions.

	:Created Date: 3/12/2015
	:Author: **Craig Gunter**

"""

# All Functions

import time
import os
import timeit

from sys import platform as _platform

SPORT_LIST = [
	'MMBASEBALL3', 'MPBASEBALL1', 'MMBASEBALL4', 'MPLINESCORE4', 'MPLINESCORE5',
	'MPMP-15X1', 'MPMP-14X1', 'MPMULTISPORT1-baseball', 'MPMULTISPORT1-football', 'MPFOOTBALL1', 'MMFOOTBALL4',
	'MPBASKETBALL1', 'MPSOCCER_LX1-soccer', 'MPSOCCER_LX1-football', 'MPSOCCER1', 'MPHOCKEY_LX1', 'MPHOCKEY1',
	'MPCRICKET1', 'MPRACETRACK1', 'MPLX3450-baseball', 'MPLX3450-football', 'MPGENERIC', 'MPSTAT']


def thread_timer(passed_function, period=.01, arg=None, align_time=0.0):
	"""
	Wrapper to increase accuracy of calling a function periodically for linux.
	.. warning:: This only works if function takes less time to complete than the period.
	"""
	next_call = time.time()
	start_time = time.time()
	if _platform == "linux" or _platform == "linux2":
		os.nice(-1)
		if align_time:
			next_call = align_time
			count = 0
			while (next_call - start_time) < 0:
				next_call = next_call + period
				count += 1
			next_call = next_call + period * count
			print('thread_timer adjusted', start_time - align_time, 'seconds')

	stamp = 0
	while 1:
		stamp += 1
		next_call = next_call + period
		if arg is not None:
			passed_function(arg)
		else:
			passed_function()
		count = 0

		try:
			now = time.time()
			time.sleep(next_call - now)
		except:
			now = time.time()
			while (next_call - now) < 0:
				next_call = next_call + period
				count += 1
			next_call = next_call + period * count
			try:
				now = time.time()
				time.sleep(next_call - now)
			except:
				time.sleep(period)


def select_sport_instance(config_dict, number_of_teams=2):
	"""
	Returns an object from the *Game* module based on the sport passed.
	"""
	if config_dict['sport'] == 'MPMULTISPORT1-baseball' and config_dict['MPLX3450Flag']:
		config_dict['sport'] = 'MPLX3450-baseball'
	elif config_dict['sport'] == 'MPMULTISPORT1-football' and config_dict['MPLX3450Flag']:
		config_dict['sport'] = 'MPLX3450-football'

	# TODO: Move this out into Console function?
	# Write sport change from mp_lx3450_flag to config file
	import app.config_default_settings
	c = app.config_default_settings.Config()
	c.write_sport(config_dict['sport'])
	del c

	choice = SPORT_LIST.index(config_dict['sport']) + 1

	# 'MMBASEBALL3'#'MPBASEBALL1'#'MMBASEBALL4'
	# 'MPMULTISPORT1-baseball'#'MPLX3450-baseball'
	# 'MPLINESCORE4'#'MPLINESCORE5'#'MPMP-15X1'#'MPMP-14X1'
	if (1 <= choice <= 8) or choice == 20:
		from app.game.game import Baseball
		game = Baseball(config_dict, number_of_teams)

	# 'MPMULTISPORT1-football'#'MPFOOTBALL1'#'MMFOOTBALL4'
	# 'MPSOCCER_LX1-football'#'MPLX3450-football'
	elif (9 <= choice <= 11) or choice == 14 or choice == 21:
		from app.game.game import Football
		game = Football(config_dict, number_of_teams)

	elif choice == 12:  # 'MPBASKETBALL1'
		from app.game.game import Basketball
		game = Basketball(config_dict, number_of_teams)

	elif choice == 13 or choice == 15:  # 'MPSOCCER_LX1-soccer'#'MPSOCCER1'
		from app.game.game import Soccer
		game = Soccer(config_dict, number_of_teams)

	elif choice == 16 or choice == 17:  # 'MPHOCKEY_LX1'#'MPHOCKEY1'
		from app.game.game import Hockey
		game = Hockey(config_dict, number_of_teams)

	elif choice == 18:  # 'MPCRICKET1'
		from app.game.game import Cricket
		game = Cricket(config_dict, number_of_teams)

	elif choice == 19:  # 'MPRACETRACK1'
		from app.game.game import Racetrack
		game = Racetrack(config_dict, number_of_teams)
	elif choice == 23:  # 'STAT'
		from app.game.game import Stat
		game = Stat(config_dict, number_of_teams)
	elif choice == 22:  # 'GENERIC'
		from app.game.game import Game
		game = Game(config_dict, number_of_teams)
	else:
		print('sport not in list')
		raise Exception
	return game


def active_player_list_select(game):  # Used for Stat game methods
	"""
	Loads the current list of active players for the current team.
	"""
	active_player_list = None
	if game.gameSettings['currentTeamGuest']:
		team_name = 'GUEST'
		team = game.guest
		try:
			active_player_list = game.activeGuestPlayerList
		except:
			pass
	else:
		team_name = ' HOME'
		team = game.home
		try:
			active_player_list = game.activeHomePlayerList
		except:
			pass
	return active_player_list, team, team_name


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
			if x == len(messages) - 1:
				print(message)
			else:
				print(message, end=' ')


def elapse_time(passed_function, lower_limit=0, on=False, time_it=False):
	"""
	Simple function to test execution time of the passed function.
	Does not accept args.
	"""
	if on:
		start_time = time.time()
		result = passed_function()
		end_time = time.time()
		total_time = (end_time - start_time) * 1000
		if total_time >= lower_limit * 1000:
			print(passed_function, 'took', total_time, 'ms, lower limit=', str(lower_limit))
	else:
		result = passed_function()

	if time_it:
		t = timeit.Timer(passed_function, "print 'time_it'")
		print(t.timeit(1) * 1000, 'ms')

	return result
