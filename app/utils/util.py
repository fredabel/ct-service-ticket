from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get("SECRET_KEY")

def encode_token(user_id, role="user"): 
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), 
        'iat': datetime.now(timezone.utc), 
        'sub': str(user_id),  # User ID
        'role': role # User role
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.userid = int(data['sub'])  # Fetch the user ID
            if not data['role'] == "user":
                return jsonify({'message': 'Access denied!'}), 403
        except jose.exceptions.ExpiredSignatureError:
             return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
             return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated

def mechanic_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.userid = int(data['sub'])  # Fetch the user ID
            if not data['role'] == "mechanic":
                return jsonify({'message': 'Access denied!'}), 403
        except jose.exceptions.ExpiredSignatureError:
             return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
             return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated

# def role_required(*roles):
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             token = None
#             # Look for the token in the Authorization header
#             if 'Authorization' in request.headers:
#                 token = request.headers['Authorization'].split()[1]
                
#             if not token:
#                 return jsonify({'message': 'Token is missing!'}), 401
#             try:
#                 # Decode the token
#                 data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#                 request.userid = int(data['sub'])  # Fetch the user ID
#                 if data.get('role') not in roles:
#                     return jsonify({'message': 'Access denied!'}), 403
#             except jose.exceptions.ExpiredSignatureError:
#                 return jsonify({'message': 'Token has expired!'}), 401
#             except jose.exceptions.JWTError:
#                 return jsonify({'message': 'Invalid token!'}), 401
#             return f(*args, **kwargs)
#         return decorated
#     return decorator

