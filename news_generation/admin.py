from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(RawNews)
admin.site.register(TranslatedArticles)
admin.site.register(Languages)
admin.site.register(VideoLinks)
admin.site.register(ItemConfig)