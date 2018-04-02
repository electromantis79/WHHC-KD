from unittest import TestCase
import app.serial_IO.serial_packet as packet
import app.game.game as game
import app.utils.reads
import os


class TestSerialPacket(TestCase):
	def setUp(self):
		os.chdir('/Repos/MP2ASCII/app')
		self.config_dict = app.utils.reads.read_config()
		self.game = game.Basketball(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

	def test__string_eater_one_place(self):
		packet_ = 'B12345'
		self.assertEquals(
			'12345', self.packet._string_eater(packet_, places=1))

	def test__string_eater_five_places(self):
		packet_ = 'B12345'
		self.assertEquals(
			'5', self.packet._string_eater(packet_, places=5,))

	def test__string_eater_none(self):
		packet_ = None
		self.assertIsNone(
			self.packet._string_eater(packet_, places=5,))

	def _encode_decode_encode(self):
		print "\nCreate ASCII string"
		string = self.packet.encode_packet(print_string=True)
		print "\nLoad String back into game"
		self.packet.encode_packet(print_string=True, packet=string)
		print "\nPrint string again to look for changes"
		final_string = self.packet.encode_packet(print_string=True)
		self.assertEqual(string, final_string)

	def test_basketball_encode_decode_encode(self):
		self._encode_decode_encode()

	def _with_vars(self):
		game_variable_name = 'period'
		team_variable_name = 'scoreUnits'
		game_variable = 9
		team_variable = 6
		print
		print game_variable_name, game_variable, 'HOME:', team_variable_name, team_variable
		self.game.set_game_data(game_variable_name, game_variable, places=1)
		self.game.set_team_data(self.game.home, team_variable_name, team_variable)

		self._encode_decode_encode()

		self.assertEqual(
			game_variable, self.game.get_game_data(game_variable_name))
		self.assertEqual(
			team_variable, self.game.get_team_data(self.game.home, team_variable_name))

	def test_basketball_encode_decode_encode_with_vars(self):
		self._with_vars()

	def test_football_encode_decode_encode(self):
		self.game = game.Football(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def test_football_encode_decode_encode_with_vars(self):
		self.game = game.Football(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()

	def test_baseball_encode_decode_encode(self):
		self.game = game.Baseball(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def test_baseball_encode_decode_encode_with_vars(self):
		self.game = game.Baseball(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()

	def test_soccer_encode_decode_encode(self):
		self.game = game.Soccer(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def test_soccer_encode_decode_encode_with_vars(self):
		self.game = game.Soccer(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()

	def test_hockey_encode_decode_encode(self):
		self.game = game.Hockey(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def test_hockey_encode_decode_encode_with_vars(self):
		self.game = game.Hockey(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()

	def _test_cricket_encode_decode_encode(self):  # Remove _ when test used
		self.game = game.Cricket(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def _test_cricket_encode_decode_encode_with_vars(self):  # Remove _ when test used
		self.game = game.Cricket(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()

	def _test_racetrack_encode_decode_encode(self):  # Remove _ when test used
		self.game = game.Racetrack(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def _test_racetrack_encode_decode_encode_with_vars(self):  # Remove _ when test used
		self.game = game.Racetrack(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()

	def test_stat_encode_decode_encode(self):
		self.game = game.Stat(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def test_stat_encode_decode_encode_with_vars(self):
		self.game = game.Stat(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()

	def _test_game_encode_decode_encode(self):  # Remove _ when test used
		self.game = game.Game(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._encode_decode_encode()

	def _test_game_encode_decode_encode_with_vars(self):  # Remove _ when test used
		self.game = game.Game(self.config_dict)
		self.packet = packet.SerialPacket(self.game)

		self._with_vars()
