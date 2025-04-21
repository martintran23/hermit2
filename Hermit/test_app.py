import unittest
from main import app, bookings
import json

class HermitTestCases(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_rental_search(self):
        pass

    def test_search_with_invalid_location(self):
        pass

    def test_valid_property_id(self):
        pass

    def test_invalid_property_id(self):
        invalid_id = "invalid-id-12345"
        response  = self.app.get(f"/property/{invalid_id}")
        self.assertIn(response.status_code, [400, 404])
        try:
            data = response.get_json(force = True)
        except Exception:
            data = None
        self.assertTrue(
            data is None or isinstance(data, dict) and ("error" in data or data == {}),
            "Expected an error message or empty JSON object"
        )

    def test_booking(self):
        pass

if __name__ == '__main__':
    unittest.main()