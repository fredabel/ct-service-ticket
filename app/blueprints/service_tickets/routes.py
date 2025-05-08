from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema, return_service_ticket_schema, edit_service_ticket_schema
from marshmallow import ValidationError
from app.models import ServiceTicket, Mechanic, db
from sqlalchemy import select, delete

# -------------------- Create a New Service Ticket --------------------
# This route allows the creation of a new service ticket.
@service_tickets_bp.route("/",methods=['POST'])
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
        print(ticket_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_service_ticket = ServiceTicket(
        service_date=ticket_data['service_date'],
        service_desc=ticket_data['service_desc'],
        customer_id=ticket_data['customer_id'],
        vin=ticket_data['vin']
    )
    for mechanic_id in ticket_data['mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalar()
        if mechanic:
            new_service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({"message": "invalid mechanic id"}), 400
        
    db.session.add(new_service_ticket)
    db.session.commit() 
    
    return return_service_ticket_schema.jsonify(new_service_ticket), 201

# -------------------- Get All Service Tickets --------------------
# This route retrieves all service tickets.
@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

# -------------------- Edit Service Tickets --------------------
# This route allows the editing of service tickets.
# It updates the mechanics associated with a service ticket.
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['PUT'])
def edit_service_tickets(service_ticket_id):
    try:
        ticket_data = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    query = select(ServiceTicket).where(ServiceTicket.id==service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    for mechanic_id in ticket_data['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
            
    for mechanic_id in ticket_data['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)   
    db.session.commit()
    return return_service_ticket_schema.jsonify(service_ticket), 200

# -------------------- Get a Specific Service Ticket --------------------
# This route retrieves a specific service ticket by their ID.
@service_tickets_bp.route("/<int:ticket_id>", methods=['DELETE'])
def delete_service_ticket(ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    if not service_ticket:
        return jsonify({"message": "Service ticket not found"}), 404
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": "Service ticket deleted successfully"}), 200
