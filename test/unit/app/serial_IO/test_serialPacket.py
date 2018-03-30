from unittest import TestCase


class TestSerialPacket(TestCase):
	def setUp(self):
		import app.serial_IO.serial_packet as packet
		import app.game.game as game
		import os
		os.chdir('/Repos/MP2ASCII/app')
		self.game = game.Basketball()
		self.packet = packet.SerialPacket(self.game)

	def test__string_eater_one_place(self):
		packet = 'B12345'
		self.assertEquals(
			self.packet._string_eater(packet, places=1,), '12345')

	def test__string_eater_five_places(self):
		packet = 'B12345'
		self.assertEquals(
			self.packet._string_eater(packet, places=5,), '5')
