from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select, delete


#Create a new mechanic
@mechanics_bp.route("/",methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
        email_exist = db.session.execute(select(Mechanic).where(Mechanic.email == mechanic_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"status":"error","message": "A mechanic with this email already exists!"}), 400
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_mechanic = Mechanic(
        name = mechanic_data['name'],
        email = mechanic_data['email'],
        phone = mechanic_data['phone'],
        salary = mechanic_data['salary'],
    )
    db.session.add(new_mechanic)
    db.session.commit()
    return jsonify({"message":"Successfully created mechanic","mechanic": mechanic_schema.dump(new_mechanic)}), 201

#Get all mechanics
@mechanics_bp.route("/",methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    if mechanics == None:
        return jsonify({"message":"Invalid mechanic"}), 404
    return mechanics_schema.jsonify(mechanics), 201

#Get a mechanic
@mechanics_bp.route("/<int:mechanic_id>",methods=['GET'])
def get_mechanic(mechanic_id):
    
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic == None:
        return jsonify({"message":"Invalid mechanic"}), 404
    
    return mechanic_schema.jsonify(mechanic), 201

#Update a mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
def update_mechanic(mechanic_id):
    
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic == None:
        return jsonify({"message":"Invalid mechanic"}), 404
    try:
        mechanic_data = mechanic_schema.load(request.json)    
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

#Delete a mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
def delete_mechanic(mechanic_id):
    
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic == None:
        return jsonify({"message":"Invalid mechanic"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {mechanic_id}"})
