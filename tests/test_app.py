import unittest
from server.app import app
from flask import session
from unittest.mock import patch, MagicMock
from bson import ObjectId
import json
import uuid
from datetime import datetime
import requests


# ─── Chat API Tests ────────────────────────────────────────────────────────
class ChatApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_get_messages_unauthenticated(self):
        resp = self.client.get('/api/chat/booking1')
        self.assertEqual(resp.status_code, 401)
        self.assertIn(b'Login required', resp.data)

    @patch('server.routes.api.chat.chats')
    def test_post_and_get_messages(self, mock_chats):
        # log in
        with self.client.session_transaction() as sess:
            sess['email'] = 'user@ex.com'
        # empty message
        resp = self.client.post('/api/chat/booking1', json={'message': '   '})
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'Empty message', resp.data)
        # successful post
        mock_chats.insert_one.return_value = MagicMock(
            inserted_id=ObjectId('507f1f77bcf86cd799439011')
        )
        resp = self.client.post('/api/chat/booking1', json={'message': 'hello'})
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual(data['booking_id'], 'booking1')
        self.assertEqual(data['user_email'], 'user@ex.com')
        # now mock a stored message and GET
        fake_doc = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'booking_id': 'booking1',
            'user_email': 'user@ex.com',
            'message': 'hi',
            'timestamp': datetime.utcnow()
        }
        mock_chats.find.return_value.sort.return_value = [fake_doc]
        resp = self.client.get('/api/chat/booking1')
        self.assertEqual(resp.status_code, 200)
        msgs = json.loads(resp.data)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]['booking_id'], 'booking1')

# ─── Listings API Tests ────────────────────────────────────────────────────
class ListingsApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_get_listings_unauthenticated(self):
        resp = self.client.get('/api/listings')
        self.assertEqual(resp.status_code, 401)
        self.assertIn(b'Login required', resp.data)

    @patch('server.routes.api.listings.host_listings')
    def test_get_listings_empty_and_nonempty(self, mock_coll):
        # login
        with self.client.session_transaction() as sess:
            sess['email'] = 'host@ex.com'
        # empty result
        mock_coll.find.return_value = []
        resp = self.client.get('/api/listings')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), [])
        # one listing
        fake = {
            '_id': ObjectId('507f1f77bcf86cd799439012'),
            'host_email': 'host@ex.com',
            'title': 'T','address':'A','price':100,
            'description':'D','image_url':'I'
        }
        mock_coll.find.return_value = [fake]
        resp = self.client.get('/api/listings')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data[0]['id'], '507f1f77bcf86cd799439012')

    @patch('server.routes.api.listings.host_listings')
    def test_create_update_delete_listing(self, mock_coll):
        # unauthenticated create
        resp = self.client.post('/api/listings', json={'title':'T'})
        self.assertEqual(resp.status_code, 403)
        # login as host
        with self.client.session_transaction() as sess:
            sess['email'] = 'host@ex.com'
            sess['role']  = 'host'
        # missing fields
        resp = self.client.post('/api/listings', json={'title':'T'})
        self.assertEqual(resp.status_code, 400)
        # create
        fake_ins = MagicMock(inserted_id=ObjectId('507f1f77bcf86cd799439013'))
        mock_coll.insert_one.return_value = fake_ins
        payload = {'title':'T','address':'A','price':1,'description':'D','image_url':'I'}
        resp = self.client.post('/api/listings', json=payload)
        self.assertEqual(resp.status_code, 201)
        # update not found
        mock_coll.update_one.return_value = MagicMock(matched_count=0)
        resp = self.client.put('/api/listings/507f1f77bcf86cd799439014', json={'title':'New'})
        self.assertEqual(resp.status_code, 404)
        # update ok
        mock_coll.update_one.return_value = MagicMock(matched_count=1)
        resp = self.client.put('/api/listings/507f1f77bcf86cd799439014', json={'title':'New'})
        self.assertEqual(resp.status_code, 200)
        # delete not found
        mock_coll.delete_one.return_value = MagicMock(deleted_count=0)
        resp = self.client.delete('/api/listings/507f1f77bcf86cd799439015')
        self.assertEqual(resp.status_code, 404)
        # delete ok
        mock_coll.delete_one.return_value = MagicMock(deleted_count=1)
        resp = self.client.delete('/api/listings/507f1f77bcf86cd799439015')
        self.assertEqual(resp.status_code, 200)

# ─── Reviews API Tests ─────────────────────────────────────────────────────
class ReviewsApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_get_reviews_empty_and_nonempty(self):
        with patch('server.routes.api.reviews.reviews_col') as mock_col:
            mock_col.find.return_value.sort.return_value = []
            resp = self.client.get('/api/reviews/prop1')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(json.loads(resp.data), [])
            # one review
            fake = {
                '_id': ObjectId('507f1f77bcf86cd799439016'),
                'property_id':'prop1','user_email':'u@e.com',
                'rating':5,'comment':'Good','timestamp':datetime.utcnow()
            }
            mock_col.find.return_value.sort.return_value = [fake]
            resp = self.client.get('/api/reviews/prop1')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(json.loads(resp.data)[0]['rating'], 5)

    def test_post_review(self):
        # unauthenticated
        resp = self.client.post('/api/reviews/prop1', json={'rating':5,'comment':'Nice'})
        self.assertEqual(resp.status_code, 401)
        # login
        with self.client.session_transaction() as sess:
            sess['email'] = 'u@e.com'
        # invalid rating
        resp = self.client.post('/api/reviews/prop1', json={'rating':6})
        self.assertEqual(resp.status_code, 400)
        # valid
        with patch('server.routes.api.reviews.reviews_col') as mock_col:
            mock_col.insert_one.return_value = MagicMock(inserted_id=ObjectId('507f1f77bcf86cd799439017'))
            resp = self.client.post('/api/reviews/prop1', json={'rating':4,'comment':'Nice'})
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(json.loads(resp.data)['rating'], 4)

# ─── Properties API Tests ─────────────────────────────────────────────────
class PropertiesApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('server.routes.properties.rentals_collection')
    def test_missing_location(self, mock_coll):
        resp = self.client.get('/api/properties')
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'Location parameter is required', resp.data)

    def test_invalid_limit_offset(self):
        resp = self.client.get('/api/properties?location=LA&limit=foo')
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'limit and offset must be integers', resp.data)

    @patch('server.routes.properties.rentals_collection')
    def test_cached_results(self, mock_coll):
        mock_coll.find.return_value = [{'property_id':'p1','search_location':'LA','_id':'123'}]
        resp = self.client.get('/api/properties?location=LA')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data)[0]['_id'], '123')

    @patch('server.routes.properties.requests.get')
    @patch('server.routes.properties.rentals_collection')
    def test_external_api_404_and_success(self, mock_coll, mock_get):
        # force cache error
        mock_coll.find.side_effect = Exception()
        fake_resp = MagicMock()
        fake_resp.raise_for_status.return_value = None
        fake_resp.json.return_value = {'totalResultCount': 0}
        mock_get.return_value = fake_resp
        resp = self.client.get('/api/properties?location=NY')
        self.assertEqual(resp.status_code, 404)
        # now one listing from API
        fake_resp.json.return_value = {
            'totalResultCount':1,
            'listings':[{'property_id':'p2'}]
        }
        resp = self.client.get('/api/properties?location=NY')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data)[0]['property_id'], 'p2')

    @patch('server.routes.properties.requests.get')
    def test_external_api_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("boom")
        resp = self.client.get('/api/properties?location=TX')
        self.assertEqual(resp.status_code, 500)

# ─── Page‐only Routes Tests ─────────────────────────────────────────────────
class PageRoutesAdditionalTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_become_host_page(self):
        # redirect if not logged in
        resp = self.client.get('/become-host')
        self.assertEqual(resp.status_code, 302)
        # now logged in
        with self.client.session_transaction() as sess:
            sess['email'] = 'h@e'; sess['role']='host'
        resp = self.client.get('/become-host')
        self.assertEqual(resp.status_code, 200)

    def test_chat_page(self):
        resp = self.client.get('/chat/abc')
        self.assertEqual(resp.status_code, 302)
        with self.client.session_transaction() as sess:
            sess['email']='u@e'
        resp = self.client.get('/chat/abc')
        self.assertEqual(resp.status_code, 200)

    def test_payments_pages(self):
        resp = self.client.get('/payments/123')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/payments/123/confirm')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'123', resp.data)

    def test_reviews_page(self):
        resp = self.client.get('/reviews/prop1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'prop1', resp.data)

class HermitTestCases(unittest.TestCase):
    def setUp(self):
        # set up test client
        self.app = app.test_client()
        self.client = app.test_client()
        self.app.testing = True
        # Mock user data for login/signup
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass"
        }
        # Simulate user signup and login for test setup
        self.app.post('/api/signup',
                      data=json.dumps(self.user_data),
                      content_type='application/json')
        self.app.post('/api/login',
                      data=json.dumps(self.user_data),
                      content_type='application/json')
        # Class-level variable to store all support requests across tests, resets each test
        self.support_requests = []
        # Sample booking data used in multiple tests
        self.booking_data = {
            "property_id": "test123",
            "start_date":  "2025-05-01",
            "end_date":    "2025-05-05"
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
        response = self.app.get(f"/property/{invalid_id}")
        self.assertIn(response.status_code, [400, 404])
        try:
            data = response.get_json(force=True)
        except Exception:
            data = None
        self.assertTrue(
            data is None
            or isinstance(data, dict)
            and ("error" in data or data == {}),
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
        self.assertTrue(any(b["user_email"] == "test@example.com"
                            for b in user_bookings))

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
        signup_data = {"email": "user@example.com"}
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
        self.app.post('/api/signup',
                      data=json.dumps(signup_data),
                      content_type='application/json')
        # Step 2: Attempt login with correct credentials
        response = self.app.post('/api/login',
                                 data=json.dumps(signup_data),
                                 content_type='application/json')
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
            sess['role'] = 'host'

    def test_redirect_if_not_logged_in(self):
        # Remove the email from the session to simulate a user not logged in
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
        self.login_session('host@example.com')
        response = self.client.get('/api/listings')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_get_listings_unauthenticated(self):
        # Test for unauthenticated users trying to get listings
        response = self.client.get('/api/listings')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Login required')

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
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.json["error"])

    def test_update_listing_unauthenticated(self):
        # Tests reject unauthenticated PUT /api/listings/<id>.
        response = self.client.put('/api/listings/123', json={"title": "New"})
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.json["error"])

    def test_update_listing_invalid_id(self):
        # Tests return 404 for updating non-existent listing.
        self.login_session('host@example.com')
        response = self.client.put(
            '/api/listings/000000000000000000000000',
            json={"title": "Updated"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Listing not found", response.json["error"])

    def test_delete_listing_unauthenticated(self):
        # Tests reject unauthenticated DELETE /api/listings/<id>.
        response = self.client.delete('/api/listings/123')
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.json["error"])

    def test_delete_listing_invalid_id(self):
        # Tests return 404 for deleting non-existent listing.
        self.login_session('host@example.com')
        response = self.client.delete(
            '/api/listings/000000000000000000000000'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Listing not found", response.json["error"])

    def test_modify_booking_invalid_date(self):
        # Test that invalid date input is handled
        with self.app.session_transaction() as sess:
            sess['email'] = 'user@example.com'
        response = self.app.post(
            '/modify-booking?booking_id=1',
            data={
                'start_date': 'invalid-date',
                'end_date':   'invalid-date'
            }
        )
        self.assertNotIn('Your booking dates have been updated.',
                         response.data.decode())

    def test_support_page_unauthenticated(self):
        # Test that an unauthenticated user is redirected to the login page.
        response = self.client.get('/support')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/login')

    def test_view_previous_tickets(self):
        # Test that a user sees their previously submitted tickets.
        self.login_session('testuser@example.com')
        # Submit a support request
        self.client.post('/support', data={
            'booking_id': '12345',
            'message':    'I need assistance with my booking.'
        })
        response = self.client.get('/support')
        self.assertIn(b'12345', response.data)
        self.assertIn(b'I need assistance with my booking.', response.data)

    def test_my_bookings_page_unauthenticated(self):
        # Test that an unauthenticated user is redirected to the login page when trying to access /my-bookings.
        response = self.client.get('/my-bookings')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/login')

    def test_my_bookings_page_authenticated(self):
        # Test that an authenticated user can access their bookings page.
        self.login_session('testuser@example.com')
        response = self.client.get('/my-bookings')
        self.assertIn(b'Loading your bookings\xe2\x80\xa6', response.data)

    def test_my_bookings_page_with_no_user(self):
        # Test that a user is redirected to login page if there is no user in the session.
        with self.client.session_transaction() as sess:
            sess['email'] = None
        response = self.client.get('/my-bookings')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/login')

if __name__ == '__main__':
    unittest.main()
