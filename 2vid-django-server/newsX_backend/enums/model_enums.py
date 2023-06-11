from enum import Enum

class RawNewsEnum(Enum):
    id = 'id'
    article = 'article'
    title = 'title'
    date = 'date'
    time = 'time'
    source_url = 'source_url'
    source = 'source'
    original_source = 'original_source'
    image_url = 'image_url'
    author = 'author'
    category = 'category'

class TranslatedArticlesEnum(Enum):

    id = 'id'
    t_id = 't_id'
    translated_article = 'translated_article'
    translated_title = 'translated_title'
    language = 'language'

class LanguagesEnum(Enum):

    l_id = 'l_id'
    lang = 'lang'
    google_lang_code = 'google_lang_code'
    ai4b_lang_code = 'ai4b_lang_code'
    aks_lang_code = 'aks_lang_code'
    bcp_47_lang_code = 'bcp_47_lang_code'
    is_active = 'is_active'

class VideoLinksEnum(Enum):

    id = 'id'
    v_id = 'v_id'
    video_url = 'video_url'
    language = 'language'

class TemporaryEnum(Enum):
    from_forms = 'Video from google forms'