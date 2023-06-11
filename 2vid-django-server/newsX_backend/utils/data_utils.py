import datetime
import hashlib

CURRENT_YEAR = str(datetime.datetime.now().year)

def hash_SHA256(text:str):
    result = hashlib.sha256(text.strip().encode('utf-8'))
    return result.hexdigest()

def format_dateTime_from_inshorts(date:str, time:str):
    obj = datetime.datetime.strptime(date.strip() + ' ' + CURRENT_YEAR + ' ' + time.upper().strip(), '%d %b %Y %I:%M %p')
    date_formatted = obj.strftime('%Y-%m-%d')
    time_formatted = obj.strftime('%H:%M:%S')
    timestamp = obj.timestamp
    return date_formatted, time_formatted, timestamp

def dateTime_now():
    obj = datetime.datetime.now()
    date_formatted = obj.strftime('%Y-%m-%d')
    time_formatted = obj.strftime('%H:%M:%S')
    timestamp = obj.timestamp
    return date_formatted, time_formatted, timestamp

def create_raw_news_id(article:str, date_formatted:str, time_formatted:str):
    id = hash_SHA256(article.strip()+ '-' + date_formatted.strip() + '-' + time_formatted.strip())
    return id

def create_raw_news_id_from_url(url):
    id = hash_SHA256(str(url))
    return id

def create_translated_news_id(t_id:str, l_id:str):
    id = hash_SHA256( t_id.strip()+ '-' + l_id.strip())
    return id

def create_video_links_id(v_id:str, l_id:str):
    id = hash_SHA256( v_id.strip()+ '-' + l_id.strip())
    return id