from django.db import models

class RawNews(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    article = models.TextField()
    title = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    source_url = models.TextField(default=None, blank=True, null=True)
    source = models.TextField( default=None, blank=True, null=True)
    original_source = models.TextField(default=None, blank=True, null=True)
    image_url = models.TextField(default=None, blank=True, null=True)
    author = models.TextField()
    category = models.TextField()


class TranslatedArticles(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    t_id = models.CharField(max_length=255)
    translated_article = models.TextField(default=None, blank=True, null=True)
    translated_title = models.TextField(default=None, blank=True, null=True)
    language = models.ForeignKey('Languages', null=True, on_delete=models.SET_NULL)

class Languages(models.Model):

    l_id = models.CharField(max_length=255, primary_key=True)
    lang = models.CharField(max_length=255)
    google_lang_code = models.CharField(max_length=255)
    ai4b_lang_code = models.CharField(max_length=255, null=True)
    aks_lang_code = models.CharField(max_length=255, null=True)
    bcp_47_lang_code = models.CharField(max_length=255)
    is_active =models.BooleanField(null=False)

class VideoLinks(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    v_id = models.CharField(max_length=255)
    video_url = models.TextField(default=None, blank=True, null=True)
    language = models.ForeignKey('Languages', null=True, on_delete=models.SET_NULL)

class ItemConfig(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    email_list = models.TextField(default=None, blank=True, null=True)
    is_bgm_enabled = models.BooleanField(default=False, blank=True, null=True)
