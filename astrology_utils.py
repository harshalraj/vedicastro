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
    
    # Helper to calculate Antardashas
    def get_antardashas(md_lord, md_start_date, is_balance=False, birth_date_obj=None):
        # Sequence starts from the MD Lord itself
        start_idx = dasha_lords.index(md_lord)
        ads = []
        
        md_years = dasha_years[md_lord]
        
        # If Balance Dasha: Start Date is NOT the MD Start. It is Birth Date.
        # We need to find the theoretical MD Start.
        # But we can also just calculate the full sequence and filter.
        
        theo_start_date = None
        if is_balance and birth_date_obj:
            # We need to backtrack to find theoretical start
            # logic: md_start_date passed in IS the birth date for Balance Dasha
            # We already computed remaining_percent in the main function but didn't pass it.
            # Let's re-calculate or pass it.
            # Simpler: Generate AD list with relative time (years from 0), then map to dates?
            pass

        # Let's use a simpler forward generation for normal Dashas
        # And a special filtering for Balance.
        
        curr_ad_date = datetime.datetime.strptime(md_start_date, "%Y-%m-%d")
        
        # Proper Standard Calculation
        # AD Lord Loop
        
        # If Balance: we need to find WHICH AD we are in or past.
        # Let's generate the Full 9 ADs assuming md_start_date was the ACTUAL start of the MD.
        # If is_balance, md_start_date is actually the Birth Date, which is mid-way. 
        # So we can't use it as the seed for the sequence if we want to show the partial first AD correctly?
        # Actually, for the user, they just want to see the sub-periods from Birth onwards.
        # So we need to calculate the Full MD Schedule relative to a Theoretical Start.
        
        return ads

    # Refined Logic for Dashas
    dashas = []
    current_date = birth_date
    
    # 1. Balance Dasha
    # Calculate Theoretical Start of this MD
    passed_percent = 1.0 - remaining_percent
    passed_years = dasha_years[start_lord] * passed_percent
    theo_start = birth_date - datetime.timedelta(days=passed_years * 365.25)
    
    # Calculate Full ADs for this Theoretical Context, filter for > BirthDate
    def generate_filtered_ads(md_lord, md_duration_years, relative_start_date, cutoff_date):
        filtered_list = []
        ad_start_cursor = relative_start_date
        
        md_lord_idx = dasha_lords.index(md_lord)
        
        for i in range(9):
            ad_lord = dasha_lords[(md_lord_idx + i) % 9]
            ad_dur = (md_duration_years * dasha_years[ad_lord]) / 120.0
            ad_days = ad_dur * 365.25
            ad_end_cursor = ad_start_cursor + datetime.timedelta(days=ad_days)
            
            # Check overlap with [cutoff_date, infinity]
            if ad_end_cursor > cutoff_date:
                # This AD is visible
                # Determine display start
                disp_start = max(ad_start_cursor, cutoff_date)
                
                # Duration for display
                # We can't easily recalc duration string if we chop it.
                # But let's show the dates correctly.
                
                filtered_list.append({
                    "Lord": ad_lord,
                    "Start": disp_start.strftime("%Y-%m-%d"),
                    "End": ad_end_cursor.strftime("%Y-%m-%d"),
                    "Duration": "-" # Placeholder or calc diff
                })
                
            ad_start_cursor = ad_end_cursor
            
        return filtered_list

    # First Dasha Object
    days_balance = balance_years * 365.25
    balance_end_date = current_date + datetime.timedelta(days=days_balance)
    
    # Generate ADs for First Dasha
    first_ads = generate_filtered_ads(start_lord, dasha_years[start_lord], theo_start, birth_date)
    
    dashas.append({
        "Lord": start_lord,
        "Start": current_date.strftime("%Y-%m-%d"),
        "End": balance_end_date.strftime("%Y-%m-%d"),
        "Duration": f"{balance_years:.1f}y (Bal)",
        "Antardashas": first_ads
    })
    
    current_date = balance_end_date
    curr_lord_idx = (lord_idx + 1) % 9
    
    # Loop
    birth_year = birth_date.year
    cycle_count = 0
    
    # Standard AD Generator for full dashas
    def generate_full_ads(md_lord, start_date):
        md_lord_idx = dasha_lords.index(md_lord)
        md_dur = dasha_years[md_lord]
        res = []
        curr = start_date
        for i in range(9):
             ad_lord = dasha_lords[(md_lord_idx + i) % 9]
             ad_years = (md_dur * dasha_years[ad_lord]) / 120.0
             ad_days = ad_years * 365.25
             end = curr + datetime.timedelta(days=ad_days)
             res.append({
                 "Lord": ad_lord,
                 "Start": curr.strftime("%Y-%m-%d"),
                 "End": end.strftime("%Y-%m-%d"),
                 "Duration": f"{ad_years:.2f}y"
             })
             curr = end
        return res

    # We iterate 8 times to complete the cycle of 9 planets (1 Balance + 8 Full)
    while cycle_count < 8:
        lord = dasha_lords[curr_lord_idx]
        years = dasha_years[lord]
        
        days_duration = years * 365.25
        end_date = current_date + datetime.timedelta(days=days_duration)
        
        dashas.append({
            "Lord": lord,
            "Start": current_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d"),
            "Duration": f"{years}y",
            "Antardashas": generate_full_ads(lord, current_date)
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
