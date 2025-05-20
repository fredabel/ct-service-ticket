from app.models import ServiceTicket
from app.extensions import ma
from marshmallow import fields
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    
    mechanic_ids = fields.List(fields.Int()) 
    mechanics = fields.Nested("MechanicSchema", many=True, exclude=["service_tickets"])
    customer = fields.Nested("CustomerSchema")
    ticket_items = fields.Nested("SerializedPartSchema", many=True, exclude=["ticket"])

    class Meta:
        model = ServiceTicket
        include_fk = True 
        fields = ("id", "service_date", "service_desc", "vin", "customer_id", "customer", "mechanic_ids", "mechanics", "ticket_items")

class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")
        
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True) 
return_service_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
edit_service_ticket_schema = EditServiceTicketSchema()