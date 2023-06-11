from bs4 import BeautifulSoup
import json
import uuid
from bardapi import Bard
import uuid
import os
from datetime import datetime
from hashlib import sha256
from dotenv import load_dotenv

from newsX_backend.enums.model_enums import RawNewsEnum
from newsX_backend.utils.data_utils import hash_SHA256, format_dateTime_from_inshorts, create_raw_news_id_from_url, dateTime_now, create_raw_news_id
from newsX_backend.utils.db_utils import insert_raw_news
from newsX_backend.models.util_models import NewsIdResponse

load_dotenv()

bard_token = os.getenv("GOOGLE_BARD_API_KEY")
bard = Bard(token=bard_token)

def parse_and_write_to_db(news_data, data=None,category='all')->NewsIdResponse:
    news_list= parse_news(news_data, category=category)
    insertion_count = 0
    news_ids_inserted = []
    all_news_ids = []
    for news in news_list:
        all_news_ids.append(news[RawNewsEnum.id.value])
        #handling url to video from form.
        if data is not None:
            news[RawNewsEnum.author.value] = data['email']
            news[RawNewsEnum.source.value] = data['isBgm']
        if insert_raw_news(news):
            insertion_count+=1
            news_ids_inserted.append(news[RawNewsEnum.id.value])

    result = NewsIdResponse(all_news_ids=all_news_ids, news_ids_inserted=news_ids_inserted)
    return result

def parse_news(news_data, category='all'):
    soup = BeautifulSoup(news_data, 'html.parser')
    all_news = soup.findAll("div", {"class": "news-card z-depth-1"})
    data = []
    count = len(all_news)

    for each_news in all_news:
        article_body = each_news.find(
            "div", {"itemprop": "articleBody"}).get_text()
        headline = each_news.find("span", {"itemprop": "headline"}).get_text()
        try:
            url = each_news.find("a", {"class": "source"})['href']
        except:
            url = ''
        try:
            image_url = each_news.find(
                "div", {"class": "news-card-image"})['style'].split("'")[1]
        except:
            image_url = ''
        other_details = each_news.find(
            "div", {"class": "news-card-author-time news-card-author-time-in-content"})
        this_news = {
            RawNewsEnum.id.value : None,
            RawNewsEnum.article.value: article_body,
            RawNewsEnum.title.value: headline,
            RawNewsEnum.date.value: other_details.find("span", {"class": "date"}).get_text(),
            RawNewsEnum.time.value: other_details.find("span", {"class": "time"}).get_text(),
            RawNewsEnum.source_url.value: url,
            RawNewsEnum.original_source.value: None,
            RawNewsEnum.image_url.value: image_url,
            RawNewsEnum.author.value: other_details.find("span", {"class": "author"}).get_text(),
            RawNewsEnum.category.value: category
        }
        date_str, time_str, timestamp = format_dateTime_from_inshorts(this_news[RawNewsEnum.date.value], this_news[RawNewsEnum.time.value])
        this_news[RawNewsEnum.date.value] = date_str
        this_news[RawNewsEnum.time.value] = time_str

        this_news[RawNewsEnum.id.value] = create_raw_news_id(article=this_news[RawNewsEnum.article.value],
                                                             date_formatted=this_news[RawNewsEnum.date.value],
                                                             time_formatted=this_news[RawNewsEnum.time.value])
        data.append(this_news)
    return data

def get_news_with_bard(url,data=None):
    wordcount = 100
    input_text = f'''give only a summarized version of the main news given in this link under {wordcount} words as a text paragraph, no bullet points: {url}'''

    response = ''
    num_tries = 0

    while len(response) > 1000 or len(response)<300 and num_tries < 5:
        if len(response) > 1000:
            wordcount = int(wordcount*0.9)
        elif len(response) < 300 and len(response) > 0:
            wordcount = int(wordcount*1.1)
        response = str(bard.get_answer(input_text)['content'])
        response = response[response.find(':')+1:].replace('*','').strip()
        num_tries+=1

    # print('News fetched: \n ', response)
    news_id = create_raw_news_id_from_url(url)
    
    date_str, time_str, timestamp = dateTime_now()
    
    news_dict = {
            RawNewsEnum.id.value: news_id,
            RawNewsEnum.article.value: response,
            RawNewsEnum.title.value: response,
            RawNewsEnum.date.value: date_str,
            RawNewsEnum.time.value: time_str,
            RawNewsEnum.source_url.value: str(url),
            RawNewsEnum.original_source.value: None,
            RawNewsEnum.image_url.value: None,
            RawNewsEnum.author.value: 'unknown',
            RawNewsEnum.category.value: 'all',
        }
    
    if data is not None:
        news_dict[RawNewsEnum.author.value] = data['email']
        news_dict[RawNewsEnum.source.value] = data['isBgm']
    insertion_count = 0
    news_ids_inserted = []
    all_news_ids = [news_dict[RawNewsEnum.id.value]]

    if insert_raw_news(news_dict):
            insertion_count+=1
            news_ids_inserted.append(news_dict[RawNewsEnum.id.value])

    return NewsIdResponse(all_news_ids=all_news_ids, news_ids_inserted=news_ids_inserted)

