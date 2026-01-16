from flask import Flask, render_template, request, jsonify
from astrology_utils import calculate_chart
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from astrology_utils import calculate_chart
from analysis_utils import get_yogas, get_house_analysis, get_mahadasha_prediction, get_nakshatra_analysis, check_manglik, get_karmic_analysis
from chat_logic import process_question
import datetime

app = Flask(__name__)

# Initialize Geolocator
geolocator = Nominatim(user_agent="vedic_astro_app")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/suggest_place', methods=['GET'])
def suggest_place():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        # Get more results and allow shorter queries
        locations = geolocator.geocode(query, exactly_one=False, limit=20, language='en')
        suggestions = []
        if locations:
            for loc in locations:
                suggestions.append({
                    'display_name': loc.address,
                    'lat': loc.latitude,
                    'lon': loc.longitude
                    # Timezone lookup would ideally happen here or on selection.
                    # For simplicity, we might ask the frontend to deal with timezone or use a library here.
                    # Let's use a standard timezone approximation or ask user, but usually automation is better.
                    # For now, we return lat/lon and we might need `timezonefinder` package for accurate TZ.
                    # Since I didn't install `timezonefinder` yet, I'll rely on a basic offset or frontend logic if possible,
                    # OR I will add timezonefinder to dependencies.
                    # Let's stick to lat/lon for now and default to IST (5.5) or ask user if critical.
                    # Actually, better to just default to 5.5 for now as the user implies Indian context ("Lagna", "Rashi"), 
                    # but I should probably allow manual offset entry or fetch it.
                    # I'll add a 'timezone' field to the frontend to allow manual edit, defaulting to 5.5.
                })
        return jsonify(suggestions)
    except Exception as e:
        print(f"Error in suggest_place: {e}")
        return jsonify([])

@app.route('/get_chart', methods=['POST'])
def get_chart():
    data = request.json
    name = data.get('name')
    dob = data.get('dob')
    tob = data.get('tob')
    lat = float(data.get('lat'))
    lon = float(data.get('lon'))
    tz = float(data.get('tz', 5.5)) # Default to IST
    
    try:
        chart_data = calculate_chart(name, dob, tob, lat, lon, tz)
        return jsonify(chart_data)
    except Exception as e:
        print(f"Error in get_chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_kundali():
    data = request.json
    try:
        name = data.get('name')
        dob = data.get('dob')
        tob = data.get('tob')
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        tz = float(data.get('tz', 5.5))
        
        # Calculate Chart
        chart_data = calculate_chart(name, dob, tob, lat, lon, tz)
        
        # Perform Analysis
        yogas = get_yogas(chart_data)
        house_analysis = get_house_analysis(chart_data)
        dasha_pred = get_mahadasha_prediction(chart_data.get('vimshottari', []))
        nak_analysis = get_nakshatra_analysis(chart_data)
        manglik_dosha = check_manglik(chart_data)
        karmic_analysis = get_karmic_analysis(chart_data)
        
        response = {
            "yogas": yogas,
            "house_analysis": house_analysis,
            "dasha_prediction": dasha_pred,
            "nakshatra_analysis": nak_analysis,
            "manglik": manglik_dosha,
            "karmic_analysis": karmic_analysis
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error in analyze_kundali: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '')
        payload = data.get('chart_params') # Full payload to recalc chart on fly or pass chart_data
        
        if not question or not payload:
            return jsonify({"error": "Missing inputs"}), 400
            
        # Recalculate chart (stateless)
        chart_data = calculate_chart(
            payload['name'], payload['dob'], payload['tob'], 
            float(payload['lat']), float(payload['lon']), float(payload['tz'])
        )
        
        result = process_question(question, chart_data)
        return jsonify(result)
        
    except Exception as e:
        print(f"Chat Analysis Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
