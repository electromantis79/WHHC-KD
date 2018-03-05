#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys, csv
import time,threading
import functools
from PyQt4.QtSvg import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from radio_button_widget_class import *

from Scoreboard import *

from UI_KeypadLayout import Keypad_Layout
from UI_digit import *
from MP_Serial import MP_Serial_Handler

def save_obj(obj, name ):
	try:
		output_file=open('obj/'+name+'.txt','w')
		output_file.write(str(obj))
		output_file.close()
	except Exception as er:
		print er

def load_obj(name ):
	try:
		input_file=open('obj/'+name+'.txt','r')
		obj = eval(input_file.read())
		input_file.close()
		return obj
	except Exception as er:
		print er


class Simulation_Window(QMainWindow):
	'''This class creates a main window to use a keypad'''
	radioFontBig=QFont('arial',30)

	#constructor
	def __init__(self):
		super(Simulation_Window, self).__init__()
		self.backgroundGrayColor=QColor('#E7E7E8')
		palette = QPalette()
		palette.setColor(QPalette.Background, self.backgroundGrayColor)
		self.setPalette(palette)
		self.setWindowTitle('Scoreboard Simulation')
		self.previousModelIndex=0
		self.previousSportIndex=9
		self.create_central_widget()

	def create_central_widget(self):
		self.create_select_sport_layout()
		self.stacked_layout = QStackedLayout()
		self.stacked_layout.addWidget(self.select_sport_widget)

		self.central_widget = QWidget()

		self.central_widget.setLayout(self.stacked_layout)
		self.setCentralWidget(self.central_widget)

	def create_select_sport_layout(self):
		#initial layout

		self.sport_radio_buttons = RadioButtonWidget("Available Sport Codes\n", "Please select a sport", sportList, self.previousSportIndex)# sportList is local of Game

		self.reverse_HG_check_box = QCheckBox('Reverse Home and Guest')
		self.keypad_3150_check_box = QCheckBox('MM Keypad for LX3150')
		self.MMBasketball_check_box = QCheckBox('MM Keypad for Basketball')
		self.select_sport_button = QPushButton('Select')
		self.select_sport_button.setMaximumSize(5000, 5000)

		self.F_Jumper = QCheckBox('F Option Jumper')
		self.G_Jumper = QCheckBox('G Option Jumper')
		self.H_Jumper = QCheckBox('H Option Jumper')
		self.I_Jumper = QCheckBox('I Option Jumper')

		self.keypad_options_layout = QVBoxLayout()
		self.keypad_options_layout.addWidget(self.reverse_HG_check_box)
		self.keypad_options_layout.addWidget(self.keypad_3150_check_box)
		self.keypad_options_layout.addWidget(self.MMBasketball_check_box)

		self.option_jumpers_layout = QVBoxLayout()
		self.option_jumpers_layout.addWidget(self.F_Jumper)
		self.option_jumpers_layout.addWidget(self.G_Jumper)
		self.option_jumpers_layout.addWidget(self.H_Jumper)
		self.option_jumpers_layout.addWidget(self.I_Jumper)

		self.sport_options_grid = QHBoxLayout()
		self.sport_options_grid.addLayout(self.keypad_options_layout)
		self.sport_options_grid.addLayout(self.option_jumpers_layout)

		self.select_sport_layout_with_select = QVBoxLayout()
		self.select_sport_layout_with_select.addWidget(self.sport_radio_buttons)
		self.select_sport_layout_with_select.addLayout(self.sport_options_grid)
		self.select_sport_layout_with_select.addWidget(self.select_sport_button)

		self.select_sport_widget = QWidget()
		self.select_sport_widget.setLayout(self.select_sport_layout_with_select)

		#connections
		self.select_sport_button.clicked.connect(self.create_select_model_layout)

	def create_select_model_layout(self):
		#initial layout
		models=Scoreboard()
		self.modelList = models.modelList
		self.modelList.sort()
		self.model_radio_buttons = RadioButtonWidget("Available Models\n", "Please select a model", self.modelList, self.previousModelIndex)
		self.select_model_button = QPushButton('Select')

		#create layout to hold widgets
		self.select_model_layout = QVBoxLayout()
		self.select_model_layout.addWidget(self.model_radio_buttons)
		self.select_model_layout.addWidget(self.select_model_button)

		self.select_model_widget = QWidget()
		self.select_model_widget.setLayout(self.select_model_layout)

		#bring to top of stack
		self.stacked_layout.addWidget(self.select_model_widget)
		self.stacked_layout.setCurrentIndex(1)

		#connections
		self.select_model_button.clicked.connect(self.create_keypad_layout)

	def create_keypad_layout(self):
		#Prepare Data
		self.previousSportIndex=self.sport_radio_buttons.selected_button()
		self.previousModelIndex=self.model_radio_buttons.selected_button()
		self.sport=sportList[self.previousSportIndex]#get button selected
		self.model=self.modelList[self.previousModelIndex]#get button selected

		self.create_scoreboard_view()
		self.instantiate_scoreboard()

		self.keypad=Keypad_Layout(self.scoreboard.keyMap, self.scoreboard.lcd)
		#connections
		letters=self.keypad.letters
		numbers=self.keypad.numbers
		for i in range(8):
			for j in range(5):
				keyPressed=letters[j]+numbers[i]
				vars(self.keypad)[keyPressed+'_button'].clicked.connect(self.keypad_pressed)
				vars(self.keypad)[keyPressed+'_button'].setObjectName(keyPressed)

		self.scoreboard.board.setPos(100,150)

		self.new_scoreboard_button=QPushButton('New Scoreboard')
		self.new_scoreboard_button.setMaximumWidth(500)

		self.simulation_grid = QGridLayout()
		self.simulation_grid.addLayout(self.keypad.console_grid, 0, 0, Qt.AlignRight)
		self.simulation_grid.addWidget(self.scoreboard_view, 0, 1)
		self.simulation_grid.addWidget(self.new_scoreboard_button, 1, 0, Qt.AlignRight)

		self.view_simulation_widget = QWidget()
		self.view_simulation_widget.setLayout(self.simulation_grid)

		#bring to top of stack
		self.stacked_layout.addWidget(self.view_simulation_widget)
		self.stacked_layout.setCurrentIndex(2)

		self.new_scoreboard_button.clicked.connect(self.create_central_widget)

	def create_scoreboard_view(self):
		#QSvgWidget("Graphics/LX1060-Test-B.svg")

		self.scene = GraphicsScene()
		self.scoreboard_view = GraphicsView(self.scene)

		sizeHint = self.scoreboard_view.sizeHint()
		logo_width_height_ratio =  1 * sizeHint.width() / sizeHint.height()
		logo_width = 1000
		self.modelLabel=QGraphicsTextItem(self.model)
		self.modelLabel.setFont(self.radioFontBig)
		self.modelLabel.setPos(100,100)
		self.scene.addItem(self.modelLabel)
		#self.scoreboard_view.setFixedSize(logo_width, logo_width/logo_width_height_ratio)
		self.scoreboard_view.setFixedSize(1000,1000)

		self.scoreboard_view.setRenderHint(QPainter.Antialiasing)
		#background=QPixmap('Graphics/Background_1Kx1K.png')
		#self.scoreboard_view.setBackgroundBrush(QBrush(background))
		self.scoreboard_view.setCacheMode(GraphicsView.CacheBackground)
		self.scoreboard_view.setViewportUpdateMode(GraphicsView.SmartViewportUpdate)#FullViewportUpdate

		self.scoreboard_view.setDragMode(GraphicsView.ScrollHandDrag)
		self.scoreboard_view.setTransformationAnchor(GraphicsView.AnchorUnderMouse)
		self.scoreboard_view.setResizeAnchor(GraphicsView.AnchorUnderMouse)
		#self.scoreboard_view.setSceneRect(2,0,996,996)

	def instantiate_scoreboard(self):
		self.reverseHomeAndGuest = self.reverse_HG_check_box.isChecked()
		self.keypad3150 = self.keypad_3150_check_box.isChecked()
		self.MMBasketball = self.MMBasketball_check_box.isChecked()

		self.buildOptionJumpers()

		c=Config()
		c.writeSport(self.sport)

		self.scoreboard=Scoreboard(self.model, color='red', driverType='LXDriver', graphicsFlag=1, serialInputFlag=1, parent=None, scene=self.scene)
		self.scoreboard.setKeypad(self.reverseHomeAndGuest, self.keypad3150, self.MMBasketball)

		self.saveObjFiles()

		#create all timers
		self.refreshLCD_ClockTimer = QTimer()
		self.refreshLCD_ClockTimer.timeout.connect(self.refreshLCD_PeriodClock)
		self.refreshLCD_hitTimer = QTimer()
		self.refreshLCD_hitTimer.timeout.connect(self.refreshLCD_hitClock)
		self.refreshLCD_errorTimer = QTimer()
		self.refreshLCD_errorTimer.timeout.connect(self.refreshLCD_errorClock)
		self.closeMenuTimer = QTimer()
		self.closeMenuTimer.timeout.connect(self.refreshLCD_MenuTimer)
		self.refreshLCD_SplashTimer = QTimer()
		self.refreshLCD_SplashTimer.timeout.connect(self.refreshLCD_SplashScreenTimer)


	def saveObjFiles(self):
		save_obj(self.scoreboard.game.gameData, 'gameData')
		save_obj(self.scoreboard.game.teamsDict[self.scoreboard.game.home]['teamData'], 'home')
		save_obj(self.scoreboard.game.teamsDict[self.scoreboard.game.guest]['teamData'], 'guest')
		for clock in self.scoreboard.game.clockDict:
			save_obj(self.scoreboard.game.clockDict[str(clock)].__dict__, str(clock))

	def buildOptionJumpers(self):
		optionJumpers=''
		if self.F_Jumper.isChecked():
			optionJumpers+='F'
		else:
			optionJumpers+='0'
		if self.G_Jumper.isChecked():
			optionJumpers+='G'
		else:
			optionJumpers+='0'
		if self.H_Jumper.isChecked():
			optionJumpers+='H'
		else:
			optionJumpers+='0'
		if self.I_Jumper.isChecked():
			optionJumpers+='I'
		else:
			optionJumpers+='0'
		c=Config()
		c.writeOptionJumpers(optionJumpers)

	def sizeHint(self):
		return QSize(1000, 1000)

#Keypad button functions, Events, and Timer Functions

	def keypad_pressed(self):
		print '\n*********************NEW BUTTON PRESS EVENT****************************\n'
		print self.scoreboard.game.sport, self.scoreboard.game.gameData['sportType']
		sending_button = self.sender()
		keyPressed = str(sending_button.objectName())
		self.scoreboard.keyPressed(keyPressed)
		self.checkEvents()
		self.keypad.lcdRow1_line_edit.setText(self.scoreboard.lcd.row1)
		self.keypad.lcdRow2_line_edit.setText(self.scoreboard.lcd.row2)
		self.scoreboard.addrMap.Map(self.scoreboard.keyMap.funcString, self.scoreboard.game)
		self.scoreboard.data2Drivers(self.scoreboard.addrMap.sendList)
		#self.scoreboard.addrMap.UnMap(self.scoreboard.game, self.scoreboard.addrMap.sendList)
		#printDict(self.scoreboard.game.__dict__)
		print '\n*********************BUTTON PRESS EVENT OVER****************************\n'

	#All extra events that happen with a key press

	def checkEvents(self):
		self.timeEvents()
		self.dataEvents()
		self.lcdEvents()

	def timeEvents(self):
		if self.scoreboard.lcd.splashTimer.running:
			self.refreshLCD_SplashTimer.start(self.scoreboard.lcd.splashTimer.maxSeconds*1000)
		if self.scoreboard.game.clockDict['periodClock'].running:
			self.refreshLCD_ClockTimer.start(0)
		if self.scoreboard.game.gameData['sportType']=='baseball':
			if self.scoreboard.game.gameSettings['hitIndicatorFlashOn'] and not self.refreshLCD_hitTimer.isActive():
				self.refreshLCD_hitTimer.start(0)
			if self.scoreboard.game.gameSettings['errorIndicatorFlashOn'] and not self.refreshLCD_errorTimer.isActive():
				self.refreshLCD_errorTimer.start(0)
		if self.scoreboard.lcd.menuTimer.running and not self.scoreboard.lcd.currentMenuString=='yardsToGoReset':
			self.closeMenuTimer.start(self.scoreboard.lcd.menuTimer.maxSeconds*1000)
		if not self.scoreboard.lcd.menuFlag:
			self.defaultScreen()

	def dataEvents(self):
		if self.scoreboard.game.gameData['resetGameFlag']:
			self.scoreboard.game.gameData['resetGameFlag']=False
			#self.scoreboard.Reset()
		if self.scoreboard.game.gameSettings['dimmingFlag']:# each entery cycles through 6 brightness levels and sends them to each bank
			self.scoreboard.game.gameSettings['dimmingFlag']=False
			#ADD addrMap stuff for tunneling here

	def lcdEvents(self):
		if self.scoreboard.game.gameSettings['periodClockResetFlag']:
			self.scoreboard.game.gameSettings['periodClockResetFlag']=False
			self.scoreboard.game.clockDict['periodClock'].Update()
			self.defaultScreen()
		if self.scoreboard.lcd.currentMenuString=='yardsToGoReset':
			self.scoreboard.lcd.menuFlag=False
			self.defaultScreen()
			self.scoreboard.lcd.menuFlag=True


	#Timed events for the main program

	def refreshLCD_SplashScreenTimer(self):
		print '\nEND SPLASH'
		self.refreshLCD_SplashTimer.stop()
		self.stacked_layout.removeWidget(self.view_simulation_widget)
		self.create_keypad_layout()
		self.defaultScreen()

	def refreshLCD_MenuTimer(self):
		print '\nEND MENU'
		self.closeMenuTimer.stop()
		self.defaultScreen()

	def refreshLCD_PeriodClock(self):
		print 'clock'
		timerName='refreshLCD_ClockTimer'
		self.refreshIndicator(timerName,  durationName=None, flashOnName=None, clockName='periodClock')
		self.scoreboard.lcd.verbose=True

	def refreshLCD_hitClock(self):
		timerName, durationName, flashOnName='refreshLCD_hitTimer', 'hitFlashDuration', 'hitIndicatorFlashOn'
		self.refreshIndicator(durationName, flashOnName)

	def refreshLCD_errorClock(self):
		timerName, durationName, flashOnName='refreshLCD_errorTimer', 'errorFlashDuration', 'errorIndicatorFlashOn'
		self.refreshIndicator(durationName, flashOnName)

	def refreshIndicator(self, timerName, durationName, flashOnName, clockName=None):
		self.scoreboard.lcd.verbose=False
		self.defaultScreen()
		vars(self)[timerName].stop()
		if clockName:
			vars(self)[timerName].start(self.scoreboard.game.clockDict[clockName].resolution*100)
			if not self.scoreboard.game.clockDict['periodClock'].running:
				vars(self)[timerName].stop()
		else:
			vars(self)[timerName].start(self.scoreboard.game.gameSettings[durationName]*1000+self.scoreboard.game.gameSettings[durationName]*1000*.01)
			if not self.scoreboard.game.gameSettings[flashOnName]:
				vars(self)[timerName].stop()
		self.scoreboard.lcd.verbose=True

	def defaultScreen(self):
		self.scoreboard.exitMenuLCD()
		self.keypad.lcdRow1_line_edit.setText(self.scoreboard.lcd.row1)
		self.keypad.lcdRow2_line_edit.setText(self.scoreboard.lcd.row2)


def main():
	print "ON"
	Simulation = QApplication(sys.argv)
	w = Simulation_Window()
	w.showMaximized()
	w.raise_()
	sys.exit(Simulation.exec_())


if __name__ == '__main__':
	main()
