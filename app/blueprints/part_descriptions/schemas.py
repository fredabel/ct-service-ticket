from app.models import PartDescription
from app.extensions import ma
from marshmallow import fields

class PartDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescription
     
part_description_schema = PartDescriptionSchema()
part_descriptions_schema = PartDescriptionSchema(many=True)