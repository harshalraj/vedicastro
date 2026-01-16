from flask import Flask, render_template, request, jsonify
from astrology_utils import calculate_chart
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
