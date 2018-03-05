#!/usr/bin/env python

# by Craig Gunter
#
# "Keypad_Mapping module"
#
# Keypad_Mapping()Input = None
#
# 		Map() = Maps key to event
#
#
#			main() =


#	Varibles available /w Defaults
"""




"""
from time import sleep

from Config import *
from Game import *
#from Keypad_Mapping_Rules import Keypad_Mapping_Rules
from Address_Mapping import Address_Mapping

class Keypad_Mapping(object):

	def __init__(self, game, reverseHomeAndGuest=False, keypad3150=False, MMBasketball=False):

		self.funcString = ''
		#self.keyRules = Keypad_Mapping_Rules(game)
		self.reverseHomeAndGuest=reverseHomeAndGuest
		self.keypad3150 = keypad3150
		self.MMBasketball = MMBasketball

		self.gameFuncDict = {'guestScorePlusTen':game.guestScorePlusTen, 'guestScorePlusOne':game.guestScorePlusOne, 'NewGame':game.NewGame, \
		'homeScorePlusTen':game.homeScorePlusTen, 'homeScorePlusOne':game.homeScorePlusOne, 'secondsMinusOne':game.secondsMinusOne,  \
		'minutesMinusOne':game.minutesMinusOne, 'periodClockReset':game.periodClockReset, 'periodClockOnOff':game.periodClockOnOff, \
		'setClock':game.setClock, 'setClockTenthSec':game.setClockTenthSec, 'tenthSecOnOff':game.tenthSecOnOff, 'clockUpDown':game.clockUpDown, \
		'autoHorn':game.autoHorn, 'timeOfDay':game.timeOfDay, 'timeOutTimer':game.timeOutTimer, 'possession':game.possession,\
		'secondsPlusOne':game.secondsPlusOne,  'horn':game.Horn,'setHomeScore':game.setHomeScore,'setGuestScore':game.setGuestScore, \
		'playClocks':game.playClocks, 'shotClocks':game.shotClocks,'blank':game.blank,'None':game.blank, '':game.blank}

		self.gameFuncDict.update({'Number_7_ABC':game.Number_7_ABC, 'Number_8_DEF':game.Number_8_DEF, 'Number_9_GHI':game.Number_9_GHI, \
		'Number_5_MNO':game.Number_5_MNO, 'Number_6_PQR':game.Number_6_PQR,  'Number_1_STU':game.Number_1_STU, \
		'Number_2_VWX':game.Number_2_VWX, 'Number_3_YZ':game.Number_3_YZ,'Number_4_JKL':game.Number_4_JKL,'Number_0_&-.!':game.Number_0,\
		'clear':game.clear_, 'enter':game.enter_, 'clear_GuestGoal':game.clear_,'enter_HomeGoal':game.enter_,\
		'clear_FlashHit':game.clear_,'enter_FlashError':game.enter_})

		if game.sportType=='hockey':
			self.gameFuncDict.update({'clear_GuestGoal':game.clear_GuestGoal,'enter_HomeGoal':game.enter_HomeGoal,\
			'setGuestFunctions':game.setGuestFunctions, 'setHomeFunctions':game.setHomeFunctions,\
			'guestShotsPlusOne':game.guestShotsPlusOne,'homeShotsPlusOne':game.homeShotsPlusOne, \
			'play_shotClocks':game.shotClocks,'qtrs_periodsPlusOne':game.periodsPlusOne,\
			'guestPenaltyPlusOne':game.blank, 'homePenaltyPlusOne':game.blank,\
			'guestKicksPlusOne':game.blank,'homeKicksPlusOne':game.blank,\
			'guestSavesPlusOne':game.blank,'homeSavesPlusOne':game.blank,\
			'guestPenalty':game.guestPenalty, 'homePenalty':game.homePenalty,})

		if game.sportType=='soccer':
			self.gameFuncDict.update({'guestKicksPlusOne':game.guestKicksPlusOne,'homeKicksPlusOne':game.homeKicksPlusOne,\
			'guestSavesPlusOne':game.guestSavesPlusOne,'homeSavesPlusOne':game.homeSavesPlusOne,\
			'setGuestFunctions':game.setGuestFunctions, 'setHomeFunctions':game.setHomeFunctions, \
			'guestShotsPlusOne':game.guestShotsPlusOne,'homeShotsPlusOne':game.homeShotsPlusOne, \
			'play_shotClocks':game.playClocks,'qtrs_periodsPlusOne':game.periodsPlusOne,\
			'guestPenaltyPlusOne':game.guestPenaltyPlusOne, 'homePenaltyPlusOne':game.homePenaltyPlusOne,\
			'clear_GuestGoal':game.clear_GuestGoal,'enter_HomeGoal':game.enter_HomeGoal})

		if game.sportType=='basketball':
			self.gameFuncDict.update({'guestTeamFoulsPlusOne':game.guestTeamFoulsPlusOne, 'homeTeamFoulsPlusOne':game.homeTeamFoulsPlusOne, \
			'homeBonus':game.homeBonus_, 'playerMatchGame':game.playerMatchGame, 'playerFoul':game.playerFoul,\
			'guestBonus':game.guestBonus_,'setHomeTimeOuts':game.setHomeTimeOuts,'setGuestTimeOuts':game.setGuestTimeOuts,\
			'qtrs_periodsPlusOne':game.periodsPlusOne,})

		if game.sportType=='football':
			self.gameFuncDict.update({'setYardsToGo':game.setYardsToGo, 'setBallOn':game.setBallOn,'yardsToGoReset':game.yardsToGoReset, \
			'yardsToGoMinusOne':game.yardsToGoMinusOne,'yardsToGoMinusTen':game.yardsToGoMinusTen,'downsPlusOne':game.downsPlusOne,\
			'guestTimeOutsMinusOne':game.guestTimeOutsMinusOne,'homeTimeOutsMinusOne':game.homeTimeOutsMinusOne, 'qtrs_periodsPlusOne':game.quartersPlusOne,\
			'quartersPlusOne':game.quartersPlusOne,})

		if game.sportType=='baseball' or game.sportType=='linescore':
			self.gameFuncDict.update({'flashHitIndicator':game.flashHitIndicator,'flashErrorIndicator':game.flashErrorIndicator, 'ballsPlusOne':game.ballsPlusOne, \
			'strikesPlusOne':game.strikesPlusOne, 'outsPlusOne':game.outsPlusOne, 'inningsPlusOne':game.inningsPlusOne,'teamAtBat':game.teamAtBat, \
			'setPitchCounts':game.setPitchCounts,'setBatterNumber':game.setBatterNumber,'guestPitchesPlusOne':game.guestPitchesPlusOne, \
			'homePitchesPlusOne':game.homePitchesPlusOne, 'clear_FlashHit':game.clear_FlashHit,'enter_FlashError':game.enter_FlashError, \
			'assignError':game.assignError,'singlePitchesPlusOne':game.singlePitchesPlusOne, 'setTotalRuns':game.setTotalRuns, 'setTotalHits':game.setTotalHits, \
			'setTotalErrors':game.setTotalErrors, 'setRuns_Innings':game.setRuns_Innings, 'incInningTop_Bot':game.incInningTop_Bot, 'runsPlusOne':game.runsPlusOne, \
			'hitsPlusOne':game.hitsPlusOne, 'errorsPlusOne':game.errorsPlusOne, 'setInningTop_Bot':game.setInningTop_Bot})

		if game.sportType=='stat':
			self.gameFuncDict.update({'addPlayer':game.addPlayer, 'deletePlayer':game.deletePlayer, 'displaySize':game.displaySize, 'editPlayer':game.editPlayer, \
			'fouls_digsMinusOne':game.fouls_digsMinusOne, 'fouls_digsPlusOne':game.fouls_digsPlusOne, 'nextPlayer':game.nextPlayer, 'subPlayer':game.subPlayer, \
			'points_killsMinusOne':game.points_killsMinusOne, 'points_killsPlusOne':game.points_killsPlusOne, 'previousPlayer':game.previousPlayer})

		if game.sportType=='cricket':
			self.gameFuncDict.update({'setPlayer1Number':game.setPlayer1Number, 'setPlayer2Number':game.setPlayer2Number, 'setPlayer1Score':game.setPlayer1Score, \
			'setPlayer2Score':game.setPlayer2Score, 'setTotalScore':game.setTotalScore, 'setOvers':game.setOvers, 'setLastMan':game.setLastMan, \
			'setLastWicket':game.setLastWicket, 'set1eInnings':game.set1eInnings, 'oversPlusOne':game.oversPlusOne, 'player1ScorePlusOne':game.player1ScorePlusOne, \
			'player2ScorePlusOne':game.player2ScorePlusOne, 'wicketsPlusOne':game.wicketsPlusOne})

		AllKeypad_Keys = self.readMP_Keypad_Layouts()
		self.selectKeypad(game, AllKeypad_Keys)
		tmp=self.Keypad_Keys.values()
		tmp.sort()
		print tmp

	def readMP_Keypad_Layouts(self):
		MP_Keypad_Layouts='Spreadsheets/MP_Keypad_Layouts.csv'
		csvReader=csv.DictReader(open(MP_Keypad_Layouts, 'rb'), delimiter=',', quotechar="'")
		keypad=[]
		dictionary = {}
		count=0
		for row in csvReader:
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
				#print dictionary

			except ValueError:
				print 'error'
			count+=1
		return dictionary

	def selectKeypad(self, game, AllKeypad_Keys):#update with MPCRICKET1, MPRACETRACK1, STAT keypads
		self.Keypad_Keys={}
		sportList = ['MMBASEBALL3','MPBASEBALL1','MMBASEBALL4','MPLINESCORE4','MPLINESCORE5',\
		'MPMP-15X1','MPMP-14X1','MPMULTISPORT1-baseball','MPMULTISPORT1-football', 'MPFOOTBALL1','MMFOOTBALL4','MPBASKETBALL1', \
		'MPSOCCER_LX1-soccer','MPSOCCER_LX1-football','MPSOCCER1','MPHOCKEY_LX1','MPHOCKEY1','MPCRICKET1','MPRACETRACK1','MPLX3450-baseball','MPLX3450-football','MPGENERIC', 'MPSTAT']
		position = sportList.index(game.sport)
		if position==0:#MMBASEBALL3
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MM_BASEBALL_H_G_CX4']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MM_BASEBALL_G_H_CX4']
		elif position==2:#MMBASEBALL4, so a 1360 in baseball mode
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MM_COMBO_H_G_CX4_baseball']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MM_COMBO_G_H_CX4_baseball']
		elif position==3 or position==4 or position==5 or position==6:#MPLINESCORE4, MPLINESCORE5, MPMP-15X1, MPMP-14X1
			self.Keypad_Keys=AllKeypad_Keys['MP_LINESCORE_CX4']
		elif position==7 or position==19:#MPMULTISPORT1-baseball, MPLX3450-baseball
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASEFOOT_H_G_CX4_baseball']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASEFOOT_G_H_CX4_baseball']
		elif position==8 or position==20:#MPMULTISPORT1-football, MPLX3450-football
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASEFOOT_H_G_CX4_football']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASEFOOT_G_H_CX4_football']
		elif position==9:#MPFOOTBALL1
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_FOOTBALL_H_G_CX4']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_FOOTBALL_G_H_CX4']
		elif position==10 and self.keypad3150:#MMFOOTBALL4 and a 3150
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MM_FOOTBALL_H_G_CX4']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MM_FOOTBALL_G_H_CX4']
		elif position==10:#MMFOOTBALL4 and not a 3150, so a 1360 in football mode
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MM_COMBO_H_G_CX4_football']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MM_COMBO_G_H_CX4_football']
		elif position==11 and self.MMBasketball:#MPBASKETBALL1 and MM at the same time wow!!!
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MM_BASKETBALL_H_G_OLD']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MM_BASKETBALL_G_H_OLD']
		elif position==11:#MPBASKETBALL1
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASKETBALL_H_G_CX4']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASKETBALL_G_H_CX4']
		elif position==22:#STAT
			self.Keypad_Keys=AllKeypad_Keys['MP_STAT_CX803A']
		elif position==14 or position==15 or position==16:#MPSOCCER1, MPHOCKEY_LX1, MPHOCKEY1
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_SOCKEY_H_G_CX4']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_SOCKEY_G_H_CX4']
		elif position==12:#MPSOCCER_LX1-soccer
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_SOCFOOT_H_G_CX4_soccer']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_SOCFOOT_G_H_CX4_soccer']
		elif position==13:#MPSOCCER_LX1-football
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_SOCFOOT_H_G_CX4_football']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_SOCFOOT_G_H_CX4_football']
		elif position==17: #MPCRICKET1
			self.Keypad_Keys=AllKeypad_Keys['MP_CRICKET']
		else:# position==1 MPBASEBALL1, or position==21: MPGENERIC, or position==18: MPRACETRACK1
			if self.reverseHomeAndGuest:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASESOFT_H_G_CX4']
			else:
				self.Keypad_Keys=AllKeypad_Keys['MP_BASESOFT_G_H_CX4']

	def testAllButtons(self, game):
		letters=['B', 'C', 'D', 'E', 'F']
		numbers=['8', '7', '6', '5', '4', '3', '2', '1']
		for i in range(8):
			for j in range(5):
				function=letters[j]+numbers[i]
				print function
				self.Map(function, game)
				raw_input()

	def Map(self, keyPressed, game):
		print "Pressed Key:%s" % keyPressed
		self.funcString=self.Keypad_Keys[keyPressed]# find function name
		game.lastKeyPressedString= self.funcString
		print 'lastKeyPressedString: ', game.lastKeyPressedString

		if game.menuFlag:#create menu mask map thing
			#Create overlay of active keys----------------------
			if game.lampTestFlag or game.blankTestFlag:
				if self.funcString=='clear_FlashHit' or self.funcString=='clear_GuestGoal' or self.funcString=='clear' or self.funcString=='NewGame':
					#If in lamp or blank test only allow clear and newGame
					print 'Sending press to game function'
					game=self.gameFuncDict[self.funcString]()# call game function
			elif game.currentMenuString==game.lastKeyPressedString:
				#Allow key of the current menu
				print 'Sending press to game function'
				game=self.gameFuncDict[self.funcString]()# call game function
			elif self.funcString=='clear_FlashHit' or self.funcString=='clear_GuestGoal' or self.funcString=='clear':
				#Allow all clear keys
				print 'Sending press to game function'
				game=self.gameFuncDict[self.funcString]()# call game function
			elif self.funcString=='enter_FlashError' or self.funcString=='enter_HomeGoal' or self.funcString=='clear':
				#Allow all enter keys
				print 'Sending press to game function'
				game=self.gameFuncDict[self.funcString]()# call game function
			elif self.funcString=='Number_7_ABC' or self.funcString=='Number_8_DEF' or self.funcString=='Number_9_GHI' or \
			self.funcString=='Number_5_MNO' or self.funcString=='Number_6_PQR' or self.funcString=='Number_1_STU' or \
			self.funcString=='Number_2_VWX' or self.funcString=='Number_3_YZ' or self.funcString=='Number_4_JKL' or \
			self.funcString=='Number_0_&-.!':
				#Allow all numbers
				print 'Sending press to game function'
				game=self.gameFuncDict[self.funcString]()# call game function
			else:
				#Don't do anything if not one of these buttons pressed
				print 'Press NOT SENT to game function!!!!!'

		else:
			#All keys available
			print 'Sending press to game function'
			game=self.gameFuncDict[self.funcString]()# call game function
		#game=self.keyRules.Check(self.funcString, game)# adjust with any rules

		self.keyPressFlag = True
		return game

def main():
	print "ON"
	c=Config()
	sportList = ['MMBASEBALL3','MPBASEBALL1','MMBASEBALL4','MPLINESCORE4','MPLINESCORE5',\
	'MPMP-15X1','MPMP-14X1','MPMULTISPORT1-baseball','MPMULTISPORT1-football', 'MPFOOTBALL1','MMFOOTBALL4','MPBASKETBALL1', \
	'MPSOCCER_LX1-soccer','MPSOCCER_LX1-football','MPSOCCER1','MPHOCKEY_LX1','MPHOCKEY1','MPCRICKET1','MPRACETRACK1','MPLX3450-baseball','MPLX3450-football','MPGENERIC', 'MPSTAT']
	sport=sportList[1]
	print sport
	c.writeSport(sport)
	game = selectSportInstance(sport)
	print game.sport
	keyMap=Keypad_Mapping(game)
	raw_input()
	#addrMap=Address_Mapping(game)
	keyMap.testAllButtons(game)

	while 1:
		PRESSED=raw_input('                                     Type key (Ex. B8): ')
		keyMap.Map(PRESSED, game)
		#addrMap.Map(keyMap.funcString, game)
		#gameDict=game.__dict__
		#printDict(gameDict)


if __name__ == '__main__':
	main()
