import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blueteam.settings')

app = Celery('blueteam')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-five-minutes': {
        'task': 'check_twitch_live',
        'schedule': crontab('*/5')
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
