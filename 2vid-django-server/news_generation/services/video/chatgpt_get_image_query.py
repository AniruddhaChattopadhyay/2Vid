import os
import openai
from newsX_backend.utils.directory_helper import get_news_path
from newsX_backend.enums.model_enums import RawNewsEnum
from dotenv import load_dotenv


load_dotenv()


def get_google_image_queries_from_gpt(news):
    news_id = news[RawNewsEnum.id.value]
    image_query_file_path = os.path.join(get_news_path(news_id), 'images search queries.txt')

    if os.path.exists(image_query_file_path):
        return

    openai.api_key = os.getenv("OPENAI_API_KEY")
    promt_to_be_added = "Give me a ordered list of not more than 6 google image queries as per the passage below to get relevant pictures to make a short video out of this. The queries should be ordered according to the context of the passage:"
    # news_article = "Delhi CM Arvind Kejriwal on Saturday said the Gujarat High Court's Friday order on PM Narendra Modi's degree has raised a lot of questions. \"If he has a degree and it's real, then why isn't it being shown?\" he asked. Yesterday, the court said PMO doesn't need to furnish PM Modi's degree and imposed costs of ₹25,000 on Kejriwal."
    news_article = news[RawNewsEnum.article.value]
    complete_prompt = promt_to_be_added + '\n' + news_article

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
              "content": complete_prompt}
        ]
    )

    print(completion)
    queries = completion.choices[0].message.content

    # preprocessing
    queries.replace("\"", "")
    # queries = "1.ISRO Launch Vehicle Mark 3 (LVM3) \n2.OneWeb Satellites\n3.NewSpace India commercial agreement \n4.Low-Earth Orbit Satellites \n5.LVM3 M2/OneWeb India-1 mission \n6.Sriharikota Launch Site"
    with open(image_query_file_path, 'w') as out_file:
        out_file.write(queries)
