import json

import app.game.clock


class LedSequences(object):
	"""methods must be called from inside a loop to be called faster than or equal to the 50ms minimum"""

	def __init__(self):
		""" PCB Schematic pin , Keypad Schematic designator, Name, Chap Name
			PIN_17 = LED_1 = strengthLedBottom			= Bar 1
			PIN_16 = LED_2 = strengthLedMiddleBottom	= Bar 2
			PIN_15 = LED_3 = strengthLedMiddleTop		= Bar 3
			PIN_14 = LED_4 = strengthLedTop				= Bar 4
			PIN_1  = LED_5 = topLed						= Clock Running (Baseball Example)
			PIN_13 = LED_6 = signalLed					= Signal Strength
			PIN_18 = LED_7 = batteryLed					= Battery Strength
		"""
		self.LedDict = dict()
		self.LedInfoDict = dict()
		self.LedPinList = ['P10', 'P11', 'P20', 'P6', 'P7', 'P8', 'P9']
		self.LedPinVsNumberDict = {
			'P20': '5', 'P11': '6', 'P10': '4', 'P9': '3', 'P8': '2', 'P7': '1', 'P6': '7'}
		self.LedPinVsKeypadPinDict = {
			'P20': '2', 'P11': '13', 'P10': '14', 'P9': '15', 'P8': '16', 'P7': '17', 'P6': '18'}
		self.LedPinVsFunctionNameDict = {
			'P20': 'topLed', 'P11': 'signalLed', 'P10': 'strengthLedTop', 'P9': 'strengthLedMiddleTop',
			'P8': 'strengthLedMiddleBottom', 'P7': 'strengthLedBottom', 'P6': 'batteryLed'}

		self.LedDict['object_type'] = 'Pin'
		self.LedDict['led_objects'] = dict()
		self.LedDict['led_objects']['component_type'] = 'led'
		for pin in self.LedPinList:
			self.LedDict['led_objects'][pin] = dict()
			self.LedDict['led_objects'][pin]['value'] = 0
			self.LedDict['led_objects'][pin]['keypad_pin_number'] = self.LedPinVsKeypadPinDict[pin]
			self.LedDict['led_objects'][pin]['led_id'] = self.LedPinVsNumberDict[pin]
			self.LedDict['led_objects'][pin]['function_name'] = self.LedPinVsFunctionNameDict[pin]

		self.timer = app.game.clock.Clock(count_up=True, max_seconds=3, clock_name='led_sequence')
		self.transfer_cycle_flag = False

	def get_led_dict_string(self):
		temp_dict = dict()
		temp_dict['led_objects'] = dict()
		for pin in self.LedPinList:
			temp_dict['led_objects'][pin] = dict()
			temp_dict['led_objects'][pin]['value'] = self.LedDict['led_objects'][pin]['value']
		string = json.dumps(temp_dict)
		return string

	def set_led(self, function_name, value):
		for pin in self.LedPinList:
			if self.LedDict['led_objects'][pin]['function_name'] == function_name:
				self.LedDict['led_objects'][pin]['value'] = value
				print(self.LedDict['led_objects'][pin]['function_name'], 'set to', value)
				break

	def all_off(self):
		for pin in self.LedPinList:
			self.LedDict['led_objects'][pin]['value'] = 0
		print('All LEDs Off')

	def battery_test(self, enable=False):
		"""Continue this method while in this mode (until timeout)"""
		if enable:
			print('[Signal Strength] = OFF')
			self.set_led('signalLed', 0)
			print('[Battery  Strength] = ON')
			self.set_led('batteryLed', 1)
			print('[Bar 1], [Bar 2], [Bar 3], [Bar 4] show battery strength')
			print('battery_test_sequence END')
		return enable

	def time_of_day(self, enable=False):
		"""
		Repeat toggling the [Clock Running] LED until KD enters Connected Dark Sequence or until RD exits Time of Day Mode
		"""
		if enable:
			read = self.timer.currentTime() * 1000
			if 0 <= read < 1000:
				print('All LEDs = OFF', read, 'ms')
			elif 1000 <= read < 1800:
				print('[Clock Running] = ON', read, 'ms')
			elif 1800 <= read < 3000:
				print('[Clock Running] = OFF', read, 'ms')
			elif 3000 <= read < 3800:
				print('[Clock Running] = ON', read, 'ms')
			elif 3800 <= read:
				print('[Clock Running] = OFF', read, 'ms')
				self.timer.reset_()
				print('time_of_day_sequence END')
		return enable
