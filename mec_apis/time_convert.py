from datetime import datetime

# Given timestamp values
timestamp = {'nanoSeconds': 0, 'seconds': 1693526572}

# Convert seconds to a datetime object
absolute_time = datetime.utcfromtimestamp(timestamp['seconds'])

# Print the absolute time
print("Absolute Time:", absolute_time) # Absolute Time: 2023-09-01 00:02:52
