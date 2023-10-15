import os
import glob
import json
import csv

trans = str.maketrans("", "", "{}")

# Get all csv files in the ./csv/ directory
fns = glob.glob("./sanjose/museum.csv")

# Loop through each file
for fn in fns:
    res = {}
    
    # Open and read CSV file
    with open(fn, 'r', newline='') as f:  
        reader = csv.reader(f)
        
        # Enumerate through rows, creating a dictionary entry for each
        for i, row in enumerate(reader):
            cleaned_row = [field.translate(trans) for field in row]
            if cleaned_row:
                res['id'+str(i)] = ''.join(cleaned_row)
    
    # Create JSON filename, change extension from .csv to .json
    json_fn = os.path.splitext(fn)[0] + '.json'
    
    # Write dictionary to JSON file
    with open(json_fn, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
