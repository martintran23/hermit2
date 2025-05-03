import unittest
#from main import app, bookings
from server.app import app
from unittest.mock import patch
from bson import ObjectId
import json
import uuid

class HermitTestCases(unittest.TestCase):
    def setUp(self):
        #set up test client
        self.app = app.test_client()
        self.client = app.test_client()
        self.app.testing = True
        # Mock user data for login/signup
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass"
        }
        # Simulate user signup and login for test setup
        self.app.post('/api/signup', data=json.dumps(self.user_data), content_type='application/json')
        self.app.post('/api/login', data=json.dumps(self.user_data), content_type='application/json')
        # Class-level variable to store all support requests across tests, resets each test
        self.support_requests = []
        # Sample booking data used in multiple tests
        self.booking_data = {
            "property_id": "test123",
            "user_email": "test@example.com",
            "start_date": "2025-05-01",
            "end_date": "2025-05-05"
        }
    
    def test_homepage(self):
        # Test that the homepage returns HTTP 200
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_rental_search(self):
        # Test that rental search returns a list of properties for a valid location
        response = self.app.get('/api/properties?location=Metairie, LA')
        self.assertEqual(response.status_code, 200)
        listings = json.loads(response.data)
        self.assertIsInstance(listings, list)
        self.assertGreater(len(listings), 0)

    def test_search_with_invalid_location(self):
        # Test how the app handles a search for an invalid location
        response = self.app.get('/api/properties?location=InvalidCityNameXYZ')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_invalid_property_id(self):
        # Test how the system responds to a request for a non-existent property ID
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

    def test_create_booking(self):
        # Test creating a booking with valid data
        response = self.app.post('/api/bookings', 
                                 data=json.dumps(self.booking_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("booking", data)

    def test_list_bookings(self):
        # Test listing all bookings (should return a list)
        response = self.app.get('/api/bookings')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_get_user_bookings(self):
        # Test retrieving bookings by user email
        self.app.post('/api/bookings', 
                      data=json.dumps(self.booking_data),
                      content_type='application/json')
        response = self.app.get('/api/bookings/user/test@example.com')
        self.assertEqual(response.status_code, 200)
        user_bookings = json.loads(response.data)
        self.assertTrue(any(b["user_email"] == "test@example.com" for b in user_bookings))

    def test_cancel_booking(self):
        # Test canceling a booking that was just created
        create_resp = self.app.post('/api/bookings', 
                                    data=json.dumps(self.booking_data),
                                    content_type='application/json')
        booking = json.loads(create_resp.data)['booking']
        booking_id = booking["booking_id"]

        cancel_resp = self.app.delete(f'/api/bookings/{booking_id}')
        self.assertEqual(cancel_resp.status_code, 200)
    
    @patch('server.routes.properties.rentals_collection.find')
    def test_list_properties_success(self, mock_find):
        # Test mocked property search to simulate DB returning an empty list
        mock_find.return_value = []
        response = self.client.get('/api/properties?location=NewYork')
        self.assertEqual(response.status_code, 200)

    def test_list_properties_missing_location(self):
         # Test behavior when the location parameter is omitted in search
        response = self.client.get('/api/properties')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Location parameter is required', response.data)
    
    def test_signup_success(self):
        unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        signup_data = {
            "email": unique_email,
            "password": "securepassword123"
        }
        response = self.app.post('/api/signup',
                                 data=json.dumps(signup_data),
                                 content_type='application/json')
        self.assertIn(response.status_code, [200, 201])
        data = json.loads(response.data)
        self.assertIn("message", data)

    def test_signup_missing_password(self):
        # Signup data with missing password
        signup_data = {
            "email": "user@example.com"
        }

        response = self.app.post(
            '/api/signup',
            data=json.dumps(signup_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_login_success(self):
        # Step 1: Create a new user for login
        signup_data = {
            "email": "loginuser@example.com",
            "password": "testpass"
        }
        self.app.post(
            '/api/signup',
            data=json.dumps(signup_data),
            content_type='application/json'
        )

        # Step 2: Attempt login with correct credentials
        login_data = {
            "email": "loginuser@example.com",
            "password": "testpass"
        }
        response = self.app.post(
            '/api/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)

    def test_login_invalid_credentials(self):
        # Attempt login with incorrect or nonexistent credentials
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpass"
        }

        response = self.app.post(
            '/api/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn("error", data)
    
    def login_session(self, email):
        """
        Helper function to simulate a logged-in user by setting the 'email' 
        in the session. This mimics the login process during tests.
        """
        with self.client.session_transaction() as sess:
            sess['email'] = email

    def test_redirect_if_not_logged_in(self):
        # Remove the email from the session to simulate a user not logged in
        # Remove email from session to simulate logout
        with self.client.session_transaction() as sess:
            sess.pop('email', None)
        response = self.client.get('/host/listings')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_show_host_listings_if_logged_in(self):
        # Simulate a logged-in user by setting the email in the session
        self.login_session('host@example.com')
        response = self.client.get('/host/listings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'host@example.com', response.data)

    def test_get_listings_authenticated(self):
        # Test for authenticated users trying to get listings
        self.login_session('host@example.com')  # Simulate login
        response = self.client.get('/api/listings')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_get_listings_unauthenticated(self):
        # Test for unauthenticated users trying to get listings
        response = self.client.get('/api/listings')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Login required')

    def test_get_listings_empty(self):
        # Test for authenticated user with no listings in the database
        self.login_session('test@example.com')
        response = self.client.get('/api/listings')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_create_listing_missing_fields(self):
        # Tests reject listing creation with missing fields.
        self.login_session('host@example.com')
        data = {
            "title": "Test",
            "address": "123 Street"
            # missing price, description, image_url
        }
        response = self.client.post('/api/listings', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing fields", response.json["error"])

    def test_create_listing_unauthenticated(self):
        # Tests reject unauthenticated listing creation.
        data = {
            "title": "Title",
            "address": "Addr",
            "price": 100,
            "description": "Desc",
           "image_url": "img.jpg"
        }
        response = self.client.post('/api/listings', json=data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Login required", response.json["error"])

    def test_update_listing_unauthenticated(self):
        # Tests reject unauthenticated PUT /api/listings/<id>.
        response = self.client.put('/api/listings/123', json={"title": "New"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("Login required", response.json["error"])

    def test_update_listing_invalid_id(self):
        # Tests return 404 for updating non-existent listing.
        self.login_session('host@example.com')
        response = self.client.put('/api/listings/000000000000000000000000', json={"title": "Updated"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("Listing not found", response.json["error"])

    def test_delete_listing_unauthenticated(self):
        # Tests reject unauthenticated DELETE /api/listings/<id>.
        response = self.client.delete('/api/listings/123')
        self.assertEqual(response.status_code, 401)
        self.assertIn("Login required", response.json["error"])

    def test_delete_listing_invalid_id(self):
        # Tests if return 404 for deleting non-existent listing.
        self.login_session('host@example.com')
        response = self.client.delete('/api/listings/000000000000000000000000')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Listing not found", response.json["error"])

    def test_modify_booking_invalid_date(self):
        # Test that invalid date input is handled
        with self.app.session_transaction() as sess:
            sess['email'] = 'user@example.com'  # Simulate logged-in user
        response = self.app.post('/modify-booking?booking_id=1', data={
            'start_date': 'invalid-date',
            'end_date': 'invalid-date'
        })
        self.assertNotIn('Your booking dates have been updated.', response.data.decode())
    
    def test_support_page_unauthenticated(self):
        # Test that an unauthenticated user is redirected to the login page.
        response = self.client.get('/support')
        # Ensure the user is redirected to the login page
        self.assertEqual(response.status_code, 302)  # Check for redirection status code
        self.assertEqual(response.location, '/login')  # Check if the redirection location is the login page

    def test_view_previous_tickets(self):
        # Test that a user sees their previously submitted tickets.
        self.login_session('testuser@example.com')
        # Submit a support request
        self.client.post('/support', data={
            'booking_id': '12345',
            'message': 'I need assistance with my booking.'
        })
        response = self.client.get('/support')
        self.assertIn(b'12345', response.data)  # Check if booking_id is present in the response
        self.assertIn(b'I need assistance with my booking.', response.data)  # Check if message is present
    
    def test_my_bookings_page_unauthenticated(self):
        # Test that an unauthenticated user is redirected to the login page when trying to access /my-bookings.
        response = self.client.get('/my-bookings')
        
        # Assert that the user is redirected to the login page (status code 302 and Location header)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/login')

    def test_my_bookings_page_authenticated(self):
        # Test that an authenticated user can access their bookings page.
        self.login_session('testuser@example.com')
        response = self.client.get('/my-bookings')
        # Check if the loading message is present (this indicates the page is attempting to load bookings)
        self.assertIn(b'Loading your bookings\xe2\x80\xa6', response.data)  # Ensure the correct loading message is displayed

    def test_my_bookings_page_with_no_user(self):
        # Test that a user is redirected to login page if there is no user in the session.
        with self.client.session_transaction() as sess:
            sess['email'] = None
        response = self.client.get('/my-bookings')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/login')
        
if __name__ == '__main__':
    unittest.main()