from buildtimetrend.trend import Trend
import unittest

class TestTrend(unittest.TestCase):

    def setUp(self):
        self.trend = Trend()

    def test_nofile(self):
	# function should return false when file doesn't exist
        self.assertFalse(self.trend.gather_data('nofile.xml'))
        self.assertFalse(self.trend.gather_data(''))

	# function should thrown an error  when no filename is set
        self.assertRaises(TypeError, self.trend.gather_data)

if __name__ == '__main__':
    unittest.main()
