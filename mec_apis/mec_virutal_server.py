"""
Virtual MEC server for demo purposes.
"""

import json
import time
from flask import Flask, jsonify
import socket

app = Flask(__name__)

class JsonlIterator:
    def __init__(self, filename="api_responses.jsonl"):
        with open(filename, 'r') as f:
            self.lines = f.readlines()
        self.index = 0

    def get_next(self):
        """
        Returns the current line in JSON format and moves to the next line.
        """
        data = json.loads(self.lines[self.index])
        self.index = (self.index + 1) % len(self.lines)
        return data

class VirtualMEC:
    def __init__(self, filename='./mec_apis/api_responses.jsonl'):
        self.jsonl_iter = JsonlIterator(filename)

    def _fetch_data(self):
        """
        Fetch the next set of data from the iterator.
        """
        return self.jsonl_iter.get_next()['userList']['user'][0]

    def fetch_user_coordinates(self):
        """
        Virtually fetch user coordinates.
        """
        data = self._fetch_data()
        location_info = data['locationInfo']
        return location_info['latitude'][0], location_info['longitude'][0], location_info['timestamp']['seconds']

    def fetch_user_coordinates_zoneid_cellid(self):
        """
        Virtually fetch user coordinates, zone ID, and cell ID.
        """
        data = self._fetch_data()
        location_info = data['locationInfo']
        latitude = location_info['latitude'][0]
        longitude = location_info['longitude'][0]
        timestamp_seconds = location_info['timestamp']['seconds']
        cellid = data['accessPointId']
        zoneid = data['zoneId']

        print(latitude, longitude, timestamp_seconds, cellid, zoneid)
        return latitude, longitude, timestamp_seconds, cellid, zoneid


# Initialize the VirtualMEC
v = VirtualMEC()

"""
def broadcast_location(latitude, longitude):
    BROADCAST_IP = '255.255.255.255'
    PORT = 12345  # Choose an appropriate port
    message = f"{latitude},{longitude}".encode('utf-8')

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.sendto(message, (BROADCAST_IP, PORT))
    sock.close()

@app.route('/get_location', methods=['GET'])
def get_location():
    latitude, longitude, timestamp_seconds, cellid, zoneid = v.fetch_user_coordinates_zoneid_cellid()
    return jsonify({
        'latitude': latitude,
        'longitude': longitude,
        'timestamp_seconds': timestamp_seconds,
        'cellid': cellid,
        'zoneid': zoneid
    })

@app.route('/broadcast_location', methods=['GET'])
def broadcast():
    latitude, longitude, _, _, _ = v.fetch_user_coordinates_zoneid_cellid()
    broadcast_location(latitude, longitude)
    return jsonify({
        'status': 'broadcasted',
        'latitude': latitude,
        'longitude': longitude
    })

if __name__ == "__main__":
    app.run('0.0.0.0',port = 9091, debug=True)

"""