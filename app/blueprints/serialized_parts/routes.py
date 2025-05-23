from flask import request, jsonify
from app.blueprints.serialized_parts import serialized_parts_bp
from app.blueprints.serialized_parts.schemas import serialized_part_schema, serialized_parts_schema, serialized_part_schema_no_ticket, serialized_parts_schema_no_ticket
from app.blueprints.part_descriptions.schemas import part_description_schema
from marshmallow import ValidationError
from app.models import SerializedPart, PartDescription, ServiceTicket, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
from app.utils.util import token_required

# -------------------- Create a Serialized Part --------------------
# This route allows the creation of a new serialized part.
# Rate limited to 10 requests per hour to prevent spamming.
@serialized_parts_bp.route("/",methods=['POST'])
@limiter.limit("10/minute")
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
# @cache.cached(timeout=60)
def get_serialized_parts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(SerializedPart)
        serialized_parts = db.paginate(query, page=page, per_page=per_page)
        return serialized_parts_schema_no_ticket.jsonify(serialized_parts), 200
    except:
        query = select(SerializedPart)
        serialized_parts = db.session.execute(query).scalars().all()
    return serialized_parts_schema_no_ticket.jsonify(serialized_parts), 200

# -------------------- Get a Specific Serialized Part --------------------
# This route retrieves a specific serialized part by their ID.
# Cached for 30 seconds to reduce database lookups.
@serialized_parts_bp.route("/<int:part_id>",methods=['GET'])
@limiter.exempt
# @cache.cached(timeout=30)
def get_mechanic(part_id):
    query = select(SerializedPart).where(SerializedPart.id == part_id)
    serialized_part = db.session.execute(query).scalars().first()
    if serialized_part == None:
        return jsonify({"message":"Invalid serialized part description"}), 404
    return serialized_part_schema_no_ticket.jsonify(serialized_part), 200

# -------------------- Search Serialized Parts --------------------
# This route allows searching for serialized parts by name.
# Rate limited to 15 requests per minute.
@serialized_parts_bp.route("/search", methods=['GET'])
@limiter.limit("15/minute")
def search_serialized_parts():
    name = request.args.get('name')
    query = select(SerializedPart).where(SerializedPart.name.like(f'%{name}%'))
    serialized_parts = db.session.execute(query).scalars().all()
    return serialized_parts_schema.jsonify(serialized_parts), 200

# -------------------- Update a Serialized Part --------------------
# This route allows updating a serialized part by its ID.
# Rate limited to 10 requests per hour.
@serialized_parts_bp.route("/<int:serialized_part_id>", methods=['PUT'])
@limiter.limit("10/hour")
def update_serialized_part(serialized_part_id):
    
    try:
        serialized_part_data = serialized_part_schema.load(request.json)

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    part_description = db.session.get(PartDescription, serialized_part_data['desc_id'])
    if not part_description:
        return jsonify({"status": "error","message":"Part description not found"}), 404
    
    ticket = db.session.get(ServiceTicket, serialized_part_data['ticket_id'])
    if not ticket:
        return jsonify({"status": "error","message":"Service ticket not found"}), 404
    
    serialized_part = db.session.get(SerializedPart, serialized_part_id)
    if not serialized_part:
        return jsonify({"status": "error","message":"Serialized part not found"}), 404
    
    # if serialized_part.ticket_id == serialized_part_data['ticket_id']:
    #     return jsonify({"status": "error","message":"Ticket is already assigned to this serialized part"}), 400
    # if serialized_part.desc_id == serialized_part_data['desc_id']:
    #     return jsonify({"status": "error","message":"Part description is already assigned to this serialized part"}), 400

    for field, value in serialized_part_data.items():
        setattr(serialized_part, field, value)
    
    db.session.commit()
    return jsonify({"status": "success","message":"Successfully updated serialized part ","serialized_part": serialized_part_schema.dump(serialized_part)}), 200

# -------------------- Delete a Serialized Part --------------------
# This route allows deleting a serialized part by its ID.
# Rate limited to 5 requests per day.
@serialized_parts_bp.route("/<int:serialized_part_id>", methods=['DELETE'])
@limiter.limit("5/day")
def delete_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)
    if not serialized_part:
        return jsonify({"status": "error","message":"Serialized part not found"}), 404
    
    db.session.delete(serialized_part)
    db.session.commit()
    return jsonify({"status": "success","message": "Successfully deleted serialized part"}), 200

# -------------------- Get All Stock --------------------
# This route retrieves all stock of serialized parts.
# Cached for 60 seconds to improve performance.
# Rate limited to 10 requests per minute.
@serialized_parts_bp.route("/inventory", methods=['GET'])
# @cache.cached(timeout=60)
# @limiter.limit("10 per minute")
def get_all_stock():
    query = select(PartDescription)
    parts_description = db.session.execute(query).scalars().all()
    # Check if there are any part descriptions
    if not parts_description:
        return jsonify({"status": "error","message":"No part descriptions found"}), 404
    
    stock = []
    for part_description in parts_description:
        part_items = part_description.serial_items
        count = 0
        for part in part_items:
            if not part.ticket_id:
                count += 1
        stock.append({
            "part_description": part_description_schema.dump(part_description),
            "stock": count
        })
    return jsonify(stock), 200
  
# -------------------- Get Individual Stock --------------------
# This route allows getting the stock of a specific part by its ID.
# Cached for 30 seconds to reduce database lookups.
# Rate limited to 10 requests per minute.  
@serialized_parts_bp.route("/inventory/<int:part_id>", methods=['GET'])
# @cache.cached(timeout=30)
@limiter.limit("10/minute")
def get_individual_stock(part_id):
    
    part_description = db.session.get(PartDescription, part_id)
    if not part_description:
        return jsonify({"status": "error","message":"Part description not found"}), 404
    
    parts = part_description.serial_items
    count = 0
    for part in parts:
        if not part.ticket_id:
            count += 1
    return jsonify({"part_description": part_description_schema.dump(part_description), "stock": count }), 200
    
    
