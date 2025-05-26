import unittest
from app import create_app
from app.models import db, Customer, Mechanic, PartDescription, SerializedPart, ServiceTicket
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash
import datetime

class TestSerializedPartDescription(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all() # Drop all tables before creating new ones
            db.create_all() # Create all tables
            
            # Add PartDescription for part tests
            part = PartDescription(
                name="Brake Pad",
                brand="BrandX",
                price=99.99
            )
            db.session.add(part)
            db.session.commit()
            
            # Create SerializedPart for part tests
            serialized_part = SerializedPart(
                desc_id=part.id,
                ticket_id=None  
            )
            
            db.session.add(serialized_part)
            db.session.commit()
            
            
            # Create customer
            customer = Customer(
                name="Fred Tuazon",
                email="ft@email.com",
                phone="1234567890",
                password=generate_password_hash("password123")
            )
            db.session.add(customer)
            db.session.commit()
            
            # Create mechanic
            mechanic = Mechanic(
                name="Mike Smith",
                email="mk@email.com",
                phone="1234567890",
                salary=50000,
                password=generate_password_hash("password123")
            )
            
            db.session.add(mechanic)
            db.session.commit()
            
            # Create a service ticket
            ticket = ServiceTicket(
                customer_id=1, 
                vin="CMD12456", 
                service_date=datetime.date.fromisoformat("2025-03-21"), 
                service_desc="Test description"
            )
            db.session.add(ticket)
            db.session.commit()
            
        self.client = self.app.test_client()
        
    def test_create_serialized_part_description(self): # Test create serialized part description with valid payload
        
        response = self.client.post('/serialized_parts/', json={"desc_id":1})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "Successfully created serialized part")
    
    def test_fields_required(self): # Test required fields are present in the payload
        
        response = self.client.post('/serialized_parts/', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['desc_id'][0], "Missing data for required field.")
        
    def test_get_all_serialized_part_descriptions(self): # Test retrieve all serialized part descriptions with pagination
        
        response = self.client.get('/serialized_parts/', query_string={'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        
    def test_get_serialized_part_descriptions_by_id(self): # Test retrieve serialized part descriptions by ID
        
        response = self.client.get('serialized_parts/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], 1)
    
    def test_get_serialized_part_descriptions_invalid_id(self): # Test retrieve serialized part descriptions by invalid ID
        
        response = self.client.get('serialized_parts/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Invalid serialized part description")
        
    def test_update_valid_serialized_part_description(self): # Test updating an existing serialized part description with valid payload
        response = self.client.put('serialized_parts/1', json={"desc_id": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully updated serialized part")
        
    def test_update_valid_serialized_part_description_with_invalid_descid(self): # Test updating an existing serialized part description with invalid desc_id
        response = self.client.put('serialized_parts/1', json={"desc_id": 999})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Part description not found")
        
    def test_update_valid_serialized_part_description_with_no_desc_id(self): # Test updating an existing serialized part description with no desc_id
        response = self.client.put('serialized_parts/1', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['desc_id'][0], "Missing data for required field.")
        
    def test_update_valid_serialized_part_description_with_unknown_field(self): # Test updating an existing serialized part description with unknown field
        response = self.client.put('serialized_parts/1', json={"unknown_field": "value"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['unknown_field'][0], "Unknown field.")
        
    def test_update_serialized_part_description_ticket_id(self): # Test updating an existing serialized part description with ticket_id
        response = self.client.put('serialized_parts/1', json={"desc_id": 1, "ticket_id": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully updated serialized part")
        
    def test_update_serialized_part_description_invalid_ticket_id(self): # Test updating an existing serialized part description with invalid ticket_id
        response = self.client.put('serialized_parts/1', json={"desc_id": 1, "ticket_id": 999})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket not found")
        
    def test_delete_serialized_part_description_by_id(self): # Test delete an existing serialized part description by IDs
        response = self.client.delete('serialized_parts/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully deleted serialized part 1")
    
    def test_delete_invalid_serialized_part_description_by_id(self): # Test delete an invalid serialized part description id
        response = self.client.delete('serialized_parts/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Serialized part not found")
        
    def test_get_all_inventory_serialized_parts(self):
        response = self.client.get('/serialized_parts/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    
    def test_get_inventory_by_parts_id(self):
        response = self.client.get('/serialized_parts/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_description']['id'], 1)
        
    def test_get_inventory_by_invalid_parts_id(self):
        response = self.client.get('/serialized_parts/inventory/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Part description not found")
       

    
    
    