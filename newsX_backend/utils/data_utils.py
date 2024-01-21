import datetime
import hashlib
import re
from num2words import num2words
from googletrans import Translator

from newsX_backend.mappers.language_mapper import Languages, get_google_tanslate_langcode

CURRENT_YEAR = str(datetime.datetime.now().year)
REGEX_EXPRESSION = r'-?\d+(\,\d+)?(\.\d+)?' # Regex for numbers

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

def handle_number_preprocessing(text, language=Languages.ENGLISH, delimeter=' '):
    change_list = []
    index_offset = 0

    def convert_number_to_word(number_match):
        if type(number_match) is re.Match:
            nonlocal index_offset
            number = number_match.group(0)
            print('Number:: ', number)
            word = num2words(number)
            if language != Languages.ENGLISH:
                dest_lang_code = get_google_tanslate_langcode(language)
                translator = Translator(service_urls=['translate.googleapis.com'])
                translated_text = translator.translate(word, dest=dest_lang_code)
                word = translated_text.text
            word = word.replace(' ', delimeter)
            print('Word:: ', word)
            match_obj = {
                'number': number,
                'number_loc': [number_match.start(), number_match.end()],
                'word': word,
                'word_loc': [number_match.start()+index_offset, number_match.end()+index_offset+len(word)-len(str(number))]
            }
            index_offset += len(word)-len(str(number))
            change_list.append(match_obj)
        return word

    text = text.strip()
    print(text)
    text = re.sub(REGEX_EXPRESSION, convert_number_to_word, text)
    print(text)
    print(change_list)
    return text, change_list