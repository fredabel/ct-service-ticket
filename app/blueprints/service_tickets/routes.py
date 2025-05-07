from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema, return_service_ticket_schema
from marshmallow import ValidationError
from app.models import ServiceTicket, Mechanic, db
from sqlalchemy import select, delete

#Create a service ticket
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

#Get all service tickets
@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

#Delete a service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=['DELETE'])
def delete_service_ticket(ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    if not service_ticket:
        return jsonify({"message": "Service ticket not found"}), 404
    
    db.session.delete(service_ticket)
    db.session.commit()
    
    return jsonify({"message": "Service ticket deleted successfully"}), 200
