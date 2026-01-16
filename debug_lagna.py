from astrology_utils import calculate_chart
from astrology_utils import calculate_chart
from analysis_utils import get_yogas, get_house_analysis, get_mahadasha_prediction, get_nakshatra_analysis, check_manglik, get_karmic_analysis
import json

if __name__ == "__main__":
    name = "Harshal"
    dob = "1990-12-08"
    tob = "22:35"
    lat = 25.77 
    lon = 85.87
    tz = 5.5
    
    print(f"Calculating for: {name}, {dob} {tob}, {lat}, {lon}")
    data = calculate_chart(name, dob, tob, lat, lon, tz)
    
    print("Ascendant:", data['details']['Ascendant'])
    
    print("\n--- ANALYSIS REPORT ---")
    yogas = get_yogas(data)
    print("Yogas:")
    for y in yogas:
        print(f"- {y['name']}: {y['desc']}")
        
    vim = data.get('vimshottari', [])
    if vim:
        print(f"\nMimshottari Dasha (Total {len(vim)} Rows):")
        for d in vim:
            print(f"MD: {d['Lord']} | {d['Start']} to {d['End']} | {d['Duration']}")
    print("\nDasha Prediction:")
    dp = get_mahadasha_prediction(data['vimshottari'])
    print(f"Running: {dp['current_lord']} ({dp['period']})")
    print(dp['prediction'])
    
    print("\nNakshatra Analysis:")
    na = get_nakshatra_analysis(data)
    print(f"{na.get('nakshatra')}: {na.get('traits')}")
    
    print("\nManglik Status:")
    md = check_manglik(data)
    print(f"Status: {md['status']}")
    print(md['desc'])
    
    print("\nKarmic Analysis:")
    ka = get_karmic_analysis(data)
    print("RAHU (Purpose):")
    print(ka['rahu']['house_text'])
    print(ka['rahu']['nakshatra_text'])
    print("KETU (Past):")
    print(ka['ketu']['house_text'])
    print(ka['ketu']['nakshatra_text'])
    
    print("\nHouse Analysis (Sample):")
    ha = get_house_analysis(data)
    for h in ha[:3]: # First 3
        print(f"{h['planet']} in H{h['house']}: {h['text']}")
