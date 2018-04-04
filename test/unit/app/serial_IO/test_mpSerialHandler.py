from unittest import TestCase
import app.serial_IO.mp_serial


class TestMpSerialHandler(TestCase):
	def setUp(self):
		self.serial = app.serial_IO.mp_serial.MpSerialHandler(serial_input_type='MP')

	def test_serial_output(self):
		self.serial.serial_output('test')

	def test_serial_input(self):
		self.serial.serial_input()
