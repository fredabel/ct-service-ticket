from flask import Flask
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_bp
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.part_descriptions import part_descriptions_bp
from app.blueprints.serialized_parts import serialized_parts_bp

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
    
    return app
