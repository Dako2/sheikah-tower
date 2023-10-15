import re
import datetime
# from datetimerange import DateTimeRange
from dateparser.search import search_dates

def extract_time(sentence):
    sentence_dates = search_dates(sentence)
    if sentence_dates is None:
        return None
    
    return sentence_dates


if __name__ == "__main__":
    print(extract_time("What are the events today?"))
    print(extract_time("What are the events in 1 hour?"))
    print(extract_time("What were the events at 2pm today?"))
    print(extract_time("What were the events at 2pm tmr?"))
    print(extract_time("What are events about Sonic at 1pm Oct 17"))
    print(extract_time("Who is David?"))