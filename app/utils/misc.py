#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module holds all functions used outside of main program.

	:Created Date: 3/29/2018
	:Author: **Craig Gunter**

"""


def print_dict(dict_, print_dicts=True):
	"""
	Prints an alphabetized display of a dictionaries contents for debugging.
	"""
	keys = list(dict_.keys())
	values = []
	keys.sort(key=str.lower)
	for x in range(len(dict_)):
		valuex = dict_[keys[x]]
		values.append(valuex)
	count = 0
	print()
	if print_dicts:
		for x in range(len(dict_)):
			if (
					keys[x] == 'addrFuncDict' or keys[x] == 'funcDict'
					or keys[x] == 'functionDict' or keys[x] == 'Menu_LCD_Text'
					or keys[x] == 'fontDict' or keys[x] == 'gameFuncDict'):
				print(keys[x], ' = a huge dictionary...')
				print()
			else:
				print(keys[x], ' = ', values[x])
				print()
		print()
	else:
		for x in range(len(dict_)):
			try:
				list(values[x].values())
			except:
				print(keys[x], ' = ', values[x])
				count += 1
		print('\n', count, 'Individual Variables')

	print(len(dict_), 'Variables including Dictionaries')


def print_dicts_expanded(dict_, print_dict_=True):
	"""
	Prints an alphabetized display of a dictionaries contents for debugging
	then does again for each element in main dictionary.
	"""
	print_dict(dict_.__dict__, print_dicts=print_dict_)
	print('Main Dictionary')
	input()
	for data in dict_.__dict__:
		print('-----------------------------------')
		try:
			dict2 = vars(dict_)[data]
			print_dict(dict2, print_dicts=print_dict_)
			print('Dictionary', data)
		except:
			print(data, vars(dict_)[data])
		input()


def silent_remove(filename):
	"""
	Deletes a file but doesn't care if it is not there to begin with.
	"""
	import errno
	import os
	try:
		os.remove(filename)
	except OSError as e:  # this would be "except OSError, e:" before Python 2.6
		if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
			raise  # re-raise exception if a different error occurred


def save_object_to_file(dictionary, dictionary_name):
	import app.utils.configobj
	try:
		config_obj = app.utils.configobj.ConfigObj(dictionary_name)
		silent_remove(dictionary_name)
	except:
		print('Object does not exist!')
		raise

	try:
		config_obj.clear()
		config_obj.update(dictionary)
		config_obj.write()
	except:
		print('Saving Object Failed!')
		raise
