from flask import Blueprint, jsonify, request
from utils.jwtToken import send_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId  # Import ObjectId for MongoDB queries
import jwt
import datetime

JWT_SECRET = 'hOBIEr9b5guVvBE5IGBeVqwrBAW7NuUS'

def configure_jwt_secret(secret):
    global JWT_SECRET
    JWT_SECRET = secret

userRoutes = Blueprint('userRoutes', __name__)

# User registration route
@userRoutes.route('/register', methods=['POST'])
def registerUser():
    from app import db
    data = request.json
    hashed_password = generate_password_hash(data['password'])
    user = {
        "name": data['name'],
        "email": data['email'],
        "password": hashed_password,
    }
    result = db.users.insert_one(user)  # Assuming 'users' is the name of your MongoDB collection
    new_user = db.users.find_one({"_id": result.inserted_id})
    token = jwt.encode({'user_id': str(new_user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, JWT_SECRET)
    return send_token(token, new_user), 200

# User login route
@userRoutes.route('/login', methods=['POST'])
def login_user():
    from app import db
    data = request.json
    user = db.users.find_one({"email": data['email']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    user['_id'] = str(user['_id'])  # Convert ObjectId to string
    
    # token = jwt.encode({'user_id': str(user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, JWT_SECRET)
    token = jwt.encode({'user_id': str(user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, JWT_SECRET)
    
    response_data = {
        'success': True,
        'token': token,
        'user': user
    }
    
    return jsonify(response_data), 200

# User profile route
@userRoutes.route('/me', methods=['GET'])
def get_user_profile():
    from app import db
    token = request.headers.get('Authorization').split(' ')[1]
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    user_id = decoded_token['user_id']
    user = db.users.find_one({"_id": ObjectId(user_id)})
    # Convert ObjectId to string before serializing to JSON
    user['_id'] = str(user['_id'])
    return jsonify({'user': user}), 200


@userRoutes.route('/logout', methods=['GET'])
def logout():
    # Clear the token cookie
    response = jsonify({'message': 'Logged out successfully'})
    response.set_cookie('token', '', expires=0, httponly=True)
    return response, 200