from flask import jsonify, make_response
from bson import ObjectId 
import datetime

def send_token(token, user):
    # Convert ObjectId to string
    user_id = str(user['_id'])
    response = jsonify({'user': {'_id': user_id, 'name': user['name'], 'email': user['email'], 'token': token}})
    
    # Set cookie in the response
    response = make_response(response)
    response.set_cookie('token', token, httponly=True, expires=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    
    return response
