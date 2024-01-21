import os
import json
import unicodedata
import math
import numpy as np
import re
import configparser

from mutagen.mp3 import MP3
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import ImageFont, ImageDraw, Image

from numpy import unicode

from newsX_backend.mappers.language_mapper import db_language_code_dict
from newsX_backend.utils.db_utils import get_language_by_title, get_translated_article, get_raw_news_by_id
from newsX_backend.utils.data_utils import handle_number_preprocessing
from newsX_backend.enums.model_enums import TranslatedArticlesEnum, RawNewsEnum

from newsX_backend.utils.directory_helper import get_translated_file, get_audio_file_path, get_news_video_lang_path, get_font_file, get_intro_video_path, get_outro_video_path
from newsX_backend.mappers.language_mapper import get_bcp_47_lang_code

import random

config = configparser.ConfigParser()
config.read('.config')

INTRO_FLAG = config.getboolean('VIDEO', 'VIDEO_INTRO_FLAG')
OUTRO_FLAG = config.getboolean('VIDEO', 'VIDEO_OUTRO_FLAG')

ENCODING = 'utf-8'
SPACE_SYLLABEL = 'SPACE'


def get_audio_length_in_sec(news_id, language):
    audio_filepath = os.path.join(
        get_audio_file_path(news_id, language), 'audio.mp3')
    audio = MP3(audio_filepath)
    return audio.info.length


def generate_subtitles(news_dict, language):
    news_id = news_dict['id']

    l_id = db_language_code_dict[language]
    translated_news = get_translated_article(news_id, l_id)
    translated_message = translated_news[TranslatedArticlesEnum.translated_article.value]

    # if language == 'English':
    #     translated_message = news_dict['article']
    # else:

    #     f = open(get_translated_file(news_id))
    #     translated_json = json.load(f)
    #     f.close()
    #     translated_message = translated_json[language]['article_translated']


    original_message = translated_message.encode(ENCODING).decode(ENCODING)

    decoded_message, change_list = handle_number_preprocessing(original_message, language, delimeter='-')

    syllabel_list = list(map(lambda x: unicodedata.name(x,u' '), decoded_message))
    word_count = original_message.split(' ')
    syllabel_count = len(syllabel_list)
    if syllabel_list[-1] != SPACE_SYLLABEL:
        syllabel_list.append(SPACE_SYLLABEL)
    audio_length = get_audio_length_in_sec(news_id, language)*1000
    syllabel_time_length = audio_length/syllabel_count

    idx = 0
    word_timestamp_map = []
    start = 0
    end = 0
    for syl in syllabel_list:
        if syl == SPACE_SYLLABEL:
            word_timestamp_map.append([word_count[idx], start, end])
            idx += 1
            start = end
        end += syllabel_time_length

    srt_str = ''
    idx = 1
    line = ''

    for i, itm in enumerate(word_timestamp_map):
        line = line + ' ' + itm[0]
        if i > 0 and (i+1) % 4 == 0:
            srt_str += str(idx) + '\n'
            idx += 1
            srt_str += "00:00:" + "{:02}".format(math.floor(word_timestamp_map[i-3][1]/1000)) + "," + "{:03}".format(
                math.floor(word_timestamp_map[i-3][1] % 1000))
            srt_str += ' --> '
            srt_str += "00:00:" + "{:02}".format(math.floor(word_timestamp_map[i][2]/1000)) + "," + "{:03}".format(
                math.floor(word_timestamp_map[i][2] % 1000))
            srt_str += '\n'
            srt_str += line + '\n\n'
            line = ''
        elif i == len(word_timestamp_map)-1:
            srt_str += str(idx) + '\n'
            idx += 1
            start_word_index = len(word_timestamp_map) - (i+1) % 4
            srt_str += "00:00:" + "{:02}".format(math.floor(word_timestamp_map[start_word_index][1]/1000)) + "," + "{:03}".format(
                math.floor(word_timestamp_map[start_word_index][1] % 1000))
            srt_str += ' --> '
            srt_str += "00:00:" + "{:02}".format(math.floor(word_timestamp_map[i][2]/1000)) + "," + "{:03}".format(
                math.floor(word_timestamp_map[i][2] % 1000))
            srt_str += '\n'
            srt_str += line + '\n\n'
            line = ''

    subtitle_file = os.path.join(
        get_news_video_lang_path(news_id, language), 'video.srt')
    f = open(subtitle_file, 'w', encoding=ENCODING)
    f.write(srt_str)
    f.close()
    print("Subtitle file generated at:  " + subtitle_file)
    print("Burning Subtitles to Video")

    video_file_path = os.path.join(
        get_news_video_lang_path(news_id, language), 'video.mp4')
    output_file_path = os.path.join(get_news_video_lang_path(
        news_id, language), 'video_with_subs.mp4')
    burn_subtitle_to_video(video_file_path, subtitle_file,
                           output_file_path, language)
    
    return output_file_path


def file_to_subtitles(filename, encoding=None):
    """ Converts a srt file into subtitles.

    The returned list is of the form ``[((ta,tb),'some text'),...]``
    and can be fed to SubtitlesClip.

    Only works for '.srt' format for the moment.
    """

    times_texts = []
    current_times = None
    current_text = ""
    with open(filename, "r", encoding=encoding) as f:
        for line in f:
            times = re.findall("([0-9]*:[0-9]*:[0-9]*,[0-9]*)", line)
            if times:
                current_times = [cvsecs(t) for t in times]
            elif line.strip() == "":
                if current_times is not None:
                    times_texts.append((current_times, current_text.strip("\n")))
                current_times, current_text = None, ""
            elif current_times:
                current_text += line
    return times_texts


def burn_subtitle_to_video(video_file_path, subtitle_file_path, output_file_path, language):

    def pipeline(frame):
        try:
            img_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(img_pil)

            text = str(next(subs_by_frame)[1])

            words = text.split(' ')
            line1 = ' '.join(word for word in words[:math.ceil(len(words)/2)])
            line2 = ''
            if math.ceil(len(words)/2) < len(words):
                line2 = ' '.join(word for word in words[math.ceil(len(words)/2):])

            #font
            text_font = ImageFont.truetype(fontpath, font_size, encoding=ENCODING)

            # padding
            horizontal_pad = 20
            vertical_pad = 10

            # size
            text_size = font.getsize(text)
            radius = 20
            line1_size = text_font.getsize(line1)
            img_width, img_height = img_pil.size

            rect1_size = [2*horizontal_pad + line1_size[0],
                         2*vertical_pad + line1_size[1]]

            line2_size = text_font.getsize(line2)
            rect2_size = [2*horizontal_pad + line2_size[0],
                         2*vertical_pad + line2_size[1]]
            font_reduction = 5
            while rect1_size[0] > img_width or rect2_size[0] > img_width:
                text_font = ImageFont.truetype(fontpath, font_size - font_reduction, encoding=ENCODING)

                line1_size = text_font.getsize(line1)
                img_width, img_height = img_pil.size

                rect1_size = [2*horizontal_pad + line1_size[0],
                            2*vertical_pad + line1_size[1]]

                line2_size = text_font.getsize(line2)
                rect2_size = [2*horizontal_pad + line2_size[0],
                            2*vertical_pad + line2_size[1]]
                font_reduction+=5

            # starting locations
            rect1_start = (
                int((img_width-rect1_size[0])/2), int(img_height*0.65)
                )
            line1_start = (rect1_start[0]+horizontal_pad,
                          rect1_start[1]+vertical_pad)

            rect2_start = (int((img_width - rect2_size[0])/2) , int(rect1_start[1]+rect1_size[1]))
            line2_start = ( rect2_start[0]+horizontal_pad, rect2_start[1]+vertical_pad )

            # end_location
            rect1_end = (rect1_start[0] + rect1_size[0],
                        rect1_start[1] + rect1_size[1])
            rect2_end = (rect2_start[0] + rect2_size[0],
                        rect2_start[1] + rect2_size[1])


            # color
            rect1_color = (255, 255, 255, 1)
            line1_color = (141, 0, 230, 1)

            rect2_color = (141, 0, 230, 1)
            line2_color = (255, 255, 255, 1)

            draw.rounded_rectangle([rect1_start, rect1_end], radius,fill=rect1_color)
            draw.text(line1_start, line1, font=text_font, fill=line1_color,
                      language=get_bcp_47_lang_code(language))

            if len(line2) > 0:
                draw.rounded_rectangle([rect2_start, rect2_end], radius, fill=rect2_color)
                draw.text(line2_start, line2, font=text_font, fill=line2_color,
                          language=get_bcp_47_lang_code(language))

            frame = np.array(img_pil)
        except StopIteration:
            pass
        # additional frame manipulation
        return frame

    subtitles = file_to_subtitles(subtitle_file_path, encoding=ENCODING)
    print(subtitles)
    video = VideoFileClip(video_file_path)

    fps = video.fps
    duration = math.ceil(video.duration)
    total_frames = math.ceil(duration*fps)

    subs_by_frame = []

    subtitle_index = 0
    for i in range(total_frames):
        if float((i+1)/total_frames) <= subtitles[subtitle_index][0][1]/duration:
            subs_by_frame.append((i, subtitles[subtitle_index][1]))
        else:
            subtitle_index += 1
            subtitle_index = min(subtitle_index, len(subtitles)-1)
            subs_by_frame.append((i, subtitles[subtitle_index][1]))

    fontpath = get_font_file(language)
    font_size = 60
    font = ImageFont.truetype(fontpath, font_size, encoding=ENCODING)

    subs_by_frame = iter(subs_by_frame)

    result = video.fl_image(pipeline)

    if INTRO_FLAG:
        result = add_intro_video(result, language)
    if OUTRO_FLAG:
        result = add_outro_video(result, language)
    random_hash = str(random.getrandbits(128))
    result.write_videofile(output_file_path, fps=video.fps, temp_audiofile=f"{random_hash}temp-audio.m4a",
                           remove_temp=True, codec="libx264", audio_codec="aac")
    return output_file_path


def add_intro_video(base_video, language):
    if not INTRO_FLAG:
        print("********** create_video.py::add_intro_video() called when INTRO_FLAG=False **********")
        return
    intro_video = get_intro_video_path(language)
    intro_video = VideoFileClip(intro_video, target_resolution=[1600,900])
    
    if isinstance(base_video, str):
        base_video = VideoFileClip(base_video)
    
    output_video = concatenate([intro_video, base_video])
    return output_video

def add_outro_video(base_video, language):
    if not OUTRO_FLAG:
        print("********** create_video.py::add_outro_video() called when OUTRO_FLAG=False **********")
        return
    outro_video = get_outro_video_path(language)
    outro_video = VideoFileClip(outro_video, target_resolution=[1600,900])

    if isinstance(base_video, str):
        base_video = VideoFileClip(base_video)
    
    output_video = concatenate([base_video, outro_video])
    return output_video