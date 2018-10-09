import unittest
from PhotoCleaner import PhotoCleaner

class TestPhotoCleaner(unittest.TestCase):

    def test_is_valid_filetype(self):
        pc = PhotoCleaner()
        self.assertTrue(pc.is_valid_filetype('./aamir1.jpg'))
        self.assertFalse(pc.is_valid_filetype('/Users/aamir/Photos/fake'))
        self.assertFalse(pc.is_valid_filetype('./home.png'))

if __name__ == '__main__':
    unittest.main()