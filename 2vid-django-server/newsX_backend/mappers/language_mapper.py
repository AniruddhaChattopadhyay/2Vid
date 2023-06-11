from googletrans import LANGCODES
from news_generation.models import Languages as LanguageModel

class Languages():
    ENGLISH = 'English'
    BENGALI = 'Bengali'
    HINDI = 'Hindi'
    TAMIL = 'Tamil'
    GUJARATI = 'Gujarati'
    TELUGU = 'Telugu'
    KANNADA = 'Kannada'
    SPANISH = 'Spanish'

DEFINED_LANGUAGES = [
    'English',
    'Bengali',
    'Hindi',
    'Tamil',
    'Gujarati',
    'Telugu',
    'Kannada',
    'Spanish'
    ]

ACTIVE_LANGUAGES = [
    Languages.ENGLISH,
    Languages.BENGALI,
    Languages.HINDI,
    Languages.KANNADA,
    Languages.TAMIL,
    Languages.SPANISH,
    Languages.TELUGU
]

transliterate_dict = {
    'Bengali': 'Bengali',
    'Hindi': 'Devanagari',
    'Tamil': 'Tamil',
    'Gujarati': 'Gujarati',
    'Telugu': 'Telugu',
    'Kannada': 'Kannada',
    'Spanish': 'Spanish',
    'English': 'English'
}

db_language_code_dict = {
    'Bengali': '001',
    'Hindi': '002',
    'Tamil': '003',
    'Gujarati': '004',
    'Telugu': '005',
    'Kannada': '006',
    'English': '007',
    'Spanish': '008'
}


google_translate_langcode_dict = {
    Languages.BENGALI: LANGCODES['bengali'],
    Languages.ENGLISH: LANGCODES['english'],
    Languages.HINDI: LANGCODES['hindi'],
    Languages.TAMIL: LANGCODES['tamil'],
    Languages.TELUGU: LANGCODES['telugu'],
    Languages.KANNADA: LANGCODES['kannada'],
    Languages.GUJARATI: LANGCODES['gujarati'],
    Languages.SPANISH: LANGCODES['spanish']
}

font_dict = {
    'Bengali': 'NotoSansBengali-Black.ttf',
    'English': 'NotoSans-Black.ttf',
    'Hindi': 'NotoSansDevanagari-Black.ttf',
    'Gujarati': 'NotoSansGujarati-Black.ttf',
    'Telugu': 'NotoSansTelugu-Black.ttf',
    'Kannada': 'NotoSansKannada-Black.ttf',
    'Tamil': 'NotoSansTamil-Black.ttf',
    'Spanish': 'NotoSans-Black.ttf'
}

def get_font_filename(language):
    return font_dict[language]

def get_language_mapper(language):
    return transliterate_dict[language]


def get_AI4Bharat_lang_code(language):
    lang_code_dict = {
        'Bengali': 'bn',
        'English': 'en',
        'Hindi': 'hi',
        'Telugu': 'te',
        'Gujarati': 'gu',
        'Kannada': 'kn',
        'Tamil': 'ta',
        'Spanish': 'es'
    }

    return lang_code_dict[language]


def get_bcp_47_lang_code(language):
    lang_code_dict = {
        'Bengali': 'bn-IN',
        'English': 'en-IN',
        'Hindi': 'hi-IN',
        'Gujarati': 'gu',
        'Telugu': 'te',
        'Tamil': 'ta-IN',
        'Kannada': 'kn',
        'Spanish': 'es-ES'
    }
    return lang_code_dict[language]

def lang_detect_mapping(lang_code):
    lang_code_dict = {
        "bn":"Bengali",
        "en":"English",
        "hi":"Hindi",
        "gu":"Gujarati",
        "te":"Telugu",
        "ta":"Tamil",
        "kn":"Kannada",
        "es":"Spanish"
    }
    return(lang_code_dict[lang_code])


def get_google_tanslate_langcode(language):
    if language in DEFINED_LANGUAGES:
        return google_translate_langcode_dict[language]
    else:
        raise Exception('get_google_tanslate_langcode :: Language not supported :: language='+language)
    
