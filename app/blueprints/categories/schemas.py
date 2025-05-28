from app.models import Category
from app.extensions import ma
from marshmallow import fields

class CategorySchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Category
     
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)