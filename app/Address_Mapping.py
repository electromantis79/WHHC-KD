#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
**COMPLETION** = 75%  Sphinx Approved = **True**

.. topic:: Overview

    This module maps data stored in memory to the 32 or 64 bank MP architecture for a given sport.
    This can be done in either direction (memory to MP word or MP word to memory)

    :Created Date: 3/16/2015
    :Modified Date: 12/8/2017
    :Author: **Craig Gunter**

    .. warning:: This is *where the magic happens*.
"""
import cProfile, pstats, StringIO
import time

from functions import *
from MP_Data_Handler import MP_Data_Handler

class Address_Mapping(object):
	"""

	**Initialization**

	* Build a dictionary of the 32 possible words of a sport named **wordsDict**. This will be the default values for that sport.

		*Key* = binary address of group and bank

		*Value* = a 16-bit word in the low-byte then high-byte format

		  **Word** in this context is one packet of information a driver needs to update a single header

			===========  ===========
			High Byte    Low Byte
			===========  ===========
			1GBBWWIH     0GFEDCBA
			===========  ===========

			G = Group, B = Bank, W = Word (Different than the word mentioned above)

			I = Control bit, H through A = The eight segments of display data

			.. note:: Low byte is received first and the high byte is received second
	
	* 
	
	"""

	def __init__(self, sportType='Generic', game=None):
		self.sportType=sportType
		if game is not None:
			self.game=game

		#Variables and Dictionaries
		self.verbose=False
		self.verboseTunnel=False
		self.rssi=0
		self.rssiFlag=False
		self.tenthsTransitionFlag=False
		self.multisportChangeSportFlag=False
		self.multisportChangeSportCount=0
		self.brightness=100
		self.quantumDimmingTunnel=0
		self.quantumETNTunnel=0
		self.fontJustifyControl=0
		self.leftETNByte=0
		self.rightETNByte=0
		self.quantumETNTunnelTeam=''
		self.addressPair=1
		self.quantumETNTunnelProcessed=False
		self.wordListAddrStat = [1,2,3,5,6,7,9,10,11,13,14,15,17,18,19,21,22,23,33,34,35,37,38,39,41,42,43,45,46,47,49,50,51,53,54,55]
		self.tempClockDict={}
		
		if self.sportType=='stat':
			self.statFlag=True
			#self.wordListAddr = range(1,65)
			self.wordListAddr = self.wordListAddrStat
		else:
			self.statFlag=False
			self.wordListAddr = range(1,33)

		self.mp = MP_Data_Handler()
		self.wordsDict = dict.fromkeys(self.wordListAddr, 0)
		self._blankMap()

		self.configDict=readConfig()
		self.sport=self.configDict['sport']

		self.addressMapDict={}
		self.fullAddressMapDict = readAddressMap(self.sport, self.sportType, self.wordListAddr)
		self._buildAddrMap()
		
		self.periodClockUnMapKeysList=['hoursUnits', 'minutesTens', \
		'minutesUnits', 'secondsTens', 'secondsUnits', 'tenthsUnits', \
		'hundredthsUnit', 'colonIndicator']
		self.periodClockUnMapDict=dict.fromkeys(self.periodClockUnMapKeysList)

	#Startup methods
	def _blankMap(self):
		"""Build blank MP wordsDict"""
		if self.statFlag:
			for k in range(2):
				for i in range(2):
					for j in range(4):
						self.wordsDict[((i*4+j)*4+1)+k*32] = self.mp.Encode(i+1, j+1, 1, k, 0, 0x0, 0x0, 'AlwaysHighLow', 0, True)
						self.wordsDict[((i*4+j)*4+2)+k*32] = self.mp.Encode(i+1, j+1, 2, k, 0, 0x0, 0x0, 'AlwaysHighLow', 0, True)
						self.wordsDict[((i*4+j)*4+3)+k*32] = self.mp.Encode(i+1, j+1, 3, k, 0, 0x0, 0x0, 'AlwaysHighLow', 0, True)
						self.wordsDict[((i*4+j)*4+4)+k*32] = self.mp.Encode(i+1, j+1, 4, k, 0, 0, 0, 'AlwaysHighLow', 0)
		else:
			for i in range(2):
				for j in range(4):
					self.wordsDict[(i*4+j)*4+1] = self.mp.Encode(i+1, j+1, 1, 0, 0, 0x0, 0x0, 'AlwaysHighLow', 0)
					self.wordsDict[(i*4+j)*4+2] = self.mp.Encode(i+1, j+1, 2, 0, 0, 0x0, 0x0, 'AlwaysHighLow', 0)
					self.wordsDict[(i*4+j)*4+3] = self.mp.Encode(i+1, j+1, 3, 0, 0, 0, 0, 'AlwaysHighLow', 0)
					self.wordsDict[(i*4+j)*4+4] = self.mp.Encode(i+1, j+1, 4, 1, 0, 0, 0, 'AlwaysHighLow', 0)

	def _buildAddrMap(self):
		"""Build an address map with the current state of flag selected alternates."""
		for address in self.wordListAddr:
			try:
				self.addressMapDict[address]=self.fullAddressMapDict[address][1]
			except:
				print 'Error', address, self.addressMapDict

	#startup methods end

	#callable methods and internal methods start -----

	def setGame(self, game):
		#PUBLIC
		self.game=game

	def Map(self):
		#PUBLIC
		"""
		Updates the list of MP Formated data packs to be sent

		The _adjustAllBanks chain::

			_adjustAllBanks first calls _updateAddrWords
			_updateAddrWords calls _loadFromAddDict
			_loadFromAddDict calls mp.Encode
				Current Dict of 32 words are up to date

		.. note:: Map and UnMap are the only publically callable methods for this class.
		"""
		if 0:
			#This section is for testing time characteristics
			
			tic=time.time()
			pr = cProfile.Profile()
			pr.enable()
			# ... do something ...
			elapseTime(self._adjustAllBanks, On=True, Timeit=False)
			pr.disable()
			s = StringIO.StringIO()
			sortby = 'cumulative'
			ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
			ps.print_stats()
			print s.getvalue()
			toc=time.time()
			elapse=toc-tic
			print elapse
			
		else:
			#Normal Operation
			
			self._adjustAllBanks()

	#G1		B1=1,2,3,4		B2=5,6,7,8 		B3=9,10,11,12, 		B4=13,14,15,16
	#G2		B1=17,18,19,20 	B2=21,22,23,24 	B3=25,26,27,28 		B4=29,30,31,32

	#Map()'s main methods - "The _adjustAllBanks chain"
	def _adjustAllBanks(self):
		"""
		Checks states of flags per sport and creates a list of alternate mapping adressess and adds them to the standard addressMapDict.

		Fetch the data, make any changes, and adjust the **wordsDict**.
		"""

		verbose('\n-------_adjustAllBanks-------\n', self.verbose)
		Alts = []

		#Freeze clock data
		if self.game.clockDict.has_key('periodClock'):
			
			self.tempClockDict.clear()
			for clocks in self.game.clockDict.keys():
				self.tempClockDict[clocks]=dict(self.game.clockDict[clocks].timeUnitsDict)

			if self.tempClockDict['periodClock']['daysTens']==0 and self.tempClockDict['periodClock']['daysUnits']==0 and \
			self.tempClockDict['periodClock']['hoursTens']==0 and self.tempClockDict['periodClock']['hoursUnits']==0 and \
			self.tempClockDict['periodClock']['minutesTens']==0 and self.tempClockDict['periodClock']['minutesUnits']==0 and \
			self.tempClockDict['periodClock']['secondsTens']<6:
				underMinute = True
			else:
				underMinute = False
			#print 'underMinute', underMinute, 'periodClockTenthsFlag', self.game.gameSettings['periodClockTenthsFlag']

		#Check for any flag changes
		if self.game.sport=='MPBASEBALL1' or self.game.sport=='MMBASEBALL3':
			if underMinute:
				if self.game.gameSettings['2D_Clock']:
					Alts=self._formatALTS(Alts, [2,21], 2)
			else:
				if self.game.gameSettings['2D_Clock']:
					Alts=self._formatALTS(Alts, [1,2,21,22], 2)
			if self.game.gameSettings['hoursFlagJumper'] and self.game.gameSettings['2D_Clock']:
				Alts=self._formatALTS(Alts, [3,23], 2)
			if self.game.gameSettings['scoreTo19Flag']:
				Alts=self._formatALTS(Alts, [5,6,7,8,9,10,11,12,25,26,27,28], 2)
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [1,2,21,22], 4)

		elif self.game.sport=='MPLINESCORE5':
			if self.game.gameSettings['clock_3D_or_less_Flag'] and not underMinute:
				Alts=self._formatALTS(Alts, [23], 2)
				
			if self.game.gameSettings['doublePitchCountFlag'] and self.game.gameSettings['pitchSpeedFlag']:
				Alts=self._formatALTS(Alts, [5,14,15,16,31,32], 2)
			elif self.game.gameSettings['doublePitchCountFlag']:
				Alts=self._formatALTS(Alts, [14,15,16,31,32], 2)
			elif self.game.gameSettings['pitchSpeedFlag']:
				Alts=self._formatALTS(Alts, [31,32], 3)
				Alts=self._formatALTS(Alts, [5], 2)
				
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [21,22], 4)
			elif underMinute and self.game.gameSettings['periodClockTenthsFlag']:
				Alts=self._formatALTS(Alts, [21,22], 2)

		elif self.game.sport=='MPLINESCORE4':
			if underMinute and self.game.gameSettings['periodClockTenthsFlag']:
				Alts=self._formatALTS(Alts, [21,22], 2)
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [21,22], 4)

		elif self.game.sport=='MPMP_15X1' or self.game.sport=='MPMP_14X1' or self.game.sport=='MMBASEBALL4':
			pass

		elif self.sport=='MPMULTISPORT1-football' or self.sport=='MPMULTISPORT1-baseball' or \
		self.sport=='MPLX3450-football' or self.sport=='MPLX3450-baseball':
			
			if self.sport=='MPLX3450-baseball' and underMinute:
				Alts=self._formatALTS(Alts, [1], 2)
			if underMinute and self.game.gameSettings['periodClockTenthsFlag']:
				Alts=self._formatALTS(Alts, [6,7,8,21,22], 2)
				if self.sport=='MPLX3450-football':
					Alts=self._formatALTS(Alts, [1,2], 2)
			if self.game.gameSettings['clock_3D_or_less_Flag'] and (self.sport=='MPLX3450-baseball' or self.sport=='MPMULTISPORT1-baseball'):
				Alts=self._formatALTS(Alts, [31], 2)
				if underMinute:
					Alts=self._formatALTS(Alts, [8], 3)
				else:
					Alts=self._formatALTS(Alts, [8], 5)
					
			if self.sport=='MPMULTISPORT1-football':
				if self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
					Alts=self._formatALTS(Alts, [6,7,8,21,22], 3)
				if self.game.gameSettings['timeOfDayClockEnable']:
					Alts=self._formatALTS(Alts, [6,7,8,21,22], 4)
					
			elif self.sport=='MPLX3450-football':
				if self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
					Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 3)
				if self.game.gameSettings['timeOfDayClockEnable']:
					Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 4)

					
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [6,7,8,21,22], 4)

		elif self.game.sport=='MPFOOTBALL1':
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 3)
			elif underMinute:
				if not self.game.gameSettings['trackClockEnable'] and self.game.gameSettings['periodClockTenthsFlag']:
					Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 2)

			if self.game.gameSettings['trackClockEnable']: # Just Tenths Units word 3 or 4
				if self.game.gameSettings['periodClockTenthsFlag']:
					Alts=self._formatALTS(Alts, [11,18], 2)

			if self.game.gameSettings['yardsToGoUnits_to_quarter']:# or 1:# This added for a range test with a 2180 WARNING
				Alts=self._formatALTS(Alts, [23], 2)

		elif self.game.sport=='MMFOOTBALL4':
			if underMinute and self.game.gameSettings['periodClockTenthsFlag']:
				Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 2)
			if self.game.gameSettings['yardsToGoUnits_to_quarter']:
				Alts=self._formatALTS(Alts, [3,23], 2)

		elif self.sport=='MPSOCCER_LX1-football' or self.sport=='MPSOCCER_LX1-soccer':
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [6,7,8,21,22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				Alts=self._formatALTS(Alts, [6,7,8,21,22], 3)
			elif underMinute:
				if not self.game.gameSettings['trackClockEnable'] and self.game.gameSettings['periodClockTenthsFlag']:
					Alts=self._formatALTS(Alts, [6,7,8,21,22], 2)

			if self.game.gameSettings['trackClockEnable']:
				if self.game.gameSettings['periodClockTenthsFlag']:
					Alts=self._formatALTS(Alts, [18], 2)			

		elif self.game.sport=='MPBASKETBALL1':
			if self.game.gameSettings['shotClockBlankEnable']:
				Alts=self._formatALTS(Alts, [5], 3)
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 3)
			elif underMinute and self.game.gameSettings['periodClockTenthsFlag']:
				Alts=self._formatALTS(Alts, [1,2,6,7,8,21,22], 2)

		elif self.game.sport=='MPHOCKEY_LX1':
			if self.game.gameSettings['shotClockBlankEnable']:
				Alts=self._formatALTS(Alts, [5], 3)
			if self.game.gameSettings['timeOfDayClockEnable']:
				Alts=self._formatALTS(Alts, [6,7,8,21,22], 4)
			elif self.game.gameSettings['timeOutTimerEnable'] and self.game.gameSettings['timeOutTimerToScoreboard']:
				Alts=self._formatALTS(Alts, [6,7,8,21,22], 3)
			elif underMinute and self.game.gameSettings['periodClockTenthsFlag']:
				Alts=self._formatALTS(Alts, [6,7,8,21,22], 2)

		#Build addressMapDict with all level 1 Alts
		self._buildAddrMap()

		#Use addressMapDict to get values, format them and update the wordsDict
		self._updateAddrWords(Alts)

	def _formatALTS(self, List, addresses, ALT):
		for address in addresses:
			List.append((address, ALT))
		return List

	def _updateAddrWords(self, Alts):
		verbose(['Alts', Alts], self.verbose)
		#print self.addressMapDict
		#print Alts

		#Method for blanking others in time of day clock mode
		if self.game.gameSettings['timeOfDayClockBlankingEnable']:
			self.addressMapDict.clear()
			self._blankMap()
			addressList=[]
			for index, addressTup in enumerate(Alts):
				if addressTup[1]!=4:
					Alts.remove(Alts[index])
				else:
					addressList.append(addressTup[0])
		else:
			#Normal Operation
			addressList=self.wordListAddr

		#Switch out alternates
		for addressTup in Alts:
			try:
				self.addressMapDict[addressTup[0]]=self.fullAddressMapDict[addressTup[0]][addressTup[1]]
			except:
				print 'Alts', Alts , 'Not in address map'
				#print self.addressMapDict

		#Sort the players on a stat board
		if self.statFlag:# 0 for troubleshooting ASCII 2 MP converter
			self._sortPlayers()

		#Use map to get correct variable, then store in the words dictionary
		for address in addressList:

			#Fetch all data values
			group, bank, word, iBit, hBit, highNibble, lowNibble, blankType, segmentData = self._loadFromAddDict(address)
			
			#Replace 221 with rssi value - For testing of WHH Console
			if group==2 and bank==2 and word==1 and self.rssiFlag:
				highNibble=self.rssi/10
				lowNibble=self.rssi%10
			
			#Encode values into MP style word and fill wordsDict
			self.wordsDict[address]=self.mp.Encode(group, bank, word, iBit, hBit, highNibble, lowNibble, blankType, segmentData, statFlag=self.statFlag)

	def _sortPlayers(self):
		activePlayerList, team, teamName=activePlayerListSelect(self.game)
		activePlayerList.sort()

		for x, playerNumber in enumerate(activePlayerList):
			playerID=self.game.getPlayerData(team, 'playerNumber', playerNumber=playerNumber)
			self.game.setTeamData(team, 'player'+self.game.statNumberList[x+1], int(playerNumber), 2)
			foul=self.game.getPlayerData(team, 'fouls', playerID=playerID)
			self.game.setTeamData(team, 'foul'+self.game.statNumberList[x+1], foul, 2)
			points=self.game.getPlayerData(team, 'points', playerID=playerID)
			self.game.setTeamData(team, 'points'+self.game.statNumberList[x+1], points, 2)
		if len(activePlayerList)<self.game.maxActive:
			for x in range((len(self.game.statNumberList)-1)-len(activePlayerList)):
				self.game.setTeamData(team, 'player'+self.game.statNumberList[x+1+len(activePlayerList)], 255, 2)
				self.game.setTeamData(team, 'foul'+self.game.statNumberList[x+1+len(activePlayerList)], 255, 2)
				self.game.setTeamData(team, 'points'+self.game.statNumberList[x+1+len(activePlayerList)], 255, 2)

	def _loadFromAddDict(self, address): #This is the beginning of data manipulation into the MP Format!!!
		""" Get word info, adjust it, and convert it to memory value."""

		#addressMapDict fetch
		group= int(self.addressMapDict[address]['GROUP']) #INT
		word= int(self.addressMapDict[address]['WORD']) #INT
		bank= int(self.addressMapDict[address]['BANK']) #INT
		iBit=self.addressMapDict[address]['I_BIT']
		hBit=self.addressMapDict[address]['H_BIT']
		highNibble=self.addressMapDict[address]['HIGH_NIBBLE']
		lowNibble=self.addressMapDict[address]['LOW_NIBBLE']
		blankType=self.addressMapDict[address]['BLANK_TYPE']
		segmentData=self.addressMapDict[address]['SEGMENT_DATA']
		if self.verbose:
			print group, bank, word, iBit, hBit, highNibble, lowNibble, blankType, segmentData

		#Prepare values for encoding
		iBit = self._iBit_Format(iBit)#string to int
		
		hBit = self._hBit_Format(hBit)#string to int

		highNibble, lowNibble, blankType = self._Nibble_Format(highNibble, lowNibble, blankType, word, address)

		segmentData = self._segmentData_Format(segmentData)#string to int
		
		if self.verbose:
			print group, bank, word, iBit, hBit, highNibble, lowNibble, blankType, segmentData
		return group, bank, word, iBit, hBit, highNibble, lowNibble, blankType, segmentData

	#Map()'s main methods end

	#Formatting Functions
	def _iBit_Format(self, iBit):
		#Format data - iBit
		team=self._teamExtract(iBit)
		if iBit=='0'or iBit=='':
			iBit=0
		elif iBit=='1' or iBit=='active':
			iBit=1
		elif iBit=='teamOneBonus2' or iBit=='teamTwoBonus2':
			value=self.game.getTeamData(team, 'bonus')
			if value==2:
				iBit=1
			else:
				iBit=0
		elif iBit[:7]=='teamTwo' or iBit[:7]=='teamOne':
			iBit=iBit[:7]+str.lower(iBit[7])+iBit[8:]
			iBit=self.game.getTeamData(team, iBit[7:])
		elif iBit[:7]=='penalty':
			timerNumber=iBit[7]
			iBit=self._trimPenalty(iBit)
			teamString=iBit[:7]
			iBit=self._trimTeamName(iBit)
			if iBit[:5]=='colon':
				team=self._teamExtract(teamString)
				iBit=self.game.getTeamData(team, 'TIMER'+timerNumber+'_COLON_INDICATOR')
		elif iBit=='outs1':
			outs=self.game.getGameData('outs')
			if outs>=1:
				iBit=1
			else:
				iBit=0
		elif iBit=='outs2':
			outs=self.game.getGameData('outs')
			if outs>=2:
				iBit=1
			else:
				iBit=0
		elif iBit=='quarter4':
			quarter=self.game.getGameData('quarter')
			if quarter>=4:
				iBit=1
			else:
				iBit=0
		else:
			iBit=self.game.getGameData(iBit)
		return iBit

	def _hBit_Format(self, hBit):
		#Format data - hBit
		team=self._teamExtract(hBit)
		if hBit=='0'or hBit=='':
			hBit=0
		elif hBit=='1':
			hBit=1
		elif hBit[:7]=='teamTwo' or hBit[:7]=='teamOne':
			hBit=hBit[:7]+str.lower(hBit[7])+hBit[8:]
			hBit=self.game.getTeamData(team, hBit[7:])
		elif hBit[:7]=='penalty':
			timerNumber=hBit[7]
			hBit=self._trimPenalty(hBit)
			teamString=hBit[:7]
			hBit=self._trimTeamName(hBit)
			if hBit[:5]=='colon':
				team=self._teamExtract(teamString)
				hBit=self.game.getTeamData(team, 'TIMER'+timerNumber+'_COLON_INDICATOR')
		else:
			hBit=self.game.getGameData(hBit)
		return hBit

	def _teamExtract(self, value):
		team=None
		if value[:7]=='teamOne' or value[9:16]=='teamOne':
			team=self.game.guest
		elif value[:7]=='teamTwo' or value[9:16]=='teamTwo':
			team=self.game.home
		return team

	def _trimPenalty(self, name):
		name=name[9:]
		return name

	def _trimTeamName(self, name):
		name=name[:7]+str.lower(name[7])+name[8:]
		name=name[7:]
		return name

	def _periodClockValueCheck(self, value):
		answer = value=='hoursUnits' or value=='tenthsUnits' or value=='minutesUnits' \
			or value=='minutesTens'or value=='secondsUnits'or value=='secondsTens'
		return answer

	def _teamValueCheck(self, value):
		return value[:4]=='team' or value[9:13]=='team'

	def _gameValueCheck(self, value):
		if self._periodClockValueCheck(value):
			return 0
		elif self._teamValueCheck(value):
			return 0
		return 1

	def _Nibble_Format(self, highNibbleName, lowNibbleName, blankType, word, addrWordNumber):
		"""
		Gets the current game data values with these names, formats them, and returns them.
		"""
		verbose(['\nNibble Format(before) - highNibbleName, lowNibbleName, blankType, word, addrWordNumber - \n', \
		highNibbleName, lowNibbleName, blankType, word, addrWordNumber], self.verbose)

		#Handle nibble blanking
		if highNibbleName=='blank'and lowNibbleName=='blank':
			highNibble=lowNibble=highNibbleName=lowNibbleName=0
			blankType='AlwaysHighLow'
			
		elif highNibbleName=='blank':
			highNibble=highNibbleName=0
			blankType='AlwaysHigh'
			
		elif lowNibbleName=='blank':
			lowNibble=lowNibbleName=0
			blankType='AlwaysLow'

		#Handle rejected values
		if highNibbleName=='' or highNibbleName=='0':
			highNibble=highNibbleName=0
			
		if lowNibbleName=='' or lowNibbleName=='0':
			lowNibble=lowNibbleName=0

		#High nibble
		blankTypeH=False
		if highNibbleName!=0:
			teamH=self._teamExtract(highNibbleName)
			
			if self._periodClockValueCheck(highNibbleName):
				
				#cancel blanking for this
				LINE5andCjumper= self.game.gameData['sport']=='MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']
				BASEBALL1_3andCjumper= (self.game.gameData['sport']=='MPBASEBALL1' or self.game.gameData['sport']=='MMBASEBALL3') \
				and 'C' in self.game.gameData['optionJumpers']
				MultiBBandCjumper= (self.sport=='MPMULTISPORT1-baseball' or self.sport=='MPLX3450-baseball') and 'C' in self.game.gameData['optionJumpers']
				if BASEBALL1_3andCjumper or LINE5andCjumper or MultiBBandCjumper or \
				self.tempClockDict['periodClock']['hoursUnits']!=0 or self.game.gameSettings['hoursFlag'] and \
				(highNibbleName=='minutesTens' or highNibbleName=='secondsTens'):
					if self.game.gameData['sport']=='MPLINESCORE5' and 'C' not in self.game.gameData['optionJumpers']:
						pass
					else:
						blankType=0
				
				highNibble=self.tempClockDict['periodClock'][highNibbleName]#int
				
			elif highNibbleName=='delayOfGameClock_secondsTens':
				highNibble=self.tempClockDict['delayOfGameClock'][highNibbleName[17:]]#int
				
				if highNibble==255 or highNibble==25:
					blankTypeH=True
					
			elif highNibbleName=='shotClock_secondsTens':
				highNibble=self.tempClockDict['shotClock'][highNibbleName[10:]]#int
				
				if highNibble==255 or highNibble==25:
					blankTypeH=True
					
			elif highNibbleName=='timeOutTimer_secondsTens' or highNibbleName=='timeOutTimer_minutesTens':
				highNibble=self.tempClockDict['timeOutTimer'][highNibbleName[13:]]#int
				
			elif highNibbleName=='segmentTimer_secondsTens' or highNibbleName=='segmentTimer_minutesTens':
				highNibble=self.tempClockDict['segmentTimer'][highNibbleName[13:]]#int
				
			elif highNibbleName=='timeOfDayClock_hoursTens' or highNibbleName=='timeOfDayClock_minutesTens':
				highNibble=self.tempClockDict['timeOfDayClock'][highNibbleName[15:]]#int
				
			elif highNibbleName[:7]=='penalty':
				timerNumber=highNibbleName[7]
				
				highNibbleName=self._trimPenalty(highNibbleName)
				
				teamString=highNibbleName[:7]
				
				highNibbleName=self._trimTeamName(highNibbleName)
				
				if highNibbleName[:6]=='player':
					place=highNibbleName[6:]
					teamH=self._teamExtract(teamString)
					varName='timer'+timerNumber+teamString+'playerFlag'
					_flagCheck=self._flagCheck(varName)
					
					highNibble=self.game.getTeamData(teamH, 'TIMER'+timerNumber+'_PLAYER_NUMBER'+place)#int
					#print 'TIMER'+timerNumber+'_PLAYER_NUMBER'+place, highNibble
					
					if highNibble==0 and _flagCheck:
						blankType=0

					if highNibble==255 or highNibble==25:
						blankTypeH=True

					
				elif highNibbleName[:5]=='colon':
					teamH=self._teamExtract(teamString)
					highNibble=self.game.getTeamData(teamH, 'TIMER'+timerNumber+'_COLON_INDICATOR')#int
					#print 'TIMER'+timerNumber+'_COLON_INDICATOR', highNibble
					
				else:
					highNibble=self.tempClockDict['penalty'+timerNumber+'_'+teamString][highNibbleName]#int
					#print 'penalty'+timerNumber+'_'+teamString, highNibble

					if highNibble==255 or highNibble==25:
						blankTypeH=True

			elif self._teamValueCheck(highNibbleName):
				highNibbleName=self._trimTeamName(highNibbleName)
				highNibble=self.game.getTeamData(teamH, highNibbleName)#int
				
				if highNibble==255 or highNibble==25:
					blankTypeH=True

			else:
				highNibble=self.game.getGameData(highNibbleName)#int
				
				if highNibble==255 or highNibble==25:
					blankTypeH=True
					
				elif highNibble==0 and self.game.gameSettings['playerMatchGameFlag']:
					#Need to comment explicitly
					blankType=0

		#Low nibble
		blankTypeL=False
		if lowNibbleName!=0:
			teamL=self._teamExtract(lowNibbleName)
			
			if self._periodClockValueCheck(lowNibbleName):
				lowNibble=self.tempClockDict['periodClock'][lowNibbleName]#int
				
			elif lowNibbleName=='inningUnits':
				lowNibble=self.game.getGameData(lowNibbleName)#int
				
				if self.game.getGameData('inningTens'):
					blankType=0
					
			elif lowNibbleName=='singlePitchCountTens':
				lowNibble=self.game.getGameData(lowNibbleName)#int
				
				if self.game.getGameData('singlePitchCountHundreds'):
					blankType=0
					
			elif lowNibbleName=='pitchSpeedUnits':
				lowNibble=self.game.getGameData(lowNibbleName)#int
				
				if self.game.getGameData('pitchSpeedHundreds'):
					blankType=0
										
			elif lowNibbleName=='delayOfGameClock_secondsUnits':
				lowNibble=self.tempClockDict['delayOfGameClock'][lowNibbleName[17:]]#int
				
				if lowNibble==255 or lowNibble==25:
					blankTypeL=True
					
			elif lowNibbleName=='shotClock_secondsUnits':
				lowNibble=self.tempClockDict['shotClock'][lowNibbleName[10:]]#int
				
				if lowNibble==255 or lowNibble==25:
					blankTypeL=True
					
			elif lowNibbleName=='timeOutTimer_secondsUnits' or lowNibbleName=='timeOutTimer_minutesUnits' or lowNibbleName=='timeOutTimer_minutesTens':
				lowNibble=self.tempClockDict['timeOutTimer'][lowNibbleName[13:]]#int
				
			elif lowNibbleName=='segmentTimer_secondsUnits' or lowNibbleName=='segmentTimer_minutesUnits' or lowNibbleName=='segmentTimer_minutesTens':
				lowNibble=self.tempClockDict['segmentTimer'][lowNibbleName[13:]]#int
				
			elif lowNibbleName=='timeOfDayClock_hoursUnits' or lowNibbleName=='timeOfDayClock_minutesUnits' or lowNibbleName=='timeOfDayClock_hoursTens':
				lowNibble=self.tempClockDict['timeOfDayClock'][lowNibbleName[15:]]#int
				
			elif lowNibbleName[:7]=='penalty':
				timerNumber=lowNibbleName[7]
				
				lowNibbleName=self._trimPenalty(lowNibbleName)
				
				teamString=lowNibbleName[:7]
				
				lowNibbleName=self._trimTeamName(lowNibbleName)
				
				if lowNibbleName[:6]=='player':
					place=lowNibbleName[6:]
					teamL=self._teamExtract(teamString)
					varName='timer'+timerNumber+teamString+'playerFlag'
					_flagCheck=self._flagCheck(varName)
					lowNibble=self.game.getTeamData(teamL, 'TIMER'+timerNumber+'_PLAYER_NUMBER'+place)#int
					
					#print 'TIMER'+timerNumber+'_PLAYER_NUMBER'+place, lowNibble
					if lowNibble==0 and _flagCheck:
						blankType=0

					if lowNibble==255 or lowNibble==25:
						blankTypeL=True
						
				elif lowNibbleName[:5]=='colon':
					teamL=self._teamExtract(teamString)
					lowNibble=self.game.getTeamData(teamL, 'TIMER'+timerNumber+'_COLON_INDICATOR')#int
					#print 'TIMER'+timerNumber+'_COLON_INDICATOR'+place, lowNibble
					
				else:
					lowNibble=self.tempClockDict['penalty'+timerNumber+'_'+teamString][lowNibbleName]#int
					#print 'penalty'+timerNumber+'_'+teamString, lowNibble
					if lowNibble==255 or lowNibble==25:
						blankTypeL=True
						
			elif self._teamValueCheck(lowNibbleName):
				teamString=lowNibbleName[:7]
				lowNibbleName=self._trimTeamName(lowNibbleName)
				
				if lowNibbleName[:6]=='player':
					teamL=self._teamExtract(teamString)
					if teamL==self.game.guest:
						activePlayerList=self.game.activeGuestPlayerList
					elif teamL==self.game.home:
						activePlayerList=self.game.activeHomePlayerList
					else:
						activePlayerList=[]
						
					statNumber=lowNibbleName[6:-4]
					lowNibble=self.game.getTeamData(teamL, lowNibbleName)#int
					
					activeIndex=self.game.statNumberList.index(statNumber)
					if activeIndex<=len(activePlayerList):
						playerNumber=activePlayerList[activeIndex-1]
						try:
							if playerNumber[0]=='0':
								blankType=0
						except:
							pass
							
					if lowNibble==255 or lowNibble==25:
						blankTypeL=True
						
				elif lowNibbleName=='pitchCountTens':
					lowNibble=self.game.getTeamData(teamL, lowNibbleName)#int
					
					if self.game.getTeamData(teamL, 'pitchCountHundreds'):
						blankType=0
				else:
					lowNibble=self.game.getTeamData(teamL, lowNibbleName)#int
					
					if lowNibble==255 or lowNibble==25:
						blankTypeL=True
			else:
				lowNibble=self.game.getGameData(lowNibbleName)#int
				
				if lowNibble==255 or lowNibble==25:
					blankTypeL=True

		#Blanking dependent on 255 value
		if blankTypeH and blankTypeL:
			blankType='AlwaysHighLow'
			highNibble=0
			lowNibble=0
		elif blankTypeH:
			blankType='AlwaysHigh'
			highNibble=0
		elif blankTypeL:
			blankType='AlwaysLow'
			lowNibble=0

		#Print if out of range or verbose
		if self.verbose or 0:
			print '\nNibble Format(after) - highNibble, lowNibble, blankType, word, addrWordNumber -- \n', highNibble, lowNibble, blankType, word, addrWordNumber
		return highNibble, lowNibble, blankType

	def _flagCheck(self, varName):
		if self.game.gameSettings[varName]:
			_flagCheck=1
		else:
			_flagCheck=0
		return _flagCheck

	def _segmentData_Format(self, segmentData):
		#Format data - segmentData
		
		#print 'segmentData before:', segmentData
		if segmentData=='' or segmentData=='0':
			segmentData=0
		elif segmentData=='BSO':
			segmentData=self._BSODecode()
		elif segmentData=='Down_Quarter':
			segmentData=self._DownQuarterDecode()
		elif segmentData=='fQtr4_gDec':
			segmentData=''
			if self.game.getGameData('decimalIndicator'):
				segmentData='g'
			if self.game.gameData['sportType']=='soccer':
				value='period'
			else:
				value='quarter'
			if self.game.getGameData(value)>=4:
				segmentData+='f'
		elif segmentData=='gDec':
			if self.game.getGameData('decimalIndicator'):
				segmentData='g'
			else:
				segmentData=''
		elif segmentData=='f_hitIndicator':
			if self.game.getGameData('hitIndicator'):
				segmentData='f'
			else:
				segmentData=''
		elif segmentData=='abcBall_efStrike':
			segmentData=''
			balls=self.game.getGameData('balls')
			strikes=self.game.getGameData('strikes')
			if balls==0:
				pass
			elif balls==1:
				segmentData='a'
			elif balls==2:
				segmentData='ab'
			elif balls>=3:
				segmentData='abc'
			if strikes==0:
				pass
			elif strikes==1:
				segmentData+='e'
			elif strikes>=2:
				segmentData+='ef'
		elif segmentData=='bc_strike':
			segmentData=''
			strikes=self.game.getGameData('strikes')
			if strikes==0:
				pass
			elif strikes==1:
				segmentData+='b'
			elif strikes>=2:
				segmentData+='bc'
		elif segmentData=='abcBall_deOut_gDec':
			segmentData=''
			balls=self.game.getGameData('balls')
			outs=self.game.getGameData('outs')
			if balls==0:
				pass
			elif balls==1:
				segmentData='a'
			elif balls==2:
				segmentData='ab'
			elif balls>=3:
				segmentData='abc'
			if outs==0:
				pass
			elif outs==1:
				segmentData+='d'
			elif outs>=2:
				segmentData+='de'
			if self.game.getGameData('decimalIndicator'):
				segmentData+='g'
		elif segmentData=='aGeHposs_fQrt4_gDec':
			segmentData=''
			if self.game.getTeamData(self.game.guest, 'possession'):
				segmentData='a'
			if self.game.getTeamData(self.game.home, 'possession'):
				segmentData+='e'
			if self.game.getGameData('decimalIndicator'):
				segmentData+='g'
			if self.game.getGameData('quarter')>=4:
				segmentData+='f'
		elif segmentData=='abcde_PossBonus':
			segmentData=''
			if self.game.getTeamData(self.game.home, 'possession'):
				segmentData='a'
			if self.game.getTeamData(self.game.guest, 'possession'):
				segmentData+='b'
			homeB=self.game.getTeamData(self.game.home, 'bonus')
			guestB=self.game.getTeamData(self.game.guest, 'bonus')
			if homeB==0:
				pass
			if homeB==1:
				segmentData+='c'
			if homeB>=2:
				segmentData+='ce'
			if guestB==0:
				pass
			if guestB>=1:
				segmentData+='d'
		elif segmentData=='home_ace_PossBonus':
			segmentData=''
			if self.game.getTeamData(self.game.home, 'possession'):
				segmentData='a'
			homeB=self.game.getTeamData(self.game.home, 'bonus')
			if homeB==0:
				pass
			if homeB==1:
				segmentData+='c'
			if homeB>=2:
				segmentData+='ce'
		elif segmentData=='guest_ace_PossBonus':
			segmentData=''
			if self.game.getTeamData(self.game.guest, 'possession'):
				segmentData='a'
			guestB=self.game.getTeamData(self.game.guest, 'bonus')
			if guestB==0:
				pass
			if guestB==1:
				segmentData+='c'
			if guestB>=2:
				segmentData+='ce'
		elif segmentData=='period_efg':
			segmentData=''
			period=self.game.getGameData('period')
			if period==0:
				pass
			elif period==1:
				segmentData+='e'
			elif period==2:
				segmentData+='ef'
			elif period==3:
				segmentData+='efg'
			elif period>=4:
				segmentData+='efg'
		elif segmentData=='bc_detect':
			segmentData=0
		else:
			print 'Address Map spreadsheet has a segment data value not handled yet'

		if segmentData=='':
			segmentData=None
		#print 'segmentData after:', segmentData
		return segmentData

	#Segment Decode Functions
	def _BSODecode(self):
		segmentData=''
		balls=self.game.getGameData('balls')
		strikes=self.game.getGameData('strikes')
		outs=self.game.getGameData('outs')
		if balls==0:
			pass
		elif balls==1:
			segmentData='a'
		elif balls==2:
			segmentData='ab'
		elif balls>=3:
			segmentData='abc'
		if strikes==0:
			pass
		elif strikes==1:
			segmentData+='d'
		elif strikes>=2:
			segmentData+='de'
		if outs==0:
			pass
		elif outs==1:
			segmentData+='f'
		elif outs>=2:
			segmentData+='fg'
		return segmentData

	def _DownQuarterDecode(self):
		segmentData=''
		down=self.game.getGameData('down')
		quarter=self.game.getGameData('quarter')
		if down==0:
			pass
		elif down==1:
			segmentData='a'
		elif down==2:
			segmentData='ab'
		elif down==3:
			segmentData='abc'
		elif down>=4:
			segmentData='abcd'
		if quarter==0:
			pass
		elif quarter==1:
			segmentData+='e'
		elif quarter==2:
			segmentData+='ef'
		elif quarter==3:
			segmentData+='efg'
		elif quarter>=4:
			segmentData+='efg'
		return segmentData
	#Segment Decode Functions End
	#Formatting Functions End

	#-------------------------------------------------------
	
	def UnMap(self, wordList=[]): #MP Data decoded and stored in Game Object
		#PUBLIC
		"""
		Decodes words in the wordList and saves them to the game object based on sport.
		"""

		sportList = ['MMBASEBALL3','MPBASEBALL1','MMBASEBALL4','MPLINESCORE4','MPLINESCORE5',\
		'MPMP-15X1','MPMP-14X1','MPMULTISPORT1-baseball','MPMULTISPORT1-football', 'MPFOOTBALL1','MMFOOTBALL4','MPBASKETBALL1', \
		'MPSOCCER_LX1-soccer','MPSOCCER_LX1-football','MPSOCCER1','MPHOCKEY_LX1','MPHOCKEY1','MPCRICKET1','MPRACETRACK1','MPLX3450-baseball','MPLX3450-football','MPGENERIC', 'MPSTAT']
		#print '----Unmap wordList size', len(wordList)

		#Create address word list to target one address for each data type or allow passed value
		if self.game.gameData['sport']=='MPBASKETBALL1':
			addressWordList=[5,13,14,15,19,20,21,22,23,24,25,26,27,28]
		elif self.game.gameData['sport']=='MPFOOTBALL1' or self.game.gameData['sport']=='MMFOOTBALL4':
			addressWordList=[5,19,20,21,22,24,25,26,29,30,31,32]
			if 'E' in self.game.gameData['optionJumpers']:
				addressWordList.append(18)
		elif self.game.gameData['sport']=='MPHOCKEY_LX1':
			addressWordList=[1,2,3,4,5,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
		elif self.game.gameData['sport']=='MPSOCCER_LX1-soccer':
			addressWordList=[5,9,10,13,14,18,19,20,21,22,23,24,25,26,29,30,31]
		elif self.game.gameData['sport']=='MPSOCCER_LX1-football':
			addressWordList=[5,13,18,19,20,21,22,24,25,26,29,30,32]
		elif self.game.gameData['sport']=='MPLINESCORE5':
			addressWordList=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,32]
		elif self.game.gameData['sport']=='MPBASEBALL1' or self.game.gameData['sport']=='MMBASEBALL3':
			addressWordList=[5,6,7,13,14,15,16,17,18,21,22,23,24]
		elif self.game.gameData['sport']=='MMBASEBALL4':
			addressWordList=[9,10,11,13,14,15,21,22,23]
		elif self.game.gameData['sport']=='MPMULTISPORT1-baseball':
			addressWordList=[5,9,11,10,13,14,15,16,17,18,21,22,24,29,30,31,32,12]
		elif self.game.gameData['sport']=='MPMULTISPORT1-football':
			addressWordList=[5,9,10,17,21,22,24,29,30,31,11,12]
		elif self.game.gameData['sport']=='MPLX3450-baseball':
			addressWordList=[5,9,11,10,13,14,15,16,17,18,21,22,24,29,30,31,32,12]
		elif self.game.gameData['sport']=='MPLX3450-football':
			addressWordList=[5,9,10,17,21,22,24,29,30,31,11,12]
		elif self.statFlag:
			addressWordList=[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19,21,22,23]
		else:
			addressWordList=[]


		#Update game data with word list
		for element in wordList:
			group, bank, word, I_Bit, numericData = self.mp.Decode(element)
			addr=self.mp.GBW_to_MP_Address(group, bank, word)+1
			decodeData=(addr, group, bank, word, I_Bit, numericData)
			if self.verbose:
				print '\naddr:', addr, group, bank, word, 'I:', I_Bit, 'Data:', numericData
				
			if self._tunnelCheck(word, numericData):
				#Tunneling data
				verbose([ 'word', word], self.verboseTunnel)
				if word==1:
					if numericData==0xbc:
						verbose([ 'Quantum dimming tunnel open!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel=1
					elif numericData==0xad:
						verbose([ 'Quantum ETN tunnel open!!!!'], self.verboseTunnel)
						self.quantumETNTunnel=1
							
			elif self.quantumDimmingTunnel or self.quantumETNTunnel:
				verbose([ 'word', word], self.verboseTunnel)
				if word==1:
					if not (numericData>=0xaa and numericData<0xf0):
						verbose([ 'Quantum data tunnel closed!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel=0
						self.quantumETNTunnel=0
						
				elif word==2:
					verbose([ 'numericData', numericData], self.verboseTunnel)
					if self.quantumDimmingTunnel:
						self.brightness=(numericData & 0x0f) + ((numericData & 0xf0) >> 4)*10
					elif self.quantumETNTunnel:
						if numericData>=64:
							#Trim Team bit
							numericData-=64
							
							self.quantumETNTunnelTeam=self.game.home
						else:
							self.quantumETNTunnelTeam=self.game.guest
							
						verbose([ 'self.quantumETNTunnelTeam =', self.quantumETNTunnelTeam], self.verboseTunnel)

						if numericData:
							#address pair
							self.fontJustifyControl=0
							verbose([ 'address pair', numericData], self.verboseTunnel)
							self.addressPair=numericData
						else:
							#control for font-justify either team because of trimming
							self.fontJustifyControl=1

				elif word==3:
					if self.quantumETNTunnel and not self.fontJustifyControl:
						self.leftETNByte=numericData
						verbose([ 'leftETNByte', numericData], self.verboseTunnel)

				elif word==4:
					if self.quantumETNTunnel and self.fontJustifyControl:
						font=numericData/6+1
						justify=numericData%6+1
							
						self.game.setTeamData(self.quantumETNTunnelTeam, 'font', font, 1)
						self.game.setTeamData(self.quantumETNTunnelTeam, 'justify', justify, 1)
						verbose([ 'font', font, 'justify', justify], self.verboseTunnel)

						verbose([ 'Quantum data tunnel closed!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel=0
						self.quantumETNTunnel=0
						self.quantumETNTunnelProcessed=True
													
					elif self.quantumETNTunnel:
						self.rightETNByte=numericData
						verbose([ 'rightETNByte', numericData], self.verboseTunnel)
						if self.leftETNByte and self.rightETNByte:
							name=self.game.getTeamData(self.quantumETNTunnelTeam, 'name')[:(self.addressPair-1)*2]+chr(self.leftETNByte)+chr(self.rightETNByte)
						elif self.leftETNByte:
							name=self.game.getTeamData(self.quantumETNTunnelTeam, 'name')[:(self.addressPair-1)*2]+chr(self.leftETNByte)
						elif self.rightETNByte:
							verbose([ 'ERROR - should not send 0 in word 3 and something in word 4', self.leftETNByte and self.rightETNByte], self.verboseTunnel)
							name=''
						else:
							name=self.game.getTeamData(self.quantumETNTunnelTeam, 'name')
								
						self.game.setTeamData(self.quantumETNTunnelTeam, 'name', name, 1)
						verbose([ 'name-', name, '-'], self.verboseTunnel)
						
						verbose([ 'Quantum data tunnel closed!!!!'], self.verboseTunnel)
						self.quantumDimmingTunnel=0
						self.quantumETNTunnel=0
						self.quantumETNTunnelProcessed=True
	
			else:
				#Normal data
				if addr in addressWordList:
					#print 'enter list and tunnel check'
					
					#Handle persistant ALT selection
					ALT=1
					BASE1orBASE3= self.game.gameData['sport']=='MPBASEBALL1' or self.game.gameData['sport']=='MMBASEBALL3'
					MULTIbaseOr3450baseCjumper= self.game.gameData['sport']=='MPMULTISPORT1-baseball' or self.game.gameData['sport']=='MPLX3450-baseball'\
					and 'C' in self.game.gameData['optionJumpers']
					LINE5andCjumper= self.game.gameData['sport']=='MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']

					
					if not BASE1orBASE3 and not LINE5andCjumper and not MULTIbaseOr3450baseCjumper and (addr==21 or addr==22):
						if self.periodClockUnMapDict['colonIndicator']==0 or self.tenthsTransitionFlag:
							ALT=2
					elif LINE5andCjumper or MULTIbaseOr3450baseCjumper:
						if addr==21 and self.tenthsTransitionFlag:
							ALT=2
					elif addr==18 and (self.game.gameData['sport']=='MPFOOTBALL1' \
					or self.game.gameData['sport']=='MPSOCCER_LX1-soccer' or \
					self.game.gameData['sport']=='MPSOCCER_LX1-football') and 'E' in self.game.gameData['optionJumpers']:
						ALT=2
					elif self.game.gameData['sport']=='MPLINESCORE5':
						if 'D' in self.game.gameData['optionJumpers'] and 'B' in self.game.gameData['optionJumpers']:
							if addr==14 or addr==15 or addr==16 or addr==31 or addr==32:
								ALT=2
							elif addr==5 or addr==7:
								ALT=2
						elif 'D' in self.game.gameData['optionJumpers']:
							if addr==14 or addr==15 or addr==16 or addr==31 or addr==32:
								ALT=2
						elif 'B' in self.game.gameData['optionJumpers']:
							if addr==31 or addr==32:
								ALT=3
							elif addr==5 or addr==7:
								ALT=2
						else:
							pass
					elif BASE1orBASE3:
						if 'C' in self.game.gameData['optionJumpers']:
							if addr==21 or addr==22:
								ALT=2
					if self.verbose:
						print 'ALT', ALT			

					#Get the current variable names for all bits
					if self.statFlag:
						if I_Bit:
							addr=addr+32
							
					dataNames=self._getDictInfo(addr, ALT=ALT)
							
					#Save values if checks are passed
					self._saveData(decodeData, dataNames)
									
				else:
					pass#print 'addr', addr, 'skipped'#

		#Multisport user switch state check
		MPMULTISPORT1= self.game.gameData['sport']=='MPMULTISPORT1-baseball' or self.game.gameData['sport']=='MPMULTISPORT1-football'
		MPLX3450= self.game.gameData['sport']=='MPLX3450-baseball' or self.game.gameData['sport']=='MPLX3450-football'
		MPSOCCER_LX1= self.game.gameData['sport']=='MPSOCCER_LX1-soccer' or self.game.gameData['sport']=='MPSOCCER_LX1-football'
		MULTISPORTtype= MPMULTISPORT1 or MPLX3450 or MPSOCCER_LX1
								
		if MULTISPORTtype:
			if self.multisportChangeSportCount<10:
				self.multisportChangeSportCount+=1
			else:
				self.multisportChangeSportCount=0
				
				#Select values to compare
				if MPMULTISPORT1:
					if self.game.gameData['sport']=='MPMULTISPORT1-baseball':
						#Baseball
						#checkHomeDict={}
						#checkGuestDict={}
						checkGameDict={'segmentQuarterFlag':True}
						sport='MPMULTISPORT1-football'
					else:
						#Football
						#checkHomeDict={}
						#checkGuestDict={}
						checkGameDict={'segmentQuarterFlag':False, 'quarter':1}
						sport='MPMULTISPORT1-baseball'
				elif MPLX3450:
					if self.game.gameData['sport']=='MPLX3450-baseball':
						#Baseball
						#checkHomeDict={}
						#checkGuestDict={}
						checkGameDict={'segmentQuarterFlag':True}
						sport='MPLX3450-football'
					else:
						#Football
						#checkHomeDict={}
						#checkGuestDict={}
						checkGameDict={'segmentQuarterFlag':False, 'quarter':1}
						sport='MPLX3450-baseball'
				elif MPSOCCER_LX1:
					if self.game.gameData['sport']=='MPSOCCER_LX1-soccer':
						#Soccer
						#checkHomeDict={}
						#checkGuestDict={}
						checkGameDict={'bcDetectFlag':True}
						sport='MPSOCCER_LX1-football'
					else:
						#Football
						#checkHomeDict={}
						#checkGuestDict={}
						checkGameDict={'down':0}
						sport='MPSOCCER_LX1-soccer'
									
				#Check for multisport reset state
				if checkGameDict.viewitems() <= self.game.gameData.viewitems():# \
				#and checkHomeDict.viewitems() <= self.game.teamsDict[self.game.home].teamData.viewitems() \
				#and checkGuestDict.viewitems() <= self.game.teamsDict[self.game.guest].teamData.viewitems():

					#Change sport							
					from config_default_settings import Config
					c=Config()							
					c.writeSport(sport)
					
					#Tell console to reset
					self.game.gameSettings['resetGameFlag']=True
						
	def _tunnelCheck(self, word, numericData):
		highData=(numericData&0xf0)>>4
		lowData=numericData&0x0f
		if word==1:
			if (lowData>=0xa and lowData!=0xf) or (highData>=0xa and highData!=0xf):
				return 1
		return 0

	def _getDictInfo(self, addr, ALT=1):
		iBit=self.fullAddressMapDict[addr][ALT]['I_BIT']
		hBit=self.fullAddressMapDict[addr][ALT]['H_BIT']
		lowNibble=self.fullAddressMapDict[addr][ALT]['LOW_NIBBLE']
		highNibble=self.fullAddressMapDict[addr][ALT]['HIGH_NIBBLE']
		segmentData=self.fullAddressMapDict[addr][ALT]['SEGMENT_DATA']

		dataNames=(iBit, hBit, highNibble, lowNibble, segmentData)
		return dataNames

	def _saveData(self, decodeData, dataNames):
		addr, group, bank, word, I_Bit, numericData = decodeData
		iBit, hBit, highNibble, lowNibble, segmentData = dataNames
		#print '\naddr', addr, 'iBit', iBit, 'hBit', hBit
		#print 'highNibble', highNibble, 'lowNibble', lowNibble, 'segmentData', segmentData
		if not self.statFlag and (word==3 or word==4):
			highData=0
			lowData=numericData&0x7f
			lowData=self.mp.numericDataDecode(lowData)
			H_Bit=(numericData&0x80)>>7			
			if segmentData=='':
				hTeam=self._teamExtract(hBit)
				iTeam=self._teamExtract(iBit)
				highTeam=self._teamExtract(highNibble)#may not need
				lowTeam=self._teamExtract(lowNibble)
				
				dataNames = self._checkPeriodClockState(decodeData, dataNames, highData, lowData, H_Bit)
				iBit, hBit, highNibble, lowNibble, segmentData = dataNames		
						
				self._setPeriodClockUnMapDict(iBit, I_Bit)
				self._setPeriodClockUnMapDict(hBit, H_Bit)
				self._setPeriodClockUnMapDict(highNibble, highData)
				self._setPeriodClockUnMapDict(lowNibble, lowData)
				
				#Special cases not to save I Bit --------------------
				if 0:
					#Don't save duplicates
					pass
				else:
					self._setData(iBit, I_Bit, iTeam)
					if self.verbose:
						print 'iBit', iBit, 'saved'
									
				#Special cases not to save H Bit --------------------
				HOCK_27_28= (addr==27 or addr==28) and self.game.gameData['sport']=='MPHOCKEY_LX1'
				SOC_soc_32= addr==32 and self.game.gameData['sport']=='MPSOCCER_LX1-soccer'
				BB4_11= addr==11 and self.game.gameData['sport']=='MMBASEBALL4'
				
				if HOCK_27_28 or BB4_11 or SOC_soc_32:
					#This if statement added to handle error with 401 sending non-matching data to two locations
					#Don't save duplicates
					pass
				else:
					self._setData(hBit, H_Bit, hTeam)
					if self.verbose:
						print 'hBit', hBit, 'saved'
					
				#Special cases not to save High Nibble --------------------
				#self._setData(highNibble, highData, highTeam)  #may not need
				
				#Special cases not to save Low Nibble --------------------
				self._setData(lowNibble, lowData, lowTeam)
				if self.verbose:
					print 'lowNibble', lowNibble, 'saved'

				if self.verbose:
					print 'addr', addr, 'iTeam', iTeam, 'iBit', iBit, I_Bit, \
					'hTeam', hTeam, 'hBit', hBit, H_Bit
					print 'highTeam', highTeam, 'highNibble', highNibble, highData, \
					'lowTeam', lowTeam, 'lowNibble', lowNibble, lowData
			else:
				#decode segment datas storage value
				if self.verbose:
					print 'segmentData', segmentData
				hTeam=self._teamExtract(hBit)

				dataNames = self._checkPeriodClockState(decodeData, dataNames, highData, lowData, H_Bit)
				iBit, hBit, highNibble, lowNibble, segmentData = dataNames
				
				self._setPeriodClockUnMapDict(hBit, H_Bit)
			
				#Special cases not to save H Bit --------------------
				SOC_soc_31= addr==31 and self.game.gameData['sport']=='MPSOCCER_LX1-soccer'
				if SOC_soc_31:
					#Don't save duplicates
					pass
				else:
					self._setData(hBit, H_Bit, hTeam)
					if self.verbose:
						print 'hBit', hBit, 'saved'
					
				#Area for all custom decodeing, try to use data from a better location if possible
				if self.game.gameData['sportType']=='basketball':
					if segmentData=='home_ace_PossBonus':
						if self.verbose:
							print bin(numericData), bin(0b00010000&numericData), 0b00000001&numericData
						if 0b00000001&numericData:
							self._setData('teamTwoPossession', True, self.game.home)
						elif 0b00000001&numericData==0:
							self._setData('teamTwoPossession', False, self.game.home)
						if 0b00010000&numericData:
							self._setData('teamTwoBonus', 2, self.game.home)
						elif 0b00000100&numericData:
							self._setData('teamTwoBonus', 1, self.game.home)
						elif 0b00010000&numericData==0 or 0b00000100&numericData==0:
							self._setData('teamTwoBonus', 0, self.game.home)
					if segmentData=='guest_ace_PossBonus':
						if self.verbose:
							print bin(numericData), 0b00000000&numericData, 0b00000001&numericData
						if 0b00000001&numericData:
							self._setData('teamOnePossession', True, self.game.guest)
						elif 0b00000000&numericData==0:
							self._setData('teamOnePossession', False, self.game.guest)
						if 0b00010000&numericData:
							self._setData('teamOneBonus', 2, self.game.guest)
						elif 0b00000100&numericData:
							self._setData('teamOneBonus', 1, self.game.guest)
						elif 0b00010000&numericData==0 or 0b00000100&numericData==0:
							self._setData('teamOneBonus', 0, self.game.guest)
				elif self.game.gameData['sport']=='MPMULTISPORT1-football' or self.game.gameData['sport']=='MPLX3450-football':
					if segmentData=='Down_Quarter':
						if 0b00010000&numericData:
							self.game.gameData['segmentQuarterFlag']=True
						elif 0b00010000&numericData==0:
							self.game.gameData['segmentQuarterFlag']=False
				elif self.game.gameData['sport']=='MPMULTISPORT1-baseball' or self.game.gameData['sport']=='MPLX3450-baseball':
					if segmentData=='bc_strike' or segmentData=='period_efg':
						if 0b00010000&numericData:
							self.game.gameData['segmentQuarterFlag']=True
						elif 0b00010000&numericData==0:
							self.game.gameData['segmentQuarterFlag']=False		
				elif self.game.gameData['sport']=='MPSOCCER_LX1-soccer':
					if segmentData=='bc_detect':
						if 0b00000110&numericData:
							self.game.gameData['bcDetectFlag']=True
						elif 0b00000110&numericData==0:
							self.game.gameData['bcDetectFlag']=False	

		else:
			#word 1 and word 2
			highData=(numericData&0xf0)>>4
			lowData=numericData&0x0f
			
			iTeam=self._teamExtract(iBit)
			highTeam=self._teamExtract(highNibble)
			lowTeam=self._teamExtract(lowNibble)
			
			dataNames = self._checkPeriodClockState(decodeData, dataNames, highData, lowData)
			iBit, hBit, highNibble, lowNibble, segmentData = dataNames
						
			self._setPeriodClockUnMapDict(iBit, I_Bit)
			self._setPeriodClockUnMapDict(highNibble, highData)
			self._setPeriodClockUnMapDict(lowNibble, lowData)
			
			#Special cases not to save I Bit --------------------
			SOC_soc_18= addr==18 and self.game.gameData['sport']=='MPSOCCER_LX1-soccer'
			MULTIbase3450base= (self.game.gameData['sport']=='MPMULTISPORT1-baseball' or \
			self.game.gameData['sport']=='MPLX3450-baseball')
			LINE5_17_18= (addr==17 or addr==18) and self.game.gameData['sport']=='MPLINESCORE5'
			
			BASE1orBASE3= self.game.gameData['sport']=='MPBASEBALL1' or self.game.gameData['sport']=='MMBASEBALL3'
			_13or14= addr==13 or addr==14
			#Together
			BB13and13_14= BASE1orBASE3 and _13or14
			BB134and13_14= (BASE1orBASE3 or self.game.gameData['sport']=='MMBASEBALL4') and _13or14
			MULTIbase3450baseAnd13_14= MULTIbase3450base and _13or14
						
			if SOC_soc_18 or LINE5_17_18 or BB13and13_14:
				#Don't save duplicates
				pass
			else:
				self._setData(iBit, I_Bit, iTeam)
				if self.verbose:
					print 'iBit', iBit, 'saved'
			
			#Special cases not to save High Nibble ----------------
			SOC_soc_18= addr==18 and self.game.gameData['sport']=='MPSOCCER_LX1-soccer'
			notEjumper= not('E' in self.game.gameData['optionJumpers'])
			#Together
			SOC_soc_18and_notEjumper= SOC_soc_18 and notEjumper
			
			if SOC_soc_18and_notEjumper:
				#Don't save duplicates
				pass
			else:
				self._setData(highNibble, highData, highTeam)	
				if self.verbose:
					print 'highNibble', highNibble, 'saved'

			#Special cases not to save Low Nibble ------------------
			#SOC_soc_18and_notEjumper is above
			#BB134and13_14 is above
			if SOC_soc_18and_notEjumper	or BB134and13_14 or MULTIbase3450baseAnd13_14:
				#Don't save duplicates
				pass
			else:
				self._setData(lowNibble, lowData, lowTeam)
				if self.verbose:
					print 'lowNibble', lowNibble, 'saved'

			if self.verbose:
				print 'addr', addr, 'iTeam', iTeam, 'iBit', iBit, I_Bit
				print 'highTeam', highTeam, 'highNibble', highNibble, highData, \
				'lowTeam', lowTeam, 'lowNibble', lowNibble, lowData
				
	def _setPeriodClockUnMapDict(self, name, value):
		if name in self.periodClockUnMapDict:
			self.periodClockUnMapDict[name]=value
			#print name, self.periodClockUnMapDict[name]		
	
	def _checkPeriodClockState(self, decodeData, dataNames, highData, lowData, H_Bit=None):
		addr, group, bank, word, I_Bit, numericData = decodeData
		iBit, hBit, highNibble, lowNibble, segmentData = dataNames
		LINE5andCjumper= self.game.gameData['sport']=='MPLINESCORE5' and 'C' in self.game.gameData['optionJumpers']
		MULTIbaseOr3450baseCjumper= (self.game.gameData['sport']=='MPMULTISPORT1-baseball' or self.game.gameData['sport']=='MPLX3450-baseball')\
		and 'C' in self.game.gameData['optionJumpers']
		
		#Minutes received
		if highNibble=='minutesTens':
			#print'-minutes State Check'
			pass			
							
		#Seconds received
		elif highNibble=='secondsTens':
			#print'-seconds State Check'
			if lowData==15 or (self.periodClockUnMapDict['secondsTens']==0 and self.periodClockUnMapDict['secondsUnits']==0 \
			and highData>=6 and lowData==0):
				self.tenthsTransitionFlag=True
				dataNames=self._getDictInfo(addr, ALT=2)
				self._setData('minutesTens', 0)
				self._setData('minutesUnits', 0)
				if self.verbose:
					print 'self.tenthsTransitionFlag=True and set minutes to zero'
					print '\naddr', addr, 'iBit', iBit, I_Bit, \
					'hBit', hBit, H_Bit
					print 'highNibble', highNibble, highData, \
					'lowNibble', lowNibble, lowData	
								
			elif (LINE5andCjumper or MULTIbaseOr3450baseCjumper) and (lowData<10 and lowData>=0) and self.tenthsTransitionFlag:
				self.tenthsTransitionFlag=False
				self._setData('tenthsUnits', 0)
				if self.verbose:
					print 'self.tenthsTransitionFlag=False and set tenthsUnits to zero'
					print '\naddr', addr, 'iBit', iBit, I_Bit, \
					'hBit', hBit, H_Bit
					print 'highNibble', highNibble, highData, \
					'lowNibble', lowNibble, lowData			
								
		#Tenths received
		elif highNibble=='tenthsUnits':
			#print'-tenths State Check'
			pass

		#Colon received
		elif hBit=='colonIndicator':
			#print'-colonIndicator State Check'
			if self.periodClockUnMapDict['colonIndicator']==0 and H_Bit==1:
				self.tenthsTransitionFlag=False
				self._setData('tenthsUnits', 0)
				if self.verbose:
					print 'self.tenthsTransitionFlag=False and set tenthsUnits to zero'
					print '\naddr', addr, 'iBit', iBit, I_Bit, \
					'hBit', hBit, H_Bit
					print 'highNibble', highNibble, highData, \
					'lowNibble', lowNibble, lowData								
		
		return dataNames

	def _setData(self, name, value, team=None):
		if self._gameValueCheck(name):
			#print 'GAME'
			self.game.setGameData(name, value, places=1)
		elif self._teamValueCheck(name):
			#print 'TEAM', name, name[:7]
			if name[:7]=='penalty':
				timerNumber=name[7]
				name=self._trimPenalty(name)
				teamString=name[:7]
				name=self._trimTeamName(name)
				if name[:6]=='player':
					place=name[6:]
					self.game.setTeamData(team, 'TIMER'+timerNumber+'_PLAYER_NUMBER'+place, value, places=1)
				elif name[:5]=='colon':
					if self.verbose:
						print 'skip penalty timer colons'
				else:
					clockName='penalty'+str(timerNumber)+'_'+teamString+'_'+name
					if self.verbose:
						print clockName
					self.game.setGameData(clockName, value, places=1)
			else:
				name=self._trimTeamName(name)
				self.game.setTeamData(team, name, value, places=1)
		elif self._periodClockValueCheck(name):
			#print 'CLOCK'
			self.game.setGameData('periodClock_'+name, value, places=1)
		else:
			print 'FAIL'

class Lamptest_Mapping(Address_Mapping):
	"""Map of all non-horn segments on per the sport."""
	def __init__(self, sportType='Generic'):
		super(Lamptest_Mapping, self).__init__(sportType, game=None)

		if self.statFlag:
			for k in range(2):
				for i in range(2):
					for j in range(4):
						self.wordsDict[((i*4+j)*4+1)+k*32] = self.mp.Encode(i+1, j+1, 1, k, 0, 8, 8, 0, 0, True)
						self.wordsDict[((i*4+j)*4+2)+k*32] = self.mp.Encode(i+1, j+1, 2, k, 0, 8, 8, 0, 0, True)
						self.wordsDict[((i*4+j)*4+3)+k*32] = self.mp.Encode(i+1, j+1, 3, k, 0, 8, 8, 0, 0, True)
						self.wordsDict[((i*4+j)*4+4)+k*32] = self.mp.Encode(i+1, j+1, 4, k, 0, 0, 0, 0, 0, True)
		else:
			for i in range(2):
				for j in range(4):
					self.wordsDict[(i*4+j)*4+1] = self.mp.Encode(i+1, j+1, 1, 1, 1, 8, 8, 0, 0)# 0x58 is 88 in decimal for lamp test
					self.wordsDict[(i*4+j)*4+2] = self.mp.Encode(i+1, j+1, 2, 1, 1, 8, 8, 0, 0)
					self.wordsDict[(i*4+j)*4+3] = self.mp.Encode(i+1, j+1, 3, 1, 1, 0, 8, 0, 0)
					self.wordsDict[(i*4+j)*4+4] = self.mp.Encode(i+1, j+1, 4, 1, 1, 0, 8, 0, 0)

		self._adjustAllBanks()

	def _blankMap(self):
		pass

	def _buildAddrMap(self):
		"""pass"""
		pass

	def _adjustAllBanks(self):
		"""Sets all non-horn segments on per the sport."""
		if self.sport=='MPBASEBALL1' or self.sport=='MMBASEBALL3' or self.sport=='MPLINESCORE5':
			self.wordsDict[1] = self.mp.Encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[2] = self.mp.Encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.Encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			#self.wordsDict[5] = self.mp.Encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			#self.wordsDict[6] = self.mp.Encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[8] = self.mp.Encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.Encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.Encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.Encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.Encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.Encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.Encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport=='MPLINESCORE4':
			#self.wordsDict[1] = self.mp.Encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			#self.wordsDict[2] = self.mp.Encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.Encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			#self.wordsDict[5] = self.mp.Encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			#self.wordsDict[6] = self.mp.Encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[8] = self.mp.Encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.Encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.Encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.Encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.Encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[24] = self.mp.Encode(2, 2, 4, 1, 0, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.Encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.Encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport=='MPMP_15X1' or self.sport=='MPMP_14X1':
			self.wordsDict[1] = self.mp.Encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[2] = self.mp.Encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.Encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			#self.wordsDict[5] = self.mp.Encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			#self.wordsDict[6] = self.mp.Encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[8] = self.mp.Encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.Encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.Encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.Encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			#self.wordsDict[21] = self.mp.Encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[24] = self.mp.Encode(2, 2, 4, 1, 0, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.Encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.Encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport=='MPMULTISPORT1-football' or self.sport=='MPLX3450-football' or self.sport=='MPMULTISPORT1-baseball' or self.sport=='MPLX3450-baseball':
			if self.sport=='MPLX3450-football' or self.sport=='MPLX3450-baseball':
				self.wordsDict[1] = self.mp.Encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
				#self.wordsDict[2] = self.mp.Encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			else:
				#self.wordsDict[1] = self.mp.Encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
				self.wordsDict[2] = self.mp.Encode(1, 1, 2, 0, 1, 8, 8, 0, 0)

			#self.wordsDict[4] = self.mp.Encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[5] = self.mp.Encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[6] = self.mp.Encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[8] = self.mp.Encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.Encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			#self.wordsDict[16] = self.mp.Encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.Encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.Encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.Encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.Encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport=='MPFOOTBALL1' or self.sport=='MMFOOTBALL4' or self.sport=='MMBASEBALL4'or self.sport=='MPBASKETBALL1':
			self.wordsDict[1] = self.mp.Encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[2] = self.mp.Encode(1, 1, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.Encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[5] = self.mp.Encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[6] = self.mp.Encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			if  not self.sport=='MPBASKETBALL1':
				self.wordsDict[8] = self.mp.Encode(1, 2, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[12] = self.mp.Encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.Encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[20] = self.mp.Encode(2, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.Encode(2, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[28] = self.mp.Encode(2, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[32] = self.mp.Encode(2, 4, 4, 1, 0, 0, 8, 0, 0)

		elif self.sport=='MPHOCKEY_LX1':
			self.wordsDict[1] = self.mp.Encode(1, 1, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[4] = self.mp.Encode(1, 1, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[5] = self.mp.Encode(1, 2, 1, 0, 1, 8, 8, 0, 0)
			self.wordsDict[6] = self.mp.Encode(1, 2, 2, 0, 1, 8, 8, 0, 0)
			self.wordsDict[12] = self.mp.Encode(1, 3, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[16] = self.mp.Encode(1, 4, 4, 1, 0, 0, 8, 0, 0)
			self.wordsDict[21] = self.mp.Encode(2, 2, 1, 0, 1, 8, 8, 0, 0)

	def Map(self):
		"""pass"""
		pass

	def UnMap(self):
		"""pass"""
		pass

class Blanktest_Mapping(Address_Mapping):
	"""Map of all segements off."""
	def __init__(self, sportType='Generic'):
		super(Blanktest_Mapping, self).__init__(sportType, game=None)

	def _buildAddrMap(self):
		"""pass"""
		pass

	def _adjustAllBanks(self):
		"""pass"""
		pass

	def Map(self):
		"""pass"""
		pass

	def UnMap(self):
		"""pass"""
		pass


def test():
	"""Test function if module ran independently."""
	print "ON"
	c = Config()
	sport = 'MPSTAT'
	c.writeSport(sport)
	game = selectSportInstance(sport)
	addrMap = Address_Mapping(game.gameData['sportType'], game=game)
	elapseTime(addrMap.Map, On=False, Timeit=False)
	
	printDictsExpanded(addrMap, True)
	raw_input()

	"""
	LHword0 = addrMap.mp.Encode(1, 3, 1, 1, 0, 6, 9, 0, 0)
	LHword1 = addrMap.mp.Encode(1, 3, 2, 0, 0, 5, 8, 0, 0)
	LHword2 = addrMap.mp.Encode(1, 3, 3, 1, 0, 0, 5, 0, 0)
	LHword3 = addrMap.mp.Encode(1, 3, 4, 0, 0, 0, 6, 0, 0)
	#LHword4 = addrMap.mp.Encode(2, 3, 4, 1, 0, 0, 0, 0, 'abcd')
	#LHword5 = addrMap.mp.Encode(2, 3, 1, 0, 0, 0, 1, 0, 0)
	#LHword6 = addrMap.mp.Encode(2, 1, 1, 0, 0, 0, 1, 0, 0)
	wordList=[LHword0, LHword1 , LHword2, LHword3]#, LHword4, LHword5, LHword6]
	addrMap.UnMap(addressWordList=[9,10,11,12], wordList=wordList)
	print addrMap.game.getTeamData(game.guest, 'TIMER1_PLAYER_NUMBERTens')

	#raw_input()
	print
	#addrDict=addrMap.__dict__
	#printDict(addrDict)
	#printDictsExpanded(addrMap, True)
	"""


if __name__ == '__main__':
	# from serial_packet_Class import Serial_Packet
	from config_default_settings import Config
	test()
