import datetime

# Keyword Mappings
TOPICS = {
    "self": {"house": 1, "karaka": ["Sun"], "keywords": ["self", "personality", "appearance", "body", "health", "character", "ego", "identity"]},
    "wealth": {"house": 2, "karaka": ["Jupiter", "Venus"], "keywords": ["money", "wealth", "finance", "rich", "bank", "gain", "family", "speech"]},
    "siblings": {"house": 3, "karaka": ["Mars", "Mercury"], "keywords": ["sibling", "brother", "sister", "courage", "communication", "skill", "talent", "writing"]},
    "home": {"house": 4, "karaka": ["Moon", "Mars"], "keywords": ["home", "house", "property", "land", "mother", "residence", "car", "vehicle", "peace"]},
    "children": {"house": 5, "karaka": ["Jupiter"], "keywords": ["child", "children", "baby", "son", "daughter", "progeny", "kids", "pregnant", "creativity", "intelligence"]},
    "health": {"house": 6, "karaka": ["Saturn", "Mars", "Sun"], "keywords": ["health", "disease", "sick", "pain", "hospital", "illness", "sickness", "debt"]},
    "job": {"house": 6, "karaka": ["Saturn", "Sun"], "keywords": ["job", "service", "employment", "employee", "workplace", "colleague", "subordinate"]}, # Separated from Health
    "marriage": {"house": 7, "karaka": ["Venus", "Jupiter"], "keywords": ["marriage", "spouse", "wife", "husband", "partner", "love", "relationship", "marry", "married", "wedding", "partnership", "business partner"]},
    "transformation": {"house": 8, "karaka": ["Saturn"], "keywords": ["death", "longevity", "occult", "mystery", "secret", "sudden", "inheritance", "transformation", "research"]},
    "luck": {"house": 9, "karaka": ["Jupiter", "Sun"], "keywords": ["luck", "fortune", "dharma", "spiritual", "guru", "father", "travel", "pilgrimage", "higher education", "university"]},
    "education": {"house": 9, "karaka": ["Mercury", "Jupiter"], "keywords": ["education", "study", "studies", "learning", "degree", "school", "college", "knowledge", "exam"]}, # 9th House primary for Higher Ed
    "career": {"house": 10, "karaka": ["Saturn", "Sun"], "keywords": ["career", "job", "work", "business", "profession", "promotion", "status", "reputation", "fame", "authority"]},
    "gains": {"house": 11, "karaka": ["Jupiter"], "keywords": ["gain", "income", "profit", "friend", "network", "wish", "desire", "award", "prize"]},
    "loss": {"house": 12, "karaka": ["Saturn", "Ketu"], "keywords": ["loss", "expense", "foreign", "abroad", "sleep", "spiritual", "moksha", "isolation", "prison", "hospitalization"]}
}

HOUSE_MEANINGS = {
    1: "Defines your personality, body, and how the world sees you.",
    2: "Shows your wealth, family values, and way of speaking.",
    3: "Represents courage, communication, skills, and siblings.",
    4: "Relates to basic education and the emotional aspect of learning, plus home and mother.",
    5: "Governs intellect, creativity, memory, and undergraduate-level knowledge.",
    6: "Deals with health, work, debts, and everyday challenges.",
    7: "Indicates marriage, partnerships, and public relations.",
    8: "Reveals transformation, secrets, sudden events, and longevity.",
    9: "The primary house for higher learning, philosophy, university education, and spiritual/advanced studies.",
    10: "Defines career, reputation, authority, and achievements.",
    11: "Shows income, gains, friends, and fulfilled desires.",
    12: "Governs losses, expenses, isolation, and spiritual liberation."
}

HOUSE_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

from transit_utils import get_current_transits, analyze_transits

def get_house_of_planet(d1_chart, planet):
    for h, planets in d1_chart.items():
        if planet in planets:
            return h
    return "?"

def get_sign_of_house(house_num, ascendant_sign):
    signs_list = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    asc_idx = signs_list.index(ascendant_sign)
    target_sign_idx = (asc_idx + house_num - 1) % 12
    return signs_list[target_sign_idx]

def process_question(question, chart_data):
    # 1. Identify Topic
    q_lower = question.lower()
    topic_data = None
    detected_topic = "General"
    
    for key, data in TOPICS.items():
        for kw in data['keywords']:
            if kw in q_lower:
                topic_data = data
                detected_topic = key.capitalize()
                break
        if topic_data:
            break
            
    if not topic_data:
        return {
            "answer": "I can generally answer questions about any aspect of life (Career, Wealth, Marriage, Health, Spirituality, etc.). Try asking something specific like 'How is my luck?' or 'Will I go abroad?'.",
            "topic": "Unknown"
        }

    # 2. Logic Branching: Education (Multi-House) vs Others (Single House)
    target_houses = []
    if detected_topic == "Education":
        target_houses = [9, 5, 4] # Priority Order
    else:
        target_houses = [topic_data['house']]

    karakas = topic_data['karaka']
    ascendant_sign = chart_data['details']['Ascendant']
    p_details = {p['Planet']: p for p in chart_data['planetary_details']}
    
    response = f"**Aspect:** {detected_topic}\n"
    
    all_relevant_planets_for_transit = []
    all_relevant_planets_for_transit.extend(karakas)

    # 3. Analyze Each House Logic
    for h_num in target_houses:
        sign = get_sign_of_house(h_num, ascendant_sign)
        lord = HOUSE_LORDS[sign]
        lord_info = p_details.get(lord)
        
        all_relevant_planets_for_transit.append(lord)
        
        lord_placed_house = get_house_of_planet(chart_data['d1'], lord)
        lord_placed_sign = lord_info['Sign'] if lord_info else "?"

        # Append to response
        response += f"\n**{h_num}th House ({HOUSE_MEANINGS[h_num]}):**\n"
        response += f"- **House Lord:** {lord} (Placed in {lord_placed_sign}, House {lord_placed_house})\n"
        
        # Simple synthesis
        if str(lord_placed_house) in ['6', '8', '12']:
            response += f"  - *Observation:* The lord is in a challenging house ({lord_placed_house}), suggesting potential hurdles or hard work needed here.\n"
        elif str(lord_placed_house) in ['1', '4', '7', '10', '5', '9']:
            response += f"  - *Observation:* The lord is well-placed in a Kendra/Trikona, indicating strength.\n"

    # Add Karakas info once
    response += "\n**Karaka (Significators) Analysis:**\n"
    for k in karakas:
        k_info = p_details.get(k)
        if k_info:
            h = get_house_of_planet(chart_data['d1'], k)
            response += f"- **{k}:** Placed in {k_info['Sign']} (House {h})\n"

    # 4. Dasha Analysis (Check against ALL relevant planets)
    vimshottari = chart_data.get('vimshottari', [])
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    unique_planets = list(set(all_relevant_planets_for_transit)) # Dedup

    upcoming_period = None
    is_running = False

    # Check currently running dasha
    for d in vimshottari:
        start = d['Start']
        end = d['End']
        if start <= current_date <= end:
            if d['Lord'] in unique_planets:
                upcoming_period = f"currently in the **Mahadasha of {d['Lord']}** (until {end})."
                is_running = True
            
            if 'Antardashas' in d:
                for ad in d['Antardashas']:
                    if ad['Start'] <= current_date <= ad['End']:
                        if ad['Lord'] in unique_planets:
                            upcoming_period = f"currently in the **Antardasha of {ad['Lord']}** (under {d['Lord']} MD) until {ad['End']}."
                            is_running = True
                            break
            break

    # If not currently running relevant period, find the NEAREST upcoming one (AD or MD)
    if not is_running:
        nearest_date = None
        nearest_msg = ""
        
        # We need to iterate through the entire structured list. 
        # Assuming 'vimshottari' is sorted by date.
        for d in vimshottari:
            # Check MD Start
            if d['Start'] > current_date:
                if d['Lord'] in unique_planets:
                    # Found a future MD
                    nearest_msg = f"upcoming **Mahadasha of {d['Lord']}** starting on {d['Start']}."
                    break # Stop at first major future event
            
            # Check ADs
            if 'Antardashas' in d:
                for ad in d['Antardashas']:
                     if ad['Start'] > current_date:
                         if ad['Lord'] in unique_planets:
                             # We found a relevant sub-period
                             nearest_msg = f"upcoming **Antardasha of {ad['Lord']}** (in {d['Lord']} MD) starting on {ad['Start']}."
                             break
                if nearest_msg: break
        
        if nearest_msg:
             upcoming_period = nearest_msg
        else:
             upcoming_period = "No immediate major activation found in Dasha."

    # 5. Connect with Transits (Gochar) of ALL relevant planets
    transit_insight = ""
    try:
        current_transits = get_current_transits()
        moon_sign = chart_data['details'].get('Moon Sign', 'Aries') 
        transit_msg = analyze_transits(moon_sign, current_transits, unique_planets)
        
        if transit_msg:
            # Check for positive keywords in the transit analysis to construct a summary
            if "favorable" in transit_msg.lower() or "auspicious" in transit_msg.lower() or "supportive" in transit_msg.lower():
                transit_insight = "However, **Current Transits are Favorable**, indicating a good time to act despite the neutral Dasha."
            elif "challenging" in transit_msg.lower():
                transit_insight = "Current Transits also suggest some challenges, so patience is advised."
            
            response += f"\n**🌍 Current Planetary Transits (Gochar):**\n"
            response += f"{transit_msg}\n"
            
    except Exception as e:
        print(f"Transit Error: {e}")

    response += f"\n**Timing:**\nYou are {upcoming_period}\n"
    if is_running:
        response += "Since a relevant planet is active, expect significant developments in this area.\n"
    elif transit_insight:
        response += f"{transit_insight}\n"

    return {
        "answer": response,
        "topic": detected_topic
    }
