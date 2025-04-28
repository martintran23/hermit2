import unittest
#from main import app, bookings
from server.oldapp import app
from server.app import app
from unittest.mock import patch
import json

class HermitTestCases(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.client = app.test_client()
        self.app.testing = True

        self.booking_data = {
            "property_id": "test123",
            "user_email": "test@example.com",
            "start_date": "2025-05-01",
            "end_date": "2025-05-05"
        }
    
    def test_homepage(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_rental_search(self):
        response = self.app.get('/api/properties?location=Metairie, LA')
        self.assertEqual(response.status_code, 200)
        listings = json.loads(response.data)
        self.assertIsInstance(listings, list)
        self.assertGreater(len(listings), 0)

    def test_search_with_invalid_location(self):
        response = self.app.get('/api/properties?location=InvalidCityNameXYZ')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_valid_property_id(self):
        listings_resp = self.app.get('/api/properties?location=Metairie, LA')
        listings = json.loads(listings_resp.data)

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
        pass

    def test_create_booking(self):
        response = self.app.post('/api/bookings', 
                                 data=json.dumps(self.booking_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("booking", data)

    def test_list_bookings(self):
        response = self.app.get('/api/bookings')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_get_user_bookings(self):
        self.app.post('/api/bookings', 
                      data=json.dumps(self.booking_data),
                      content_type='application/json')
        response = self.app.get('/api/bookings/user/test@example.com')
        self.assertEqual(response.status_code, 200)
        user_bookings = json.loads(response.data)
        self.assertTrue(any(b["user_email"] == "test@example.com" for b in user_bookings))

    def test_cancel_booking(self):
        create_resp = self.app.post('/api/bookings', 
                                    data=json.dumps(self.booking_data),
                                    content_type='application/json')
        booking = json.loads(create_resp.data)['booking']
        booking_id = booking["booking_id"]

        cancel_resp = self.app.delete(f'/api/bookings/{booking_id}')
        self.assertEqual(cancel_resp.status_code, 200)
    
    @patch('server.routes.properties.rentals_collection.find')
    def test_list_properties_success(self, mock_find):
        mock_find.return_value = []
        response = self.client.get('/api/properties?location=NewYork')
        self.assertEqual(response.status_code, 200)

    def test_list_properties_missing_location(self):
        response = self.client.get('/api/properties')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Location parameter is required', response.data)
        
if __name__ == '__main__':
    unittest.main()