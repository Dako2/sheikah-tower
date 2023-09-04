import json

# Specify the path to the JSON file
input_file = "monaco_coordinates.json"

# Read the JSON data from the file
with open(input_file, "r") as json_file:
    coordinates_data = json.load(json_file)

# Now you can work with the coordinates_data dictionary
print(coordinates_data)
