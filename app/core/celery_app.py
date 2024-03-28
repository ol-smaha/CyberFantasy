import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.conf.enable_utc = False
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

