from flask import Blueprint, jsonify, request
from model import load_disease_model
from bson import ObjectId
from datetime import datetime
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, auc
from middleware.auth import isAuthenticatedUser, authorizeRoles
import jwt

diseaseRoutes = Blueprint('diseaseRoutes', __name__)

JWT_SECRET = 'hOBIEr9b5guVvBE5IGBeVqwrBAW7NuUS'

def configure_jwt_secret(secret):
    global JWT_SECRET
    JWT_SECRET = secret

@diseaseRoutes.route('/admin/disease/dataset', methods=['GET'])
def getDataset():
    df = pd.read_csv('./model/kalamansi-disease-dataset.csv')
    shape = df.shape
    data = df.to_json(orient='records')  # Convert the DataFrame to a JSON string

    return jsonify({'shape': shape, 'data': data})

@diseaseRoutes.route('/disease/classification-report', methods=['GET'])
def get_classification_report():
    y_test = [0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]
    y_pred = [0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0]

    report = classification_report(y_test, y_pred, output_dict=True)
    accuracy = accuracy_score(y_test, y_pred)
    return jsonify({
        'report': report,
        'accuracy': accuracy
    })

@diseaseRoutes.route('/disease/confusion-matrix', methods=['GET'])
def predict():
    y_test = [0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]
    predict = [0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0]
    
    cm = confusion_matrix(y_test, predict)
    conf_matrix = pd.DataFrame(data=cm, columns=['Predicted:0', 'Predicted:1'], index=['Actual:0', 'Actual:1'])
    conf_matrix_dict = conf_matrix.to_dict('list') # Convert to a dictionary of lists
    print("Confusion Matrix:", conf_matrix) 
    

    return jsonify(conf_matrix_dict)

@diseaseRoutes.route('/disease/roc-curve', methods=['GET'])
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
discoloration_mapping = {'Absent': 0, 'Present': 1}
lesions_mapping = {'Absent': 0, 'Present': 1}
fertilized_mapping = {'No': 0, 'Yes': 1}
watering_mapping = {'Irregular': 0, 'Regular': 1}
pest_mapping = {'Absent': 0, 'Present': 1}
leaf_mapping = {'Absent': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
wilt_mapping = {'Absent': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
pruning_mapping = {'Never': 0, 'Occasional': 1, 'Regular': 2, 'Frequent': 3}
pesticide_mapping = {'Nothing': 0, 'Fungicide': 1, 'Insecticide': 2}


@diseaseRoutes.route('/predict/disease', methods=['POST'])
def predict_disease():
    from app import db
    disease_model = load_disease_model()
    try:
        # Get input features from JSON data
        data = request.get_json()
        leaf_spots = data['leaf_spots']
        wilting = data['wilting']
        discoloration = data['discoloration']
        lesions = data['lesions']
        fertilized = data['fertilized']
        watering_sched = data['watering_sched']
        pruning = data['pruning']
        pesticide_use = data['pesticide_use']
        pest_presence = data['pest_presence']
        
        # Map categorical inputs to numerical representations
        leaf_val = leaf_mapping[leaf_spots]
        wilt_val = wilt_mapping[wilting]
        discolor_val = discoloration_mapping[discoloration]
        lesion_val = lesions_mapping[lesions]
        fertilized_val = fertilized_mapping[fertilized]
        water_val = watering_mapping[watering_sched]
        pruning_val = pruning_mapping[pruning]
        pesticide_val = pesticide_mapping[pesticide_use]
        pest_presence_val = pest_mapping[pest_presence]
        
        # Create input data for prediction
        input_disease = pd.DataFrame({
            'discolor': [discolor_val],
            'lesion': [lesion_val],
            'fertilizer': [fertilized_val],
            'water_sched': [water_val],
            'pest': [pest_presence_val],
            'leaf_spot': [leaf_val],
            'leaf_wilting': [wilt_val],
            'tree_pruning': [pruning_val],
            'pesticide': [pesticide_val],
            
        })
        
        # Make prediction using the loaded model
        disease_prediction = disease_model.predict(input_disease)
        # Map prediction back to categorical representation
        predicted_disease = 'infected' if disease_prediction[0] == 1 else 'not infected'

        # Fetch recommendations based on input features
        fertilizerReco = db.diseaseRecommendations.find_one({'factor': 'fertilized', 'value': fertilized})
        wateringReco = db.diseaseRecommendations.find_one({'factor': 'watering_sched', 'value': watering_sched})
        discolorReco = db.diseaseRecommendations.find_one({'factor': 'discoloration', 'value': discoloration})
        lesionReco = db.diseaseRecommendations.find_one({'factor': 'lesions', 'value': lesions})
        leafReco = db.diseaseRecommendations.find_one({'factor': 'leaf_spots', 'value': leaf_spots})
        wiltingReco = db.diseaseRecommendations.find_one({'factor': 'wilting', 'value': wilting})
        pruningReco = db.diseaseRecommendations.find_one({'factor': 'pruning', 'value': pruning})
        pestReco = db.diseaseRecommendations.find_one({'factor': 'pest_presence', 'value': pest_presence})
        pesticideReco = db.diseaseRecommendations.find_one({'factor': 'pesticide_use', 'value': pesticide_use})

        # Store input features and prediction in MongoDB (disease collection)
        disease_input = {
            'leaf_spots': leaf_spots,
            'wilting': wilting,
            'discoloration': discoloration,
            'lesions': lesions,
            'fertilized': fertilized,
            'watering_sched': watering_sched,
            'pruning': pruning,
            'pesticide_use': pesticide_use,
            'pest_presence': pest_presence,
            'predicted_disease': predicted_disease,
            'created_at': datetime.utcnow(),
        }
        disease_id = db.disease.insert_one(disease_input).inserted_id
        disease_data = db.disease.find_one({'_id': disease_id})
        disease_data['_id'] = str(disease_data['_id'])
        
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded_token['user_id']
        user = db.users.find_one({"_id": ObjectId(user_id)})

        user['_id'] = str(user['_id'])

        
        combined_data = {
            'user': user,
            # 'disease_id': disease_id,
            'disease_data': disease_data,
            'fertilizerReco': fertilizerReco['recommendation'] if fertilizerReco else '',
            'fertilizer_image': fertilizerReco['image'] if fertilizerReco and 'image' in fertilizerReco else '',
            'wateringReco': wateringReco['recommendation'] if wateringReco else '',
            'watering_image': wateringReco['image'] if wateringReco and 'image' in wateringReco else '',
            'discolorReco': discolorReco['recommendation'] if discolorReco else '',
            'discolor_image': discolorReco['image'] if discolorReco and 'image' in discolorReco else '',
            'lesionReco': lesionReco['recommendation'] if lesionReco else '',
            'lesion_image': lesionReco['image'] if lesionReco and 'image' in lesionReco else '',
            'leafReco': leafReco['recommendation'] if leafReco else '',
            'leaf_image': leafReco['image'] if leafReco and 'image' in leafReco else '',
            'wiltingReco': wiltingReco['recommendation'] if wiltingReco else '',
            'wilting_image': wiltingReco['image'] if wiltingReco and 'image' in wiltingReco else '',
            'pruningReco': pruningReco['recommendation'] if pruningReco else '',
            'pruning_image': pruningReco['image'] if pruningReco and 'image' in pruningReco else '',
            'pestReco': pestReco['recommendation'] if pestReco else '',
            'pest_image': pestReco['image'] if pestReco and 'image' in pestReco else '',
            'pesticideReco': pesticideReco['recommendation'] if pesticideReco else '',
            'pesticide_image': pesticideReco['image'] if pesticideReco and 'image' in pesticideReco else '',
            'created_at': datetime.utcnow(),
        }

        # Retrieve the inserted data from the database
        newDisease = db.disease.find_one({'_id': disease_id}, {'_id': 0})

        combined_id = db.combinedDiseaseResult.insert_one(combined_data).inserted_id
        newCombined = db.combinedDiseaseResult.find_one({'_id': combined_id})

        if newCombined is not None:
            newCombined['_id'] = str(newCombined['_id'])
            if 'disease_id' in newCombined:
                newCombined['disease_id'] = str(newCombined['disease_id'])
        else:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({'disease_data': newCombined}), 200
        # return jsonify({'inserted_data': newDisease}), 200
    except Exception as e:
        print(str(e))  # Print error message to console
        return jsonify({'error': str(e)}), 500
    
@diseaseRoutes.route('/predict/disease/<id>', methods=['GET'])
def get_latest_predicted_disease(id):
    from app import db
    try:
        # Retrieve the document with the given ID from the combinedDiseaseResult collection
        disease_data = db.combinedDiseaseResult.find_one({'_id': ObjectId(id)})
        if disease_data:
            disease_data['_id'] = str(disease_data['_id'])
            return jsonify({'disease_data': disease_data}), 200
        else:
            return jsonify({'error': 'No recommendation data found with the given ID'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diseaseRoutes.route('/admin/disease/all', methods=['GET'])
def get_AllDisease():
    from app import db
    try:
        # Retrieve all documents from the disease collection
        disease_data = list(db.disease.find())
        for disease in disease_data:
            disease['_id'] = str(disease['_id'])
        # Return the disease data as JSON response
        return jsonify({'disease_data': disease_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@diseaseRoutes.route('/admin/disease/<id>', methods=['GET'])
def get_DiseaseById(id):
    from app import db
    try:
        # Retrieve the document with the given ID from the disease collection
        disease_data = db.disease.find_one({'_id': ObjectId(id)})
        if disease_data:
            disease_data['_id'] = str(disease_data['_id'])
            return jsonify({'disease_data': disease_data}), 200
        else:
            return jsonify({'error': 'No disease data found with the given ID'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@diseaseRoutes.route('/admin/disease/<disease_id>', methods=['DELETE'])
def delete_disease(disease_id):
    from app import db
    try:
        # Convert the disease_id from string to ObjectId
        disease_id = ObjectId(disease_id)
        
        # Delete the disease document from the disease collection
        result = db.disease.delete_one({'_id': disease_id})
        db.combinedDiseaseResult.delete_one({'disease_id': disease_id})

        if result.deleted_count > 0:
            return jsonify({'message': 'Document deleted successfully'}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@diseaseRoutes.route('/admin/disease-predicts-per-month', methods=['GET'])
def getDiseasePredictsPerMonth():
    from app import db
    try:
        # Aggregate the number of disease predictions per month
        predicts_per_month = list(db.disease.aggregate([
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'}
                    },
                    'infected': {
                        '$sum': {
                            '$cond': [{'$eq': ['$predicted_disease', 'infected']}, 1, 0]
                        }
                    },
                    'notInfected': {
                        '$sum': {
                            '$cond': [{'$eq': ['$predicted_disease', 'not infected']}, 1, 0]
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