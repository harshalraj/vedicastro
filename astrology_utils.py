import ephem
import math
import datetime

def get_ayanamsa(jd):
    # Lahiri Ayanamsa Calculation (Approximate)
    # T = (jd - 2451545.0) / 36525.0
    # Ayanamsa = 23.8585 + 1.3963 * T
    t = (jd - 2451545.0) / 36525.0
    ayanamsa = 23.8585 + 1.3963 * t
    ayanamsa = 23.8585 + 1.3963 * t
    return ayanamsa

def get_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(round(((deg - d) * 60 - m) * 60))
    return f"{d}°{m}'{s}\""

def get_sign_from_lon(lon):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    idx = int(lon / 30) % 12
    return signs[idx]

def get_mean_node(jd):
    # Mean Longitude of the Moon's Ascending Node (Rahu)
    # Formula: Omega = 125.04452 - 1934.136261 * T
    # Where T is Julian centuries from J2000.0
    # Source: Approximate formula.
    # Note: Motion is retrograde (decreasing).
    
    t = (jd - 2451545.0) / 36525.0
    omega = 125.04452 - 1934.136261 * t
    omega = omega % 360
    if omega < 0:
        omega += 360
    return omega

def get_nakshatra(lon):
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", 
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    # Each Nakshatra is 13 deg 20 min = 13.3333 deg
    # 360 / 27 = 13.333333
    one_star = 360.0 / 27.0
    idx = int(lon / one_star)
    percent = (lon % one_star) / one_star
    pada = int(percent * 4) + 1
    return f"{nakshatras[idx]} ({pada})"

def calculate_vimshottari(moon_lon, birth_date):
    # Nakshatra Rulers and Dasha Years
    # Sequence: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
    dasha_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_years = {
        "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, 
        "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
    }
    
    # Nakshatra mapping to Lords (0-26)
    # 0 (Ashwini) -> Ketu
    # 1 (Bharani) -> Venus
    # ...
    # Pattern repeats every 9 nakshatras.
    
    # 360 degrees / 27 nakshatras = 13.3333 degrees per nakshatra
    one_star = 360.0 / 27.0
    moon_nak_idx = int(moon_lon / one_star)
    moon_nak_progress = (moon_lon % one_star) / one_star # 0.0 to 1.0 (passed)
    remaining_percent = 1.0 - moon_nak_progress
    
    # Determine Lord of Birth Nakshatra
    lord_idx = moon_nak_idx % 9
    start_lord = dasha_lords[lord_idx]
    
    # Calculate Balance of Dasha
    total_years = dasha_years[start_lord]
    balance_years = total_years * remaining_percent
    
    # Generate Timeline
    # We will generate Mahadashas for 120 years from birth (or slightly more to cover life)
    dashas = []
    
    current_date = birth_date
    
    # First Dasha (Balance)
    # Add balance_years to current_date
    days_balance = balance_years * 365.25
    end_date = current_date + datetime.timedelta(days=days_balance)
    
    dashas.append({
        "Lord": start_lord,
        "Start": current_date.strftime("%Y-%m-%d"),
        "End": end_date.strftime("%Y-%m-%d"),
        "Duration": f"{balance_years:.1f}y (Bal)"
    })
    
    current_date = end_date
    
    # Subsequent Dashas
    curr_lord_idx = (lord_idx + 1) % 9
    
    # Loop for roughly 120 years total cycle or just one full cycle
    # Let's do a full cycle of 9 planets after the first partial one?
    # Or just enough to cover up to 100 years from birth.
    
    age = 0
    cycle_count = 0
    # Stop if we exceed 120 years from birth
    birth_year = birth_date.year
    
    while cycle_count < 9:
        lord = dasha_lords[curr_lord_idx]
        years = dasha_years[lord]
        
        days_duration = years * 365.25
        end_date = current_date + datetime.timedelta(days=days_duration)
        
        dashas.append({
            "Lord": lord,
            "Start": current_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d"),
            "Duration": f"{years}y"
        })
        
        current_date = end_date
        curr_lord_idx = (curr_lord_idx + 1) % 9
        cycle_count += 1
        
        if end_date.year - birth_year > 120:
            break
            
    return dashas

def calculate_chart(name, date_str, time_str, lat, lon, tz_offset):
    # Setup Ephem Observer
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    
    # Calculate UTC time
    local_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    utc_dt = local_dt - datetime.timedelta(hours=tz_offset)
    obs.date = utc_dt
    
    # Calculate Ayanamsa
    jd = ephem.julian_date(obs.date)
    ayanamsa = get_ayanamsa(jd)
    
    # Bodies
    bodies = {
        'Sun': ephem.Sun(),
        'Moon': ephem.Moon(),
        'Mercury': ephem.Mercury(),
        'Venus': ephem.Venus(),
        'Mars': ephem.Mars(),
        'Jupiter': ephem.Jupiter(),
        'Saturn': ephem.Saturn(),
    }
    
    d1_chart_content = {i: [] for i in range(1, 13)}
    planet_positions = {}
    planetary_details = [] # List for the table
    
    signs_list = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    # Calculate Ascendant
    ramc = obs.sidereal_time()
    eps = 23.4392911 * math.pi / 180.0
    latitude = float(lat) * math.pi / 180.0
    
    y = -math.cos(ramc)
    x = math.sin(ramc) * math.cos(eps) + math.tan(latitude) * math.sin(eps)
    
    asc_rad = math.atan2(y, x)
    asc_deg_trop = (asc_rad * 180.0 / math.pi) + 180 
    asc_deg_trop = asc_deg_trop % 360
    
    asc_sid_deg = (asc_deg_trop - ayanamsa) % 360
    asc_sign = get_sign_from_lon(asc_sid_deg)
    asc_sign_idx = signs_list.index(asc_sign)
    
    asc_nakshatra = get_nakshatra(asc_sid_deg)
    planetary_details.append({
        'Planet': 'Ascendant',
        'Sign': asc_sign,
        'Degree': get_dms(asc_sid_deg % 30),
        'Nakshatra': asc_nakshatra
    })
    
    # Calculate Rahu/Ketu
    rahu_mean_trop = get_mean_node(jd)
    rahu_sid_deg = (rahu_mean_trop - ayanamsa) % 360
    ketu_sid_deg = (rahu_sid_deg + 180) % 360
    
    planet_positions['Rahu'] = rahu_sid_deg
    planet_positions['Ketu'] = ketu_sid_deg
    
    # Calculate Bodies
    for name, body in bodies.items():
        body.compute(obs)
        ecl = ephem.Ecliptic(body)
        trop_lon = ecl.lon * 180.0 / math.pi
        sid_lon = (trop_lon - ayanamsa) % 360
        planet_positions[name] = sid_lon

    # Process all planets (including Rahu/Ketu) for details and chart
    all_bodies = list(bodies.keys()) + ['Rahu', 'Ketu']
    
    for name in all_bodies:
        lon = planet_positions[name]
        sign = get_sign_from_lon(lon)
        s_idx = signs_list.index(sign)
        h_num = (s_idx - asc_sign_idx) % 12 + 1
        d1_chart_content[h_num].append(name)
        
        nak = get_nakshatra(lon)
        planetary_details.append({
            'Planet': name,
            'Sign': sign,
            'Degree': get_dms(lon % 30),
            'Nakshatra': nak
        })
        
    # Moon Chart
    if 'Moon' in planet_positions:
        moon_lon = planet_positions['Moon']
        moon_sign = get_sign_from_lon(moon_lon)
        moon_sign_idx = signs_list.index(moon_sign)
        
        moon_chart_content = {i: [] for i in range(1, 13)}
        asc_rel_moon = (asc_sign_idx - moon_sign_idx) % 12 + 1
        moon_chart_content[asc_rel_moon].append("Lagna")
        
        for name in all_bodies:
            lon = planet_positions[name]
            s_idx = signs_list.index(get_sign_from_lon(lon))
            h_num = (s_idx - moon_sign_idx) % 12 + 1
            moon_chart_content[h_num].append(name)
        
        moon_data = moon_chart_content
        moon_sign_name = moon_sign
        
        # Calculate Vimshottari
        vimshottari = calculate_vimshottari(moon_lon, local_dt) # passing local_dt which acts as birth date
    else:
        moon_data = {}
        moon_sign_name = "Unknown"
        vimshottari = []

    return {
        'd1': d1_chart_content,
        'moon': moon_data,
        'details': {
            'Name': name,
            'Date': date_str,
            'Time': time_str,
            'Ascendant': asc_sign,
            'Moon Sign': moon_sign_name
        },
        'planetary_details': planetary_details,
        'vimshottari': vimshottari
    }
