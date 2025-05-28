from flask import Blueprint

ticket_status_bp = Blueprint('ticket_status_bp',__name__)

from . import routes