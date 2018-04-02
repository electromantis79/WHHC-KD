from unittest import TestCase
import cProfile, pstats, StringIO
import os

import app.address_mapping
import app.utils.functions
import app.utils.reads


class TestAddressMapping(TestCase):
	def setUp(self):
		os.chdir('/Repos/MP2ASCII/app')
		self.config_dict = app.utils.reads.read_config()
		self.game = app.utils.functions.select_sport_instance(self.config_dict, number_of_teams=2)
		self.addr = app.address_mapping.AddressMapping(game=self.game)

	def test_profile_map(self):
		pr = cProfile.Profile()
		pr.enable()
		self.addr.map()  # Function being timed
		pr.disable()
		s = StringIO.StringIO()
		sortby = 'cumulative'
		ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
		ps.print_stats()
		print 'stat', s.getvalue()
