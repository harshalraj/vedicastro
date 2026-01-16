from chat_logic import process_question
from astrology_utils import calculate_chart

# Test Data
dob = "1990-12-08"
tob = "22:35"
lat = 25.77
lon = 85.87
tz = 5.5

print("Calculating Chart...")
chart_data = calculate_chart("Test User", dob, tob, lat, lon, tz)

print("\n--- Testing Career Question ---")
q1 = "How is my career?"
res1 = process_question(q1, chart_data)
print(f"Q: {q1}")
print(f"Topic: {res1['topic']}")
print(f"Answer:\n{res1['answer']}")

print("\n--- Testing Marriage Question ---")
q2 = "When will I get married?"
res2 = process_question(q2, chart_data)
print(f"Q: {q2}")
print(f"Topic: {res2['topic']}")
print(f"Answer:\n{res2['answer']}")
