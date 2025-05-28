from app.models import Priority
from app.extensions import ma
from marshmallow import fields

class PrioritySchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Priority
     
priority_schema = PrioritySchema()
priorities_schema = PrioritySchema(many=True)