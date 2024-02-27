from flask import Blueprint, jsonify, request
from utils.jwtToken import send_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId 
import jwt
import datetime
from middleware.auth import isAuthenticatedUser, authorizeRoles

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
    token = jwt.encode({'user_id': str(new_user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=90)}, JWT_SECRET)
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
    token = jwt.encode({'user_id': str(user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=90)}, JWT_SECRET)
    
    response_data = {
        'success': True,
        'token': token,
        'user': user
    }
    
    return jsonify(response_data), 200

@userRoutes.route('/me', methods=['GET'])
@isAuthenticatedUser
def get_user_profile():
    from app import db
    token = request.headers.get('Authorization').split(' ')[1]
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    user_id = decoded_token['user_id']
    user = db.users.find_one({"_id": ObjectId(user_id)})
    # Convert ObjectId to string before serializing to JSON
    user['_id'] = str(user['_id'])
    return jsonify({'user': user}), 200

@userRoutes.route('/me/update', methods=['PUT'])
@isAuthenticatedUser
def updateProfile():
    from app import db
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Missing Authorization header'}), 400

    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    user_id = decoded_token['user_id']
    user = db.users.find_one({"_id": ObjectId(user_id)})

    data = request.json

    update_data = {k: v for k, v in data.items() if k in ['name', 'email']}
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated_user = db.users.find_one({"_id": ObjectId(user_id)})
    updated_user['_id'] = str(updated_user['_id'])

    return jsonify({'user': updated_user}), 200


@userRoutes.route('/logout', methods=['GET'])
def logout():
    # Clear the token cookie
    response = jsonify({'message': 'Logged out successfully'})
    response.set_cookie('token', '', expires=0, httponly=True)
    return response, 200

@userRoutes.route('/admin/users', methods=['GET'])
@isAuthenticatedUser
@authorizeRoles('admin')
def getAllUsers():
    from app import db
    try:

        users = list(db.users.find())
        for user in users:
            user['_id'] = str(user['_id'])

        # Return the quality data as JSON response
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@userRoutes.route('/admin/users/<id>', methods=['GET'])
@isAuthenticatedUser
@authorizeRoles('admin')
def getUser(id):
    from app import db
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing Authorization header'}), 400

        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token['user_id']

        # Retrieve the user document with the given ID
        user = db.users.find_one({"_id": ObjectId(id)}, {'_id': 0})

        if user is None:
            return jsonify({'message': 'User not found'}), 404

        # Return the user data as JSON response
        return jsonify({'user': user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@userRoutes.route('/admin/users/<id>', methods=['PUT'])
@isAuthenticatedUser
@authorizeRoles('admin')
def updateUser(id):
    from app import db
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing Authorization header'}), 400

        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token['user_id']

        # Retrieve the update data from the request
        data = request.json
        update_data = {k: v for k, v in data.items() if k in ['name', 'email', 'role']}

        # Update the user document with the given ID
        result = db.users.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        if result.matched_count == 0:
            return jsonify({'message': 'User not found'}), 404

        # Return a success message
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@userRoutes.route('/admin/users/<id>', methods=['DELETE'])
@isAuthenticatedUser
@authorizeRoles('admin')
def deleteUser(id):
    from app import db
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing Authorization header'}), 400

        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token['user_id']

        # Delete the user document with the given ID
        result = db.users.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            return jsonify({'message': 'User not found'}), 404

        # Return a success message
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500