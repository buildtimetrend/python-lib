from buildtimetrend.trend import Trend
import unittest

TEST_SAMPLE_FILE = 'test/testsample_buildtimes.xml'

class TestTrend(unittest.TestCase):

    def setUp(self):
        self.trend = Trend()

    def test_nofile(self):
	# function should return false when file doesn't exist
        self.assertFalse(self.trend.gather_data('nofile.xml'))
        self.assertFalse(self.trend.gather_data(''))

	# function should thrown an error  when no filename is set
        self.assertRaises(TypeError, self.trend.gather_data)

    def test_gather_data(self):
	# read and parse sample file
        self.assertTrue(self.trend.gather_data(TEST_SAMPLE_FILE))

	# test number of builds and stages
	self.assertEquals(3, len(self.trend.builds))
	self.assertEquals(5, len(self.trend.stages))

	# test buildnames
	self.assertListEqual(['#1', '11.1', '#3'], self.trend.builds)

	# test stages (names + duration)
	self.assertDictEqual(
		{'stage1': ['4', '3', '2'], 'stage2': ['5', '6', '7'],
		'stage3': ['10', '11', '12'], 'stage4': ['1', 0, '3'],
		'stage5': [0, '6', 0]},
		self.trend.stages)


if __name__ == '__main__':
    unittest.main()
