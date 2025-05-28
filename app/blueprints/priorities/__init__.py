from flask import Blueprint

priorities_bp = Blueprint('priorities_bp',__name__)

from . import routes