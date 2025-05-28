from app.models import TicketStatus
from app.extensions import ma
from marshmallow import fields

class TicketStatusSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = TicketStatus
     
ticket_status_schema = TicketStatusSchema()
ticket_statuses_schema = TicketStatusSchema(many=True)