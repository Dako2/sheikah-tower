# todo this script failed. Therefore added some manual inputs in the json file/db
import requests
import json

def fetch_coordinates(location):
    params = f"q={location}&country=Monaco&format=json"
    api_url = f"https://nominatim.openstreetmap.org/search?{params}"
    
    response = requests.get(api_url)
    #print(response)
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    return print("Failed to retreive the coordinates.")

"""
# List of historical and sightseeing spots in Monaco
monaco_spots = [
    "Prince's Palace of Monaco",
    "Oceanographic Museum of Monaco"
    # "Monte Carlo Casino",
    # "Monaco-Ville",
    # "Port Hercules",
    # "Cathedral of Our Lady Immaculate",
    # "Saint-Martin Gardens",
    # "Japanese Garden",
    # Add more spots as needed
]

# Fetch coordinates for each spot
coordinates_data = {}
for spot in monaco_spots:
    coordinates = fetch_coordinates(spot)
    if coordinates:
        coordinates_data[spot] = {
            "latitude": coordinates[0],
            "longitude": coordinates[1]
        }

# Save coordinates data to a JSON file
output_file = "monaco_coordinates.json"
with open(output_file, "w") as json_file:
    json.dump(coordinates_data, json_file, indent=4)

print(f"Coordinates data saved to '{output_file}'")
"""