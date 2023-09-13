import requests
import json
from environment import GOOGLE_MAP_API

def get_nearby_places(api_key, latitude, longitude, radius=1000, keyword=None):
    """Fetch nearby places using Google Places API.
    
    Parameters:
    - api_key (str): Your Google Places API key.
    - latitude (float): Latitude of the location.
    - longitude (float): Longitude of the location.
    - radius (int, optional): Search radius in meters. Default is 1000 meters.
    - keyword (str, optional): A term to be matched against all available fields, including but not limited to name, type, and address.

    Returns:
    - dict: Parsed JSON response from the Google Places API.
    """
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'key': api_key
    }
    
    if keyword:
        params['keyword'] = keyword

    response = requests.get(endpoint_url, params=params)
    return response.json()

if __name__ == "__main__":

    # Sample location: New York City (40.730610, -73.935242)
    lat, lng = 37.417146,-122.076376
    
    results = get_nearby_places(GOOGLE_MAP_API, lat, lng)
    for place in results.get('results', []):
        name = place.get('name')
        place_lat = place.get('geometry', {}).get('location', {}).get('lat')
        place_lng = place.get('geometry', {}).get('location', {}).get('lng')
        rating = place.get('rating', 'N/A')  # rating of the place out of 5
        user_ratings_total = place.get('user_ratings_total', 'N/A')  # total number of ratings
        
        print(f"{name}: ({place_lat}, {place_lng}), Rating: {rating}, Total Ratings: {user_ratings_total}")
