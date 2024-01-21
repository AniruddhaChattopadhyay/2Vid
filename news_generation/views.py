from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import Http404, JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from news_generation.services.services import *




# Create your views here.


class NewsGeneration(APIView):

    def post(self, request):
        return news_generation_post(request)


class NewsGenerationByURL(APIView):

    def post(self, request):
        return news_generation_by_url(request)


class ProcessNewsFromURL(APIView):

    def post(self,request):
        return process_news_from_url(request)

class UpdateLanguageTable(APIView):
    
    def post(self, request):
        return update_language_table(request)

class ScriptToVideo(APIView):
    def post(self, request):
        print(request.data)
        return script_to_video(request)
    
class UrlToVideo(APIView):
    def post(self, request):
        return url_to_video(request)
    
class TestView(APIView):

    def post(self,request):
        return test_service(request)

@csrf_exempt
def process_form_view(request):
    return process_news_from_form(request)
    
@csrf_exempt
def show_submission(request):
    return render(request,'submission.html',{})