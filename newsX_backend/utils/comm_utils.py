import configparser
import os
from dotenv import load_dotenv
import json
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

from newsX_backend.utils.db_utils import get_video_links, get_raw_news_by_id, get_item_config
from newsX_backend.mappers.language_mapper import db_language_code_dict
from newsX_backend.enums.model_enums import RawNewsEnum, VideoLinksEnum, LanguagesEnum, ItemConfigEnum
from newsX_backend.models.util_models import NewsIdResponse
from newsX_backend.utils.db_utils import get_raw_news_by_id

load_dotenv()

config = configparser.ConfigParser()
config.read('.config')

MAIL_ENABLED = config.getboolean('MAIL', 'MAIL_ENABLED')
SENDER_MAIL = config.get('MAIL', 'MAIL_SENDER')


SIB_API_KEY = os.getenv("SIB_API_KEY")

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = SIB_API_KEY


def get_details(news_id, languages):
    urls = []
    for language in languages:
        l_id = db_language_code_dict[language]
        video_data = get_video_links(v_id=news_id, l_id=l_id)
        urls.append(video_data)
    title = get_raw_news_by_id([news_id])[0][RawNewsEnum.title.value].strip()
    print(urls)
    return title, urls


def send_mail(news_id_response: NewsIdResponse, languages):
    RECIEVER_LIST = config.get('MAIL', 'MAIL_RECIEVER_LIST').split(',')
    
    if not MAIL_ENABLED:
        return
    news_id_list = news_id_response.all_news_ids
    
    reciever_email_list_additional = []
    for id in news_id_list:
        config_dict = get_item_config(id)
        reciever_email_list_additional = reciever_email_list_additional + json.loads(config_dict[ItemConfigEnum.email_list.value])
    
    RECIEVER_LIST.extend(reciever_email_list_additional)

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = 'subject'
    html_content = 'Hi,<br>'
    sender = {"name": 'Admin-DataX', "email": SENDER_MAIL}
    to = [ {'email': mail_id, 'name':mail_id} for mail_id in RECIEVER_LIST ]
    headers = {"Some-Custom-Name": "hash-idb2bid-1231a-23ty5j4-35757y-566y"}

    for id in news_id_list:
        title ,urls = get_details(id,languages)
        html_content += f'<br> Video links for news titled: "{title}".<br>'
        for url_dict in urls:
            url = url_dict[VideoLinksEnum.video_url.value]
            l_id = url_dict['language_id']
            language = {v: k for k, v in db_language_code_dict.items()}[l_id]
            html_content+= f'{language} URL : {url}<br>'
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers,html_content=html_content, sender=sender, subject=subject)
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
