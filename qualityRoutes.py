from flask import Blueprint, jsonify, request
from model import load_quality_model
import pandas as pd
import numpy as np
from datetime import datetime
from bson import ObjectId 
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, auc
from middleware.auth import isAuthenticatedUser, authorizeRoles
import jwt

qualityRoutes = Blueprint('qualityRoutes', __name__)

JWT_SECRET = 'hOBIEr9b5guVvBE5IGBeVqwrBAW7NuUS'

def configure_jwt_secret(secret):
    global JWT_SECRET
    JWT_SECRET = secret

@qualityRoutes.route('/admin/quality/dataset', methods=['GET'])
def getDataset():
    df = pd.read_csv('./model/kalamansi_dataset.csv')
    shape = df.shape
    data = df.to_json(orient='records')  # Convert the DataFrame to a JSON string

    return jsonify({'shape': shape, 'data': data})

@qualityRoutes.route('/quality/classification-report', methods=['GET'])
def get_classification_report():
    y_test = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1]
    y_pred = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    accuracy = accuracy_score(y_test, y_pred)
    return jsonify({
        'report': report,
        'accuracy': accuracy
    })

@qualityRoutes.route('/quality/confusion-matrix', methods=['GET'])
def predict():
    y_test = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1]
    predict = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]
    
    cm = confusion_matrix(y_test, predict)
    conf_matrix = pd.DataFrame(data=cm, columns=['Predicted:0', 'Predicted:1'], index=['Actual:0', 'Actual:1'])
    conf_matrix_dict = conf_matrix.to_dict('list') # Convert to a dictionary of lists
    print("Confusion Matrix:", conf_matrix) 
    

    return jsonify(conf_matrix_dict)


@qualityRoutes.route('/quality/roc-curve', methods=['GET'])
def get_roc_curve():
    y_test = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1]
    y_pred = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]

    # Calculate true positive (TP), false positive (FP), true negative (TN), and false negative (FN) rates
    fpr, tpr, _ = roc_curve(y_test, y_pred)
    roc_auc = auc(fpr, tpr)

    # Convert numpy arrays to lists before returning as JSON
    return jsonify({
        'fpr': fpr.tolist(),
        'tpr': tpr.tolist(),
        'roc_auc': roc_auc
    })

# Define mapping dictionaries
firm_mapping = {'flabby': 0, 'firm': 1}
shape_mapping = {'oblong': 0, 'spherical': 1}
blemishes_mapping = {'not present': 0, 'present': 1}
fertilized_mapping = {'not fertilized': 0, 'fertilized': 1}
watering_mapping = {'irregular': 0, 'regular': 1}
pruning_mapping = {'not regular': 0, 'regular': 1}
pest_mapping = {'no': 0, 'yes': 1}
quality_mapping = {'low': 0, 'high': 1}
size_mapping = {'small': 0, 'medium': 1, 'big': 2}
color_mapping = {'dull yellow': 0, 'bright green': 1, 'mixed': 2}
soil_mapping = {'loamy': 0, 'clayey': 1, 'sandy': 2}
sun_mapping = {'full shade': 0, 'partial shade': 1, 'full sun': 2}
location_mapping = {'patio': 0, 'balcony': 1, 'rooftop': 2}

@qualityRoutes.route('/predict/quality', methods=['POST'])
@isAuthenticatedUser
def predictQuality():
    from app import db
    quality_model = load_quality_model()
    try:
        # Get input features from JSON data
        data = request.get_json()
        size = data['size']
        firmness = data['firmness']
        shape = data['shape']
        skin_color = data['skin_color']
        blemishes = data['blemishes']
        soil_type = data['soil_type']
        sun_exposure = data['sun_exposure']
        location = data['location']
        fertilized = data['fertilized']
        watering_sched = data['watering_sched']
        pruning = data['pruning']
        pest_presence = data['pest_presence']
        
        # Map categorical inputs to numerical representations
        size_val = size_mapping[size]
        firmness_val = firm_mapping[firmness]
        shape_val = shape_mapping[shape]
        skin_color_val = color_mapping[skin_color]
        blemishes_val = blemishes_mapping[blemishes]
        soil_type_val = soil_mapping[soil_type]
        sun_exposure_val = sun_mapping[sun_exposure]
        location_val = location_mapping[location]
        fertilized_val = fertilized_mapping[fertilized]
        watering_sched_val = watering_mapping[watering_sched]
        pruning_val = pruning_mapping[pruning]
        pest_presence_val = pest_mapping[pest_presence]
        
        # Create input data for prediction
        input_quality = pd.DataFrame({
            'fruit_firmness': [firmness_val],
            'fruit_shape': [shape_val],
            'fruit_blemishes': [blemishes_val],
            'fertilizer': [fertilized_val],
            'water_sched': [watering_sched_val],
            'fruit_pruning': [pruning_val],
            'pest': [pest_presence_val],
            'fruit_size': [size_val],
            'fruit_color': [skin_color_val],
            'soil': [soil_type_val],
            'sun_expo': [sun_exposure_val],
            'loc': [location_val]
        })
        
        # Make prediction using the loaded model
        quality_prediction = quality_model.predict(input_quality)
        # Map prediction back to categorical representation
        predicted_quality = 'high' if quality_prediction[0] == 1 else 'low'
        
        # Fetch recommendations based on input features
        soil_recommendation = db.qualityRecommendations.find_one({'factor': 'soil_type', 'value': soil_type})
        watering_recommendation = db.qualityRecommendations.find_one({'factor': 'watering_sched', 'value': watering_sched})
        sun_recommendation = db.qualityRecommendations.find_one({'factor': 'sun_exposure', 'value': sun_exposure})

        # Store input features and prediction in MongoDB (quality collection)
        quality_input = {
            'size': size,
            'firmness': firmness,
            'shape': shape,
            'skin_color': skin_color,
            'blemishes': blemishes,
            'soil_type': soil_type,
            'sun_exposure': sun_exposure,
            'location': location,
            'fertilized': fertilized,
            'watering_sched': watering_sched,
            'pruning': pruning,
            'pest_presence': pest_presence,
            'predicted_quality': predicted_quality,
            'created_at': datetime.utcnow(),
        }
        quality_id = db.quality.insert_one(quality_input).inserted_id
        quality_data = db.quality.find_one({'_id': quality_id})
        quality_data['_id'] = str(quality_data['_id'])

        token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token['user_id']
        user = db.users.find_one({"_id": ObjectId(user_id)})

        user['_id'] = str(user['_id'])

        combined_data = {
            'user': user,
            # 'quality_id': quality_id, 
            'quality_data': quality_data, 
            'soil_recommendation': soil_recommendation['recommendation'] if soil_recommendation else '',
            'soil_image': soil_recommendation['image'] if soil_recommendation and 'image' in soil_recommendation else '',
            'watering_recommendation': watering_recommendation['recommendation'] if watering_recommendation else '',
            'watering_image': watering_recommendation['image'] if watering_recommendation and 'image' in watering_recommendation else '',
            'sun_recommendation': sun_recommendation['recommendation'] if sun_recommendation else '',
            'sun_image': sun_recommendation['image'] if sun_recommendation and 'image' in sun_recommendation else '',
            'created_at': datetime.utcnow(),
        }


        # return jsonify({'quality_id': str(quality_id), 'predicted_quality': predicted_quality}), 200
        db.quality.find_one({'_id': quality_id}, {'_id': 0})
        combined_id = db.combinedQualityResult.insert_one(combined_data).inserted_id

        # Retrieve the inserted data from the database
        newCombined = db.combinedQualityResult.find_one({'_id': combined_id})

        # Check if document was found
        if newCombined is not None:
            # Convert ObjectId to string
            newCombined['_id'] = str(newCombined['_id'])
            if 'quality_id' in newCombined:
                newCombined['quality_id'] = str(newCombined['quality_id'])
        else:
            return jsonify({'error': 'Document not found'}), 404

        return jsonify({'quality_data': newCombined}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

@qualityRoutes.route('/predict/quality/<id>', methods=['GET'])
def get_latest_predicted_quality(id):
    from app import db
    try:
        # Retrieve the document with the given ID from the combinedQualityResult collection
        quality_data = db.combinedQualityResult.find_one({'_id': ObjectId(id)})
        if quality_data:
            quality_data['_id'] = str(quality_data['_id'])
            # if 'quality_id' in reco_data:
            #     reco_data['quality_id'] = str(reco_data['quality_id'])
            return jsonify({'quality_data': quality_data}), 200
        else:
            return jsonify({'error': 'No recommendation data found with the given ID'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qualityRoutes.route('/admin/quality/<id>', methods=['GET'])
def get_QualityById(id):
    from app import db
    try:
        # Retrieve the document with the given ID from the quality collection
        quality_data = db.quality.find_one({'_id': ObjectId(id)})
        if quality_data:
            quality_data['_id'] = str(quality_data['_id'])
            return jsonify({'quality_data': quality_data}), 200
        else:
            return jsonify({'error': 'No quality data found with the given ID'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@qualityRoutes.route('/admin/quality/all', methods=['GET'])
def get_AllQuality():
    from app import db
    try:
        # Retrieve all documents from the quality collection
        # quality_data = list(db.quality.find({}, {'_id': 0}))
        quality_data = list(db.quality.find())
        for quality in quality_data:
            quality['_id'] = str(quality['_id'])

        return jsonify({'quality_data': quality_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@qualityRoutes.route('/admin/quality/<quality_id>', methods=['DELETE'])
def deleteQuality(quality_id):
    from app import db
    try:
        # Convert string to ObjectId
        quality_id = ObjectId(quality_id)
        # Delete document from quality collection
        result = db.quality.delete_one({'_id': quality_id})
        db.combinedQualityResult.delete_one({'quality_id': quality_id})
        # Check if a document was deleted
        if result.deleted_count > 0:
            return jsonify({'message': 'Document deleted successfully'}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        print(str(e))  # Print error message to console
        return jsonify({'error': str(e)}), 500
    
@qualityRoutes.route('/admin/quality-predicts-per-month', methods=['GET'])
def getQualityPredictsPerMonth():
    from app import db
    try:
        # Aggregate quality predicts per month
        predicts_per_month = list(db.quality.aggregate([
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'}
                    },
                    'low': {
                        '$sum': {
                            '$cond': [{'$eq': ['$predicted_quality', 'low']}, 1, 0]
                        }
                    },
                    'high': {
                        '$sum': {
                            '$cond': [{'$eq': ['$predicted_quality', 'high']}, 1, 0]
                        }
                    },
                    'lastCreatedAt': { '$max': '$created_at' } 
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]))
        return jsonify({'predicts_per_month': predicts_per_month}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

