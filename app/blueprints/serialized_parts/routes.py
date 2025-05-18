from flask import request, jsonify
from app.blueprints.serialized_parts import serialized_parts_bp
from app.blueprints.serialized_parts.schemas import serialized_part_schema, serialized_parts_schema
from app.blueprints.part_descriptions.schemas import part_description_schema
from marshmallow import ValidationError
from app.models import SerializedPart, PartDescription, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
from app.utils.util import token_required

# -------------------- Create a Serialized Part --------------------
# This route allows the creation of a new serialized part.
# Rate limited to 20 requests per minute to prevent spamming.
@serialized_parts_bp.route("/",methods=['POST'])
@limiter.limit("20 per minute")
def create_serialized_part():
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_serialized_part = SerializedPart(**serialized_part_data)
    db.session.add(new_serialized_part)
    db.session.commit()
    return jsonify({
        "status": "success",
        "message":"Successfully created serialzied part",
        "part": serialized_part_schema.dump(new_serialized_part)
    }), 201

# -------------------- Get All Serialized Parts --------------------
# This route retrieves all serialized parts.
# Cached for 60 seconds to improve performance.
@serialized_parts_bp.route("/",methods=['GET'])
@cache.cached(timeout=60)
def get_serialized_parts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(SerializedPart)
        serialized_parts = db.paginate(query, page=page, per_page=per_page)
        return serialized_parts_schema.jsonify(serialized_parts), 200
    except:
        query = select(SerializedPart)
        serialized_parts = db.session.execute(query).scalars().all()
    return serialized_parts_schema.jsonify(serialized_parts), 200

# -------------------- Search Serialized Parts --------------------
# This route allows searching for serialized parts by name.
# Rate limited to 15 requests per minute.
@serialized_parts_bp.route("/search", methods=['GET'])
@limiter.limit("15 per minute")
def search_serialized_parts():
    name = request.args.get('name')
    query = select(SerializedPart).where(SerializedPart.name.like(f'%{name}%'))
    serialized_parts = db.session.execute(query).scalars().all()
    return serialized_parts_schema.jsonify(serialized_parts), 200

# -------------------- Update a Serialized Part --------------------
# This route allows updating a serialized part by its ID.
# Rate limited to 10 requests per minute.
@serialized_parts_bp.route("/<int:serialized_part_id>", methods=['PUT'])
@limiter.limit("10 per minute")
def update_serialized_part(serialized_part_id):
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    serialized_part = db.session.get(SerializedPart, serialized_part_id)
    if not serialized_part:
        return jsonify({"status": "error","message":"Part description not found"}), 404
    
    for field, value in serialized_part_data.items():
        setattr(serialized_part, field, value)
    
    db.session.commit()
    return jsonify({"status": "success","message":"Successfully updated part description","serialized_part": serialized_part_schema.dump(serialized_part)}), 200

# -------------------- Delete a Serialized Part --------------------
# This route allows deleting a serialized part by its ID.
# Rate limited to 10 requests per minute.
@serialized_parts_bp.route("/<int:serialized_part_id>", methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)
    if not serialized_part:
        return jsonify({"status": "error","message":"Part description not found"}), 404
    
    db.session.delete(serialized_part)
    db.session.commit()
    return jsonify({"status": "success","message": "Successfully deleted part description"}), 200

# -------------------- Get All Stock --------------------
# This route retrieves all stock of serialized parts.
# Cached for 60 seconds to improve performance.
# Rate limited to 10 requests per minute.
@serialized_parts_bp.route("/inventory", methods=['GET'])
@cache.cached(timeout=60)
@limiter.limit("10 per minute")
def get_all_stock():
    query = select(PartDescription)
    parts_description = db.session.execute(query).scalars().all()
    stock = []
    for part_description in parts_description:
        part_items = part_description.serial_items
        count = 0
        for part in part_items:
            if not part.ticket_id:
                count += 1
        data = part_description_schema.dump(part_description)
        data["stock"] = count
        stock.append(data)          
    return jsonify(stock), 200
  
# -------------------- Get Individual Stock --------------------
# This route allows getting the stock of a specific part by its ID.
# Cached for 30 seconds to reduce database lookups.
# Rate limited to 15 requests per minute.  
@serialized_parts_bp.route("/inventory/<int:part_id>", methods=['GET'])
@cache.cached(timeout=30)
@limiter.limit("15 per minute")
def get_individual_stock(part_id):
    part_description = db.session.get(PartDescription, part_id)
    parts = part_description.serial_items
    count = 0
    for part in parts:
        if not part.ticket_id:
            count += 1
    return jsonify({"item": part_description.name, "stock": count }), 200
    
    
    