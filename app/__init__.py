from flask import Flask
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_bp
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.part_descriptions import part_descriptions_bp
from app.blueprints.serialized_parts import serialized_parts_bp
from app.blueprints.categories import categories_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs' 
API_URL = '/static/swagger.yaml'

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Service Ticket Management System API"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(part_descriptions_bp, url_prefix='/part_descriptions')
    app.register_blueprint(serialized_parts_bp, url_prefix='/serialized_parts')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)
    
    return app
