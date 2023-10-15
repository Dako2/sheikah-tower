import re
import datetime
# from datetimerange import DateTimeRange
from dateparser.search import search_dates

def extract_time(sentence):
    sentence_dates = search_dates(sentence)
    # Dedup
    sentence_dates = list(dict.fromkeys(sentence_dates))
    print(sentence_dates)
    return sentence_dates


if __name__ == "__main__":
    print(extract_time("What are the events today?"))
    print(extract_time("What are the events in 1 hour?"))
    print(extract_time("What were the events at 2pm today?"))
    print(extract_time("What were the events at 2pm tmr?"))