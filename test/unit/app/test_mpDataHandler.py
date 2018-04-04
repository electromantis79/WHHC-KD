from unittest import TestCase
import app.mp_data_handler


class TestMpDataHandler(TestCase):
	def setUp(self):
		self.mp = app.mp_data_handler.MpDataHandler()

	def test_gbw_to_mp_address(self):
		group, bank, word = 1, 1, 1
		self.assertEqual(0b00000, self.mp.gbw_to_mp_address(group, bank, word))
		group, bank, word = 2, 2, 3
		self.assertEqual(0b10110, self.mp.gbw_to_mp_address(group, bank, word))
