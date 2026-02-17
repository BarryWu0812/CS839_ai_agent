import argparse
import sys
import os
import requests

# OpenTripMap API configuration
# Get a free key at https://opentripmap.io/
API_KEY = os.getenv("OTM_API_KEY", "5ae2e3f221c38a28845f05b6") # Default key for demo

def get_places(city_name):
    """Fetch real attractions using OpenTripMap API."""
    try:
        # 1. Get coordinates for the city
        geo_url = f"https://api.opentripmap.com/0.1/en/places/geoname?name={city_name}&apikey={API_KEY}"
        geo_resp = requests.get(geo_url, timeout=5)
        geo_data = geo_resp.json()
        
        if "lat" not in geo_data:
            return None

        lat, lon = geo_data["lat"], geo_data["lon"]

        # 2. Get interesting places within 10km
        list_url = f"https://api.opentripmap.com/0.1/en/places/radius?radius=10000&lon={lon}&lat={lat}&kinds=interesting_places&format=json&limit=50&apikey={API_KEY}"
        list_resp = requests.get(list_url, timeout=5)
        list_data = list_resp.json()
        
        # Filter names and remove duplicates
        names = list(dict.fromkeys([p["name"] for p in list_data if p.get("name")]))
        return names if len(names) > 2 else None
    except:
        return None

def generate_markdown(city, days, places):
    is_fallback = False
    if not places:
        is_fallback = True
        places = [
            "Central Historical Square", "Local Art Museum", "City Botanical Garden",
            "Main Shopping District", "Panoramic Viewpoint", "Historic Cathedral",
            "Local Food Market", "Science & Technology Center", "Riverside Walk"
        ]

    output = f"# Itinerary for {city.title()}\n\n"
    output += f"**Duration:** {days} days\n\n"
    
    spots_per_day = 3
    for day in range(1, days + 1):
        output += f"## Day {day}\n"
        
        # Select unique spots for the day
        start_idx = ((day - 1) * spots_per_day) % len(places)
        for i in range(spots_per_day):
            spot = places[(start_idx + i) % len(places)]
            label = " (example)" if is_fallback else ""
            output += f"- {spot}{label}\n"
        output += "\n"
    
    return output

def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown travel itinerary.")
    parser.add_argument("--city", required=True, help="Target city")
    parser.add_argument("--days", type=int, required=True, help="Number of days")
    args = parser.parse_args()

    if args.days < 1:
        print("Error: Days must be at least 1.")
        sys.exit(1)

    places = get_places(args.city)
    print(generate_markdown(args.city, args.days, places))

if __name__ == "__main__":
    main()
