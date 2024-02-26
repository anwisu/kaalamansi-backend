from flask import jsonify, request
from functools import wraps
from flask import g
from bson import ObjectId 


import jwt

JWT_SECRET = 'hOBIEr9b5guVvBE5IGBeVqwrBAW7NuUS'

def isAuthenticatedUser(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app import db
        token = request.headers.get('Authorization').split(' ')[1]
        if not token:
            return jsonify({'message':'Login first to access this resource'}), 401
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return jsonify({'message':'Invalid token'}), 401
        g.user = db.users.find_one({"_id": ObjectId(decoded['user_id'])})
        return f(*args, **kwargs)
    return decorated_function

def authorizeRoles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user['role'] not in roles:
                return jsonify({'message':f'Role ({g.user["role"]}) is not allowed to acccess this resource'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator