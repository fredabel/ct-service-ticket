from app.models import ServiceTicket
from app.extensions import ma
from marshmallow import fields
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    
    mechanic_ids = fields.List(fields.Int()) 
    mechanics = fields.Nested("MechanicSchema", many=True)
    customer = fields.Nested("CustomerSchema")
    
    class Meta:
        model = ServiceTicket
        include_fk = True 
        fields = ("mechanic_ids", "service_date", "service_desc", "vin", "customer_id", "mechanics", "customer")

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True) 
return_service_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
