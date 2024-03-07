from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from cloudinary.uploader import upload
import os
from werkzeug.utils import secure_filename

recommendationRoutes = Blueprint('recommendationRoutes', __name__)

@recommendationRoutes.route('/admin/disease/recommendation/new', methods=['POST'])
def newdiseaseRecommendation():
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
def getAlldiseaseRecommendation():
    from app import db
    try:
        # Retrieve all documents from the disease collection
        diseaseReco= list(db.diseaseRecommendations.find({}, {'_id': 0}))

        # Return the disease data as JSON response
        return jsonify({'diseaseReco': diseaseReco}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendationRoutes.route('/admin/disease/recommendations/<id>', methods=['GET'])
def read_recommendation(id):
    from app import db
    recommendation = db.diseaseRecommendations.find_one({'_id': ObjectId(id)})
    return jsonify(recommendation), 200

@recommendationRoutes.route('/recommendations/<id>', methods=['PUT'])
def update_recommendation(id):
    from app import db
    data = request.get_json()
    db.diseaseRecommendations.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({'message': 'Recommendation updated successfully'}), 200

@recommendationRoutes.route('/admin/disease/recommendations/<id>', methods=['DELETE'])
def delete_recommendation(id):
    from app import db
    db.diseaseRecommendations.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Recommendation deleted successfully'}), 200


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



