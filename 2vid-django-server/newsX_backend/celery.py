from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsX_backend.settings.local')

app = Celery('newsX_backend',
             broker='amqp://guest:guest@localhost:5672/',
             backend='rpc://guest:guest@localhost:5672/')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
