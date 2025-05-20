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
    print(customer.email)
    if customer and check_password_hash(customer.password, password):
        token = encode_token(customer.id, "customer")
        response = {
            "status": "success",
            "message": "Successfully logged in.",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password!"}), 401

# -------------------- Create a New Customer --------------------
# This route allows the creation of a new customer.
# Rate limited to 10 requests per hour to prevent spamming.
@customers_bp.route("/",methods=['POST'])
@limiter.limit("3/hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
        email_exist = db.session.execute(select(Customer).where(Customer.email == customer_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"status":"error","message": "A customer with this email already exists!"}), 400
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer_data['password'] = generate_password_hash(customer_data['password'])
    new_customer = Customer(**customer_data)
    
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message":"Successfully created customer","customer": customer_schema.dump(new_customer)}), 201

# -------------------- Get All Customers --------------------
# This route retrieves all customers.
# Cached for 30 seconds to improve performance.
# Rate limited to 10 requests per hour to prevent abuse.
@customers_bp.route("/",methods=['GET'])
@cache.cached(timeout=30)
@limiter.limit("10/hour")
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customers), 200

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
        return jsonify({"message":"Invalid customer"}), 404
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
    print(customer)
    if customer == None:
        return jsonify({"message":"Invalid customer"}), 404
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    if customer_data['email'] != customer.email:
        email_exist = db.session.execute(select(Customer).where(Customer.email == customer_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"message": "A customer with this email already exists"}), 400
    for field, value in customer_data.items():
        setattr(customer, field, value)
    db.session.commit()
    return jsonify({"message":"Successfully updated customer","customer": customer_schema.dump(customer)}), 200

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
        return jsonify({"message":"Invalid customer"}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {request.userid}"}), 200

# -------------------- Get a Customer's Tickets --------------------
# This route retrieves all service tickets for a specific customer by their ID.
@customers_bp.route("/my-tickets", methods=['GET'])
@limiter.exempt
@token_required
def get_customer_tickets():
    if request.user_type != "customer":
        return jsonify({"message": "Unauthorized access!"}), 403
    
    query = select(Customer).where(Customer.id == request.userid)
    customer = db.session.execute(query).scalars().first()
    if customer is None:
        return jsonify({"message": "Invalid customer"}), 404
    return jsonify({"customer": my_tickets_schema.dump(customer)}), 200
