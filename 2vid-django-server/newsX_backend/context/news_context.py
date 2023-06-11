from data.mappers import NewsDictKeys

class NewsResponse():
        def __init__(self, value,status) -> None:
            self.value = value
            self.status = status

class NewsContext():

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(NewsContext, self).__new__(self)
        return self.instance
    
    def build(self,news_dict,languages:list,current_language=None) -> None:
        self.news_dict = news_dict
        self.news_id = self.news_dict[NewsDictKeys.ID_KEY]

        self.languages = languages
        if len(languages)<1:
            raise Exception('NewsContext.__init__() :: Atleast 1 language needs to be provided :: Curent languages list : ', languages)
        
        self.current_language = current_language if current_language is not None else languages[0]
        return self


    def next_language(self):
        current_index = self.languages.index(self.current_language)
        
        if current_index+1 >= len(self.languages):
            return NewsResponse(None,False)
        
        self.current_language = self.languages[current_index+1]
        return NewsResponse(self.current_language, True)
    
    def get_category(self):
        return self.news_dict[NewsDictKeys.CATEGORY_KEY]
    
    def get_language(self):
        return self.current_language
    
    def set_language(self, language):
        if language in self.languages:
            self.current_language = language