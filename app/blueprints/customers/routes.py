from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema, my_tickets_schema
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------- Login Route --------------------
# This route allows customers to log in using their email and password.
# If the credentials are valid, a token is generated and returned.
@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as err:
        return jsonify(err.messages), 400
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and check_password_hash(customer.password, password):
        token = encode_token(customer.id, role="user")
        response = {
            "status": "success",
            "message": "Successfully logged in.",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({"status":"error","message": "Invalid email or password!"}), 401

# -------------------- Create a New Customer --------------------
# This route allows the creation of a new customer.
# Rate limited to 10 requests per hour to prevent spamming.
@customers_bp.route("/",methods=['POST'])
@limiter.limit("5/hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
        email_exist = db.session.execute(select(Customer).where(Customer.email == customer_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"status":"error","message": "A customer with this email already exists!"}), 400
        customer_data['password'] = generate_password_hash(customer_data['password'])
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"status":"success","message":"Successfully created customer","customer": customer_schema.dump(new_customer)}), 201

# -------------------- Get All Customers --------------------
# This route retrieves all customers.
# Cached for 30 seconds to improve performance.
# Rate limited to 10 requests per hour to prevent abuse.
@customers_bp.route("/",methods=['GET'])
@cache.cached(timeout=30)
@limiter.limit("10/hour")
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if page < 1 or per_page < 1:
        return jsonify({"status": "error", "message": "Page and per_page must be greater than 0."}), 400
    query = select(Customer)
    pagination = db.paginate(query, page=page, per_page=per_page)
    return jsonify({
        "customers": customers_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200

# -------------------- Get a Specific Customer --------------------
# This route retrieves a specific customer by their ID.
# Cached for 30 seconds to reduce database lookups.
@customers_bp.route("/<int:customer_id>",methods=['GET'])
@limiter.exempt
# @cache.cached(timeout=30)
def get_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    if customer == None:
        return jsonify({"status":"error","message":"Invalid customer"}), 404
    return customer_schema.jsonify(customer), 200

# -------------------- Update a Customer --------------------
# This route allows updating a customer's details by their ID.
# Validates the input and ensures the email is unique.
# Rate limited to 5 requests per hour to prevent abuse.
@customers_bp.route("/", methods=['PUT'])
@limiter.limit("5/hour")
@token_required
def update_customer():
    query = select(Customer).where(Customer.id == request.userid)
    customer = db.session.execute(query).scalars().first()
    if customer == None:
        return jsonify({"status":"error","message":"Invalid customer"}), 404
    try:
        customer_data = customer_schema.load(request.json)
        customer_data['password'] = generate_password_hash(customer_data['password'])
    except ValidationError as err:
        return jsonify(err.messages), 400
    if customer_data['email'] != customer.email:
        email_exist = db.session.execute(select(Customer).where(Customer.email == customer_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"status":"error", "message": "A customer with this email already exists"}), 400
    for field, value in customer_data.items():
        setattr(customer, field, value)
    db.session.commit()
    return jsonify({"status":"success","message":"Successfully updated customer","customer": customer_schema.dump(customer)}), 200

# -------------------- Delete a Customer --------------------
# This route allows deleting a customer by their ID.
# Rate limited to 5 requests per day to prevent abuse.
# Requires a valid token for authentication.
@customers_bp.route("/", methods=['DELETE'])
@limiter.limit("5/day")
@token_required
def delete_customer():
    query = select(Customer).where(Customer.id == request.userid)
    customer = db.session.execute(query).scalars().first()
    if customer == None:
        return jsonify({"status":"error","message":"Invalid customer"}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"status":"success","message": f"Succesfully deleted customer {request.userid}"}), 200

# -------------------- Get a Customer's Tickets --------------------
# This route retrieves all service tickets for a specific customer by their ID.
@customers_bp.route("/my-tickets", methods=['GET'])
@limiter.exempt
@token_required
def get_customer_tickets():
    query = select(Customer).where(Customer.id == request.userid)
    customer = db.session.execute(query).scalars().first()
    if customer is None:
        return jsonify({"status":"error","message":"Invalid customer"}), 404
    
    data = my_tickets_schema.dump(customer)
    data["customer"] = customer_schema.dump(customer)
    return jsonify(data), 200


# -------------------- Search Customer --------------------
# This route allows searching for mechanics by their name.
# Cached for 30 seconds to improve performance.
@customers_bp.route("/search", methods=['GET'])
# @cache.cached(timeout=30)
def search_customer():
    
    name = request.args.get('name')
    email = request.args.get('email')
    
    #For future updates, pagination can be added
    # page = request.args.get('page', default=1, type=int)
    # per_page = request.args.get('per_page', default=10, type=int)
    
    if not name and not email:
        return jsonify({"status":"error","message": "At least one search parameter (name or email) is required."}), 400

    query = select(Customer)
    filters = []
    if name:
        filters.append(Customer.name.ilike(f'%{name}%'))
    if email:
        filters.append(Customer.email.ilike(f'%{email}%'))
    if filters:
        query = query.where(*filters)
        
    # customers = db.paginate(query, page=page, per_page=per_page)
    customers = db.session.execute(query).scalars().all()
    # if not customers:
    #     return jsonify({"status": "error","message": "No customers found"}), 404
    return customers_schema.jsonify(customers), 200
