#!/usr/bin/python
# # -*- coding: utf-8 -*-

"""

.. topic:: Overview

    This module handles encoding game data in to the packet format.

    :Created Date: 3/16/2015
    :Author: **Craig Gunter**

"""


class Serial_Packet (object):
	'''Creates serial packet object.'''

	def __init__(self, game):
		self.game = game

		self.MPserial = False
		self.ETNFlag = False

	@staticmethod
	def stringEater(packet, places=1):
		if packet is not None:
			packet = packet[places:]
		return packet

	def encodePacket(self, printString=False, ETNFlag=False, packet=None):
		"""Encodes packet for serial transmission."""
		string = ''
		self.ETNFlag = ETNFlag
		originalPacket = packet
		self.decodePacket=packet
		
		self.ETNChangeFlag=False
		self.guestNameChangeFlag=False
		self.guestNameChangeOneCharFlag=False
		self.guestFontJustifyChangeFlag=False
		self.homeNameChangeFlag=False
		self.homeNameChangeOneCharFlag=False
		self.homeFontJustifyChangeFlag=False
		self.printCorruption=False
		self.printETNData=False
		#start byte, 1B
		string+=chr(0x01)
		
		if packet is not None:
			#print 'packet\n', packet
			
			if packet:
				check=self.checksumByte(string, packet=self.decodePacket)
				packStart=self.decodePacket[0]!=chr(0x01)
				packEnd=self.decodePacket[-1]!=chr(0x04)
				if self.printCorruption and (packStart or packEnd or check):
					print 'Packet Corruption'
					print 'packet[0]', self.decodePacket[0], 'chr(0x01)', chr(0x01), 'packet[0]!=chr(0x01)', packStart
					print 'packet[-1]', self.decodePacket[-1], 'chr(0x04)', chr(0x04), 'packet[-1]!=chr(0x04)', packEnd
					print 'self.checksumByte() returns', check
					return self.game, 0
			lengthCheck=self.versionIDByte(string, packet=packet, lengthCheck=1)
			if lengthCheck is None:
				return self.game, 0
			#print '\nPacket checked good'
			
			#Remove start byte
			self.decodePacket=self.stringEater(self.decodePacket)

		string=self.versionIDByte(string, packet=self.decodePacket)

		if not (self.game.gameData['sportType']=='stat' or self.ETNFlag):
			string=self.periodClockString(string, packet=self.decodePacket)

			if self.game.gameData['sportType']=='football' or self.game.gameData['sportType']=='soccer':
				playClockFlag=True
			else:
				playClockFlag=False
			string=self.play_shotClockString(string, playClockFlag=playClockFlag, packet=self.decodePacket)

			string=self.timeOutClockString(string, packet=self.decodePacket)

			string=self.timeOfDayClockString(string, packet=self.decodePacket)

			string=self.practiceClockString(string, packet=self.decodePacket)

			string=self.segmentCountString(string, packet=self.decodePacket)

			if self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
				string=self.timerActivityIndicatorString(string, packet=self.decodePacket)

		for team in [self.game.guest, self.game.home]:
			if self.ETNFlag:
				string=self.teamETNString(string, team, packet=self.decodePacket)
			elif self.game.gameData['sportType']=='stat':
				string=self.teamStatString(string, team, packet=self.decodePacket)
			else:
				string=self.teamScoreString(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
					string=self.teamHEpitchCountString(string, team, packet=self.decodePacket)
					#print string, '\nlength', len(string)
				elif self.game.gameData['sportType']=='football' or self.game.gameData['sportType']=='basketball':
					string=self.teamTimeOutsLeftString(string, team, packet=self.decodePacket)
				elif self.game.gameData['sportType']=='soccer' or self.game.gameData['sportType']=='hockey':
					string=self.teamShotsSavesKicksString(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType']=='soccer' or self.game.gameData['sportType']=='hockey':
					string=self.teamGoalIndicatorString(string, team, packet=self.decodePacket)

				if not (self.game.gameData['sportType']=='stat' or self.game.gameData['sportType']=='hockey' or self.ETNFlag):
					string=self.teamPossessionString(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType']=='soccer' or self.game.gameData['sportType']=='hockey':
					string=self.teamPenaltyIndicatorCountString(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType']=='basketball':
					string=self.teamBonusString(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
					string=self.teamInningScoreString(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType']=='hockey':
					string=self.teamPenaltyPlayerNumberClockString(string, team, packet=self.decodePacket)

				if self.game.gameData['sportType']=='basketball':
					string=self.teamGoalIndicatorString(string, team, packet=self.decodePacket)

					string=self.teamFoulsPlayerNumberFoulsString(string, team, packet=self.decodePacket)

		if not self.ETNFlag:
			if not self.game.gameData['sportType']=='stat':
				string=self.periodInningString(string, packet=self.decodePacket)

			if self.game.gameData['sportType']=='football':
				string=self.extraFootballString(string, packet=self.decodePacket)

			if self.game.gameData['sportType']=='basketball':
				string=self.playerNumberFoulsString(string, packet=self.decodePacket)

			if self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
				string=self.extraBaseballString(string, packet=self.decodePacket)

			if not self.game.gameData['sportType']=='stat':
				string=self.hornOneTwoString(string, packet=self.decodePacket)

			if self.game.gameData['sportType']=='baseball'  or self.game.gameData['sportType']=='linescore'or self.game.gameData['sportType']=='basketball' or self.game.gameData['sportType']=='hockey':
				string=self.shotHornString(string, packet=self.decodePacket)

		string=self.reservedString(string, packet=self.decodePacket)

		if packet is None:
			string=self.checksumByte(string, packet=self.decodePacket)

			#stop byte
			string+=chr(0x04)

			#print string for testing
			if printString:
				print string
				print 'length', len(string)

			return self.game, string
		else:
			
			#Clear flag if set by lengthCheck version of versionIDByte
			self.ETNFlag=False
			
			if printString:
				print self.decodePacket
				print 'length', len(self.decodePacket)
				#print packet
				#print 'length', len(packet)
			return self.game, packet

# ----------------------------------------------------------------------

	def getValue(self, valueName, minValueNotBlanked=1, team=None, clock=None):
		if team is None:
			#gameData, clockData is saved in gameData
			if self.game.gameData[valueName]>=minValueNotBlanked and self.game.gameData[valueName]<=9:
				value=self.game.gameData[valueName]
			else:
				value=' '
		else:
			#teamData
			if self.game.getTeamData(team, valueName)>=minValueNotBlanked and self.game.getTeamData(team, valueName)<=9:
				value=self.game.getTeamData(team, valueName)
			else:
				value=' '
		return value

	def versionIDByte(self, string, packet=None, lengthCheck=0):
		#Sport and version byte, 2
		if self.ETNFlag:
			sport='N'
			version='1'
			packetLength=60
		elif self.game.gameData['sportType']=='football':
			sport='F'
			version='1'
			packetLength=80
		elif self.game.gameData['sportType']=='basketball':
			sport='K'
			version='1'
			packetLength=100
		elif self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
			sport='B'
			version='1'
			packetLength=160
		elif self.game.gameData['sportType']=='soccer':
			sport='S'
			version='1'
			packetLength=90
		elif self.game.gameData['sportType']=='hockey':
			sport='H'
			version='1'
			packetLength=110
		elif self.game.gameData['sportType']=='stat':
			sport='P'
			version='1'
			packetLength=90
		partialString=sport+version			
		string+=partialString
		
		if lengthCheck:
			if len(packet)>1 and packet[1]=='N':
				self.ETNFlag=True
				packetLength=60
				
			if self.printCorruption and len(packet)!=packetLength and not self.MPserial:
				string=None
				print 'Packet Length Error'
				print 'len(packet), packetLength = ', len(packet), packetLength
				print 'self.decodePacket "', self.decodePacket, '"END\n'
				return string

		else:
			self.decodePacket=self.stringEater(self.decodePacket, places=len(partialString))
			
		return string

	def periodClockString(self, string, packet=None):
		#prepare all period clock bytes HH:MM:SS.xcm, 12
		clockName='periodClock'
		timeListNames=['daysTens', 'daysUnits', 'hoursTens', \
		'hoursUnits', 'minutesTens', 'minutesUnits', 'secondsTens', \
		'secondsUnits', 'tenthsUnits', 'hundredthsUnits']
		if packet is not None:
			if packet[0]==' ':
				hoursTensByte=0
			else:
				hoursTensByte=int(packet[0])
			if packet[1]==' ':
				hoursUnitsByte=0
			else:
				hoursUnitsByte=int(packet[1])
			self.game.setClockData(clockName, timeListNames[2], hoursTensByte, 1)
			self.game.setClockData(clockName, timeListNames[3], hoursUnitsByte, 1)
			if packet[2]==' ':
				hoursColonByte=0
			else:
				hoursColonByte=1
			#self.game.setGameData('hoursColonIndicator', hoursColonByte) Does not exist
			if packet[3]==' ':
				minutesTensByte=0
			else:
				minutesTensByte=int(packet[3])
			if packet[4]==' ':
				minutesUnitsByte=0
			else:
				minutesUnitsByte=int(packet[4])
			self.game.setClockData(clockName, timeListNames[4], minutesTensByte, 1)
			self.game.setClockData(clockName, timeListNames[5], minutesUnitsByte, 1)
			if packet[5]==' ':
				colonByte=0
				
				#self.game.gameData['colonIndicator']=False
				#self.game.gameData['decimalIndicator']=True
				periodClockTenthsFlag=True
			else:
				colonByte=1
				#self.game.gameData['colonIndicator']=True
				#self.game.gameData['decimalIndicator']=False
				periodClockTenthsFlag=False
			if self.game.gameSettings['trackClockEnable']:
				colonByte=1
			self.game.setGameData('colonIndicator', colonByte)
			#print self.game.gameData['colonIndicator']
			if packet[6]==' ':
				secondsTensByte=0
			else:
				secondsTensByte=int(packet[6])
			if packet[7]==' ':
				secondsUnitsByte=0
			else:
				secondsUnitsByte=int(packet[7])
			self.game.setClockData(clockName, timeListNames[6], secondsTensByte, 1)
			self.game.setClockData(clockName, timeListNames[7], secondsUnitsByte, 1)
			decimalByte=not colonByte
			if self.game.gameSettings['trackClockEnable']:
				if packet[8]==' ':
					decimalByte=0
					periodClockTenthsFlag=0
				else:
					decimalByte=1
					periodClockTenthsFlag=1
			self.game.gameSettings['periodClockTenthsFlag']=periodClockTenthsFlag
			self.game.setGameData('decimalIndicator', decimalByte)
			if packet[9]==' ':
				tenthsUnitsByte=0
			else:
				tenthsUnitsByte=int(packet[9])
			if packet[10]==' ':
				hundredthsUnitsByte=0
			else:
				hundredthsUnitsByte=int(packet[10])
			if packet[11]==' ':
				thousandthsUnitsByte=0
			else:
				thousandthsUnitsByte=int(packet[11])
			self.game.setClockData(clockName, timeListNames[8], tenthsUnitsByte, 1)
			self.game.setClockData(clockName, timeListNames[9], hundredthsUnitsByte, 1)
			#self.game.setClockData(clockName, thousandthsUnits', thousandthsUnitsByte, 1) Does not exist

		#make the clock variables
		colon=self.game.gameData['colonIndicator']

		#hours behavior
		hoursTensByte=self.getValue(clockName+'_'+'hoursTens', minValueNotBlanked=1)#blank if 0
		hoursUnitsByte=self.getValue(clockName+'_'+'hoursUnits', minValueNotBlanked=hoursTensByte==' ')#blank if zero if previous blank
		if hoursTensByte==' ' and hoursUnitsByte==' ':
			#blank if both are blank
			hoursColonByte=' '
		else:
			hoursColonByte=':'

		#minutes behavior
		minutesTensByte=self.getValue(clockName+'_'+'minutesTens', minValueNotBlanked=hoursColonByte==' ')#blank if zero if previous blank
		minutesUnitsByte=self.getValue(clockName+'_'+'minutesUnits', minValueNotBlanked=minutesTensByte==' ')#blank if zero if previous blank
		if minutesTensByte==' ' and minutesUnitsByte==' ':
			#blank if both are blank
			colonByte=' '
		else:
			colonByte=':'

		#seconds behavior
		secondsTensByte=self.getValue(clockName+'_'+'secondsTens', minValueNotBlanked=colonByte==' ')#blank if zero if previous blank
		secondsUnitsByte=self.getValue(clockName+'_'+'secondsUnits', minValueNotBlanked=0)
		
		#decimal behavior
		if self.game.gameData[clockName+'_'+'tenthsUnits']==15:
			decimalByte=' '
		else:
			decimalByte='.'

		#sub-second behavior
		if 1:#decimalByte=='.':
			tenthsUnitsByte=self.getValue(clockName+'_'+'tenthsUnits', minValueNotBlanked=0)
			hundredthsUnitsByte=' '#self.getValue(clockName+'_'+'hundredthsUnits', minValueNotBlanked=0)
		else:
			tenthsUnitsByte=' '
			hundredthsUnitsByte=' '
		
		LINE5andCjumper= self.game.gameData['sport']=='MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']
		MULTIbaseOr3450baseCjumper= (self.game.gameData['sport']=='MPMULTISPORT1-baseball' or self.game.gameData['sport']=='MPLX3450-baseball')\
		and 'C' in self.game.gameData['optionJumpers']
		BASE1orBASE3Cjumper= (self.game.gameData['sport']=='MPBASEBALL1' or self.game.gameData['sport']=='MMBASEBALL3')\
		and 'C' in self.game.gameData['optionJumpers']
		
		#Override if 2 digit clock baseball
		if LINE5andCjumper or MULTIbaseOr3450baseCjumper or BASE1orBASE3Cjumper:
			decimalByte=' '
			tenthsUnitsByte=' '
			hundredthsUnitsByte=' '			
			
		#thousandths not currently used
		thousandthsUnitsByte=' '

		#format as a string
		periodClock=(\
		hoursTensByte, hoursUnitsByte, hoursColonByte, \
		minutesTensByte, minutesUnitsByte, colonByte, \
		secondsTensByte, secondsUnitsByte, decimalByte, \
		tenthsUnitsByte, hundredthsUnitsByte, thousandthsUnitsByte)
		clockS=('%s%s%s%s%s%s%s%s%s%s%s%s') % periodClock

		#period clock byte(s) HH:MM:SS.xcm , 12
		self.decodePacket=self.stringEater(self.decodePacket, places=len(clockS))
		string+=clockS
		return string

	def play_shotClockString(self, string, playClockFlag=True, packet=None):
		#play_shot clock byte(s), SS.x, 4

		if playClockFlag:
			name='delayOfGameClock'
		else:
			name='shotClock'

		if packet is not None:
			if packet[0]==' ':
				play_shotTensByte=255
			else:
				play_shotTensByte=int(packet[0])
			if packet[1]==' ':
				play_shotUnitsByte=255
			else:
				play_shotUnitsByte=int(packet[1])
			self.game.setClockData(name, 'secondsTens', play_shotTensByte, 1)
			self.game.setClockData(name, 'secondsUnits', play_shotUnitsByte, 1)
			if packet[2]==' ':
				play_shotDecimalByte=0
			else:
				play_shotDecimalByte=1
			#self.game.setGameData('play_shotDecimalIndicator', play_shotDecimalByte) Does not exist
			if packet[3]==' ':
				play_shotTenthsByte=0
			else:
				play_shotTenthsByte=1
			#self.game.setClockData(name, '_tenthsUnits', play_shotTenthsByte) Does not exist

		play_shotTensByte=self.getValue(name+'_secondsTens', minValueNotBlanked=1)
		play_shotUnitsByte=self.getValue(name+'_secondsUnits', minValueNotBlanked=0)

		#decimal is not currently used
		play_shotDecimalFlag=False
		if play_shotDecimalFlag:
			play_shotDecimalByte='.'
		else:
			play_shotDecimalByte=' '

		#seconds units is not currently used
		if play_shotDecimalByte=='.':
			play_shotTenthsByte=self.getValue(name+'_tenthsUnits', minValueNotBlanked=0)
		else:
			play_shotTenthsByte=' '

		play_shotClock='%s%s%s%s' % (play_shotTensByte, play_shotUnitsByte, play_shotDecimalByte, play_shotTenthsByte)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(play_shotClock))
		string+=play_shotClock
		#print 'play_shotClock', play_shotClock, 'len(play_shotClock)', len(play_shotClock)
		return string

	def timeOutClockString(self, string, packet=None):
		#time out clock byte(s), MM:SS, 5
		clockName='timeOutTimer'

		if packet is not None:
			if packet[0]==' ':
				minutesTensByte=0
			else:
				minutesTensByte=int(packet[0])
			if packet[1]==' ':
				minutesUnitsByte=0
			else:
				minutesUnitsByte=int(packet[1])
			self.game.setGameData(clockName+'_'+'minutesTens', minutesTensByte, 1)
			self.game.setGameData(clockName+'_'+'minutesUnits', minutesUnitsByte, 1)
			if packet[2]==' ':
				colonByte=0
			else:
				colonByte=1
			#This colon breaks the main colon from period clock
			#self.game.setGameData('colonIndicator', colonByte)
			if packet[3]==' ':
				secondsTensByte=0
			else:
				secondsTensByte=int(packet[3])
			if packet[4]==' ':
				secondsUnitsByte=0
			else:
				secondsUnitsByte=int(packet[4])
			self.game.setGameData(clockName+'_'+'secondsTens', secondsTensByte, 1)
			self.game.setGameData(clockName+'_'+'secondsUnits', secondsUnitsByte, 1)

		#minutes behavior
		minutesTensByte=self.getValue(clockName+'_'+'minutesTens', minValueNotBlanked=1)
		minutesUnitsByte=self.getValue(clockName+'_'+'minutesUnits', minValueNotBlanked=minutesTensByte==' ')
		if minutesTensByte==' ' and minutesUnitsByte==' ':
			colonByte=' '
		else:
			colonByte=':'

		#seconds behavior
		secondsTensByte=self.getValue(clockName+'_'+'secondsTens', minValueNotBlanked=minutesUnitsByte==' ')
		secondsUnitsByte=self.getValue(clockName+'_'+'secondsUnits', minValueNotBlanked=0)

		#format as a string
		timeOutClock=(\
		minutesTensByte, minutesUnitsByte, colonByte, \
		secondsTensByte, secondsUnitsByte)
		clockS=('%s%s%s%s%s') % timeOutClock
		self.decodePacket=self.stringEater(self.decodePacket, places=len(clockS))
		string+=clockS
		return string

	def timeOfDayClockString(self, string, packet=None):
		#time of day byte(s), CCHH:MM:SS, 10
		#make the clock variables
		clockName='timeOfDayClock'
		colon=self.game.gameData['colonIndicator']
		timeListNames=['daysTens', 'daysUnits', 'hoursTens', \
		'hoursUnits', 'minutesTens', 'minutesUnits', 'secondsTens', \
		'secondsUnits', 'tenthsUnits', 'hundredthsUnits']

		if packet is not None:
			CCBYTES=packet[:2]=='AM'

			if packet[2]==' ':
				hoursTensByte=0
			else:
				hoursTensByte=int(packet[2])
			if packet[3]==' ':
				hoursUnitsByte=0
			else:
				hoursUnitsByte=int(packet[3])
			self.game.setGameData(clockName+'_'+timeListNames[2], hoursTensByte, 1)
			self.game.setGameData(clockName+'_'+timeListNames[3], hoursUnitsByte, 1)
			if packet[4]==' ':
				hoursColonByte=0
			else:
				hoursColonByte=1
			#self.game.setGameData('hoursColonIndicator', hoursColonByte) Does not exist
			if packet[5]==' ':
				minutesTensByte=0
			else:
				minutesTensByte=int(packet[5])
			if packet[6]==' ':
				minutesUnitsByte=0
			else:
				minutesUnitsByte=int(packet[6])
			self.game.setGameData(clockName+'_'+timeListNames[4], minutesTensByte, 1)
			self.game.setGameData(clockName+'_'+timeListNames[5], minutesUnitsByte, 1)
			if packet[7]==' ':
				colonByte=0
			else:
				colonByte=1
			#This colon breaks the main colon from period clock
			#self.game.setGameData('colonIndicator', colonByte)
			if packet[8]==' ':
				secondsTensByte=0
			else:
				secondsTensByte=int(packet[8])
			if packet[9]==' ':
				secondsUnitsByte=0
			else:
				secondsUnitsByte=int(packet[9])
			self.game.setGameData(clockName+'_'+timeListNames[6], secondsTensByte, 1)
			self.game.setGameData(clockName+'_'+timeListNames[7], secondsUnitsByte, 1)

		#CC=24 or AM or PM
		if self.game.getClockData(clockName, 'PM'):
			CCBYTES='PM'
		else:
			CCBYTES='AM'
		#FIX 24 and ask internal clock source question

		#hours behavior
		hoursTensByte=self.getValue(clockName+'_'+'hoursTens', minValueNotBlanked=1)
		hoursUnitsByte=self.getValue(clockName+'_'+'hoursUnits', minValueNotBlanked=hoursTensByte==' ')
		if hoursTensByte==' ' and hoursUnitsByte==' ':
			hoursColonByte=' '
		else:
			hoursColonByte=':'

		#minutes behavior
		minutesTensByte=self.getValue(clockName+'_'+'minutesTens', minValueNotBlanked=0)
		minutesUnitsByte=self.getValue(clockName+'_'+'minutesUnits', minValueNotBlanked=minutesTensByte==' ')
		if minutesTensByte==' ' and minutesUnitsByte==' ':
			colonByte=' '
		else:
			colonByte=':'

		#seconds behavior
		secondsTensByte=self.getValue(clockName+'_'+'secondsTens', minValueNotBlanked=minutesUnitsByte==' ')
		secondsUnitsByte=self.getValue(clockName+'_'+'secondsUnits', minValueNotBlanked=0)

		#format as a string
		timeOfDay=(CCBYTES, \
		hoursTensByte, hoursUnitsByte, hoursColonByte, \
		minutesTensByte, minutesUnitsByte, colonByte, \
		secondsTensByte, secondsUnitsByte)
		clockS=('%s%s%s%s%s%s%s%s%s') % timeOfDay
		self.decodePacket=self.stringEater(self.decodePacket, places=len(clockS))
		string+=clockS
		return string

	def practiceClockString(self, string, packet=None):
		#practice clock byte(s), HH:MM:SS.xcm, 12

		#make the clock variables
		clockName='segmentTimer'
		colon=self.game.gameData['colonIndicator']
		timeListNames=['daysTens', 'daysUnits', 'hoursTens', \
		'hoursUnits', 'minutesTens', 'minutesUnits', 'secondsTens', \
		'secondsUnits', 'tenthsUnits', 'hundredthsUnits']

		if packet is not None:
			if packet[0]==' ':
				hoursTensByte=0
			else:
				hoursTensByte=int(packet[0])
			if packet[1]==' ':
				hoursUnitsByte=0
			else:
				hoursUnitsByte=int(packet[1])
			self.game.setGameData(clockName+'_'+timeListNames[2], hoursTensByte, 1)
			self.game.setGameData(clockName+'_'+timeListNames[3], hoursUnitsByte, 1)
			if packet[2]==' ':
				hoursColonByte=0
			else:
				hoursColonByte=1
			#self.game.setGameData('hoursColonIndicator', hoursColonByte) Does not exist
			if packet[3]==' ':
				minutesTensByte=0
			else:
				minutesTensByte=int(packet[3])
			if packet[4]==' ':
				minutesUnitsByte=0
			else:
				minutesUnitsByte=int(packet[4])
			self.game.setGameData(clockName+'_'+timeListNames[4], minutesTensByte, 1)
			self.game.setGameData(clockName+'_'+timeListNames[5], minutesUnitsByte, 1)
			if packet[5]==' ':
				colonByte=0
			else:
				colonByte=1
			#This colon breaks the main colon from period clock
			#self.game.setGameData('colonIndicator', colonByte)
			if packet[6]==' ':
				secondsTensByte=0
			else:
				secondsTensByte=int(packet[6])
			if packet[7]==' ':
				secondsUnitsByte=0
			else:
				secondsUnitsByte=int(packet[7])
			self.game.setGameData(clockName+'_'+timeListNames[6], secondsTensByte, 1)
			self.game.setGameData(clockName+'_'+timeListNames[7], secondsUnitsByte, 1)
			if packet[8]==' ':
				decimalByte=0
			else:
				decimalByte=1
			#self.game.setGameData('decimalIndicator', decimalByte) Does not exist
			if packet[9]==' ':
				tenthsUnitsByte=0
			else:
				tenthsUnitsByte=int(packet[9])
			if packet[10]==' ':
				hundredthsUnitsByte=0
			else:
				hundredthsUnitsByte=int(packet[10])
			if packet[11]==' ':
				thousandthsUnitsByte=0
			else:
				thousandthsUnitsByte=int(packet[11])
			self.game.setGameData(clockName+'_'+timeListNames[8], tenthsUnitsByte, 1)
			self.game.setGameData(clockName+'_'+timeListNames[9], hundredthsUnitsByte, 1)
			#self.game.setGameData(clockName+'_'+'thousandthsUnits', thousandthsUnitsByte, 1) Does not exist

		#hours behavior
		hoursTensByte=self.getValue(clockName+'_'+'hoursTens', minValueNotBlanked=1)
		hoursUnitsByte=self.getValue(clockName+'_'+'hoursUnits', minValueNotBlanked=hoursTensByte==' ')
		if hoursTensByte==' ' and hoursUnitsByte==' ':
			hoursColonByte=' '
		else:
			hoursColonByte=':'

		#minutes behavior
		minutesTensByte=self.getValue(clockName+'_'+'minutesTens', minValueNotBlanked=hoursColonByte==' ')
		minutesUnitsByte=self.getValue(clockName+'_'+'minutesUnits', minValueNotBlanked=minutesTensByte==' ')
		if minutesTensByte==' ' and minutesUnitsByte==' ':
			colonByte=' '
		else:
			colonByte=':'

		#seconds behavior
		secondsTensByte=self.getValue(clockName+'_'+'secondsTens', minValueNotBlanked=minutesUnitsByte==' ')
		secondsUnitsByte=self.getValue(clockName+'_'+'secondsUnits', minValueNotBlanked=0)
		if colonByte==' ':
			decimalByte='.'
		else:
			decimalByte=' '

		#sub-second behavior
		if decimalByte=='.':
			tenthsUnitsByte=self.getValue(clockName+'_'+'tenthsUnits', minValueNotBlanked=0)
			hundredthsUnitsByte=self.getValue(clockName+'_'+'hundredthsUnits', minValueNotBlanked=0)
		else:
			tenthsUnitsByte=' '
			hundredthsUnitsByte=' '

		#thousandths not currently used
		thousandthsUnitsByte=' '

		#format as a string
		segmentTimer=(\
		hoursTensByte, hoursUnitsByte, hoursColonByte, \
		minutesTensByte, minutesUnitsByte, colonByte, \
		secondsTensByte, secondsUnitsByte, decimalByte, \
		tenthsUnitsByte, hundredthsUnitsByte, thousandthsUnitsByte)
		clockS=('%s%s%s%s%s%s%s%s%s%s%s%s') % segmentTimer

		#Make method for this cause it matches the periodClock one

		self.decodePacket=self.stringEater(self.decodePacket, places=len(clockS))
		string+=clockS
		return string

	def segmentCountString(self, string, packet=None):
		#segment count byte(s), 2w
		if packet is not None:
			if packet[0]==' ':
				segTen=0
			else:
				segTen=int(packet[0])
			if packet[1]==' ':
				segUnit=0
			else:
				segUnit=int(packet[1])
			self.game.setGameData('segmentCountTens', segTen, 1)
			self.game.setGameData('segmentCountUnits', segUnit, 1)

		segTen=self.getValue('segmentCountTens', minValueNotBlanked=1)
		segUnit=self.getValue('segmentCountUnits', minValueNotBlanked=0)
		segmentCount='%s%s' % (segTen, segUnit)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(segmentCount))
		string+=segmentCount
		return string

	def timerActivityIndicatorString(self, string, packet=None):
		#timer Activity Indicator (Blinky) byte(s), 1
		if packet is not None:
			if packet[0]==' ':
				colonIndicator=0
			else:
				colonIndicator=1

			if (0 and self.game.gameData['sport']=='MPLX3450-baseball') or self.game.gameSettings['clock_3D_or_less_Flag'] or self.game.gameSettings['2D_Clock']:
				#Need to fix this to override only when in correct modes per sport
				self.game.setGameData('colonIndicator', colonIndicator, 1)
				self.game.setGameData('decimalIndicator', 0, 1)
		
		if self.game.getGameData('colonIndicator') and 'C' in self.game.gameData['optionJumpers']:
			colonIndicator='*'
		else:
			colonIndicator=' '

		self.decodePacket=self.stringEater(self.decodePacket, places=len(colonIndicator))
		string+=colonIndicator
		return string

	def teamScoreString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ':
				segHun=0
			else:
				segHun=int(packet[0])
			if packet[1]==' ':
				segTen=0
			else:
				segTen=int(packet[1])
			if packet[2]==' ':
				segUnit=0
			else:
				segUnit=int(packet[2])
			self.game.setTeamData(team, 'scoreHundreds', segHun, 1)
			self.game.setTeamData(team, 'scoreTens', segTen, 1)
			self.game.setTeamData(team, 'scoreUnits', segUnit, 1)

		scoreHundred=self.getValue('scoreHundreds', minValueNotBlanked=1, team=team)
		scoreTen=self.getValue('scoreTens', minValueNotBlanked=scoreHundred==' ', team=team)
		scoreUnit=self.getValue('scoreUnits', minValueNotBlanked=0, team=team)
		teamScore='%s%s%s' % (scoreHundred, scoreTen, scoreUnit)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(teamScore))
		string+=teamScore
		return string

	def teamStatString(self, string, team, packet=None):
		count=0
		for number in self.game.statNumberList:
			if number is not None:
				if packet is not None:
					if packet[count*6]==' ':
						playerTen=25
					else:
						playerTen=int(packet[count*6])
					if packet[count*6+1]==' ':
						playerUnit=25
					else:
						playerUnit=int(packet[count*6+1])
					self.game.setTeamData(team, 'player'+number+'Tens', playerTen, 1)
					self.game.setTeamData(team, 'player'+number+'Units', playerUnit, 1)
					if packet[count*6+2]==' ':
						foulTen=25
					else:
						foulTen=int(packet[count*6+2])
					if packet[count*6+3]==' ':
						foulUnit=25
					else:
						foulUnit=int(packet[count*6+3])
					self.game.setTeamData(team, 'foul'+number+'Tens', foulTen, 1)
					self.game.setTeamData(team, 'foul'+number+'Units', foulUnit, 1)
					if packet[count*6+4]==' ':
						pointsTen=25
					else:
						pointsTen=int(packet[count*6+4])
					if packet[count*6+5]==' ':
						pointsUnit=25
					else:
						pointsUnit=int(packet[count*6+5])
					self.game.setTeamData(team, 'points'+number+'Tens', pointsTen, 1)
					self.game.setTeamData(team, 'points'+number+'Units', pointsUnit, 1)
					count+=1

				playerTen=self.getValue('player'+number+'Tens', minValueNotBlanked=self.game.getTeamData(team, 'player'+number+'Tens')>9, team=team)
				playerUnit=self.getValue('player'+number+'Units', minValueNotBlanked=self.game.getTeamData(team, 'player'+number+'Units')>9, team=team)
				playerString='%s%s' % (playerTen, playerUnit)
				string+=playerString

				foulTen=self.getValue('foul'+number+'Tens', minValueNotBlanked=self.game.getTeamData(team, 'foul'+number+'Tens')>9, team=team)
				foulUnit=self.getValue('foul'+number+'Units', minValueNotBlanked=self.game.getTeamData(team, 'foul'+number+'Units')>9, team=team)
				foulString='%s%s' % (foulTen, foulUnit)
				string+=foulString

				pointsTen=self.getValue('points'+number+'Tens', minValueNotBlanked=self.game.getTeamData(team, 'points'+number+'Tens')>9, team=team)
				pointsUnit=self.getValue('points'+number+'Units', minValueNotBlanked=self.game.getTeamData(team, 'points'+number+'Units')>9, team=team)
				pointsString='%s%s' % (pointsTen, pointsUnit)
				string+=pointsString
				self.decodePacket=self.stringEater(self.decodePacket, places=(len(playerString)+len(foulString)+len(pointsString)))
		return string

	def teamETNString(self, string, team, packet=None):
		if packet is not None:
			name=packet[0:20]
			name=name.rstrip()
					
			if packet[20]==' ':
				font=0
			else:
				font=int(packet[20])
			if packet[21]==' ':
				justify=0
			else:
				justify=int(packet[21])
			storedName=self.game.getTeamData(team, 'name')
			nameCheck=storedName!=name
			fontCheck=self.game.getTeamData(team, 'font')!=font
			justifyCheck=self.game.getTeamData(team, 'justify')!=justify
			
			if nameCheck or fontCheck or justifyCheck:
				if self.printETNData:
					print 'name', name,'font', font,'justify', justify
					print 'team', team, 'nameCheck', nameCheck, 'fontCheck', fontCheck, 'justifyCheck', justifyCheck
				self.ETNChangeFlag=True
				if team=='TEAM_1':
					if nameCheck:
						self.guestNameChangeFlag=True
						lenCheck=len(storedName)-len(name)
						if storedName and abs(lenCheck)==1 and 0:
							self.guestNameChangeOneCharFlag=True
							if self.printETNData:
								print 'single guest passed'
					if fontCheck or justifyCheck:
						self.guestFontJustifyChangeFlag=True
				elif team=='TEAM_2':
					if nameCheck:
						self.homeNameChangeFlag=True
						lenCheck=len(storedName)-len(name)
						if self.printETNData:
							print 'len(storedName)', len(storedName), 'len(name)', len(name), 'abs(lenCheck)', abs(lenCheck)
						if storedName and abs(lenCheck)==1 and 0:
							self.homeNameChangeOneCharFlag=True
							if self.printETNData:
								print 'single home passed'
					if fontCheck or justifyCheck:
						self.homeFontJustifyChangeFlag=True
								
			self.game.setTeamData(team, 'name', name, 1)
			self.game.setTeamData(team, 'font', font, 1)
			self.game.setTeamData(team, 'justify', justify, 1)

		name=self.game.getTeamData(team, 'name')
		if len(name)>20:
			name=name[:20]
		string+=name

		paddedString=''
		padding=20-len(name)
		for x in range(padding):
			paddedString+=' '
		
		self.decodePacket=self.stringEater(self.decodePacket, places=20)
		string+=paddedString

		font=self.game.getTeamData(team, 'font')
		justify=self.game.getTeamData(team, 'justify')
		fontJustify='%s%s' % (font, justify)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(fontJustify))
		string+=fontJustify
		return string

	def teamTimeOutsLeftString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ':
				TOL=0
			else:
				TOL=int(packet[0])
			self.game.setTeamData(team, 'timeOutsLeft', TOL, 1)
			
		teamTimeout='%s' % (self.getValue('timeOutsLeft', minValueNotBlanked=0, team=team))
		self.decodePacket=self.stringEater(self.decodePacket, places=len(teamTimeout))
		string+=teamTimeout
		return string

	def teamHEpitchCountString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ' or packet[0]=='0':
				hitsHundreds=0
			else:
				hitsHundreds=1
			if packet[1]==' ':
				hitsTens=0
			else:
				hitsTens=int(packet[1])
			if packet[2]==' ':
				hitsUnits=0
			else:
				hitsUnits=int(packet[2])
			if packet[3]==' ':
				errorsTens=0
			else:
				errorsTens=int(packet[3])
			if packet[4]==' ':
				errorsUnits=0
			else:
				errorsUnits=int(packet[4])
			if packet[5]==' ' or packet[5]=='0':
				pitchCountHundreds=0
			else:
				pitchCountHundreds=1
			if packet[6]==' ':
				pitchCountTens=0
			else:
				pitchCountTens=int(packet[6])
			if packet[7]==' ':
				pitchCountUnits=0
			else:
				pitchCountUnits=int(packet[7])
				
			#Save double pitch count from single pitch count
			LINE5andDjumper= self.game.gameData['sport']=='MPLINESCORE5' and ('D' in self.game.gameData['optionJumpers'])
			self.game.setTeamData(team, 'pitchCountHundreds', pitchCountHundreds, 1)
			self.game.setTeamData(team, 'pitchCountTens', pitchCountTens, 1)
			self.game.setTeamData(team, 'pitchCountUnits', pitchCountUnits, 1)			
			if self.game.getTeamData(self.game.home, 'atBatIndicator') and team==self.game.guest:
				self.game.setGameData('singlePitchCountHundreds', pitchCountHundreds, 1)
				self.game.setGameData('singlePitchCountTens', pitchCountTens, 1)
				self.game.setGameData('singlePitchCountUnits', pitchCountUnits, 1)	
			elif not self.game.getTeamData(self.game.home, 'atBatIndicator') and team==self.game.home:
				self.game.setGameData('singlePitchCountHundreds', pitchCountHundreds, 1)
				self.game.setGameData('singlePitchCountTens', pitchCountTens, 1)
				self.game.setGameData('singlePitchCountUnits', pitchCountUnits, 1)	

				
			self.game.setTeamData(team, 'hitsHundreds', hitsHundreds, 1)
			self.game.setTeamData(team, 'hitsTens', hitsTens, 1)
			self.game.setTeamData(team, 'hitsUnits', hitsUnits, 1)
			self.game.setTeamData(team, 'errorsTens', errorsTens, 1)
			self.game.setTeamData(team, 'errorsUnits', errorsUnits, 1)


		hitsHundred=self.getValue('hitsHundreds', minValueNotBlanked=1, team=team)
		hitsTen=self.getValue('hitsTens', minValueNotBlanked=hitsHundred==' ', team=team)
		hitsUnit=self.getValue('hitsUnits', minValueNotBlanked=0, team=team)
		teamHits='%s%s%s' % (hitsHundred, hitsTen, hitsUnit)
		string+=teamHits

		errorsTen=self.getValue('errorsTens', minValueNotBlanked=1, team=team)
		errorsUnit=self.getValue('errorsUnits', minValueNotBlanked=0, team=team)
		errorsString='%s%s' % (errorsTen, errorsUnit)
		string+=errorsString
		
		#Save double pitch count from single pitch count
		if self.game.gameData['sport']=='MPLINESCORE5' and not ('D' in self.game.gameData['optionJumpers']):
			if self.game.getTeamData(self.game.home, 'atBatIndicator'):
				#In Bottom
				self.game.setTeamData(self.game.guest, 'pitchCountHundreds', self.game.getGameData('singlePitchCountHundreds'), 1)
				self.game.setTeamData(self.game.guest, 'pitchCountTens', self.game.getGameData('singlePitchCountTens'), 1)
				self.game.setTeamData(self.game.guest, 'pitchCountUnits', self.game.getGameData('singlePitchCountUnits'), 1)	
	
			else:
				self.game.setTeamData(self.game.home, 'pitchCountHundreds', self.game.getGameData('singlePitchCountHundreds'), 1)
				self.game.setTeamData(self.game.home, 'pitchCountTens', self.game.getGameData('singlePitchCountTens'), 1)
				self.game.setTeamData(self.game.home, 'pitchCountUnits', self.game.getGameData('singlePitchCountUnits'), 1)	

		pitchCountHundred=self.getValue('pitchCountHundreds', minValueNotBlanked=1, team=team)
		pitchCountTen=self.getValue('pitchCountTens', minValueNotBlanked=pitchCountHundred==' ', team=team)
		pitchCountUnit=self.getValue('pitchCountUnits', minValueNotBlanked=0, team=team)
		teamPitchCount='%s%s%s' % (pitchCountHundred, pitchCountTen, pitchCountUnit)
		string+=teamPitchCount
		self.decodePacket=self.stringEater(self.decodePacket, places=(len(teamHits)+len(errorsString)+len(teamPitchCount)))
		return string

	def teamShotsSavesKicksString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ':
				shotsTens=0
			else:
				shotsTens=int(packet[0])
			if packet[1]==' ':
				shotsUnits=0
			else:
				shotsUnits=int(packet[1])
			self.game.setTeamData(team, 'shotsTens', shotsTens, 1)
			self.game.setTeamData(team, 'shotsUnits', shotsUnits, 1)

		shotsTen=self.getValue('shotsTens', minValueNotBlanked=1, team=team)
		shotsUnit=self.getValue('shotsUnits', minValueNotBlanked=0, team=team)
		shotsString='%s%s' % (shotsTen, shotsUnit)
		string+=shotsString

		if self.game.gameData['sportType']=='soccer':
			if packet is not None:
				if packet[2]==' ':
					savesTens=0
				else:
					savesTens=int(packet[2])
				if packet[3]==' ':
					savesUnits=0
				else:
					savesUnits=int(packet[3])
				self.game.setTeamData(team, 'savesTens', savesTens, 1)
				self.game.setTeamData(team, 'savesUnits', savesUnits, 1)
				if packet[4]==' ':
					kicksTens=0
				else:
					kicksTens=int(packet[4])
				if packet[5]==' ':
					kicksUnits=0
				else:
					kicksUnits=int(packet[5])
				self.game.setTeamData(team, 'kicksTens', kicksTens, 1)
				self.game.setTeamData(team, 'kicksUnits', kicksUnits, 1)

			savesTen=self.getValue('savesTens', minValueNotBlanked=1, team=team)
			savesUnit=self.getValue('savesUnits', minValueNotBlanked=0, team=team)
			savesString='%s%s' % (savesTen, savesUnit)
			string+=savesString

			kicksTen=self.getValue('kicksTens', minValueNotBlanked=1, team=team)
			kicksUnit=self.getValue('kicksUnits', minValueNotBlanked=0, team=team)
			kicksString='%s%s' % (kicksTen, kicksUnit)
			string+=kicksString
			self.decodePacket=self.stringEater(self.decodePacket, places=(len(shotsString)+len(savesString)+len(kicksString)))
		else:
			self.decodePacket=self.stringEater(self.decodePacket, places=len(shotsString))
		return string

	def teamPossessionString(self, string, team, packet=None):
		if self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
			name='atBatIndicator'
			symbol='B'
		else:
			name='possession'
			symbol='P'
		if packet is not None:
			if packet[0]==' ':
				teamPossession=0
			else:
				teamPossession=1
			self.game.setTeamData(team, name, teamPossession, 1)

		if self.game.getTeamData(team, name):
			teamPossession=symbol
		else:
			teamPossession=' '

		self.decodePacket=self.stringEater(self.decodePacket, places=len(teamPossession))
		string+=teamPossession
		return string

	def teamPenaltyIndicatorCountString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ':
				penaltyIndicator=0
			else:
				penaltyIndicator=1
			if packet[1]==' ':
				penaltyCount=0
			else:
				penaltyCount=int(packet[1])
			self.game.setTeamData(team, 'penaltyIndicator', penaltyIndicator, 1)
			self.game.setTeamData(team, 'penaltyCount', penaltyCount, 1)

		if self.game.getTeamData(team, 'penaltyIndicator'):
			penI='P'
		else:
			penI=' '
		penaltyCount=self.getValue('penaltyCount', minValueNotBlanked=0, team=team)
		penalty='%s%s' % (penI, penaltyCount)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(penalty))
		string+=penalty
		return string

	def teamBonusString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ':
				bonus=0
			else:
				bonus=int(packet[0])
			self.game.setTeamData(team, 'bonus', bonus, 1)

		if self.game.getTeamData(team, 'bonus')==1:
			teamBonus='1'
		elif self.game.getTeamData(team, 'bonus')==2:
			teamBonus='2'
		else:
			teamBonus=' '
		string+=teamBonus
		self.decodePacket=self.stringEater(self.decodePacket, places=len(teamBonus))
		return string

	def teamInningScoreString(self, string, team, packet=None):
		for inning in range(15):
			if packet is not None:
				if packet[inning]==' ':
					scoreInning=255
				else:
					scoreInning=int(packet[inning])
				self.game.setTeamData(team, 'scoreInn'+str(inning+1), scoreInning, 1)
			scoreInn=self.getValue('scoreInn'+str(inning+1), minValueNotBlanked=self.game.getTeamData(team, 'scoreInn'+str(inning+1))>9, team=team)
			string+=str(scoreInn)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(range(15)))
		return string

	def teamPenaltyPlayerNumberClockString(self, string, team, packet=None):
		pen='penalty'
		if team[-1]=='1':
			teamName='teamOne'
		elif team[-1]=='2':
			teamName='teamTwo'
		for x, clockNumber in enumerate([1,2]):
			clockName=pen+str(clockNumber)+'_'+teamName
			if packet is not None:
				if packet[0+x*6]==' ':
					PLAYER_NUMBERTens=255
				else:
					PLAYER_NUMBERTens=int(packet[0+x*6])
				if packet[1+x*6]==' ':
					PLAYER_NUMBERUnits=255
				else:
					PLAYER_NUMBERUnits=int(packet[1+x*6])
				if packet[2+x*6]==' ':
					minutesUnits=255
				else:
					minutesUnits=int(packet[2+x*6])

				if packet[4+x*6]==' ':
					secondsTens=255
				else:
					secondsTens=int(packet[4+x*6])
				if packet[5+x*6]==' ':
					secondsUnits=255
				else:
					secondsUnits=int(packet[5+x*6])
					
				if (minutesUnits==255 and secondsTens==255 and secondsUnits==255) or \
				(minutesUnits==0 and secondsTens==0 and secondsUnits==0):
					colon=False
				else:
					colon=True
										
				self.game.setTeamData(team, 'TIMER'+str(clockNumber)+'_PLAYER_NUMBERTens', PLAYER_NUMBERTens, 1)
				self.game.setTeamData(team, 'TIMER'+str(clockNumber)+'_PLAYER_NUMBERUnits', PLAYER_NUMBERUnits, 1)
				self.game.clockDict[clockName].timeUnitsDict['minutesUnits']=minutesUnits
				self.game.setTeamData(team, 'TIMER'+str(clockNumber)+'_COLON_INDICATOR', colon, 1)
				self.game.clockDict[clockName].timeUnitsDict['secondsTens']=secondsTens
				self.game.clockDict[clockName].timeUnitsDict['secondsUnits']=secondsUnits

			timerPlayerNumberTens=self.getValue('TIMER'+str(clockNumber)+'_PLAYER_NUMBERTens', minValueNotBlanked=self.game.getTeamData(team, 'TIMER'+str(clockNumber)+'_PLAYER_NUMBERTens')>9, team=team)
			timerPlayerNumberUnits=self.getValue('TIMER'+str(clockNumber)+'_PLAYER_NUMBERUnits', minValueNotBlanked=self.game.getTeamData(team, 'TIMER'+str(clockNumber)+'_PLAYER_NUMBERUnits')>9, team=team)
			timerPlayerNumber='%s%s' % (timerPlayerNumberTens, timerPlayerNumberUnits)
			string+=timerPlayerNumber

			#minutes behavior

			minutesUnitsByte=self.getValue(clockName+'_'+'minutesUnits', minValueNotBlanked=0)

			#seconds behavior
			secondsTensByte=self.getValue(clockName+'_'+'secondsTens', minValueNotBlanked=0)
			secondsUnitsByte=self.getValue(clockName+'_'+'secondsUnits', minValueNotBlanked=0)
			if minutesUnitsByte==' ' or secondsTensByte==' ' or secondsUnitsByte==' ':
				colonByte=' '
			else:
				colonByte=':'
			#format as a string
			penaltyClock=(\
			minutesUnitsByte, colonByte, \
			secondsTensByte, secondsUnitsByte)
			clockS=('%s%s%s%s') % penaltyClock
			string+=clockS
			#print penaltyClock
			self.decodePacket=self.stringEater(self.decodePacket, places=len(timerPlayerNumber)+len(clockS))

		return string

	def teamGoalIndicatorString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ':
				goalIndicator=0
			else:
				goalIndicator=1
			self.game.setTeamData(team, 'goalIndicator', goalIndicator, 1)

		if self.game.getTeamData(team, 'goalIndicator'):
			goalI='G'
		else:
			goalI=' '
		string+=goalI
		self.decodePacket=self.stringEater(self.decodePacket, places=len(goalI))
		return string

	def teamFoulsPlayerNumberFoulsString(self, string, team, packet=None):
		if packet is not None:
			if packet[0]==' ':
				foulsTens=0
			else:
				foulsTens=int(packet[0])
			if packet[1]==' ':
				foulsUnits=0
			else:
				foulsUnits=int(packet[1])
			self.game.setTeamData(team, 'foulsTens', foulsTens, 1)
			self.game.setTeamData(team, 'foulsUnits', foulsUnits, 1)

		foulsTen=self.getValue('foulsTens', minValueNotBlanked=1, team=team)
		foulsUnit=self.getValue('foulsUnits', minValueNotBlanked=0, team=team)
		teamFoul='%s%s' % (foulsTen, foulsUnit)
		string+=teamFoul

		teamPlayerFoul='    '
		string+=teamPlayerFoul
		self.decodePacket=self.stringEater(self.decodePacket, places=(len(teamFoul)+len(teamPlayerFoul)))
		return string

	def periodInningString(self, string, packet=None):
		#period byte
		if self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
			if packet is not None:
				if packet[0]==' ':
					inningTens=0
				else:
					inningTens=int(packet[0])
				if packet[1]==' ':
					inningUnits=0
				else:
					inningUnits=int(packet[1])
				self.game.setGameData('inningTens', inningTens, 1)
				self.game.setGameData('inningUnits', inningUnits, 1)
			inningTens=self.getValue('inningTens', minValueNotBlanked=1)
			inningUnits=self.getValue('inningUnits', minValueNotBlanked=0)
			periodByte='%s%s' % (inningTens, inningUnits)
		elif self.game.gameData['sportType']=='football':
			if packet is not None:
				if packet[0]==' ':
					quarter=0
				else:
					quarter=int(packet[0])
				self.game.setGameData('quarter', quarter, 1)
			quarter=self.getValue('quarter', minValueNotBlanked=0)
			periodByte='%s' % (quarter)
		else:
			if packet is not None:
				if packet[0]==' ':
					period=0
				else:
					period=int(packet[0])
				self.game.setGameData('period', period, 1)
			period=self.getValue('period', minValueNotBlanked=0)
			periodByte='%s' % (period)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(periodByte))
		string+=periodByte
		return string

	def extraFootballString(self, string, packet=None):
		if packet is not None:
			if packet[0]==' ':
				down=0
			else:
				down=int(packet[0])
			if packet[1]==' ':
				ballOnTens=0
			else:
				ballOnTens=int(packet[1])
			if packet[2]==' ':
				ballOnUnits=0
			else:
				ballOnUnits=int(packet[2])
			if packet[3]==' ':
				yardsToGoTens=0
			else:
				yardsToGoTens=int(packet[3])
			if packet[4]==' ':
				yardsToGoUnits=0
			else:
				yardsToGoUnits=int(packet[4])
			self.game.setGameData('down', down, 1)
			self.game.setGameData('ballOnTens', ballOnTens, 1)
			self.game.setGameData('ballOnUnits', ballOnUnits, 1)
			self.game.setGameData('yardsToGoTens', yardsToGoTens, 1)
			self.game.setGameData('yardsToGoUnits', yardsToGoUnits, 1)

		downUnit=self.getValue('down', minValueNotBlanked=0)
		ballOnTen=self.getValue('ballOnTens', minValueNotBlanked=1)
		ballOnUnit=self.getValue('ballOnUnits', minValueNotBlanked=0)
		yardsToGoTen=self.getValue('yardsToGoTens', minValueNotBlanked=1)
		yardsToGoUnit=self.getValue('yardsToGoUnits', minValueNotBlanked=0)
		teamFoul='%s%s%s%s%s' % (downUnit, ballOnTen, ballOnUnit, yardsToGoTen, yardsToGoUnit)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(teamFoul))
		string+=teamFoul
		return string

	def playerNumberFoulsString(self, string, packet=None):
		if packet is not None:
			if packet[0]==' ':
				playerNumberTens=255
			else:
				playerNumberTens=int(packet[0])
			if packet[1]==' ':
				playerNumberUnits=255
			else:
				playerNumberUnits=int(packet[1])
			if packet[2]==' ':
				playerFoulsTens=255
			else:
				playerFoulsTens=int(packet[2])
			if packet[3]==' ':
				playerFoulsUnits=255
			else:
				playerFoulsUnits=int(packet[3])
			self.game.setGameData('playerNumberTens', playerNumberTens, 1)
			self.game.setGameData('playerNumberUnits', playerNumberUnits, 1)
			self.game.setGameData('playerFoulsTens', playerFoulsTens, 1)
			self.game.setGameData('playerFoulsUnits', playerFoulsUnits, 1)

		playerNumberTen=self.getValue('playerNumberTens', minValueNotBlanked=self.game.getGameData('playerNumberTens')>9)
		playerNumberUnit=self.getValue('playerNumberUnits', minValueNotBlanked=self.game.getGameData('playerNumberUnits')>9)
		playerFoulsTen=self.getValue('playerFoulsTens', minValueNotBlanked=1)
		playerFoulsUnit=self.getValue('playerFoulsUnits', minValueNotBlanked=0)
		player='%s%s%s%s' % (playerNumberTen, playerNumberUnit, playerFoulsTen, playerFoulsUnit)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(player))
		string+=player
		return string

	def extraBaseballString(self, string, packet=None):
		if packet is not None:
			if packet[0]==' ':
				inningBot=0
			else:
				inningBot=1
			if packet[1]==' ':
				balls=0
			else:
				balls=int(packet[1])
			if packet[2]==' ':
				strikes=0
			else:
				strikes=int(packet[2])
			if packet[3]==' ':
				outs=0
			else:
				outs=int(packet[3])
			if packet[4]==' ':
				hitIndicator=0
			else:
				hitIndicator=1
			if packet[5]==' ':
				errorIndicator=0
			else:
				errorIndicator=1
			if packet[6]==' ':
				errorPosition=255
			else:
				errorPosition=int(packet[6])
			self.game.setGameData('inningBot', inningBot, 1)
			self.game.setGameData('balls', balls, 1)
			self.game.setGameData('strikes', strikes, 1)
			self.game.setGameData('outs', outs, 1)
			self.game.setGameData('hitIndicator', hitIndicator, 1)
			self.game.setGameData('errorIndicator', errorIndicator, 1)
			self.game.setGameData('errorPosition', errorPosition, 1)

		if self.game.getTeamData(self.game.guest, 'atBatIndicator'):
			innBot='T'
		else:
			innBot='B'
		balls=self.getValue('balls', minValueNotBlanked=1)
		strikes=self.getValue('strikes', minValueNotBlanked=1)
		outs=self.getValue('outs', minValueNotBlanked=1)
		if self.game.gameData['hitIndicator']:
			hit='H'
		else:
			hit=' '
		if self.game.gameData['errorIndicator']:
			error='E'
		else:
			error=' '
		errorPosition=self.getValue('errorPosition', minValueNotBlanked=1)
		stuff='%s%s%s%s%s%s%s' % (innBot, balls, strikes, outs, hit, error, errorPosition)
		string+=stuff
		
		#-----
		if packet is not None:
			if packet[7]==' ':
				pitchSpeedHundreds=0
			else:
				pitchSpeedHundreds=int(packet[7])
			if packet[8]==' ':
				pitchSpeedTens=0
			else:
				pitchSpeedTens=int(packet[8])
			if packet[9]==' ':
				pitchSpeedUnits=0
			else:
				pitchSpeedUnits=int(packet[9])
			self.game.setGameData('pitchSpeedHundreds', pitchSpeedHundreds, 1)
			self.game.setGameData('pitchSpeedTens', pitchSpeedTens, 1)
			self.game.setGameData('pitchSpeedUnits', pitchSpeedUnits, 1)

		pitchSpeedHundred=self.getValue('pitchSpeedHundreds', minValueNotBlanked=1)
		pitchSpeedTen=self.getValue('pitchSpeedTens', minValueNotBlanked=pitchSpeedHundred==' ')
		pitchSpeedUnit=self.getValue('pitchSpeedUnits', minValueNotBlanked=0)
		pitchSpeed='%s%s%s' % (pitchSpeedHundred, pitchSpeedTen, pitchSpeedUnit)
		string+=pitchSpeed
		
		#-----10
		pitchSpeedUnitOfMeasure=' '
		string+=pitchSpeedUnitOfMeasure
		
		#-----
		if packet is not None:
			if packet[11]==' ':
				batterNumberTens=0
			else:
				batterNumberTens=int(packet[11])
			if packet[12]==' ':
				batterNumberUnits=0
			else:
				batterNumberUnits=int(packet[12])
			self.game.setGameData('batterNumberTens', batterNumberTens, 1)
			self.game.setGameData('batterNumberUnits', batterNumberUnits, 1)
			
		batterNumberTen=self.getValue('batterNumberTens', minValueNotBlanked=1)
		batterNumberUnit=self.getValue('batterNumberUnits', minValueNotBlanked=0)	
		batterNumber='%s%s' % (batterNumberTen, batterNumberUnit)
		string+=batterNumber
		
		battingAverage='      ' # 6 bytes Player Batting Average N.NNNN
		string+=battingAverage

		runnerOnFirst='  ' # 2 bytes Runner on First NN
		string+=runnerOnFirst

		runnerOnSecond='  ' # 2 bytes Runner on Second NN
		string+=runnerOnSecond
		
		runnerOnThird='  ' # 2 bytes Runner on Third NN
		string+=runnerOnThird
		
		self.decodePacket=self.stringEater(self.decodePacket, places=len(stuff)+len(pitchSpeed)+\
		len(pitchSpeedUnitOfMeasure)+len(batterNumber)+len(battingAverage)+\
		len(runnerOnFirst)+len(runnerOnSecond)+len(runnerOnThird))
		return string

	def hornOneTwoString(self, string, packet=None):
		if packet is not None:
			if packet[0]==' ':
				periodHorn=0
			else:
				periodHorn=1

			self.game.setGameData('periodHorn', periodHorn, 1)
			
			if self.game.gameSettings['visualHornEnable']:
				self.game.gameData['visualHornIndicator1']=periodHorn
				#print 'VISUAL HORN ON'
				if self.game.gameData['sportType']=='basketball' or self.game.gameData['sportType']=='hockey':
					self.game.gameData['visualHornIndicator2']=periodHorn
		if self.game.gameData['periodHorn']:
			horn1='H'
		else:
			horn1=' '
		string+=horn1
		if self.game.gameData['sportType']=='football' or self.game.gameData['sportType']=='soccer':
			if packet is not None:
				if packet[1]==' ':
					delayOfGameHorn=0
				else:
					delayOfGameHorn=1
				self.game.setGameData('delayOfGameHorn', delayOfGameHorn, 1)
			if self.game.gameData['delayOfGameHorn']:
				horn2='H'
			else:
				horn2=' '

		else:
			horn2=' '#horn2
		string+=horn2
		self.decodePacket=self.stringEater(self.decodePacket, places=len(horn1)+len(horn2))
		return string

	def shotHornString(self, string, packet=None):
		if packet is not None:
			if packet[0]==' ':
				shotClockHorn=0
			else:
				shotClockHorn=1
			self.game.setGameData('shotClockHorn', shotClockHorn, 1)

		if self.game.gameData['shotClockHorn']:
			shotHorn='H'
		else:
			shotHorn=' '
		string+=shotHorn
		if self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
			breakTimeOut=' ' #break/time out horn
		else:
			breakTimeOut=''
		string+=breakTimeOut
		self.decodePacket=self.stringEater(self.decodePacket, places=len(shotHorn)+len(breakTimeOut))
		return string

	def reservedString(self, string='', packet=None):
		if self.ETNFlag or self.game.gameData['sportType']=='soccer':
			reserved='           ' #11
		elif self.game.gameData['sportType']=='baseball' or self.game.gameData['sportType']=='linescore':
			reserved='                        ' #24
		elif self.game.gameData['sportType']=='football':
			reserved='            ' #12
		elif self.game.gameData['sportType']=='basketball' or self.game.gameData['sportType']=='hockey':
			reserved='                ' #16
		elif self.game.gameData['sportType']=='stat':
			reserved='             ' #13
		string+=reserved
		#print 'len(reserved)', len(reserved)
		self.decodePacket=self.stringEater(self.decodePacket, places=len(reserved))
		return string

	def checksumByte(self, string, packet=None):
		#check sum byte
		CS=0
		#print 'string', string
		if packet is not None:
			#print 'packet', packet
			string=packet[0:-2]
			#print 'packet string', string

		for y in range(len(string)):
			if y!=0:
				CS+=ord(string[y])
		#print 'CS', CS, 'CS%0x100', CS%0x100, 'CS%0x100+0x32', CS%0x100+0x32
		if (CS%0x100)<(0x32):
			checkSum=chr(CS%0x100+0x32)
		else:
			checkSum=chr(CS%0x100)
		#print 'ord(checkSum)', ord(checkSum)

		if packet is not None:
			try:
				if checkSum!=packet[-2]:
					#error
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


# TODO: clean this function and create real test functions


"""
def test():
	'''Test function if module ran independently.'''
	print "ON"
	sport='MPFOOTBALL1'
	game = selectSportInstance(sport)
	var1='period'
	var2='TIMER2_PLAYER_NUMBERTens'
	game.setGameData(var1, 9, 1)
	game.setTeamData(game.home, var2, 7)

	#printDict(self.game.__dict__)
	time.sleep(1)
	sp=Serial_Packet()
	print "\nCreate ASCII string"
	game, string=sp.encodePacket(game, printString=True, ETNFlag=False)
	print "\nLoad String back into game"
	sp.encodePacket(game, printString=True, ETNFlag=False, packet=string)
	print "\nPrint string again to look for changes"
	game, string=sp.encodePacket(game, printString=True, ETNFlag=False)

	#print game.getGameData(var1)
	#print game.getTeamData(game.home, var2)


if __name__ == '__main__':
	import time
	os.chdir('..') 
	'''Added this for csvOneRowRead to work with this structure, 
	add this line for each level below project root'''
	test()
"""
