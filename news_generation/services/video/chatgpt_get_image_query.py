import os
import openai
from newsX_backend.utils.directory_helper import get_news_path
from newsX_backend.enums.model_enums import RawNewsEnum
from dotenv import load_dotenv

from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain

load_dotenv()

OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
IMAGE_VIDEO_QUERY_COUNT = 10

VIDEO_TYPE_TAG = '[Video]'
IMAGE_TYPE_TAG = '[Image]'

def get_google_image_queries_from_gpt(news):
    news_id = news[RawNewsEnum.id.value]
    image_query_file_path = os.path.join(get_news_path(news_id), 'images search queries.txt')

    if os.path.exists(image_query_file_path):
        return

    openai.api_key = OPEN_API_KEY
    promt_to_be_added = "Give me a ordered list of 6 google image queries as per the passage below to get relevant pictures to make a short video out of this. The queries should be ordered according to the context of the passage:"
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

def _get_image_video_query_reponse_from_gpt(news):
    query_count = IMAGE_VIDEO_QUERY_COUNT

    news_id = news[RawNewsEnum.id.value]
    news_article = news[RawNewsEnum.article.value]

    image_query_file_path = os.path.join(get_news_path(news_id), 'images search queries.txt')

    template = '''From this article provide a list of queries. The list can contain two type of items Image Query or Video Query and mark them by mentioning either ''' + str(IMAGE_TYPE_TAG) + ''' or ''' + str(VIDEO_TYPE_TAG) + ''' .
The queries should be for relevant images or videos describing the article, given in contextual order.
The Image queries are for google search so they can be descriptive, about 3 to 6 words.
But the video queries should be very generic, it should not contain any named entities or proper nouns, the video query is for stock video search platforms and should contain generic terms only. The video queries should br strictly one worded. If the video query becomes more than 1 word then replace it with the most suitable topic of 1 word, do not worry about context.
Now, Along with all the queries, give a list of exactly 4 similar words of that query and add '|' as separator between the query and the list of similar words and use ',' as delimiter for the list of similar words
The query and list of similar words are two different entities, the specifications for the query is not applicable on the list of similar words.
Remember the Video query should be exactly 1 word.
I need total of ''' + str(query_count) + ''' queries.
Here's the article:
{article}'''
    prompt = PromptTemplate(template=template, input_variables=["article"])
    llm = OpenAI(temperature=0.5, openai_api_key=OPEN_API_KEY)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return llm_chain.run(news_article)

def get_image_video_processed_query(news):
    image_query_file_path = os.path.join(get_news_path(news_id), 'images search queries.txt')

    gpt_response = None
    max_retries = 5
    retries = 0
    while retries < max_retries:
        gpt_response = _get_image_video_query_reponse_from_gpt(news)
        retries+=1
        if len(str(gpt_response).strip().split('\n')) == IMAGE_VIDEO_QUERY_COUNT:
            break

    list_length = len(str(gpt_response).strip().split('\n'))
    if list_length != IMAGE_VIDEO_QUERY_COUNT:
        raise Exception(f'chat_gpt_image_query.py :: get_image_video_processed_query() :: ChatGPT response invalid, No of lines returned = {list_length} while required length is {IMAGE_VIDEO_QUERY_COUNT}')

    raw_query_list = str(gpt_response).strip().split('\n')

    query_list = []

    for item in raw_query_list:
        query_start = item.lower().rindex(IMAGE_TYPE_TAG)
        if query_start == -1:
            query_start = item.lower().rindex(VIDEO_TYPE_TAG)
        
        query_end = item.index('|')
        if query_start == -1 or query_end == -1:
            query = item[query_start+1:query_end]
