from app import create_app
from app.models import db
from flask_cors import CORS

app = create_app('DevelopmentConfig')
CORS(app)
with app.app_context():
    db.drop_all()
    db.create_all()

app.run()
    
