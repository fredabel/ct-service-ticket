import unittest
from app import create_app
from app.models import db, Mechanic
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash
from app.utils.util import encode_token


class TestMechanic(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.fields = ["name", "email", "phone", "password", "salary"]
        self.payLoad = {
            "name": "Mike Smith",
            "email": "ms@email.com",
            "phone": "123456789",
            "salary": 50000,
            "password": "password123"
        }
        with self.app.app_context():
            db.drop_all() # Drop all tables before creating new ones
            db.create_all() # Create all tables
            db.session.add(Mechanic(
                name=self.payLoad["name"],
                email=self.payLoad["email"],
                phone=self.payLoad["phone"],
                salary=self.payLoad["salary"],
                password=generate_password_hash(self.payLoad["password"])
            ))
            db.session.commit()
        self.token = encode_token(1, role="mechanic")
        self.client = self.app.test_client()
        
    def test_create_mechanic(self): # Creating a new mechanic with new email as we already have one in the database
        
        self.payLoad["name"] = "Roger Johnson"
        self.payLoad["email"] = "rj@email.com"
        
        response = self.client.post('/mechanics/', json=self.payLoad )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "Successfully created mechanic")
    
    def test_email_already_exists(self): # Creating a mechanic with an email that already exists in the database
       
        response2 = self.client.post('/mechanics/', json=self.payLoad)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json['message'], "A mechanic with this email already exists!")
    
    def test_fields_required(self): # Required fields are present in the payload
        
        for field in list(self.payLoad.keys()):
            payload = self.payLoad.copy()
            payload.pop(field)
            response = self.client.post('/mechanics/', json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json[field][0], "Missing data for required field.")
    
    def test_login_mechanic(self): # Mechanic login with valid credentials
        
        login_payload = {
            "email": self.payLoad["email"],
            "password": self.payLoad["password"]
        }
        response = self.client.post('/mechanics/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
    
    def test_login_invalid_credentials(self): # Mechanic login with invalid credentials
        
        login_payload = {
            "email": "wrong@email.com",
            "password": "wrongpassword123"
        }
        
        response = self.client.post('/mechanics/login', json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"],"Invalid email or password!", )
        
    def test_update_mechanic(self): # Updating an existing mechanic
        
        headers = {'Authorization': f'Bearer {self.token}'}
        payLoad = self.payLoad.copy()
        payLoad["name"] = "Updated Name"
        response = self.client.put('mechanics/', json=payLoad, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully updated mechanic")
        self.assertEqual(response.json['mechanic']['name'], "Updated Name")
        
    def test_delete_mechanic(self): # Deleting an existing mechanic
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.delete('mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Succesfully deleted mechanic 1")
        
    def test_get_all_mechanics(self): # Get all mechanics
        
        response = self.client.get('/mechanics/', query_string={'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['mechanics'], list)
    
    def test_get_mechanic_by_id(self): # Get a specific mechanic by ID
        response = self.client.get('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], self.payLoad["name"])
    
    def test_get_mechanic_by_invalid_id(self): # Get a mechanic does not exist
        
        response = self.client.get('/mechanics/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Invalid mechanic")
        
    def test_popular_mechanic(self): # Get popular mechanics
        
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    
    def test_search_mechanic_by_name(self): # Searching a mechanic by name 
        
        response = self.client.get('/mechanics/search', query_string={"name": self.payLoad['name']})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    
    def test_search_mechanic_by_email(self): # Searching a mechanic by email 
        
        response = self.client.get('/mechanics/search', query_string={"email": self.payLoad['email']})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        
    def test_search_mechanic_no_params(self): # Searching a mechanic with no parameters
    
        response = self.client.get('/mechanics/search')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "At least one search parameter (name or email) is required.")

    
   
    
    