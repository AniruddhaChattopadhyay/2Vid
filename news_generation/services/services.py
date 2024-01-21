from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render
from celery import chain

from news_generation.tasks import *

from newsX_backend.mappers.language_mapper import ACTIVE_LANGUAGES, DEFINED_LANGUAGES, Languages
from news_generation.forms import ProcessFromURLForm

from newsX_backend.utils.db_utils import CAUTION_THIS_WILL_BREAK_STUFF__modify_language_model_objects
from news_generation.services.video.bgm_services import get_bgm_type


def news_generation_post(request):
    '''
    {
        category: 'someCategory',
        [optional] no_pages: no_pages
    }
    '''
    try:
        data = request.data
        category = data['category']
        no_pages_to_crawl = int(data['no_pages'])
        if no_pages_to_crawl is None:
            no_pages_to_crawl = 2
        async_response = get_news_task.delay(category, no_pages_to_crawl)
        response = {"request_data": data }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as error:
        return internal_server_error(error,"Failed to fetch news")


def news_generation_by_url(request):
    '''
    {
        url: 'someUrlFromInshorts'
    }
    '''
    try:
        data = request.data
        url = data['url']
        async_response = get_news_from_url_task.delay(url,data)
        response = {"request_data": data }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as error:
        return internal_server_error(error,"Failed to fetch news from url: "+str(url))

def process_news_from_url(request):
    '''
    {
        url: 'someUrlFromInshorts',
        [optional] languages: [languages in present in DEFINED_LANGUAGES]
    }
    '''
    try:
        data = request.data
        url = data['url']
        languages = ACTIVE_LANGUAGES
        if 'languages' in list(data.keys()):
            languages = data['languages']
            languages = list(set(languages) & set(DEFINED_LANGUAGES))
        chain_task = chain(get_news_from_url_task.s(url,data), translate_news_task.s(languages), tts_task.s(languages), video_generation_task.s(languages), send_mail_task.s(languages)).delay()
        # chain_task = chain(get_news_from_url_task.s(url), send_mail_task.s(languages)).delay()
        # async_response = chain_task.get()
        response = {"request_data": data }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as error:
        return internal_server_error(error,"Translation API Failed")
    
def process_news_from_form(request):
    url = None
    languages = []
    form = ProcessFromURLForm()
    if request.method == 'POST':
        form = ProcessFromURLForm(request.POST)
        if form.is_valid():
             # Process the form data
            url = form.cleaned_data['url']
            english_chkb = form.cleaned_data['English']
            hindi_chkb = form.cleaned_data['Hindi']
            bengali_chkb = form.cleaned_data['Bengali']

            print(url, english_chkb, hindi_chkb, bengali_chkb)

            if english_chkb:
                languages.append(Languages.ENGLISH)
            if hindi_chkb:
                languages.append(Languages.HINDI)
            if bengali_chkb:
                languages.append(Languages.BENGALI)
            if len(languages)==0:
                languages.append(Languages.ENGLISH)
            try:
                chain_task = chain(get_news_from_url_task.s(url,data), translate_news_task.s(languages), tts_task.s(languages), video_generation_task.s(languages), send_mail_task.s(languages)).delay()
            except Exception as error:
                print(error)
    else:
        print('NOT POST')
    return render(request, 'processUrlForm.html', {'form': form})

def update_language_table(request):
    ## DO NOT RUN (Unless you know what this does) - WILL BREAK 
    
    # CAUTION_THIS_WILL_BREAK_STUFF__modify_language_model_objects()
    
    return Response({"message": "Check Update DB method and MySQL DB to verify update" }, status=status.HTTP_200_OK)


def script_to_video(request):
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
    try:
        data = request.data
        data['languages'] = data['languages']
        lang_list = []
        for lang in data['languages']:
            lang_list.append(lang.strip())
        data['languages'] = lang_list
        all_requested_languages = list(set(list(data['languages'])) & set(ACTIVE_LANGUAGES))
        print(all_requested_languages)
        chain(create_raw_from_script_task.s(data),translate_news_task_from_script.s(), tts_task.s(all_requested_languages), video_generation_task.s(all_requested_languages), send_mail_task.s(all_requested_languages)).delay()  
        return Response({"lang": all_requested_languages}, status=status.HTTP_200_OK)
    except Exception as e:
        return internal_server_error(e)

def url_to_video(request):
    '''
    {
        url: 'someUrlFromInshorts'
        languages: [languages in present in DEFINED_LANGUAGES]
        email : mail_id
        isBgm : YES/NO
    }
    '''

    try:
        data = request.data
        url = data['url']
        data['languages'] = data['languages']
        lang_list = []
        for lang in data['languages']:
            lang_list.append(lang.strip())
        data['languages'] = lang_list
        if 'languages' in list(data.keys()):
            languages = data['languages']
            languages = list(set(languages) & set(DEFINED_LANGUAGES))
        chain_task = chain(get_news_from_url_task.s(url,data), translate_news_task.s(languages), tts_task.s(languages), video_generation_task.s(languages), send_mail_task.s(languages)).delay()
        # chain_task = chain(get_news_from_url_task.s(url), send_mail_task.s(languages)).delay()
        # async_response = chain_task.get()
        response = {"request_data": data }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as error:
        return internal_server_error(error,"URL-TO-VIDEO API Failed")

def internal_server_error(error,error_message='Server Error'):
    print(error)
    data, msg = "", error_message
    response = {"data": data, "msg": msg, 'error_message': str(error)}
    return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def test_service(request):
    data = request.data
    response = get_bgm_type(data['text'])
    return Response(response, status=status.HTTP_200_OK)
