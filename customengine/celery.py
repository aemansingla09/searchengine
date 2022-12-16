import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customengine.settings')

app = Celery('customengine')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

if settings.DEBUG:

    @app.task(bind=True)
    def debug_task(self):
        """Debug method."""
        print(f'Request: {self.request!r}')