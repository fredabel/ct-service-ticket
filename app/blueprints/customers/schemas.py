from app.models import Customer
from app.extensions import ma
from marshmallow import fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, required=True)
    class Meta:
        model = Customer

class CustomerUpdateSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, required=False)
    class Meta:
        model = Customer

class MyTicketsSchema(ma.SQLAlchemyAutoSchema):
    service_tickets = fields.Nested("ServiceTicketSchema", many=True, exclude=["customer"])
    class Meta:
        model = Customer
        include_fk = True 
        fields = ("service_tickets", "id")
        
               
customer_schema = CustomerSchema()
customer_update_schema = CustomerUpdateSchema()
customers_schema = CustomerSchema(many=True)
my_tickets_schema = MyTicketsSchema()
login_schema = CustomerSchema(exclude=["name","phone"])