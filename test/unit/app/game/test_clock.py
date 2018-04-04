from unittest import TestCase
import app.game.clock
import time


class TestClock(TestCase):
	def setUp(self):
		self.clock = app.game.clock.Clock(
			count_up=False, max_seconds=10, resolution=0.01,
			hours_flag=False, clock_name='generic', internal_clock=False)

	def test_game_data_update(self):
		name = 'periodClock'
		game_data = {}
		game_data = self.clock.game_data_update(game_data, name=name)
		full_name = name + '_secondsUnits'
		self.assertIn(full_name, game_data)

	def test_run_clock(self):
		self.clock.start_()
		while self.clock.running:
			print (
				self.clock.timeUnitsDict['minutesTens'], self.clock.timeUnitsDict['minutesUnits'],
				self.clock.timeUnitsDict['secondsTens'], self.clock.timeUnitsDict['secondsUnits'],
				self.clock.timeUnitsDict['tenthsUnits'], self.clock.timeUnitsDict['hundredthsUnits'])
			time.sleep(0.01)
			if self.clock.timeUnitsDict['secondsUnits'] <= 9:
				self.clock.stop_()
				self.clock.kill_()
				break
