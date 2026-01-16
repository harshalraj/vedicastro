import datetime
from interpretation_data import PLANET_IN_HOUSE, PLANET_IN_SIGN
from karmic_data import RAHU_HOUSE_PURPOSE, KETU_HOUSE_KARMA, RAHU_NAKSHATRA_PURPOSE, KETU_NAKSHATRA_KARMA

def get_yogas(chart_data):
    """
    Analyzes the chart for common auspicious Yogas.
    """
    yogas = []
    
    # Extract data for easier access
    # d1 is House -> [Planets]
    d1 = chart_data.get('d1', {})
    # details has Ascendant Sign
    asc_sign = chart_data['details']['Ascendant']
    
    # Planetary Details List for Sign/Degree info
    p_details = {p['Planet']: p for p in chart_data['planetary_details']}
    
    # Helper: Get House of a Planet
    def get_house(planet_name):
        for h, planets in d1.items():
            if planet_name in planets:
                return int(h)
        return None
        
    # Helper: Get Sign of a Planet
    def get_sign(planet_name):
        if planet_name in p_details:
            return p_details[planet_name]['Sign']
        return None

    # Helper: Get Lord of a House
    signs_order = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                   'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    sign_lords = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
        'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
        'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    asc_idx = signs_order.index(asc_sign)
    
    def get_lord_of_house_num(house_num):
        # House 1 is asc_sign. House 2 is next sign...
        # sign_idx = (asc_idx + (house_num - 1)) % 12
        sign_idx = (asc_idx + (house_num - 1)) % 12
        sign = signs_order[sign_idx]
        return sign_lords[sign]

    # --- YOGA CHECKS ---

    # 1. Gajakesari Yoga: Jupiter in Kendra (1, 4, 7, 10) from Moon
    moon_house = get_house('Moon')
    jupiter_house = get_house('Jupiter')
    
    if moon_house and jupiter_house:
        # Distance from Moon to Jupiter
        dist = (jupiter_house - moon_house) % 12
        if dist < 0: dist += 12
        # Counting inclusive: 0 (same), 3 (4th), 6 (7th), 9 (10th)
        # indices diff is 0, 3, 6, 9 corresponds to 1st, 4th, 7th, 10th positions
        if dist in [0, 3, 6, 9]:
            yogas.append({
                "name": "Gajakesari Yoga",
                "desc": "Jupiter in Kendra from Moon. Brings wisdom, wealth, and respect."
            })
            
    # 2. Budhaditya Yoga: Sun and Mercury in same house
    sun_house = get_house('Sun')
    mercury_house = get_house('Mercury')
    if sun_house and mercury_house and sun_house == mercury_house:
        yogas.append({
            "name": "Budhaditya Yoga",
            "desc": "Sun and Mercury combined. Excellent for intellect, communication, and business."
        })
        
    # 3. Ruchaka Yoga (Pancha Mahapurusha): Mars in Own/Exalted sign AND in Kendra (1,4,7,10 from Lagna)
    mars_sign = get_sign('Mars')
    mars_house = get_house('Mars')
    if mars_house in [1, 4, 7, 10]:
        if mars_sign in ['Aries', 'Scorpio', 'Capricorn']: # Own or Exalted
            yogas.append({
                "name": "Ruchaka Yoga",
                "desc": "Strong Mars in Kendra. Indicates courage, leadership, and physical strength."
            })
            
    # 4. Bhadra Yoga: Mercury in Own/Exalted AND in Kendra
    merc_sign = get_sign('Mercury')
    merc_house = get_house('Mercury')
    if merc_house in [1, 4, 7, 10]:
        if merc_sign in ['Gemini', 'Virgo']:
            yogas.append({
                "name": "Bhadra Yoga",
                "desc": "Strong Mercury in Kendra. Outstanding intellect, speech, and analysis."
            })

    # 5. Hamsa Yoga: Jupiter in Own/Exalted AND in Kendra
    jup_sign = get_sign('Jupiter')
    jup_house = get_house('Jupiter')
    if jup_house in [1, 4, 7, 10]:
        if jup_sign in ['Sagittarius', 'Pisces', 'Cancer']:
            yogas.append({
                "name": "Hamsa Yoga",
                "desc": "Strong Jupiter in Kendra. Bringing wisdom, purity, and spiritual inclination."
            })
            
    # 6. Malavya Yoga: Venus in Own/Exalted AND in Kendra
    ven_sign = get_sign('Venus')
    ven_house = get_house('Venus')
    if ven_house in [1, 4, 7, 10]:
        if ven_sign in ['Taurus', 'Libra', 'Pisces']:
            yogas.append({
                "name": "Malavya Yoga",
                "desc": "Strong Venus in Kendra. Granting luxury, beauty, and artistic talent."
            })

    # 7. Shasha Yoga: Saturn in Own/Exalted AND in Kendra
    sat_sign = get_sign('Saturn')
    sat_house = get_house('Saturn')
    if sat_house in [1, 4, 7, 10]:
        if sat_sign in ['Capricorn', 'Aquarius', 'Libra']:
            yogas.append({
                "name": "Shasha Yoga",
                "desc": "Strong Saturn in Kendra. Authority, discipline, and longevity."
            })
            
    # 8. Lakshmi Yoga: 9th Lord in Kendra/Trikona (1,4,7,10, 5,9) & Exalted/Own sign OR with Ascendant Lord
    # Simplified: 9th Lord in Own/Exal sign.
    lord_9 = get_lord_of_house_num(9)
    # Finding where Lord 9 is
    # This requires more mapping (which planet corresponds to string 'Mars')
    # Let's skip complex lordship logic implementation for MVP and stick to planet positions.
    
    # 9. Chandra Mangal Yoga: Moon and Mars conjunction
    if moon_house and mars_house and moon_house == mars_house:
         yogas.append({
            "name": "Chandra Mangal Yoga",
            "desc": "Moon and Mars conjoined. Earnings through enterprise, but potential for anxiety."
        })
        
    # 10. Vipreet Raja Yoga (Harsha, Sarala, Vimala)
    # Lords of 6, 8, 12 in 6, 8, 12
    lord_6 = get_lord_of_house_num(6)
    lord_8 = get_lord_of_house_num(8)
    lord_12 = get_lord_of_house_num(12)
    
    # Mapping planet names to houses
    # Need to find house of lord_6
    house_of_lord_6 = get_house(lord_6)
    house_of_lord_8 = get_house(lord_8)
    house_of_lord_12 = get_house(lord_12)
    
    dusthana = [6, 8, 12]
    
    if house_of_lord_6 in dusthana:
        yogas.append({
            "name": "Harsha Vipreet Raja Yoga",
            "desc": f"Lord of 6th ({lord_6}) is in House {house_of_lord_6}. Health, wealth, and victory over enemies."
        })
    if house_of_lord_8 in dusthana:
        yogas.append({
            "name": "Sarala Vipreet Raja Yoga",
            "desc": f"Lord of 8th ({lord_8}) is in House {house_of_lord_8}. Longevity, fearlessness, and prosperity."
        })
    if house_of_lord_12 in dusthana:
        yogas.append({
            "name": "Vimala Vipreet Raja Yoga",
            "desc": f"Lord of 12th ({lord_12}) is in House {house_of_lord_12}. Independence, happiness, and just conduct."
        })

    # 11. Kemadruma Yoga (Negative but important)
    # No planet in 2nd or 12th from Moon (excluding Sun/Rahu/Ketu)
    # This checks neighbors of Moon House
    if moon_house:
        prev_h = (moon_house - 2) % 12 + 1 # 12th from Moon
        next_h = moon_house % 12 + 1 # 2nd from Moon
        
        has_planet_prev = False
        has_planet_next = False
        
        # Check all houses for planets
        for h, planets in d1.items():
            if h == prev_h:
               valid_ps = [p for p in planets if p not in ['Sun', 'Rahu', 'Ketu']]
               if valid_ps: has_planet_prev = True
            if h == next_h:
               valid_ps = [p for p in planets if p not in ['Sun', 'Rahu', 'Ketu']]
               if valid_ps: has_planet_next = True
               
        if not has_planet_prev and not has_planet_next:
            # Check Kendra from Lagna/Moon can cancel it, but let's just flag it for detailed analysis
             yogas.append({
                "name": "Kemadruma Yoga",
                "desc": "No planets surrounding Moon. Mental isolation or struggles, but can be cancelled by other strengths."
            })
            
    return yogas

    # 12. Parasara Raja Yoga (Kendra-Trikona Relationships)
    # Lords of Kendra (1, 4, 7, 10) and Trikona (1, 5, 9) in conjunction or mutual aspect (we check conjunction here for MVP)
    # Most powerful: 9th and 10th Lords. 
    # Also 4th+5th, 1st+5th, 1st+9th etc.
    
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]
    
    # Check all Kendra + Trikona combinations
    # Simplified: Check Conjunctions
    
    for k in kendra_houses:
        for t in trikona_houses:
            k_lord = get_lord_of_house_num(k)
            t_lord = get_lord_of_house_num(t)
            
            # Avoid self-conjunction (1st lord with 1st lord)
            if k_lord == t_lord:
                continue
                
            k_house = get_house(k_lord)
            t_house = get_house(t_lord)
            
            if k_house and t_house and k_house == t_house:
                # Special Name for 9th+10th
                y_name = f"Dharma-Karma Adhipati Yoga (Lords of {k} and {t})" if {k,t} == {9,10} else f"Raja Yoga (Lords of {k} and {t})"
                
                # Check duplication?
                exists = any(y['name'] == y_name for y in yogas)
                if not exists:
                     yogas.append({
                        "name": y_name,
                        "desc": f"Conjunction of Kendra ({k}) and Trikona ({t}) lords. Brings power, success, and luck."
                    })

    # 13. Parivartana Yoga (Exchange of Signs)
    # Check if Planet A is in B's sign AND Planet B is in A's sign
    # We essentially check houses. 
    # Lord of House X in House Y AND Lord of House Y in House X.
    
    # Iterate all unique pairs of houses (1-12)
    checked_pairs = set()
    for h1 in range(1, 13):
        for h2 in range(h1 + 1, 13):
            l1 = get_lord_of_house_num(h1)
            l2 = get_lord_of_house_num(h2)
            
            # Where are they placed?
            p1_house = get_house(l1)
            p2_house = get_house(l2)
            
            if p1_house == h2 and p2_house == h1:
                # Exchange Detected
                # Categorize: 
                # Maha Parivartana: Kendra/Trikona or 2, 11 involvement (Good)
                # Dainya: 6, 8, 12 involved (Bad)
                # Khala: 3rd involved (Mixed)
                
                is_dusthana = any(h in [6, 8, 12] for h in [h1, h2])
                
                if is_dusthana:
                     # Skip Dainya for "Raja Yoga" request, or label appropriately? 
                     # User asked for "All other Raja Yogas", usually implies Good ones.
                     # But Parivartana is powerful. Let's list Maha only if we want to be strict, or list all.
                     # Let's list Dainya as "Dainya Yoga" (not Raja).
                     pass 
                else:
                    yogas.append({
                        "name": "Maha Parivartana Yoga",
                        "desc": f"Exchange of signs between Lords of {h1} and {h2}. Mutual strengthening of houses."
                    })
                    
    # 14. Neech Bhanga Raja Yoga (Cancellation of Debilitation)
    # Logic: If a planet is debilitated, check conditions to cancel it.
    # 1. Lord of the sign where it is debilitated is in Kendra from Lagna or Moon.
    # 2. Planet that would be exalted in that sign is in Kendra from Lagna or Moon.
    
    debilitation_map = {
        'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer', 'Mercury': 'Pisces',
        'Jupiter': 'Capricorn', 'Venus': 'Virgo', 'Saturn': 'Aries'
    }
    
    exaltation_map = {v: k for k, v in debilitation_map.items()} # Inverted? No.
    # Exaltation signs: Sun->Aries, Moon->Taurus, Mars->Cap, Merc->Virgo, Jup->Cancer, Ven->Pisces, Sat->Libra.
    # The map above checks Debilitation.
    # E.g. If Sun is in Libra. Lord of Libra is Venus. Is Venus in Kendra?
    # Or, Planet Exalted in Libra is Saturn. Is Saturn in Kendra?
    
    planet_exalted_in_sign = {
        'Aries': 'Sun', 'Taurus': 'Moon', 'Capricorn': 'Mars', 'Virgo': 'Mercury',
        'Cancer': 'Jupiter', 'Pisces': 'Venus', 'Libra': 'Saturn'
    }
    
    for planet, deb_sign in debilitation_map.items():
        p_sign = get_sign(planet)
        if p_sign == deb_sign:
            # Planet is Debilitated
            is_cancelled = False
            reason = ""
            
            # Condition 1: Lord of Debilitation Sign
            lord_of_deb = sign_lords[deb_sign]
            lord_house_lagna = get_house(lord_of_deb)
            
            # Kendra from Lagna
            if lord_house_lagna in [1, 4, 7, 10]:
                is_cancelled = True
                reason = f"Lord of debilitation sign ({lord_of_deb}) is in Kendra."
                
            # Kendra from Moon
            # Need relative house
            if not is_cancelled and moon_house and lord_house_lagna:
                dist_moon = (lord_house_lagna - moon_house) % 12
                if dist_moon in [0, 3, 6, 9]: # 1, 4, 7, 10 equivalent indices
                    is_cancelled = True
                    reason = f"Lord of debilitation sign ({lord_of_deb}) is in Kendra from Moon."

            # Condition 2: Planet Exalted in this sign
            if not is_cancelled:
                exalted_planet = planet_exalted_in_sign.get(deb_sign)
                if exalted_planet:
                    ex_house_lagna = get_house(exalted_planet)
                    
                    if ex_house_lagna in [1, 4, 7, 10]:
                        is_cancelled = True
                        reason = f"Planet exalted in this sign ({exalted_planet}) is in Kendra."
                        
                    if not is_cancelled and moon_house and ex_house_lagna:
                        dist_moon = (ex_house_lagna - moon_house) % 12
                        if dist_moon in [0, 3, 6, 9]:
                            is_cancelled = True
                            reason = f"Planet exalted in this sign ({exalted_planet}) is in Kendra from Moon."
                            
            if is_cancelled:
                yogas.append({
                    "name": "Neech Bhanga Raja Yoga",
                    "desc": f"{planet} is debilitated in {p_sign}, but cancelled: {reason} Converts weakness into strength."
                })
    # 15. Dhan Yoga (Wealth Producing Combinations)
    # Combinations involving Lords of 1, 2, 5, 9, 11.
    # Specifically connection between (2 and 11), (2 and 5), (2 and 9), (11 and 5), (11 and 9).
    # Also 1st lord connection with these is Dhan/Raja.
    
    wealth_lords_indices = [2, 11]
    trine_lords_indices = [1, 5, 9]
    
    # Check interaction between Wealth Lords and Trine Lords
    for w in wealth_lords_indices:
        for t in trine_lords_indices:
             w_lord = get_lord_of_house_num(w)
             t_lord = get_lord_of_house_num(t)
             
             if w_lord == t_lord: continue # Same planet ownership (e.g. Venus owns 2 and 7 for Aries? No, 2&7. But 2&9 impossible? Mercuryowns 3&6. Saturn 10&11.)
             # Only Mercury (Gemini/Virgo) or Jupiter/Mars etc.
             # e.g. for Cap Lagna: Saturn is 1 and 2. So Lord 1 = Lord 2. This is a Great Yoga itself.
             
             # If same lord: It is a self-generating yoga?
             if w_lord == t_lord:
                 # Skip for now to avoid redundant print, or handle as special case.
                 pass
             
             # Check Conjunction
             w_house = get_house(w_lord)
             t_house = get_house(t_lord)
             
             if w_house and t_house and w_house == t_house:
                 y_name = f"Dhan Yoga (Lords of {w} and {t})"
                 exists = any(y['name'] == y_name for y in yogas)
                 if not exists:
                     yogas.append({
                        "name": y_name,
                        "desc": f"Conjunction of Lord of {w} (Wealth) and Lord of {t}. Indicator of significant prosperity."
                     })
                     
    # Check 2nd and 11th specific relationship
    l2 = get_lord_of_house_num(2)
    l11 = get_lord_of_house_num(11)
    if get_house(l2) == 11 and get_house(l11) == 2:
         yogas.append({
            "name": "Maha Dhan Yoga",
            "desc": f"Exchange of signs between Lords of 2nd (Wealth) and 11th (Gains). Excellent for financial success."
         })
    elif get_house(l2) == 11:
         yogas.append({
            "name": "Dhan Yoga (2nd Lord in 11th)",
            "desc": "Lord of Wealth is in the House of Gains. Money comes easily."
         })
    elif get_house(l11) == 2:
         yogas.append({
            "name": "Dhan Yoga (11th Lord in 2nd)",
            "desc": "Lord of Gains is in the House of Wealth. Multiple sources of income."
         })
         
    return yogas

def check_manglik(chart_data):
    """
    Checks for Manglik Dosha (Mars in 1, 4, 7, 8, 12).
    Simple check from Lagna.
    """
    d1 = chart_data.get('d1', {})
    
    # helper
    def get_house(planet_name):
        for h, planets in d1.items():
            if planet_name in planets:
                return int(h)
        return None
        
    mars_house = get_house('Mars')
    
    if not mars_house:
        return {"status": False, "desc": "Mars position could not be determined."}
        
    manglik_houses = [1, 4, 7, 8, 12]
    
    if mars_house in manglik_houses:
        return {
            "status": True,
            "desc": f"Mars is in House {mars_house}. This indicates Manglik Dosha. It implies high energy in relationships and requires matching."
        }
    else:
        return {
            "status": False,
            "desc": "Mars is not in a Manglik position from Lagna. No Manglik Dosha detected."
        }

def get_house_analysis(chart_data):
    """
    Returns generic interpretations for planetary placements.
    Simulated Sutras (Bhrigu/Jaimini style).
    """
    analysis = []
    
    # Extract data
    d1 = chart_data['d1']
    p_details = {p['Planet']: p for p in chart_data['planetary_details']}
    
    def analyze_planet(planet, house, sign):
        # Look up interpretatons
        text = ""
        
        # 1. House Reading
        house_key = f"{planet}_{house}"
        h_text = PLANET_IN_HOUSE.get(house_key, "")
        if h_text:
            text += h_text + " "
            
        # 2. Sign Reading
        sign_key = f"{planet}_{sign}"
        s_text = PLANET_IN_SIGN.get(sign_key, "")
        if s_text:
            text += s_text
            
        return text

    # Iterate over key planets
    key_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    # Find house for each
    house_map = {}
    for h, planets in d1.items():
        for p in planets:
            house_map[p] = int(h)
            
    for p in key_planets:
        if p in house_map and p in p_details:
            h = house_map[p]
            s = p_details[p]['Sign']
            reading = analyze_planet(p, h, s)
            if reading:
                analysis.append({
                    "planet": p,
                    "house": h,
                    "sign": s,
                    "text": reading
                })

    return analysis

def get_mahadasha_prediction(vimshottari_data):
    """
    Returns prediction for current Dasha.
    """
    if not vimshottari_data:
        return {}
        
    # Find current date dasha
    today = datetime.datetime.now().date()
    current_dasha = None
    
    for d in vimshottari_data:
        # Date format YYYY-MM-DD
        try:
            start = datetime.datetime.strptime(d['Start'], "%Y-%m-%d").date()
            end = datetime.datetime.strptime(d['End'], "%Y-%m-%d").date()
            if start <= today <= end:
                current_dasha = d
                break
        except:
            continue
            
    if not current_dasha:
        return {"current": "Unknown", "text": "Could not determine current Dasha."}
        
    lord = current_dasha['Lord']
    
    # Generic Dasha Phals
    phal = {
        "Sun": "A period of authority, visibility, and vitality. Good for career advancement but watch out for ego conflicts.",
        "Moon": "A period of emotional sensitivity, changes, and focus on home dynamics. Travel is possible.",
        "Mars": "High energy, initiative, and drive. Avoid aggression and accidents. Good for technical work or real estate.",
        "Rahu": "A time of confusion, foreign travel, or sudden material gains. Ambition increases but mental peace may vary.",
        "Jupiter": "Expansion, learning, wisdom, and general prosperity. Auspicious for family and knowledge.",
        "Saturn": "Hard work, discipline, and slow but steady progress. Tests of patience and maturity.",
        "Mercury": "Focus on communication, business, learning, and adaptability. Good for trade and intellect.",
        "Ketu": "Detachment, spiritual growth, and introspection. Sudden breaks or mystical experiences.",
        "Venus": "Romance, luxury, comfort, and artistic pursuits. Good for relationships and enjoyment."
    }
    
    prediction = phal.get(lord, "A period of change.")
    
    return {
        "current_lord": lord,
        "period": f"{current_dasha['Start']} to {current_dasha['End']}",
        "prediction": prediction
    }

def get_nakshatra_analysis(chart_data):
    """
    Returns personality analysis based on Moon's Nakshatra.
    """
    moon_nak = ""
    for p in chart_data['planetary_details']:
        if p['Planet'] == 'Moon':
            moon_nak = p['Nakshatra'].split(' (')[0] # Remove pada info
            break
            
    if not moon_nak:
        return {}
        
    traits = {
        "Ashwini": "You are energetic, quick, and like to start new things but may leave them unfinished. You are independent and courageous.",
        "Bharani": "You have a determined and truthful nature. You value honesty and can be slightly rigid in your views.",
        "Krittika": "You are sharp, critical, and ambitious. You have a fiery nature and leadership qualities.",
        "Rohini": "You are charming, artistic, and love luxury. You are emotional and attached to family/home.",
        "Mrigashira": "You are curious, restless, and constantly seeking new experiences. You have a gentle and searching nature.",
        "Ardra": "You are intellectual and analytical but can go through emotional storms. You are capable of great transformation.",
        "Punarvasu": "You are benevolent, patient, and content. You recover well from setbacks and value simplicity.",
        "Pushya": "You are nurturing, spiritual, and helpful. This is considered the most auspicious star for stability.",
        "Ashlesha": "You are insightful, mystical, and protective. You can be secretive and have strong intuition.",
        "Magha": "You have a regal and authoritative presence. You value tradition, ancestry, and respect.",
        "Purva Phalguni": "You are creative, relaxed, and love rest and recreation. You enjoy the good things in life.",
        "Uttara Phalguni": "You are helpful, supportive, and reliable. You make a good friend and are socially responsible.",
        "Hasta": "You are skilled with your hands, detail-oriented, and industrious. You have a quick wit.",
        "Chitra": "You are artistic, designing, and visually oriented. You like things to be perfect and beautiful.",
        "Swati": "You are diplomatic, independent, and adaptable like the wind. You value freedom and balance.",
        "Vishakha": "You are focused, goal-oriented, and determined. You have the drive to achieve your ambitions.",
        "Anuradha": "You are friendly, loyal, and group-oriented. You can navigate difficulties with persistence.",
        "Jyeshtha": "You are mature, protective, and responsible. You may feel a burden of leadership or seniority.",
        "Mula": "You are investigative and can get to the root of matters. You may experience sudden changes or losses.",
        "Purva Ashadha": "You are optimistic, invincible, and have a strong conviction. You believe in your cause.",
        "Uttara Ashadha": "You are persistent, enduring, and victorious over time. You have great stamina and patience.",
        "Shravana": "You are a great listener and learner. You seek knowledge and have a melodious voice or ear.",
        "Dhanishtha": "You are musical, rhythmical, and ambitious. You have good timing and social skills.",
        "Shatabhisha": "You are secretive, healing, and visionary. You can see things others miss and value privacy.",
        "Purva Bhadrapada": "You are intense, spiritual, and can be two-faced or versatile. You have deep philosophical capability.",
        "Uttara Bhadrapada": "You are disciplined, wise, and compassionate. You control your anger well and are profound.",
        "Revati": "You are nurturing, wealthy, and protective of others. You are a dreamer and empathetic."
    }
    
    return {
        "nakshatra": moon_nak,
        "traits": traits.get(moon_nak, "A unique and complex personality.")
    }

def get_karmic_analysis(chart_data):
    """
    Returns Purpose (Rahu) and Past Karma (Ketu) Analysis.
    """
    # Need to find House and Nakshatra for Rahu and Ketu
    d1 = chart_data.get('d1', {})
    p_details = {p['Planet']: p for p in chart_data['planetary_details']}
    
    def get_house(planet):
        for h, planets in d1.items():
            if planet in planets:
                return int(h)
        return None
        
    def get_nakshatra_name(planet):
        if planet in p_details:
             # Format is "Name (Pada)" e.g. "Ashwini (1)"
             return p_details[planet]['Nakshatra'].split(' (')[0]
        return None

    rahu_h = get_house('Rahu')
    ketu_h = get_house('Ketu')
    
    rahu_nak = get_nakshatra_name('Rahu')
    ketu_nak = get_nakshatra_name('Ketu')
    
    rahu_house_text = RAHU_HOUSE_PURPOSE.get(rahu_h, "Rahu's house purpose is mysterious.")
    ketu_house_text = KETU_HOUSE_KARMA.get(ketu_h, "Ketu's past karma is hidden.")
    
    rahu_nak_text = RAHU_NAKSHATRA_PURPOSE.get(rahu_nak, "")
    ketu_nak_text = KETU_NAKSHATRA_KARMA.get(ketu_nak, "")
    
    return {
        "rahu": {
            "house_text": rahu_house_text,
            "nakshatra_text": rahu_nak_text,
            "house": rahu_h,
            "nakshatra": rahu_nak
        },
        "ketu": {
            "house_text": ketu_house_text,
            "nakshatra_text": ketu_nak_text,
            "house": ketu_h,
            "nakshatra": ketu_nak
        }
    }
