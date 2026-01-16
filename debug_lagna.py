from astrology_utils import calculate_chart
import json

# Input: Harshal, 8th Dec 1990, 22:35, Samastipur Bihar
# Samastipur Lat/Lon: 25.86, 85.78 (Approx from prev search)
# Timezone: 5.5

name = "Harshal"
dob = "1990-12-08"
tob = "22:35"
lat = 25.77  # Using one of the results
lon = 85.87
tz = 5.5

print(f"Calculating for: {name}, {dob} {tob}, {lat}, {lon}")
data = calculate_chart(name, dob, tob, lat, lon, tz)

print("Ascendant:", data['details']['Ascendant'])
print("Moon Sign:", data['details']['Moon Sign'])
print("Planetary Details:")
for planet in data['planetary_details']:
    print(f"{planet['Planet']}: {planet['Nakshatra']}")

print("\nVimshottari Dasha:")
for dasha in data['vimshottari']:
    print(f"{dasha['Lord']}: {dasha['Start']} to {dasha['End']} ({dasha['Duration']})")
