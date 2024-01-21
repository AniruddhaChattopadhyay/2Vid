from newsX_backend.enums.model_enums import RawNewsEnum,TranslatedArticlesEnum
from newsX_backend.mappers.language_mapper import ACTIVE_LANGUAGES, DEFINED_LANGUAGES, Languages,db_language_code_dict,lang_detect_mapping
from newsX_backend.utils.data_utils import create_raw_news_id
from newsX_backend.utils.db_utils import get_translated_article
from news_generation.services.translation.translateService import translate_news
from newsX_backend.utils.db_utils import insert_raw_news
from newsX_backend.utils.db_utils import insert_raw_news
from news_generation.services.item_config.item_services import save_item_config
from datetime import datetime
from langdetect import detect
from newsX_backend.models.util_models import NewsIdResponse
from newsX_backend.utils.data_utils import dateTime_now




def create_raw_from_script(data):
    '''
    {
        script: 'text'
        email: 'mail-id'
        AIAudioFlag : 'AI Voice' or 'Recorded Voice'
        audioURL: someURL
        languages: [languages in present in DEFINED_LANGUAGES]
        isBgm: TRUE/FALSE
    }
    '''
    script_lang = lang_detect_mapping(detect(data['script']))
    date, time, timestamp = dateTime_now()

    if script_lang in DEFINED_LANGUAGES and len(data['script'])>100:
        if script_lang is not Languages.ENGLISH:
            script = str(date['script']).replace('\n','')
            news_id = create_raw_news_id(
                article=script,
                date_formatted=date,
                time_formatted=time,
            )
            bgm_flag = str(data['isBgm'])
            if data['AIAudioFlag'] == 'AI Voice':
                image_url = None
            else:
                image_url = data['audioURL']
            news_dict = {
                    RawNewsEnum.id.value: news_id,
                    RawNewsEnum.article.value: script,
                    RawNewsEnum.title.value: 'Video from google forms',
                    RawNewsEnum.date.value: date,
                    RawNewsEnum.time.value: time,
                    RawNewsEnum.source.value: bgm_flag,
                    RawNewsEnum.source_url.value: "",
                    RawNewsEnum.original_source.value: script_lang,
                    RawNewsEnum.image_url.value: image_url,
                    RawNewsEnum.author.value: data['email'],
                    RawNewsEnum.category.value: 'all',
            }
            pass
            
            translated_dict = translate_news(news_dict,Languages.ENGLISH)
            l_id = db_language_code_dict[Languages.ENGLISH]
            t_id = translated_dict['TranslatedArticlesEnum.t_id.value']
            translation_model = get_translated_article(t_id,l_id)
            news_dict['article'] = translation_model[TranslatedArticlesEnum.translated_article.value]
            insert_raw_news(news_dict)
            save_item_config(news_id,data)
            translation_languages = data['languages'].remove(script_lang)
            return (NewsIdResponse(all_news_ids=[news_id], news_ids_inserted=None) , list(set(translation_languages) & set(ACTIVE_LANGUAGES)))

        else:

            script = data['script'].replace('\n','')
            news_id = create_raw_news_id(
                article=script,
                date_formatted=date,
                time_formatted=time,
            )
            if data['AIAudioFlag'] == 'AI Voice':
                image_url = None
            else:
                image_url = data['audioURL']
            news_dict = {
                    RawNewsEnum.id.value: news_id,
                    RawNewsEnum.article.value: script,
                    RawNewsEnum.title.value: 'Video from google forms',
                    RawNewsEnum.date.value: date,
                    RawNewsEnum.time.value: time,
                    RawNewsEnum.source.value: "",
                    RawNewsEnum.source_url.value: "",
                    RawNewsEnum.original_source.value: script_lang,
                    RawNewsEnum.image_url.value: image_url,
                    RawNewsEnum.author.value: data['email'],
                    RawNewsEnum.category.value: 'all',
            }

            insert_raw_news(news_dict)
            save_item_config(news_id,data)
            return (NewsIdResponse(all_news_ids=[news_id], news_ids_inserted=None) , list(set(data['languages']) & set(ACTIVE_LANGUAGES)))
    else:
        pass
