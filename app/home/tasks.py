import logging
import requests
from celery.decorators import task
from django.conf import settings
from django.core import management

logger = logging.getLogger('celery')


@task(autoretry_for=(Exception,))
def clear_sessions():
    return management.call_command('clearsessions')


def send_discord_message(channel_id, message):
    url = '{}/channels/{}/messages'.format(
        settings.DISCORD_API_URL,
        channel_id,
    )
    headers = {
        'Authorization': 'Bot {}'.format(settings.DISCORD_BOT_TOKEN),
    }
    data = {'content': message}
    r = requests.post(url, headers=headers, data=data, timeout=10)
    if not r.ok:
        r.raise_for_status()
    return r
