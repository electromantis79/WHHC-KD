#!/usr/bin/python
# # -*- coding: utf-8 -*-

"""

.. topic:: Overview

	This module handles encoding game data in to the packet format.

	:Created Date: 3/16/2015
	:Author: **Craig Gunter**

"""


# TODO: correct naming conventions for local method variables

class SerialPacket (object):
	"""Creates serial packet object."""

	def __init__(self, game):
		self.game = game

		self.MPserial = False
		self.ETNFlag = False
		self.decodePacket = None
		self.printCorruption = False
		self.printETNData = False
		
		# Change flags
		self.ETNChangeFlag = False
		self.guestNameChangeFlag = False
		self.guestNameChangeOneCharFlag = False
		self.guestFontJustifyChangeFlag = False
		self.homeNameChangeFlag = False
		self.homeNameChangeOneCharFlag = False
		self.homeFontJustifyChangeFlag = False

	@staticmethod
	def _string_eater(packet, places=1):
		if packet is not None:
			packet = packet[places:]
		return packet

	# PUBLIC methods

	def encode_packet(self, print_string=False, e_t_n_flag=False, packet=None):
		"""Encodes packet for serial transmission or saves in-coming packet."""
		self.ETNFlag = e_t_n_flag
		self.decodePacket = packet  # packet variable should never be altered

		# This is the return value being built
		string = ''

		# Reset change flags
		self.ETNChangeFlag = False
		self.guestNameChangeFlag = False
		self.guestNameChangeOneCharFlag = False
		self.guestFontJustifyChangeFlag = False
		self.homeNameChangeFlag = False
		self.homeNameChangeOneCharFlag = False
		self.homeFontJustifyChangeFlag = False
		self.printCorruption = False
		self.printETNData = False
		
		# Start byte, 1B
		string += chr(0x01)
		
		if packet is not None:
			if packet:
				check = self._checksum_byte(string, packet=self.decodePacket)
				pack_start = self.decodePacket[0] != chr(0x01)
				pack_end = self.decodePacket[-1] != chr(0x04)
				if self.printCorruption and (pack_start or pack_end or check):
					print 'Packet Corruption'
					print 'packet[0]', self.decodePacket[0], 'chr(0x01)', chr(0x01), 'packet[0]!=chr(0x01)', pack_start
					print 'packet[-1]', self.decodePacket[-1], 'chr(0x04)', chr(0x04), 'packet[-1]!=chr(0x04)', pack_end
					print 'self.checksumByte() returns', check
					return 0
			length_check = self.version_i_d_byte(string, packet=packet, length_check=True)
			if length_check is None:
				return 0

			# Remove start byte
			self.decodePacket = self._string_eater(self.decodePacket)

		string = self.version_i_d_byte(string, packet=self.decodePacket)

		if not (self.game.gameData['sportType'] == 'stat' or self.ETNFlag):
			string = self._period_clock_string(string, packet=self.decodePacket)

			if self.game.gameData['sportType'] == 'football' or self.game.gameData['sportType'] == 'soccer':
				play_clock_flag = True
			else:
				play_clock_flag = False
			string = self._play_shot_clock_string(string, play_clock_flag=play_clock_flag, packet=self.decodePacket)

			string = self._time_out_clock_string(string, packet=self.decodePacket)

			string = self._time_of_day_clock_string(string, packet=self.decodePacket)

			string = self._practice_clock_string(string, packet=self.decodePacket)

			string = self._segment_count_string(string, packet=self.decodePacket)

			if self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
				string = self._timer_activity_indicator_string(string, packet=self.decodePacket)

		for team in [self.game.guest, self.game.home]:
			if self.ETNFlag:
				string = self._team_e_t_n_string(string, team, packet=self.decodePacket)
			elif self.game.gameData['sportType'] == 'stat':
				string = self._team_stat_string(string, team, packet=self.decodePacket)
			else:
				string = self._team_score_string(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
					string = self._team_h_epitch_count_string(string, team, packet=self.decodePacket)
				elif self.game.gameData['sportType'] == 'football' or self.game.gameData['sportType'] == 'basketball':
					string = self._team_time_outs_left_string(string, team, packet=self.decodePacket)
				elif self.game.gameData['sportType'] == 'soccer' or self.game.gameData['sportType'] == 'hockey':
					string = self._team_shots_saves_kicks_string(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType'] == 'soccer' or self.game.gameData['sportType'] == 'hockey':
					string = self._team_goal_indicator_string(string, team, packet=self.decodePacket)

				if not (self.game.gameData['sportType'] == 'stat' or self.game.gameData['sportType'] == 'hockey' or self.ETNFlag):
					string = self._team_possession_string(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType'] == 'soccer' or self.game.gameData['sportType'] == 'hockey':
					string = self._team_penalty_indicator_count_string(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType'] == 'basketball':
					string = self._team_bonus_string(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
					string = self._team_inning_score_string(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType'] == 'hockey':
					string = self._team_penalty_player_number_clock_string(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType'] == 'basketball':
					string = self._team_goal_indicator_string(string, team, packet=self.decodePacket)

					string = self._team_fouls_player_number_fouls_string(string, team, packet=self.decodePacket)

		if not self.ETNFlag:
			if not self.game.gameData['sportType'] == 'stat':
				string = self._period_inning_string(string, packet=self.decodePacket)

			if self.game.gameData['sportType'] == 'football':
				string = self._extra_football_string(string, packet=self.decodePacket)

			if self.game.gameData['sportType'] == 'basketball':
				string = self._player_number_fouls_string(string, packet=self.decodePacket)

			if self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
				string = self._extra_baseball_string(string, packet=self.decodePacket)

			if not self.game.gameData['sportType'] == 'stat':
				string = self._horn_one_two_string(string, packet=self.decodePacket)

			if (
					self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore'
					or self.game.gameData['sportType'] == 'basketball' or self.game.gameData['sportType'] == 'hockey'):
				string = self._shot_horn_string(string, packet=self.decodePacket)

		string = self._reserved_string(string, packet=self.decodePacket)

		if packet is None:
			string = self._checksum_byte(string, packet=self.decodePacket)

			# Stop byte
			string += chr(0x04)

			# Print string for testing
			if print_string:
				print string
				print 'length', len(string)

			return string
		else:
			
			# Clear flag if set by lengthCheck version of versionIDByte
			self.ETNFlag = False
			
			if print_string:
				print self.decodePacket
				print 'length', len(self.decodePacket)
			return packet

	def version_i_d_byte(self, string, packet=None, length_check=False):
		"""
		Adds sport ID and packet format version to string.
		If length_check, it confirms length and checks for ETN injection.
		"""

		# Sport and version byte, 2
		if self.ETNFlag:
			sport = 'N'
			version = '1'
			packet_length = 60
		elif self.game.gameData['sportType'] == 'football':
			sport = 'F'
			version = '1'
			packet_length = 80
		elif self.game.gameData['sportType'] == 'basketball':
			sport = 'K'
			version = '1'
			packet_length = 100
		elif self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
			sport = 'B'
			version = '1'
			packet_length = 160
		elif self.game.gameData['sportType'] == 'soccer':
			sport = 'S'
			version = '1'
			packet_length = 90
		elif self.game.gameData['sportType'] == 'hockey':
			sport = 'H'
			version = '1'
			packet_length = 110
		elif self.game.gameData['sportType'] == 'stat':
			sport = 'P'
			version = '1'
			packet_length = 90
		partial_string = sport+version
		string += partial_string

		if length_check:
			if len(packet) > 1 and packet[1] == 'N':
				self.ETNFlag = True
				packet_length = 60

			if self.printCorruption and len(packet) != packet_length and not self.MPserial:
				string = None
				print 'Packet Length Error'
				print 'len(packet), packet_length = ', len(packet), packet_length
				print 'self.decodePacket "', self.decodePacket, '"END\n'
				return string

		else:
			self.decodePacket = self._string_eater(self.decodePacket, places=len(partial_string))

		return string

	# END PUBLIC methods -----------------------------------------------------

	def _get_value(self, value_name, min_value_not_blanked=1, team=None):
		if team is None:
			# gameData, clockData is saved in gameData
			if min_value_not_blanked <= self.game.gameData[value_name] <= 9:
				value = self.game.gameData[value_name]
			else:
				value = ' '
		else:
			# teamData
			if min_value_not_blanked <= self.game.get_team_data(team, value_name) <= 9:
				value = self.game.get_team_data(team, value_name)
			else:
				value = ' '
		return value

	def _period_clock_string(self, string, packet=None):
		"""Prepare all period clock bytes HH:MM:SS.xcm, 12"""
		clockName = 'periodClock'
		timeListNames = [
			'daysTens', 'daysUnits', 'hoursTens',
			'hoursUnits', 'minutesTens', 'minutesUnits', 'secondsTens',
			'secondsUnits', 'tenthsUnits', 'hundredthsUnits']
		if packet is not None:
			if packet[0] == ' ':
				hoursTensByte = 0
			else:
				hoursTensByte = int(packet[0])
			if packet[1] == ' ':
				hoursUnitsByte = 0
			else:
				hoursUnitsByte = int(packet[1])
			self.game.set_clock_data(clockName, timeListNames[2], hoursTensByte, 1)
			self.game.set_clock_data(clockName, timeListNames[3], hoursUnitsByte, 1)
			if packet[2] == ' ':
				hoursColonByte = 0
			else:
				hoursColonByte = 1
			# self.game.set_game_data('hoursColonIndicator', hoursColonByte) Does not exist
			if packet[3] == ' ':
				minutesTensByte = 0
			else:
				minutesTensByte = int(packet[3])
			if packet[4] == ' ':
				minutesUnitsByte = 0
			else:
				minutesUnitsByte = int(packet[4])
			self.game.set_clock_data(clockName, timeListNames[4], minutesTensByte, 1)
			self.game.set_clock_data(clockName, timeListNames[5], minutesUnitsByte, 1)
			if packet[5] == ' ':
				colonByte = 0
				# self.game.gameData['colonIndicator']=False
				# self.game.gameData['decimalIndicator']=True
				periodClockTenthsFlag = True
			else:
				colonByte = 1
				# self.game.gameData['colonIndicator']=True
				# self.game.gameData['decimalIndicator']=False
				periodClockTenthsFlag = False
			if self.game.gameSettings['trackClockEnable']:
				colonByte = 1
			self.game.set_game_data('colonIndicator', colonByte)
			if packet[6] == ' ':
				secondsTensByte = 0
			else:
				secondsTensByte = int(packet[6])
			if packet[7] == ' ':
				secondsUnitsByte = 0
			else:
				secondsUnitsByte = int(packet[7])
			self.game.set_clock_data(clockName, timeListNames[6], secondsTensByte, 1)
			self.game.set_clock_data(clockName, timeListNames[7], secondsUnitsByte, 1)
			decimalByte = not colonByte
			if self.game.gameSettings['trackClockEnable']:
				if packet[8] == ' ':
					decimalByte = 0
					periodClockTenthsFlag = 0
				else:
					decimalByte = 1
					periodClockTenthsFlag = 1
			self.game.gameSettings['periodClockTenthsFlag'] = periodClockTenthsFlag
			self.game.set_game_data('decimalIndicator', decimalByte)
			if packet[9] == ' ':
				tenthsUnitsByte = 0
			else:
				tenthsUnitsByte = int(packet[9])
			if packet[10] == ' ':
				hundredthsUnitsByte = 0
			else:
				hundredthsUnitsByte = int(packet[10])
			if packet[11] == ' ':
				thousandthsUnitsByte = 0
			else:
				thousandthsUnitsByte = int(packet[11])
			self.game.set_clock_data(clockName, timeListNames[8], tenthsUnitsByte, 1)
			self.game.set_clock_data(clockName, timeListNames[9], hundredthsUnitsByte, 1)
			# self.game.set_clock_data(clockName, thousandthsUnits', thousandthsUnitsByte, 1) Does not exist

		# Make the clock variables
		# colon = self.game.gameData['colonIndicator']

		# Hours behavior
		hoursTensByte = self._get_value(clockName + '_' + 'hoursTens', min_value_not_blanked=1)  # blank if 0
		hoursUnitsByte = self._get_value(
			clockName+'_'+'hoursUnits', min_value_not_blanked=hoursTensByte == ' ')  # blank if zero if previous blank
		if hoursTensByte == ' ' and hoursUnitsByte == ' ':
			# blank if both are blank
			hoursColonByte = ' '
		else:
			hoursColonByte = ':'

		# Minutes behavior
		minutesTensByte = self._get_value(
			clockName+'_'+'minutesTens', min_value_not_blanked=hoursColonByte == ' ')  # blank if zero if previous blank
		minutesUnitsByte = self._get_value(
			clockName+'_'+'minutesUnits', min_value_not_blanked=minutesTensByte == ' ')  # blank if zero if previous blank
		if minutesTensByte == ' ' and minutesUnitsByte == ' ':
			# blank if both are blank
			colonByte = ' '
		else:
			colonByte = ':'

		# Seconds behavior
		secondsTensByte = self._get_value(
			clockName+'_'+'secondsTens', min_value_not_blanked=colonByte == ' ')  # blank if zero if previous blank
		secondsUnitsByte = self._get_value(clockName + '_' + 'secondsUnits', min_value_not_blanked=0)
		
		# Decimal behavior
		if self.game.gameData[clockName+'_'+'tenthsUnits'] == 15:
			decimalByte = ' '
		else:
			decimalByte = '.'

		# Sub-second behavior
		if 1:  # decimalByte == '.':
			tenthsUnitsByte = self._get_value(clockName + '_' + 'tenthsUnits', min_value_not_blanked=0)
			hundredthsUnitsByte = ' '  # self.getValue(clockName+'_'+'hundredthsUnits', minValueNotBlanked=0)
		else:
			tenthsUnitsByte = ' '
			hundredthsUnitsByte = ' '
		
		LINE5andCjumper = self.game.gameData['sport'] == 'MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']
		MULTIbaseOr3450baseCjumper = (
				(
					self.game.gameData['sport'] == 'MPMULTISPORT1-baseball'
					or self.game.gameData['sport'] == 'MPLX3450-baseball'
				)
				and 'C' in self.game.gameData['optionJumpers'])
		BASE1orBASE3Cjumper = (
				(
						self.game.gameData['sport'] == 'MPBASEBALL1' or self.game.gameData['sport'] == 'MMBASEBALL3')
				and 'C' in self.game.gameData['optionJumpers'])
		
		# Override if 2 digit clock baseball
		if LINE5andCjumper or MULTIbaseOr3450baseCjumper or BASE1orBASE3Cjumper:
			decimalByte = ' '
			tenthsUnitsByte = ' '
			hundredthsUnitsByte = ' '
			
		# Thousandths not currently used
		thousandthsUnitsByte = ' '

		# Format as a string
		periodClock = (
			hoursTensByte, hoursUnitsByte, hoursColonByte, minutesTensByte, minutesUnitsByte, colonByte,
			secondsTensByte, secondsUnitsByte, decimalByte,	tenthsUnitsByte, hundredthsUnitsByte, thousandthsUnitsByte)
		clockS = '%s%s%s%s%s%s%s%s%s%s%s%s' % periodClock

		# Period clock byte(s) HH:MM:SS.xcm , 12
		self.decodePacket = self._string_eater(self.decodePacket, places=len(clockS))
		string += clockS
		return string

	def _play_shot_clock_string(self, string, play_clock_flag=True, packet=None):
		# play_shot clock byte(s), SS.x, 4

		if play_clock_flag:
			name = 'delayOfGameClock'
		else:
			name = 'shotClock'

		if packet is not None:
			if packet[0] == ' ':
				play_shotTensByte = 255
			else:
				play_shotTensByte = int(packet[0])
			if packet[1] == ' ':
				play_shotUnitsByte = 255
			else:
				play_shotUnitsByte = int(packet[1])
			self.game.set_clock_data(name, 'secondsTens', play_shotTensByte, 1)
			self.game.set_clock_data(name, 'secondsUnits', play_shotUnitsByte, 1)
			if packet[2] == ' ':
				play_shotDecimalByte = 0
			else:
				play_shotDecimalByte = 1
			# self.game.set_game_data('play_shotDecimalIndicator', play_shotDecimalByte) Does not exist
			if packet[3] == ' ':
				play_shotTenthsByte = 0
			else:
				play_shotTenthsByte = 1
			# self.game.set_clock_data(name, '_tenthsUnits', play_shotTenthsByte) Does not exist

		play_shotTensByte = self._get_value(name + '_secondsTens', min_value_not_blanked=1)
		play_shotUnitsByte = self._get_value(name + '_secondsUnits', min_value_not_blanked=0)

		# Decimal is not currently used
		play_shotDecimalFlag = False
		if play_shotDecimalFlag:
			play_shotDecimalByte = '.'
		else:
			play_shotDecimalByte = ' '

		# Tenths units is not currently used
		if play_shotDecimalByte == '.':
			play_shotTenthsByte = self._get_value(name + '_tenthsUnits', min_value_not_blanked=0)
		else:
			play_shotTenthsByte = ' '

		play_shotClock = '%s%s%s%s' % (play_shotTensByte, play_shotUnitsByte, play_shotDecimalByte, play_shotTenthsByte)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(play_shotClock))
		string += play_shotClock
		return string

	def _time_out_clock_string(self, string, packet=None):
		# Time out clock byte(s), MM:SS, 5
		clockName = 'timeOutTimer'

		if packet is not None:
			if packet[0] == ' ':
				minutesTensByte = 0
			else:
				minutesTensByte = int(packet[0])
			if packet[1] == ' ':
				minutesUnitsByte = 0
			else:
				minutesUnitsByte = int(packet[1])
			self.game.set_game_data(clockName + '_' + 'minutesTens', minutesTensByte, 1)
			self.game.set_game_data(clockName + '_' + 'minutesUnits', minutesUnitsByte, 1)
			if packet[2] == ' ':
				colonByte = 0
			else:
				colonByte = 1
			# This colon breaks the main colon from period clock
			# self.game.set_game_data('colonIndicator', colonByte)
			if packet[3] == ' ':
				secondsTensByte = 0
			else:
				secondsTensByte = int(packet[3])
			if packet[4] == ' ':
				secondsUnitsByte = 0
			else:
				secondsUnitsByte = int(packet[4])
			self.game.set_game_data(clockName + '_' + 'secondsTens', secondsTensByte, 1)
			self.game.set_game_data(clockName + '_' + 'secondsUnits', secondsUnitsByte, 1)

		# Minutes behavior
		minutesTensByte = self._get_value(clockName + '_' + 'minutesTens', min_value_not_blanked=1)
		minutesUnitsByte = self._get_value(clockName + '_' + 'minutesUnits', min_value_not_blanked=minutesTensByte == ' ')
		if minutesTensByte == ' ' and minutesUnitsByte == ' ':
			colonByte = ' '
		else:
			colonByte = ':'

		# Seconds behavior
		secondsTensByte = self._get_value(clockName + '_' + 'secondsTens', min_value_not_blanked=minutesUnitsByte == ' ')
		secondsUnitsByte = self._get_value(clockName + '_' + 'secondsUnits', min_value_not_blanked=0)

		# Format as a string
		timeOutClock = (minutesTensByte, minutesUnitsByte, colonByte, secondsTensByte, secondsUnitsByte)
		clockS = '%s%s%s%s%s' % timeOutClock
		self.decodePacket = self._string_eater(self.decodePacket, places=len(clockS))
		string += clockS
		return string

	def _time_of_day_clock_string(self, string, packet=None):
		# time of day byte(s), CCHH:MM:SS, 10

		# Make the clock variables
		clockName = 'timeOfDayClock'
		# colon = self.game.gameData['colonIndicator']
		timeListNames = [
			'daysTens', 'daysUnits', 'hoursTens', 'hoursUnits', 'minutesTens', 'minutesUnits',
			'secondsTens', 'secondsUnits', 'tenthsUnits', 'hundredthsUnits']

		if packet is not None:
			CCBYTES = packet[:2] == 'AM'

			if packet[2] == ' ':
				hoursTensByte = 0
			else:
				hoursTensByte = int(packet[2])
			if packet[3] == ' ':
				hoursUnitsByte = 0
			else:
				hoursUnitsByte = int(packet[3])
			self.game.set_game_data(clockName + '_' + timeListNames[2], hoursTensByte, 1)
			self.game.set_game_data(clockName + '_' + timeListNames[3], hoursUnitsByte, 1)
			if packet[4] == ' ':
				hoursColonByte = 0
			else:
				hoursColonByte = 1
			# self.game.set_game_data('hoursColonIndicator', hoursColonByte) Does not exist
			if packet[5] == ' ':
				minutesTensByte = 0
			else:
				minutesTensByte = int(packet[5])
			if packet[6] == ' ':
				minutesUnitsByte = 0
			else:
				minutesUnitsByte = int(packet[6])
			self.game.set_game_data(clockName + '_' + timeListNames[4], minutesTensByte, 1)
			self.game.set_game_data(clockName + '_' + timeListNames[5], minutesUnitsByte, 1)
			if packet[7] == ' ':
				colonByte = 0
			else:
				colonByte = 1
			# This colon breaks the main colon from period clock
			# self.game.set_game_data('colonIndicator', colonByte)
			if packet[8] == ' ':
				secondsTensByte = 0
			else:
				secondsTensByte = int(packet[8])
			if packet[9] == ' ':
				secondsUnitsByte = 0
			else:
				secondsUnitsByte = int(packet[9])
			self.game.set_game_data(clockName + '_' + timeListNames[6], secondsTensByte, 1)
			self.game.set_game_data(clockName + '_' + timeListNames[7], secondsUnitsByte, 1)

		# CC=24 or AM or PM
		if self.game.get_clock_data(clockName, 'PM'):
			CCBYTES = 'PM'
		else:
			CCBYTES = 'AM'
		# FIXME: check 24 and ask internal clock source question

		# Hours behavior
		hoursTensByte = self._get_value(clockName + '_' + 'hoursTens', min_value_not_blanked=1)
		hoursUnitsByte = self._get_value(clockName + '_' + 'hoursUnits', min_value_not_blanked=hoursTensByte == ' ')
		if hoursTensByte == ' ' and hoursUnitsByte == ' ':
			hoursColonByte = ' '
		else:
			hoursColonByte = ':'

		# Minutes behavior
		minutesTensByte = self._get_value(clockName + '_' + 'minutesTens', min_value_not_blanked=0)
		minutesUnitsByte = self._get_value(clockName + '_' + 'minutesUnits', min_value_not_blanked=minutesTensByte == ' ')
		if minutesTensByte == ' ' and minutesUnitsByte == ' ':
			colonByte = ' '
		else:
			colonByte = ':'

		# Seconds behavior
		secondsTensByte = self._get_value(clockName + '_' + 'secondsTens', min_value_not_blanked=minutesUnitsByte == ' ')
		secondsUnitsByte = self._get_value(clockName + '_' + 'secondsUnits', min_value_not_blanked=0)

		# Format as a string
		timeOfDay = (
			CCBYTES, hoursTensByte, hoursUnitsByte, hoursColonByte,
			minutesTensByte, minutesUnitsByte, colonByte,
			secondsTensByte, secondsUnitsByte)
		clockS = '%s%s%s%s%s%s%s%s%s' % timeOfDay
		self.decodePacket = self._string_eater(self.decodePacket, places=len(clockS))
		string += clockS
		return string

	def _practice_clock_string(self, string, packet=None):
		# Practice clock byte(s), HH:MM:SS.xcm, 12

		# Make the clock variables
		clockName = 'segmentTimer'
		# colon = self.game.gameData['colonIndicator']
		timeListNames = [
			'daysTens', 'daysUnits', 'hoursTens', 'hoursUnits', 'minutesTens', 'minutesUnits',
			'secondsTens', 'secondsUnits', 'tenthsUnits', 'hundredthsUnits']

		if packet is not None:
			if packet[0] == ' ':
				hoursTensByte = 0
			else:
				hoursTensByte = int(packet[0])
			if packet[1] == ' ':
				hoursUnitsByte = 0
			else:
				hoursUnitsByte = int(packet[1])
			self.game.set_game_data(clockName + '_' + timeListNames[2], hoursTensByte, 1)
			self.game.set_game_data(clockName + '_' + timeListNames[3], hoursUnitsByte, 1)
			if packet[2] == ' ':
				hoursColonByte = 0
			else:
				hoursColonByte = 1
			# self.game.set_game_data('hoursColonIndicator', hoursColonByte) Does not exist
			if packet[3] == ' ':
				minutesTensByte = 0
			else:
				minutesTensByte = int(packet[3])
			if packet[4] == ' ':
				minutesUnitsByte = 0
			else:
				minutesUnitsByte = int(packet[4])
			self.game.set_game_data(clockName + '_' + timeListNames[4], minutesTensByte, 1)
			self.game.set_game_data(clockName + '_' + timeListNames[5], minutesUnitsByte, 1)
			if packet[5] == ' ':
				colonByte = 0
			else:
				colonByte = 1
			# This colon breaks the main colon from period clock
			# self.game.set_game_data('colonIndicator', colonByte)
			if packet[6] == ' ':
				secondsTensByte = 0
			else:
				secondsTensByte = int(packet[6])
			if packet[7] == ' ':
				secondsUnitsByte = 0
			else:
				secondsUnitsByte = int(packet[7])
			self.game.set_game_data(clockName + '_' + timeListNames[6], secondsTensByte, 1)
			self.game.set_game_data(clockName + '_' + timeListNames[7], secondsUnitsByte, 1)
			if packet[8] == ' ':
				decimalByte = 0
			else:
				decimalByte = 1
			# self.game.set_game_data('decimalIndicator', decimalByte) Does not exist
			if packet[9] == ' ':
				tenthsUnitsByte = 0
			else:
				tenthsUnitsByte = int(packet[9])
			if packet[10] == ' ':
				hundredthsUnitsByte = 0
			else:
				hundredthsUnitsByte = int(packet[10])
			if packet[11] == ' ':
				thousandthsUnitsByte = 0
			else:
				thousandthsUnitsByte = int(packet[11])
			self.game.set_game_data(clockName + '_' + timeListNames[8], tenthsUnitsByte, 1)
			self.game.set_game_data(clockName + '_' + timeListNames[9], hundredthsUnitsByte, 1)
			# self.game.set_game_data(clockName+'_'+'thousandthsUnits', thousandthsUnitsByte, 1) Does not exist

		# Hours behavior
		hoursTensByte = self._get_value(clockName + '_' + 'hoursTens', min_value_not_blanked=1)
		hoursUnitsByte = self._get_value(clockName + '_' + 'hoursUnits', min_value_not_blanked=hoursTensByte == ' ')
		if hoursTensByte == ' ' and hoursUnitsByte == ' ':
			hoursColonByte = ' '
		else:
			hoursColonByte = ':'

		# Minutes behavior
		minutesTensByte = self._get_value(clockName + '_' + 'minutesTens', min_value_not_blanked=hoursColonByte == ' ')
		minutesUnitsByte = self._get_value(clockName + '_' + 'minutesUnits', min_value_not_blanked=minutesTensByte == ' ')
		if minutesTensByte == ' ' and minutesUnitsByte == ' ':
			colonByte = ' '
		else:
			colonByte = ':'

		# Seconds behavior
		secondsTensByte = self._get_value(clockName + '_' + 'secondsTens', min_value_not_blanked=minutesUnitsByte == ' ')
		secondsUnitsByte = self._get_value(clockName + '_' + 'secondsUnits', min_value_not_blanked=0)
		if colonByte == ' ':
			decimalByte = '.'
		else:
			decimalByte = ' '

		# Sub-second behavior
		if decimalByte == '.':
			tenthsUnitsByte = self._get_value(clockName + '_' + 'tenthsUnits', min_value_not_blanked=0)
			hundredthsUnitsByte = self._get_value(clockName + '_' + 'hundredthsUnits', min_value_not_blanked=0)
		else:
			tenthsUnitsByte = ' '
			hundredthsUnitsByte = ' '

		# Thousandths not currently used
		thousandthsUnitsByte = ' '

		# Format as a string
		segmentTimer = (
			hoursTensByte, hoursUnitsByte, hoursColonByte, minutesTensByte, minutesUnitsByte, colonByte,
			secondsTensByte, secondsUnitsByte, decimalByte, tenthsUnitsByte, hundredthsUnitsByte, thousandthsUnitsByte)
		clockS = '%s%s%s%s%s%s%s%s%s%s%s%s' % segmentTimer

		# TODO: Could make method for this cause it matches the periodClock one

		self.decodePacket = self._string_eater(self.decodePacket, places=len(clockS))
		string += clockS
		return string

	def _segment_count_string(self, string, packet=None):
		# Segment count byte(s), 2w
		if packet is not None:
			if packet[0] == ' ':
				segTen = 0
			else:
				segTen = int(packet[0])
			if packet[1] == ' ':
				segUnit = 0
			else:
				segUnit = int(packet[1])
			self.game.set_game_data('segmentCountTens', segTen, 1)
			self.game.set_game_data('segmentCountUnits', segUnit, 1)

		segTen = self._get_value('segmentCountTens', min_value_not_blanked=1)
		segUnit = self._get_value('segmentCountUnits', min_value_not_blanked=0)
		segmentCount = '%s%s' % (segTen, segUnit)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(segmentCount))
		string += segmentCount
		return string

	def _timer_activity_indicator_string(self, string, packet=None):
		# Timer Activity Indicator (Blinky) byte(s), 1
		if packet is not None:
			if packet[0] == ' ':
				colonIndicator = 0
			else:
				colonIndicator = 1

			if (
					(0 and self.game.gameData['sport'] == 'MPLX3450-baseball')
					or self.game.gameSettings['clock_3D_or_less_Flag'] or self.game.gameSettings['2D_Clock']):
				# TODO: Need to fix this to override only when in correct modes per sport

				self.game.set_game_data('colonIndicator', colonIndicator, 1)
				self.game.set_game_data('decimalIndicator', 0, 1)
		
		if self.game.get_game_data('colonIndicator') and 'C' in self.game.gameData['optionJumpers']:
			colonIndicator = '*'
		else:
			colonIndicator = ' '

		self.decodePacket = self._string_eater(self.decodePacket, places=len(colonIndicator))
		string += colonIndicator
		return string

	def _team_score_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				segHun = 0
			else:
				segHun = int(packet[0])
			if packet[1] == ' ':
				segTen = 0
			else:
				segTen = int(packet[1])
			if packet[2] == ' ':
				segUnit = 0
			else:
				segUnit = int(packet[2])
			self.game.set_team_data(team, 'scoreHundreds', segHun, 1)
			self.game.set_team_data(team, 'scoreTens', segTen, 1)
			self.game.set_team_data(team, 'scoreUnits', segUnit, 1)

		scoreHundred = self._get_value('scoreHundreds', min_value_not_blanked=1, team=team)
		scoreTen = self._get_value('scoreTens', min_value_not_blanked=scoreHundred == ' ', team=team)
		scoreUnit = self._get_value('scoreUnits', min_value_not_blanked=0, team=team)
		teamScore = '%s%s%s' % (scoreHundred, scoreTen, scoreUnit)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(teamScore))
		string += teamScore
		return string

	def _team_stat_string(self, string, team, packet=None):
		count = 0
		for number in self.game.statNumberList:
			if number is not None:
				if packet is not None:
					if packet[count*6] == ' ':
						playerTen = 25
					else:
						playerTen = int(packet[count*6])
					if packet[count*6+1] == ' ':
						playerUnit = 25
					else:
						playerUnit = int(packet[count*6+1])
					self.game.set_team_data(team, 'player' + number + 'Tens', playerTen, 1)
					self.game.set_team_data(team, 'player' + number + 'Units', playerUnit, 1)
					if packet[count*6+2] == ' ':
						foulTen = 25
					else:
						foulTen = int(packet[count*6+2])
					if packet[count*6+3] == ' ':
						foulUnit = 25
					else:
						foulUnit = int(packet[count*6+3])
					self.game.set_team_data(team, 'foul' + number + 'Tens', foulTen, 1)
					self.game.set_team_data(team, 'foul' + number + 'Units', foulUnit, 1)
					if packet[count*6+4] == ' ':
						pointsTen = 25
					else:
						pointsTen = int(packet[count*6+4])
					if packet[count*6+5] == ' ':
						pointsUnit = 25
					else:
						pointsUnit = int(packet[count*6+5])
					self.game.set_team_data(team, 'points' + number + 'Tens', pointsTen, 1)
					self.game.set_team_data(team, 'points' + number + 'Units', pointsUnit, 1)
					count += 1

				playerTen = self._get_value(
					'player'+number+'Tens', min_value_not_blanked=self.game.get_team_data(
						team, 'player' + number + 'Tens') > 9, team=team)
				playerUnit = self._get_value(
					'player'+number+'Units', min_value_not_blanked=self.game.get_team_data(
						team, 'player' + number + 'Units') > 9, team=team)
				playerString = '%s%s' % (playerTen, playerUnit)
				string += playerString

				foulTen = self._get_value(
					'foul'+number+'Tens', min_value_not_blanked=self.game.get_team_data(
						team, 'foul' + number + 'Tens') > 9, team=team)
				foulUnit = self._get_value(
					'foul'+number+'Units', min_value_not_blanked=self.game.get_team_data(
						team, 'foul' + number + 'Units') > 9, team=team)
				foulString = '%s%s' % (foulTen, foulUnit)
				string += foulString

				pointsTen = self._get_value(
					'points'+number+'Tens', min_value_not_blanked=self.game.get_team_data(
						team, 'points' + number + 'Tens') > 9, team=team)
				pointsUnit = self._get_value(
					'points'+number+'Units', min_value_not_blanked=self.game.get_team_data(
						team, 'points' + number + 'Units') > 9, team=team)
				pointsString = '%s%s' % (pointsTen, pointsUnit)
				string += pointsString
				self.decodePacket = self._string_eater(
					self.decodePacket, places=(len(playerString)+len(foulString)+len(pointsString)))
		return string

	def _team_e_t_n_string(self, string, team, packet=None):
		if packet is not None:
			name = packet[0:20]
			name = name.rstrip()
					
			if packet[20] == ' ':
				font = 0
			else:
				font = int(packet[20])
			if packet[21] == ' ':
				justify = 0
			else:
				justify = int(packet[21])
			storedName = self.game.get_team_data(team, 'name')
			nameCheck = storedName != name
			fontCheck = self.game.get_team_data(team, 'font') != font
			justifyCheck = self.game.get_team_data(team, 'justify') != justify
			
			if nameCheck or fontCheck or justifyCheck:
				if self.printETNData:
					print 'name', name, 'font', font, 'justify', justify
					print 'team', team, 'nameCheck', nameCheck, 'fontCheck', fontCheck, 'justifyCheck', justifyCheck
				self.ETNChangeFlag = True
				if team == 'TEAM_1':
					if nameCheck:
						self.guestNameChangeFlag = True
						lenCheck = len(storedName)-len(name)
						if storedName and abs(lenCheck) == 1 and 0:
							self.guestNameChangeOneCharFlag = True
							if self.printETNData:
								print 'single guest passed'
					if fontCheck or justifyCheck:
						self.guestFontJustifyChangeFlag = True
				elif team == 'TEAM_2':
					if nameCheck:
						self.homeNameChangeFlag = True
						lenCheck = len(storedName)-len(name)
						if self.printETNData:
							print 'len(storedName)', len(storedName), 'len(name)', len(name), 'abs(lenCheck)', abs(lenCheck)
						if storedName and abs(lenCheck) == 1 and 0:
							self.homeNameChangeOneCharFlag = True
							if self.printETNData:
								print 'single home passed'
					if fontCheck or justifyCheck:
						self.homeFontJustifyChangeFlag = True
								
			self.game.set_team_data(team, 'name', name, 1)
			self.game.set_team_data(team, 'font', font, 1)
			self.game.set_team_data(team, 'justify', justify, 1)

		name = self.game.get_team_data(team, 'name')
		if len(name) > 20:
			name = name[:20]
		string += name

		paddedString = ''
		padding = 20-len(name)
		for x in range(padding):
			paddedString += ' '
		
		self.decodePacket = self._string_eater(self.decodePacket, places=20)
		string += paddedString

		font = self.game.get_team_data(team, 'font')
		justify = self.game.get_team_data(team, 'justify')
		fontJustify = '%s%s' % (font, justify)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(fontJustify))
		string += fontJustify
		return string

	def _team_time_outs_left_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				TOL = 0
			else:
				TOL = int(packet[0])
			self.game.set_team_data(team, 'timeOutsLeft', TOL, 1)
			
		teamTimeout = '%s' % (self._get_value('timeOutsLeft', min_value_not_blanked=0, team=team))
		self.decodePacket = self._string_eater(self.decodePacket, places=len(teamTimeout))
		string += teamTimeout
		return string

	def _team_h_epitch_count_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ' or packet[0] == '0':
				hitsHundreds = 0
			else:
				hitsHundreds = 1
			if packet[1] == ' ':
				hitsTens = 0
			else:
				hitsTens = int(packet[1])
			if packet[2] == ' ':
				hitsUnits = 0
			else:
				hitsUnits = int(packet[2])
			if packet[3] == ' ':
				errorsTens = 0
			else:
				errorsTens = int(packet[3])
			if packet[4] == ' ':
				errorsUnits = 0
			else:
				errorsUnits = int(packet[4])
			if packet[5] == ' ' or packet[5] == '0':
				pitchCountHundreds = 0
			else:
				pitchCountHundreds = 1
			if packet[6] == ' ':
				pitchCountTens = 0
			else:
				pitchCountTens = int(packet[6])
			if packet[7] == ' ':
				pitchCountUnits = 0
			else:
				pitchCountUnits = int(packet[7])
				
			# Save double pitch count from single pitch count
			# LINE5andDjumper= self.game.gameData['sport'] == 'MPLINESCORE5' and ('D' in self.game.gameData['optionJumpers'])
			self.game.set_team_data(team, 'pitchCountHundreds', pitchCountHundreds, 1)
			self.game.set_team_data(team, 'pitchCountTens', pitchCountTens, 1)
			self.game.set_team_data(team, 'pitchCountUnits', pitchCountUnits, 1)			
			if self.game.get_team_data(self.game.home, 'atBatIndicator') and team == self.game.guest:
				self.game.set_game_data('singlePitchCountHundreds', pitchCountHundreds, 1)
				self.game.set_game_data('singlePitchCountTens', pitchCountTens, 1)
				self.game.set_game_data('singlePitchCountUnits', pitchCountUnits, 1)	
			elif not self.game.get_team_data(self.game.home, 'atBatIndicator') and team == self.game.home:
				self.game.set_game_data('singlePitchCountHundreds', pitchCountHundreds, 1)
				self.game.set_game_data('singlePitchCountTens', pitchCountTens, 1)
				self.game.set_game_data('singlePitchCountUnits', pitchCountUnits, 1)	

			self.game.set_team_data(team, 'hitsHundreds', hitsHundreds, 1)
			self.game.set_team_data(team, 'hitsTens', hitsTens, 1)
			self.game.set_team_data(team, 'hitsUnits', hitsUnits, 1)
			self.game.set_team_data(team, 'errorsTens', errorsTens, 1)
			self.game.set_team_data(team, 'errorsUnits', errorsUnits, 1)

		hitsHundred = self._get_value('hitsHundreds', min_value_not_blanked=1, team=team)
		hitsTen = self._get_value('hitsTens', min_value_not_blanked=hitsHundred == ' ', team=team)
		hitsUnit = self._get_value('hitsUnits', min_value_not_blanked=0, team=team)
		teamHits = '%s%s%s' % (hitsHundred, hitsTen, hitsUnit)
		string += teamHits

		errorsTen = self._get_value('errorsTens', min_value_not_blanked=1, team=team)
		errorsUnit = self._get_value('errorsUnits', min_value_not_blanked=0, team=team)
		errorsString = '%s%s' % (errorsTen, errorsUnit)
		string += errorsString
		
		# Save double pitch count from single pitch count
		if self.game.gameData['sport'] == 'MPLINESCORE5' and not ('D' in self.game.gameData['optionJumpers']):
			if self.game.get_team_data(self.game.home, 'atBatIndicator'):
				# In Bottom
				self.game.set_team_data(self.game.guest, 'pitchCountHundreds', self.game.get_game_data('singlePitchCountHundreds'), 1)
				self.game.set_team_data(self.game.guest, 'pitchCountTens', self.game.get_game_data('singlePitchCountTens'), 1)
				self.game.set_team_data(self.game.guest, 'pitchCountUnits', self.game.get_game_data('singlePitchCountUnits'), 1)	
	
			else:
				self.game.set_team_data(self.game.home, 'pitchCountHundreds', self.game.get_game_data('singlePitchCountHundreds'), 1)
				self.game.set_team_data(self.game.home, 'pitchCountTens', self.game.get_game_data('singlePitchCountTens'), 1)
				self.game.set_team_data(self.game.home, 'pitchCountUnits', self.game.get_game_data('singlePitchCountUnits'), 1)	

		pitchCountHundred = self._get_value('pitchCountHundreds', min_value_not_blanked=1, team=team)
		pitchCountTen = self._get_value('pitchCountTens', min_value_not_blanked=pitchCountHundred == ' ', team=team)
		pitchCountUnit = self._get_value('pitchCountUnits', min_value_not_blanked=0, team=team)
		teamPitchCount = '%s%s%s' % (pitchCountHundred, pitchCountTen, pitchCountUnit)
		string += teamPitchCount
		self.decodePacket = self._string_eater(
			self.decodePacket, places=(len(teamHits) + len(errorsString) + len(teamPitchCount)))
		return string

	def _team_shots_saves_kicks_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				shotsTens = 0
			else:
				shotsTens = int(packet[0])
			if packet[1] == ' ':
				shotsUnits = 0
			else:
				shotsUnits = int(packet[1])
			self.game.set_team_data(team, 'shotsTens', shotsTens, 1)
			self.game.set_team_data(team, 'shotsUnits', shotsUnits, 1)

		shotsTen = self._get_value('shotsTens', min_value_not_blanked=1, team=team)
		shotsUnit = self._get_value('shotsUnits', min_value_not_blanked=0, team=team)
		shotsString = '%s%s' % (shotsTen, shotsUnit)
		string += shotsString

		if self.game.gameData['sportType'] == 'soccer':
			if packet is not None:
				if packet[2] == ' ':
					savesTens = 0
				else:
					savesTens = int(packet[2])
				if packet[3] == ' ':
					savesUnits = 0
				else:
					savesUnits = int(packet[3])
				self.game.set_team_data(team, 'savesTens', savesTens, 1)
				self.game.set_team_data(team, 'savesUnits', savesUnits, 1)
				if packet[4] == ' ':
					kicksTens = 0
				else:
					kicksTens = int(packet[4])
				if packet[5] == ' ':
					kicksUnits = 0
				else:
					kicksUnits = int(packet[5])
				self.game.set_team_data(team, 'kicksTens', kicksTens, 1)
				self.game.set_team_data(team, 'kicksUnits', kicksUnits, 1)

			savesTen = self._get_value('savesTens', min_value_not_blanked=1, team=team)
			savesUnit = self._get_value('savesUnits', min_value_not_blanked=0, team=team)
			savesString = '%s%s' % (savesTen, savesUnit)
			string += savesString

			kicksTen = self._get_value('kicksTens', min_value_not_blanked=1, team=team)
			kicksUnit = self._get_value('kicksUnits', min_value_not_blanked=0, team=team)
			kicksString = '%s%s' % (kicksTen, kicksUnit)
			string += kicksString
			self.decodePacket = self._string_eater(
				self.decodePacket, places=(len(shotsString) + len(savesString) + len(kicksString)))
		else:
			self.decodePacket = self._string_eater(self.decodePacket, places=len(shotsString))
		return string

	def _team_possession_string(self, string, team, packet=None):
		if self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
			name = 'atBatIndicator'
			symbol = 'B'
		else:
			name = 'possession'
			symbol = 'P'
		if packet is not None:
			if packet[0] == ' ':
				teamPossession = 0
			else:
				teamPossession = 1
			self.game.set_team_data(team, name, teamPossession, 1)

		if self.game.get_team_data(team, name):
			teamPossession = symbol
		else:
			teamPossession = ' '

		self.decodePacket = self._string_eater(self.decodePacket, places=len(teamPossession))
		string += teamPossession
		return string

	def _team_penalty_indicator_count_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				penaltyIndicator = 0
			else:
				penaltyIndicator = 1
			if packet[1] == ' ':
				penaltyCount = 0
			else:
				penaltyCount = int(packet[1])
			self.game.set_team_data(team, 'penaltyIndicator', penaltyIndicator, 1)
			self.game.set_team_data(team, 'penaltyCount', penaltyCount, 1)

		if self.game.get_team_data(team, 'penaltyIndicator'):
			penI = 'P'
		else:
			penI = ' '
		penaltyCount = self._get_value('penaltyCount', min_value_not_blanked=0, team=team)
		penalty = '%s%s' % (penI, penaltyCount)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(penalty))
		string += penalty
		return string

	def _team_bonus_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				bonus = 0
			else:
				bonus = int(packet[0])
			self.game.set_team_data(team, 'bonus', bonus, 1)

		if self.game.get_team_data(team, 'bonus') == 1:
			teamBonus = '1'
		elif self.game.get_team_data(team, 'bonus') == 2:
			teamBonus = '2'
		else:
			teamBonus = ' '
		string += teamBonus
		self.decodePacket = self._string_eater(self.decodePacket, places=len(teamBonus))
		return string

	def _team_inning_score_string(self, string, team, packet=None):
		for inning in range(15):
			if packet is not None:
				if packet[inning] == ' ':
					scoreInning = 255
				else:
					scoreInning = int(packet[inning])
				self.game.set_team_data(team, 'scoreInn' + str(inning + 1), scoreInning, 1)
			scoreInn = self._get_value(
				'scoreInn'+str(inning+1), min_value_not_blanked=self.game.get_team_data(
					team, 'scoreInn' + str(inning + 1)) > 9, team=team)
			string += str(scoreInn)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(range(15)))
		return string

	def _team_penalty_player_number_clock_string(self, string, team, packet=None):
		pen = 'penalty'
		if team[-1] == '1':
			teamName = 'teamOne'
		elif team[-1] == '2':
			teamName = 'teamTwo'
		for x, clockNumber in enumerate([1, 2]):
			clockName = pen+str(clockNumber)+'_'+teamName
			if packet is not None:
				if packet[0+x*6] == ' ':
					PLAYER_NUMBERTens = 255
				else:
					PLAYER_NUMBERTens = int(packet[0+x*6])
				if packet[1+x*6] == ' ':
					PLAYER_NUMBERUnits = 255
				else:
					PLAYER_NUMBERUnits = int(packet[1+x*6])
				if packet[2+x*6] == ' ':
					minutesUnits = 255
				else:
					minutesUnits = int(packet[2+x*6])

				if packet[4+x*6] == ' ':
					secondsTens = 255
				else:
					secondsTens = int(packet[4+x*6])
				if packet[5+x*6] == ' ':
					secondsUnits = 255
				else:
					secondsUnits = int(packet[5+x*6])
					
				if (
						(minutesUnits == 255 and secondsTens == 255 and secondsUnits == 255)
						or (minutesUnits == 0 and secondsTens == 0 and secondsUnits == 0)):
					colon = False
				else:
					colon = True
										
				self.game.set_team_data(team, 'TIMER' + str(clockNumber) + '_PLAYER_NUMBERTens', PLAYER_NUMBERTens, 1)
				self.game.set_team_data(team, 'TIMER' + str(clockNumber) + '_PLAYER_NUMBERUnits', PLAYER_NUMBERUnits, 1)
				self.game.clockDict[clockName].timeUnitsDict['minutesUnits'] = minutesUnits
				self.game.set_team_data(team, 'TIMER' + str(clockNumber) + '_COLON_INDICATOR', colon, 1)
				self.game.clockDict[clockName].timeUnitsDict['secondsTens'] = secondsTens
				self.game.clockDict[clockName].timeUnitsDict['secondsUnits'] = secondsUnits

			timerPlayerNumberTens = self._get_value(
				'TIMER'+str(clockNumber)+'_PLAYER_NUMBERTens',
				min_value_not_blanked=self.game.get_team_data(
					team, 'TIMER' + str(clockNumber) + '_PLAYER_NUMBERTens') > 9, team=team)
			timerPlayerNumberUnits = self._get_value(
				'TIMER'+str(clockNumber)+'_PLAYER_NUMBERUnits',
				min_value_not_blanked=self.game.get_team_data(
					team, 'TIMER' + str(clockNumber) + '_PLAYER_NUMBERUnits') > 9, team=team)
			timerPlayerNumber = '%s%s' % (timerPlayerNumberTens, timerPlayerNumberUnits)
			string += timerPlayerNumber

			# Minutes behavior

			minutesUnitsByte = self._get_value(clockName + '_' + 'minutesUnits', min_value_not_blanked=0)

			# Seconds behavior
			secondsTensByte = self._get_value(clockName + '_' + 'secondsTens', min_value_not_blanked=0)
			secondsUnitsByte = self._get_value(clockName + '_' + 'secondsUnits', min_value_not_blanked=0)
			if minutesUnitsByte == ' ' or secondsTensByte == ' ' or secondsUnitsByte == ' ':
				colonByte = ' '
			else:
				colonByte = ':'
			# Format as a string
			penaltyClock = (minutesUnitsByte, colonByte, secondsTensByte, secondsUnitsByte)
			clockS = '%s%s%s%s' % penaltyClock
			string += clockS
			self.decodePacket = self._string_eater(self.decodePacket, places=len(timerPlayerNumber) + len(clockS))

		return string

	def _team_goal_indicator_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				goalIndicator = 0
			else:
				goalIndicator = 1
			self.game.set_team_data(team, 'goalIndicator', goalIndicator, 1)

		if self.game.get_team_data(team, 'goalIndicator'):
			goalI = 'G'
		else:
			goalI = ' '
		string += goalI
		self.decodePacket = self._string_eater(self.decodePacket, places=len(goalI))
		return string

	def _team_fouls_player_number_fouls_string(self, string, team, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				foulsTens = 0
			else:
				foulsTens = int(packet[0])
			if packet[1] == ' ':
				foulsUnits = 0
			else:
				foulsUnits = int(packet[1])
			self.game.set_team_data(team, 'foulsTens', foulsTens, 1)
			self.game.set_team_data(team, 'foulsUnits', foulsUnits, 1)

		foulsTen = self._get_value('foulsTens', min_value_not_blanked=1, team=team)
		foulsUnit = self._get_value('foulsUnits', min_value_not_blanked=0, team=team)
		teamFoul = '%s%s' % (foulsTen, foulsUnit)
		string += teamFoul

		teamPlayerFoul = '    '
		string += teamPlayerFoul
		self.decodePacket = self._string_eater(self.decodePacket, places=(len(teamFoul) + len(teamPlayerFoul)))
		return string

	def _period_inning_string(self, string, packet=None):
		# Period byte
		if self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
			if packet is not None:
				if packet[0] == ' ':
					inningTens = 0
				else:
					inningTens = int(packet[0])
				if packet[1] == ' ':
					inningUnits = 0
				else:
					inningUnits = int(packet[1])
				self.game.set_game_data('inningTens', inningTens, 1)
				self.game.set_game_data('inningUnits', inningUnits, 1)
			inningTens = self._get_value('inningTens', min_value_not_blanked=1)
			inningUnits = self._get_value('inningUnits', min_value_not_blanked=0)
			periodByte = '%s%s' % (inningTens, inningUnits)
		elif self.game.gameData['sportType'] == 'football':
			if packet is not None:
				if packet[0] == ' ':
					quarter = 0
				else:
					quarter = int(packet[0])
				self.game.set_game_data('quarter', quarter, 1)
			quarter = self._get_value('quarter', min_value_not_blanked=0)
			periodByte = '%s' % quarter
		else:
			if packet is not None:
				if packet[0] == ' ':
					period = 0
				else:
					period = int(packet[0])
				self.game.set_game_data('period', period, 1)
			period = self._get_value('period', min_value_not_blanked=0)
			periodByte = '%s' % period
		self.decodePacket = self._string_eater(self.decodePacket, places=len(periodByte))
		string += periodByte
		return string

	def _extra_football_string(self, string, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				down = 0
			else:
				down = int(packet[0])
			if packet[1] == ' ':
				ballOnTens = 0
			else:
				ballOnTens = int(packet[1])
			if packet[2] == ' ':
				ballOnUnits = 0
			else:
				ballOnUnits = int(packet[2])
			if packet[3] == ' ':
				yardsToGoTens = 0
			else:
				yardsToGoTens = int(packet[3])
			if packet[4] == ' ':
				yardsToGoUnits = 0
			else:
				yardsToGoUnits = int(packet[4])
			self.game.set_game_data('down', down, 1)
			self.game.set_game_data('ballOnTens', ballOnTens, 1)
			self.game.set_game_data('ballOnUnits', ballOnUnits, 1)
			self.game.set_game_data('yardsToGoTens', yardsToGoTens, 1)
			self.game.set_game_data('yardsToGoUnits', yardsToGoUnits, 1)

		downUnit = self._get_value('down', min_value_not_blanked=0)
		ballOnTen = self._get_value('ballOnTens', min_value_not_blanked=1)
		ballOnUnit = self._get_value('ballOnUnits', min_value_not_blanked=0)
		yardsToGoTen = self._get_value('yardsToGoTens', min_value_not_blanked=1)
		yardsToGoUnit = self._get_value('yardsToGoUnits', min_value_not_blanked=0)
		teamFoul = '%s%s%s%s%s' % (downUnit, ballOnTen, ballOnUnit, yardsToGoTen, yardsToGoUnit)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(teamFoul))
		string += teamFoul
		return string

	def _player_number_fouls_string(self, string, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				playerNumberTens = 255
			else:
				playerNumberTens = int(packet[0])
			if packet[1] == ' ':
				playerNumberUnits = 255
			else:
				playerNumberUnits = int(packet[1])
			if packet[2] == ' ':
				playerFoulsTens = 255
			else:
				playerFoulsTens = int(packet[2])
			if packet[3] == ' ':
				playerFoulsUnits = 255
			else:
				playerFoulsUnits = int(packet[3])
			self.game.set_game_data('playerNumberTens', playerNumberTens, 1)
			self.game.set_game_data('playerNumberUnits', playerNumberUnits, 1)
			self.game.set_game_data('playerFoulsTens', playerFoulsTens, 1)
			self.game.set_game_data('playerFoulsUnits', playerFoulsUnits, 1)

		playerNumberTen = self._get_value(
			'playerNumberTens', min_value_not_blanked=self.game.get_game_data('playerNumberTens') > 9)
		playerNumberUnit = self._get_value(
			'playerNumberUnits', min_value_not_blanked=self.game.get_game_data('playerNumberUnits') > 9)
		playerFoulsTen = self._get_value('playerFoulsTens', min_value_not_blanked=1)
		playerFoulsUnit = self._get_value('playerFoulsUnits', min_value_not_blanked=0)
		player = '%s%s%s%s' % (playerNumberTen, playerNumberUnit, playerFoulsTen, playerFoulsUnit)
		self.decodePacket = self._string_eater(self.decodePacket, places=len(player))
		string += player
		return string

	def _extra_baseball_string(self, string, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				inningBot = 0
			else:
				inningBot = 1
			if packet[1] == ' ':
				balls = 0
			else:
				balls = int(packet[1])
			if packet[2] == ' ':
				strikes = 0
			else:
				strikes = int(packet[2])
			if packet[3] == ' ':
				outs = 0
			else:
				outs = int(packet[3])
			if packet[4] == ' ':
				hitIndicator = 0
			else:
				hitIndicator = 1
			if packet[5] == ' ':
				errorIndicator = 0
			else:
				errorIndicator = 1
			if packet[6] == ' ':
				errorPosition = 255
			else:
				errorPosition = int(packet[6])
			self.game.set_game_data('inningBot', inningBot, 1)
			self.game.set_game_data('balls', balls, 1)
			self.game.set_game_data('strikes', strikes, 1)
			self.game.set_game_data('outs', outs, 1)
			self.game.set_game_data('hitIndicator', hitIndicator, 1)
			self.game.set_game_data('errorIndicator', errorIndicator, 1)
			self.game.set_game_data('errorPosition', errorPosition, 1)

		if self.game.get_team_data(self.game.guest, 'atBatIndicator'):
			innBot = 'T'
		else:
			innBot = 'B'
		balls = self._get_value('balls', min_value_not_blanked=1)
		strikes = self._get_value('strikes', min_value_not_blanked=1)
		outs = self._get_value('outs', min_value_not_blanked=1)
		if self.game.gameData['hitIndicator']:
			hit = 'H'
		else:
			hit = ' '
		if self.game.gameData['errorIndicator']:
			error = 'E'
		else:
			error = ' '
		errorPosition = self._get_value('errorPosition', min_value_not_blanked=1)
		stuff = '%s%s%s%s%s%s%s' % (innBot, balls, strikes, outs, hit, error, errorPosition)
		string += stuff
		
		# -----
		if packet is not None:
			if packet[7] == ' ':
				pitchSpeedHundreds = 0
			else:
				pitchSpeedHundreds = int(packet[7])
			if packet[8] == ' ':
				pitchSpeedTens = 0
			else:
				pitchSpeedTens = int(packet[8])
			if packet[9] == ' ':
				pitchSpeedUnits = 0
			else:
				pitchSpeedUnits = int(packet[9])
			self.game.set_game_data('pitchSpeedHundreds', pitchSpeedHundreds, 1)
			self.game.set_game_data('pitchSpeedTens', pitchSpeedTens, 1)
			self.game.set_game_data('pitchSpeedUnits', pitchSpeedUnits, 1)

		pitchSpeedHundred = self._get_value('pitchSpeedHundreds', min_value_not_blanked=1)
		pitchSpeedTen = self._get_value('pitchSpeedTens', min_value_not_blanked=pitchSpeedHundred == ' ')
		pitchSpeedUnit = self._get_value('pitchSpeedUnits', min_value_not_blanked=0)
		pitchSpeed = '%s%s%s' % (pitchSpeedHundred, pitchSpeedTen, pitchSpeedUnit)
		string += pitchSpeed
		
		# -----10
		pitchSpeedUnitOfMeasure = ' '
		string += pitchSpeedUnitOfMeasure
		
		# -----
		if packet is not None:
			if packet[11] == ' ':
				batterNumberTens = 0
			else:
				batterNumberTens = int(packet[11])
			if packet[12] == ' ':
				batterNumberUnits = 0
			else:
				batterNumberUnits = int(packet[12])
			self.game.set_game_data('batterNumberTens', batterNumberTens, 1)
			self.game.set_game_data('batterNumberUnits', batterNumberUnits, 1)
			
		batterNumberTen = self._get_value('batterNumberTens', min_value_not_blanked=1)
		batterNumberUnit = self._get_value('batterNumberUnits', min_value_not_blanked=0)
		batterNumber = '%s%s' % (batterNumberTen, batterNumberUnit)
		string += batterNumber
		
		battingAverage = '      '  # 6 bytes Player Batting Average N.NNNN
		string += battingAverage

		runnerOnFirst = '  '  # 2 bytes Runner on First NN
		string += runnerOnFirst

		runnerOnSecond = '  '  # 2 bytes Runner on Second NN
		string += runnerOnSecond
		
		runnerOnThird = '  '  # 2 bytes Runner on Third NN
		string += runnerOnThird
		
		self.decodePacket = self._string_eater(
			self.decodePacket, places=(
					len(stuff) + len(pitchSpeed) + len(pitchSpeedUnitOfMeasure) + len(batterNumber) + len(battingAverage)
					+ len(runnerOnFirst) + len(runnerOnSecond) + len(runnerOnThird))
		)
		return string

	def _horn_one_two_string(self, string, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				periodHorn = 0
			else:
				periodHorn = 1

			self.game.set_game_data('periodHorn', periodHorn, 1)
			
			if self.game.gameSettings['visualHornEnable']:
				self.game.gameData['visualHornIndicator1'] = periodHorn
				if self.game.gameData['sportType'] == 'basketball' or self.game.gameData['sportType'] == 'hockey':
					self.game.gameData['visualHornIndicator2'] = periodHorn
		if self.game.gameData['periodHorn']:
			horn1 = 'H'
		else:
			horn1 = ' '
		string += horn1
		if self.game.gameData['sportType'] == 'football' or self.game.gameData['sportType'] == 'soccer':
			if packet is not None:
				if packet[1] == ' ':
					delayOfGameHorn = 0
				else:
					delayOfGameHorn = 1
				self.game.set_game_data('delayOfGameHorn', delayOfGameHorn, 1)
			if self.game.gameData['delayOfGameHorn']:
				horn2 = 'H'
			else:
				horn2 = ' '

		else:
			horn2 = ' '
		string += horn2
		self.decodePacket = self._string_eater(self.decodePacket, places=len(horn1) + len(horn2))
		return string

	def _shot_horn_string(self, string, packet=None):
		if packet is not None:
			if packet[0] == ' ':
				shotClockHorn = 0
			else:
				shotClockHorn = 1
			self.game.set_game_data('shotClockHorn', shotClockHorn, 1)

		if self.game.gameData['shotClockHorn']:
			shotHorn = 'H'
		else:
			shotHorn = ' '
		string += shotHorn
		if self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
			breakTimeOut = ' '
		else:
			breakTimeOut = ''
		string += breakTimeOut
		self.decodePacket = self._string_eater(self.decodePacket, places=len(shotHorn) + len(breakTimeOut))
		return string

	def _reserved_string(self, string='', packet=None):
		if self.ETNFlag or self.game.gameData['sportType'] == 'soccer':
			reserved = '           '  # 11
		elif self.game.gameData['sportType'] == 'baseball' or self.game.gameData['sportType'] == 'linescore':
			reserved = '                        '  # 24
		elif self.game.gameData['sportType'] == 'football':
			reserved = '            '  # 12
		elif self.game.gameData['sportType'] == 'basketball' or self.game.gameData['sportType'] == 'hockey':
			reserved = '                '  # 16
		elif self.game.gameData['sportType'] == 'stat':
			reserved = '             '  # 13
		string += reserved
		self.decodePacket = self._string_eater(self.decodePacket, places=len(reserved))
		return string

	def _checksum_byte(self, string, packet=None):
		# Check sum byte
		CS = 0
		if packet is not None:
			string = packet[0:-2]

		for y in range(len(string)):
			if y != 0:
				CS += ord(string[y])
		if (CS % 0x100) < 0x32:
			checkSum = chr(CS % 0x100+0x32)
		else:
			checkSum = chr(CS % 0x100)

		if packet is not None:
			try:
				if checkSum != packet[-2]:
					# Error
					if self.printCorruption:
						print 'ord(checkSum), packet[-2]', ord(checkSum), ord(packet[-2])
						print 'packet', packet
					return 1
				else:
					return 0
			except:
				print 'checkSum try failed', packet
				return 1
		else:
			string += checkSum
			return string
