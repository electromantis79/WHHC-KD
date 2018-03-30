from behave import *
import os

use_step_matcher('re')


@given('a basketball game')
def step_impl(context):
	import app.game.game
	os.chdir('/Repos/MP2ASCII/app')
	context.game = app.game.game.Basketball()


@given("a basketball packet")
def step_impl(context):
	import app.serial_IO.serial_packet
	context.packet = app.serial_IO.serial_packet.SerialPacket(context.game)


@when('a basketball packet is encoded')
def step_impl(context):
	context.string = context.packet.encode_packet()


@then('a basketball packet of the correct format is returned')
def step_impl(context):
	print context.string


@given("a football game")
def step_impl(context):
	import app.game.game
	os.chdir('/Repos/MP2ASCII/app')
	context.game = app.game.game.Football()


@given("a football packet")
def step_impl(context):
	import app.serial_IO.serial_packet
	context.packet = app.serial_IO.serial_packet.SerialPacket(context.game)


@when("a football packet is encoded")
def step_impl(context):
	context.string = context.packet.encode_packet()


@then("a football packet of the correct format is returned")
def step_impl(context):
	print context.string
