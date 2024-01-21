import os
import json

import openai
from dotenv import load_dotenv
from googletrans import Translator, LANGCODES

from newsX_backend.utils.directory_helper import get_news_path
from newsX_backend.mappers.language_mapper import Languages, DEFINED_LANGUAGES, get_google_tanslate_langcode, db_language_code_dict
from newsX_backend.utils.db_utils import get_raw_news_by_id, get_language_by_title, insert_translated_news
from newsX_backend.utils.data_utils import create_translated_news_id
from newsX_backend.enums.model_enums import RawNewsEnum, TranslatedArticlesEnum
from newsX_backend.models.util_models import NewsIdResponse
from news_generation.models import Languages as LanguageModel

load_dotenv()


TRANSLATION_METHODS = ['GOOGLE', 'CHATGPT']

def translate_to_multiple_languages(news_id_list, languages, method='GOOGLE'):
    news_list = get_raw_news_by_id(news_id_list)
    print(news_list)
    print(languages)
    translated_ids = set()
    for news in news_list:
        for language in languages:
            status_object = translate_news(news,language)
            translated_ids.add(status_object[TranslatedArticlesEnum.t_id.value])
    return NewsIdResponse(list(translated_ids))

def translate_news(news_dict, language, method='GOOGLE'):
    if method not in TRANSLATION_METHODS:
        print('translate_news() :: Method not supported :: method='+method + '\nMethods supported = '+ TRANSLATION_METHODS +' \nReverting to default method "GOOGLE"')
        method = 'GOOGLE'

    if method == 'GOOGLE':
        return google_translate(news_dict, language)
    elif method == 'CHATGPT':
        return gpt_translate(news_dict, language)

def gpt_translate(news_dict, translation_language):
    print("initiating translation...")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt_article = "Translate the following text to " + \
        translation_language+" entirely there should not be any English text and make sure the numbers are in text format in " + \
        translation_language + " and not in digits : "+news_dict['article']
    prompt_title = "Translate the following text to " + \
        translation_language+": "+news_dict['title']
    completion_article = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
              "content": prompt_article
             }
        ]
    )

    completion_title = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt_title
            }
        ]
    )

    print(completion_article)
    article_translated = completion_article.choices[0].message.content

    print(completion_title)
    title_translated = completion_title.choices[0].message.content

    print('Translation completed for ' + translation_language)

    return write_translated_news_to_db(news_dict, article_translated.text, title_translated.text, translation_language)
    # write_translation_to_json(news_dict, article_translated, title_translated, translation_language)


def google_translate(news_dict, language):
    if language not in DEFINED_LANGUAGES:
        raise Exception('google_translate() :: Language not supported :: language='+language)
    
    article_text = news_dict['article']
    title_text = news_dict['title']
    lang_code = get_google_tanslate_langcode(language)
    translator = Translator(service_urls=['translate.googleapis.com'])

    article_translation = translator.translate(article_text, dest=lang_code)
    title_translation = translator.translate(title_text, dest=lang_code)

    # print(article_translation, title_translation)
    print('Translation completed for ' + language)

    return write_translated_news_to_db(news_dict, article_translation.text, title_translation.text, language)
    # write_translation_to_json(news_dict, article_translation.text, title_translation.text, language)


def write_translated_news_to_db(news_dict,article_translated,title_translated, translation_language):
    l_id = db_language_code_dict[translation_language]

    id = create_translated_news_id( news_dict[RawNewsEnum.id.value], l_id)

    language_object = LanguageModel(**get_language_by_title(translation_language))
    
    translated_news_dict = {
        TranslatedArticlesEnum.id.value : id,
        TranslatedArticlesEnum.t_id.value : news_dict[RawNewsEnum.id.value],
        TranslatedArticlesEnum.translated_article.value : article_translated,
        TranslatedArticlesEnum.translated_title.value : title_translated,
        TranslatedArticlesEnum.language.value : language_object
    }
    write_status = insert_translated_news(translated_news_dict)
    return {TranslatedArticlesEnum.t_id.value: translated_news_dict[TranslatedArticlesEnum.t_id.value], 'insertion': write_status, 'translation_language': translation_language}


def write_translation_to_json(news_dict,article_translated,title_translated, translation_language):
    # decoding the translation from unicode
    news_path = get_news_path(news_dict['id'])
    translation_json_file = os.path.join(news_path, 'translated_result.json')
    translated_dict = dict()

    message_dict = {'article_translated': article_translated,
                    'title_translated': title_translated,
                    'translation_language': translation_language
                    }

    if not os.path.exists(translation_json_file):
        translated_dict = {'id': news_dict['id'],
                           translation_language: message_dict
                           }
    else:
        f = open(translation_json_file)
        translated_dict = json.load(f)
        translated_dict[translation_language] = message_dict
        f.close()

    f = open(translation_json_file, 'w', encoding='utf-8')
    json.dump(translated_dict, f, indent=4)
    f.close()
