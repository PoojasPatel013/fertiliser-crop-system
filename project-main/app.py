from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load model and preprocessing objects
with open('fertilizer_prediction_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('preprocessing_objects.pkl', 'rb') as preprocessing_file:
    preprocessing_objects = pickle.load(preprocessing_file)

# Extract preprocessing objects
label_encoders = preprocessing_objects['label_encoders']
scaler = preprocessing_objects['scaler']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input data from request
        data = request.json
        
        # Print preprocessing objects for debugging
        print("Label Encoders:", preprocessing_objects['label_encoders'].keys())
        
        # Extract input values
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        moisture = float(data['moisture'])
        soil_type = data['soil_type']
        crop_type = data['crop_type']
        
        # Dynamically find the correct encoder keys
        soil_type_encoder_key = [k for k in preprocessing_objects['label_encoders'].keys() if 'soil' in k.lower()][0]
        crop_type_encoder_key = [k for k in preprocessing_objects['label_encoders'].keys() if 'crop' in k.lower()][0]
        fertilizer_encoder_key = [k for k in preprocessing_objects['label_encoders'].keys() if 'fertilizer' in k.lower()][0]
        
        # Encode categorical variables
        soil_type_encoded = preprocessing_objects['label_encoders'][soil_type_encoder_key].transform([soil_type])[0]
        crop_type_encoded = preprocessing_objects['label_encoders'][crop_type_encoder_key].transform([crop_type])[0]
        
        # Add default values for missing features (Nitrogen, Potassium, Phosphorous)
        # You might want to adjust these based on your domain knowledge
        nitrogen = 20  # Default value
        potassium = 20  # Default value
        phosphorous = 20  # Default value
        
        # Prepare input features
        input_features = np.array([
            temperature, humidity, moisture, 
            soil_type_encoded, crop_type_encoded,
            nitrogen, potassium, phosphorous
        ]).reshape(1, -1)
        
        # Scale features
        input_features_scaled = preprocessing_objects['scaler'].transform(input_features)
        
        # Predict probabilities
        probabilities = model.predict_proba(input_features_scaled)[0]
        
        # Get fertilizer names
        fertilizer_names = preprocessing_objects['label_encoders'][fertilizer_encoder_key].classes_
        
        # Create predictions list
        predictions = sorted(
            [
                {
                    'fertilizer': name, 
                    'probability': round(prob * 100, 2)
                } 
                for name, prob in zip(fertilizer_names, probabilities)
            ], 
            key=lambda x: x['probability'], 
            reverse=True
        )
        
        return jsonify({
            'primary_fertilizer': predictions[0]['fertilizer'],
            'confidence': predictions[0]['probability'],
            'top_predictions': predictions[:3]
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # This will print the full error traceback
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)