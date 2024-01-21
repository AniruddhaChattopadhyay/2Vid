from icrawler.builtin import GoogleImageCrawler
from super_image import EdsrModel, ImageLoader
from PIL import Image
import requests
import os
import torch.multiprocessing as mp

from newsX_backend.utils.directory_helper import get_news_path, get_news_images_path

Model = EdsrModel.from_pretrained('ml_models/edsr-base', scale=4)

MIN_RESOLUTION = 600*600

def get_images_from_google(news_dict):
    news_id = news_dict['id']
    query_file_path = os.path.join(get_news_path(
        news_id), 'images search queries.txt')
    with open(query_file_path, 'r') as f:
        query_raw = f.read()

    queryList = query_raw.split('\n')
    print(queryList)

    for idx, query in enumerate(queryList):
        image_path = get_news_images_path(news_id)
        topic_image_path = os.path.join(image_path, str(idx))
        if not os.path.exists(topic_image_path):
            os.mkdir(topic_image_path)

        google_crawler = GoogleImageCrawler(
            feeder_threads=4,
            parser_threads=4,
            downloader_threads=4,
            storage={'root_dir': topic_image_path})
        google_crawler.crawl(
            keyword=query + ' images', max_num=2)
    
# def process_images(news_id):
#     images_parent_dir = get_news_images_path(news_id)
#     for root, subdirectories, files in os.walk(images_parent_dir):
#         for subdirectory in sorted(subdirectories):
#             images_path = os.path.join(root, subdirectory)
#             for image_file in sorted(os.listdir(images_path)):
#                 if (image_file.endswith('.png') or image_file.endswith('.jpg')) and image_file.find('scaled')==-1 and image_file.find('resized')==-1:
#                     image_path = os.path.join(images_path, image_file)
#                     image = Image.open(image_path)
#                     if image.height*image.width < MIN_RESOLUTION:
#                         print(f'Image Upscaled: {image_file}',  image.height, image.width, image.height/image.width)
#                         p = mp.Process(target=upscale_image, args=(image_path, images_path,Model,))
#                         p.start()
#                         p.join()
#                         # upscale_image(image_path, images_path)
#                         os.remove(image_path)
#                     break

# def upscale_image(image_file, image_root_path, model):
#     image = Image.open(image_file)
#     inputs = ImageLoader.load_image(image)
#     preds = Model(inputs)
#     output_file = os.path.join(image_root_path,image_file+'_scaled_4x.png')
#     ImageLoader.save_image(preds, output_file)
#     image.close()