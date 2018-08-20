import app.game.clock


class LedSequences(object):
	"""methods must be called from inside a loop to be called faster than or equal to the 50ms minimum"""

	def __init__(self, led_dict):
		""" PCB Schematic pin , Keypad Schematic designator, Name, Chap Name
			PIN_17 = LED_1 = strengthLedBottom			= Bar 1
			PIN_16 = LED_2 = strengthLedMiddleBottom	= Bar 2
			PIN_15 = LED_3 = strengthLedMiddleTop		= Bar 3
			PIN_14 = LED_4 = strengthLedTop				= Bar 4
			PIN_1  = LED_5 = topLed						= Clock Running (Baseball Example)
			PIN_13 = LED_6 = signalLed					= Signal Strength
			PIN_18 = LED_7 = batteryLed					= Battery Strength
		"""
		self.LedDict = led_dict
		self.timer = app.game.clock.Clock(count_up=True, max_seconds=3, clock_name='led_sequence')
		self.transfer_cycle_flag = False

	def get_led_dict_string(self):
		string = '$'
		for key in self.LedDict:
			string += key + self.LedDict[key]
		return string

	def set_led(self, key, value):
		# Example - key = 'L5' for led 5 (topLed), value = '1' or '0'
		self.LedDict[key] = value

	def battery_test(self, enable=False):
		"""Continue this method while in this mode (until timeout)"""
		if enable:
			print('[Signal Strength] = OFF')
			self.set_led('L6', '0')
			print('[Battery  Strength] = ON')
			self.set_led('L7', '1')
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
