#!/usr/bin/env python

# by Craig Gunter
#
# "Address_Mapping module"
#
# Address_Mapping()Input = None
#
# 		Map() = Maps key to event
#
#
#			main() =


#	Varibles available /w Defaults
"""




"""

from time import sleep
import sys

from Config import *
from Game import *
from MP_Data_Handler import *
from Driver import *

class Address_Mapping(object):

	def __init__(self, game):

		self.mp = MP_Data_Handler()
		self.lx = LX_Driver('LX22')

		seq = range(1,33)
		self.wordsDict = dict.fromkeys(seq, 0)
		self.lastWordsDict = {}

		self.blankMap()

		self.lastWordsDict.update(self.wordsDict)

		self.addrWordNamesDict={}
		self.addrWordNamesALTSDict={}

		self.buildAddrFuncDict()
		self.buildAddrMap(game)

	def blankMap(self):
		#Build blank MP wordsDict
		for i in range(2):
			for j in range(4):
				self.wordsDict[(i*4+j)*4+1] = self.mp.Encode(i+1, j+1, 1, 0, 0, 'BCD', 0x0, 2, 0, 0)
				self.wordsDict[(i*4+j)*4+2] = self.mp.Encode(i+1, j+1, 2, 0, 0, 'BCD', 0x0, 2, 0, 0)
				self.wordsDict[(i*4+j)*4+3] = self.mp.Encode(i+1, j+1, 3, 0, 0, 'segment', 0, 0, 0, '')
				self.wordsDict[(i*4+j)*4+4] = self.mp.Encode(i+1, j+1, 4, 1, 0, 'segment', 0, 0, 0, '')

	def buildAddrFuncDict(self):
		#All games
		self.addrFuncDict = {'guestScorePlusTen':self._guestScore, 'guestScorePlusOne':self._guestScore,'homeScorePlusTen':self._homeScore,\
		'homeScorePlusOne':self._homeScore,'secondsMinusOne':self._clock,'possession':self._possession,'horn':self.Horn,\
		'minutesMinusOne':self._clock, 'periodClockReset':self._clock, 'periodClockOnOff':self._clock,'secondsPlusOne':self._clock}

			#Number pad - no nothing--------------------------------------------------------------
		self.addrFuncDict.update({'Number_7_ABC':self.doNothing, 'Number_8_DEF':self.doNothing, 'Number_9_GHI':self.doNothing, \
		'Number_5_MNO':self.doNothing, 'Number_6_PQR':self.doNothing,  'Number_1_STU':self.doNothing, \
		'Number_2_VWX':self.doNothing, 'Number_3_YZ':self.doNothing,'Number_4_JKL':self.doNothing,'Number_0_&-.!':self.doNothing,\
		'clear':self.doNothing, 'enter':self.doNothing, 'clear_FlashHit':self.doNothing,'enter_FlashError':self.doNothing})

			#All games - no nothing--------------------------------------------------------------
		self.addrFuncDict.update({'blank':self.doNothing,'None':self.doNothing, '':self.doNothing,\
		'NewGame':self.doNothing,'setClock':self.doNothing, 'setClockTenthSec':self.doNothing, \
		'autoHorn':self.doNothing, 'timeOfDay':self.doNothing, 'timeOutTimer':self.doNothing, \
		'setHomeScore':self.doNothing,'setGuestScore':self.doNothing,'clockUpDown':self.doNothing,\
		'playClocks':self.doNothing, 'shotClocks':self.doNothing,'tenthSecOnOff':self.doNothing})

		#hockey and soccer
		self.addrFuncDict.update({'guestShotsPlusOne':self._Shots,'homeShotsPlusOne':self._Shots,'qtrs_periodsPlusOne':self._qtrs_periods,\
		'guestPenaltyPlusOne':self._Penalty, 'homePenaltyPlusOne':self._Penalty,\
		'guestKicksPlusOne':self._Kicks,'homeKicksPlusOne':self._Kicks,\
		'guestSavesPlusOne':self._Saves,'homeSavesPlusOne':self._Saves})

			#hockey no nothing--------------------------------------------------------------
		self.addrFuncDict.update({'clear_GuestGoal':self.doNothing,'enter_HomeGoal':self.doNothing,'play_shotClocks':self.doNothing,\
		'setGuestFunctions':self.doNothing, 'setHomeFunctions':self.doNothing,\
		'guestPenalty':self.doNothing, 'homePenalty':self.doNothing,})

			#soccer no nothing--------------------------------------------------------------
		self.addrFuncDict.update({'setGuestFunctions':self.doNothing, 'setHomeFunctions':self.doNothing, \
		'play_shotClocks':self.doNothing,'clear_GuestGoal':self.doNothing,'enter_HomeGoal':self.doNothing})

		#basketball
		self.addrFuncDict.update({'guestTeamFoulsPlusOne':self._Fouls, 'homeTeamFoulsPlusOne':self._Fouls, \
		'homeBonus':self._Bonus,'guestBonus':self._Bonus,'qtrs_periodsPlusOne':self._qtrs_periods})

			#no nothing--------------------------------------------------------------
		self.addrFuncDict.update({ 'playerMatchGame':self.doNothing, 'playerFoul':self.doNothing,\
		'setHomeTimeOuts':self.doNothing,'setGuestTimeOuts':self.doNothing})

		#football
		self.addrFuncDict.update({'yardsToGoReset':self._YardsToGo,'yardsToGoMinusOne':self._YardsToGo,'yardsToGoMinusTen':self._YardsToGo,\
		'guestTimeOutsMinusOne':self._TimeOuts,'homeTimeOutsMinusOne':self._TimeOuts,'downsPlusOne':self._Downs,\
		'qtrs_periodsPlusOne':self._qtrs_periods,'quartersPlusOne':self._qtrs_periods,})

			#no nothing--------------------------------------------------------------
		self.addrFuncDict.update({'setYardsToGo':self.doNothing, 'setBallOn':self.doNothing})

		#baseball
		self.addrFuncDict.update({'ballsPlusOne':self._balls,'homePitchesPlusOne':self._pitchCount,'singlePitchesPlusOne':self._pitchCount,\
		'strikesPlusOne':self._strikes, 'outsPlusOne':self._outs, 'inningsPlusOne':self._innings,'teamAtBat':self._teamAtBat, \
		'guestPitchesPlusOne':self._pitchCount,'incInningTop_Bot':self._innings, 'runsPlusOne':self._runsPlusOne,'hitsPlusOne':self._hitsPlusOne,\
		'flashHitIndicator':self._flashHitIndicator,'flashErrorIndicator':self._flashErrorIndicator,'errorsPlusOne':self._errorsPlusOne})

			#no nothing--------------------------------------------------------------
		self.addrFuncDict.update({'setPitchCounts':self.doNothing,'setBatterNumber':self.doNothing,'clear_FlashHit':self.doNothing,\
		'enter_FlashError':self.doNothing,'assignError':self.doNothing,'setTotalRuns':self.doNothing,'setTotalHits':self.doNothing,\
		'setTotalErrors':self.doNothing, 'setRuns_Innings':self.doNothing,'setInningTop_Bot':self.doNothing})

		#stat
		self.addrFuncDict.update({'fouls_digsMinusOne':self._fouls_digs, 'fouls_digsPlusOne':self._fouls_digs,\
		'points_killsMinusOne':self._points_kills, 'points_killsPlusOne':self._points_kills})

			#no nothing--------------------------------------------------------------
		self.addrFuncDict.update({'addPlayer':self.doNothing, 'deletePlayer':self.doNothing, 'displaySize':self.doNothing, \
		'editPlayer':self.doNothing,'nextPlayer':self.doNothing,'subPlayer':self.doNothing,'previousPlayer':self.doNothing})

	def buildAddrMap(self, game):
		self.addrWordNamesALTSDict.clear()
		self.addrWordNamesDict.clear()
		self.addressMapDict = self.readAddressMap(game)
		for key in self.addressMapDict.keys():
			if key[-3:]=='Alt':
				addrWordNumber=int(self.addressMapDict[key]['ADDRESS_WORD_NUMBER'])
				self.addrWordNamesALTSDict[addrWordNumber]=key
			else:
				addrWordNumber=int(self.addressMapDict[key]['ADDRESS_WORD_NUMBER'])
				self.addrWordNamesDict[addrWordNumber]=key
		self.Initialize_Legacy_Display(game)
		return

	def readAddressMap(self, game):
		AddressMap='Spreadsheets/AddressMap.csv'
		csvReader=csv.DictReader(open(AddressMap, 'rb'), delimiter=',', quotechar="'")
		value=[]
		dictionaryName = {}
		realSport=game.sport
		#print realSport
		for row in csvReader:
			try:
				sport=row['SPORT']
				#print '\nsport\n', sport
				if sport==realSport:
					value=row.values()
					dictName=sport+row['SPORT_NAME']+row['DICTIONARY_NAME']
					#print '\ndictName\n', dictName
					del row['DICTIONARY_NAME']
					del row['SPORT']

					dictionaryName[dictName]=row
					#print '\ndictionaryName\n', dictionaryName.keys()
					#raw_input()
				else:
					#raw_input()
					pass

			except ValueError:
				#print '\npass\n'
				#raw_input()
				pass
		#print
		return dictionaryName

	def _updateAddrWords(self, game, Regs=range(1,33), Alts=[], Flag=False):
		#game + No arguments = all addresses regular
		#game + Just Reg builds only the regulars
		#All arguments builds a combination of Regs and Alts
		addrWordNames=[]
		if Flag:
			for number in Alts:
				addrWordNames.append(self.addrWordNamesALTSDict[number])#Alts
			for number in list(set(Regs)- set(Alts)):
				addrWordNames.append(self.addrWordNamesDict[number])#Left over Regs
		else:
			for number in Regs:
				addrWordNames.append(self.addrWordNamesDict[number])#All Regs

		for addrWordName in addrWordNames:
			addrWordNumber, group, bank, word, iBit, hBit, dataType, numericData, blank, placeHold, segmentData = self._loadFromAddDict(game, addrWordName)
			self.wordsDict[addrWordNumber]=self.mp.Encode(group, bank, word, iBit, hBit, dataType, numericData, blank, placeHold, segmentData)

		self.checkWords()

	def _loadFromAddDict(self, game, addrWordName):
		''' Get word info and prepare it for encoding '''
		addrWordNumber=int(self.addressMapDict[addrWordName]['ADDRESS_WORD_NUMBER'])
		group=int(self.addressMapDict[addrWordName]['GROUP'])
		word=int(self.addressMapDict[addrWordName]['WORD'])
		bank=int(self.addressMapDict[addrWordName]['BANK'])
		iBit=self.addressMapDict[addrWordName]['I_BIT']
		hBit=self.addressMapDict[addrWordName]['H_BIT']
		numericData=self.addressMapDict[addrWordName]['NUMERIC_DATA']
		highNibble=self.addressMapDict[addrWordName]['HIGH_NIBBLE']
		lowNibble=self.addressMapDict[addrWordName]['LOW_NIBBLE']
		dataType=self.addressMapDict[addrWordName]['DATA_TYPE']
		blank=int(self.addressMapDict[addrWordName]['BLANKIFZERO'])
		placeHold=int(self.addressMapDict[addrWordName]['PLACEHOLDER'])
		segmentData=self.addressMapDict[addrWordName]['SEGMENT_DATA']

		#Format data - iBit
		if iBit=='0'or iBit=='':
			iBit=0
		elif iBit=='1' or iBit=='active':
			iBit=1
		else:
			iBit=vars(game)[iBit]

		#Format data - hBit
		if hBit=='0'or hBit=='':
			hBit=0
		elif hBit=='1':
			hBit=1
		else:
			hBit=vars(game)[hBit]

		#Format data - numericData
		#print 'numericData before:', numericData
		if numericData=='' or numericData=='0':
			numericData=0
		elif numericData=='blank':
			numericData=0
			blank=2
		elif numericData=='minutes' or numericData=='seconds' or numericData=='hoursUnits' or numericData=='tenthsUnits' \
		or numericData=='minutesUnits'or numericData=='minutesTens'or numericData=='secondsUnits'or numericData=='secondsTens':
			numericData=vars(game.periodClock)[numericData]
		else:
			numericData=vars(game)[numericData]

		if highNibble=='' and lowNibble=='':
			pass
		elif highNibble=='tenthsUnits' and lowNibble=='blank':
			highNibble=(vars(game.periodClock)[highNibble])*10
			lowNibble=0
			blank=4
			numericData=highNibble+lowNibble
		elif lowNibble=='blank':
			highNibble=(vars(game)[highNibble])*10
			lowNibble=0
			blank=4
			numericData=highNibble+lowNibble
		else:
			highNibble=(vars(game)[highNibble])*10
			lowNibble=vars(game)[lowNibble]
			numericData=highNibble+lowNibble
		if numericData>=255:
			numericData=0
			blank=2

		#Special Blanking
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			if game.innings==0 and addrWordNumber==27:
				blank=2
				print'Blankinning'
		#print 'numericData after:', numericData

		#Format data - segmentData
		#print 'segmentData before:', segmentData
		if segmentData=='' or segmentData=='0':
			segmentData=0
		elif segmentData=='BSO':
			segmentData=self._BSODecode(game)
		elif segmentData=='Down_Quarter':
			segmentData=self._DownQuarterDecode(game)
		elif segmentData=='fQtr4_gDec':
			if game.decimalIndicator:
				segmentData='g'
			else:
				segmentData=''
			if game.quarters==4:
				segmentData+='f'
			else:
				segmentData+=''
		elif segmentData=='gDec':
			if game.decimalIndicator:
				segmentData='g'
			else:
				segmentData=''
		elif segmentData=='f_hitIndicator':
			if game.hitIndicator:
				segmentData='f'
			else:
				segmentData=''
		#print 'segmentData after:', segmentData

		return addrWordNumber, group, bank, word, iBit, hBit, dataType, numericData, blank, placeHold, segmentData

#G1		B1=1,2,3,4		B2=5,6,7,8 		B3=9,10,11,12, 		B4=13,14,15,16
#G2		B1=17,18,19,20 	B2=21,22,23,24 	B3=25,26,27,28 		B4=29,30,31,32

	def Initialize_Legacy_Display(self, game):
		print '\n-------Initialize_Legacy_Display-------\n'
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.clock_3D_or_less_Flag
			Regs = [1, 2, 3, 4, 21, 22, 23, 24]
			Alts = [1, 2, 21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)

			Flag = game.scoreTo19Flag
			Regs = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 26, 27, 28, 29, 30, 31, 32]
			Alts = [5, 6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 28, 29, 30, 31, 32]
			self._updateAddrWords(game, Regs, Alts, Flag)

		elif game.sport=='MPLINESCORE5':
			Flag = game.clock_3D_or_less_Flag
			Regs = [21, 22, 23, 24]
			Alts = [21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)

			Flag = game.pitchSpeedFlag
			Regs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 26, 27, 28, 29, 30, 31, 32]
			Alts = [5]
			self._updateAddrWords(game, Regs, Alts, Flag)

		elif game.sport=='MPLINESCORE4':
			Flag = game.tenthsFlag
			Regs = [21, 22, 23, 24]
			Alts = [21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)

			Regs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 26, 27, 28, 29, 30, 31, 32]
			self._updateAddrWords(game, Regs)

		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1' or game.sport=='MMBASEBALL4':
			self._updateAddrWords(game)

		elif game.sport=='MPMULTISPORT1':
			Flag = game.tenthsFlag
			Regs = range(1,33)
			Alts = [6, 7, 8, 21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)

		elif game.sport=='MPLX3450':
			Flag = game.tenthsFlag
			Regs = range(1,33)
			Alts = [6, 7, 8]
			self._updateAddrWords(game, Regs, Alts, Flag)

		elif game.sport=='MPFOOTBALL1' or game.sport=='MMFOOTBALL4' or game.sport=='MPBASKETBALL1':
			Flag = game.tenthsFlag
			Regs = range(1,33)
			Alts = [1, 2, 6, 7, 8, 21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)

	def checkWords(self):
		self.sendList = []
		for address in self.wordsDict:
			#print address
			#print self.lastWordsDict[address]
			#print self.wordsDict[address]
			if (self.wordsDict[address] != self.lastWordsDict[address]):
				print "Changed and sent Word #%2d" % address

				self.sendList.append(self.wordsDict[address])
			self.lastWordsDict[address] = self.wordsDict[address]
		print 'sendList = ', self.sendList
		#self.lx.receive(self.sendList)

	def Map(self, funcString, game):
		self.Initialize_Legacy_Display(game)
		#self.addrFuncDict[funcString](game)# map game data to words dictionary
		return

	def doNothing(self, game):
		return

	#All games----------------------------
	def _guestScore(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [6, 10, 26]
			Alts = Regs
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5':
			Regs = [17, 25, 26, 27, 28, 29, 30]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [9]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [9, 17, 18, 19, 20, 25, 26, 27, 28]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPFOOTBALL1':
			Regs = [10, 26]
			self._updateAddrWords(game, Regs)

	def _homeScore(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [5, 9, 25]
			Alts = Regs
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5':
			Regs = [1, 9, 10, 11, 12, 13, 14]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [1]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [13, 21, 22, 23, 24, 29, 30, 31, 32]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPFOOTBALL1':
			Regs = [9, 25]
			self._updateAddrWords(game, Regs)

	def _clock(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.clock_3D_or_less_Flag
			Regs = [1, 2, 3, 4, 21, 22, 23, 24]
			Alts = [1, 2, 21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5' or game.sport=='MPLINESCORE4':
			Flag = game.tenthsFlag
			Regs = [21, 22, 23, 24]
			Alts = [21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [1, 2, 3, 4]
			self._updateAddrWords(game, Regs)
		if game.sport=='MPFOOTBALL1':
			Flag = game.tenthsFlag
			Regs = [1, 2, 3, 4, 6, 7, 8, 21, 22, 23, 24]
			Alts = [1, 2, 6, 7, 8, 21, 22]
			self._updateAddrWords(game, Regs, Alts, Flag)

#G1		B1=1,2,3,4		B2=5,6,7,8 		B3=9,10,11,12, 		B4=13,14,15,16
#G2		B1=17,18,19,20 	B2=21,22,23,24 	B3=25,26,27,28 		B4=29,30,31,32

	def _possession(self, game):
		pass

	def Horn(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Regs = [1, 2, 21, 22]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE5' or game.sport=='MPLINESCORE4':
			Regs = [21, 22]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [1, 2]
			self._updateAddrWords(game, Regs)
		if game.sport=='MPFOOTBALL1':
			Regs = [1, 2, 6, 7, 8, 21, 22]
			self._updateAddrWords(game, Regs)
	#All games---------END----------------

	#Hockey-------------------------------
	def _Shots(self, game):
		pass
	def _Penalty(self, game):
		pass
	def _Kicks(self, game):
		pass
	def _Saves(self, game):
		pass
	def _qtrs_periods(self, game):
		pass
	#Hockey------------END----------------

	#Soccer-------------------------------
	#Soccer------------END----------------

	#Basketball---------------------------
	def _Fouls(self, game):
		pass

	def _Bonus(self, game):
		pass
	#Basketball--------END----------------

	#Football-----------------------------
	def _YardsToGo(self, game):
		pass
	def _TimeOuts(self, game):
		pass
	def _Downs(self, game):
		pass
	#Football----------END----------------

	#Baseball-----------------------------
	def _pitchCount(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Regs = [17, 18, 19, 20]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE5':
			Flag = game.doublePitchCountFlag
			Regs = [14, 15, 16, 31, 32]
			Alts = [14, 15, 16]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE4':
			Regs = [17, 18, 19, 20]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_14X1':
			Regs = [25, 26]
			self._updateAddrWords(game, Regs)

	def _flashHitIndicator(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [7, 11, 13, 27, 28]
			Alts = [7, 11, 27, 28]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5':
			Regs = [5, 17]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [5, 11, 13]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [5]
			self._updateAddrWords(game, Regs)

	def _hitsPlusOne(self, game):
		if game.sport=='MPLINESCORE5':
			Regs = [2, 5, 17, 18]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [2, 5, 10, 11, 13]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [5, 11, 15]
			self._updateAddrWords(game, Regs)

#G1		B1=1,2,3,4		B2=5,6,7,8 		B3=9,10,11,12, 		B4=13,14,15,16
#G2		B1=17,18,19,20 	B2=21,22,23,24 	B3=25,26,27,28 		B4=29,30,31,32

	def _flashErrorIndicator(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [6, 7, 10, 11, 14, 26, 27]
			Alts = [6, 7, 10, 11, 26, 27]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5':
			Regs = [6, 18]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [6, 11, 14]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [6]
			self._updateAddrWords(game, Regs)

	def _errorsPlusOne(self, game):
		if game.sport=='MPLINESCORE5':
			Regs = [4, 6, 18, 20]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [4, 6, 11, 12, 14]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [6, 11, 15]
			self._updateAddrWords(game, Regs)

	def _runsPlusOne(self, game):
		if game.inningTop:
			self._guestScore(game)
		else:
			self._homeScore(game)

	def _teamAtBat(self, game):
		pass

	def _balls(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [7, 8, 11, 12, 13, 15, 16, 27, 28]
			Alts = [7, 8, 11, 12, 27, 28]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5':
			Regs = [6, 19]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [6, 14]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [6]
			self._updateAddrWords(game, Regs)

	def _strikes(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [7, 8, 11, 12, 13, 16, 27, 28]
			Alts = [7, 8, 11, 12, 27, 28]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5':
			Regs = [6, 19]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [6, 14]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [6]
			self._updateAddrWords(game, Regs)

	def _outs(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [7, 8, 11, 12, 14, 16, 27, 28]
			Alts = [7, 8, 11, 12, 27, 28]
			self._updateAddrWords(game, Regs, Alts, Flag)
		elif game.sport=='MPLINESCORE5':
			Regs = [7, 19]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPLINESCORE4':
			Regs = [7, 15]
			self._updateAddrWords(game, Regs)
		elif game.sport=='MPMP_15X1' or game.sport=='MPMP_14X1':
			Regs = [7]
			self._updateAddrWords(game, Regs)

#G1		B1=1,2,3,4		B2=5,6,7,8 		B3=9,10,11,12, 		B4=13,14,15,16
#G2		B1=17,18,19,20 	B2=21,22,23,24 	B3=25,26,27,28 		B4=29,30,31,32

	def _innings(self, game):
		if game.sport=='MPBASEBALL1' or game.sport=='MMBASEBALL3':
			Flag = game.scoreTo19Flag
			Regs = [5, 6, 7, 9, 10, 11, 25, 26, 27]
			Alts = Regs
			self._updateAddrWords(game, Regs, Alts, Flag)
		if game.sport=='MPLINESCORE5' or game.sport=='MPLINESCORE4' or game.sport=='MPMP_14X1':
			if game.sport=='MPMP_14X1':
				Regs = [17]
			else:
				Regs = [3]
			self._updateAddrWords(game, Regs)
	#Baseball----------END----------------

	#Stat---------------------------------
	def _fouls_digs(self, game):
		pass

	def _points_kills(self, game):
		pass
	#Stat--------------END----------------

	#Segment Decode Functions
	def _BSODecode(self, game):
		segmentData=''

		if game.balls==0:
			pass
		elif game.balls==1:
			segmentData='a'
		elif game.balls==2:
			segmentData='ab'
		elif game.balls==3:
			segmentData='abc'
		if game.strikes==0:
			pass
		elif game.strikes==1:
			segmentData+='d'
		elif game.strikes==2:
			segmentData+='de'
		if game.outs==0:
			pass
		elif game.outs==1:
			segmentData+='f'
		elif game.outs==2:
			segmentData+='fg'
		return segmentData

	def _DownQuarterDecode(self, game):
		segmentData=''

		if game.downs==0:
			pass
		elif game.downs==1:
			segmentData='a'
		elif game.downs==2:
			segmentData='ab'
		elif game.downs==3:
			segmentData='abc'
		elif game.downs==4:
			segmentData='abcd'
		if game.quarters==0:
			pass
		elif game.quarters==1:
			segmentData+='e'
		elif game.quarters==2:
			segmentData+='ef'
		elif game.quarters==2:
			segmentData+='efg'
		return segmentData

class Lamptest_Mapping(Address_Mapping):
	def __init__(self, game):
		super(Lamptest_Mapping, self).__init__(game)

		for i in range(2):
			for j in range(4):
				self.wordsDict[(i*4+j)*4+1] = self.mp.Encode(i+1, j+1, 1, 0, 0, 'BCD', 0x58, 0, 0, 0)# 0x58 is 88 in decimal for lamp test
				self.wordsDict[(i*4+j)*4+2] = self.mp.Encode(i+1, j+1, 2, 0, 0, 'BCD', 0x58, 0, 0, 0)
				self.wordsDict[(i*4+j)*4+3] = self.mp.Encode(i+1, j+1, 3, 0, 0, 'segment', 0, 0, 0, 'abcdefg')
				self.wordsDict[(i*4+j)*4+4] = self.mp.Encode(i+1, j+1, 4, 1, 0, 'segment', 0, 0, 0, 'abcdefg')
		#print self.wordsDict
		#need h segment fix with horn map

	def blankMap(self):
		pass

	def buildAddrMap(self, game):
		del self.addrWordNamesALTSDict
		del self.addrWordNamesDict
		del self.addrFuncDict

class Blanktest_Mapping(Address_Mapping):
	def __init__(self, game):
		super(Blanktest_Mapping, self).__init__(game)

	def buildAddrMap(self, game):
		del self.addrWordNamesALTSDict
		del self.addrWordNamesDict
		del self.addrFuncDict

def main():
	print "ON"
	c=Config()
	sport='MPBASEBALL1'
	c.writeSport(sport)
	game = selectSportInstance(sport)

	addrMap=Address_Mapping(game)
	addrDict=addrMap.__dict__
	#printDict(addrDict)

	raw_input()
	game.homeScore=15
	game.inningsTens=1
	gameDict=game.__dict__
	printDict(gameDict)
	raw_input()
	print '\n    -------homeScore'
	addrMap._homeScore(game)
	#raw_input()
	#print '\n     ------clock'
	#addrMap._clock(game)



if __name__ == '__main__':
	main()
