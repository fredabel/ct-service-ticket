from app.models import Mechanic
from app.extensions import ma
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    service_tickets = fields.Nested("ServiceTicketSchema", many=True, exclude=["mechanics","ticket_items","customer"]) 
    password = fields.String(load_only=True, required=True)
    class Meta:
        model = Mechanic
        
class MechanicUpdateSchema(ma.SQLAlchemyAutoSchema):
    service_tickets = fields.Nested("ServiceTicketSchema", many=True, exclude=["mechanics","ticket_items","customer"]) 
    password = fields.String(load_only=True, required=False)
    class Meta:
        model = Mechanic
     
mechanic_schema = MechanicSchema(exclude=["service_tickets"])
mechanic_update_schema = MechanicUpdateSchema(exclude=["service_tickets"])
mechanics_schema = MechanicSchema(many=True, exclude=["service_tickets"]) 
mechanic_schema_with_tickets =  MechanicSchema()
mechanics_schema_with_tickets =  MechanicSchema(many=True)
login_schema = MechanicSchema(exclude=["name","phone","salary"])