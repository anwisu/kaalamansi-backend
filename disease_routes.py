from flask import Blueprint, jsonify, request
from model import load_disease_model
import pandas as pd

disease_routes = Blueprint('disease_routes', __name__)


# DISEASE PREDICTION ROUTES
# Define mapping dictionaries
leaf_mapping = {'Absent': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
wilt_mapping = {'Absent': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
pruning_mapping = {'Never': 0, 'Occasional': 1, 'Regular': 2, 'Frequent': 3}
pesticide_mapping = {'Nothing': 0, 'Fungicide': 1, 'Insecticide': 2}
discoloration_mapping = {'Absent': 0, 'Present': 1}
lesions_mapping = {'Absent': 0, 'Present': 1}
fertilized_mapping = {'No': 0, 'Yes': 1}
watering_mapping = {'Irregular': 0, 'Regular': 1}
pest_mapping = {'Absent': 0, 'Present': 1}

@disease_routes.route('/predict/disease', methods=['POST'])
def predict_disease():
    from app import db
    disease_model = load_disease_model()
    try:
        # Get input features from JSON data
        d_data = request.get_json()
        leaf_spots = d_data['leaf_spots']
        wilting = d_data['wilting']
        discoloration = d_data['discoloration']
        lesions = d_data['lesions']
        fertilized = d_data['fertilized']
        watering_sched = d_data['watering_sched']
        pruning = d_data['pruning']
        pesticide_use = d_data['pesticide_use']
        pest_presence = d_data['pest_presence']
        
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
            'leaf_spot': [leaf_val],
            'leaf_wilting': [wilt_val],
            'discolor': [discolor_val],
            'leasion': [lesion_val],
            'fertilizer': [fertilized_val],
            'water_sched': [water_val],
            'tree_pruning': [pruning_val],
            'pesticide': [pesticide_val],
            'pest': [pest_presence_val],
        })
        
        # Make prediction using the loaded model
        disease_prediction = disease_model.predict(input_disease)
        # Map prediction back to categorical representation
        predicted_disease = 'infected' if disease_prediction[0] == 1 else 'not infected'

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
            'predicted_disease': predicted_disease
        }
        disease_id = db.disease.insert_one(disease_input).inserted_id

        # Retrieve the inserted data from the database
        newDisease = db.disease.find_one({'_id': disease_id}, {'_id': 0})

        return jsonify({'inserted_data': newDisease}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500