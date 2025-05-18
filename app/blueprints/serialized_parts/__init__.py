from flask import Blueprint

serialized_parts_bp = Blueprint('serialized_parts_bp',__name__)

from . import routes