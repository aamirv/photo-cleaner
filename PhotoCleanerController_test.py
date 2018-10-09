import unittest
from datetime import datetime
from PhotoCleanerController import PhotoCleanerController

class TestPhotoCleanerController(unittest.TestCase):

    def test_parse_directory_name_with_no_location(self):
        pcc = PhotoCleanerController()
        # test no info
        result = pcc.parse_directory_name("/Random/Directory/No/Info")
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        # test .
        result = pcc.parse_directory_name(".")
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        # test just year
        result = pcc.parse_directory_name("/Random/Directory/2008")
        expected_dt = datetime(2008, 1, 1)
        self.assertEqual(result[0], expected_dt)
        self.assertIsNone(result[1])
        # test just year/month
        result = pcc.parse_directory_name("/Random/Directory/200804")
        expected_dt = datetime(2008, 4, 1)
        self.assertEqual(result[0], expected_dt)
        self.assertIsNone(result[1])
        # test year/month/day
        result = pcc.parse_directory_name("/Random/Directory/20080406")
        expected_dt = datetime(2008, 4, 6)
        self.assertEqual(result[0], expected_dt)
        self.assertIsNone(result[1])
        # test non result
        result = pcc.parse_directory_name("/Random/Directory/208")
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        # test bad year
        with self.assertRaises(ValueError):
            result = pcc.parse_directory_name("/Random/Directory/1500")
        # test bad month
        with self.assertRaises(ValueError):
            result = pcc.parse_directory_name("/Random/Directory/20084")
        with self.assertRaises(ValueError):
            result = pcc.parse_directory_name("/Random/Directory/200813")
        # test bad day
        with self.assertRaises(ValueError):
            result = pcc.parse_directory_name("/Random/Directory/20080433")
        with self.assertRaises(ValueError):
            result = pcc.parse_directory_name("/Random/Directory/20090229")

    def test_parse_directory_name_with_location(self):
        pcc = PhotoCleanerController()
        # test just year
        result = pcc.parse_directory_name("/Random/Directory/2008 Japan")
        expected_dt = datetime(2008, 1, 1)
        expected_location = "Japan"
        self.assertEqual(result[0], expected_dt)
        self.assertEqual(result[1], expected_location)
        # test just year/month
        result = pcc.parse_directory_name("/Random/Directory/200804 Hawaii and Cozumel")
        expected_dt = datetime(2008, 4, 1)
        expected_location = "Hawaii and Cozumel"
        self.assertEqual(result[0], expected_dt)
        self.assertEqual(result[1], expected_location)
        # test year/month/day
        result = pcc.parse_directory_name("/Random/Directory/20080406 Berlin, Chicago")
        expected_dt = datetime(2008, 4, 6)
        expected_location = "Berlin, Chicago"
        self.assertEqual(result[0], expected_dt)
        self.assertEqual(result[1], expected_location)
        # test number to start location
        result = pcc.parse_directory_name("/Random/Directory/20080413 4 Islands of Hawaii")
        expected_dt = datetime(2008, 4, 13)
        expected_location = "4 Islands of Hawaii"
        self.assertEqual(result[0], expected_dt)
        self.assertEqual(result[1], expected_location)

if __name__ == '__main__':
    unittest.main()