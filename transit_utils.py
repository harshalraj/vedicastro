import ephem
import datetime

# Zodiac Signs Mapping (0 = Aries, ..., 11 = Pisces)
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_current_transits():
    """
    Calculates current planetary positions (Gochar) for today.
    Returns a dictionary: {'Planet': 'SignName'}
    """
    transit_positions = {}
    today = datetime.datetime.now()
    
    # Planets to track for key transits
    # Focusing on major slow-moving planets + Nodes
    planets = {
        'Saturn': ephem.Saturn(),
        'Jupiter': ephem.Jupiter(),
        'Rahu': ephem.Moon(), # Placeholder, Ephem doesn't have Rahu directly usually?
        # Actually Ephem has strict planets. Nodes are often calculated relative to Moon/Sun.
        # But commonly we approximate or use a library that supports it. 
        # Alternatively, we can calculate node position manually if ephem doesn't support it directly in base.
        # Let's check available bodies. 
        # For MVP Transit: Saturn and Jupiter are most critical. 
        # Adding Mars, Sun, Venus, Mercury for thoroughness.
        'Mars': ephem.Mars(),
        'Sun': ephem.Sun(),
        'Venus': ephem.Venus(),
        'Mercury': ephem.Mercury(),
        'Moon': ephem.Moon()
    }

    # Observer setup
    obs = ephem.Observer()
    obs.date = today
    
    for name, body in planets.items():
        body.compute(obs)
        
        if name == 'Rahu':
             # Ephem doesn't support Rahu directly easily without extensions in some versions.
             # We might skip Rahu/Ketu for Gochar in this simple version or use a simplified approximation if needed.
             # To be safe and avoid "AttributeError", let's strictly stick to standard planets first.
             continue

        # Calculate Sidereal Longitude (Nirayana)
        # 1. Get Geocentric Ecliptic Longitude (Tropical) using ephem.Ecliptic
        ecl = ephem.Ecliptic(body)
        tropical_lon_rad = ecl.lon # this is in radians
        
        tropical_lon_deg = float(tropical_lon_rad) * 180.0 / 3.14159265359 # Rad to Deg
        
        # 2. Subtract Ayanamsa (~24.1 deg for Lahiri)
        ayanamsa = 24.1 
        sidereal_lon = (tropical_lon_deg - ayanamsa) % 360
        
        sign_index = int(sidereal_lon // 30)
        sign_name = SIGNS[sign_index]
        transit_positions[name] = sign_name
        
    return transit_positions

def analyze_transits(birth_moon_sign, transit_positions, relevant_planets=None):
    """
    Analyzes the impact of transits relative to the Birth Moon (Rashi).
    Can focus on specific 'relevant_planets' (e.g. House Lord of the topic).
    """
    if not birth_moon_sign or birth_moon_sign not in SIGNS:
        return "Values for Moon Sign are missing, so Transit analysis is skipped."
        
    moon_idx = SIGNS.index(birth_moon_sign)
    
    analysis = []
    
    # 1. SATURN TRANSIT (Global Importance)
    if 'Saturn' in transit_positions:
        sat_sign = transit_positions['Saturn']
        sat_idx = SIGNS.index(sat_sign)
        pos_from_moon = (sat_idx - moon_idx) % 12 + 1
        
        msg = ""
        if pos_from_moon == 12:
            msg = f"**Sade Sati (Rising):** Saturn in 12th from Moon ({sat_sign}). Expenses/restlessness."
        elif pos_from_moon == 1:
            msg = f"**Sade Sati (Peak):** Saturn on Moon ({sat_sign}). Intense pressure/work."
        elif pos_from_moon == 2:
            msg = f"**Sade Sati (Setting):** Saturn in 2nd from Moon ({sat_sign}). Financial/speech caution."
        elif pos_from_moon == 4:
            msg = f"**Dhaiya:** Saturn in 4th. Domestic/career changes."
        elif pos_from_moon == 8:
            msg = f"**Ashtama Shani:** Saturn in 8th. Sudden obstacles."
        
        if msg:
            analysis.append(msg)

    # 2. JUPITER TRANSIT (Global Importance)
    if 'Jupiter' in transit_positions:
        jup_sign = transit_positions['Jupiter']
        jup_idx = SIGNS.index(jup_sign)
        pos_from_moon = (jup_idx - moon_idx) % 12 + 1
        
        if pos_from_moon in [2, 5, 7, 9, 11]:
            analysis.append(f"**Jupiter Blessing:** Transiting {pos_from_moon}th house ({jup_sign}). Good for growth.")

    # 3. CONTEXT SPECIFIC PLANETS
    if relevant_planets:
        analysis.append("\n**Key Planet Transits for this Topic:**")
        dedup_planets = set(relevant_planets)
        
        for planet in dedup_planets:
            if planet in transit_positions:
                curr_sign = transit_positions[planet]
                p_idx = SIGNS.index(curr_sign)
                h_from_moon = (p_idx - moon_idx) % 12 + 1
                
                # Simple interpretation
                status = "Neutral"
                if h_from_moon in [3, 6, 11]:
                    status = "Favorable (Upachaya)"
                elif h_from_moon in [8, 12]:
                    status = "Challenging"
                elif h_from_moon in [1, 5, 9]:
                    status = "Supportive (Trikona)"
                elif h_from_moon in [4, 7, 10]:
                    status = "Active (Kendra)"

                analysis.append(f"- **{planet}:** Currently in {curr_sign} ({h_from_moon}th from Moon). Status: *{status}*.")
    
    if not analysis:
        return "No major transit effects noted."

    return "\n".join(analysis)
