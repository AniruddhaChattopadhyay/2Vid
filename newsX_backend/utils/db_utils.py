import configparser
from news_generation.models import RawNews
from newsX_backend.enums.model_enums import (
    RawNewsEnum,
    VideoLinksEnum,
    TranslatedArticlesEnum,
    ItemConfigEnum
)
from newsX_backend.utils.data_utils import create_raw_news_id, create_raw_news_id_from_url
from news_generation.models import (
    Languages as LanguageModel,
    RawNews,
    TranslatedArticles,
    VideoLinks,
    ItemConfig
)
from newsX_backend.mappers.language_mapper import *

config = configparser.ConfigParser()
config.read(".config")

INSERT_NEWS_TO_DB_FLAG = config.getboolean("DB", "INSERT_NEWS_TO_DB_FLAG")


#  ---------- FETCH ---------------------------------------------------------------------------------------
#  --------------------------------------------------------------------------------------------------------

def get_raw_news_by_id(news_id_list: list):
    return RawNews.objects.filter(pk__in=news_id_list).values()


def get_language_by_title(language):
    l_id = db_language_code_dict[language]
    return get_language_by_l_id(l_id)


def get_language_by_l_id(l_id):
    return LanguageModel.objects.filter(pk=l_id).values()[0]


def get_translated_article(t_id, l_id):
    return TranslatedArticles.objects.filter(t_id=t_id, language_id=l_id).values()[0]


def get_video_links(v_id, l_id=None):
    if l_id is None:
        return VideoLinks.objects.filter(v_id=v_id).values()
    else:
        return VideoLinks.objects.filter(v_id=v_id, language_id=l_id).values()[0]

def get_item_config(id):
    return ItemConfig.objects.get(id=id).__dict__


#  ---------- INSERTION -----------------------------------------------------------------------------------
#  --------------------------------------------------------------------------------------------------------

def insert_raw_news(news_dict: dict):
    news_id = news_dict[RawNewsEnum.id.value]
    if news_id != create_raw_news_id(
        article=news_dict[RawNewsEnum.article.value],
        date_formatted=news_dict[RawNewsEnum.date.value],
        time_formatted=news_dict[RawNewsEnum.time.value],
    ) and news_id != create_raw_news_id_from_url(news_dict[RawNewsEnum.source_url.value]):
        raise Exception("insert_raw_news :: Id not not in proper format")

    if not INSERT_NEWS_TO_DB_FLAG:
        return False

    if RawNews.objects.filter(id=news_id).exists():
        print("*** RawNews already exists in DB")
        return False
    else:
        news = RawNews(**news_dict)
        try:
            print("Saving News")
            news.save()
            return True
        except Exception as e:
            print("** ERROR ** :: insert_raw_news",e, news_dict)
            return False


def insert_translated_news(translated_news_dict):
    if not INSERT_NEWS_TO_DB_FLAG:
        return False
    if TranslatedArticles.objects.filter(
        t_id=translated_news_dict[TranslatedArticlesEnum.t_id.value],
        language=translated_news_dict[TranslatedArticlesEnum.language.value],
    ).exists():
        print("*** TranslatedNews already exists in DB")
        return False
    else:
        try:
            translated_article_object = TranslatedArticles(**translated_news_dict)
            translated_article_object.save()
            return True
        except Exception as error:
            print(error)
            return False


def insert_video_link(video_link_dict):
    if not INSERT_NEWS_TO_DB_FLAG:
        return False

    if VideoLinks.objects.filter(
        v_id=video_link_dict[VideoLinksEnum.v_id.value],
        language=video_link_dict[VideoLinksEnum.language.value],
    ).exists():
        print("*** VideoLink already exists in DB :: Overwriting Video Link")
    try:
        video_links_object = VideoLinks(**video_link_dict)
        video_links_object.save()
    except Exception as error:
        print(error)
        return False

def insert_item_config(item_config_dict):
    if not INSERT_NEWS_TO_DB_FLAG:
        return False
    
    if not RawNews.objects.filter(
        id=item_config_dict[ItemConfigEnum.id.value]
    ).exists() :
        print("*** RawNews doesn't  exists in DB :: Skipping Item Config")
        return False
    
    if ItemConfig.objects.filter(
        id=item_config_dict[ItemConfigEnum.id.value]
    ).exists():
        print("*** ItemConfig already exists in DB :: Overwriting Item Config")

    try:
        item_config_dict = ItemConfig(**item_config_dict)
        item_config_dict.save()
        return True
    except Exception as error:
        print(error)
        return False


#  ---------- UPDATE --------------------------------------------------------------------------------------
#  --------------------------------------------------------------------------------------------------------

def update_item_config(item_config_dict:dict):
    if not INSERT_NEWS_TO_DB_FLAG:
        return False
    
    if ItemConfigEnum.id.value not in item_config_dict.keys():
        print("*** ItemConfig object doesn't have id :: Skipping Item Config Update")
        return False

    if not RawNews.objects.filter(
        id=item_config_dict[ItemConfigEnum.id.value]
    ).exists() :
        print("*** RawNews doesn't  exists in DB :: Skipping Item Config")
        return False

    if not ItemConfig.objects.filter(
        id=item_config_dict[ItemConfigEnum.id.value]
    ).exists():
        return insert_item_config(item_config_dict)
    else:
        try:
            current_item = ItemConfig.objects.get(id=item_config_dict[ItemConfigEnum.id.value])
            item_dict = current_item.__dict__
            for key in item_config_dict.keys():
                item_dict[key] = item_config_dict[key]
            
            current_item.email_list = item_dict[ItemConfigEnum.email_list.value]
            current_item.is_bgm_enabled = item_dict[ItemConfigEnum.is_bgm_enabled.value]
            current_item.save()
            return True
        except Exception as error:
            print(error)
            return False


def CAUTION_THIS_WILL_BREAK_STUFF__modify_language_model_objects():
    objects = []
    for language in DEFINED_LANGUAGES:
        if LanguageModel.objects.filter(l_id=db_language_code_dict[language]).exists():
            continue
        obj = LanguageModel(
            l_id=db_language_code_dict[language],
            lang=language,
            google_lang_code=google_translate_langcode_dict[language],
            ai4b_lang_code=get_AI4Bharat_lang_code(language),
            aks_lang_code=transliterate_dict[language],
            bcp_47_lang_code=get_bcp_47_lang_code(language),
            is_active=bool(language in ACTIVE_LANGUAGES),
        )
        objects.append(obj)
        # # obj.save()
        print(f"{language} NOT Saved in DB")
    return objects
