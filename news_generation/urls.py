from django.urls import path
from .views import NewsGeneration, NewsGenerationByURL, ProcessNewsFromURL, UpdateLanguageTable, process_form_view, show_submission ,  ScriptToVideo , UrlToVideo, TestView

urlpatterns = [
    path("getnews/bulk/", NewsGeneration.as_view()),
    path("getnews/url/", NewsGenerationByURL.as_view()),
    path("processnews/url/", ProcessNewsFromURL.as_view()),
    path("processnews/page/", process_form_view),
    path("processnews/page/submit/", show_submission, name = 'form_submission'),
    path("utils/language/update/", UpdateLanguageTable.as_view(), name = 'form_submission'),
    path("2vid/scripttovideo/", ScriptToVideo.as_view()),
    path("2vid/urltovideo/", UrlToVideo.as_view()),
    path("test/testservice/", TestView.as_view()),
]
