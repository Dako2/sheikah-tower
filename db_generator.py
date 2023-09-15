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
import os 

v = VecDataBase(update_db = False)

def get_nearby_places(latitude, longitude, radius=5000, keyword=None):
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
    #endpoint_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'key': GOOGLE_MAP_API
    }
    
    if keyword:
        params['keyword'] = keyword

    response = requests.get(endpoint_url, params=params)
    print(response.json())
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
    
def query_interestpoints(lat = 37.417146,lng = -122.076376, radius = 500, keyword = None):
    results = get_nearby_places(lat, lng, radius, keyword)
    db = {}
    for place in results.get('results', []):
        name = place.get('name')
        place_lat = place.get('geometry', {}).get('location', {}).get('lat')
        place_lng = place.get('geometry', {}).get('location', {}).get('lng')
        rating = place.get('rating', 'N/A')  # rating of the place out of 5
        user_ratings_total = place.get('user_ratings_total', 'N/A')  # total number of ratings
        
        print(f"{name}: ({place_lat}, {place_lng}), Rating: {rating}, Total Ratings: {user_ratings_total}")
        try:
            if int(user_ratings_total) > 400:
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
def gen_db_to_emb_csvformat(db, cellid): #combine wiki, web page data
    #pass it to csv
    wiki_data = {key: value for key, value in db.items() if 'wiki' in value}
    combined_data = wiki_data 
    csv_path = save_to_csv_and_np(combined_data, cellid)

def save_to_json(new_place, jsonfile = './db/monaco_coordinates.json'):
    if not os.path.exists(jsonfile):
        with open(jsonfile, 'w') as file:
            json.dump({}, file)
        print(f"{jsonfile} created.")

    with open(jsonfile, 'r') as file:
        data = json.load(file)
    # Check if the place already exists in data and add if not
    for place_name, place_data in new_place.items():
        if place_name not in data:
            data[place_name] = place_data
            print(f"Added {place_name} to data.")
        else:
            data[place_name] = place_data
            print(f"{place_name} already exists in data.")

    # Save the updated data back to the file
    with open(jsonfile, 'w') as file:
        json.dump(data, file, indent=4)
        
def chunk_string(s, token_count=50):
    # Tokenize the string
    tokens = s.split()
    chunks = [tokens[i:i + token_count] for i in range(0, len(tokens), token_count)]
    rows = [' '.join(chunk) for chunk in chunks]
    return rows

def save_to_csv_and_np(combined_data, cellid):
    jsonfile = 'monoco_zone_cellid_places.json'
    if not os.path.exists(jsonfile):
        with open(jsonfile, 'w') as file:
            json.dump({}, file)
        print(f"{jsonfile} created.")

    with open(jsonfile, 'r') as file:
        db_json = json.load(file)

    db_folder_path = './db/'
    for key, value in combined_data.items():
        filename = key + ".csv"
        rows = chunk_string(value['wiki'])
        corpus = [row.strip() for row in rows]
        csv_path = './db/csv/'+filename
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in corpus:
                writer.writerow([row])
        print(f"Saved to {filename}")
        
        db_emb_path = './db/' + filename + '.npy'
        db_ebds = v.model.encode(corpus, convert_to_numpy=True)
        np.save(db_emb_path, db_ebds)

        name = value.get('name')
        place_lat = value.get('geometry', {}).get('location', {}).get('lat')
        place_lng = value.get('geometry', {}).get('location', {}).get('lng')

        # Ensure the path and get a reference to the 'places' dictionary
        places_dict = ensure_path(db_json, [cellid[0], cellid[1], 'places'])

        # Insert the new place into the 'places' dictionary
        places_dict[name] = {"latitude": place_lat, "longitude": place_lng, "db_path": csv_path}

    with open(jsonfile, 'w') as file:
        json.dump(db_json, file, indent=4)


def ensure_path(d, keys):
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    return d.setdefault(keys[-1], {})


if __name__ == "__main__":
    #43.7410606,7.4208206
    import glob
    zone_dic = {}
    for fn in glob.glob("./db/zones/*.json"):
        with open(fn, 'r') as file:
            zone_info = json.load(file)
            zone_dic[zone_info['accessPointList']['zoneId']] = zone_info['accessPointList']['accessPoint']
    for zoneid, ap_list in zone_dic.items():
        for ap in ap_list:
            cellid = ap['accessPointId']
            lat = ap['locationInfo']['latitude'][0]
            lng = ap['locationInfo']['longitude'][0]
            db = query_interestpoints(lat = lat, lng = lng, radius = 250, keyword=None)
            gen_db_to_emb_csvformat(db, (zoneid,cellid))