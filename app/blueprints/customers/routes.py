from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache

#Create a new customer
@customers_bp.route("/",methods=['POST'])
#To prevent spamming of new customer creation.
@limiter.limit("20 per minute") # Limit to 20 requests per minute
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
        phone = customer_data['phone']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message":"Successfully created customer","customer": customer_schema.dump(new_customer)}), 201

#Get all customers
@customers_bp.route("/",methods=['GET'])

# Cache the list of mechanics since it doesn’t change often.
@cache.cached(timeout=60) # Cache the response for 60 seconds

# This route could be called frequently, so rate limiting can prevent excessive requests.
@limiter.limit("10 per minute")  # Limit to 10 requests per minute

def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    if customers == None:
        return jsonify({"message":"Invalid customer"}), 404
    return customers_schema.jsonify(customers), 201

#Get a customer
@customers_bp.route("/<int:customer_id>",methods=['GET'])

#This route could also be abused if someone tries to brute force mechanic IDs.
@limiter.limit("15 per minute")  # Limit to 15 requests per minute

#Cache individual mechanic details to reduce database lookups.
@cache.cached(timeout=30) # Cache the response for 30 seconds

def get_customer(customer_id):
    
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    if customer == None:
        return jsonify({"message":"Invalid customer"}), 404
    
    return customer_schema.jsonify(customer), 201

#Update a customer
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

#Delete a customer
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    if customer == None:
        return jsonify({"message":"Invalid customer"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {customer_id}"})
