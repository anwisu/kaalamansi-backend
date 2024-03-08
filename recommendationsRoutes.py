from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from cloudinary.uploader import upload
from pymongo import ReturnDocument
import base64
import io
import os
from werkzeug.utils import secure_filename

recommendationRoutes = Blueprint('recommendationRoutes', __name__)

# QUALITY RECOMMENDATIONS
@recommendationRoutes.route('/admin/quality/recommendation/new', methods=['POST'])
def newQualityRecommendation():
    from app import db

    # Get images from the request
    images = request.files.getlist('images')

    # List to store image URLs
    image_urls = []

    # Upload each image to Cloudinary
    for image in images:
        try:
            # Save the image temporarily
            filename = secure_filename(image.filename)
            image.save(filename)

            # Upload the image to Cloudinary
            result = upload(filename, folder='recommendations', width=150, crop="scale")

            # Delete the temporary image
            os.remove(filename)

            # Add the image URL to the list
            image_urls.append({
                'public_id': result['public_id'],
                'url': result['secure_url']
            })
        except Exception as e:
            return jsonify({'message': str(e)}), 400

    # Get other form data
    factor = request.form.get('factor')
    value = request.form.get('value')
    recommendation = request.form.get('recommendation')

    # Prepare data for database
    data = {
        'factor': factor,
        'value': value,
        'recommendation': recommendation,
        'images': image_urls,
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

# @recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['GET'])
# def getQualityRecoDetails(id):
#     from app import db
#     try:
#         recommendation = db.qualityRecommendations.find_one({"_id": ObjectId(id)}, {'_id': 0})
#         if recommendation is None:
#             return jsonify({'error': 'Recommendation not found'}), 404
#         return jsonify(recommendation), 200
#     except Exception as e:
#         print(str(e))
#         return jsonify({'error': str(e)}), 500

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['GET'])
def get_quality_reco(id):
    from app import db
    try:
        recommendation = db.qualityRecommendations.find_one({'_id': ObjectId(id)})
        if recommendation:
            # Convert ObjectId to string to make it JSON serializable
            recommendation['_id'] = str(recommendation['_id'])
            return jsonify(recommendation), 200
        else:
            return jsonify({'message': 'Recommendation not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['PUT'])
def updateQualityReco(id):
    from app import db
    data = request.get_json()

    # Handle images update
    if 'images' in data:
        images = data['images']
        image_data = []
        try:
            for image in images:
                if not 'cloudinary' in image:
                    # Decode the base64 image data
                    image_decoded = base64.b64decode(image['data'].split(',')[1])
                    image_io = io.BytesIO(image_decoded)

                    # Upload the image to Cloudinary
                    result = upload(image_io, folder='recommendations', width=150, crop="scale")

                    # Add the image URL to the list
                    image_data.append({
                        'public_id': result['public_id'],
                        'url': result['secure_url']
                    })
                else:
                    image_data.append(image)
            data['images'] = image_data
        except Exception as e:
            return jsonify({'message': str(e)}), 400

    # Update the data in the database
    try:
        updated_recommendation = db.qualityRecommendations.find_one_and_update(
            {'_id': ObjectId(id)},
            {'$set': data},
            return_document=ReturnDocument.AFTER
        )
        if not updated_recommendation:
            return jsonify({'message': 'Recommendation not updated'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

    return jsonify(str(updated_recommendation['_id'])), 200

@recommendationRoutes.route('/admin/quality/recommendations/<id>', methods=['DELETE'])
def delete_recommendation(id):
    from app import db
    db.qualityRecommendations.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Recommendation deleted successfully'}), 200

# DISEASE RECOMMENDATIONS
@recommendationRoutes.route('/admin/disease/recommendation/new', methods=['POST'])
def newDiseaseRecommendation():
    from app import db

    # Get images from the request
    images = request.files.getlist('images')

    # List to store image URLs
    image_urls = []

    # Upload each image to Cloudinary
    for image in images:
        try:
            # Save the image temporarily
            filename = secure_filename(image.filename)
            image.save(filename)

            # Upload the image to Cloudinary
            result = upload(filename, folder='recommendations', width=150, crop="scale")

            # Delete the temporary image
            os.remove(filename)

            # Add the image URL to the list
            image_urls.append({
                'public_id': result['public_id'],
                'url': result['secure_url']
            })
        except Exception as e:
            return jsonify({'message': str(e)}), 400

    # Get other form data
    factor = request.form.get('factor')
    value = request.form.get('value')
    recommendation = request.form.get('recommendation')

    # Prepare data for database
    data = {
        'factor': factor,
        'value': value,
        'recommendation': recommendation,
        'images': image_urls,
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
        diseaseReco= list(db.diseaseRecommendations.find({}, {'_id': 0}))

        # Return the disease data as JSON response
        return jsonify({'diseaseReco': diseaseReco}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



