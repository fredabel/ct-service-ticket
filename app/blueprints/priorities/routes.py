from flask import request, jsonify
from app.blueprints.priorities import priorities_bp
from app.blueprints.priorities.schemas import priority_schema, priorities_schema
from marshmallow import ValidationError
from app.models import Priority, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter


# -------------------- Create a Priority --------------------
# This route allows the creation of a new priority.
# Rate limited to 10 requests per hour to prevent spamming.
@priorities_bp.route("/",methods=['POST'])
@limiter.limit("10/hour")
def create_priority():
    try:
        priority_data = priority_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_priority = Priority(**priority_data)
    db.session.add(new_priority)
    db.session.commit()
    return jsonify({"status": "success","message":"Successfully created a new priority","priority": priority_schema.dump(new_priority)}), 201