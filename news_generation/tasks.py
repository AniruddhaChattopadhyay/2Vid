from __future__ import absolute_import, unicode_literals

from celery import shared_task, Celery

from newsX_backend.models.util_models import NewsIdResponse
from newsX_backend.utils.comm_utils import send_mail

from .services.news_fetching.get_news import getNews, getNewsFromUrl
from .services.translation.translateService import translate_to_multiple_languages
from .services.tts.translated_text_to_voice import text_to_speech
from .services.video.create_video import create_video_from_ids
from .services.input_handling.input_handling import create_raw_from_script


import time

# app = Celery('tasks', broker='amqp://localhost//')

# @app.task

# @app.task
@shared_task
def get_news_task(category, number_of_pages_to_crawl):
    return getNews(category, number_of_pages_to_crawl)


@shared_task
def get_news_from_url_task(url,data):
    response = getNewsFromUrl(url,data)
    return response


@shared_task
def translate_news_task(news_id_response:NewsIdResponse,languages):
    response = translate_to_multiple_languages(news_id_response.all_news_ids, languages)
    return response

@shared_task
def translate_news_task_from_script(news_id_trans_lang_tuple):
    print(news_id_trans_lang_tuple)
    response = translate_to_multiple_languages(news_id_trans_lang_tuple[0].all_news_ids, news_id_trans_lang_tuple[1])
    return response

@shared_task
def tts_task(news_id_response:NewsIdResponse, languages):
    response = text_to_speech(news_id_response.all_news_ids, languages)
    return response


@shared_task
def video_generation_task(news_id_response:NewsIdResponse, languages):
    response = create_video_from_ids(news_id_response.all_news_ids, languages)
    return response

@shared_task
def send_mail_task(news_id_response:NewsIdResponse, languages):
    response = send_mail(news_id_response, languages)
    return response

@shared_task
def create_raw_from_script_task(data):
    response = create_raw_from_script(data)
    return response