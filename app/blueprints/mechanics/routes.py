from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, mechanic_schema_with_tickets, mechanics_schema_with_tickets, login_schema
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
from app.utils.util import encode_token, mechanic_required
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------- Login Route --------------------
# This route allows mechanic to log in using their email and password.
# If the credentials are valid, a token is generated and returned.
@mechanics_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as err:
        return jsonify(err.messages), 400
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and check_password_hash(mechanic.password, password):
        token = encode_token(mechanic.id, role="mechanic")
        return jsonify({"status": "success", "message": "Successfully logged in.", "token": token}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid email or password!"}), 401

# -------------------- Create a New Mechanic --------------------
# This route allows the creation of a new mechanic.
# Rate limited to 20 requests per hour to prevent spamming.
@mechanics_bp.route("/",methods=['POST'])
@limiter.limit("20/hour")
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
        email_exist = db.session.execute(select(Mechanic).where(Mechanic.email == mechanic_data['email'])).scalars().first()
        if email_exist:
            return jsonify({"status":"error","message": "A mechanic with this email already exists!"}), 400
        mechanic_data['password'] = generate_password_hash(mechanic_data['password'])
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return jsonify({"status": "succes", "message": "Successfully created mechanic", "mechanic": mechanic_schema.dump(new_mechanic)}), 201

# -------------------- Get All Mechanics --------------------
# This route retrieves all mechanics.
# Cached for 60 seconds to improve performance.
# Pagination is implemented to limit the number of mechanics returned in a single request.
@mechanics_bp.route("/",methods=['GET'])
# @cache.cached(timeout=60) 
@limiter.exempt
def get_mechanics():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = select(Mechanic)
    pagination = db.paginate(query, page=page, per_page=per_page)
    return jsonify({
        "mechanics": mechanics_schema_with_tickets.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200

# -------------------- Get a Specific Mechanic --------------------
# This route retrieves a specific mechanic by their ID.
# Cached for 30 seconds to reduce database lookups.
@mechanics_bp.route("/<int:id>",methods=['GET'])
@limiter.exempt
# @cache.cached(timeout=30)
def get_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()
    if mechanic == None:
        return jsonify({"status": "error","message":"Invalid mechanic"}), 404
    return mechanic_schema_with_tickets.jsonify(mechanic), 200

# -------------------- Update a Mechanic --------------------
# This route allows updating a mechanic's details by their ID.
# Rate limited to 20 requests per hour to prevent abuse.
# Validates the input and ensures the email is unique.
@mechanics_bp.route("/", methods=['PUT'])
@limiter.limit("10/hour")
@mechanic_required
def update_mechanic():
    
    query = select(Mechanic).where(Mechanic.id == request.userid)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic == None:
        return jsonify({"message":"Invalid mechanic"}), 404
    try:
        mechanic_data = mechanic_schema.load(request.json) 
        mechanic_data['password'] = generate_password_hash(mechanic_data['password'])  
    except ValidationError as err:
        return jsonify(err.messages), 400
    if mechanic_data['email'] != mechanic.email:
        email_exist = db.session.execute(select(Mechanic).where(Mechanic.email == mechanic_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"message": "A mechanic with this email already exists"}), 400
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)
    db.session.commit()
    
    return jsonify({"message":"Successfully updated mechanic","mechanic": mechanic_schema.dump(mechanic)}), 200

# -------------------- Delete a Mechanic --------------------
# This route allows deleting a mechanic by their ID.
# Rate limited to 5 requests per day to prevent abuse.
@mechanics_bp.route("/", methods=['DELETE'])
@limiter.limit("5/day")
@mechanic_required
def delete_mechanic():
    
    query = select(Mechanic).where(Mechanic.id == request.userid)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic == None:
        return jsonify({"message":"Invalid mechanic"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Succesfully deleted mechanic {request.userid}"}), 200

# -------------------- Get Popular Mechanics --------------------
# This route retrieves the mechanics based on the number of service tickets they have handled.
# Cached for 60 seconds to improve performance.
@mechanics_bp.route("/popular", methods=['GET'])
@cache.cached(timeout=60)
def popular_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    
    # Build response with tickets_count
    response = []
    for mechanic in mechanics:
        data = mechanic_schema_with_tickets.dump(mechanic)
        data["ticket_counts"] = len(mechanic.service_tickets) if mechanic.service_tickets else 0
        response.append(data)
    return jsonify(response), 200


# -------------------- Search Mechanics --------------------
# This route allows searching for mechanics by their name.
# Cached for 30 seconds to improve performance.
@mechanics_bp.route("/search", methods=['GET'])
# @cache.cached(timeout=30)
def search_mechanics():
    
    name = request.args.get('name')
    email = request.args.get('email')
    
    if not name and not email:
        return jsonify({"status":"error","message": "At least one search parameter (name or email) is required."}), 400

    query = select(Mechanic)
    filters = []
    if name:
        filters.append(Mechanic.name.ilike(f'%{name}%'))
    if email:
        filters.append(Mechanic.email.ilike(f'%{email}%'))
    if filters:
        query = query.where(*filters)

    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema_with_tickets.jsonify(mechanics), 200