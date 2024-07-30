from flask import Flask, request, jsonify
import pandas as pd
import os
from dotenv import load_dotenv
from flask_cors import CORS
from shapely.geometry import Polygon


load_dotenv()
app = Flask(__name__)
CORS(app)



app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')
# Dummy data for crop requirements
crop_data = {
    "Crops": ["TestA", "Testb", "Testc"],
    "Potassium": [100, 120, 80],
    "Nitrogen": [50, 70, 40],
    "Phosphorus": [30, 40, 20],
    "Magnesium": [100, 5, 30]
}
crop_data_Potassium = pd.read_csv("data/Crops_Requirement_Potassium.csv")
crop_data_Nitrogen = pd.read_csv("data/Crops_Requirement_Nitrogen.csv")
crop_data_Phosphorus = pd.read_csv("data/Crops_Requirement_Phosphorus.csv")
crop_data_Magnesium = pd.read_csv("data/Crops_Requirement_Magnesium.csv")

# crop_df = pd.DataFrame(crop_df)

# Route to check if the service is working
@app.route('/', methods=['GET'])
def hello_world():
    return "API Is Running: Add the Route"


@app.route('/status', methods=['GET'])
def check_status():
    return jsonify({"status": "Service is up and running"})

# Route to get all crops name
@app.route('/crops', methods=['GET'])
def get_available_crops():
    crops_list = crop_data_Nitrogen['Crops'].tolist()
    return jsonify({"Crops": crops_list})


# Route to get crop requirements
@app.route('/crop-requirements', methods=['POST'])
def get_crop_requirements():
    data = request.get_json()
    crop_name = data.get('crop')
    soil_type = data.get('soil', 1)


    if crop_name:
        potassium_requirement = crop_data_Potassium[crop_data_Potassium['Crops'] == crop_name]
        nitrogen_requirement = crop_data_Nitrogen[crop_data_Nitrogen['Crops'] == crop_name]
        phosphorus_requirement = crop_data_Phosphorus[crop_data_Phosphorus['Crops'] == crop_name]
        magnesium_requirement = crop_data_Magnesium[crop_data_Magnesium['Crops'] == crop_name]

        if not potassium_requirement.empty:

            potassium_requirement_value = potassium_requirement[str(soil_type)].values[0]
            nitrogen_requirement_value = nitrogen_requirement[str(soil_type)].values[0]
            phosphorus_requirement_value = phosphorus_requirement[str(soil_type)].values[0]
            magnesium_requirement_value = magnesium_requirement[str(soil_type)].values[0]

            return jsonify({
                "crop": crop_name,
                "soil_type": soil_type,
                "potassium_requirement": int(potassium_requirement_value),
                "nitrogen_requirement": int(nitrogen_requirement_value),
                "phosphorus_requirement": int(phosphorus_requirement_value),
                "magnesium_requirement": int(magnesium_requirement_value)
            })
        else:
            return jsonify({"error": "Crop not found"}), 404
    else:
        return jsonify({"error": "Crop name not provided"}), 400



# Route to select crop based on requirements
@app.route('/select-crops', methods=['POST'])
def get_select_crop():
    data = request.get_json()
    soil_type = data.get('soil', 1)
    potassium_value = data.get('potassium_requirement', 50)
    nitrogen_value  = data.get('nitrogen_requirement', 50)
    phosphorus_value  = data.get('phosphorus_requirement', 50)
    magnesium_value  = data.get('magnesium_requirement', 50)

    # Filter crops based on nutritional requirements
    selected_crops = []
    for crop_name in crop_data_Nitrogen['Crops']:
        potassium_requirement = crop_data_Potassium[crop_data_Potassium['Crops'] == crop_name][str(soil_type)].values[0]
        nitrogen_requirement = crop_data_Nitrogen[crop_data_Nitrogen['Crops'] == crop_name][str(soil_type)].values[0]
        phosphorus_requirement = crop_data_Phosphorus[crop_data_Phosphorus['Crops'] == crop_name][str(soil_type)].values[0]
        magnesium_requirement = crop_data_Magnesium[crop_data_Magnesium['Crops'] == crop_name][str(soil_type)].values[0]


        # Check if all nutrient requirements are met or exceeded
        if (potassium_value >= potassium_requirement and
            nitrogen_value >= nitrogen_requirement and
            phosphorus_value >= phosphorus_requirement and
            magnesium_value >= magnesium_requirement):

            # Add crop to the selected list with its nutritional requirements
            selected_crops.append({
                "crop": crop_name,
                "potassium_requirement": int(potassium_requirement),
                "nitrogen_requirement": int(nitrogen_requirement),
                "phosphorus_requirement": int(phosphorus_requirement),
                "magnesium_requirement": int(magnesium_requirement)
            })

    if selected_crops:
        return jsonify({"selected_crops": selected_crops})
    else:
        return jsonify({"message": "No crops meet the specified requirements."}), 404

@app.route('/aggregator', methods=['POST'])
def aggregator():
    data = request.get_json()
    users_recommendations = data.get('meal_plans', [])

    aggregated_list = []

    for user in users_recommendations:
        crop_name = user.get('crop')
        found = False
        for aggregated_crop in aggregated_list:
            if crop_name == aggregated_crop['crop']:
                aggregated_crop['count'] = int(aggregated_crop['count']) + 1
                found = True
                break

        if not found:
            aggregated_list.append({
                "crop": crop_name,
                "count": 1,
            })

    if aggregated_list:
        return jsonify({"recommendation": aggregated_list})
    else:
        return jsonify({"message": "No users meal plans found."}), 404


@app.route('/comparison-output', methods=['POST'])
def comparison_output():
    data = request.get_json()
    growable_crops = data.get('growable', [])
    recommendations = data.get('recommendation', [])

    common_crops = []

    for recommendation in recommendations:
        crop_name = recommendation.get('crop')
        count = int(recommendation.get('count'))
        for growable_crop in growable_crops:
            if growable_crop['crop'] == crop_name:
                common_crops.append({
                    "crop": crop_name,
                    "count": count,
                    "potassium_requirement": int(growable_crop['potassium_requirement']),
                    "nitrogen_requirement": int(growable_crop['nitrogen_requirement']),
                    "phosphorus_requirement": int(growable_crop['phosphorus_requirement']),
                    "magnesium_requirement": int(growable_crop['magnesium_requirement'])
                })

    # Sort common crops by count
    common_crops.sort(key=lambda x: int(x['count']), reverse=True)

    if common_crops:
        return jsonify({"common_crops": common_crops})
    else:
        return jsonify({"message": "No crops match the recommendation."}), 404











@app.route('/test-getnutrients-single', methods=['POST'])
def testgetnutrients():
    try:
        data = request.get_json()
        latitude_value = data.get('latitude')
        longitude_value  = data.get('longitude')
        
        if latitude_value is None or longitude_value is None:
            return jsonify({"error": "Latitude and longitude are required."}), 400

        latitude_value = float(latitude_value)
        longitude_value  = float(longitude_value)


        nutrients = {
                "latitude": latitude_value,
                "longitude": longitude_value,
                "potassium_requirement": 100,  # Dummy value
                "nitrogen_requirement": 50,   
                "phosphorus_requirement": 30, 
                "magnesium_requirement": 20   
            }

        return jsonify(nutrients)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input, please provide valid latitude and longitude."}), 400




@app.route('/test-getnutrients-multiple', methods=['POST'])
def test_get_nutrients_multiple():
    try:
        data = request.get_json()
        coordinates = data.get('coordinates')
        
        if not coordinates or len(coordinates) < 3:
            return jsonify({"error": "At least 3 points are required."}), 400

        # Converting coordinates to Shapely Polygon
        polygon = Polygon(coordinates)
        
        # Polygon Validity
        if not polygon.is_valid:
            return jsonify({"error": "Invalid polygon."}), 400

        area = polygon.area

        nutrients = {
            "area": area,
            "potassium_requirement": 100,  # Dummy value
            "nitrogen_requirement": 50,   
            "phosphorus_requirement": 30, 
            "magnesium_requirement": 20   
        }

        return jsonify(nutrients)
    except Exception as e:
        return jsonify({"error": str(e)}), 400





if __name__ == '__main__':
    app.run(debug=True)
