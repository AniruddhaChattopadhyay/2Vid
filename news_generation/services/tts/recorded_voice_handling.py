import gdown
from newsX_backend.utils.directory_helper import get_news_path, get_audio_file_path
from newsX_backend.enums.model_enums import RawNewsEnum
from urllib.parse import urlparse, parse_qs
import os

def download_recorded_voice(news_dict, language):
    try:
        url = news_dict[RawNewsEnum.image_url.value]
        parsed_url = urlparse(url)
        file_id = parse_qs(parsed_url.query)['id'][0]
        audio_path = get_audio_file_path(news_dict[RawNewsEnum.id.value], language)
        audio_file = os.path.join(audio_path,'audio.mp3')
        gdown.download(id = file_id, output = audio_file, quiet=False)
        return True

    except Exception as e:
        print("**ERROR** : ",str(e))
        return False
