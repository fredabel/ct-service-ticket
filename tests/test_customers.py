import unittest
from app import create_app
from app.models import db, Customer
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.util import encode_token


class TestCustomer(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.payLoad = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "123456789",
            "password": "password123"
        }
        with self.app.app_context():
            db.drop_all() # Drop all tables before creating new ones
            db.create_all() # Create all tables
            db.session.add(Customer(
                name=self.payLoad["name"],
                email=self.payLoad["email"],
                phone=self.payLoad["phone"],
                password=generate_password_hash(self.payLoad["password"])
            ))
            db.session.commit()
        self.token = encode_token(1, role="user")
        self.client = self.app.test_client()
        
    
    def test_create_customer(self): # Creating a new customer with new email
        
        payLoad = {
            "name": "Jane Doe",
            "email": "jane@email.com",
            "phone": "987654321",
            "password": "password456"
        }
        
        response = self.client.post('/customers/', json=payLoad)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "Successfully created customer")
    
    def test_email_already_exists(self): # Creating a customer with an email that already exists
       
        response2 = self.client.post('/customers/', json=self.payLoad)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json['message'], "A customer with this email already exists!")
    
    def test_all_fields_required(self): # Test all required fields
        
        for field in list(self.payLoad.keys()):
            payload = self.payLoad.copy()
            payload.pop(field)
            response = self.client.post('/customers/', json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json[field][0], "Missing data for required field.")
    
    def test_login_customer(self): # Customer login with valid credentials
        
        login_payload = {
            "email": self.payLoad["email"],
            "password": self.payLoad["password"]
        }
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
        
    def test_login_invalid_credentials(self): # Customer login with invalid credentials
        
        login_payload = {
            "email": "wrong@email.com",
            "password": "wrongpassword123"
        }
        
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"],"Invalid email or password!", )
    
    def test_update_customer(self): # Updating an existing customer
        
        headers = {'Authorization': f'Bearer {self.token}'}
        payLoad = self.payLoad.copy()
        payLoad["name"] = "Updated Name"
        response = self.client.put('customers/', json=payLoad, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customer']['name'], payLoad["name"])
        
    def test_delete_customer(self): # Deleting an existing customer
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.delete('customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "success")
        
    def test_get_all_customers(self): # Get all customers with pagination
        
        response = self.client.get('/customers/', query_string={'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['customers'], list)
    
    def test_get_customer_by_id(self): # Get a valid customer by ID
        
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], self.payLoad["name"])
    
    def test_get_customer_by_invalid_id(self): # Get a customer does not exist
        
        response = self.client.get('/customers/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Invalid customer")
        
    def test_get_customer_tickets(self): # Get customer's tickets
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("customer", response.json)
    
    def test_search_customer_by_name(self): # Searching a customer by name 
        
        response = self.client.get('/customers/search', query_string={"name": self.payLoad['name']})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    
    def test_search_customer_by_email(self): # Searching a customer by email 
        
        response = self.client.get('/customers/search', query_string={"email": self.payLoad['email']})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        
    def test_search_customer_no_params(self): # Searching a customer with no parameters
    
        response = self.client.get('/customers/search')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "At least one search parameter (name or email) is required.")
    
  
    
   
    
    