from unittest import TestCase
import cProfile
import pstats
import StringIO
import os

import app.address_mapping
import app.utils.functions
import app.utils.reads


class TestAddressMappingBaseballOne(TestCase):
	def setUp(self):
		os.chdir('/Repos/MP2ASCII/app')
		self.config_dict = app.utils.reads.read_config()
		self.config_dict['sport'] = 'MPBASEBALL1'
		self.game = app.utils.functions.select_sport_instance(self.config_dict, number_of_teams=2)
		self.addr = app.address_mapping.AddressMapping(game=self.game)

	def _profile_function(self, passed_function, args=None):
		pr = cProfile.Profile()
		if args is not None:
			pr.enable()
			passed_function(args)  # Function being timed
			pr.disable()
		else:
			pr.enable()
			passed_function()  # Function being timed
			pr.disable()
		s = StringIO.StringIO()
		sortby = 'cumulative'
		ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
		ps.print_stats()
		print 'stat', s.getvalue()

	def test_profile_map(self):
		self._profile_function(self.addr.map)

	def test_unmap_home_score(self):
		high_nibble = 6
		low_nibble = 9
		word_0 = self.addr.mp.encode(1, 2, 1, 1, 0, high_nibble, low_nibble, 0, 0)
		word_list = [word_0]
		self.addr.un_map(word_list)
		self.assertEqual(high_nibble, self.addr.game.get_team_data(self.game.home, 'scoreTens'))
		self.assertEqual(low_nibble, self.addr.game.get_team_data(self.game.home, 'scoreUnits'))

	def test_unmap_guest_score(self):
		high_nibble = 6
		low_nibble = 9
		word_0 = self.addr.mp.encode(1, 2, 2, 1, 0, high_nibble, low_nibble, 0, 0)
		word_list = [word_0]
		self.addr.un_map(word_list)
		self.assertEqual(high_nibble, self.addr.game.get_team_data(self.game.guest, 'scoreTens'))
		self.assertEqual(low_nibble, self.addr.game.get_team_data(self.game.guest, 'scoreUnits'))

	def test_unmap_guest_score_profile(self):
		high_nibble = 6
		low_nibble = 9
		word_0 = self.addr.mp.encode(1, 2, 2, 1, 0, high_nibble, low_nibble, 0, 0)
		word_list = [word_0]

		self._profile_function(self.addr.un_map, word_list)
