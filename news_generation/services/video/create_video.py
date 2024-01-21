from pathlib import Path
import os
import subprocess
import configparser
from mutagen.mp3 import MP3
from PIL import Image
import imageio
from moviepy import editor
from moviepy.editor import *
from moviepy.audio.fx.volumex import volumex

from newsX_backend.utils.directory_helper import get_audio_file_path, get_news_images_path, get_news_video_path, get_news_video_lang_path, get_zoom_videos_path, get_transition_audio_path
from newsX_backend.utils.db_utils import get_language_by_title, get_raw_news_by_id, insert_video_link, get_item_config
from newsX_backend.utils.firebase_utils import UploadVideo
from newsX_backend.enums.model_enums import VideoLinksEnum, RawNewsEnum, ItemConfigEnum
from newsX_backend.mappers.language_mapper import db_language_code_dict
from newsX_backend.utils.data_utils import create_video_links_id
from newsX_backend.models.util_models import NewsIdResponse
from news_generation.services.video.bgm_services import get_bgm

from news_generation.models import Languages as LanguageModel

from .chatgpt_get_image_query import get_google_image_queries_from_gpt
from .image_query_processing import get_images_from_google
from .subtitle_generator import generate_subtitles



config = configparser.ConfigParser()
config.read('.config')

INTRO_FLAG = config.getboolean('VIDEO', 'VIDEO_INTRO_FLAG')
OUTRO_FLAG = config.getboolean('VIDEO', 'VIDEO_OUTRO_FLAG')

DEFAULT_BGM_FLAG = config.getboolean('VIDEO','VIDEO_BGM_FLAG')
BGM_VOLUMEX = config.getfloat('VIDEO','VIDEO_BGM_VOLUMEX')

AUDIO_VOLUMEX = config.getfloat('AUDIO','AUDIO_VOLUMEX')

TRANSITION_MODE = config.getint('TRANSITION', 'TRANSITION_MODE')
TRANSITION_SOUND = config.getboolean('TRANSITION', 'TRANSITION_SOUND')

def create_video_from_ids(news_id_list, languages):
    news_list = get_raw_news_by_id(news_id_list)

    for news in news_list:
        for language in languages:
            video_file = create_video(news, language)
            video_url = upload_to_storage(video_file)
            status = write_to_db(news, language, video_url)
    return NewsIdResponse(news_id_list)

def create_video_gif(news_id, language, audio_length, first_gif=False):
    list_of_images = []
    list_of_image_paths = []
    images_parent_dir = get_news_images_path(news_id)

    for root, subdirectories, files in os.walk(images_parent_dir):
        for subdirectory in subdirectories:
            images_path = os.path.join(root, subdirectory)
            for image_file in os.listdir(images_path):
                if image_file.endswith('.png') or image_file.endswith('.jpg'):
                    image_path = os.path.join(images_path, image_file)
                    image = image = resize_to_vertical(image_path)
                    resized_image_file = os.path.join(
                        images_path, 'resized_image_001.png')
                    image.convert('RGB').save(resized_image_file)
                    list_of_images.append(image)
                    list_of_image_paths.append(resized_image_file)
                    break

    # print(len(list_of_images))
    duration = audio_length/len(list_of_images)

    # Creating directories for zoom video clips
    zoom_video_base_path = get_zoom_videos_path(news_id)
    list_output_files = []
    for idx, image_path in enumerate(list_of_image_paths):
        out_file = get_zoom_videos_path(news_id, idx)
        list_output_files.append(out_file)
    print(list_output_files)
    print(list_of_image_paths)
    screensize = [900, 1600]
    zoom_fps = 30
    create_zoom_effect_video_clips(
        list_of_image_paths, list_output_files, screensize, duration, zoom_fps)

    list_of_zoomed_videos = []
    for root, subdirectories, files in os.walk(zoom_video_base_path):
        for subdirectory in subdirectories:
            videos_path = os.path.join(root, subdirectory)
            for video_file in os.listdir(videos_path):
                if video_file.endswith('.mp4'):
                    video_file_path = os.path.join(videos_path, video_file)
                    zoomed_video = editor.VideoFileClip(video_file_path)
                    list_of_zoomed_videos.append(zoomed_video)
                    break

    if first_gif:
        video_path = get_news_video_path(news_id)
        base_gif_path = os.path.join(video_path, 'images.gif')
        imageio.mimsave(base_gif_path,
                        list_of_images, fps=1/duration)

    # Now save the images.gif in respective folder
    video_lang_path = get_news_video_lang_path(news_id, language)

    if TRANSITION_MODE != 0:
        final_clip = handle_video_transition(list_of_zoomed_videos)
    else:
        base_zoomed_gif_path = os.path.join(video_lang_path, 'images.gif')
        final_clip = editor.concatenate_videoclips(list_of_zoomed_videos)

    return final_clip

def handle_video_transition(list_of_zoomed_videos):
    # get the transition audio file
    transition_audio = editor.AudioFileClip(
        get_transition_audio_path())

    TRANSITION_DURATION = 0.3
    clips_to_be_added = []

    # adding transition sound based on the flag
    if TRANSITION_SOUND == True:
        clips_to_be_added = [
            clip.set_audio(CompositeAudioClip([
                transition_audio
                .set_start(clip.duration - TRANSITION_DURATION)
                .set_duration(TRANSITION_DURATION)
            ]))
            for clip in list_of_zoomed_videos
        ]
    else:
        clips_to_be_added = list_of_zoomed_videos

    final_clip = []
    # TRANSITION_MODE=1 is SLIDE TRANSITION
    if TRANSITION_MODE == 1:

        # Order of SLIDE EFFECT
        slide_in_effect = ['left', 'top', 'right', 'bottom']

        slided_clips = [editor.CompositeVideoClip(
            [clip.fx(editor.transfx.slide_in, TRANSITION_DURATION, slide_in_effect[idx % 4])]) for idx, clip in enumerate(clips_to_be_added)]

        # Final Clip
        # padding=-TRANSITION_DURATION
        final_clip = editor.concatenate(slided_clips)

    # TRANSITION_MODE=2 is FADE TRANSITION
    else:
        transition_vid_list = []
        for idx, vid in enumerate(clips_to_be_added):
            if idx != 0:
                transition_vid_list.append(
                    vid.fx(vfx.fadein, TRANSITION_DURATION).fx(vfx.fadeout, TRANSITION_DURATION))
            else:
                transition_vid_list.append(vid)
        final_clip = editor.concatenate_videoclips(transition_vid_list)

    return final_clip

def create_video(news_dict, language):
    news_id = news_dict['id']
    audio_path = os.path.join(
        get_audio_file_path(news_id, language), "audio.mp3")
    video_path = get_news_video_path(news_id)
    video_lang_path = get_news_video_lang_path(news_id, language)

    images_parent_dir = get_news_images_path(news_id)

    audio = MP3(audio_path)
    audio_length = audio.info.length

    video = None
    if not os.path.exists(os.path.join(video_path, 'images.gif')):
        get_google_image_queries_from_gpt(news_dict)
        get_images_from_google(news_dict)
        # create the images.gif in the news directory just as a flag to mark that images have been crawled from google
        video = create_video_gif(news_id, language, audio_length, True)
    else:
        # creating the images.gif based on the audio length and saving them in the respective language video folder
        video = create_video_gif(news_id, language, audio_length, False)

    # video = editor.VideoFileClip(os.path.join(video_lang_path, 'images.gif'))
    audio = editor.AudioFileClip(audio_path)
    audio = audio.fx(volumex, AUDIO_VOLUMEX)

    item_config = get_item_config(news_id)
    
    BGM_FLAG = item_config.get(ItemConfigEnum.is_bgm_enabled.value, DEFAULT_BGM_FLAG)

    if BGM_FLAG:
        bgm_path = get_bgm(news_dict)
        bgm_audio = editor.AudioFileClip(bgm_path)
        bgm_audio = bgm_audio.subclip(0, audio.duration)
        bgm_audio = bgm_audio.fx(volumex, BGM_VOLUMEX)
        audio = editor.CompositeAudioClip([audio, bgm_audio])

    else:
        pass

    if TRANSITION_MODE != 0:
        final_video = video.set_audio(CompositeAudioClip([video.audio, audio]))
    else:
        final_video = video.set_audio(audio)
    
    final_video = video.set_audio(audio)
    video_file = os.path.join(video_lang_path, 'video.mp4')
    final_video.write_videofile(fps=60, codec="libx264", filename=video_file)
    sub_video_file = generate_subtitles(news_dict,language)
    return sub_video_file


def run_ffmpeg_zoom(command_list ,image_path, output_file, screensize, duration, fps=60, zoom_ratio=0.0005, zoom_smooth=100):
    ffmpeg_command = f"""ffmpeg -framerate {fps} -loop 1 -i "{image_path}" -filter_complex "[0:v]scale={screensize[0] * zoom_smooth}x{screensize[1] * zoom_smooth}, zoompan=z='min(zoom+{zoom_ratio},1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={duration * fps},trim=duration={duration}[v1];[ v1]scale={screensize[0]}:{screensize[1]}[v]" -map "[v]" -y "{output_file}" """
    # command_list.append(ffmpeg_command)
    # return command_list
    process = subprocess.Popen(
        ffmpeg_command, shell=True, stdout=subprocess.PIPE)
    process.wait()


def create_zoom_effect_video_clips(image_paths, output_files, screensize, duration, fps=60, zoom_ratio=0.0015, zoom_smooth=5):
    command_list = []
    for idx, image_path in enumerate(image_paths):
        command_list = run_ffmpeg_zoom(
            command_list,image_path, output_files[idx], screensize, duration, fps, zoom_ratio, zoom_smooth)
    # procs = [subprocess.Popen(i,shell=True, stdout=subprocess.PIPE) for i in command_list ]
    # for p in procs:
    #     p.wait()


def upload_to_storage(file_location):
    video_ref = UploadVideo()
    url = video_ref.upload_video_to_storage(file_location)
    return url

def write_to_db(news, language, url):
    language_obj = LanguageModel(**get_language_by_title(language))
    language_id = db_language_code_dict[language]
    id = create_video_links_id(news[RawNewsEnum.id.value], language_id)

    video_links_dict = {
        VideoLinksEnum.id.value: id,
        VideoLinksEnum.v_id.value: news[RawNewsEnum.id.value],
        VideoLinksEnum.video_url.value: url,
        VideoLinksEnum.language.value: language_obj
    }

    status = insert_video_link(video_links_dict)
    return status

def resize_to_vertical(image_path):
    image = Image.open(image_path)
    aspect_ratio = image.height/image.width
    req_aspect_ratio = 16/9
    if aspect_ratio > req_aspect_ratio:
        return image.resize((900, 1600), Image.ANTIALIAS)
    else:
        if aspect_ratio < 0.8:
            size = (image.width, 0.8*image.width)
            # image.thumbnail( size, Image.Resampling.LANCZOS)
            padding =  Image.new(image.mode, (image.width, int(image.width*0.8)), (0, 0, 0))
            padding.paste(image , (0,int((image.width*0.8 - image.height)/2)))
            color = (0, 0, 0)
            if image.mode in ["L", "1", "P"]:
                color = (0)
            elif image.mode in ["RGBA", "CMYK"]:
                color = (0, 0, 0, 0)
            padding = Image.new(
                image.mode, (image.width, int(image.width*0.8)), color)
            padding.paste(image, (0, int((image.width*0.8 - image.height)/2)))
            image = padding

        if aspect_ratio < 1.3:
            crop_px_horizontal = int(( image.width - image.height/1.3)/2)
            image = image.crop((crop_px_horizontal, 0 ,image.width-crop_px_horizontal, image.height))


        if aspect_ratio < req_aspect_ratio:
            image = image.resize((900, 1600), Image.ANTIALIAS)


        return image