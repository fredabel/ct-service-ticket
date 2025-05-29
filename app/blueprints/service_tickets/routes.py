from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema, return_service_ticket_schema, edit_service_ticket_schema
from app.blueprints.mechanics.schemas import mechanics_schema
from app.blueprints.part_descriptions.schemas import part_description_schema, part_descriptions_schema
from app.blueprints.serialized_parts.schemas import serialized_part_schema, serialized_parts_schema
from marshmallow import ValidationError
from app.models import Customer, ServiceTicket, Mechanic, PartDescription, SerializedPart, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
# from app.utils.util import encode_token

# -------------------- Create a New Service Ticket --------------------
# This route allows the creation of a new service ticket.
# Rate limited to 10 requests per hour to prevent spamming.
@service_tickets_bp.route("/",methods=['POST'])
@limiter.limit("10/hour")
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, ticket_data['customer_id'])
    if not customer:
        return jsonify({"status": "error", "message": "Invalid customer id"}), 400
    
    # Remove 'mechanic_ids' before using ticket_data for model creation/update
    mechanic_ids = ticket_data.pop('mechanic_ids', [])
    new_service_ticket = ServiceTicket(**ticket_data)
    # new_service_ticket = ServiceTicket(
    #     service_date=ticket_data['service_date'],
    #     service_desc=ticket_data['service_desc'],
    #     customer_id=ticket_data['customer_id'],
    #     vin=ticket_data['vin']
    # )
    
    for mechanic_id in mechanic_ids:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalar()
        if mechanic:
            new_service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({"status": "error", "message": "Invalid mechanic id"}), 400 
    db.session.add(new_service_ticket)
    db.session.commit() 
    return return_service_ticket_schema.jsonify(new_service_ticket), 201

# -------------------- Get All Service Tickets --------------------
# This route retrieves all service tickets.
# Cached for 60 seconds to improve performance.
@service_tickets_bp.route("/", methods=['GET'])
# @cache.cached(timeout=60)
@limiter.exempt
def get_service_tickets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = select(ServiceTicket)
    pagination = db.paginate(query, page=page, per_page=per_page)
    return jsonify({
        "tickets": service_tickets_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200

# -------------------- Get Individual Service Ticket --------------------
# This route retrieves specific service ticket.
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['GET'])
@limiter.exempt
def get_service_ticket(service_ticket_id):
    ticket = db.session.get(ServiceTicket,service_ticket_id)
    if ticket:
        return service_ticket_schema.jsonify(ticket), 200
    return jsonify({"status":"error", "message":"Invalid ticket id"}), 404

# -------------------- Update Service Ticket --------------------
# This route allows the editing of service tickets.
# Rate limited to 10 requests per hour to prevent abuse.
@service_tickets_bp.route("/<int:ticket_id>", methods=['PUT'])
@limiter.limit("10/hour")
def update_service_ticket(ticket_id):
    
    try:
        ticket_data = service_ticket_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id==ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    if not service_ticket:
        return jsonify({"status": "error", "message": "Service ticket not found"}), 404
    
    customer = db.session.get(Customer, ticket_data['customer_id'])
    if not customer:
        return jsonify({"status": "error", "message": "Invalid customer id"}), 400
    
    for field, value in ticket_data.items():
        if not field == "mechanic_ids":
            setattr(service_ticket, field, value)
            
    mechanic_ids = ticket_data.get('mechanic_ids', [])
    for mechanic_id in mechanic_ids:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalar()
        
        if not mechanic:
            return jsonify({"status": "error", "message": "Invalid mechanic id"}), 400 
        
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({"status": "error", "message": f"The mechanic {mechanic_id} already exists in this ticket."}), 400
        
    db.session.commit()
    
    return return_service_ticket_schema.jsonify(service_ticket), 201
    
    

# -------------------- Edit Mechanics of Service Tickets --------------------
# This route allows the editing of service tickets.
# Rate limited to 10 requests per hour.
@service_tickets_bp.route("/<int:id>/edit-mechanics", methods=['PUT'])
@limiter.limit("10/hour")
def edit_service_tickets(id):
    try:
        ticket_data = edit_service_ticket_schema.load(request.json)
        add_ids = ticket_data.get('add_mechanic_ids', [])
        remove_ids = ticket_data.get('remove_mechanic_ids', [])
    except ValidationError as e:
        return jsonify(e.messages), 400
    query = select(ServiceTicket).where(ServiceTicket.id==id)
    service_ticket = db.session.execute(query).scalars().first()
    
    if not service_ticket:
        return jsonify({"status": "error", "message": "Service ticket not found"}), 404
    
    for mechanic_id in add_ids:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({"status": "error", "message": f"The mechanic {mechanic_id} already exists in this ticket."}), 400
    
    for mechanic_id in remove_ids:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)
        else:
            return jsonify({"status": "error", "message": f"The mechanic {mechanic_id} not exist in this ticket."}), 400

    db.session.commit()
    return return_service_ticket_schema.jsonify(service_ticket), 200

# -------------------- Add Mechanic to Service Ticket --------------------
# Rate limited to 10 requests per hour.
@service_tickets_bp.route("/<int:ticket_id>/add-mechanic/<int:mechanic_id>", methods=['PUT'])
@limiter.limit("10/hour")
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({
                'message': f"Mechanic {mechanic.name} successfully added to ticket",
                'service_ticket': service_ticket_schema.dump(ticket),
                'status': 'success'
                # 'mechanics': mechanics_schema.dump(ticket.mechanics)
            }), 200
            
        return jsonify({"status": "error", "message":  "Mechanic already assigned to this ticket."}), 400
    
    return jsonify({"status": "error", "message": "Service ticket or mechanic not found."}), 404

# -------------------- Remove Mechanic from Service Ticket --------------------
# This route allows removing a mechanic from a service ticket.
# Rate limited to 10 requests per hour.
@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=['PUT'])
@limiter.limit("10/hour")
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': f"Mechanic {mechanic.name} successfully removed from ticket",
                'service_ticket': service_ticket_schema.dump(ticket),
                # 'mechanics': mechanics_schema.dump(ticket.mechanics)
            }), 200  
        return jsonify({"status": "error", "message": "Mechanic not included on this ticket."}), 400
    return jsonify({"status": "error", "message": "Service ticket or mechanic not found."}), 404

# -------------------- Add Part to Service Ticket --------------------
# Rate limited to 10 requests per hour.
@service_tickets_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=['PUT'])
@limiter.limit("10/hour")
def add_item(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(SerializedPart, part_id)

    if ticket and part:
        if not part.ticket_id:
            ticket.ticket_items.append(part)
            db.session.commit()
            return jsonify({
                "status": "success",
                'message': f"Part {part.description.name} successfully added to ticket",
                # 'part': part_description_schema.dump(part.description),
                'service_ticket': service_ticket_schema.dump(ticket),
                # 'items': serialized_parts_schema.dump(ticket.ticket_items)
            }), 200
        return jsonify({"status": "error", "message": "Part already assigned to a ticket."}), 400  
    return jsonify({"status": "error", "message": "Service ticket or serialized part not found."}), 404

# -------------------- Remove Part from Service Ticket --------------------
# This route allows removing a part from a service ticket by ticket and serialzied part ID.
# Rate limited to 10 requests per hour.
@service_tickets_bp.route("/<int:ticket_id>/remove-part/<int:part_id>", methods=['PUT'])
@limiter.limit("10/hour")
def remove_part_from_ticket(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(SerializedPart, part_id)

    if not ticket or not part:
        return jsonify({"status":"error", "message": "Service ticket or serialized part not found."}), 404

    if part in ticket.ticket_items:
        ticket.ticket_items.remove(part)
        db.session.commit()
        return jsonify({
            "status":"success",
            'message': f"Part {part.description.name} successfully removed from ticket",
            'service_ticket': service_ticket_schema.dump(ticket),
            # 'items': serialized_parts_schema.dump(ticket.ticket_items)
        }), 200
    else:
        return jsonify({"status":"error","message": "Serialized part not included to this ticket."}), 400

# -------------------- Add parts to cart to a Serivce Ticket --------------------
# This route allows adding parts to a service ticket's cart.
# It checks if the part is not already assigned to another ticket before adding it to the cart.
@service_tickets_bp.route("/<int:ticket_id>/add-to-cart/<int:part_id>", methods=['PUT'])
@limiter.exempt
def add_to_cart(ticket_id, part_id):
    
    ticket = db.session.get(ServiceTicket, ticket_id)
    part_desc = db.session.get(PartDescription, part_id)
    
    if not ticket or not part_desc:
        return jsonify({"status":"error","message": "Invalid ticket_id or part_id."}), 404

    # Get quantity from JSON body, default to 1 if not provided
    data = request.get_json(silent=True) or {}
    quantity = data.get('quantity', 1)

    # Find available serialized parts for this description
    available_parts = [p for p in part_desc.serial_items if not p.ticket_id]
    if len(available_parts) < quantity:
        return jsonify({"status":"error","message": f"Only {len(available_parts)} stock(s) available for this part."}), 400

    # Add the requested quantity of parts to the ticket
    for part in available_parts[:quantity]:
        ticket.ticket_items.append(part)
    db.session.commit()

    return jsonify({
        'status':'success', 
        'message': f"{quantity} part(s) successfully added to cart",
        'service_ticket': service_ticket_schema.dump(ticket),
        # 'items': serialized_parts_schema.dump(ticket.ticket_items)
    }), 200
    
    # parts = part_desc.serial_items
    # for part in parts:
    #     if not part.ticket.id:
    #         ticket.ticket_items.append(part)
    #         db.session.commit()
    #         return jsonify({
    #             'message': f"Part {part.name} successfully added to cart",
    #             'service_ticket': service_ticket_schema.dump(ticket),
    #             'items': serialized_parts_schema.dump(ticket.serialized_parts)
    #         }), 200
   
    # return jsonify({"error": "Invalid ticket_id."}), 400

# -------------------- Delete a Specific Service Ticket --------------------
# This route deletes a specific service ticket by their ID.
# Rate limited to 5 requests per hour.
@service_tickets_bp.route("/<int:id>", methods=['DELETE'])
@limiter.limit("5/hour")
def delete_service_ticket(id):
    query = select(ServiceTicket).where(ServiceTicket.id == id)
    service_ticket = db.session.execute(query).scalars().first()
    if not service_ticket:
        return jsonify({"status": "error", "message": "Service ticket not found"}), 404
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"status":"success", "message": f"Successfully deleted service ticket {id}"}), 200
