from flask import request, jsonify
from app.blueprints.categories import categories_bp
from app.blueprints.categories.schemas import category_schema, categories_schema
from marshmallow import ValidationError
from app.models import Category, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter

# -------------------- Create a Category --------------------
# This route allows the creation of a new category.
# Rate limited to 10 requests per hour to prevent spamming.
@categories_bp.route("/",methods=['POST'])
@limiter.limit("10/hour")
def create_category():
    try:
        category_data = category_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_category = Category(**category_data)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({
        "status": "success", 
        "message":"Successfully created a new category", 
        "category": category_schema.dump(new_category)}), 201
