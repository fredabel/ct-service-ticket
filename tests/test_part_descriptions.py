import unittest
from app import create_app
from app.models import db, PartDescription
from marshmallow import ValidationError


class TestPartDescription(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.payLoad = {
            "name": "Brakes",
            "brand": "Brand A",
            "price": 100.00,
        }
        with self.app.app_context():
            db.drop_all() # Drop all tables before creating new ones
            db.create_all() # Create all tables
            db.session.add(PartDescription(**self.payLoad))
            db.session.commit()
        self.client = self.app.test_client()
        
    def test_create_part_description(self): # Create part description with valid payload
        
        response = self.client.post('/part_descriptions/', json=self.payLoad)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "Successfully created part description")
    
    def test_fields_required(self): # Required fields are present in the payload
        
        for field in list(self.payLoad.keys()):
            payload = self.payLoad.copy()
            payload.pop(field)
            response = self.client.post('/part_descriptions/', json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json[field][0], "Missing data for required field.")
    
    def test_get_all_part_descriptions(self): # Retrieve all part descriptions with pagination
        
        response = self.client.get('/part_descriptions/', query_string={'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['items'], list)
    
    def test_get_part_descriptions_by_id(self): # Retrieve part descriptions by ID
        
        response = self.client.get('part_descriptions/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], self.payLoad['name'])
    
    def test_get_part_descriptions_invalid_id(self): # Retrieve part descriptions by invalid ID
        
        response = self.client.get('part_descriptions/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Invalid part description")

    def test_update_part_descriptions(self): # Updating an existing part description
        
        payLoad = self.payLoad.copy()
        payLoad["name"] = "Updated Name"
        response = self.client.put('part_descriptions/1', json=payLoad)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully updated part description")
        self.assertEqual(response.json['part_description']['name'], payLoad["name"])
        
    def test_update_invalid_part_descriptions(self): # Updating part description does not exist
        
        payLoad = self.payLoad.copy()
        payLoad["name"] = "Updated Name"
        response = self.client.put('part_descriptions/999', json=payLoad)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Part description not found")
        
    def test_delete__part_descriptions(self): # Deleting existing part description 
        
        response = self.client.delete('part_descriptions/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully deleted part description")
    
    def test_delete_invalid_part_descriptions(self): # Deleting part description does not exist
        
        response = self.client.delete('part_descriptions/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Part description not found")
    
    def test_search_part_description_by_name(self): # Searching a part description by name 
        
        response = self.client.get('/part_descriptions/search', query_string={"name": self.payLoad['name']})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        
    def test_search_part_description_by_brand(self): # Searching a part description by brand 
        
        response = self.client.get('/part_descriptions/search', query_string={"brand": self.payLoad['brand']})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_search_part_description_no_params(self): # Searching a part description with no parameters
    
        response = self.client.get('/part_descriptions/search')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Please provide a name or brand to search")
   
    
    