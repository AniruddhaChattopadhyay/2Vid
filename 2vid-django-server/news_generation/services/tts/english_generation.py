from gtts import gTTS
from newsX_backend.utils.directory_helper import get_news_path, get_audio_file_path
from newsX_backend.enums.model_enums import RawNewsEnum, TemporaryEnum
from .recorded_voice_handling import download_recorded_voice
import os
from newsX_backend.mappers.language_mapper import ACTIVE_LANGUAGES, DEFINED_LANGUAGES, Languages

def handle_recorded_voice(news_dict):
    if news_dict[RawNewsEnum.title.value] == TemporaryEnum.from_forms.value and 'google.drive' in news_dict[RawNewsEnum.image_url.value] and news_dict[RawNewsEnum.original_source.value] == Languages.ENGLISH:
        return download_recorded_voice(news_dict,Languages.ENGLISH)
    else:
        return False

def generate_english_audio(news_dict):
    news_id = news_dict[RawNewsEnum.id.value]
    article = news_dict[RawNewsEnum.article.value]
    if not handle_recorded_voice(news_dict):
        tts = gTTS(article, lang='en', tld='co.in')
        audio_path = get_audio_file_path(news_id, 'English')
        audio_file = os.path.join(audio_path,'audio.mp3')
        tts.save(audio_file)