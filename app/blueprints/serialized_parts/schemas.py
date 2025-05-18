from app.models import SerializedPart
from app.extensions import ma
from marshmallow import fields

class SerializedPartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SerializedPart
        include_fk = True
serialized_part_schema = SerializedPartSchema()
serialized_parts_schema = SerializedPartSchema(many=True)