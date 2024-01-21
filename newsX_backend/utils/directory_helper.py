import os
import random
from  newsX_backend.mappers.language_mapper import DEFINED_LANGUAGES, get_font_filename
from newsX_backend.mappers.category_types import Category, BgmCategory

def get_news_path(news_id):
    generated_dir = get_generated_files_path()
    news_dir = news_id
    path = os.path.join(generated_dir, news_dir)
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        pass
    return path


def get_generated_files_path():
    curr_path = os.getcwd()
    generated_dir = 'generated_files'
    path = os.path.join(curr_path, generated_dir)
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        pass
    return path


def get_news_images_path(news_id):
    news_path = get_news_path(news_id)
    images_dir = 'Images'
    path = os.path.join(news_path, images_dir)
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        pass
    return path


def get_news_video_path(news_id):
    news_path = get_news_path(news_id)
    video_dir = 'Video'
    path = os.path.join(news_path, video_dir)
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        pass
    return path

def get_news_video_lang_path(news_id, language):
    video_root_path = get_news_video_path(news_id)
    video_lang_path = os.path.join(video_root_path, language)
    if not os.path.exists(video_lang_path):
        os.mkdir(video_lang_path)
    return video_lang_path


def get_audio_file_path(news_id, language):
    news_path = get_news_path(news_id)
    audio_dir = 'Voice'
    audio_path = os.path.join(news_path, audio_dir)
    if not os.path.exists(audio_path):
        os.mkdir(audio_path)
    language_audio_path = os.path.join(audio_path, language)
    if not os.path.exists(language_audio_path):
        os.mkdir(language_audio_path)
    return language_audio_path

def get_translated_file(news_id):
    news_path = get_news_path(news_id)
    translated_file_name = 'translated_result.json'
    translated_file = os.path.join(news_path,translated_file_name)
    return translated_file

def get_font_file(language):
    curr_path = os.getcwd()
    font_filename = get_font_filename(language)
    path = os.path.join(curr_path, 'resources', 'fonts', language, font_filename)
    print(path)
    return path

def get_zoom_videos_path(news_id,image_number=None):
    video_path = get_news_video_path(news_id)
    clip_folder_path = os.path.join(video_path, 'zoom_clips')

    if not os.path.exists(clip_folder_path):
        os.mkdir(clip_folder_path)

    if image_number is None:
        return clip_folder_path

    image_video_path = os.path.join(clip_folder_path, str(image_number))
    if not os.path.exists(image_video_path):
        os.mkdir(image_video_path)

    image_video_file = os.path.join(image_video_path,'00000'+str(image_number)+'.mp4')
    return image_video_file

def get_resource_base_dir_path():
    curr_path = os.getcwd()
    resource_dir = os.path.join(curr_path,'resources')
    return resource_dir

def get_intro_video_path(lang=None):
    resource_path = get_resource_base_dir_path()
    intro_base_path = os.path.join(resource_path, 'videos','intro')
    if lang is None:
        return intro_base_path
    if lang in DEFINED_LANGUAGES:
        intro_lang_path =  os.path.join(intro_base_path, lang)
        for item in os.listdir(intro_lang_path):
            if item.endswith('.webm') or item.endswith('.mp4') or item.endswith('.mov'):
                intro_file = os.path.join(intro_lang_path, item)
                return intro_file
        raise Exception(' get_intro_video_path :: No intro video file found in directory:  ' + intro_lang_path )
    else:
        raise Exception(' get_intro_video_path :: Language parameter is incorrect :: "' + lang + '" not supported')

def get_outro_video_path(lang=None):
    resource_path = get_resource_base_dir_path()
    outro_base_path = os.path.join(resource_path, 'videos','outro')
    if lang is None:
        return outro_base_path
    if lang in DEFINED_LANGUAGES:
        outro_lang_path =  os.path.join(outro_base_path, lang)
        for item in os.listdir(outro_lang_path):
            if item.endswith('.webm') or item.endswith('.mp4') or item.endswith('.mov'):
                outro_file = os.path.join(outro_lang_path, item)
                return outro_file
        raise Exception(' get_outro_video_path :: No outro video file found in directory:  ' + outro_lang_path )
    else:
        raise Exception(' get_outro_video_path :: Language parameter is incorrect :: "' + lang + '" not supported')

def get_bgm_path(bgm_category=None):
    resource_path = get_resource_base_dir_path()
    bgm_base_path = os.path.join(resource_path, 'audio','bgm')
    if bgm_category is None:
        return bgm_base_path
    if bgm_category in BgmCategory.DEFINED_BGM_CATEGORY:
        bgm_folder_name = BgmCategory.PATH_MAPPER[bgm_category]
        bgm_catg_path =  os.path.join(bgm_base_path, bgm_folder_name)
        bgm_files = []
        for item in os.listdir(bgm_catg_path):
            if item.lower().endswith('.mp3') or item.lower().endswith('.wav') or item.lower().endswith('.flac'):
                bgm_files.append(item)

        if len(bgm_files)>0:
            selected_file = random.choice(bgm_files)
            bgm_file = os.path.join(bgm_catg_path, selected_file)
            return bgm_file
        else:
            raise Exception('get_bgm_path :: No BGM File found for category: ' + bgm_category)
    else:
        raise Exception('get_bgm_path :: Category parameter is incorrect :: "' + bgm_category + '" not supported')

def get_transition_audio_path():
    resource_path = get_resource_base_dir_path()
    transition_base_path = os.path.join(resource_path, 'audio', 'transition')
    for item in os.listdir(transition_base_path):
        if item.endswith('.mp3') or item.endswith('.wav'):
            transition_audio_file = os.path.join(transition_base_path, item)
            print(transition_audio_file)
            return transition_audio_file