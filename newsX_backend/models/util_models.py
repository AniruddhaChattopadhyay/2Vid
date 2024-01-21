
class NewsIdResponse():

    def __init__(self, all_news_ids:list, news_ids_inserted=None) -> None:
        self.all_news_ids = all_news_ids
        self.news_ids_inserted = news_ids_inserted
        self.news_count = len(self.all_news_ids) 
        self.insertion_count = len(news_ids_inserted) if news_ids_inserted is not None else 0