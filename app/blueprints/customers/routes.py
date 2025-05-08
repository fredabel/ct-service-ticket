from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


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

    if customer and customer.password == password:
        token = encode_token(customer.id)
        response = {
            "status": "success",
            "message": "successfully logged in.",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password!"}), 401

# -------------------- Create a New Customer --------------------
# This route allows the creation of a new customer.
# Rate limited to 20 requests per minute to prevent spamming.
@customers_bp.route("/",methods=['POST'])
@limiter.limit("20 per minute") 
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
        email_exist = db.session.execute(select(Customer).where(Customer.email == customer_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"status":"error","message": "A customer with this email already exists!"}), 400
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_customer = Customer(
        name = customer_data['name'],
        email = customer_data['email'],
        phone = customer_data['phone'],
        password = customer_data['password']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message":"Successfully created customer","customer": customer_schema.dump(new_customer)}), 201

# -------------------- Get All Customers --------------------
# This route retrieves all customers.
# Cached for 60 seconds to improve performance.
# Rate limited to 10 requests per minute to prevent excessive requests.
@customers_bp.route("/",methods=['GET'])
@cache.cached(timeout=60)
@limiter.limit("10 per minute")
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customers), 200

# -------------------- Get a Specific Customer --------------------
# This route retrieves a specific customer by their ID.
# Cached for 30 seconds to reduce database lookups.
# Rate limited to 15 requests per minute to prevent abuse.
@customers_bp.route("/<int:customer_id>",methods=['GET'])
@limiter.limit("15 per minute")
@cache.cached(timeout=30)
def get_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    if customer == None:
        return jsonify({"message":"Invalid customer"}), 404
    return customer_schema.jsonify(customer), 200

# -------------------- Update a Customer --------------------
# This route allows updating a customer's details by their ID.
# Validates the input and ensures the email is unique.
@customers_bp.route("/<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
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
# Requires a valid token for authentication.
@customers_bp.route("/", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    if customer == None:
        return jsonify({"message":"Invalid customer"}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {customer_id}"}), 200
