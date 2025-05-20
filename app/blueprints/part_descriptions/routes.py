from flask import request, jsonify
from app.blueprints.part_descriptions import part_descriptions_bp
from app.blueprints.part_descriptions.schemas import part_description_schema, part_descriptions_schema
from marshmallow import ValidationError
from app.models import PartDescription, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
from app.utils.util import token_required

# -------------------- Create a Part Description --------------------
# This route allows the creation of a new part description.
# Rate limited to 20 requests per hour to prevent spamming.
@part_descriptions_bp.route("/",methods=['POST'])
@limiter.limit("20/hour")
def create_part_description():
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_part_description = PartDescription(**part_description_data)
    db.session.add(new_part_description)
    db.session.commit()
    return jsonify({"status": "success","message":"Successfully created part description","part_description": part_description_schema.dump(new_part_description)}), 201

# -------------------- Get All Part Descriptions --------------------
# This route retrieves all part descriptions.
# Cached for 30 seconds to improve performance.
# Rate limited to 10 requests per minute to prevent excessive requests.
@part_descriptions_bp.route("/",methods=['GET'])
# @cache.cached(timeout=30)
@limiter.limit("10/hour")
def get_part_descriptions():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(PartDescription)
        part_descriptions = db.paginate(query, page=page, per_page=per_page)
        return part_descriptions_schema.jsonify(part_descriptions), 200
    except:
        query = select(PartDescription)
        part_descriptions = db.session.execute(query).scalars().all()
    return part_descriptions_schema.jsonify(part_descriptions), 200

# -------------------- Update a Part Description --------------------
# This route allows updating a part description by its ID.
# Rate limited to 10 requests per hour.
@part_descriptions_bp.route("/<int:part_description_id>", methods=['PUT'])
@limiter.limit("10/hour")
def update_part_description(part_description_id):
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    part_description = db.session.get(PartDescription, part_description_id)
    if not part_description:
        return jsonify({"status": "error","message":"Part description not found"}), 404
    
    for field, value in part_description_data.items():
        setattr(part_description, field, value)
    
    db.session.commit()
    return jsonify({"status": "success","message":"Successfully updated part description","part_description": part_description_schema.dump(part_description)}), 200

# -------------------- Delete a Part Description --------------------
# This route allows deleting a part description by its ID.
# Rate limited to 5 requests per day to prevent abuse. 
@part_descriptions_bp.route("/<int:part_description_id>", methods=['DELETE'])
@limiter.limit("5/day")
def delete_part_description(part_description_id):
    
    part_description = db.session.get(PartDescription, part_description_id)
    
    if not part_description:
        return jsonify({"status": "error","message":"Part description not found"}), 404
    
    # Check for related serialized parts
    if part_description.serial_items:
        return jsonify({"status": "error", "message": "Cannot delete: related serialized parts exist."}), 400
    
    db.session.delete(part_description)
    db.session.commit()
    return jsonify({"status": "success","message": "Successfully deleted part description"}), 200

# -------------------- Search Part Descriptions --------------------
# This route allows searching for part descriptions by name.
# Rate limited to 15 requests per minute.
@part_descriptions_bp.route("/search", methods=['GET'])
@limiter.limit("15/minute")
def search_part_descriptions():
    name = request.args.get('name')
    query = select(PartDescription).where(PartDescription.name.like(f'%{name}%'))
    part_descriptions = db.session.execute(query).scalars().all()
    return part_descriptions_schema.jsonify(part_descriptions), 200