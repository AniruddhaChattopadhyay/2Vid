import torch
from aksharamukha import transliterate
import json
from pydub import AudioSegment
import os
import base64
import requests
import json
from gtts import gTTS
import configparser
from dotenv import load_dotenv

from newsX_backend.utils.directory_helper import get_news_path, get_audio_file_path, get_generated_files_path
from newsX_backend.mappers.language_mapper import get_language_mapper, get_AI4Bharat_lang_code, db_language_code_dict, Languages
from newsX_backend.utils.db_utils import get_language_by_title, get_translated_article, get_raw_news_by_id
from newsX_backend.utils.data_utils import handle_number_preprocessing
from newsX_backend.enums.model_enums import TranslatedArticlesEnum, RawNewsEnum, TemporaryEnum
from newsX_backend.models.util_models import NewsIdResponse
from .recorded_voice_handling import download_recorded_voice
from news_generation.models import Languages as LanguageModel
from news_generation.services.tts.aws_polly_service import AWSPollyTTS

load_dotenv()

config = configparser.ConfigParser()
config.read('.config')

XI_LABS_API_KEY = os.getenv("XI_LABS_API_KEY")
XI_LABS_CHUNK_SIZE = 1024
XI_LABS_BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"
XI_LABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM" # Rachel Voice ID

HINDI_ELEVENLABS = config.getboolean('AUDIO', 'AUDIO_HINDI_ELEVENLABS_MODEL')
def handle_recorded_voice(news_dict,language):
    if news_dict[RawNewsEnum.title.value] == TemporaryEnum.from_forms.value and news_dict[RawNewsEnum.image_url.value] != None and 'drive.google.com' in news_dict[RawNewsEnum.image_url.value] and news_dict[RawNewsEnum.original_source.value] == language:
        return download_recorded_voice(news_dict,language)
    else:
        return False
    
def text_to_speech(news_id_list,languages):
    news_list = get_raw_news_by_id(news_id_list)

    for news in news_list:
        for language in languages:
            if not handle_recorded_voice(news,language):
                audio_file = translate_text_to_voice(news,language)
    
    return NewsIdResponse(news_id_list)


def convert_wav_to_mp3(news_id, language, input_file):
  # specify the input and output file paths
    output_file = os.path.join(
        get_audio_file_path(news_id, language), 'audio.mp3')

    # read the input file using pydub
    audio = AudioSegment.from_wav(input_file)

    # export the audio to mp3 format
    audio.export(output_file, format="mp3")
    return output_file


def useLocalModel(news_dict, language):
    print("*"*10 + "Using Local Model" + "*")
    print("")
    news_id = news_dict['id']
    model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language='indic',
                                         speaker='v3_indic')

    # model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
    #                                     model='silero_tts',
    #                                     language='en', speaker='v3_en')

    t_id = news_id
    l_id = db_language_code_dict[language]
    translated_dict = get_translated_article(t_id, l_id)

    orig_text = translated_dict[TranslatedArticlesEnum.translated_article.value].encode(
        'utf-8').decode('utf-8')

    print( '****************** Orig Text***********************', orig_text)
    processed_original_text , change_list  = handle_number_preprocessing(orig_text, language=language)
    print( '****************** Processed Original***********************', processed_original_text)

    # language = translated_dict[language]['translation_language']
    speaker = str(language).lower() + '_female'

    language = language.capitalize()
    roman_text = transliterate.process(
        get_language_mapper(language), 'ISO', processed_original_text)
    
    # print( '****************** Orig Roman***********************', original_roman_text)
    # roman_text , change_list  = handle_number_preprocessing(original_roman_text, language=language)
    # print('****************** Processed Roman***********************', roman_text)
    sample_rate = 48000

    audio = model.apply_tts(roman_text,
                            speaker=speaker)

    audio_path = model.save_wav(text=roman_text,
                                 speaker=speaker,
                                 sample_rate=sample_rate)
    
    return convert_wav_to_mp3(news_id, language, audio_path)


def translate_text_to_voice(news_dict, language):

    news_id = news_dict['id']
    t_id = news_id
    l_id = db_language_code_dict[language]
    translated_dict = get_translated_article(t_id, l_id)
    orig_text = translated_dict[TranslatedArticlesEnum.translated_article.value]

    if language in [Languages.ENGLISH, Languages.HINDI, Languages.SPANISH] :
        print("************* AWS POLLY START *********************")
        aws_polly = AWSPollyTTS()
        audio_folder_path = get_audio_file_path(news_id, language)
        audio_file = os.path.join(audio_folder_path,'audio.mp3')
        if aws_polly.perform_tts(orig_text,language, audio_file):
            return audio_file

    # if (language == Languages.HINDI and HINDI_ELEVENLABS) or language==Languages.SPANISH:
    #     audio_file = translate_text_to_voice_elevenlabs(news_dict, language)
    #     if audio_file is not None:
    #         return audio_file
        
    url = "https://tts-api.ai4bharat.org/"
    gender = 'female'
    source_language = get_AI4Bharat_lang_code(language)

    processed_text , change_list  = handle_number_preprocessing(orig_text, language=language)
    payload = json.dumps({
        "input": [
            {
                "source": processed_text
            }
        ],
        "config": {
            "gender": gender,
            "language": {
                "sourceLanguage": source_language
            }
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        response_dict = response.json()
        if 'status' in response_dict and response_dict['status'] == "ERROR":
            print(response_dict['status'])
            print(response_dict['status_text'])
            useLocalModel(news_dict, language)
        else:
            audio_base64 = response_dict['audio'][0]['audioContent']
            sample_rate = response_dict['config']['samplingRate']
            temp_file_location = os.path.join(get_news_path(news_id=news_id),'temp.wav')
            wav_file = open(temp_file_location, "wb")
            decoded_base64 = base64.b64decode(audio_base64)
            wav_file.write(decoded_base64)
            wav_file.close()
            return convert_wav_to_mp3(news_id, language, temp_file_location)
    else:
        print(f"AI4Bharat Failure: {response.status_code}")
        return useLocalModel(news_dict, language)


def generate_english_audio_xi_labs(news_dict):
    orig_text = news_dict[RawNewsEnum.article.value]
    processed_text , change_list  = handle_number_preprocessing(orig_text, language=Languages.ENGLISH)
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": XI_LABS_API_KEY
    }

    data = {
        "text": processed_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }
    voice_ids = ["21m00Tcm4TlvDq8ikWAM", 'AZnzlk1XvdvUeBnXmlld', 'EXAVITQu4vr4xnSDxMaL', 'ErXwobaYiN019PkySvjV', 'MF3mGyEYCl7XYWbV9V6O', 'TxGEqnHWrfWFTfGW9XjX', 'VR6AewLTigWG4xSOukaG', 'pNInz6obpgDQGcFmaJgB', 'yoZ06aMxZJJ28mfd3POQ']
    voice = "21m00Tcm4TlvDq8ikWAM"
    response = requests.post(XI_LABS_BASE_URL+voice, json=data, headers=headers)
    news_id = news_dict[RawNewsEnum.id.value]
    audio_path = get_audio_file_path(news_id, 'English')
    audio_file = os.path.join(audio_path,'audio.mp3')

    if response.status_code == 200:
        with open(audio_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=XI_LABS_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        return audio_file
    else:
        raise Exception("XI Labs Response error:", response)

def translate_text_to_voice_elevenlabs(news_dict, language):
    news_id = news_dict[RawNewsEnum.id.value]

    t_id = news_id
    l_id = db_language_code_dict[language]
    translated_dict = get_translated_article(t_id, l_id)

    orig_text = translated_dict[TranslatedArticlesEnum.translated_article.value]
    processed_text , change_list  = handle_number_preprocessing(orig_text, language=language)
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": XI_LABS_API_KEY
    }

    data = {
        "text": processed_text,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }
    voice_ids = ["21m00Tcm4TlvDq8ikWAM", 'AZnzlk1XvdvUeBnXmlld', 'EXAVITQu4vr4xnSDxMaL', 'ErXwobaYiN019PkySvjV', 'MF3mGyEYCl7XYWbV9V6O', 'TxGEqnHWrfWFTfGW9XjX', 'VR6AewLTigWG4xSOukaG', 'pNInz6obpgDQGcFmaJgB', 'yoZ06aMxZJJ28mfd3POQ']
    voice = "21m00Tcm4TlvDq8ikWAM"
    response = requests.post(XI_LABS_BASE_URL+voice, json=data, headers=headers)
    audio_path = get_audio_file_path(news_id, language)
    audio_file = os.path.join(audio_path,'audio.mp3')

    if response.status_code == 200:
        with open(audio_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=XI_LABS_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

        return audio_file
    else:
        return

def generate_english_audio(news_dict):
    news_id = news_dict[RawNewsEnum.id.value]
    article = news_dict[RawNewsEnum.article.value]
    tts = gTTS(article, lang='en', tld='co.in')
    audio_path = get_audio_file_path(news_id, 'English')
    audio_file = os.path.join(audio_path,'audio.mp3')
    tts.save(audio_file)
    return audio_file