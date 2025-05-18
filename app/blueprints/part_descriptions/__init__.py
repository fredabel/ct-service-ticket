from flask import Blueprint

part_descriptions_bp = Blueprint('part_descriptions_bp',__name__)

from . import routes