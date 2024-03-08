from flask import Blueprint, jsonify, request
from utils.jwtToken import send_token
from bson import ObjectId 
from bson.json_util import dumps
from cloudinary.uploader import upload
from middleware.auth import isAuthenticatedUser, authorizeRoles
import jwt
import datetime


JWT_SECRET = 'hOBIEr9b5guVvBE5IGBeVqwrBAW7NuUS'

def configure_jwt_secret(secret):
    global JWT_SECRET
    JWT_SECRET = secret

userPredictRoutes = Blueprint('userPredictRoutes', __name__)

@userPredictRoutes.route('/me/quality/predictions/all', methods=['GET'])
@isAuthenticatedUser
def get_user_predictions():
    from app import db

    try:
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token['user_id']

        userPredictions = db.combinedQualityResult.find({'user._id': user_id})

        # Convert the cursor to a list of dictionaries
        userPredictions_list = list(userPredictions)

        # Convert ObjectIds to strings
        for prediction in userPredictions_list:
            prediction['_id'] = str(prediction['_id'])
            if 'quality_id' in prediction:
                prediction['quality_id'] = str(prediction['quality_id'])

        return jsonify({'user_predictions': userPredictions_list}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500