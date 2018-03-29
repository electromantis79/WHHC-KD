#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module holds all functions exclusive to the simulator.

	:Created Date: 3/29/2018
	:Author: **Craig Gunter**

"""


def _bit_len(int_type):  # Used by font_width
	length = 0
	while int_type:
		int_type >>= 1
		length += 1
	return length


def font_width(list_type, space=False, font_name=None):
	"""
	Measures width of ETN character.
	"""
	# Use only after trim
	if space:
		if font_name is None:
			return 4
		elif font_name == 'ETN14BoldCG':
			return 2
		elif font_name == 'ETN14CondensedCG' or font_name == 'ETN14RegularCG':
			return 3
		else:
			return 4
	else:
		max_width = []
		for x, element in enumerate(list_type):
			max_width.append(_bit_len(list_type[x]))
		if len(max_width):
			return max(max_width)
		else:
			return 0


def font_trim(font_list, shift=True, display_height=9):
	"""
	Trims the pixels around a ETN character. Standard font is in a 16 x 16 grid.
	"""
	if display_height == 14:
		x = 2
	else:
		x = 7
	font_list.reverse()
	while x:
		font_list.pop()
		x -= 1
	for x, element in enumerate(font_list):
		if shift:
			font_list[x] = element >> 2
	return font_list


def binar(bina):
	"""
	Function rename to avoid conflict with PyQt bin() function.
	"""
	return bin(bina)
