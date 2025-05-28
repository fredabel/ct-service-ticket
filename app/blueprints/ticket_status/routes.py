from flask import request, jsonify
from app.blueprints.ticket_status import ticket_status_bp
from app.blueprints.ticket_status.schemas import ticket_status_schema
from marshmallow import ValidationError
from app.models import TicketStatus, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
