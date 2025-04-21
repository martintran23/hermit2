import unittest
from main import app, bookings
import json

class HermitTestCases(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

if __name__ == '__main__':
    unittest.main()