import unittest
from app import create_app
from app.models import db, Customer, Mechanic, PartDescription, SerializedPart, ServiceTicket
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash
import datetime

class TestServiceTicket(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.payLoad = {
            "customer_id": 1,
            "vin": "CMD12456",
            "service_date": "2025-03-20",
            "service_desc": "Test ticket"
        }
        with self.app.app_context():
            db.drop_all() # Drop all tables before creating new ones
            db.create_all() # Create all tables
            
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
            
            mechanic2 = Mechanic(
                name="Jane Doe",
                email="jane@email.com",
                phone="0987654321",
                salary=60000,
                password=generate_password_hash("password123")
            )
            
            db.session.add(mechanic)
            db.session.add(mechanic2)
            db.session.commit()
            
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
            serialized_part2 = SerializedPart(
                desc_id=part.id,
                ticket_id=None  
            )
            db.session.add(serialized_part)
            db.session.add(serialized_part2)
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
    
    def test_create_service_ticket_with_out_mechanics(self): # Test create a service ticket with valid payload
        
        response = self.client.post('/service-tickets/', json=self.payLoad)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['id'], 2)
    
    def test_create_service_ticket_with_unknown_field(self): # Test create a service ticket with unkown field in payload
        payLoad = self.payLoad.copy()
        payLoad["unknown_field"] = "value"
        response = self.client.post('/service-tickets/', json=payLoad)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['unknown_field'][0], "Unknown field.")
    
    def test_create_service_ticket_with_mechanics(self): # Test create a service ticket with mechanic payload
        payLoad = self.payLoad.copy()
        payLoad["mechanic_ids"] = [1]
        response = self.client.post('/service-tickets/', json=payLoad)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['id'], 2)
        
    def test_fields_required(self): # Test required fields are present in the payload
        
        for field in list(self.payLoad.keys()):
            payload = self.payLoad.copy()
            payload.pop(field)
            response = self.client.post('/service-tickets/', json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json[field][0], "Missing data for required field.")
     
    def test_get_all_service_tickets(self): # Test retrieve all service tickets with pagination
        response = self.client.get('/service-tickets/', query_string={'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['tickets'], list)
    
    def test_get_service_ticket_by_id(self): # Test retrieve service ticket by ID
        response = self.client.get('/service-tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], 1)
        
    def test_get_invalid_service_ticket_by_id(self): # Test retrieve service ticket does not exist
        response = self.client.get('/service-tickets/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Invalid ticket id")
        
    def test_delete_service_ticket(self): # Test delete service ticket by ID
        response = self.client.delete('/service-tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully deleted service ticket 1")
    
    def test_delete_invalid_service_ticket(self): # Test deleting service ticket does not exist
        response = self.client.delete('/service-tickets/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket not found")
        
    def test_service_ticket_edit_mechanics(self): # Test editing mechanics of a service ticket by adding/removing mechanics
        parameters = ["add_mechanic_ids", "remove_mechanic_ids"]
        for param in parameters:
            payLoad = { param: [1] }
            response = self.client.put('/service-tickets/1/edit-mechanics', json=payLoad)
            self.assertEqual(response.status_code, 200)
    
    def test_service_ticket_edit_mechanics_invalid(self): # Test editing mechanics of a service ticket with invalid mechanic IDs
        parameters = ["add_mechanic_ids", "remove_mechanic_ids"]
        for param in parameters:
            payLoad = { param: [99999, 10000] }
            response = self.client.put('/service-tickets/1/edit-mechanics', json=payLoad)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json['status'], "error")
    
    def test_edit_invalid_service_ticket(self): # Test editing mechanics of a service ticket with invalid mechanic IDs
      
        payLoad = {}
        response = self.client.put('/service-tickets/99/edit-mechanics', json=payLoad)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket not found")
        
    def test_edit_service_ticket_with_unknown_field(self): # Test editing a service ticket with unkown field
      
        payLoad = {"unknown_field": "value"}
        response = self.client.put('/service-tickets/1/edit-mechanics', json=payLoad)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['unknown_field'][0], "Unknown field.")
    
    def test_edit_service_ticket_by_adding_mechanic_id(self): # Test editing a service ticket by adding a mechanic ID
        
        response = self.client.put('/service-tickets/1/add-mechanic/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Mechanic Jane Doe successfully added to ticket")
        self.assertEqual(response.json['service_ticket']['id'], 1)
        
    def test_edit_service_ticket_by_adding_invalid_mechanic_id(self): # Test editing a service ticket by adding a invalid mechanic ID
        response = self.client.put('/service-tickets/1/add-mechanic/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket or mechanic not found.")

    def test_edit_service_ticket_by_adding_already_exist_mechanic_id(self): # Test editing a service ticket by adding a mechanic ID that already exists
        
        # First add the mechanic to the ticket
        response = self.client.put('/service-tickets/1/add-mechanic/2')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.put('/service-tickets/1/add-mechanic/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Mechanic already assigned to this ticket.")

    def test_edit_service_ticket_by_removing_mechanic_id(self): # Test editing a service ticket by removing a mechanic ID
        
        # First add the mechanic to the ticket
        response = self.client.put('/service-tickets/1/add-mechanic/2')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.put('/service-tickets/1/remove-mechanic/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Mechanic Jane Doe successfully removed from ticket")
        self.assertEqual(response.json['service_ticket']['id'], 1)
        
    def test_edit_service_ticket_by_removing_invalid_id(self): # Test editing a service ticket by removing a invalid mechanic ID
        
        response = self.client.put('/service-tickets/999/remove-mechanic/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket or mechanic not found.")

    def test_edit_service_ticket_by_removing_not_included_mechanic_id(self): # Test editing a service ticket by adding a mechanic ID that already exists
        
        # First add the mechanic 2 to the ticket
        response = self.client.put('/service-tickets/1/add-mechanic/2')
        self.assertEqual(response.status_code, 200)
        
        # Now try to remove mechanic 1 which is not included in the ticket
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Mechanic not included on this ticket.")

    def test_edit_service_ticket_by_adding_serialized_part_id(self):
        
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Part Brake Pad successfully added to ticket")
    
    def test_edit_service_ticket_by_adding_serialized_part_id_invalid(self):
        
        response = self.client.put('/service-tickets/999/add-part/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket or serialized part not found.")
        
    def test_edit_service_ticket_by_adding_already_exist_serialized_part_id(self):
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Part already assigned to a ticket.")
        
    def test_edit_service_ticket_by_removing_serialized_part_id(self):
        
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.put('/service-tickets/1/remove-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Part Brake Pad successfully removed from ticket")
    
    def test_edit_service_ticket_by_removing_not_included_serialized_part_id(self):
        
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.put('/service-tickets/1/remove-part/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Serialized part not included to this ticket.")
    
    def test_edit_service_ticket_by_removing_invalid_serialized_part_id(self):

        response = self.client.put('/service-tickets/999/remove-part/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket or serialized part not found.")
    
    def test_edit_service_ticket_add_to_cart(self):
        
        response = self.client.put('/service-tickets/1/add-to-cart/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "1 part(s) successfully added to cart")
        self.assertEqual(response.json['service_ticket']['id'], 1)
    
    def test_edit_service_ticket_add_to_cart_with_quantity(self):
        
        response = self.client.put('/service-tickets/1/add-to-cart/1', json={'quantity': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "1 part(s) successfully added to cart")    
    
    def test_edit_service_ticket_add_to_cart_with_exceeded_quantity(self):
        
        response = self.client.put('/service-tickets/1/add-to-cart/1', json={'quantity': 4})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Only 2 stock(s) available for this part.")    
    
    def test_edit_service_ticket_add_to_cart_invalid_ticket_id(self):
        
        response = self.client.put('/service-tickets/9999/add-to-cart/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Invalid ticket_id or part_id.")
        
    
