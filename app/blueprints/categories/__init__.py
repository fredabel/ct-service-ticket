from flask import Blueprint

categories_bp = Blueprint('categories_bp',__name__)

from . import routes