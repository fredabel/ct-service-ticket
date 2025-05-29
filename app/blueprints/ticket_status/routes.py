from flask import request, jsonify
from app.blueprints.ticket_status import ticket_status_bp
from app.blueprints.ticket_status.schemas import ticket_status_schema, ticket_statuses_schema
from marshmallow import ValidationError
from app.models import TicketStatus, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter

# -------------------- Create a Ticket Status --------------------
# This route allows the creation of a new ticket status.
# Rate limited to 10 requests per hour to prevent spamming.
@ticket_status_bp.route("/",methods=['POST'])
@limiter.limit("10/hour")
def create_ticket_status():
    try:
        ticket_status_data = ticket_status_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_ticket_status = TicketStatus(**ticket_status_data)
    db.session.add(new_ticket_status)
    db.session.commit()
    return jsonify({"status": "success", "message":"Successfully created a new ticket status", "ticket_status": ticket_status_schema.dump(new_ticket_status)}), 201
