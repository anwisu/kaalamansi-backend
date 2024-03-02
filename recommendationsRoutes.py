from flask import Blueprint, jsonify, request
from bson import ObjectId

recommendationRoutes = Blueprint('recommendationRoutes', __name__)

@recommendationRoutes.route('/admin/quality/recommendation/new', methods=['POST'])
def newQualityRecommendation():
    from app import db
    data = request.get_json()
    recommendation_id = db.qualityRecommendations.insert_one(data).inserted_id
    return jsonify(str(recommendation_id)), 201

@recommendationRoutes.route('/admin/quality/recommendations/all', methods=['GET'])
def getAllQualityRecommendation():
    from app import db
    try:
        # Retrieve all documents from the quality collection
        qualityReco= list(db.qualityRecommendations.find({}, {'_id': 0}))

        # Return the quality data as JSON response
        return jsonify({'qualityReco': qualityReco}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['GET'])
def read_recommendation(id):
    from app import db
    recommendation = db.qualityRecommendations.find_one({'_id': ObjectId(id)})
    return jsonify(recommendation), 200

@recommendationRoutes.route('/recommendations/<id>', methods=['PUT'])
def update_recommendation(id):
    from app import db
    data = request.get_json()
    db.qualityRecommendations.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({'message': 'Recommendation updated successfully'}), 200

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['DELETE'])
def delete_recommendation(id):
    from app import db
    db.qualityRecommendations.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Recommendation deleted successfully'}), 200


