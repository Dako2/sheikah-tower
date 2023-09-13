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
import csv
import numpy as np

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
                    place['wiki'] = info.strip()
                    db[name] = place
        except:
            pass
    return db

"""
museum.csv
museum.npy

"""
def gen_db_to_emb_csvformat(db):
    #pass it to csv 
    wiki_data = {key: value['wiki'] for key, value in db.items() if 'wiki' in value}
    save_to_csv_and_np(wiki_data) 

def chunk_string(s, token_count=50):
    # Tokenize the string
    tokens = s.split()
    chunks = [tokens[i:i + token_count] for i in range(0, len(tokens), token_count)]
    rows = [' '.join(chunk) for chunk in chunks]
    return rows

def save_to_csv_and_np(wiki_data):
    for key, value in wiki_data.items():
        filename = key + ".csv"
        rows = chunk_string(value)
        corpus = [row.strip() for row in rows]
        # Write to the CSV file
        with open('./db/'+filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in corpus:
                writer.writerow([row])
        print(f"Saved to {filename}")
        db_emb_path = './db/' + filename + '.npy'
        db_ebds = v.model.encode(corpus, convert_to_numpy=True)
        np.save(db_emb_path, db_ebds)

    return 

if __name__ == "__main__":
    db = query_interestpoints(lat = 37.417146,lng = -122.076376)
    a = gen_db_to_emb_csvformat(db)
