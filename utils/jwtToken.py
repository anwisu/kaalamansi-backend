from flask import jsonify
from bson import ObjectId 

def send_token(token, user):
    # Convert ObjectId to string
    user_id = str(user['_id'])
    return jsonify({'user': {'_id': user_id, 'name': user['name'], 'email': user['email'], 'token': token}})


