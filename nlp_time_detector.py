import re

#TODO
def extract_time(sentence):
    # Define regular expressions to match different time formats
    time_regexes = [
        r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?',  # 12-hour format
        r'\d{1,2}\s*(?:AM|PM|am|pm)',  # 12-hour format without colon
        r'\d{1,2}\.\d{2}',  # Decimal format
        r'\d{1,2}:\d{2}',  # 24-hour format
    ]
    
    # Combine all regexes into a single pattern
    pattern = '|'.join(time_regexes)
    
    # Search for the pattern in the sentence
    match = re.search(pattern, sentence)
    
    # If a match is found, return the matched string
    if match:
        return match.group(0)
    
    # Otherwise, return None
    return None
