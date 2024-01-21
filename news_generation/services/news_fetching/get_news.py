from bs4 import BeautifulSoup
import requests
import re
import json

from newsX_backend.utils.news_parser import parse_and_write_to_db, get_news_with_bard
from newsX_backend.models.util_models import NewsIdResponse

""" Crawls inshorts to get news based on the category and the number of pages of that category needed

The List of valid(case sensetive) categories are:
1. all
2. national //Indian News only
3. business
4. sports
5. world
6. politics
7. technology
8. startup
9. entertainment
10. miscellaneous
11. hatke
12. science
13. automobile
"""

def getNewsFromUrl(url,data)->NewsIdResponse:
    print(f'Fetching news from: {url}')
    
    if url.find('inshorts.com') != -1:
        return getNewsFromInshortsUrl(url,data)
    else:
        return  get_news_with_bard(url,data)

def getNews(category, number_of_pages_to_crawl):
    regex_min_news_id = re.compile('var min_news_id = "(.*?)";')
    url = "https://www.inshorts.com/en/read/"
    page_number = 1
    news_count = 0
    try:
        if category != 'all':
            request = requests.get(
                url + category)
        else:
            request = requests.get(url)

    except requests.exceptions.RequestException as e:
        print(e)
        return
    # This has to be sent as a parameter while sending a new request.
    min_news_id = regex_min_news_id.search(request.text).group(1)
    response = parse_and_write_to_db(request.text, None, category)
    news_count+=response['news_count']
    while (page_number <= number_of_pages_to_crawl):
        page_number += 1
        try:
            url = "https://www.inshorts.com/en/ajax/more_news"
            if category != 'all':
                request = requests.post(
                    url, data={'news_offset': min_news_id, 'category': category})
            else:
                request = requests.post(url, data={'news_offset': min_news_id})
        except requests.exceptions.RequestException as e:
            print(e.message)
            return
        response = parse_and_write_to_db(json.loads(request.text)['html'], None ,category)
        news_count+=response['news_count']
        # Find min_news_id for the next page.
        min_news_id = json.loads(request.text)['min_news_id']

        """
        A small log system to store the number of pages it has scraped
        and also their min_news_id respectively
        """
        with open('min_news_id.txt', 'a') as min_news_id_file:
            min_news_id_file.write(
                min_news_id + ' - ' + str(page_number) + '\n')
            min_news_id_file.close()
    
    return {'category': category, 'news_count': news_count}


def getNewsFromInshortsUrl(url,data=None):
    try:
        request = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f'Exception :: getNewsFromInshortsUrl :: {e}')
        return
    response = parse_and_write_to_db(request.text,data=data)
    return response