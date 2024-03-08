from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from cloudinary.uploader import upload

recommendationRoutes = Blueprint('recommendationRoutes', __name__)

# QUALITY RECOMMENDATIONS
@recommendationRoutes.route('/admin/quality/recommendation/new', methods=['POST'])
def newQualityRecommendation():
    from app import db
    data = request.json
    image = data['image']
    try:
        result = upload(image, folder='recommendations', width=150, crop="scale")
        image_url = result['url']  
        image_public_id = result['public_id'] 
    except Exception as e:
        return jsonify({'message': str(e)}), 400

    data = {
        'factor': data['factor'],
        'value': data['value'],
        'recommendation': data['recommendation'],
        'image': {
            'public_id': image_public_id,
            'url': image_url
        },
        'created_at': datetime.utcnow()
    }

    # Insert the data into the database
    recommendation_id = db.qualityRecommendations.insert_one(data).inserted_id

    return jsonify(str(recommendation_id)), 201

@recommendationRoutes.route('/admin/quality/recommendations/all', methods=['GET'])
def getAllQualityRecommendation():
    from app import db
    try:
        # Retrieve all documents from the quality collection
        qualityReco= list(db.qualityRecommendations.find())
        for quality in qualityReco:
            quality['_id'] = str(quality['_id'])

        # Return the quality data as JSON response
        return jsonify({'qualityReco': qualityReco}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['GET'])
def getQualityReco(id):
    from app import db
    try:
        recommendation = db.qualityRecommendations.find_one({'_id': ObjectId(id)})
        if recommendation:
            recommendation['_id'] = str(recommendation['_id'])
            return jsonify({'qualityReco': recommendation}), 200
        else:
            return jsonify({'message': 'Recommendation not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['PUT'])
def updateQualityReco(id):
    from app import db
    try:
        data = request.form
        update_data = {k: v for k, v in data.items() if k in ['factor', 'value', 'recommendation']}

        # Handle image update
        if 'image' in request.files:
            image = request.files['image']
            try:
                result = upload(image, folder='recommendations', width=150, crop="scale")
                image_url = result['url']
                image_public_id = result['public_id']
                update_data['image'] = {
                    "url": image_url,
                    "public_id": image_public_id,
                }
            except Exception as e:
                return jsonify({'message': str(e)}), 400

        # Update the user document with the given ID
        qualityReco = db.qualityRecommendations.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        if qualityReco.matched_count == 0:
            return jsonify({'message': 'Recommendation not found'}), 404

        return jsonify({'message': 'Recommendation updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['DELETE'])
def deleteQualityReco(id):
    from app import db
    db.qualityRecommendations.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Recommendation deleted successfully'}), 200

# DISEASE RECOMMENDATIONS
@recommendationRoutes.route('/admin/disease/recommendation/new', methods=['POST'])
def newDiseaseRecommendation():
    from app import db
    data = request.json
    image = data['image']
    try:
        result = upload(image, folder='recommendations', width=150, crop="scale")
        image_url = result['url']  
        image_public_id = result['public_id'] 
    except Exception as e:
        return jsonify({'message': str(e)}), 400

    data = {
        'factor': data['factor'],
        'value': data['value'],
        'recommendation': data['recommendation'],
        'image': {
            'public_id': image_public_id,
            'url': image_url
        },
        'created_at': datetime.utcnow()
    }

    # Insert the data into the database
    recommendation_id = db.diseaseRecommendations.insert_one(data).inserted_id

    return jsonify(str(recommendation_id)), 201

@recommendationRoutes.route('/admin/disease/recommendations/all', methods=['GET'])
def getAllDiseaseRecommendation():
    from app import db
    try:
        # Retrieve all documents from the disease collection
        diseaseReco= list(db.diseaseRecommendations.find())
        for disease in diseaseReco:
            disease['_id'] = str(disease['_id'])

        # Return the disease data as JSON response
        return jsonify({'diseaseReco': diseaseReco}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendationRoutes.route('/admin/disease/recommendations/<id>', methods=['GET'])
def getDiseaseReco(id):
    from app import db
    try:
        recommendation = db.diseaseRecommendations.find_one({'_id': ObjectId(id)})
        if recommendation:
            recommendation['_id'] = str(recommendation['_id'])
            return jsonify({'diseaseReco': recommendation}), 200
        else:
            return jsonify({'message': 'Recommendation not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@recommendationRoutes.route('/admin/disease/recommendations/<id>', methods=['PUT'])
def updateDiseaseReco(id):
    from app import db
    try:
        data = request.form
        update_data = {k: v for k, v in data.items() if k in ['factor', 'value', 'recommendation']}

        # Handle image update
        if 'image' in request.files:
            image = request.files['image']
            try:
                result = upload(image, folder='recommendations', width=150, crop="scale")
                image_url = result['url']
                image_public_id = result['public_id']
                update_data['image'] = {
                    "url": image_url,
                    "public_id": image_public_id,
                }
            except Exception as e:
                return jsonify({'message': str(e)}), 400

        # Update the user document with the given ID
        diseaseReco = db.diseaseRecommendations.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        if diseaseReco.matched_count == 0:
            return jsonify({'message': 'Recommendation not found'}), 404

        return jsonify({'message': 'Recommendation updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@recommendationRoutes.route('/admin/disease/recommendations/<id>', methods=['DELETE'])
def deleteDiseaseReco(id):
    from app import db
    db.diseaseRecommendations.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Recommendation deleted successfully'}), 200