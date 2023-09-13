"""
input geo location 
output interested places and wiki page (webpage) info
filter functions to highlight interest and increase usefulness
"""
import requests
import json
from environment import GOOGLE_MAP_API
import wikipedia
from VecDB import VecDataBase
import time

v = VecDataBase(update_db = False)

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

def get_info_from_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=25)
        return summary
    except wikipedia.DisambiguationError as e:
        # Handle disambiguation pages
        print(f"Multiple matches found for {query}. You might be interested in:")
        for option in e.options:
            print(option)
        return None

def get_info_from_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=25)
        return summary
    except wikipedia.DisambiguationError as e:
        # Handle disambiguation pages
        print(f"Multiple matches found for {query}. You might be interested in:")
        for option in e.options:
            print(option)
        return None
    
def query_interestpoints(lat = 37.417146,lng = -122.076376):
    results = get_nearby_places(GOOGLE_MAP_API, lat, lng)
    db = {}
    for place in results.get('results', []):
        name = place.get('name')
        place_lat = place.get('geometry', {}).get('location', {}).get('lat')
        place_lng = place.get('geometry', {}).get('location', {}).get('lng')
        rating = place.get('rating', 'N/A')  # rating of the place out of 5
        user_ratings_total = place.get('user_ratings_total', 'N/A')  # total number of ratings
        
        print(f"{name}: ({place_lat}, {place_lng}), Rating: {rating}, Total Ratings: {user_ratings_total}")
        try:
            if int(user_ratings_total) > 5000:
                query = name
                info = get_info_from_wikipedia(query)
                if info:
                    print(info)
                    place['wiki'] = info
                    db[name] = place
        except:
            pass

    return db

def wiki_gen_db_to_emb_csvformat(db):
    #pass it to csv 
    wiki_data = {key: value['wiki'] for key, value in db.items() if 'wiki' in value}
    wiki_embeddings = {key: v.model.encode(value.strip(), convert_to_numpy=True) for key, value in wiki_data.items()}
    print(wiki_embeddings)
    save_to_csv_and_np(wiki_data, wiki_embeddings)
    return wiki_embeddings

def save_to_csv_and_np(wiki_data, wiki_embeddings):

    return 

if __name__ == "__main__":
    db = query_interestpoints(lat = 37.417146,lng = -122.076376)
    a = gen_db_to_emb_csvformat(db)
