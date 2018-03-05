#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**COMPLETION** = 99%  Sphinx Approved = **True**

.. topic:: Overview

	This module creates a user interface simulation of a console and scoreboard.

    :Created Date: 1/29/2015
    :Modified Date: 3/3/2016
    :Author: **Craig Gunter**

"""

import sys, csv, time, threading

from functions import *
from pyqt_subclasses import * #Holds PyQt4 imports
from Config import Config
from radio_button_widget_class import RadioButtonWidget
from list_widget_class import ListWidget, ListLayoutWidget
from UI_Layouts import Keypad_Layout
from Scoreboard import Scoreboard
from UI_Scoreboard_Parts import *

class Simulation_Window(QMainWindow):
	'''This class creates a main window to simulate a scoreboard and controller.'''
	radioFontBig=QFont('arial',30)
	backgroundGrayColor=QColor('#E7E7E8')

	#constructor
	def __init__(self):
		super(Simulation_Window, self).__init__()
		palette = QPalette()
		palette.setColor(QPalette.Background, self.backgroundGrayColor)
		self.setPalette(palette)
		self.setWindowTitle('Scoreboard Simulation')

		c=Config()
		self.sport=c.configDict['sport']
		self.model=c.configDict['model']
		self.boardColor=c.configDict['boardColor']
		self.captionColor=c.configDict['captionColor']
		self.activeCaption=0
		self.stripeColor=c.configDict['stripeColor']
		self.LEDcolor=c.configDict['LEDcolor']
		self.vboseList=[1,0,0]# controls verbosity for console, scoreboard, and lcd
		self.refreshAssets_frequency=10#milliseconds
		self.checkClickables_frequency=10#milliseconds
		self.scoreboardDict={}
		self.reverseHomeAndGuest = False
		self.keypad3150 = False
		self.MMBasketball = False
		self.WHHBaseball = False
		self.simFlag=False
		self.captionBlankFlag=True
		self.serialInputFlag=False

		self.setOptionJumpers()

		models=Scoreboard('modelList', vboseList=[0,0,0], checkEventsFlag=False)
		self.modelList = models.modelList
		self.modelList.sort()
		board=Board()
		self.colorList=board.colorDict.keys()
		self.colorList.sort()

		self.modelDefaults = readModelDefaults()

		self.create_central_widget()

		#START Initialize ---------------------------

	def setOptionJumpers(self):
		'''Sets the option jumper check boxes to the state of the userConfig file.'''
		c=Config()
		optionJumpers=c.configDict['optionJumpers']
		if optionJumpers[0]=='B':
			self.B_JumperChecked=True
		else:
			self.B_JumperChecked=False
		if optionJumpers[1]=='C':
			self.C_JumperChecked=True
		else:
			self.C_JumperChecked=False
		if optionJumpers[2]=='D':
			self.D_JumperChecked=True
		else:
			self.D_JumperChecked=False
		if optionJumpers[3]=='E':
			self.E_JumperChecked=True
		else:
			self.E_JumperChecked=False

	def sportJumpersDisplay(self, model):
		'''Sets the sport select jumpers check boxes to the current sports configuration.'''
		if tf(self.modelDefaults[model][5]):
			self.F_Jumper.setText('F Jumper Installed')
		else:
			self.F_Jumper.setText('')
		if tf(self.modelDefaults[model][6]):
			self.G_Jumper.setText('G Jumper Installed')
		else:
			self.G_Jumper.setText('')
		if tf(self.modelDefaults[model][7]):
			self.H_Jumper.setText('H Jumper Installed')
		else:
			self.H_Jumper.setText('')
		if tf(self.modelDefaults[model][8]):
			self.I_Jumper.setText('I Jumper Installed')
		else:
			self.I_Jumper.setText('')

	def create_central_widget(self):
		'''Sets up the stack of layouts and loads the first one.'''
		if self.simFlag:
			self.simFlag=False
			del self.scene
			del self.select_model_widget
			del self.view_simulation_widget
			self.scoreboardDict.clear()
			self.activeCaption=0
		self.playClockAddedFlag=False
		self.lockerClockAddedFlag=False

		self.stacked_layout = QStackedLayout()
		self.central_widget = QWidget()
		self.central_widget.setLayout(self.stacked_layout)

		self.create_select_model_widget()

		self.stacked_layout.addWidget(self.select_model_widget)

		self.setCentralWidget(self.central_widget)

		#END Initialize ---------------------------
		#START SCREEN 1 ---------------------------

	def create_select_model_widget(self):
		'''Main layout for first screen.'''

		#initial widgets
		self.sport_list = ListLayoutWidget("Available Sport Codes", sportList, self.sport)# sportList is local of Game
		self.model_list = ListLayoutWidget("Available Models", self.modelList, self.model)
		self.board_color_list = ListLayoutWidget("Face Color", self.colorList, self.boardColor)
		self.caption_color_list = ListLayoutWidget("Caption Color", self.colorList, self.captionColor)
		self.stripe_color_list = ListLayoutWidget("Stripe Color", self.colorList, self.stripeColor)
		self.LED_color_list = ListLayoutWidget("LED Color", ['RED', 'AMBER'], self.LEDcolor)
		self.reverse_HG_check_box = QCheckBox('Reverse Home and Guest')
		self.keypad_3150_check_box = QCheckBox('MM Keypad for LX3150')
		self.MMBasketball_check_box = QCheckBox('MM Keypad for Basketball')
		self.WHHBaseball_check_box = QCheckBox('WHH Keypad for Baseball')
		#self.playClock_check_box = QCheckBox('Add a Play Clock')
		self.B_Jumper = QCheckBox('B Option Jumper')
		self.C_Jumper = QCheckBox('C Option Jumper')
		self.D_Jumper = QCheckBox('D Option Jumper')
		self.E_Jumper = QCheckBox('E Option Jumper')
		self.F_Jumper = QLabel('F Option Jumper')
		self.G_Jumper = QLabel('G Option Jumper')
		self.H_Jumper = QLabel('H Option Jumper')
		self.I_Jumper = QLabel('I Option Jumper')
		self.select_model_button = QPushButton('Select')
		self.select_model_button.setMinimumHeight(50)

		#Set check box states
		self.reverse_HG_check_box.setChecked(self.reverseHomeAndGuest)
		self.keypad_3150_check_box.setChecked(self.keypad3150)
		self.MMBasketball_check_box.setChecked(self.MMBasketball)
		self.WHHBaseball_check_box.setChecked(self.WHHBaseball)
		self.B_Jumper.setChecked(self.B_JumperChecked)
		self.C_Jumper.setChecked(self.C_JumperChecked)
		self.D_Jumper.setChecked(self.D_JumperChecked)
		self.E_Jumper.setChecked(self.E_JumperChecked)
		self.sportJumpersDisplay(self.model)

		#Option layouts

		#Vertical Keypad Option Check Boxes
		self.keypad_options_layout = QVBoxLayout()
		self.keypad_options_layout.addWidget(self.reverse_HG_check_box)
		self.keypad_options_layout.addWidget(self.keypad_3150_check_box)
		self.keypad_options_layout.addWidget(self.MMBasketball_check_box)
		self.keypad_options_layout.addWidget(self.WHHBaseball_check_box)
		#self.keypad_options_layout.addWidget(self.playClock_check_box)

		#Vertical Option Jumper Check Boxes
		self.option_jumpers_layout = QVBoxLayout()
		self.option_jumpers_layout.addWidget(self.B_Jumper)
		self.option_jumpers_layout.addWidget(self.C_Jumper)
		self.option_jumpers_layout.addWidget(self.D_Jumper)
		self.option_jumpers_layout.addWidget(self.E_Jumper)

		#Vertical Sport Jumper Check Boxes
		self.sport_jumpers_layout = QVBoxLayout()
		self.sport_jumpers_layout.addWidget(self.F_Jumper)
		self.sport_jumpers_layout.addWidget(self.G_Jumper)
		self.sport_jumpers_layout.addWidget(self.H_Jumper)
		self.sport_jumpers_layout.addWidget(self.I_Jumper)

		#Horizontal All options
		self.sport_options_grid = QHBoxLayout()
		self.sport_options_grid.addLayout(self.keypad_options_layout)
		self.sport_options_grid.addLayout(self.option_jumpers_layout)
		self.sport_options_grid.addLayout(self.sport_jumpers_layout)

		#Vertical Color Lists
		self.colors_layout = QVBoxLayout()
		self.colors_layout.addWidget(self.LED_color_list)
		self.colors_layout.addWidget(self.board_color_list)
		self.colors_layout.addWidget(self.caption_color_list)
		self.colors_layout.addWidget(self.stripe_color_list)

		#Horizontal Lists
		self.lists_layout = QHBoxLayout()
		self.lists_layout.addWidget(self.model_list)
		self.lists_layout.addWidget(self.sport_list)
		self.lists_layout.addLayout(self.colors_layout)

		#Main layout
		self.select_model_layout = QVBoxLayout()
		self.select_model_layout.addLayout(self.lists_layout)
		self.select_model_layout.addLayout(self.sport_options_grid)
		self.select_model_layout.addWidget(self.select_model_button)

		#Main widget
		self.select_model_widget = QWidget()
		self.select_model_widget.setLayout(self.select_model_layout)

		#connections
		self.select_model_button.clicked.connect(self.create_view_simulation_widget)

		self.model_list.connect(self.model_list.listWidget,SIGNAL("itemClicked(QListWidgetItem*)"),\
		self,SLOT("model_clicked(QListWidgetItem*)"))
		self.sport_list.connect(self.sport_list.listWidget,SIGNAL("itemClicked(QListWidgetItem*)"),\
		self,SLOT("sport_clicked(QListWidgetItem*)"))

		#END SCREEN 1 ---------------------------
		#START SCREEN 2 ---------------------------

	def create_view_simulation_widget(self):
		'''Layout for Keypad and scoreboard.'''
		self.select_model_widget.setCursor(QCursor(Qt.WaitCursor))
		self.simFlag=True

		#Update data with inputs given
		self.reverseHomeAndGuest = self.reverse_HG_check_box.isChecked()
		self.keypad3150 = self.keypad_3150_check_box.isChecked()
		self.MMBasketball = self.MMBasketball_check_box.isChecked()
		self.WHHBaseball = self.WHHBaseball_check_box.isChecked()
		self.sport=str(self.sport_list.listWidget.currentItem().text())
		self.model=str(self.model_list.listWidget.currentItem().text())
		self.boardColor=str(self.board_color_list.listWidget.currentItem().text())
		self.captionColor=str(self.caption_color_list.listWidget.currentItem().text())
		self.stripeColor=str(self.stripe_color_list.listWidget.currentItem().text())
		self.LEDcolor=str(self.LED_color_list.listWidget.currentItem().text())

		c=Config()
		c.writeSport(self.sport)
		c.writeUI(self.model, self.boardColor, self.captionColor, self.stripeColor, self.LEDcolor)

		self.buildOptionJumpers()

		self.instantiate_scoreboard()
		#printDict(self.scoreboardDict[self.model].__dict__)

		self.keypad_view=Keypad_Layout(self.scoreboardDict[self.model], self.model)

		#key pad button connections
		letters=self.keypad_view.letters
		numbers=self.keypad_view.numbers
		for i in range(8):
			for j in range(5):
				keyPressed=letters[j]+numbers[i]
				vars(self.keypad_view)[keyPressed+'_button'].clicked.connect(self.keypad_pressed)
				vars(self.keypad_view)[keyPressed+'_button'].setObjectName(keyPressed)

		self.create_scoreboard_view()

		#initialize User Buttons
		self.new_scoreboard_button=QPushButton('New Scoreboard')
		self.new_scoreboard_button.setMaximumWidth(500)
		self.save_dictionary_button=QPushButton('Save Dictionaries')
		self.save_dictionary_button.setMaximumWidth(500)
		self.reverse_caption_button=QPushButton('Toggle Captions')
		self.reverse_caption_button.setMaximumWidth(500)
		self.add_play_clock_button=QPushButton('Add Play/Shot Clock')
		self.add_play_clock_button.setMaximumWidth(500)
		self.add_locker_clock_button=QPushButton('Add Locker Room Clock')
		self.add_locker_clock_button.setMaximumWidth(500)

		#Horizontal User buttons
		self.bottom_buttons = QHBoxLayout()
		self.bottom_buttons.addWidget(self.reverse_caption_button)
		if self.sportType=='football' or self.sportType=='soccer' or \
		self.sportType=='basketball' or self.sportType=='hockey':
			self.bottom_buttons.addWidget(self.add_play_clock_button)
		if 0:
			self.bottom_buttons.addWidget(self.save_dictionary_button)
		self.bottom_buttons.addWidget(self.add_locker_clock_button)
		self.bottom_buttons.addWidget(self.new_scoreboard_button)

		#Main layout
		self.simulation_grid = QGridLayout()
		self.simulation_grid.addLayout(self.keypad_view.console_grid, 0, 0, Qt.AlignRight)
		self.simulation_grid.addWidget(self.scoreboard_view, 0, 1)
		self.simulation_grid.addLayout(self.bottom_buttons, 1, 0, Qt.AlignRight)

		#Main wigdet
		self.view_simulation_widget = QWidget()
		self.view_simulation_widget.setLayout(self.simulation_grid)

		#Start refresh timers
		self.refreshAssets.start(self.refreshAssets_frequency)#milliseconds
		self.checkClickables.start(self.checkClickables_frequency)#milliseconds

		#user button connections
		self.new_scoreboard_button.clicked.connect(self.create_central_widget)
		self.save_dictionary_button.clicked.connect(self.saveObjFiles)
		self.reverse_caption_button.clicked.connect(self.changeCaption)
		self.add_play_clock_button.clicked.connect(self.addPlayClock)
		self.add_locker_clock_button.clicked.connect(self.addLockerClock)

		#bring to top of stack to make it visible
		self.stacked_layout.addWidget(self.view_simulation_widget)
		self.stacked_layout.setCurrentIndex(1)

		#END SCREEN 2 ---------------------------
		#START Screen Components ---------------------------

	def buildOptionJumpers(self):
		'''Updates the userConfig file with the selected option jumpers.'''
		optionJumpers=''
		self.B_JumperChecked=self.B_Jumper.isChecked()
		self.C_JumperChecked=self.C_Jumper.isChecked()
		self.D_JumperChecked=self.D_Jumper.isChecked()
		self.E_JumperChecked=self.E_Jumper.isChecked()
		if self.B_JumperChecked:
			optionJumpers+='B'
		else:
			optionJumpers+='0'
		if self.C_JumperChecked:
			optionJumpers+='C'
		else:
			optionJumpers+='0'
		if self.D_JumperChecked:
			optionJumpers+='D'
		else:
			optionJumpers+='0'
		if self.E_JumperChecked:
			optionJumpers+='E'
		else:
			optionJumpers+='0'
		c=Config()
		c.writeOptionJumpers(optionJumpers)

	def instantiate_scoreboard(self):
		'''Creates the graphic scene and instantiates the scoreboard object.'''
		self.scene = GraphicsScene()
		self.background=QGraphicsSvgItem('Graphics/EMechBackground.svg')
		self.scene.addItem(self.background)

		scoreboard=Scoreboard(\
		self.model, captionColor=self.captionColor, driverType='LXDriver', \
		serialInputFlag=self.serialInputFlag, parent=None, scene=self.scene, vboseList=self.vboseList)

		scoreboard.setKeypad(self.reverseHomeAndGuest, self.keypad3150, self.MMBasketball, self.WHHBaseball)

		self.sportType=scoreboard.game.gameData['sportType']
		print 'Sport:', scoreboard.game.sport, 'Sport Type:', self.sportType, 'Keypad:', scoreboard.keyMap.keypadName, 'model', self.model

		self.scoreboardDict[self.model]=Board(\
		scoreboard, LEDcolor='AMBER', boardColor=self.boardColor, \
		captionColor=self.captionColor, stripeColor=self.stripeColor, \
		driverType='LXDriver', parent=self.background, scene=self.scene)

		#create all timers
		self.refreshAssets = QTimer()
		self.refreshAssets.timeout.connect(self.updateAssets)
		self.checkClickables = QTimer()
		self.checkClickables.timeout.connect(self.checkClickableEvents)

	def create_scoreboard_view(self):
		'''Creates the views for scoreboards.'''
		#Prepare zoom level
		self.boardWidth=self.scoreboardDict[self.model].boundingRect.width()
		self.boardHeight=self.scoreboardDict[self.model].boundingRect.height()
		self.backgroundWidth=self.background.boundingRect().width()
		self.backgroundHeight=self.background.boundingRect().height()
		if self.boardWidth>=312:
			self.boardFactor=150.0/342.0
		elif self.boardWidth>=240 or self.model=='LX2575' or self.model=='LX2576':
			self.boardFactor=150.0/282.0
		elif self.boardWidth>=120 or self.model=='LX2555' or self.model=='LX2556':
			self.boardFactor=150.0/216.0
		elif self.model=='GENERIC':
			self.boardFactor=.5
		else:
			self.boardFactor=1.0
		self.scoreboardDict[self.model].scale(self.boardFactor,self.boardFactor)


		if self.model=='LX2555' or self.model=='LX2575':
			model='LX2055'
		elif self.model=='LX2556' or self.model=='LX2576':
			model='LX2056'

		if self.scoreboardDict[self.model].scoreboard.partsDict[self.model]['qtyOfCabinets']==2:
			if self.model=='LX2055' or self.model=='LX2056':
				self.scoreboardDict[self.model].setPos(self.backgroundWidth/2-self.boardFactor*(self.scoreboardDict[self.model].scoreboard.statWidth+self.scoreboardDict[self.model].scoreboard.boardWidth*2)/2, \
				self.backgroundHeight/2-self.boardFactor*self.boardHeight/2)
			else:
				self.scoreboardDict[self.model].setPos(self.backgroundWidth/2-self.boardFactor*self.boardWidth/2, self.backgroundHeight/2-self.boardFactor*self.boardHeight/2)
		else:
			if self.model=='LX2555' or self.model=='LX2556' or self.model=='LX2575' or self.model=='LX2576':
				if self.model=='LX2555':
					statWidth=108
				elif self.model=='LX2556':
					statWidth=108
				elif self.model=='LX2575':
					statWidth=168
				elif self.model=='LX2576':
					statWidth=168
				scoreboard=Scoreboard(\
				model, captionColor=self.captionColor, driverType='LXDriver', serialInputFlag=self.serialInputFlag, \
				parent=None, scene=self.scene, vboseList=self.vboseList)
				scoreboard.statWidth=statWidth

				scoreboard.setKeypad(self.reverseHomeAndGuest, self.keypad3150, self.MMBasketball, self.WHHBaseball)

				print 'Sport:', scoreboard.game.sport, 'Sport Type:', self.sportType, 'Keypad:', scoreboard.keyMap.keypadName, 'model', model

				self.scoreboardDict[model]=Board(\
				scoreboard, LEDcolor='AMBER', boardColor=self.boardColor, captionColor=self.captionColor, stripeColor=self.stripeColor, \
				driverType='LXDriver', parent=self.background, scene=self.scene)

				self.scoreboardDict[model].scoreboard.setKeypad(self.reverseHomeAndGuest, self.keypad3150, self.MMBasketball)
				self.scoreboardDict[model].scale(self.boardFactor,self.boardFactor)
				self.scoreboardDict[model].setPos(\
				self.backgroundWidth/2-self.boardFactor*(self.boardWidth+self.scoreboardDict[model].scoreboard.boardWidth*2)/2, \
				self.backgroundHeight/2-self.boardFactor*self.boardHeight/4)

				self.scoreboardDict[self.model].setPos(self.backgroundWidth/2-self.boardFactor*self.boardWidth/2, self.backgroundHeight/2-self.boardFactor*self.boardHeight/4)
			else:
				self.scoreboardDict[self.model].setPos(self.backgroundWidth/2-self.boardFactor*self.boardWidth/2, self.backgroundHeight/2-self.boardFactor*self.boardHeight/2)

		self.background.scale(5,5)

		#Single View
		self.single_scoreboard_view = GraphicsView(self.scene)
		self.single_scoreboard_view.centerOn(self.backgroundWidth/2,self.backgroundHeight/2)

		self.single_scoreboard_view.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)
		self.single_scoreboard_view.setContextMenuPolicy(Qt.CustomContextMenu);
		self.single_scoreboard_view.setViewportUpdateMode(GraphicsView.MinimalViewportUpdate)#FullViewportUpdate
		self.single_scoreboard_view.setDragMode(GraphicsView.ScrollHandDrag)
		self.single_scoreboard_view.setTransformationAnchor(GraphicsView.AnchorUnderMouse)
		self.single_scoreboard_view.setResizeAnchor(GraphicsView.AnchorUnderMouse)
		self.single_scoreboard_view.connect(self.single_scoreboard_view,SIGNAL("customContextMenuRequested(QPoint)"),self,SLOT("contextMenuRequestedSingle(QPoint)"))

		#Full View
		self.scoreboard_full_view = GraphicsView(self.scene)
		self.scoreboard_full_view.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)
		self.scoreboard_full_view.setContextMenuPolicy(Qt.CustomContextMenu);
		self.scoreboard_full_view.setViewportUpdateMode(GraphicsView.MinimalViewportUpdate)#FullViewportUpdate
		self.scoreboard_full_view.setDragMode(GraphicsView.ScrollHandDrag)
		self.scoreboard_full_view.setTransformationAnchor(GraphicsView.AnchorUnderMouse)
		self.scoreboard_full_view.setResizeAnchor(GraphicsView.AnchorUnderMouse)
		self.scoreboard_full_view.connect(self.scoreboard_full_view,SIGNAL("customContextMenuRequested(QPoint)"),self,SLOT("contextMenuRequestedDouble(QPoint)"))

		#Zoom View
		self.scoreboard_zoom_view = GraphicsView(self.scene)
		self.zoomFactor=8
		self.scoreboard_zoom_view.scale(self.zoomFactor,self.zoomFactor)

		self.scoreboard_zoom_view.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)
		self.scoreboard_zoom_view.setViewportUpdateMode(GraphicsView.MinimalViewportUpdate)#FullViewportUpdate
		self.scoreboard_zoom_view.setDragMode(GraphicsView.ScrollHandDrag)
		self.scoreboard_zoom_view.setTransformationAnchor(GraphicsView.AnchorUnderMouse)
		self.scoreboard_zoom_view.setResizeAnchor(GraphicsView.AnchorUnderMouse)

		#Vertical scoreboard view
		self.single_scoreboard_layout = QVBoxLayout()
		self.single_scoreboard_layout.addWidget(self.single_scoreboard_view)

		#Vertical scoreboard view
		self.double_scoreboard_layout = QVBoxLayout()
		self.double_scoreboard_layout.addWidget(self.scoreboard_full_view)
		self.double_scoreboard_layout.addWidget(self.scoreboard_zoom_view)

		#Main wigdet
		self.scoreboard_view_single = QWidget()
		self.scoreboard_view_single.setLayout(self.single_scoreboard_layout)

		#Main wigdet
		self.scoreboard_view_double = QWidget()
		self.scoreboard_view_double.setLayout(self.double_scoreboard_layout)

		self.scoreboard_view = self.scoreboard_view_single

		#END Screen Components ---------------------------
		#START User Buttons ---------------------------

	def saveObjFiles(self):
		'''Saves objects as config files for reveiw.'''
		for model in self.scoreboardDict:
			save_obj(self.scoreboardDict[model].scoreboard.game.gameData, 'gameData')
			save_obj(self.scoreboardDict[model].scoreboard.game.teamsDict[self.scoreboardDict[model].scoreboard.game.home].teamData, 'home')
			save_obj(self.scoreboardDict[model].scoreboard.game.teamsDict[self.scoreboardDict[model].scoreboard.game.guest].teamData, 'guest')
			for clock in self.scoreboardDict[model].scoreboard.game.clockDict:
				save_obj(self.scoreboardDict[model].scoreboard.game.clockDict[str(clock)].timeUnitsDict, str(clock))

	def changeCaption(self):
		'''Cycles through the different captions on multisport boards.'''
		size=len(self.scoreboardDict[self.model].graphicsDict)
		#if self.scoreboardDict[self.model].graphicsDict[self.activeCaption].isVisible():
		self.scoreboardDict[self.model].graphicsDict[self.activeCaption].setVisible(False)
		if self.captionBlankFlag:
			self.captionBlankFlag=False
		elif self.activeCaption+1==size:
			self.scoreboardDict[self.model].graphicsDict[0].setVisible(True)
			self.activeCaption=0
			self.captionBlankFlag=True
		else:
			self.scoreboardDict[self.model].graphicsDict[self.activeCaption+1].setVisible(True)
			self.activeCaption=self.activeCaption+1

	def addPlayClock(self):
		'''Adds a play clock to the graphic scene.'''
		if not self.playClockAddedFlag:
			self.playClockAddedFlag=True
			if self.sportType=='football' or self.sportType=='soccer':
				model='LX3018'
			elif self.sportType=='basketball' or self.sportType=='hockey':
				model='LX2180'
			else:
				model=None

			if model is not None:
				scoreboard=Scoreboard(\
				model, captionColor=self.captionColor, driverType='LXDriver', \
				serialInputFlag=self.serialInputFlag, parent=None, scene=self.scene, vboseList=self.vboseList)

				scoreboard.setKeypad(self.reverseHomeAndGuest, self.keypad3150, self.MMBasketball, self.WHHBaseball)

				self.sportType=scoreboard.game.gameData['sportType']
				print 'Sport:', scoreboard.game.sport, 'Sport Type:', self.sportType, 'Keypad:', scoreboard.keyMap.keypadName, 'model', self.model

				self.scoreboardDict[model]=Board(\
				scoreboard, LEDcolor='AMBER', boardColor=self.boardColor, \
				captionColor=self.captionColor, stripeColor=self.stripeColor, \
				driverType='LXDriver', parent=self.background, scene=self.scene)

				self.scoreboardDict[model].setPos(self.backgroundWidth/2-\
				self.scoreboardDict[model].boundingRect.width()/2, self.backgroundHeight/2+\
				self.boardFactor*self.boardHeight/2+self.boardFactor*5)

	def addLockerClock(self):
		'''Adds a locker room clock to the graphic scene.'''
		if not self.lockerClockAddedFlag:
			self.lockerClockAddedFlag=True
			model='LX7406'
			scoreboard=Scoreboard(\
			model, captionColor=self.captionColor, driverType='LXDriver', \
			serialInputFlag=self.serialInputFlag, parent=None, scene=self.scene, vboseList=self.vboseList)

			scoreboard.setKeypad(self.reverseHomeAndGuest, self.keypad3150, self.MMBasketball, self.WHHBaseball)

			self.sportType=scoreboard.game.gameData['sportType']
			print 'Sport:', scoreboard.game.sport, 'Sport Type:', self.sportType, 'Keypad:', scoreboard.keyMap.keypadName, 'model', self.model

			self.scoreboardDict[model]=Board(\
			scoreboard, LEDcolor='AMBER', boardColor=self.boardColor, \
			captionColor=self.captionColor, stripeColor=self.stripeColor, \
			driverType='LXDriver', parent=self.background, scene=self.scene)

			width=0
			if self.sportType=='linescore'or self.sportType=='soccer':
				width=self.scoreboardDict[self.model].boundingRect.width()/2
			elif self.sportType=='football':
				width=self.scoreboardDict[self.model].boundingRect.width()/4

			if self.scoreboardDict[self.model].scoreboard.partsDict[self.model]['qtyOfCabinets']==2:
				if self.sportType=='stat':
					height=self.boardHeight/2
				else:
					height=self.boardHeight
			else:
				height=self.boardHeight/2

			self.scoreboardDict[model].setPos(self.boardFactor*(self.backgroundWidth/2-\
			self.scoreboardDict[self.model].boundingRect.width()/2+width), self.backgroundHeight/2+\
			self.boardFactor*height+self.boardFactor*5)

		#END User Buttons ---------------------------
		#START PyQt Slots ---------------------------

	@pyqtSlot(QListWidgetItem)
	def model_clicked(self, item):
		'''Clicking a model auto-selects its default sport and jumpers'''
		model=str(item.text())
		sportList=self.sport_list.listWidget.findItems(self.modelDefaults[model][0],Qt.MatchExactly)
		if len(sportList) > 0:
			self.sport_list.listWidget.setCurrentItem(sportList[0])
			self.B_Jumper.setChecked(tf(self.modelDefaults[model][1]))
			self.C_Jumper.setChecked(tf(self.modelDefaults[model][2]))
			self.D_Jumper.setChecked(tf(self.modelDefaults[model][3]))
			self.E_Jumper.setChecked(tf(self.modelDefaults[model][4]))
			self.sportJumpersDisplay(model)

	@pyqtSlot(QListWidgetItem)
	def sport_clicked(self, item):
		'''Clicking a sport auto-selects its default jumpers'''
		model=str(item.text())
		self.sportJumpersDisplay(model)
		self.B_Jumper.setChecked(tf(self.modelDefaults[model][1]))
		self.C_Jumper.setChecked(tf(self.modelDefaults[model][2]))
		self.D_Jumper.setChecked(tf(self.modelDefaults[model][3]))
		self.E_Jumper.setChecked(tf(self.modelDefaults[model][4]))
		self.sportJumpersDisplay(model)

	@pyqtSlot(QPoint)
	def contextMenuRequestedSingle(self,point):
		'''Right clicking brings up the menu while in standard view'''
		menu = QMenu()
		action1 = menu.addAction("Zoom To Location")

		self.connect(action1,SIGNAL("triggered()"),self,SLOT("slotZoomToLocation()"))
		self.point=self.single_scoreboard_view.mapToScene(point)
		menu.exec_(self.single_scoreboard_view.mapToGlobal(point))

	@pyqtSlot(QPoint)
	def contextMenuRequestedDouble(self,point):
		'''Right clicking brings up the menu while in split screen view'''
		menu = QMenu()
		action1 = menu.addAction("Zoom To Location")

		self.connect(action1,SIGNAL("triggered()"),self,SLOT("slotZoomToLocation()"))
		self.point=self.scoreboard_full_view.mapToScene(point)
		menu.exec_(self.scoreboard_full_view.mapToGlobal(point))

	@pyqtSlot()
	def slotZoomToLocation(self):
		'''Activates split screen view and zooms to current cursor position.'''
		self.scoreboard_zoom_view.centerOn(self.point)
		self.single_scoreboard_view.setFixedSize(1,1)
		self.scoreboard_view_single.layout().removeWidget(self.single_scoreboard_view)
		self.scoreboard_view_single.layout().addWidget(self.scoreboard_full_view)
		self.scoreboard_view_single.layout().addWidget(self.scoreboard_zoom_view)

	def sizeHint(self):
		return QSize(1000, 1000)

		#END PyQt Slots ---------------------------

		#START Keypad button functions, Events, and Timer Called Functions

	def keypad_pressed(self):
		'''Sends the key pressed to the scoreboards.'''
		print '\n*********************NEW BUTTON PRESS EVENT****************************\n'
		for model in self.scoreboardDict:
			print 'Sport:', self.scoreboardDict[model].scoreboard.game.sport, 'Sport Type:', self.sportType, 'Keypad:', self.scoreboardDict[model].scoreboard.keyMap.keypadName
			sending_button = self.sender()
			keyPressed = str(sending_button.objectName())
			self.scoreboardDict[model].scoreboard.keyPressed(keyPressed)
			#printDict(self.scoreboardDict[model].__dict__)
			self._checkEvents()
		print '\n*********************BUTTON PRESS EVENT OVER****************************\n'

	def _checkEvents(self):
		#Any other events that happen with a button press go here
		pass

	def updateAssets(self):
		'''
		Updates the lcd screen and scoreboards.
		Called every 10 ms
		'''

		#Update LCD screen
		try:
			self.keypad_view.lcdRow1_line_edit.setText(self.scoreboardDict[self.model].scoreboard.lcd.row1)
			self.keypad_view.lcdRow2_line_edit.setText(self.scoreboardDict[self.model].scoreboard.lcd.row2)
		except:
			pass

		#Update all drivers
		for model in self.scoreboardDict:
			if self.scoreboardDict[model].scoreboard.resetGraphicsFlag:
				self.scoreboardDict[model].scoreboard.resetGraphicsFlag=False
				self.scoreboardDict[model].Reset()
				print 'resetGraphicsFlag triggered'
			self.scoreboardDict[model].data2GraphicDrivers()
		try:
			pass
		except:
			print 'ERROR in updating driver graphics'

		#If reset, changes sports update keypad buttons
		if self.scoreboardDict.has_key(self.model):
			if self.scoreboardDict[self.model].scoreboard.switchKeypadFlag:
				self.keypad_view.updateNames(self.scoreboardDict[self.model].scoreboard.keyMap.Keypad_Keys)
				self.scoreboardDict[self.model].scoreboard.switchKeypadFlag=False

	def checkClickableEvents(self):
		'''
		Handles all clickable events every 10 ms.

		* **Clicking a power supply highlights it's LX's borders.**

		* **Clicking a header highlights the PCB borders it is connected to**

		* **Hide name of LX driver if not default jumpers**

		* **Double clicking a driver resets jumpers to default**

		* **Show name of LX driver if not default jumpers**

		* **Clicking a jumper updates driver behavior**

		* **Clicking a PCB highlights the header it is connected to**
		'''

		for model in self.scoreboardDict:

			#Clicking a power supply highlights it's LX's Borders
			for supply in self.scoreboardDict[model].psGraphicItemDict.keys():
				ps=self.scoreboardDict[model].psGraphicItemDict[supply].psClicked
				if ps[0]==True:

					self.scoreboardDict[model].psGraphicItemDict[supply].psClicked=(False,'')
					if self.scoreboardDict[model].psGraphicItemDict[supply].PS_I.isVisible():
						visible=True
					else:
						visible=False

					if self.scoreboardDict[model].scoreboard.powerSupplyDict[supply][0]:
						for driver in self.scoreboardDict[model].scoreboard.powerSupplyDict[supply][0]:
							var=(self.scoreboardDict[model].scoreboard.game.gameData['sportType']=='basketball' or \
							self.scoreboardDict[model].scoreboard.game.gameData['sportType']=='hockey') \
							and driver[:3]=='ETN' and supply=='2'
							if var:
								for function in self.scoreboardDict[model].scoreboard.functionDict.keys():
									if self.scoreboardDict[model].scoreboard.functionDict[function]['LXDriver'][:3]=='ETN':
										psChassis=self.scoreboardDict[model].scoreboard.functionDict[function]['psChassis']

										if psChassis==supply:
											self.scoreboardDict[model].pcbGraphicItemDict[function].border.setVisible(visible)
							else:
								self.scoreboardDict[model].lxGraphicItemDict[driver].border.setVisible(visible)
					else:
						for function in self.scoreboardDict[model].scoreboard.functionDict.keys():
							if self.scoreboardDict[model].scoreboard.functionDict[function]['LXDriver'][:3]=='ETN':
								psChassis=self.scoreboardDict[model].scoreboard.functionDict[function]['psChassis']
								if psChassis==supply:
									self.scoreboardDict[model].pcbGraphicItemDict[function].border.setVisible(visible)

			for driver in self.scoreboardDict[model].scoreboard.driverPosDict:
				#Clicking a header highlights the Digit Borders it is connected to
				lx=self.scoreboardDict[model].lxGraphicItemDict[driver].headerClicked
				if lx[0]==True:
					self.scoreboardDict[model].lxGraphicItemDict[driver].headerClicked=(False,'')
					if self.scoreboardDict[model].lxGraphicItemDict[driver].headerDict[lx[1]+'_1'].isVisible():
						visible=True
					else:
						visible=False

					for function in self.scoreboardDict[model].scoreboard.functionDict.keys():
						LXDriver=self.scoreboardDict[model].scoreboard.functionDict[function]['LXDriver']
						LXHeader=self.scoreboardDict[model].scoreboard.functionDict[function]['LXHeader']
						if LXDriver==driver and LXHeader==lx[1]:
							self.scoreboardDict[model].pcbGraphicItemDict[function].border.setVisible(visible)

					#Hide name of LX driver if not default jumpers
					self.scoreboardDict[model].lxGraphicItemDict[driver].labelGraphic.setVisible(self.scoreboardDict[model].scoreboard.lxDict[driver].checkDefaultJumpers())

				#Double Clicking a driver resets jumpers to default
				lx=self.scoreboardDict[model].lxGraphicItemDict[driver].doubleClicked
				if lx[0]==True:
					self.scoreboardDict[model].lxGraphicItemDict[driver].doubleClicked=(False,'')
					self.scoreboardDict[model].scoreboard.lxDict[driver].refreshStatus()
					self.scoreboardDict[model].showDefaultJumpers()

					#Show name of LX driver if not default jumpers
					self.scoreboardDict[model].lxGraphicItemDict[driver].labelGraphic.setVisible(self.scoreboardDict[model].scoreboard.lxDict[driver].checkDefaultJumpers())


				#Clicking a jumper updates driver behavior
				try:
					jumpers=self.scoreboardDict[model].scoreboard.lxDict[driver].jumpers
					for jumper in jumpers:
						j=self.scoreboardDict[model].lxGraphicItemDict[driver].jumperClicked
						if j[0]==True:
							self.scoreboardDict[model].lxGraphicItemDict[driver].jumperClicked=(False,'')
							if self.scoreboardDict[model].lxGraphicItemDict[driver].jumperDict[j[1]+'_1'].isVisible():
								self.scoreboardDict[model].scoreboard.lxDict[driver].setJumpers((j[1], True))
							else:
								self.scoreboardDict[model].scoreboard.lxDict[driver].setJumpers((j[1], False))
							if j[1]=='H16':
								self.scoreboardDict[model].scoreboard.lxDict[driver]._updateDisplay()
				except:
					pass

			#Clicking a digit highlights the header it is connected to
			for function in self.scoreboardDict[model].scoreboard.functionDict.keys():
				if self.scoreboardDict[model].pcbGraphicItemDict[function].pcbClicked==True:
					self.scoreboardDict[model].pcbGraphicItemDict[function].pcbClicked=(False,'')
					LXDriver=self.scoreboardDict[model].scoreboard.functionDict[function]['LXDriver']
					LXHeader=self.scoreboardDict[model].scoreboard.functionDict[function]['LXHeader']
					if self.scoreboardDict[model].pcbGraphicItemDict[function].border.isVisible():
						visible=True
					else:
						visible=False
					self.scoreboardDict[model].lxGraphicItemDict[LXDriver].headerDict[LXHeader+'_1'].setVisible(visible)

		#END Keypad button functions, Events, and Timer Called Functions

def main():
	'''Starts the application.'''
	print "ON"
	Simulation = QApplication(sys.argv)
	w = Simulation_Window()
	w.showMaximized()
	w.raise_()
	sys.exit(Simulation.exec_())

if __name__ == '__main__':
	main()
