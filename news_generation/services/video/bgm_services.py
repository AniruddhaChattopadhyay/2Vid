import os
import openai
from newsX_backend.utils.directory_helper import get_bgm_path
from newsX_backend.enums.model_enums import RawNewsEnum
from newsX_backend.mappers.category_types import BgmCategory
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

load_dotenv()



def get_bgm(news_dict):
    text = news_dict[RawNewsEnum.article.value]
    bgm_type = get_bgm_type(text)
    return get_bgm_path(bgm_type)

def get_bgm_type(text):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    BGM_TYPES = BgmCategory.DEFINED_BGM_CATEGORY.copy()

    bgm_type_string = ', '.join(BGM_TYPES)
    prompt = f'We are trying to find music type for articles from the context of an Indian person.\n What kind of background music would be appropriate for the below passage. \nThe options are {bgm_type_string} . Give answer among these options and return only the music type nothing else: {str(text)}'

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
              "content": prompt}
        ]
    )

    bgm_type = completion.choices[0].message.content
    bgm_type = str(bgm_type).lower().strip()

    BGM_TYPES.sort(key=lambda x: fuzz.ratio(x.lower().strip(),bgm_type), reverse=True)
    print(bgm_type)
    print('******'*4,BGM_TYPES)
    return BGM_TYPES[0]